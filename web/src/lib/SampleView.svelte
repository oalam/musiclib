<script lang="ts">
  // Bibliotheque des samples DT2 (7.J2, 7.J4) : arbre des dossiers du +Drive
  // (7.J8 : branche, puis une ligne par code, une case par sous-categorie), puis
  // une liste (case, non classes ou corbeille). Dans une case : les retenus a
  // ecouter (keep / drop au clavier) et la reserve ; un drop fait monter le
  // candidat suivant (selection recalculee par l'API). Selection multiple
  // (Cmd, Maj), barre d'outils, glisser-deposer vers une case ou la corbeille.
  // Export des retenus vers Transfer (7.J3) : bilan, puis copie confirmee.
  // Kits (7.J5) : pads des packs sous la grille, puis des sous-kits du pack
  // choisi ; un pad filtre grille et listes sur le kit (reserve hors plafond
  // comprise), porte ses tags (herites par ses fichiers) et sa corbeille.
  // Vue kit : arborescence BRANCHE / dossier / fichiers (case finale, retenus,
  // reserve, hors plafond), puis un dossier des non classes du kit.
  // Vue par type (7.K) : un filtre d'instrument liste a droite tous les
  // fichiers du type par sous-dossier ; un kit ne filtre que cette vue (sans
  // ses sous-dossiers vides), l'arbre de gauche ne bouge pas.
  // Barre de recherche (7.J6) : texte, tags (manuels, de kit, inferes des
  // dossiers), kits, instruments, rythmique / melodique, one-shot / boucle,
  // etoiles ; ET entre facettes, OU dans une facette ; filtre toute la page.
  // Propositions : historique des filtres en plus des facettes ; deck de la
  // telecommande de la barre generale (lecture, boucle, sample precedent / suivant).
  import { onDestroy, onMount } from 'svelte'
  import WaveSurfer from 'wavesurfer.js'
  import { remote } from './remote.svelte'
  import { loadHistory, pushHistory } from './history'
  import { api, type LooseSample, type SampleCell, type SampleEntry, type SampleExportReport, type SampleKit, type SampleKits, type SampleStatus, type FacetTag, type FacetNote, type SampleFilter } from './api'

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
  const RHYTHM = ['BD', 'SD', 'CP', 'HH', 'OH', 'CY', 'TM', 'PC', 'BR', 'DL', 'PL']
  const MELODIC = ['BS', 'BL', 'ST', 'ML', 'PD', 'VX', 'FX', 'RS']
  const CODE_ORDER = [...RHYTHM, ...MELODIC]
  const CODE_HELP: Record<string, string> = {
    BD: 'Kick (bass drum) · track 1', SD: 'Snare (caisse claire) · track 3', CP: 'Clap · track 3',
    HH: 'Hat fermé · track 4', OH: 'Hat ouvert · track 5', CY: 'Cymbale, ride, crash · track 6',
    TM: 'Tom · track 7 (perc A)', PC: 'Percussion (conga, shaker, cowbell…) · tracks 7-8',
    BR: 'Boucle break (amen…) · rythmique', DL: 'Boucle drums · rythmique', PL: 'Boucle percussions, hats, tops · rythmique',
    BS: 'Basse one-shot · track 9', BL: 'Boucle de basse · track 9', ST: 'Stab, accord, synthé, instrument · track 10',
    ML: 'Boucle mélodique (lead, séquence, accords) · track 10', PD: 'Nappe, pad, drone · track 11',
    VX: 'Voix, samples parlés · track 14', FX: 'FX de transition (riser, impact, noise…) · track 15',
    RS: 'Resample, enregistrement maison · track 16 (joker)',
  }
  // libelle court d'un code pour l'arbre : « Kick (bass drum) · track 1 » -> « Kick, bass drum »
  // track(s) de la doctrine sur deux chiffres : « track 1 » -> « 01 », « tracks 7-8 » -> « 07-08 »
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
  type View = { kind: 'cell'; folder: string } | { kind: Loose } | { kind: 'kit' } | { kind: 'type' }

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
  let sel = $state<Set<string>>(new Set())    // selection multiple (Cmd / Maj)
  let anchor: string | null = null            // origine d'une plage Maj-clic
  let showReserve = $state(false)
  // hors plafond de toute la case (2e appui sur R) ; avec un kit, toujours la
  let showOverflow = $state(false)
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
  // changement de case (M) : statut garde, rang en fin de case
  let moving = $state<{ sources: string[]; label: string; folder: string } | null>(null)
  let moveSelect: HTMLSelectElement | undefined = $state()
  // glisser-deposer : sources tirees, cible survolee (dossier ou "trash")
  let dragging = $state<string[] | null>(null)
  // export (7.J3) : bilan (dry_run) puis rapport de la copie
  let exportReport = $state<SampleExportReport | null>(null)
  let exporting = $state(false)
  let dropKey = $state<string | null>(null)
  // kit (prefixe de chemin : pack ou pack/sous-kit), '' = tous
  let kit = $state('')
  let kitData = $state<SampleKits>({ kits: [], tags: {} })
  let kitTagInput = $state('')

  let container: HTMLDivElement | undefined = $state()
  let ws: WaveSurfer | null = null

  const current = $derived(view?.kind === 'cell' ? view : null)
  // ordre : celui des dossiers cibles (branche, code, racine puis sous-categories),
  // les dossiers SAMPLE (hors cibles) en fin, par code
  const folderRank = (f: string) => {
    const i = allFolders.indexOf(f)
    return i >= 0 ? i : 1e3 + codeRank(splitFolder(f).code)
  }
  // filtre actif : seuls les dossiers qui y repondent (M cible toujours tous les dossiers)
  const folderList = $derived([...new Set([...(filterOn() ? [] : allFolders), ...cells.map(c => c.folder)])]
    .sort((a, b) => folderRank(a) - folderRank(b)))
  const byKey = $derived(new Map(cells.map(c => [c.folder, c])))
  // total d'un dossier / d'un type : candidats + hors plafond
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
      selected: cs.reduce((n, c) => n + c.selected, 0), toListen: cs.reduce((n, c) => n + c.to_listen, 0),
    }
  }).filter(b => b.codes.length))
  const shown = $derived(entries)
  const chosen = $derived(shown.filter(e => e.selected))
  const reserve = $derived(shown.filter(e => !e.selected))
  // ordre de navigation : la selection, puis la reserve si elle est depliee
  // arborescence du kit : branches (ordre de l'arbre), dossiers, puis non classes
  type Folder = { key: string; label: string; code: string; rows: SampleEntry[]; selected: number }
  type FamFolder = { key: string; label: string; folders: Folder[]; selected: number; total: number }
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
        rows, selected: branch ? rows.filter(r => r.selected).length : 0,
      }))
      return {
        key: branch || ':nc', label: branch || 'Non classés', folders,
        selected: folders.reduce((n, f) => n + f.selected, 0),
        total: folders.reduce((n, f) => n + f.rows.length, 0),
      }
    })
  })
  const visible = $derived(view?.kind === 'kit' || view?.kind === 'type'
    ? tree.flatMap(f => collapsed.has(f.key) ? [] : f.folders.flatMap(c => collapsed.has(c.key) ? [] : c.rows))
    : showReserve ? [...chosen, ...reserve] : chosen)

  /** Clic sur un code de l'arbre : ajoute / retire le filtre d'instrument (vue par type). */
  function toggleCode(code: string) {
    const cur = search.codes ?? []
    const codes = cur.includes(code) ? cur.filter(c => c !== code) : [...cur, code]
    setSearch({ ...search, codes: codes.length ? codes : undefined })
  }

  /** Vue par type : deplie et montre le dossier dans l'arborescence de droite. */
  function reveal(folder: string) {
    const s = new Set(collapsed)
    s.delete(folder)
    s.delete(splitFolder(folder).branch)
    collapsed = s
    queueMicrotask(() => document.getElementById(`t-${folder}`)?.scrollIntoView({ block: 'start', behavior: 'smooth' }))
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
  const totals = $derived(cells.reduce((a, c) => ({
    selected: a.selected + c.selected, keep: a.keep + c.keep, toListen: a.toListen + c.to_listen,
    files: a.files + total(c),
  }), { selected: 0, keep: 0, toListen: 0, files: 0 }))
  const targetCount = $derived(sel.size || (cursor ? 1 : 0))

  type Pad = { kit: string; label: string; selected: number; files: number; trashed: boolean }
  const files = (k: SampleKit) => k.candidates + k.reserve + k.unclassified + k.trashed
  // pads de packs (sommes des sous-kits) ; un pack est barre si tout est a la corbeille
  const packs = $derived.by(() => {
    const out = new Map<string, Pad>()
    for (const k of kitData.kits) {
      const p = out.get(k.pack) ?? { kit: k.pack, label: k.pack, selected: 0, files: 0, trashed: true }
      p.selected += k.selected
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
  const rightF = $derived(notes.length ? { ...search, notes } : search)
  async function toggleNote(n: string) {
    notes = notes.includes(n) ? notes.filter(x => x !== n) : [...notes, n]
    try { localStorage.setItem(NOTES_KEY, JSON.stringify(notes)) } catch { /* stockage indisponible */ }
    await loadEntries()
    if (!visible.some(e => e.source === cursor)) pick(visible[0]?.source ?? null)
  }
  /** La barre ne garde que texte, tags, kits et instruments (7.K). */
  function onlyBar(f: SampleFilter): SampleFilter {
    const { section: _s, kind: _k, minStars: _m, notes: _n, ...rest } = f
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
      const [c, u, t, tags, k, fa, wh] = await Promise.all([
        api.sampleCells(search, search.codes?.length ? '' : kit),
        api.sampleLoose('unclassified', kit, search), api.sampleLoose('trash', kit, search), api.sampleTags(),
        api.sampleKits(search), api.sampleFacets(), api.sampleNotes(),
      ])
      cells = c
      facets = fa
      wheel = wh
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
      entries = await api.sampleTree(rightF, kit).catch(() => [])
      return
    }
    if (v.kind === 'kit') {
      const t = await api.sampleKitTree(kit, rightF).catch(() => ({ entries: [], unclassified: [] }))
      entries = [...t.entries, ...t.unclassified.map(looseRow)]
      return
    }
    entries = v.kind === 'cell'
      ? await api.sampleCell(v.folder, kit, showOverflow, rightF).catch(() => [])
      : (await api.sampleLoose(v.kind, kit, rightF)).map(looseRow)
  }

  async function open(v: View) {
    view = v
    sel = new Set()
    moving = null
    const key = v.kind === 'cell' ? v.folder : `:${v.kind}`
    try { localStorage.setItem(VIEW_KEY, key) } catch { /* stockage indisponible */ }
    await loadEntries()
    const first = visible.find(e => e.status === 'pending') ?? visible[0]
    pick(first?.source ?? null)
  }

  function pick(source: string | null) {
    cursor = source
    if (!source || !ws) return
    ws.load(api.sampleAudioUrl(source)).catch(() => { /* chargement remplace par le suivant */ })
    document.getElementById(`s-${CSS.escape(source)}`)?.scrollIntoView({ block: 'nearest' })
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

  async function decide(status: SampleStatus) {
    if (!current && view?.kind !== 'kit') return
    // vue kit : les non classes n'ont pas de case (M pour leur en donner une)
    const sources = targets().filter(s => entries.find(e => e.source === s)?.folder)
    const single = sel.size ? null : cursor
    if (!(await act(s => api.sampleStatus(s, status), sources)) || !single || status === 'pending') return
    // ecoute : prochain retenu encore a ecouter apres celui-ci, sinon le premier
    const pend = entries.filter(e => e.selected && e.status === 'pending')
    const order = entries.map(e => e.source)
    const after = pend.find(e => order.indexOf(e.source) > order.indexOf(single))
    pick((after ?? pend[0])?.source ?? single)
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

  function startMove() {
    const sources = targets()
    if (!sources.length || view?.kind === 'trash') return
    const one = entries.find(e => e.source === sources[0])
    moving = {
      sources,
      label: sources.length > 1 ? `${sources.length} samples` : one?.name ?? sources[0],
      folder: current?.folder ?? (one?.folder && !one.folder.startsWith('SAMPLE/') ? one.folder : 'DRUMS/PC'),
    }
    queueMicrotask(() => moveSelect?.focus())
  }

  async function confirmMove() {
    if (!moving) return
    const m = moving
    if (current && m.folder === current.folder) { moving = null; return }
    const { code, sub } = splitFolder(m.folder)
    if (await act(s => api.sampleMove(s, code, sub), m.sources)) moving = null
  }

  function onMoveKey(e: KeyboardEvent) {
    if (e.key === 'Enter') { e.preventDefault(); confirmMove() }
    else if (e.key === 'Escape') { e.preventDefault(); moving = null }
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
    if (ev.dataTransfer) ev.dataTransfer.effectAllowed = 'move'
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

  /** Depot sur un dossier (rangement) ou sur la corbeille. */
  function onDrop(ev: DragEvent, target: string) {
    ev.preventDefault()
    const sources = dragging
    onDragEnd()
    if (!sources) return
    if (target === 'trash') toTrash(sources)
    else {
      const { code, sub } = splitFolder(target)
      act(s => api.sampleMove(s, code, sub), sources)
    }
  }

  async function runExport(dryRun: boolean) {
    if (exporting) return
    exporting = true
    try {
      exportReport = await api.sampleExport(dryRun)
      error = ''
    } catch (e) {
      fail(e)
    } finally {
      exporting = false
    }
  }

  const mo = (b: number) => `${Math.round(b / 1e6)} Mo`

  /** Choisit un kit (re-clic : retour a tous) ; la reserve du kit est depliee. */
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
    showReserve = kit !== ''
    showOverflow = false
    try { localStorage.setItem(KIT_KEY, kit) } catch { /* stockage indisponible */ }
    collapsed = new Set()
    await refresh()
    if (search.codes?.length) await open({ kind: 'type' })
    else if (kit) await open({ kind: 'kit' })
    else if (view?.kind === 'kit') {
      const c = cells.find(x => x.to_listen > 0) ?? cells[0]
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
    if (!confirm(`Mettre ${kit} à la corbeille (${n} fichiers) ? Les décisions d’écoute de ses fichiers seront perdues ; restaurable d’un bloc.`)) return
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

  /** R : reserve, puis hors plafond (sans kit), puis tout replie. */
  async function toggleReserve() {
    const c = current ? byKey.get(current.folder) : undefined
    if (!showReserve) showReserve = true
    else if (!showOverflow && !kit && c?.reserve) showOverflow = true
    else { showReserve = kit !== ''; showOverflow = false }
    await loadEntries()
    if (!visible.some(e => e.source === cursor)) pick(visible[0]?.source ?? null)
  }


  function onkey(e: KeyboardEvent) {
    const t = e.target as HTMLElement | null
    if (moving) return
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable)) return
    if (document.querySelector('aside.panel, aside.kb')) return
    if (!container?.offsetParent) return  // vue masquee (autre section du panneau lateral)
    const k = e.key
    if ((e.metaKey || e.ctrlKey) && (k === 'a' || k === 'A')) { sel = new Set(visible.map(x => x.source)); e.preventDefault(); return }
    if (e.metaKey || e.ctrlKey || e.altKey) return
    const trashView = view?.kind === 'trash'
    if (k === 'k' || k === 'K') decide('keep')
    else if (k === 'd' || k === 'D') decide('drop')
    else if (k === 'u' || k === 'U') { if (trashView) restore(); else decide('pending') }
    else if (k === 'ArrowDown') step(1)
    else if (k === 'ArrowUp') step(-1)
    else if (k === 'ArrowRight') stepCell(1)
    else if (k === 'ArrowLeft') stepCell(-1)
    else if (k === ' ') { ws?.stop(); ws?.play() }
    else if (k === 'r' || k === 'R') toggleReserve()
    else if (k === 'm' || k === 'M') startMove()
    else if (k === 't' || k === 'T') tagField?.focus()
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
    try { kit = localStorage.getItem(KIT_KEY) ?? ''; showReserve = kit !== '' } catch { /* stockage indisponible */ }
    try {
      const saved = JSON.parse(localStorage.getItem(SEARCH_KEY) ?? '{}') as SampleFilter
      search = onlyBar(saved)
      notes = JSON.parse(localStorage.getItem(NOTES_KEY) ?? 'null') ?? saved.notes ?? []
    } catch { search = {} }
    await refresh()
    if (kit && !kitData.kits.some(k => k.kit === kit || k.pack === kit)) { kit = ''; await refresh() }
    let last: string | null = null
    try { last = localStorage.getItem(VIEW_KEY) } catch { /* stockage indisponible */ }
    if (search.codes?.length) return open({ kind: 'type' })
    if (last === ':kit' && kit) return open({ kind: 'kit' })
    if (last === ':unclassified' || last === ':trash') return open({ kind: last.slice(1) as Loose })
    const c = (last && byKey.get(last)) || cells.find(x => x.to_listen > 0) || cells[0]
    if (c) await open({ kind: 'cell', folder: c.folder })
  })
  onDestroy(() => ws?.destroy())

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

<svelte:window onkeydown={onkey} />

{#snippet folderNode(f: string, sub: string)}
  {@const c = byKey.get(f)}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <span class="drop" class:over={dropKey === f}
    ondragover={e => onDragOver(e, f)} ondragleave={() => { if (dropKey === f) dropKey = null }}
    ondrop={e => onDrop(e, f)}>
    {#if c}
      <button class="cell" class:done={c.to_listen === 0} class:on={current?.folder === f}
        title="{f} : {c.candidates} candidats, plafond {c.quota ?? 'aucun'}, {c.keep} gardés, {c.drop} écartés, {c.flagged} signalés{c.reserve ? `, ${c.reserve} hors plafond` : ''}"
        onclick={() => (view?.kind === 'type' ? reveal(f) : open({ kind: 'cell', folder: f }))}><span class="sub">{sub}</span><span class="n">{c.to_listen}/{c.selected} <span class="tot">({total(c)})</span>{#if c.reserve && kit && !typeMode}<sup>+{c.reserve}</sup>{/if}</span></button>
    {:else}
      <span class="slot" title="{f} : vide, glisse-en un ici ou M"><span class="sub">{sub}</span><span class="n">vide</span></span>
    {/if}
  </span>
{/snippet}

<div class="samples">
  <section class="grid">
   <div class="zone matrix">
    <h3 class="lib-title" title="{totals.keep} gardés · {totals.toListen} à écouter sur {totals.selected} retenus{filterOn() ? ' (filtrés)' : ''}. Les chiffres d’un dossier : à écouter / retenus (total).">Library</h3>
    <p class="lib-total small muted">
      {search.codes?.length ? `${search.codes.join(', ')} : ` : ''}{totals.files.toLocaleString('fr-FR')} fichiers{searchOn() ? ' filtrés' : ''},
      toutes branches · {totals.selected.toLocaleString('fr-FR')} retenus
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
    <div class="branches" class:dragging={dragging !== null}>
      {#each branchRows as b (b.branch)}
        <div class="branch">
          <button class="fold small" title={BRANCH_HELP[b.branch] ?? b.branch} onclick={() => toggleBranch(b.branch)}>
            <span class="caret">{closedBranches.has(b.branch) ? '▸' : '▾'}</span> <strong>{b.branch}</strong>
            <span class="muted">{b.toListen}/{b.selected}</span>
          </button>
          {#if !closedBranches.has(b.branch)}
            {#each b.codes as row (row.code)}
              {@const root = row.folders.find(f => !splitFolder(f).sub)}
              <div class="code-node">
                <button class="code-label" class:mel={!RHYTHM.includes(row.code)} class:loop={LOOPS.includes(row.code)}
                  class:active={search.codes?.includes(row.code)} onclick={() => toggleCode(row.code)}
                  title="{codeTitle(row.code)} · clic : filtre d'instrument"><span class="acr">{row.code}</span>{#if codeTrack(row.code)}<span class="trk">{codeTrack(row.code)}</span>{/if} <span class="desc">({codeShort(row.code)})</span></button>
                {#if root}{@render folderNode(root, '')}{/if}
                {#if row.folders.length > 1}<span class="tot code-tot" title="total du type {row.code} : candidats + hors plafond">({codeTotal(row.folders)})</span>{/if}
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
        title="Fichiers sans code : glisse-les vers une case (ou M)"
        onclick={() => open({ kind: 'unclassified' })}>Non classés ({counts.unclassified})</button>
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <span class="trash-drop" class:over={dropKey === 'trash'}
        ondragover={e => onDragOver(e, 'trash')} ondragleave={() => { if (dropKey === 'trash') dropKey = null }}
        ondrop={e => onDrop(e, 'trash')}>
        <button class="small" aria-pressed={view?.kind === 'trash'}
          title="Sons rejetés partout, restaurables, jamais supprimés du disque"
          onclick={() => open({ kind: 'trash' })}>Corbeille ({counts.trash})</button>
      </span>
      <button class="small export-btn" disabled={exporting}
        title="Copie les retenus vers Live/samples (branche / code / sous-dossier / nom DT2), pour Transfer"
        onclick={() => runExport(true)}>{exporting ? 'Export…' : 'Exporter…'}</button>
    </div>
    {#if exportReport}
      {@const r = exportReport}
      <div class="export small">
        <strong>{r.dry_run ? 'Bilan de l’export' : 'Export terminé'}</strong>
        <span class="muted">→ {r.dest}</span>
        <p>
          {r.files} retenus ({mo(r.bytes)}) : {r.copied.length} {r.dry_run ? 'à copier' : 'copiés'},
          {r.unchanged} inchangés, {r.removed.length} {r.dry_run ? 'à retirer' : 'retirés'}.
        </p>
        {#if r.missing.length}<p class="err">Sources absentes ({r.missing.length}) : {r.missing.slice(0, 5).join(', ')}</p>{/if}
        {#if r.conflicts.length}<p class="err">Fichiers posés à la main, non écrasés ({r.conflicts.length}) : {r.conflicts.slice(0, 5).join(', ')}</p>{/if}
        {#if r.dry_run}
          <button class="small" disabled={exporting || (!r.copied.length && !r.removed.length)}
            onclick={() => runExport(false)}>{exporting ? 'Copie…' : 'Copier'}</button>
        {/if}
        <button class="small" onclick={() => (exportReport = null)}>{r.dry_run ? 'Annuler' : 'Fermer'}</button>
      </div>
    {/if}
   </div>
    <section class="kits zone">
      <h3 class="small">Kits <span class="muted">· retenus / fichiers · re-clic pour tout voir · double-clic pour tagger</span></h3>
      {#if kit && kitPanel}
        <div class="kit-bar small">
          <strong title={kit}>{kit}</strong>
          {#if kitInfo}<span class="muted">{kitInfo.candidates} candidats · {kitInfo.reserve} hors plafond · {kitInfo.unclassified} non classés</span>{/if}
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
            <span class="pad-n">{p.trashed ? 'corbeille' : `${p.selected} / ${p.files}`}</span>
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
              <span class="pad-n">{k.trashed_kit ? 'corbeille' : `${k.selected} / ${files(k)}`}{k.unclassified ? ` · ${k.unclassified} nc` : ''}</span>
              {#if kitData.tags[k.kit]?.length}<span class="pad-tags">{kitData.tags[k.kit].join(' · ')}</span>{/if}
            </button>
          {/each}
        </div>
      {/if}
    </section>
  </section>

  <section class="detail">
    <header>
      <strong>{current ? current.folder.replaceAll('/', ' / ') : view?.kind === 'type' ? `Type ${search.codes?.join(', ')}${kit ? ` · kit ${kit}` : ''}` : view?.kind === 'kit' ? `Kit ${kit}` : view?.kind === 'unclassified' ? 'Non classés' : view?.kind === 'trash' ? 'Corbeille' : 'Choisis une case'}</strong>
      {#if current}
        {@const c = byKey.get(current.folder)}
        {#if c}<span class="muted small">quota {c.quota ?? 'tout'} · {c.keep} gardés · {c.drop} écartés · {c.candidates} candidats{c.reserve ? ` · ${c.reserve} hors plafond` : ''}</span>{/if}
      {:else if view}
        <span class="muted small">{shown.length} fichiers</span>
      {/if}
      <label class="small"><input type="checkbox" bind:checked={autoplay} /> lecture auto</label>
    </header>
    <div class="wave-row">
      <div class="wave" bind:this={container}></div>
      <svg class="wheel" viewBox="0 0 100 100" role="group" aria-label="Filtrer la liste par note">
        {#each wheel as w, i (w.note)}
          {@const [lx, ly] = polar(37, i * 30)}
          {@const [cx, cy] = polar(24, i * 30)}
          <g role="button" tabindex="-1" class:on={notes.includes(w.note)} class:empty={!w.count}
            onclick={() => toggleNote(w.note)} onkeydown={() => {}}>
            <title>{w.note} : {w.count} sample{w.count > 1 ? 's' : ''}</title>
            <path d={wedge(i)} style="fill-opacity: {0.08 + 0.5 * w.count / wheelMax}" />
            <text x={lx} y={ly} class="wl">{w.note}</text>
            <text x={cx} y={cy} class="wc">{w.count}</text>
          </g>
        {/each}
      </svg>
    </div>
    <div class="toolbar small">
      <span class="count">{sel.size ? `${sel.size} sélectionnés` : cursor ? 'sample en cours' : 'rien'}</span>
      {#if view?.kind === 'trash'}
        <button class="small" disabled={!targetCount || busy} onclick={restore}>Restaurer</button>
      {:else}
        {#if current || view?.kind === 'kit' || view?.kind === 'type'}
          <button class="small" disabled={!targetCount || busy} onclick={() => decide('keep')}>Garder</button>
          <button class="small" disabled={!targetCount || busy} onclick={() => decide('drop')}>Écarter</button>
        {/if}
        <button class="small" disabled={!targetCount || busy} onclick={startMove}>Case…</button>
        <button class="small" disabled={!targetCount || busy} onclick={() => toTrash()}>Corbeille</button>
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
    <p class="keys muted small">
      {#if current || view?.kind === 'kit' || view?.kind === 'type'}<kbd>K</kbd> garder · <kbd>D</kbd> écarter · <kbd>U</kbd> annuler · {/if}
      {#if view?.kind === 'trash'}<kbd>U</kbd> restaurer · {:else}<kbd>Suppr</kbd> corbeille · <kbd>M</kbd> case · {/if}
      <kbd>1</kbd>…<kbd>5</kbd> étoiles, <kbd>0</kbd> sans · <kbd>T</kbd> tag ·
      <kbd>↑</kbd><kbd>↓</kbd> sample · <kbd>←</kbd><kbd>→</kbd> case · <kbd>Espace</kbd> rejouer · <kbd>R</kbd> réserve, puis hors plafond ·
      <kbd>⌘</kbd>/<kbd>Maj</kbd>-clic sélection, <kbd>⌘A</kbd> tout, <kbd>Échap</kbd> aucun · glisser vers une case ou la corbeille
    </p>
    {#if moving}
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div class="move" onkeydown={onMoveKey}>
        <span class="small">Ranger <span class="name">{moving.label}</span> dans</span>
        <select bind:this={moveSelect} bind:value={moving.folder}>
          {#each allFolders as f}<option value={f} title={codeTitle(splitFolder(f).code)}>{f}{splitFolder(f).sub ? '' : ` · ${CODE_HELP[splitFolder(f).code]?.split(' · ')[0] ?? ''}`}</option>{/each}
        </select>
        <button class="small" onclick={confirmMove} disabled={busy}>Ranger</button>
        <button class="small" onclick={() => (moving = null)}>Annuler</button>
        <span class="muted small">statut gardé, rangé en fin de case · <kbd>Entrée</kbd> / <kbd>Échap</kbd></span>
      </div>
    {/if}
    {#if view?.kind === 'trash' && trashedKits.length}
      <ul class="trashed-kits small">
        {#each trashedKits as k (k.kit)}
          <li><span class="name">{k.kit}</span> <span class="muted">kit entier, {k.trashed} fichiers</span>
            <button class="small" disabled={busy} onclick={() => kitAct(() => api.sampleKitRestore(k.kit))}>Restaurer le kit</button></li>
        {/each}
      </ul>
    {/if}
    {#snippet sampleRow(e: SampleEntry)}
      <li id="s-{e.source}" class="row {e.status}" class:cur={e.source === cursor} class:out={!e.selected} class:over={e.overflow}
        class:sel={sel.has(e.source)} draggable={view?.kind !== 'trash'}
        ondragstart={ev => onDragStart(ev, e.source)} ondragend={onDragEnd}>
        <button class="pick" onclick={ev => onRowClick(ev, e.source)}>
          {#if current}<span class="rank muted">{e.rank}</span>{/if}
          <span class="name">{e.name}</span>
          {#if e.stars}<span class="stars" title="{e.stars} étoile{e.stars > 1 ? 's' : ''}">{'★'.repeat(e.stars)}</span>{/if}
          <span class="dur muted small">{fmt(e.duration)}</span>
          {#if e.overflow}<span class="est" title="au-delà du plafond de candidats : garder, écarter, noter ou ranger le fait entrer">hors plafond</span>{/if}
          {#if e.bpm_est}<span class="est" title="tempo estimé par l’audio, non confirmé par la durée">~{e.bpm} bpm</span>{/if}
          {#if e.note_src === 'mesure'}<span class="est" title="note mesurée dans l’audio ({e.note_hz} Hz), à vérifier à l’oreille">~{e.note}</span>{/if}
          {#each e.flags ?? [] as f}<span class="flag" title={FLAG_HELP[f] ?? f}>{f}</span>{/each}
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
        <span class="status small">{e.status === 'keep' ? 'gardé' : e.status === 'drop' ? 'écarté' : (view?.kind === 'kit' || view?.kind === 'type') && e.folder && !e.overflow ? (e.selected ? 'retenu' : 'réserve') : ''}</span>
      </li>
    {/snippet}
    {#if view?.kind === 'kit' || view?.kind === 'type'}
      <ol class="list tree">
        {#each tree as f (f.key)}
          <li class="folder fam">
            <button class="fold" onclick={() => toggleFolder(f.key)}>
              <span class="caret">{collapsed.has(f.key) ? '▸' : '▾'}</span> {f.label}
              <span class="muted small">{f.key === ':nc' ? f.total : `${f.selected} / ${f.total}`}</span>
            </button>
          </li>
          {#if !collapsed.has(f.key)}
            {#each f.folders as c (c.key)}
              {#if f.key !== ':nc'}
                <li class="folder code" id="t-{c.key}" class:mel={!RHYTHM.includes(c.code)}>
                  <button class="fold" title={codeTitle(c.code)} onclick={() => toggleFolder(c.key)}>
                    <span class="caret">{collapsed.has(c.key) ? '▸' : '▾'}</span> {c.label}
                    <span class="muted small">{c.rows.length ? `${c.selected} / ${c.rows.length}` : 'vide'}</span>
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
        {#each visible as e, i (e.source)}
          {#if showReserve && i === chosen.length && reserve.length}<li class="sep small">Réserve ({reserve.length}) · hors sélection</li>{/if}
          {@render sampleRow(e)}
        {/each}
      </ol>
    {/if}
    {#if current && !showReserve && reserve.length}
      <button class="small" onclick={toggleReserve}>Afficher la réserve ({reserve.length})</button>
    {:else if current && showReserve && !showOverflow && !kit && byKey.get(current.folder)?.reserve}
      <button class="small" onclick={toggleReserve}>Afficher les hors plafond ({byKey.get(current.folder)?.reserve})</button>
    {/if}
    {#if view && !visible.length}<p class="muted small">{filterOn() ? 'Aucun sample ne répond au filtre.' : 'Liste vide.'}</p>{/if}
  </section>
</div>

<style>
  .samples { display: grid; grid-template-columns: minmax(280px, 440px) minmax(0, 1fr); grid-template-rows: minmax(0, 1fr); gap: 12px 16px; padding: 12px 16px; height: 100%; min-height: 0; }
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
  .code-node { display: grid; grid-template-columns: minmax(0, auto) minmax(0, 1fr) auto; align-items: center; padding-left: 14px; min-height: 22px; }
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
  .cell.done { background: var(--cell-off); color: var(--muted); }
  .cell.on { outline: 2px solid var(--accent); }
  .slot { color: var(--muted); opacity: 0.6; }
  .branches.dragging .slot { border: 1px dashed var(--border); opacity: 1; }
  .drop.over .cell, .drop.over .slot { outline: 2px dashed var(--accent); background: var(--panel-2); }
  .loose { display: flex; gap: 8px; margin-top: 10px; }
  .trash-drop { border-radius: 4px; }
  .export-btn { margin-left: auto; }
  .export { margin-top: 10px; padding: 8px 10px; border: 1px solid var(--accent); border-radius: 4px; background: var(--panel); max-width: 60ch; }
  .export p { margin: 6px 0; }
  /* largeur de la grille : les pads remplissent la colonne sans l'elargir */
  .kits h3 { margin: 0 0 6px; font-weight: 600; position: sticky; top: -8px; z-index: 1; padding: 4px 0; background: var(--bg); }
  .lib-title { margin: 0 0 2px; font-weight: 600; }
  .lib-total { margin: 0 0 6px; }
  /* trois pads par ligne, a la largeur de la colonne */
  .pads { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; }
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
  .cell sup { position: absolute; top: -7px; right: -3px; font-size: 9px; line-height: 1; padding: 1px 2px; border-radius: 6px; background: var(--panel-2); color: var(--muted); pointer-events: none; }
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
  .keys { margin: 4px 0 8px; }
  kbd { font-family: ui-monospace, Menlo, monospace; font-size: 11px; border: 1px solid var(--border); border-radius: 3px; padding: 0 4px; }
  .list { list-style: none; margin: 0; padding: 0; overflow-y: auto; flex: 1; min-height: 0; }
  .row { display: flex; align-items: center; gap: 6px; border-bottom: 1px solid var(--border); user-select: none; }
  .row.cur { background: var(--panel-2); box-shadow: inset 3px 0 0 var(--accent); }
  .row.sel { background: color-mix(in srgb, var(--accent) 18%, transparent); }
  .row.keep .name { color: var(--rhythm); }
  .row.drop { opacity: 0.5; }
  .row.drop .name { text-decoration: line-through; }
  /* retenus en avant ; reserve puis hors plafond nettement en retrait */
  .row:not(.out):not(.drop):not(.cur):not(.sel) { background: var(--panel); }
  .row:not(.out):not(.drop) .name { font-weight: 600; }
  .row.out { font-size: 12px; }
  .row.out:not(.drop) { opacity: 0.5; }
  .row.out .name { color: var(--muted); }
  .row.over:not(.drop) { opacity: 0.35; font-style: italic; }
  .row.out.cur, .row.out:hover { opacity: 0.9; }
  .pick { flex: 1; min-width: 0; display: flex; gap: 8px; align-items: baseline; background: none; border: 0; padding: 5px 6px; text-align: left; color: var(--text); cursor: pointer; }
  .rank { width: 2.5em; text-align: right; font: 11px ui-monospace, Menlo, monospace; }
  .name { font-family: ui-monospace, Menlo, monospace; white-space: pre; }
  .stars { color: #b45309; font-size: 11px; }
  .dur { width: 5em; }
  .wave-row { display: flex; gap: 10px; align-items: center; }
  .wave-row .wave { flex: 1; min-width: 0; }
  .wheel { width: 80px; height: 80px; flex: none; }
  .wheel g { cursor: pointer; outline: none; }
  .wheel path { fill: var(--accent); stroke: var(--border); stroke-width: 0.6; }
  .wheel g.on path { fill: var(--accent); fill-opacity: 1 !important; stroke: var(--text); }
  .wheel g.empty { opacity: 0.45; }
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
  .status { width: 4em; color: var(--muted); }
  .move { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; padding: 6px 8px; margin-bottom: 6px; border: 1px solid var(--accent); border-radius: 4px; background: var(--panel); }
  .sep { margin-top: 10px; padding: 6px 6px 4px; border-top: 2px dashed var(--border); color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
  .folder .fold { display: flex; gap: 6px; align-items: baseline; width: 100%; background: none; border: 0; border-bottom: 1px solid var(--border); padding: 5px 6px; text-align: left; color: var(--text); cursor: pointer; font-weight: 600; }
  .folder.fam .fold { background: var(--panel); font-size: 13px; }
  .folder.code .fold { padding-left: 22px; font: 600 12px ui-monospace, Menlo, monospace; background: color-mix(in srgb, var(--rhythm) 12%, var(--panel)); color: var(--rhythm); }
  .folder.code.mel .fold { background: color-mix(in srgb, var(--melodic) 12%, var(--panel)); color: var(--melodic); }
  .caret { width: 1em; color: var(--muted); }
  .tree .row { padding-left: 52px; }
  .small { font-size: 12px; }
  .err { color: #dc2626; font-size: 12px; }
  @media (max-width: 900px) {
    .samples { grid-template-columns: 1fr; height: auto; }
    .matrix, .kits { flex: none; max-height: 50vh; }
    .list { max-height: 60vh; }
  }
</style>
