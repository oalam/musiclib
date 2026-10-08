<script lang="ts">
  // Bibliotheque des samples DT2 (7.J2, 7.J4) : grille famille x code, puis
  // une liste (case, non classes ou corbeille). Dans une case : les retenus a
  // ecouter (keep / drop au clavier) et la reserve ; un drop fait monter le
  // candidat suivant (selection recalculee par l'API). Selection multiple
  // (Cmd, Maj), barre d'outils, glisser-deposer vers une case ou la corbeille.
  // Export des retenus vers Transfer (7.J3) : bilan, puis copie confirmee.
  // Kits (7.J5) : pads des packs sous la grille, puis des sous-kits du pack
  // choisi ; un pad filtre grille et listes sur le kit (reserve hors plafond
  // comprise), porte ses tags (herites par ses fichiers) et sa corbeille.
  // Vue kit : arborescence FAMILLE / CODE / fichiers (case finale, retenus,
  // reserve, hors plafond), puis un dossier des non classes du kit.
  // Barre de recherche (7.J6) : texte, tags (manuels, de kit, inferes des
  // dossiers), kits, instruments, rythmique / melodique, one-shot / boucle,
  // etoiles ; ET entre facettes, OU dans une facette ; filtre toute la page.
  import { onDestroy, onMount } from 'svelte'
  import WaveSurfer from 'wavesurfer.js'
  import { api, type LooseSample, type SampleCell, type SampleEntry, type SampleExportReport, type SampleKit, type SampleKits, type SampleStatus, type FacetTag, type SampleFilter } from './api'

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
  const codeTitle = (c: string) => `${c} : ${CODE_HELP[c] ?? c}${LOOPS.includes(c) ? ' (boucle)' : ''}`
  const FAMILIES = ['HARDCORE', 'JUNGLE', 'TRIBE', 'TECHNO', 'DUBSTEP', 'AUTRES', 'UNIVERSEL', 'SAMPLE']
  const codeRank = (c: string) => (CODE_ORDER.includes(c) ? CODE_ORDER.indexOf(c) : CODE_ORDER.length)

  type Loose = 'unclassified' | 'trash'
  type View = { kind: 'cell'; family: string; code: string } | { kind: Loose } | { kind: 'kit' }

  let cells = $state<SampleCell[]>([])
  // colonnes de la grille non filtree : un filtre (kit, tag) ne la redimensionne pas
  let gridCodes = $state<string[]>([])
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
  let allKits = $state<SampleKit[]>([])     // kits sans filtre (suggestions)
  let query = $state('')
  let suggestIdx = $state(0)
  let searchField: HTMLInputElement | undefined = $state()
  let tagInput = $state('')
  let tagField: HTMLInputElement | undefined = $state()
  // changement de case (M) : statut garde, rang en fin de case
  let moving = $state<{ sources: string[]; label: string; family: string; code: string } | null>(null)
  let moveSelect: HTMLSelectElement | undefined = $state()
  // glisser-deposer : sources tirees, cible survolee ("FAM/CODE" ou "trash")
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
  // toutes les familles, meme vides (TRIBE attend son pack) : cibles de rangement
  const families = $derived([...FAMILIES, ...new Set(cells.map(c => c.family).filter(f => !FAMILIES.includes(f)))])
  const codes = $derived([...new Set([...gridCodes, ...cells.map(c => c.code)])].sort((a, b) => codeRank(a) - codeRank(b)))
  const rhythmCols = $derived(codes.filter(c => RHYTHM.includes(c)).length)
  const firstMelodic = $derived(codes.find(c => !RHYTHM.includes(c)))
  const byKey = $derived(new Map(cells.map(c => [`${c.family}/${c.code}`, c])))
  const shown = $derived(entries)
  const chosen = $derived(shown.filter(e => e.selected))
  const reserve = $derived(shown.filter(e => !e.selected))
  // ordre de navigation : la selection, puis la reserve si elle est depliee
  // arborescence du kit : familles (ordre de la grille), codes, puis non classes
  type Folder = { key: string; code: string; rows: SampleEntry[]; selected: number }
  type FamFolder = { key: string; label: string; folders: Folder[]; selected: number; total: number }
  let collapsed = $state<Set<string>>(new Set())
  const tree = $derived.by((): FamFolder[] => {
    if (view?.kind !== 'kit') return []
    const fams = new Map<string, Map<string, SampleEntry[]>>()
    for (const e of shown) {
      const codesOf = fams.get(e.family) ?? new Map<string, SampleEntry[]>()
      codesOf.set(e.code, [...(codesOf.get(e.code) ?? []), e])
      fams.set(e.family, codesOf)
    }
    const famRank = (f: string) => (f === '' ? 1e3 : FAMILIES.includes(f) ? FAMILIES.indexOf(f) : FAMILIES.length)
    return [...fams.entries()].sort(([a], [b]) => famRank(a) - famRank(b)).map(([fam, codesOf]) => {
      const folders = [...codesOf.entries()].sort(([a], [b]) => codeRank(a) - codeRank(b)).map(([code, rows]) => ({
        key: `${fam}/${code}`, code, rows, selected: fam ? rows.filter(r => r.selected).length : 0,
      }))
      return {
        key: fam || ':nc', label: fam || 'Non classés', folders,
        selected: folders.reduce((n, f) => n + f.selected, 0),
        total: folders.reduce((n, f) => n + f.rows.length, 0),
      }
    })
  })
  const visible = $derived(view?.kind === 'kit'
    ? tree.flatMap(f => collapsed.has(f.key) ? [] : f.folders.flatMap(c => collapsed.has(c.key) ? [] : c.rows))
    : showReserve ? [...chosen, ...reserve] : chosen)

  function toggleFolder(key: string) {
    const s = new Set(collapsed)
    if (s.has(key)) s.delete(key)
    else s.add(key)
    collapsed = s
  }
  const totals = $derived(cells.reduce((a, c) => ({
    selected: a.selected + c.selected, keep: a.keep + c.keep, toListen: a.toListen + c.to_listen,
  }), { selected: 0, keep: 0, toListen: 0 }))
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
    return !!(f.q || f.tags?.length || f.kits?.length || f.codes?.length || f.section || f.kind || f.minStars)
  }
  function filterOn(): boolean { return searchOn() || kit !== '' }

  type Sug = { kind: 'text' | 'tag' | 'kit' | 'code'; value: string; hint: string }
  const GROUP_LABEL: Record<string, string> = { genre: 'genre', instrument: 'instrument', mot: 'mot-clé', manuel: 'tag' }
  const suggestions = $derived.by((): Sug[] => {
    const t = query.trim().toLowerCase()
    if (!t) return []
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
    return out.slice(0, 14)
  })

  async function setSearch(f: SampleFilter) {
    search = f
    try { localStorage.setItem(SEARCH_KEY, JSON.stringify(f)) } catch { /* stockage indisponible */ }
    await refresh()
    // la case ouverte ne repond plus au filtre : premiere case qui y repond
    if (current && !byKey.has(`${current.family}/${current.code}`) && ordered.length) {
      await open({ kind: 'cell', family: ordered[0].family, code: ordered[0].code })
      return
    }
    await loadEntries()
    if (!visible.some(e => e.source === cursor)) pick(visible[0]?.source ?? null)
  }

  function addSug(sg: Sug) {
    const f = { ...search }
    if (sg.kind === 'text') f.q = sg.value
    else if (sg.kind === 'tag') f.tags = [...(f.tags ?? []), sg.value]
    else if (sg.kind === 'kit') f.kits = [...(f.kits ?? []), sg.value]
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
    else f.codes = f.codes?.filter(x => x !== value)
    setSearch(f)
  }

  const chips = $derived([
    ...(search.q ? [{ kind: 'text' as const, value: search.q }] : []),
    ...(search.tags ?? []).map(v => ({ kind: 'tag' as const, value: v })),
    ...(search.kits ?? []).map(v => ({ kind: 'kit' as const, value: v })),
    ...(search.codes ?? []).map(v => ({ kind: 'code' as const, value: v })),
  ])

  function onSearchKey(e: KeyboardEvent) {
    if (e.key === 'ArrowDown') { suggestIdx = Math.min(suggestIdx + 1, suggestions.length - 1); e.preventDefault() }
    else if (e.key === 'ArrowUp') { suggestIdx = Math.max(suggestIdx - 1, 0); e.preventDefault() }
    else if (e.key === 'Enter' && suggestions.length) { addSug(suggestions[suggestIdx] ?? suggestions[0]); e.preventDefault() }
    else if (e.key === 'Escape') { query = ''; searchField?.blur(); e.preventDefault() }
    else if (e.key === 'Backspace' && !query && chips.length) { const c = chips[chips.length - 1]; dropChip(c.kind, c.value) }
  }

  const toggle = <K extends 'section' | 'kind'>(key: K, value: SampleFilter[K]) =>
    setSearch({ ...search, [key]: search[key] === value ? undefined : value })

  function cssVar(name: string): string {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  }

  function fail(e: unknown) {
    error = e instanceof Error ? e.message : String(e)
  }

  function looseRow(l: LooseSample, i: number): SampleEntry {
    const name = (l.source.split('/').pop() ?? l.source).replace(/\.wav$/i, '')
    return { source: l.source, family: '', code: '', pack: l.pack, name, duration: null, rank: i + 1,
      status: 'pending', selected: true, flags: null, bpm: null, bpm_est: false, tags: l.tags, stars: l.stars,
      auto_tags: l.auto_tags, overflow: false }
  }

  // grille (filtree), compteurs hors case et tags connus
  async function refresh() {
    try {
      const [c, u, t, tags, k, fa] = await Promise.all([
        api.sampleCells(search, kit),
        api.sampleLoose('unclassified', kit, search), api.sampleLoose('trash', kit, search), api.sampleTags(),
        api.sampleKits(search), api.sampleFacets(),
      ])
      cells = c
      facets = fa
      const [all, ak] = filterOn() ? await Promise.all([api.sampleCells(), api.sampleKits()]) : [c, k]
      gridCodes = [...new Set(all.map(x => x.code))]
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
    if (v.kind === 'kit') {
      const t = await api.sampleKitTree(kit, search).catch(() => ({ entries: [], unclassified: [] }))
      entries = [...t.entries, ...t.unclassified.map(looseRow)]
      return
    }
    entries = v.kind === 'cell'
      ? await api.sampleCell(v.family, v.code, kit, showOverflow, search).catch(() => [])
      : (await api.sampleLoose(v.kind, kit, search)).map(looseRow)
  }

  async function open(v: View) {
    view = v
    sel = new Set()
    moving = null
    const key = v.kind === 'cell' ? `${v.family}/${v.code}` : `:${v.kind}`
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

  const ordered = $derived(families.flatMap(f => codes.map(c => byKey.get(`${f}/${c}`)).filter((c): c is SampleCell => c !== undefined)))

  function stepCell(delta: number) {
    if (!ordered.length) return
    const i = current ? ordered.findIndex(c => c.family === current.family && c.code === current.code) : -1
    const c = ordered[(i + delta + ordered.length) % ordered.length]
    open({ kind: 'cell', family: c.family, code: c.code })
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
    const sources = targets().filter(s => entries.find(e => e.source === s)?.family)
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
      family: current?.family ?? (one?.family || 'UNIVERSEL'),
      code: current?.code ?? (one?.code || 'PC'),
    }
    queueMicrotask(() => moveSelect?.focus())
  }

  async function confirmMove() {
    if (!moving) return
    const m = moving
    if (current && m.family === current.family && m.code === current.code) { moving = null; return }
    if (await act(s => api.sampleMove(s, m.family, m.code), m.sources)) moving = null
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

  function onDrop(ev: DragEvent, target: { family: string; code: string } | 'trash') {
    ev.preventDefault()
    const sources = dragging
    onDragEnd()
    if (!sources) return
    if (target === 'trash') toTrash(sources)
    else act(s => api.sampleMove(s, target.family, target.code), sources)
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
  async function chooseKit(k: string) {
    kit = kit === k ? '' : k
    kitTagInput = ''
    showReserve = kit !== ''
    showOverflow = false
    try { localStorage.setItem(KIT_KEY, kit) } catch { /* stockage indisponible */ }
    collapsed = new Set()
    await refresh()
    if (kit) await open({ kind: 'kit' })
    else if (view?.kind === 'kit') {
      const c = cells.find(x => x.to_listen > 0) ?? cells[0]
      if (c) await open({ kind: 'cell', family: c.family, code: c.code })
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
    const c = current ? byKey.get(`${current.family}/${current.code}`) : undefined
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
    try { kit = localStorage.getItem(KIT_KEY) ?? ''; showReserve = kit !== '' } catch { /* stockage indisponible */ }
    try { search = JSON.parse(localStorage.getItem(SEARCH_KEY) ?? '{}') as SampleFilter } catch { search = {} }
    await refresh()
    if (kit && !kitData.kits.some(k => k.kit === kit || k.pack === kit)) { kit = ''; await refresh() }
    let last: string | null = null
    try { last = localStorage.getItem(VIEW_KEY) } catch { /* stockage indisponible */ }
    if (last === ':kit' && kit) return open({ kind: 'kit' })
    if (last === ':unclassified' || last === ':trash') return open({ kind: last.slice(1) as Loose })
    const c = (last && byKey.get(last)) || cells.find(x => x.to_listen > 0) || cells[0]
    if (c) await open({ kind: 'cell', family: c.family, code: c.code })
  })
  onDestroy(() => ws?.destroy())

  function fmt(d: number | null): string {
    return d == null ? '' : d < 10 ? `${d.toFixed(2)} s` : `${d.toFixed(1)} s`
  }
</script>

<svelte:window onkeydown={onkey} />

<div class="samples">
  <div class="searchbar zone">
    <div class="search-in">
      {#each chips as c (c.kind + c.value)}
        <span class="chip {c.kind}" title={c.kind === 'code' ? codeTitle(c.value) : c.kind}>{c.kind === 'text' ? `« ${c.value} »` : c.value}<button
          class="untag" title="Retirer" onclick={() => dropChip(c.kind, c.value)}>×</button></span>
      {/each}
      <input bind:this={searchField} bind:value={query} onkeydown={onSearchKey} oninput={() => (suggestIdx = 0)}
        placeholder={chips.length ? 'affiner…' : 'Rechercher : texte, tag, genre, instrument (BD, kick…), kit…'} />
      {#if suggestions.length}
        <ul class="suggest">
          {#each suggestions as sg, i (sg.kind + sg.value)}
            <li><button class:on={i === suggestIdx} onmousedown={ev => { ev.preventDefault(); addSug(sg) }}>
              <span class="chip {sg.kind}">{sg.kind === 'text' ? `« ${sg.value} »` : sg.value}</span>
              <span class="muted small">{sg.hint}</span></button></li>
          {/each}
        </ul>
      {/if}
    </div>
    <div class="seg small">
      <button aria-pressed={search.section === 'rhythm'} class="rhythm" onclick={() => toggle('section', 'rhythm')}>Rythmique</button>
      <button aria-pressed={search.section === 'melodic'} class="melodic" onclick={() => toggle('section', 'melodic')}>Mélodique</button>
    </div>
    <div class="seg small">
      <button aria-pressed={search.kind === 'oneshot'} onclick={() => toggle('kind', 'oneshot')}>One-shot</button>
      <button aria-pressed={search.kind === 'loop'} onclick={() => toggle('kind', 'loop')}>Boucle</button>
    </div>
    <select class="small" value={search.minStars ?? 0}
      onchange={ev => setSearch({ ...search, minStars: Number((ev.target as HTMLSelectElement).value) || undefined })}>
      <option value={0}>étoiles : toutes</option>
      {#each [1, 2, 3, 4, 5] as n}<option value={n}>{'★'.repeat(n)}{n < 5 ? ' et +' : ''}</option>{/each}
    </select>
    {#if searchOn()}<button class="small" onclick={() => setSearch({})}>Tout effacer</button>{/if}
  </div>
  <section class="grid">
   <div class="zone matrix">
    <p class="muted small">
      {totals.keep} gardés · {totals.toListen} à écouter sur {totals.selected} retenus.
      Les chiffres d’une case : à écouter / retenus{filterOn() ? ' (filtrés)' : ''}.
    </p>
    {#if error}<p class="err">{error}</p>{/if}
    <table class:dragging={dragging !== null}>
      <thead>
        <tr class="sections">
          <th></th>
          {#if rhythmCols}<th colspan={rhythmCols} class="sec rhythm" title="Tracks 1 à 8 de la doctrine">Rythmique</th>{/if}
          {#if codes.length - rhythmCols}<th colspan={codes.length - rhythmCols} class="sec melodic first" title="Tracks 9 à 16 de la doctrine">Mélodique</th>{/if}
        </tr>
        <tr><th></th>{#each codes as code}<th class:loop={LOOPS.includes(code)} class:mel={!RHYTHM.includes(code)} class:first={code === firstMelodic}
          title={codeTitle(code)}>{code}</th>{/each}</tr>
      </thead>
      <tbody>
        {#each families as fam}
          <tr>
            <th class:empty={!cells.some(c => c.family === fam)}
              title={cells.some(c => c.family === fam) ? '' : 'aucun sample : glisse-en un ici ou M'}>{fam}</th>
            {#each codes as code}
              {@const c = byKey.get(`${fam}/${code}`)}
              {@const key = `${fam}/${code}`}
              <!-- svelte-ignore a11y_no_static_element_interactions -->
              <td class:first={code === firstMelodic} class:over={dropKey === key}
                ondragover={e => onDragOver(e, key)} ondragleave={() => { if (dropKey === key) dropKey = null }}
                ondrop={e => onDrop(e, { family: fam, code })}>
                {#if c}
                  <button class="cell" class:done={c.to_listen === 0}
                    class:on={current?.family === fam && current?.code === code}
                    title="{fam}/{code} : {c.candidates} candidats, {c.keep} gardés, {c.drop} écartés, {c.flagged} signalés{c.reserve ? `, ${c.reserve} hors plafond` : ''}"
                    onclick={() => open({ kind: 'cell', family: fam, code })}>{c.to_listen}/{c.selected}{#if c.reserve && kit}<sup>+{c.reserve}</sup>{/if}</button>
                {:else}
                  <span class="slot" title="{fam}/{code}"></span>
                {/if}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
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
        title="Copie les retenus vers Live/samples (famille / code / nom DT2), pour Transfer"
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
      <h3 class="small">Kits <span class="muted">· retenus / fichiers · re-clic pour tout voir</span></h3>
      {#if kit}
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
        </div>
      {/if}
      <div class="pads">
        {#each packs as p (p.kit)}
          <button class="pad" class:on={activePack === p.kit} class:gone={p.trashed}
            title={p.kit} onclick={() => chooseKit(p.kit)}>
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
              title={k.kit} onclick={() => chooseKit(kit === k.kit ? activePack : k.kit)}>
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
      <strong>{current ? `${current.family} / ${current.code}` : view?.kind === 'kit' ? `Kit ${kit}` : view?.kind === 'unclassified' ? 'Non classés' : view?.kind === 'trash' ? 'Corbeille' : 'Choisis une case'}</strong>
      {#if current}
        {@const c = byKey.get(`${current.family}/${current.code}`)}
        {#if c}<span class="muted small">quota {c.quota ?? 'tout'} · {c.keep} gardés · {c.drop} écartés · {c.candidates} candidats{c.reserve ? ` · ${c.reserve} hors plafond` : ''}</span>{/if}
      {:else if view}
        <span class="muted small">{shown.length} fichiers</span>
      {/if}
      <label class="small"><input type="checkbox" bind:checked={autoplay} /> lecture auto</label>
    </header>
    <div class="wave" bind:this={container}></div>
    <div class="toolbar small">
      <span class="count">{sel.size ? `${sel.size} sélectionnés` : cursor ? 'sample en cours' : 'rien'}</span>
      {#if view?.kind === 'trash'}
        <button class="small" disabled={!targetCount || busy} onclick={restore}>Restaurer</button>
      {:else}
        {#if current || view?.kind === 'kit'}
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
      {#if current || view?.kind === 'kit'}<kbd>K</kbd> garder · <kbd>D</kbd> écarter · <kbd>U</kbd> annuler · {/if}
      {#if view?.kind === 'trash'}<kbd>U</kbd> restaurer · {:else}<kbd>Suppr</kbd> corbeille · <kbd>M</kbd> case · {/if}
      <kbd>1</kbd>…<kbd>5</kbd> étoiles, <kbd>0</kbd> sans · <kbd>T</kbd> tag ·
      <kbd>↑</kbd><kbd>↓</kbd> sample · <kbd>←</kbd><kbd>→</kbd> case · <kbd>Espace</kbd> rejouer · <kbd>R</kbd> réserve, puis hors plafond ·
      <kbd>⌘</kbd>/<kbd>Maj</kbd>-clic sélection, <kbd>⌘A</kbd> tout, <kbd>Échap</kbd> aucun · glisser vers une case ou la corbeille
    </p>
    {#if moving}
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div class="move" onkeydown={onMoveKey}>
        <span class="small">Ranger <span class="name">{moving.label}</span> dans</span>
        <select bind:this={moveSelect} bind:value={moving.family}>
          {#each FAMILIES as f}<option value={f}>{f}</option>{/each}
        </select>
        <select bind:value={moving.code}>
          {#each CODE_ORDER as c}<option value={c} title={codeTitle(c)}>{c} · {CODE_HELP[c]?.split(' · ')[0] ?? ''}</option>{/each}
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
      <li id="s-{e.source}" class="row {e.status}" class:cur={e.source === cursor} class:out={!e.selected}
        class:sel={sel.has(e.source)} draggable={view?.kind !== 'trash'}
        ondragstart={ev => onDragStart(ev, e.source)} ondragend={onDragEnd}>
        <button class="pick" onclick={ev => onRowClick(ev, e.source)}>
          {#if current}<span class="rank muted">{e.rank}</span>{/if}
          <span class="name">{e.name}</span>
          {#if e.stars}<span class="stars" title="{e.stars} étoile{e.stars > 1 ? 's' : ''}">{'★'.repeat(e.stars)}</span>{/if}
          <span class="dur muted small">{fmt(e.duration)}</span>
          {#if e.overflow}<span class="est" title="au-delà du plafond de candidats : garder, écarter, noter ou ranger le fait entrer">hors plafond</span>{/if}
          {#if e.bpm_est}<span class="est" title="tempo estimé par l’audio, non confirmé par la durée">~{e.bpm} bpm</span>{/if}
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
        <span class="status small">{e.status === 'keep' ? 'gardé' : e.status === 'drop' ? 'écarté' : view?.kind === 'kit' && e.family && !e.overflow ? (e.selected ? 'retenu' : 'réserve') : ''}</span>
      </li>
    {/snippet}
    {#if view?.kind === 'kit'}
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
                <li class="folder code" class:mel={!RHYTHM.includes(c.code)}>
                  <button class="fold" title={codeTitle(c.code)} onclick={() => toggleFolder(c.key)}>
                    <span class="caret">{collapsed.has(c.key) ? '▸' : '▾'}</span> {c.code}
                    <span class="muted small">{c.selected} / {c.rows.length}</span>
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
          {#if showReserve && i === chosen.length && reserve.length}<li class="sep muted small">Réserve ({reserve.length})</li>{/if}
          {@render sampleRow(e)}
        {/each}
      </ol>
    {/if}
    {#if current && !showReserve && reserve.length}
      <button class="small" onclick={toggleReserve}>Afficher la réserve ({reserve.length})</button>
    {:else if current && showReserve && !showOverflow && !kit && byKey.get(`${current.family}/${current.code}`)?.reserve}
      <button class="small" onclick={toggleReserve}>Afficher les hors plafond ({byKey.get(`${current.family}/${current.code}`)?.reserve})</button>
    {/if}
    {#if view && !visible.length}<p class="muted small">{filterOn() ? 'Aucun sample ne répond au filtre.' : 'Liste vide.'}</p>{/if}
  </section>
</div>

<style>
  .samples { display: grid; grid-template-columns: minmax(0, auto) minmax(0, 1fr); grid-template-rows: auto minmax(0, 1fr); gap: 12px 16px; padding: 12px 16px; height: 100%; min-height: 0; }
  .searchbar { grid-column: 1 / -1; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .search-in { position: relative; flex: 1; min-width: 280px; display: flex; flex-wrap: wrap; gap: 4px; align-items: center; border: 1px solid var(--border); border-radius: 4px; padding: 3px 6px; background: var(--panel); }
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
  .seg { display: inline-flex; }
  .seg button { border-radius: 0; margin-left: -1px; }
  .seg button:first-child { border-radius: 4px 0 0 4px; }
  .seg button:last-child { border-radius: 0 4px 4px 0; }
  .seg button[aria-pressed='true'] { background: var(--panel-2); outline: 1px solid var(--accent); z-index: 1; }
  .seg button.rhythm[aria-pressed='true'] { color: var(--rhythm); }
  .seg button.melodic[aria-pressed='true'] { color: var(--melodic); }
  .tag.auto { border-style: dotted; background: none; cursor: pointer; padding: 0 6px; }
  .grid { overflow: auto; }
  .filters { display: flex; gap: 10px; margin: 0 0 6px; }
  table { border-collapse: collapse; font-size: 12px; }
  th { font-weight: 600; padding: 2px 4px; text-align: left; }
  thead th { text-align: center; font-family: ui-monospace, Menlo, monospace; }
  td { padding: 1px; }
  th.empty { color: var(--muted); font-weight: 400; }
  thead th { color: var(--rhythm); cursor: help; }
  thead th.mel { color: var(--melodic); }
  thead th.loop { font-style: italic; text-decoration: underline dotted; }
  tr.sections th { font: 600 10px system-ui, sans-serif; text-transform: uppercase; letter-spacing: 0.06em; padding: 0 4px 2px; border-bottom: 1px solid var(--border); }
  tr.sections th.rhythm { color: var(--rhythm); }
  tr.sections th.melodic { color: var(--melodic); }
  .first { border-left: 2px solid var(--border); padding-left: 6px; }
  .zone { box-sizing: border-box; border: 1px solid var(--border); border-radius: 6px; padding: 8px 10px; }
  .cell { width: 44px; font: 11px ui-monospace, Menlo, monospace; padding: 3px 0; border: 1px solid var(--border); background: var(--panel); color: var(--text); border-radius: 3px; cursor: pointer; }
  .cell.done { background: var(--cell-off); color: var(--muted); }
  .cell.on { outline: 2px solid var(--accent); }
  .slot { display: block; width: 44px; height: 21px; border-radius: 3px; }
  table.dragging .slot { border: 1px dashed var(--border); }
  td.over .cell, td.over .slot { outline: 2px dashed var(--accent); background: var(--panel-2); }
  .loose { display: flex; gap: 8px; margin-top: 10px; }
  .trash-drop { border-radius: 4px; }
  .export-btn { margin-left: auto; }
  .export { margin-top: 10px; padding: 8px 10px; border: 1px solid var(--accent); border-radius: 4px; background: var(--panel); max-width: 60ch; }
  .export p { margin: 6px 0; }
  /* largeur de la grille : les pads remplissent la colonne sans l'elargir */
  .kits { margin-top: 12px; width: 0; min-width: 100%; }
  .kits h3 { margin: 0 0 6px; font-weight: 600; }
  .pads { display: flex; flex-wrap: wrap; gap: 6px; }
  .pads.subs { margin-top: 8px; padding-top: 8px; border-top: 1px dashed var(--border); }
  .pad { display: flex; flex-direction: column; justify-content: center; align-items: flex-start; gap: 2px; width: 128px; min-height: 58px; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--panel); color: var(--text); cursor: pointer; text-align: left; }
  .pad.sub { width: 116px; min-height: 50px; }
  .pad:hover { background: var(--panel-2); }
  .pad.on { outline: 2px solid var(--accent); background: var(--panel-2); }
  .pad.gone { opacity: 0.5; }
  .pad.gone .pad-name { text-decoration: line-through; }
  .pad-name { font-size: 13px; font-weight: 600; line-height: 1.15; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow-wrap: anywhere; }
  .pad-n { font: 11px ui-monospace, Menlo, monospace; color: var(--muted); }
  .pad-tags { font-size: 10px; color: var(--melodic); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
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
  .row.out:not(.drop) { opacity: 0.75; }
  .pick { flex: 1; min-width: 0; display: flex; gap: 8px; align-items: baseline; background: none; border: 0; padding: 5px 6px; text-align: left; color: var(--text); cursor: pointer; }
  .rank { width: 2.5em; text-align: right; font: 11px ui-monospace, Menlo, monospace; }
  .name { font-family: ui-monospace, Menlo, monospace; white-space: pre; }
  .stars { color: #b45309; font-size: 11px; }
  .dur { width: 5em; }
  .est { font-size: 10px; padding: 0 5px; border-radius: 8px; border: 1px dashed var(--muted); color: var(--muted); }
  .flag { font-size: 10px; padding: 0 5px; border-radius: 8px; background: #fde68a; color: #713f12; }
  .tag { display: inline-flex; align-items: center; gap: 2px; font-size: 10px; padding: 0 2px 0 6px; border-radius: 8px; border: 1px solid var(--border); color: var(--muted); white-space: nowrap; }
  .kit-tag { padding-right: 6px; border-style: dashed; }
  .untag { border: 0; background: none; color: var(--muted); padding: 0 3px; cursor: pointer; font-size: 10px; }
  .src { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; flex: 1; }
  .status { width: 4em; color: var(--muted); }
  .move { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; padding: 6px 8px; margin-bottom: 6px; border: 1px solid var(--accent); border-radius: 4px; background: var(--panel); }
  .sep { padding: 10px 6px 4px; }
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
    .list { max-height: 60vh; }
  }
</style>
