<script lang="ts">
  // Bibliotheque des samples DT2 (7.J2, 7.J4) : arbre des dossiers du +Drive
  // (7.J8 : branche, puis une ligne par code, une case par sous-categorie), puis
  // une liste (case, non classes ou corbeille). Depuis 7.L3 : plus de garder /
  // ecarter, de plafond ni de rangement ; tous les fichiers d'une case sont
  // listes, filtrables au milieu par tag ou style (filtre local de la liste).
  // Selection multiple (Cmd, Maj), corbeille (icone, Suppr, glisser dessus).
  // Kits (7.J5) : pads des packs sous la grille, puis des sous-kits du pack
  // choisi ; un pad filtre grille et listes sur le kit, porte ses tags (herites par ses fichiers) et sa corbeille.
  // Vue kit : arborescence BRANCHE / dossier / fichiers, puis un dossier des
  // non classes du kit.
  // Vue par type (7.K) : un filtre d'instrument liste a droite tous les
  // fichiers du type par sous-dossier ; un kit ne filtre que cette vue (sans
  // ses sous-dossiers vides), l'arbre de gauche ne bouge pas.
  // Barre de recherche (7.J6) : texte, tags (manuels, de kit, inferes des
  // dossiers), kits, instruments, rythmique / melodique, one-shot / boucle,
  // etoiles ; ET entre facettes, OU dans une facette ; filtre toute la page.
  // Propositions : historique des filtres en plus des facettes ; deck de la
  // telecommande de la barre generale (lecture, boucle, sample precedent / suivant).
  // Lives (7.L2) : bouton Live, panneau en troisieme colonne (LivePanel) ;
  // L ajoute la selection a la banque active (Entree : le sample en cours seul), glisser sur une ligne de banque ;
  // badge des banques du live sur les samples de la liste.
  import { onDestroy, onMount } from 'svelte'
  import WaveSurfer from 'wavesurfer.js'
  import { remote } from './remote.svelte'
  import { focus } from './focus.svelte'
  import { loadHistory, pushHistory } from './history'
  import LivePanel from './LivePanel.svelte'
  import * as retrig from './retrig'
  import { api, type LooseSample, type SampleCell, type SampleEntry, type SampleKit, type SampleKits, type FacetTag, type FacetNote, type FacetBpm, type SampleFilter, type RebuildStatus } from './api'

  const FLAG_HELP: Record<string, string> = {
    muet: 'crête sous -40 dBFS',
    faible: 'crête sous -18 dBFS : gain à remonter',
    sature: 'plateaux à pleine échelle (écrêtage)',
    blanc: 'plus de 30 ms de silence en tête : le trig traîne',
    long: 'frappe de plus de 2 s (queue, reverb ou boucle mal rangée)',
    illisible: 'fichier non décodable',
  }
  const VIEW_KEY = 'ui:sample-cell'
  const KIT_KEY = 'ui:sample-kit'
  // colonnes : one-shots puis boucles en dernier (memes codes qu'analyzer/samples.py)
  // ordre des tracks de la doctrine (digitakt/doctrine.md § 1) : rythmique
  // (tracks 1 a 8, boucles rythmiques en fin), puis melodique (9 a 16)
  const LOOPS = ['BR', 'DL', 'PL', 'ML', 'BL']
  const RHYTHM = ['BD', 'RM', 'SD', 'CP', 'TM', 'PC', 'BR', 'DL', 'PL', 'HH', 'OH', 'CY']
  const MELODIC = ['BS', 'BL', 'ST', 'ML', 'PD', 'VX', 'FX', 'RS']
  const CODE_ORDER = [...RHYTHM, ...MELODIC]
  const CODE_HELP: Record<string, string> = {
    BD: 'Kick (bass drum) · track 1', RM: 'Rumble, sub (rendu du sound design) · track 2', SD: 'Snare (caisse claire) · track 3', CP: 'Clap · track 3',
    TM: 'Tom · track 4 (perc, ou Id1 en seconde voix)', PC: 'Percussion (conga, shaker, cowbell…) · tracks 4-5',
    BR: 'Boucle break (amen…) · track 5 (Id1 rythmique)', DL: 'Boucle drums · track 5 (Id1 rythmique)', PL: 'Boucle percussions, hats, tops · track 5 (Id1 rythmique)',
    HH: 'Hat fermé · track 6', OH: 'Hat ouvert · track 7', CY: 'Cymbale, ride, crash · track 8',
    BS: 'Basse one-shot · track 9', BL: 'Boucle de basse · track 9 (ou Id2 13, passe-haut)', ST: 'Stab, accord, synthé, instrument · track 10',
    ML: 'Boucle mélodique (lead, séquence, accords) · track 14 (Id3, ou Id2 13 si grave)', PD: 'Nappe, pad, drone · track 11',
    VX: 'Voix, samples parlés · track 12', FX: 'FX de transition (riser, impact, noise…) · track 15',
    RS: 'Resample, enregistrement maison · track 16 (joker)',
  }
  // libelle court d'un code pour l'arbre : « Kick (bass drum) · track 1 » -> « Kick, bass drum »
  // track(s) de la doctrine sur deux chiffres : « track 1 » -> « 01 », « tracks 4-5 » -> « 04-05 »
  const codeTrack = (c: string) => {
    const m = /tracks? (\d+)(?:-(\d+))?/.exec(CODE_HELP[c] ?? '')
    return m ? [m[1], m[2]].filter(Boolean).map(n => n!.padStart(2, '0')).join('-') : ''
  }
  const codeShort = (c: string) => (CODE_HELP[c] ?? c).split(' · ')[0].replace(/ \(/g, ', ').replace(/\)/g, '')
  const codeTitle = (c: string) => `${c} : ${CODE_HELP[c] ?? c}${LOOPS.includes(c) ? ' (boucle)' : ''}`
  const codeRank = (c: string) => (CODE_ORDER.includes(c) ? CODE_ORDER.indexOf(c) : CODE_ORDER.length)
  // branches du +Drive (memes noms qu'analyzer/samples.py) ; FX et VX sans niveau code
  const BRANCHES = ['DRUMS', 'TONAL', 'LOOPS', 'FX', 'VX', 'SAMPLE']
  const BRANCH_HELP: Record<string, string> = {
    DRUMS: 'One-shots percussifs', TONAL: 'One-shots avec note (basse, stab, nappe)',
    LOOPS: 'Boucles (BR / DL : sous-dossier = tranche de tempo)', FX: 'FX de transition',
    VX: 'Voix', SAMPLE: 'Samples et resamples maison, sans plafond',
  }
  /** (code, sous-categorie) d'un dossier final : FX/RISE -> FX, RISE ; DRUMS/BD -> BD, ''. */
  function splitFolder(folder: string): { branch: string; code: string; sub: string } {
    const [branch, a = '', b = ''] = folder.split('/')
    return branch === 'FX' || branch === 'VX' ? { branch, code: branch, sub: a } : { branch, code: a, sub: b }
  }

  type Loose = 'unclassified' | 'trash'
  type View = { kind: 'cell'; folder: string } | { kind: Loose } | { kind: 'kit' } | { kind: 'type'; folder?: string }

  let cells = $state<SampleCell[]>([])
  // dossiers cibles (tous, meme vides) : l'arbre ne bouge pas avec un filtre
  let allFolders = $state<string[]>([])
  let closedBranches = $state<Set<string>>(new Set())
  let counts = $state({ unclassified: 0, trash: 0 })
  let allTags = $state<string[]>([])
  let error = $state('')
  let view = $state<View | null>(null)
  let entries = $state<SampleEntry[]>([])
  let cursor = $state<string | null>(null)    // source du sample en cours
  let cursorUrl = $state('')
  // zone du clavier (fleches) : liste de la lib, ou liste de la banque du live
  // apres un clic dans celle-ci ; un choix dans la lib la rend a la lib
  let zone = $state<'lib' | 'live'>('lib')                    // audio du sample en cours (rendu accorde d'un live)
  let sel = $state<Set<string>>(new Set())    // selection multiple (Cmd / Maj)
  let anchor: string | null = null            // origine d'une plage Maj-clic
  // filtre local de la liste du milieu (7.L3) : tags ou styles, ET entre eux
  let localTags = $state<string[]>([])
  let localInput = $state('')
  let busy = $state(false)
  let autoplay = $state(true)
  // barre de recherche : filtre applique cote API a toutes les lectures
  const SEARCH_KEY = 'ui:sample-search'
  let search = $state<SampleFilter>({})
  let facets = $state<FacetTag[]>([])
  let wheel = $state<FacetNote[]>([])   // roue chromatique (7.J7)
  let allKits = $state<SampleKit[]>([])     // kits sans filtre (suggestions)
  let query = $state('')
  let suggestIdx = $state(0)
  let searchField: HTMLInputElement | undefined = $state()
  let tagInput = $state('')
  let tagField: HTMLInputElement | undefined = $state()
  // glisser-deposer : sources tirees, cible survolee (corbeille ; live dans LivePanel)
  let dragging = $state<string[] | null>(null)
  let dropKey = $state<string | null>(null)
  // kit (prefixe de chemin : pack ou pack/sous-kit), '' = tous
  let kit = $state('')
  let kitData = $state<SampleKits>({ kits: [], tags: {} })
  let kitTagInput = $state('')

  // lives (7.L2) : panneau ouvert ou non, banques du live choisi par source
  const LIVE_PANEL_KEY = 'ui:live-panel'
  let liveOpen = $state(false)
  let inLive = $state(new Map<string, string[]>())
  let livePanel: LivePanel | undefined = $state()
  function toggleLive() {
    liveOpen = !liveOpen
    if (!liveOpen) inLive = new Map()
    try { localStorage.setItem(LIVE_PANEL_KEY, liveOpen ? '1' : '') } catch { /* stockage indisponible */ }
  }

  let container: HTMLDivElement | undefined = $state()
  let ws: WaveSurfer | null = null

  const current = $derived(view?.kind === 'cell' ? view : null)
  // ordre : celui des dossiers cibles (branche, code, racine puis sous-categories),
  // les dossiers SAMPLE (hors cibles) en fin, par code
  const folderRank = (f: string) => {
    const i = allFolders.indexOf(f)
    return i >= 0 ? i : 1e3 + codeRank(splitFolder(f).code)
  }
  // filtre actif : seuls les dossiers qui y repondent (M cible toujours tous les
  // dossiers), plus les sous-dossiers vides du type filtre (cibles de depot)
  const folderList = $derived([...new Set([
    ...(filterOn() ? allFolders.filter(f => search.codes?.includes(splitFolder(f).code) && !f.startsWith('SAMPLE/')) : allFolders),
    ...cells.map(c => c.folder)])]
    .sort((a, b) => folderRank(a) - folderRank(b)))
  const byKey = $derived(new Map(cells.map(c => [c.folder, c])))
  // total d'un dossier / d'un type : tous ses fichiers (candidats + hors plafond de l'API)
  const total = (c: SampleCell) => c.candidates + c.reserve
  const codeTotal = (folders: string[]) => folders.reduce((n, f) => { const c = byKey.get(f); return n + (c ? total(c) : 0) }, 0)
  // vue par type : filtre d'instrument actif
  const typeMode = $derived(!!search.codes?.length)
  const branchRows = $derived(BRANCHES.map(branch => {
    const fs = folderList.filter(f => splitFolder(f).branch === branch)
    const cs = fs.map(f => byKey.get(f)).filter((c): c is SampleCell => c !== undefined)
    const codesIn = [...new Set(fs.map(f => splitFolder(f).code))]
    return {
      branch, codes: codesIn.map(code => ({ code, folders: fs.filter(f => splitFolder(f).code === code) })),
      files: cs.reduce((n, c) => n + total(c), 0),
    }
  }).filter(b => b.codes.length))
  const tagsOf = (e: SampleEntry) => [...new Set([...e.tags, ...e.auto_tags])]
  // filtre « hors live » : masque les samples deja pris dans le live ouvert
  const HIDE_LIVE_KEY = 'ui:sample-hide-live'
  let hideLive = $state(false)
  const hidingLive = $derived(hideLive && liveOpen)
  const shown = $derived(entries.filter(e =>
    (!hidingLive || !inLive.has(e.source))
    && (!localTags.length || localTags.every(x => tagsOf(e).includes(x)))))
  // tags et styles de la liste (avant filtre local), du plus frequent au plus rare
  const localFacets = $derived.by(() => {
    const n = new Map<string, number>()
    for (const e of entries) for (const t of tagsOf(e)) n.set(t, (n.get(t) ?? 0) + 1)
    return [...n.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], 'fr'))
  })
  function addLocal(t: string) {
    const v = t.trim()
    if (v && !localTags.includes(v)) localTags = [...localTags, v]
    localInput = ''
  }
  function onLocalKey(e: KeyboardEvent) {
    if (e.key === 'Enter') { e.preventDefault(); addLocal(localInput) }
    else if (e.key === 'Escape') { e.preventDefault(); localInput = ''; (e.target as HTMLElement).blur() }
  }
  // arborescence du kit : branches (ordre de l'arbre), dossiers, puis non classes
  type Folder = { key: string; label: string; code: string; rows: SampleEntry[] }
  type FamFolder = { key: string; label: string; folders: Folder[]; total: number }
  let collapsed = $state<Set<string>>(new Set())
  const tree = $derived.by((): FamFolder[] => {
    if (view?.kind !== 'kit' && view?.kind !== 'type') return []
    const branches = new Map<string, Map<string, SampleEntry[]>>()
    for (const e of shown) {
      const branch = e.folder ? splitFolder(e.folder).branch : ''
      const byFolder = branches.get(branch) ?? new Map<string, SampleEntry[]>()
      byFolder.set(e.folder, [...(byFolder.get(e.folder) ?? []), e])
      branches.set(branch, byFolder)
    }
    const branchRank = (b: string) => (b === '' ? 1e3 : BRANCHES.indexOf(b))
    return [...branches.entries()].sort(([a], [b]) => branchRank(a) - branchRank(b)).map(([branch, byFolder]) => {
      const folders = [...byFolder.entries()].sort(([a], [b]) => folderRank(a) - folderRank(b)).map(([folder, rows]) => ({
        key: folder || ':nc/', label: folder.split('/').slice(1).join('/') || folder, code: splitFolder(folder).code,
        rows,
      }))
      return {
        key: branch || ':nc', label: branch || 'Non classés', folders,
        total: folders.reduce((n, f) => n + f.rows.length, 0),
      }
    })
  })
  const visible = $derived(view?.kind === 'kit' || view?.kind === 'type'
    ? tree.flatMap(f => collapsed.has(f.key) ? [] : f.folders.flatMap(c => collapsed.has(c.key) ? [] : c.rows))
    : shown)

  // reanalyse de la bibliotheque (7.K) : nouveaux packs, sous-dossiers manuels ;
  // les ecritures sont refusees par l'API pendant le calcul
  let rebuild = $state<RebuildStatus | null>(null)
  const rebuilding = $derived(rebuild?.status === 'running')
  async function startRebuild() {
    try { rebuild = await api.sampleRebuild(); followRebuild() } catch (e) { fail(e) }
  }
  function followRebuild() {
    const timer = setInterval(async () => {
      try {
        rebuild = await api.sampleRebuildStatus()
        if (rebuild.status === 'running') return
        clearInterval(timer)
        if (rebuild.status === 'done') {
          allFolders = await api.sampleFolders()
          await refresh()
          await loadEntries()
          if (!visible.some(e => e.source === cursor)) pick(visible[0]?.source ?? null)
        }
      } catch (e) { clearInterval(timer); fail(e) }
    }, 2000)
  }

  /** Clic sur un code de l'arbre : ajoute / retire le filtre d'instrument (vue par type) ;
   *  vue restreinte a une case du type : retour au type entier. */
  function toggleCode(code: string) {
    const cur = search.codes ?? []
    if (view?.kind === 'type' && view.folder && cur.includes(code)) { open({ kind: 'type' }); return }
    const codes = cur.includes(code) ? cur.filter(c => c !== code) : [...cur, code]
    setSearch({ ...search, codes: codes.length ? codes : undefined })
  }

  /** Vue par type : restreint la vue du milieu a la case (re-clic : type entier). */
  function reveal(folder: string) {
    const v = view?.kind === 'type' && view.folder === folder ? { kind: 'type' as const } : { kind: 'type' as const, folder }
    collapsed = new Set()
    open(v)
  }

  function toggleBranch(branch: string) {
    const s = new Set(closedBranches)
    if (s.has(branch)) s.delete(branch)
    else s.add(branch)
    closedBranches = s
  }

  function toggleFolder(key: string) {
    const s = new Set(collapsed)
    if (s.has(key)) s.delete(key)
    else s.add(key)
    collapsed = s
  }
  const totals = $derived(cells.reduce((n, c) => n + total(c), 0))
  const targetCount = $derived(sel.size || (cursor ? 1 : 0))

  type Pad = { kit: string; label: string; files: number; trashed: boolean }
  const files = (k: SampleKit) => k.candidates + k.reserve + k.unclassified + k.trashed
  // pads de packs (sommes des sous-kits) ; un pack est barre si tout est a la corbeille
  const packs = $derived.by(() => {
    const out = new Map<string, Pad>()
    for (const k of kitData.kits) {
      const p = out.get(k.pack) ?? { kit: k.pack, label: k.pack, files: 0, trashed: true }
      p.files += files(k)
      p.trashed &&= k.trashed_kit
      out.set(k.pack, p)
    }
    return [...out.values()].sort((a, b) => a.label.localeCompare(b.label, 'fr', { sensitivity: 'base' }))
  })
  const activePack = $derived(kit.split('/')[0])
  const subKits = $derived(kitData.kits.filter(k => k.pack === activePack && k.kit !== activePack))
  const kitInfo = $derived(kitData.kits.find(k => k.kit === kit))
  const kitTrashed = $derived(kitInfo?.trashed_kit ?? (kit !== '' && packs.find(p => p.kit === kit)?.trashed === true))
  const trashedKits = $derived(kitData.kits.filter(k => k.trashed_kit))

  /** Tags herites d'un kit ou d'un pack : ils se retirent sur le kit. */
  function inherited(source: string, tag: string): string | undefined {
    return Object.keys(kitData.tags).find(k => source.startsWith(`${k}/`) && kitData.tags[k].includes(tag))
  }

  function searchOn(): boolean {
    const f = search
    return !!(f.q || f.tags?.length || f.kits?.length || f.codes?.length || f.notes?.length || f.section || f.kind || f.minStars)
  }
  function filterOn(): boolean { return searchOn() || kit !== '' }

  type Sug = { kind: 'text' | 'tag' | 'kit' | 'code' | 'note' | 'history'; value: string; hint: string; recall?: SampleFilter }

  // historique des filtres (propositions), jetons lisibles = libelle de l'entree
  const HISTORY_KEY = 'ui:sample-history'
  let history = $state<SampleFilter[]>(loadHistory<SampleFilter>(HISTORY_KEY))
  let searchFocused = $state(false)
  function filterTokens(f: SampleFilter): string[] {
    return [
      ...(f.q ? [`« ${f.q} »`] : []), ...(f.tags ?? []), ...(f.kits ?? []), ...(f.codes ?? []), ...(f.notes ?? []),
      ...(f.section ? [f.section === 'rhythm' ? 'rythmique' : 'mélodique'] : []),
      ...(f.kind ? [f.kind === 'loop' ? 'boucle' : 'one-shot'] : []),
      ...(f.minStars ? [`${'★'.repeat(f.minStars)}+`] : []),
    ]
  }
  const historySugs = (t: string, n: number): Sug[] => history
    .map(h => ({ h, label: filterTokens(h).join(' · ') }))
    .filter(x => x.label && (!t || x.label.toLowerCase().includes(t)))
    .slice(0, n)
    .map(x => ({ kind: 'history' as const, value: x.label, hint: 'filtre récent', recall: x.h }))

  // roue chromatique (7.J7) : C en haut, sens horaire, 12 parts de 30 degres
  const W_OUT = 46, W_IN = 15
  function polar(r: number, deg: number): [number, number] {
    const a = (deg - 90) * Math.PI / 180
    return [50 + r * Math.cos(a), 50 + r * Math.sin(a)]
  }
  function wedge(i: number): string {
    const [a, b] = [i * 30 - 15, i * 30 + 15]
    const [x1, y1] = polar(W_OUT, a), [x2, y2] = polar(W_OUT, b)
    const [x3, y3] = polar(W_IN, b), [x4, y4] = polar(W_IN, a)
    return `M${x1},${y1} A${W_OUT},${W_OUT} 0 0 1 ${x2},${y2} L${x3},${y3} A${W_IN},${W_IN} 0 0 0 ${x4},${y4} Z`
  }
  const wheelMax = $derived(Math.max(1, ...wheel.map(w => w.count)))
  // roue des notes (7.K) : ne filtre que la vue de droite, pas l'arbre
  const NOTES_KEY = 'ui:sample-notes'
  let notes = $state<string[]>([])
  // tranches de tempo (7.K) : meme principe, si le sous-ensemble a des tempos
  const BPMS_KEY = 'ui:sample-bpms'
  let bpms = $state<string[]>([])
  let bpmFacets = $state<FacetBpm[]>([])
  const rightF = $derived({ ...search, ...(notes.length ? { notes } : {}), ...(bpms.length ? { bpms } : {}) })
  const bpmShown = $derived(bpms.length > 0 || bpmFacets.some(b => b.count > 0))
  /** « 90 » -> « 90-109 », derniere tranche « 190+ ». */
  function bpmLabel(i: number): string {
    const b = bpmFacets[i].band
    const next = bpmFacets[i + 1]?.band
    return b.startsWith('<') ? b : next ? `${b}-${Number(next) - 1}` : `${b}+`
  }
  async function toggleBpm(band: string) {
    bpms = bpms.includes(band) ? bpms.filter(x => x !== band) : [...bpms, band]
    try { localStorage.setItem(BPMS_KEY, JSON.stringify(bpms)) } catch { /* stockage indisponible */ }
    await loadEntries()
    if (!visible.some(e => e.source === cursor)) pick(visible[0]?.source ?? null)
  }
  async function toggleNote(n: string) {
    notes = notes.includes(n) ? notes.filter(x => x !== n) : [...notes, n]
    try { localStorage.setItem(NOTES_KEY, JSON.stringify(notes)) } catch { /* stockage indisponible */ }
    await loadEntries()
    if (!visible.some(e => e.source === cursor)) pick(visible[0]?.source ?? null)
  }
  /** La barre ne garde que texte, tags, kits et instruments (7.K). */
  function onlyBar(f: SampleFilter): SampleFilter {
    const { section: _s, kind: _k, minStars: _m, notes: _n, bpms: _b, ...rest } = f
    return rest
  }
  const GROUP_LABEL: Record<string, string> = { genre: 'genre', instrument: 'instrument', mot: 'mot-clé', manuel: 'tag' }
  const suggestions = $derived.by((): Sug[] => {
    const t = query.trim().toLowerCase()
    if (!t) return searchFocused ? historySugs('', 6) : []
    const out: Sug[] = [{ kind: 'text', value: query.trim(), hint: 'texte : nom DT2 ou chemin' }]
    for (const c of CODE_ORDER) {
      if (!search.codes?.includes(c) && (c.toLowerCase() === t || CODE_HELP[c].toLowerCase().includes(t)))
        out.push({ kind: 'code', value: c, hint: CODE_HELP[c] })
    }
    for (const f of facets) {
      if (f.tag.includes(t) && !search.tags?.includes(f.tag))
        out.push({ kind: 'tag', value: f.tag, hint: `${GROUP_LABEL[f.group] ?? f.group} · ${f.count}` })
    }
    const kitNames = new Set([...allKits.map(k => k.pack), ...allKits.map(k => k.kit)])
    for (const k of kitNames) {
      if (k.toLowerCase().includes(t) && !search.kits?.includes(k))
        out.push({ kind: 'kit', value: k, hint: k.includes('/') ? 'kit' : 'pack' })
    }
    return [...out.slice(0, 14), ...historySugs(t, 3)]
  })

  async function setSearch(f: SampleFilter) {
    // autre instrument : note et tempo choisis pour le precedent ne valent plus
    // (une note de kick viderait les boucles PL) ; arborescence depliee
    if ((f.codes ?? []).join() !== (search.codes ?? []).join()) {
      notes = []
      bpms = []
      collapsed = new Set()
      try { localStorage.setItem(NOTES_KEY, '[]'); localStorage.setItem(BPMS_KEY, '[]') } catch { /* stockage indisponible */ }
    }
    search = f
    history = pushHistory(HISTORY_KEY, history, f, filterTokens)
    try { localStorage.setItem(SEARCH_KEY, JSON.stringify(f)) } catch { /* stockage indisponible */ }
    await refresh()
    if (f.codes?.length) { await open({ kind: 'type' }); return }
    if (view?.kind === 'type') {
      const c = cells.find(x => x.to_listen > 0) ?? cells[0]
      if (c) { await open({ kind: 'cell', folder: c.folder }); return }
    }
    // la case ouverte ne repond plus au filtre : premiere case qui y repond
    if (current && !byKey.has(current.folder) && ordered.length) {
      await open({ kind: 'cell', folder: ordered[0].folder })
      return
    }
    await loadEntries()
    if (!visible.some(e => e.source === cursor)) pick(visible[0]?.source ?? null)
  }

  function addSug(sg: Sug) {
    if (sg.kind === 'history' && sg.recall) {
      query = ''
      suggestIdx = 0
      setSearch(onlyBar(sg.recall))
      return
    }
    const f = { ...search }
    if (sg.kind === 'text') f.q = sg.value
    else if (sg.kind === 'tag') f.tags = [...(f.tags ?? []), sg.value]
    else if (sg.kind === 'kit') f.kits = [...(f.kits ?? []), sg.value]
    else if (sg.kind === 'note') f.notes = [...(f.notes ?? []), sg.value]
    else f.codes = [...(f.codes ?? []), sg.value]
    query = ''
    suggestIdx = 0
    setSearch(f)
  }

  function dropChip(kind: Sug['kind'], value: string) {
    const f = { ...search }
    if (kind === 'text') delete f.q
    else if (kind === 'tag') f.tags = f.tags?.filter(x => x !== value)
    else if (kind === 'kit') f.kits = f.kits?.filter(x => x !== value)
    else if (kind === 'note') f.notes = f.notes?.filter(x => x !== value)
    else f.codes = f.codes?.filter(x => x !== value)
    setSearch(f)
  }

  const chips = $derived([
    ...(search.q ? [{ kind: 'text' as const, value: search.q }] : []),
    ...(search.tags ?? []).map(v => ({ kind: 'tag' as const, value: v })),
    ...(search.kits ?? []).map(v => ({ kind: 'kit' as const, value: v })),
    ...(search.codes ?? []).map(v => ({ kind: 'code' as const, value: v })),
    ...(search.notes ?? []).map(v => ({ kind: 'note' as const, value: v })),
  ])

  function onSearchKey(e: KeyboardEvent) {
    if (e.key === 'ArrowDown') { suggestIdx = Math.min(suggestIdx + 1, suggestions.length - 1); e.preventDefault() }
    else if (e.key === 'ArrowUp') { suggestIdx = Math.max(suggestIdx - 1, 0); e.preventDefault() }
    else if (e.key === 'Enter' && suggestions.length) { addSug(suggestions[suggestIdx] ?? suggestions[0]); e.preventDefault() }
    else if (e.key === 'Escape') { query = ''; searchField?.blur(); e.preventDefault() }
    // completion : Tab prend la proposition surlignee, sinon la premiere facette ;
    // Espace valide une facette dont le nom est exactement saisi (BD, kick…)
    else if (e.key === 'Tab' && query.trim() && suggestions.length) {
      const facet = suggestions.find(s => s.kind !== 'text' && s.kind !== 'history')
      addSug(suggestIdx > 0 ? suggestions[suggestIdx] : facet ?? suggestions[0])
      e.preventDefault()
    }
    else if (e.key === ' ' && query.trim()) {
      const t = query.trim().toLowerCase()
      const exact = suggestions.find(s => s.kind !== 'text' && s.kind !== 'history' && s.value.toLowerCase() === t)
      if (exact) { addSug(exact); e.preventDefault() }
    }
    else if (e.key === 'Backspace' && !query && chips.length) { const c = chips[chips.length - 1]; dropChip(c.kind, c.value) }
  }

  function cssVar(name: string): string {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  }

  function fail(e: unknown) {
    error = e instanceof Error ? e.message : String(e)
  }

  function looseRow(l: LooseSample, i: number): SampleEntry {
    const name = (l.source.split('/').pop() ?? l.source).replace(/\.wav$/i, '')
    return { source: l.source, family: '', code: '', sub: '', folder: '', pack: l.pack, name, duration: null, rank: i + 1,
      status: 'pending', selected: true, flags: null, bpm: null, bpm_est: false, tags: l.tags, stars: l.stars,
      auto_tags: l.auto_tags, overflow: false }
  }

  // grille (filtree), compteurs hors case et tags connus
  async function refresh() {
    try {
      const [c, u, t, tags, k, fa, wh, bp] = await Promise.all([
        api.sampleCells(search, search.codes?.length ? '' : kit),
        api.sampleLoose('unclassified', kit, search), api.sampleLoose('trash', kit, search), api.sampleTags(),
        api.sampleKits(search), api.sampleFacets(), api.sampleNotes(search, kit), api.sampleBpms(search, kit),
      ])
      cells = c
      facets = fa
      wheel = wh
      bpmFacets = bp
      const ak = filterOn() ? await api.sampleKits() : k
      if (!allFolders.length) allFolders = await api.sampleFolders()
      allKits = ak.kits
      counts = { unclassified: u.length, trash: t.length }
      allTags = tags
      kitData = k
      error = ''
    } catch (e) {
      fail(e)
    }
  }

  async function loadEntries() {
    const v = view
    if (!v) { entries = []; return }
    // une case videe (tout deplace) n'existe plus : liste vide
    if (v.kind === 'type') {
      const all = await api.sampleTree(rightF, kit).catch(() => [])
      entries = v.folder ? all.filter(e => e.folder === v.folder) : all
      return
    }
    if (v.kind === 'kit') {
      const t = await api.sampleKitTree(kit, rightF).catch(() => ({ entries: [], unclassified: [] }))
      entries = [...t.entries, ...t.unclassified.map(looseRow)]
      return
    }
    entries = v.kind === 'cell'
      ? await api.sampleCell(v.folder, kit, true, rightF).catch(() => [])
      : (await api.sampleLoose(v.kind, kit, rightF)).map(looseRow)
  }

  /** `target` : sample a selectionner a l'arrivee (defaut : premier a ecouter). */
  async function open(v: View, target?: string) {
    view = v
    sel = new Set()
    const key = v.kind === 'cell' ? v.folder : `:${v.kind}`
    try { localStorage.setItem(VIEW_KEY, key) } catch { /* stockage indisponible */ }
    await loadEntries()
    pick(target ?? visible[0]?.source ?? null)
  }

  // sample en cours = source du sound design (8.E), renommage compris ; sauf
  // un rendu montre depuis son badge « versé » (`quiet`), jusqu'au suivant
  let quiet: string | null = null
  $effect(() => {
    const e = visible.find(x => x.source === cursor)
    if (e && e.source !== quiet) focus.set({ source: e.source, name: e.name, code: e.code, folder: e.folder })
  })

  // rendu verse montre depuis le sound design : son dossier, puis lui
  let mounted = $state(false)
  $effect(() => {
    const r = focus.reveal
    if (!r || !mounted) return
    focus.reveal = null
    void showSample(r.folder, r.source)
  })
  async function showSample(folder: string, source: string) {
    quiet = source
    await open({ kind: 'cell', folder }, source)
  }

  /** Ecoute depuis le panneau du live : il prend les fleches (zone live). */
  function playLive(source: string, url?: string) {
    pick(source, url)
    zone = 'live'
  }

  function pick(source: string | null, url?: string) {
    zone = 'lib'
    if (source !== quiet) quiet = null
    cursor = source
    if (!source || !ws) return
    cursorUrl = url ?? api.sampleAudioUrl(source)
    ws.load(cursorUrl).catch(() => { /* chargement remplace par le suivant */ })
    queueMicrotask(() => document.getElementById(`s-${source}`)?.scrollIntoView({ block: 'nearest' }))
  }

  function saveHideLive() {
    try { localStorage.setItem(HIDE_LIVE_KEY, hideLive ? '1' : '') } catch { /* stockage indisponible */ }
  }

  /** Ajout au live (L, Entree) ; filtre « hors live » actif : le curseur passe
   * au premier sample suivant qui reste dans la liste. */
  async function addToLive(sources: string[]) {
    if (!livePanel || !sources.length) return
    const gone = new Set(sources)
    const i = visible.findIndex(e => e.source === cursor)
    const next = [...visible.slice(i + 1), ...visible.slice(0, Math.max(i, 0)).reverse()].find(e => !gone.has(e.source))
    await livePanel.add(sources)
    if (zone === 'lib' && hidingLive && cursor && !visible.some(e => e.source === cursor)) pick(next?.source ?? null)
  }

  function step(delta: number) {
    if (!visible.length) return
    const i = visible.findIndex(e => e.source === cursor)
    const j = i < 0 ? 0 : Math.min(Math.max(i + delta, 0), visible.length - 1)
    pick(visible[j].source)
  }

  const ordered = $derived(folderList.map(f => byKey.get(f)).filter((c): c is SampleCell => c !== undefined))

  function stepCell(delta: number) {
    if (!ordered.length) return
    const i = current ? ordered.findIndex(c => c.folder === current.folder) : -1
    const c = ordered[(i + delta + ordered.length) % ordered.length]
    open({ kind: 'cell', folder: c.folder })
  }

  function targets(): string[] {
    return sel.size ? [...sel] : cursor ? [cursor] : []
  }

  /** Action par lot : sur la selection, sinon le sample en cours. Le curseur
   *  reste s'il est encore dans la liste, sinon passe au suivant. */
  async function act(fn: (sources: string[]) => Promise<unknown>, sources: string[] = targets()): Promise<boolean> {
    if (!sources.length || busy) return false
    busy = true
    const before = visible.map(e => e.source)
    try {
      await fn(sources)
      sel = new Set()
      await Promise.all([refresh(), loadEntries()])
      if (!visible.some(e => e.source === cursor)) {
        const i = before.indexOf(cursor ?? '')
        const next = before.slice(i + 1).find(s => visible.some(e => e.source === s))
        pick(next ?? visible[0]?.source ?? null)
      }
      return true
    } catch (e) {
      fail(e)
      return false
    } finally {
      busy = false
    }
  }

  const stars = (n: number | null) => act(s => api.sampleStars(s, n))
  const toTrash = (sources?: string[]) => act(api.sampleTrash, sources)
  const restore = () => act(api.sampleRestore)

  async function addTag() {
    const t = tagInput.trim()
    if (!t) return
    if (await act(s => api.sampleTagsEdit(s, [t]))) tagInput = ''
    tagField?.blur()
  }

  function onTagKey(e: KeyboardEvent) {
    if (e.key === 'Enter') { e.preventDefault(); addTag() }
    else if (e.key === 'Escape') { e.preventDefault(); tagField?.blur() }
  }

  // clic : ecouter ; Cmd-clic : ajouter / retirer de la selection ; Maj-clic : plage
  function onRowClick(ev: MouseEvent, source: string) {
    if (ev.metaKey || ev.ctrlKey) {
      const s = new Set(sel)
      if (!s.size && cursor && cursor !== source) s.add(cursor)
      if (s.has(source)) s.delete(source)
      else s.add(source)
      sel = s
      anchor = source
      return
    }
    const from = anchor ?? cursor
    if (ev.shiftKey && from) {
      const order = visible.map(e => e.source)
      const [a, b] = [order.indexOf(from), order.indexOf(source)].sort((x, y) => x - y)
      if (a >= 0) sel = new Set([...sel, ...order.slice(a, b + 1)])
      return
    }
    sel = new Set()
    anchor = source
    pick(source)
  }

  function onDragStart(ev: DragEvent, source: string) {
    const sources = sel.has(source) ? [...sel] : [source]
    ev.dataTransfer?.setData('text/plain', sources.join('\n'))
    if (ev.dataTransfer) ev.dataTransfer.effectAllowed = 'copyMove'   // copie : ajout a un live
    dragging = sources
  }

  function onDragEnd() {
    dragging = null
    dropKey = null
  }

  function onDragOver(ev: DragEvent, key: string) {
    if (!dragging) return
    ev.preventDefault()
    dropKey = key
  }

  /** Depot sur la corbeille. */
  function onDrop(ev: DragEvent) {
    ev.preventDefault()
    const sources = dragging
    onDragEnd()
    if (sources) toTrash(sources)
  }

  /** Choisit un kit (re-clic : retour a tous). */
  // panneau de tagging du kit : au double-clic sur un pad seulement
  let kitPanel = $state(false)

  /** Double-clic sur un pad : le kit reste choisi et son panneau s'ouvre. */
  async function editKit(k: string) {
    if (kit !== k) await chooseKit(k)
    kitPanel = true
  }

  async function chooseKit(k: string) {
    kitPanel = false
    kit = kit === k ? '' : k
    kitTagInput = ''
    try { localStorage.setItem(KIT_KEY, kit) } catch { /* stockage indisponible */ }
    collapsed = new Set()
    await refresh()
    if (search.codes?.length) await open({ kind: 'type' })
    else if (kit) await open({ kind: 'kit' })
    else if (view?.kind === 'kit') {
      const c = cells[0]
      if (c) await open({ kind: 'cell', folder: c.folder })
    } else if (view) await open(view)
  }

  async function kitAct(fn: () => Promise<unknown>) {
    if (busy) return
    busy = true
    try {
      await fn()
      await Promise.all([refresh(), loadEntries()])
      if (!visible.some(e => e.source === cursor)) pick(visible[0]?.source ?? null)
    } catch (e) {
      fail(e)
    } finally {
      busy = false
    }
  }

  function trashKit() {
    const n = kitInfo ? files(kitInfo) : packs.find(p => p.kit === kit)?.files ?? 0
    if (!confirm(`Mettre ${kit} à la corbeille (${n} fichiers) ? Restaurable d’un bloc.`)) return
    kitAct(() => api.sampleKitTrash(kit))
  }

  async function addKitTag() {
    const t = kitTagInput.trim()
    if (!t) return
    await kitAct(() => api.sampleKitTags(kit, [t]))
    kitTagInput = ''
  }

  function onKitTagKey(e: KeyboardEvent) {
    if (e.key === 'Enter') { e.preventDefault(); addKitTag() }
    else if (e.key === 'Escape') { e.preventDefault(); (e.target as HTMLElement).blur() }
  }

  function onkey(e: KeyboardEvent) {
    const t = e.target as HTMLElement | null
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable)) return
    // panneau lateral affiche par-dessus (KB) ; une vue masquee mais montee
    // (colonne aside.panel du sound design) ne bloque pas le clavier
    if ([...document.querySelectorAll<HTMLElement>('aside.panel, aside.kb')].some(a => a.offsetParent)) return
    if (!container?.offsetParent) return  // vue masquee (autre section du panneau lateral)
    const k = e.key
    if ((e.metaKey || e.ctrlKey) && (k === 'a' || k === 'A')) { sel = new Set(visible.map(x => x.source)); e.preventDefault(); return }
    if (e.metaKey || e.ctrlKey || e.altKey) return
    const trashView = view?.kind === 'trash'
    if ((k === 'u' || k === 'U') && trashView) restore()
    else if (zone === 'live' && liveOpen && livePanel && k.startsWith('Arrow')) {
      if (k === 'ArrowDown') livePanel.step(1)
      else if (k === 'ArrowUp') livePanel.step(-1)
      else if (k === 'ArrowRight') livePanel.stepBank(1)
      else livePanel.stepBank(-1)
    }
    else if (k === 'ArrowDown') step(1)
    else if (k === 'ArrowUp') step(-1)
    else if (k === 'ArrowRight') stepCell(1)
    else if (k === 'ArrowLeft') stepCell(-1)
    else if (k === ' ') {
      // Espace tenu : relance a chaque temps au tempo de la banque active du
      // live (arret au relachement) ; sans tempo, rejoue une fois
      const bpm = liveOpen ? livePanel?.tempo() : null
      if (e.repeat) { /* deja lance */ }
      else if (bpm && cursor) { ws?.pause(); retrig.start(cursorUrl, bpm) }
      else { ws?.stop(); ws?.play() }
    }
    else if (k === 't' || k === 'T') tagField?.focus()
    else if ((k === 'l' || k === 'L') && liveOpen) addToLive(targets())
    else if (k === 'Enter' && liveOpen && cursor) addToLive([cursor])
    else if (k >= '0' && k <= '5') stars(k === '0' ? null : Number(k))
    else if ((k === 'Delete' || k === 'Backspace') && !trashView) toTrash()
    else if (k === 'Escape') sel = new Set()
    else return
    e.preventDefault()
  }

  onMount(async () => {
    if (!container) return
    ws = WaveSurfer.create({
      container,
      height: 80,
      waveColor: cssVar('--wave'),
      progressColor: cssVar('--wave-progress'),
      cursorColor: cssVar('--accent'),
      normalize: true,
    })
    ws.on('ready', () => { if (autoplay) ws?.play() })
    ws.on('play', () => { playing = true; remote.played('samples') })
    ws.on('pause', () => { playing = false })
    ws.on('finish', () => { if (looping) ws?.play(); else playing = false })
    try { kit = localStorage.getItem(KIT_KEY) ?? '' } catch { /* stockage indisponible */ }
    try { liveOpen = !!localStorage.getItem(LIVE_PANEL_KEY) } catch { /* stockage indisponible */ }
    try { hideLive = !!localStorage.getItem(HIDE_LIVE_KEY) } catch { /* stockage indisponible */ }
    // reanalyse lancee avant un rechargement de la page : on reprend le suivi
    api.sampleRebuildStatus().then(r => { if (r.status === 'running') { rebuild = r; followRebuild() } }).catch(() => {})
    try {
      const saved = JSON.parse(localStorage.getItem(SEARCH_KEY) ?? '{}') as SampleFilter
      search = onlyBar(saved)
      notes = JSON.parse(localStorage.getItem(NOTES_KEY) ?? 'null') ?? saved.notes ?? []
      bpms = JSON.parse(localStorage.getItem(BPMS_KEY) ?? '[]')
    } catch { search = {} }
    await refresh()
    if (kit && !kitData.kits.some(k => k.kit === kit || k.pack === kit)) { kit = ''; await refresh() }
    let last: string | null = null
    try { last = localStorage.getItem(VIEW_KEY) } catch { /* stockage indisponible */ }
    // un rendu a montrer (badge « versé ») remplace la vue memorisee
    if (focus.reveal) { mounted = true; return }
    mounted = true
    if (search.codes?.length) return open({ kind: 'type' })
    if (last === ':kit' && kit) return open({ kind: 'kit' })
    if (last === ':unclassified' || last === ':trash') return open({ kind: last.slice(1) as Loose })
    const c = (last && byKey.get(last)) || cells[0]
    if (c) await open({ kind: 'cell', folder: c.folder })
  })
  onDestroy(() => { ws?.destroy(); retrig.stop() })

  // deck de la telecommande
  let playing = $state(false)
  let looping = $state(false)
  const cursorName = $derived(visible.find(e => e.source === cursor)?.name ?? '')
  onDestroy(remote.register('samples', {
    get label() { return cursorName },
    get playing() { return playing },
    get looping() { return looping },
    playPause: () => ws?.playPause(),
    pause: () => ws?.pause(),
    toggleLoop: () => { looping = !looping },
    prev: () => step(-1),
    next: () => step(1),
  }))

  function fmt(d: number | null): string {
    return d == null ? '' : d < 10 ? `${d.toFixed(2)} s` : `${d.toFixed(1)} s`
  }
</script>

<svelte:window onkeydown={onkey} onkeyup={e => { if (e.key === ' ') retrig.stop() }} onblur={() => retrig.stop()} />

{#snippet folderNode(f: string, sub: string)}
  {@const c = byKey.get(f)}
  <span class="drop">
    {#if c}
      <button class="cell" class:on={current?.folder === f || (view?.kind === 'type' && view.folder === f)}
        title="{f} : {total(c)} fichiers{c.flagged ? `, ${c.flagged} signalés` : ''}"
        onclick={() => (view?.kind === 'type' ? reveal(f) : open({ kind: 'cell', folder: f }))}><span class="sub">{sub}</span><span class="n">{total(c)}</span></button>
    {:else}
      <span class="slot" title="{f} : vide"><span class="sub">{sub}</span><span class="n">vide</span></span>
    {/if}
  </span>
{/snippet}

{#if focus.picking}
  <!-- choix d'une couche du sound design (8.J) : la source ne change pas -->
  <div class="layerpick" role="status">
    <span class="small">Couche du sound design :</span>
    {#if focus.candidate && focus.candidate.source !== focus.sample?.source}
      <strong class="mono small">{focus.candidate.name}</strong>
      <button class="small" onclick={() => focus.endPick(true)}>Ajouter comme couche</button>
    {:else}
      <span class="small muted">choisir un sample autre que la source ({focus.sample?.name ?? 'aucune'})</span>
    {/if}
    <button class="small" onclick={() => focus.endPick(false)}>Annuler</button>
  </div>
{/if}

<div class="samples" class:with-live={liveOpen}>
  <section class="grid">
   <div class="zone matrix">
    <h3 class="lib-title" title="Les chiffres d’un dossier : nombre de fichiers{filterOn() ? ' (filtrés)' : ''}.">Library</h3>
    <p class="lib-total small muted">
      {search.codes?.length ? `${search.codes.join(', ')} : ` : ''}{totals.toLocaleString('fr-FR')} fichiers{searchOn() ? ' filtrés' : ''}, toutes branches
    </p>
    <div class="searchbar">
      <div class="search-in">
        {#each chips as c (c.kind + c.value)}
          <span class="chip {c.kind}" title={c.kind === 'code' ? codeTitle(c.value) : c.kind}>{c.kind === 'text' ? `« ${c.value} »` : c.value}<button
            class="untag" title="Retirer" onclick={() => dropChip(c.kind, c.value)}>×</button></span>
        {/each}
        <input bind:this={searchField} bind:value={query} onkeydown={onSearchKey} oninput={() => (suggestIdx = 0)}
          onfocus={() => (searchFocused = true)} onblur={() => (searchFocused = false)}
          placeholder={chips.length ? 'affiner…' : 'Rechercher : texte, tag, genre, instrument (BD, kick…), kit…'} />
        {#if suggestions.length}
          <ul class="suggest">
            {#each suggestions as sg, i (sg.kind + sg.value)}
              <li><button class:on={i === suggestIdx} onmousedown={ev => { ev.preventDefault(); addSug(sg) }}>
                {#if sg.kind === 'history'}<span class="muted" aria-hidden="true">↺</span> <span>{sg.value}</span>
                {:else}<span class="chip {sg.kind}">{sg.kind === 'text' ? `« ${sg.value} »` : sg.value}</span>{/if}
                <span class="muted small">{sg.hint}</span></button></li>
            {/each}
          </ul>
        {/if}
      </div>
      {#if searchOn()}<button class="small" onclick={() => setSearch({})}>Tout effacer</button>{/if}
    </div>
    {#if error}<p class="err">{error}</p>{/if}
    <div class="branches">
      {#each branchRows as b (b.branch)}
        <div class="branch">
          <button class="fold small" title={BRANCH_HELP[b.branch] ?? b.branch} onclick={() => toggleBranch(b.branch)}>
            <span class="caret">{closedBranches.has(b.branch) ? '▸' : '▾'}</span> <strong>{b.branch}</strong>
            <span class="muted">{b.files}</span>
          </button>
          {#if !closedBranches.has(b.branch)}
            {#each b.codes as row (row.code)}
              {@const root = row.folders.find(f => !splitFolder(f).sub)}
              <div class="code-node">
                <button class="code-label" class:mel={!RHYTHM.includes(row.code)} class:loop={LOOPS.includes(row.code)}
                  class:active={search.codes?.includes(row.code)} onclick={() => toggleCode(row.code)}
                  title="{codeTitle(row.code)} · clic : filtre d'instrument"><span class="acr">{row.code}</span>{#if codeTrack(row.code)}<span class="trk">{codeTrack(row.code)}</span>{/if} <span class="desc">({codeShort(row.code)})</span></button>
                {#if root}{@render folderNode(root, '')}{/if}
                {#if row.folders.length > 1}<span class="tot code-tot" title="total du type {row.code}">({codeTotal(row.folders)})</span>{/if}
              </div>
              {#each row.folders.filter(f => splitFolder(f).sub) as f (f)}
                <div class="leaf">{@render folderNode(f, splitFolder(f).sub)}</div>
              {/each}
            {/each}
          {/if}
        </div>
      {/each}
    </div>
    <div class="loose">
      <button class="small" aria-pressed={view?.kind === 'unclassified'}
        title="Fichiers sans code (consultation)"
        onclick={() => open({ kind: 'unclassified' })}>Non classés ({counts.unclassified})</button>
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <span class="trash-drop" class:over={dropKey === 'trash'}
        ondragover={e => onDragOver(e, 'trash')} ondragleave={() => { if (dropKey === 'trash') dropKey = null }}
        ondrop={onDrop}>
        <button class="small" aria-pressed={view?.kind === 'trash'}
          title="Sons rejetés partout, restaurables, jamais supprimés du disque"
          onclick={() => open({ kind: 'trash' })}>Corbeille ({counts.trash})</button>
      </span>
      <button class="small" disabled={rebuilding}
        title="Relit les packs de Samples (nouveaux kits) ; garde les tags, étoiles et mesures. Les modifications sont bloquées pendant le calcul."
        onclick={startRebuild}>{rebuilding ? 'Réanalyse…' : 'Réanalyser'}</button>
      <button class="small live-btn" aria-pressed={liveOpen} title="Panneau du live : sélection de la lib par banque, jauge de RAM, export vers Live/00-live"
        onclick={toggleLive}>Live</button>
    </div>
    {#if rebuild && rebuild.status !== 'idle'}
      <p class="small rebuild" class:err={rebuild.status === 'error'}>
        {#if rebuild.status === 'running'}Réanalyse de la bibliothèque en cours (lancée à {rebuild.started_at?.slice(11)}) : les modifications sont bloquées jusqu'à la fin.
        {:else if rebuild.status === 'done'}Réanalyse terminée : {rebuild.candidates + rebuild.reserve} fichiers classés, {rebuild.unclassified} non classés.
          <button class="small" onclick={() => (rebuild = null)}>×</button>
        {:else}Réanalyse en échec : {rebuild.error} <button class="small" onclick={() => (rebuild = null)}>×</button>{/if}
      </p>
    {/if}
   </div>
    <section class="kits zone">
      <h3 class="small">Kits <span class="muted">· fichiers · re-clic pour tout voir · double-clic pour tagger</span></h3>
      {#if kit && kitPanel}
        <div class="kit-bar small">
          <strong title={kit}>{kit}</strong>
          {#if kitInfo}<span class="muted">{files(kitInfo)} fichiers · {kitInfo.unclassified} non classés</span>{/if}
          {#each kitData.tags[kit] ?? [] as t}
            <span class="tag">{t}<button class="untag" title="Retirer le tag {t} du kit"
              onclick={() => kitAct(() => api.sampleKitTags(kit, [], [t]))}>×</button></span>
          {/each}
          {#if kitTrashed}
            <button class="small" disabled={busy} onclick={() => kitAct(() => api.sampleKitRestore(kit))}>Restaurer le kit</button>
          {:else}
            <input class="tag-in" list="sample-tags" placeholder="tag du kit" bind:value={kitTagInput} onkeydown={onKitTagKey} />
            <button class="small" disabled={!kitTagInput.trim() || busy} onclick={addKitTag}>Tagger le kit</button>
            <button class="small danger" disabled={busy} onclick={trashKit}>Corbeille du kit</button>
          {/if}
          <button class="small close" title="Fermer" onclick={() => (kitPanel = false)}>×</button>
        </div>
      {/if}
      <div class="pads">
        {#each packs as p (p.kit)}
          <button class="pad" class:on={activePack === p.kit} class:gone={p.trashed}
            title="{p.kit} · double-clic : tags et corbeille du kit"
            onclick={ev => { if (ev.detail < 2) chooseKit(p.kit) }} ondblclick={() => editKit(p.kit)}>
            <span class="pad-name">{p.label}</span>
            <span class="pad-n">{p.trashed ? 'corbeille' : p.files}</span>
            {#if kitData.tags[p.kit]?.length}<span class="pad-tags">{kitData.tags[p.kit].join(' · ')}</span>{/if}
          </button>
        {/each}
      </div>
      {#if subKits.length}
        <div class="pads subs">
          {#each subKits as k (k.kit)}
            <button class="pad sub" class:on={kit === k.kit} class:gone={k.trashed_kit}
              title="{k.kit} · double-clic : tags et corbeille du kit"
              onclick={ev => { if (ev.detail < 2) chooseKit(kit === k.kit ? activePack : k.kit) }} ondblclick={() => editKit(k.kit)}>
              <span class="pad-name">{k.label}</span>
              <span class="pad-n">{k.trashed_kit ? 'corbeille' : files(k)}{k.unclassified ? ` · ${k.unclassified} nc` : ''}</span>
              {#if kitData.tags[k.kit]?.length}<span class="pad-tags">{kitData.tags[k.kit].join(' · ')}</span>{/if}
            </button>
          {/each}
        </div>
      {/if}
    </section>
  </section>

  <section class="detail">
    <header>
      <strong>{current ? current.folder.replaceAll('/', ' / ') : view?.kind === 'type' ? (view.folder ? view.folder.replaceAll('/', ' / ') : `Type ${search.codes?.join(', ')}`) + (kit ? ` · kit ${kit}` : '') : view?.kind === 'kit' ? `Kit ${kit}` : view?.kind === 'unclassified' ? 'Non classés' : view?.kind === 'trash' ? 'Corbeille' : 'Choisis une case'}</strong>
      {#if view}<span class="muted small">{shown.length}{shown.length !== entries.length ? ` / ${entries.length}` : ''} fichiers</span>{/if}
      <label class="small"><input type="checkbox" bind:checked={autoplay} /> lecture auto</label>
    </header>
    <div class="wave-row">
      <div class="wave" bind:this={container}></div>
      <svg class="wheel" viewBox="0 0 100 100" role="group" aria-label="Filtrer la liste par note">
        {#each wheel as w, i (w.note)}
          {@const [lx, ly] = polar(37, i * 30)}
          {@const [cx, cy] = polar(24, i * 30)}
          <g role="button" tabindex="-1" class:on={notes.includes(w.note)} class:empty={!w.count}
            onclick={() => { if (w.count || notes.includes(w.note)) toggleNote(w.note) }} onkeydown={() => {}}>
            <title>{w.note} : {w.count} sample{w.count > 1 ? 's' : ''}</title>
            <path d={wedge(i)} style="fill-opacity: {0.08 + 0.5 * w.count / wheelMax}" />
            <text x={lx} y={ly} class="wl">{w.note}</text>
            {#if w.count}<text x={cx} y={cy} class="wc">{w.count}</text>{/if}
          </g>
        {/each}
      </svg>
      {#if bpmShown}
        <div class="bpms" role="group" aria-label="Filtrer la liste par tempo">
          {#each bpmFacets as b, i (b.band)}
            <button class="bpm" class:on={bpms.includes(b.band)} class:empty={!b.count}
              disabled={!b.count && !bpms.includes(b.band)} title="{bpmLabel(i)} BPM : {b.count} sample{b.count > 1 ? 's' : ''}"
              onclick={() => toggleBpm(b.band)}><span>{bpmLabel(i)}</span>{#if b.count}<span class="bc">{b.count}</span>{/if}</button>
          {/each}
        </div>
      {/if}
    </div>
    <div class="toolbar small">
      <span class="count">{sel.size ? `${sel.size} sélectionnés` : cursor ? 'sample en cours' : 'rien'}</span>
      {#if view?.kind === 'trash'}
        <button class="small" disabled={!targetCount || busy} onclick={restore}>Restaurer</button>
      {:else}
        <button class="small icon" disabled={!targetCount || busy} title="Mettre à la corbeille (Suppr)" aria-label="Corbeille"
          onclick={() => toTrash()}><svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true"><path d="M2.5 4h11M6 4V2.5h4V4M4 4l.7 9.5h6.6L12 4M6.5 6.5v5M9.5 6.5v5" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      {/if}
      <span class="stars-bar">
        {#each [1, 2, 3, 4, 5] as n}<button class="star" disabled={!targetCount || busy} title="{n} étoile{n > 1 ? 's' : ''} ({n})" onclick={() => stars(n)}>{'★'.repeat(n)}</button>{/each}
        <button class="star" disabled={!targetCount || busy} title="Retirer la note (0)" onclick={() => stars(null)}>×</button>
      </span>
      <input class="tag-in" list="sample-tags" placeholder="tag (T)" bind:this={tagField} bind:value={tagInput}
        onkeydown={onTagKey} disabled={!targetCount} />
      <datalist id="sample-tags">{#each allTags as t}<option value={t}></option>{/each}</datalist>
      <button class="small" disabled={!targetCount || !tagInput.trim() || busy} onclick={addTag}>Tagger</button>
    </div>
    <div class="local small">
      {#each localTags as t (t)}
        <span class="chip tag">{t}<button class="untag" title="Retirer" onclick={() => (localTags = localTags.filter(x => x !== t))}>×</button></span>
      {/each}
      <input class="local-in" list="local-tags" placeholder="filtrer : tag, style…" bind:value={localInput} onkeydown={onLocalKey}
        onchange={() => { if (localFacets.some(([t]) => t === localInput)) addLocal(localInput) }} />
      <datalist id="local-tags">{#each localFacets as [t, n] (t)}<option value={t}>{n}</option>{/each}</datalist>
      {#each localFacets.filter(([t]) => !localTags.includes(t)).slice(0, 8) as [t, n] (t)}
        <button class="tag auto" title="{n} fichier{n > 1 ? 's' : ''} : filtrer la liste" onclick={() => addLocal(t)}>{t} <span class="muted">{n}</span></button>
      {/each}
      {#if localTags.length}<button class="small" onclick={() => (localTags = [])}>Tout voir</button>{/if}
      {#if liveOpen}<label class="hide-live" title="Masque les samples déjà pris dans le live ouvert (toutes banques)"><input type="checkbox" bind:checked={hideLive} onchange={saveHideLive} /> hors live</label>{/if}
    </div>
    {#if view?.kind === 'trash' && trashedKits.length}
      <ul class="trashed-kits small">
        {#each trashedKits as k (k.kit)}
          <li><span class="name">{k.kit}</span> <span class="muted">kit entier, {k.trashed} fichiers</span>
            <button class="small" disabled={busy} onclick={() => kitAct(() => api.sampleKitRestore(k.kit))}>Restaurer le kit</button></li>
        {/each}
      </ul>
    {/if}
    {#snippet sampleRow(e: SampleEntry)}
      <li id="s-{e.source}" class="row" class:cur={e.source === cursor}
        class:sel={sel.has(e.source)} draggable={view?.kind !== 'trash'}
        ondragstart={ev => onDragStart(ev, e.source)} ondragend={onDragEnd}>
        <button class="pick" onclick={ev => onRowClick(ev, e.source)}>
          <span class="name">{e.name}</span>
          {#if e.stars}<span class="stars" title="{e.stars} étoile{e.stars > 1 ? 's' : ''}">{'★'.repeat(e.stars)}</span>{/if}
          <span class="dur muted small">{fmt(e.duration)}</span>
          {#if e.bpm_est}<span class="est" title="tempo estimé par l’audio, non confirmé par la durée">~{e.bpm} bpm</span>{/if}
          {#if e.note_src === 'mesure'}<span class="est" title="note mesurée dans l’audio ({e.note_hz} Hz), à vérifier à l’oreille">~{e.note}</span>{/if}
          {#each e.flags ?? [] as f}<span class="flag" title={FLAG_HELP[f] ?? f}>{f}</span>{/each}
          {#if inLive.has(e.source)}<span class="inlive" title="dans le live : {inLive.get(e.source)?.join(', ')}">{inLive.get(e.source)?.join(' · ')}</span>{/if}
          <span class="src muted small" title={e.source}>{e.source}</span>
        </button>
        {#each e.tags as t}
          {@const from = inherited(e.source, t)}
          {#if from}
            <span class="tag small kit-tag" title="Tag du kit {from} (à retirer sur le kit)">{t}</span>
          {:else}
            <span class="tag small">{t}<button class="untag" title="Retirer le tag {t}"
              onclick={() => act(s => api.sampleTagsEdit(s, [], [t]), [e.source])}>×</button></span>
          {/if}
        {/each}
        {#each e.auto_tags.filter(t => !e.tags.includes(t)) as t}
          <button class="tag small auto" title="Tag inféré des dossiers : filtrer dessus"
            onclick={() => { if (!search.tags?.includes(t)) setSearch({ ...search, tags: [...(search.tags ?? []), t] }) }}>{t}</button>
        {/each}
      </li>
    {/snippet}
    {#if view?.kind === 'kit' || view?.kind === 'type'}
      <ol class="list tree">
        {#each tree as f (f.key)}
          <li class="folder fam">
            <button class="fold" onclick={() => toggleFolder(f.key)}>
              <span class="caret">{collapsed.has(f.key) ? '▸' : '▾'}</span> {f.label}
              <span class="muted small">{f.total}</span>
            </button>
          </li>
          {#if !collapsed.has(f.key)}
            {#each f.folders as c (c.key)}
              {#if f.key !== ':nc'}
                <li class="folder code" id="t-{c.key}" class:mel={!RHYTHM.includes(c.code)}>
                  <button class="fold" title={codeTitle(c.code)} onclick={() => toggleFolder(c.key)}>
                    <span class="caret">{collapsed.has(c.key) ? '▸' : '▾'}</span> {c.label}
                    <span class="muted small">{c.rows.length || 'vide'}</span>
                  </button>
                </li>
              {/if}
              {#if !collapsed.has(c.key)}
                {#each c.rows as e (e.source)}{@render sampleRow(e)}{/each}
              {/if}
            {/each}
          {/if}
        {/each}
      </ol>
    {:else}
      <ol class="list">
        {#each visible as e (e.source)}{@render sampleRow(e)}{/each}
      </ol>
    {/if}
    {#if view && !visible.length}<p class="muted small">{filterOn() || localTags.length ? 'Aucun sample ne répond au filtre.' : 'Liste vide.'}</p>{/if}
  </section>
  {#if liveOpen}<LivePanel bind:this={livePanel} bind:inLive focused={zone === 'live'} play={playLive} />{/if}
</div>

<style>
  .samples { display: grid; grid-template-columns: minmax(260px, 380px) minmax(0, 1fr); grid-template-rows: minmax(0, 1fr); gap: 12px 16px; padding: 12px 16px; height: 100%; min-height: 0; }
  .samples.with-live { grid-template-columns: minmax(210px, 270px) minmax(0, 1.3fr) minmax(320px, 1fr); gap: 12px 10px; padding: 12px 10px; }
  .inlive { font-size: 10px; padding: 0 4px; border-radius: 3px; border: 1px solid var(--accent); color: var(--accent); white-space: nowrap; }
  .searchbar { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin-bottom: 8px; }
  .search-in { position: relative; flex: 1; min-width: 0; display: flex; flex-wrap: wrap; gap: 4px; align-items: center; border: 1px solid var(--border); border-radius: 4px; padding: 3px 6px; background: var(--panel); }
  .search-in input { flex: 1; min-width: 12em; border: 0; outline: none; background: none; color: var(--text); font-size: 13px; padding: 3px 0; }
  .suggest { position: absolute; z-index: 5; top: 100%; left: 0; right: 0; margin: 2px 0 0; padding: 4px 0; list-style: none; background: var(--panel); border: 1px solid var(--border); border-radius: 4px; box-shadow: 0 4px 14px rgb(0 0 0 / 0.15); max-height: 22em; overflow-y: auto; }
  .suggest button { display: flex; gap: 8px; align-items: center; width: 100%; border: 0; background: none; padding: 4px 8px; text-align: left; color: var(--text); cursor: pointer; }
  .suggest button.on, .suggest button:hover { background: var(--panel-2); }
  .chip { display: inline-flex; align-items: center; gap: 2px; font-size: 11px; padding: 1px 2px 1px 7px; border-radius: 9px; border: 1px solid var(--border); white-space: nowrap; }
  .suggest .chip { padding-right: 7px; }
  .chip.tag { border-color: var(--melodic); }
  .chip.kit { border-color: var(--accent); background: color-mix(in srgb, var(--accent) 10%, transparent); }
  .chip.code { font-family: ui-monospace, Menlo, monospace; border-color: var(--rhythm); color: var(--rhythm); }
  .chip.text { font-style: italic; }
  .chip.note { font-weight: 600; border-color: var(--accent); color: var(--accent); }
  .tag.auto { border-style: dotted; background: none; cursor: pointer; padding: 0 6px; }
  /* deux zones fixes de meme hauteur, Library et Kits, chacune scrollable */
  .grid { display: flex; flex-direction: column; gap: 12px; min-height: 0; overflow: hidden; }
  .matrix, .kits { flex: 1 1 0; min-height: 0; display: flex; flex-direction: column; }
  .matrix .branches { flex: 1; min-height: 0; overflow-y: auto; }
  .kits { overflow-y: auto; }
  .filters { display: flex; gap: 10px; margin: 0 0 6px; }
  .zone { box-sizing: border-box; border: 1px solid var(--border); border-radius: 6px; padding: 8px 10px; }
  .branches { font-size: 12px; display: flex; flex-direction: column; gap: 2px; }
  .branch .fold { border: 0; background: none; color: var(--text); padding: 2px 0; cursor: pointer; }
  /* treeview : une ligne par dossier, code puis sous-dossiers en retrait, compteurs a droite */
  .code-node { display: grid; grid-template-columns: minmax(0, auto) minmax(0, 1fr) auto 18px; align-items: center; padding-left: 14px; min-height: 22px; }
  .leaf { padding-left: 42px; }
  .branches .drop { display: block; }
  button.code-label { border: 0; background: none; padding: 0; text-align: left; cursor: pointer; border-radius: 3px; }
  button.code-label:hover { text-decoration: underline; }
  button.code-label { width: auto; min-width: 0; max-width: 100%; display: flex; gap: 4px; align-items: baseline; overflow: hidden; }
  button.code-label .acr { display: inline-block; min-width: 24px; padding: 0 2px; border-radius: 3px; }
  button.code-label .trk { font-weight: 400; color: var(--muted); }
  button.code-label .desc { font: 11px ui-sans-serif, system-ui, sans-serif; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  button.code-label.active .acr { background: var(--rhythm); color: var(--panel); text-align: center; }
  button.code-label.mel.active .acr { background: var(--melodic); }
  .code-label { width: 24px; font: 600 11px ui-monospace, Menlo, monospace; color: var(--rhythm); cursor: help; }
  .code-label.mel { color: var(--melodic); }
  .code-label.loop { font-style: italic; text-decoration: underline dotted; }
  .drop { display: inline-block; border-radius: 3px; }
  .cell, .slot { display: flex; justify-content: space-between; gap: 8px; width: 100%; font: 11px ui-monospace, Menlo, monospace; padding: 2px 6px; border: 1px solid transparent; background: none; color: var(--text); border-radius: 3px; text-align: left; }
  .cell { cursor: pointer; }
  .cell:hover { background: var(--panel-2); border-color: var(--border); }
  .cell .sub { color: var(--text); }
  .n { font-variant-numeric: tabular-nums; }
  .tot { color: var(--muted); }
  .code-tot { grid-column: 3; font: 11px ui-monospace, Menlo, monospace; padding-left: 6px; }
  .cell.on { outline: 2px solid var(--accent); }
  .slot { color: var(--muted); opacity: 0.6; }
  .loose { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
  .loose button { white-space: nowrap; }
  .trash-drop { border-radius: 4px; }
  .live-btn { margin-left: auto; }
  .hide-live { display: inline-flex; gap: 3px; align-items: center; margin-left: auto; white-space: nowrap; }
  .local { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; margin-bottom: 6px; }
  .local-in { width: 11em; font-size: 12px; padding: 2px 6px; }
  .icon { display: inline-flex; align-items: center; padding: 3px 6px; }
  /* largeur de la grille : les pads remplissent la colonne sans l'elargir */
  .kits h3 { margin: 0 0 6px; font-weight: 600; position: sticky; top: -8px; z-index: 1; padding: 4px 0; background: var(--bg); }
  .lib-title { margin: 0 0 2px; font-weight: 600; }
  .lib-total { margin: 0 0 6px; }
  .rebuild { margin: 6px 0 0; }
  /* trois pads par ligne, a la largeur de la colonne */
  .pads { display: grid; grid-template-columns: repeat(auto-fill, minmax(96px, 1fr)); gap: 6px; }
  .pads.subs { margin-top: 8px; padding-top: 8px; border-top: 1px dashed var(--border); }
  .pad { display: flex; flex-direction: column; justify-content: center; align-items: flex-start; gap: 2px; min-width: 0; min-height: 58px; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--panel); color: var(--text); cursor: pointer; text-align: left; }
  .pad.sub { min-height: 50px; }
  .pad:hover { background: var(--panel-2); }
  .pad.on { outline: 2px solid var(--accent); background: var(--panel-2); }
  .pad.gone { opacity: 0.5; }
  .pad.gone .pad-name { text-decoration: line-through; }
  .pad-name { font-size: 13px; font-weight: 600; line-height: 1.15; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow-wrap: anywhere; }
  .pad-n { font: 11px ui-monospace, Menlo, monospace; color: var(--muted); }
  .pad-tags { font-size: 10px; color: var(--melodic); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
  .kit-bar .close { margin-left: auto; }
  .kit-bar { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin-bottom: 8px; padding: 6px 8px; border: 1px solid var(--accent); border-radius: 4px; background: var(--panel); }
  .danger { color: #dc2626; }
  .trashed-kits { list-style: none; margin: 0 0 6px; padding: 0; }
  .trashed-kits li { display: flex; gap: 8px; align-items: center; padding: 4px 6px; border-bottom: 1px solid var(--border); }
  .cell { position: relative; }
  .trash-drop.over { outline: 2px dashed #dc2626; }
  .detail { display: flex; flex-direction: column; min-height: 0; min-width: 0; box-sizing: border-box; border: 1px solid var(--border); border-radius: 6px; padding: 8px 10px; }
  .detail header { display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; }
  .detail header label { margin-left: auto; }
  .wave { margin: 8px 0 4px; border: 1px solid var(--border); border-radius: 4px; background: var(--panel); min-height: 80px; }
  .toolbar { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin: 4px 0; }
  .toolbar .count { min-width: 9em; color: var(--muted); }
  .stars-bar { display: inline-flex; gap: 2px; }
  .star { font-size: 11px; padding: 1px 4px; color: #b45309; }
  .tag-in { width: 9em; font-size: 12px; }
  .list { list-style: none; margin: 0; padding: 0; overflow-y: auto; flex: 1; min-height: 0; }
  .row { display: flex; align-items: center; gap: 6px; border-bottom: 1px solid var(--border); user-select: none; }
  .row.cur { background: var(--panel-2); box-shadow: inset 3px 0 0 var(--accent); }
  .row.sel { background: color-mix(in srgb, var(--accent) 18%, transparent); }
  /* retenus en avant ; reserve puis hors plafond nettement en retrait */
  .row:not(.out):not(.drop):not(.cur):not(.sel) { background: var(--panel); }
  .row:not(.out):not(.drop) .name { font-weight: 600; }
  .pick { flex: 1; min-width: 0; display: flex; gap: 8px; align-items: baseline; background: none; border: 0; padding: 5px 6px; text-align: left; color: var(--text); cursor: pointer; }
  .name { font-family: ui-monospace, Menlo, monospace; white-space: pre; }
  .stars { color: #b45309; font-size: 11px; }
  .dur { width: 5em; }
  .wave-row { display: flex; gap: 10px; align-items: center; }
  .wave-row .wave { flex: 1; min-width: 0; }
  .wheel { width: 80px; height: 80px; flex: none; }
  .bpms { display: grid; grid-template-columns: repeat(2, auto); grid-template-rows: repeat(4, 1fr); grid-auto-flow: column; gap: 2px; height: 80px; flex: none; }
  .bpm { display: flex; justify-content: space-between; gap: 6px; padding: 0 6px; font: 10px ui-monospace, Menlo, monospace; border-radius: 3px; }
  .bpm .bc { color: var(--muted); }
  .bpm.on { background: var(--accent); border-color: var(--accent); color: #fff; }
  .bpm.on .bc { color: #fff; }
  .bpm.empty:not(.on) { background: var(--panel); color: var(--muted); opacity: 0.5; }
  .wheel g { cursor: pointer; outline: none; }
  .wheel path { fill: var(--accent); stroke: var(--border); stroke-width: 0.6; }
  .wheel g.on path { fill: var(--accent); fill-opacity: 1 !important; stroke: var(--text); }
  /* note absente du sous-ensemble filtre : case blanche, sans compteur ni clic */
  .wheel g.empty:not(.on) path { fill: var(--panel); fill-opacity: 1 !important; }
  .wheel g.empty:not(.on) text { fill: var(--muted); opacity: 0.5; }
  .wheel g.empty:not(.on) { cursor: default; }
  .wheel text { text-anchor: middle; dominant-baseline: central; pointer-events: none; fill: var(--text); }
  .wheel .wl { font-size: 8px; font-weight: 600; }
  .wheel .wc { font-size: 5.5px; fill: var(--muted); }
  .wheel g.on text { fill: var(--panel); }
  .est { font-size: 10px; padding: 0 5px; border-radius: 8px; border: 1px dashed var(--muted); color: var(--muted); }
  .flag { font-size: 10px; padding: 0 5px; border-radius: 8px; background: #fde68a; color: #713f12; }
  .tag { display: inline-flex; align-items: center; gap: 2px; font-size: 10px; padding: 0 2px 0 6px; border-radius: 8px; border: 1px solid var(--border); color: var(--muted); white-space: nowrap; }
  .kit-tag { padding-right: 6px; border-style: dashed; }
  .untag { border: 0; background: none; color: var(--muted); padding: 0 3px; cursor: pointer; font-size: 10px; }
  .src { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; flex: 1; }
  .folder .fold { display: flex; gap: 6px; align-items: baseline; width: 100%; background: none; border: 0; border-bottom: 1px solid var(--border); padding: 5px 6px; text-align: left; color: var(--text); cursor: pointer; font-weight: 600; }
  .folder.fam .fold { background: var(--panel); font-size: 13px; }
  .folder.code .fold { padding-left: 22px; font: 600 12px ui-monospace, Menlo, monospace; background: color-mix(in srgb, var(--rhythm) 12%, var(--panel)); color: var(--rhythm); }
  .folder.code.mel .fold { background: color-mix(in srgb, var(--melodic) 12%, var(--panel)); color: var(--melodic); }
  .caret { width: 1em; color: var(--muted); }
  .tree .row { padding-left: 52px; }
  .small { font-size: 12px; }
  .err { color: #dc2626; font-size: 12px; }
  .layerpick { position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%); z-index: 20; display: flex; align-items: center; gap: 8px;
    background: var(--panel); border: 1px solid var(--accent); border-radius: 6px; padding: 6px 12px; box-shadow: 0 4px 16px rgb(0 0 0 / 0.3); }
  @media (max-width: 900px) {
    .samples, .samples.with-live { grid-template-columns: 1fr; height: auto; }
    .matrix, .kits { flex: none; max-height: 50vh; }
    .list { max-height: 60vh; }
  }
</style>
