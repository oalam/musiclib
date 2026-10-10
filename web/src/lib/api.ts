// Types miroir des modeles Pydantic de scripts/api.py et analyzer/types.py.

export interface TrackSummary {
  slug: string
  artist: string
  title: string
  bpm: string
  key: string
  duration: string
  genre: string
  energy: string
  mood: string
  quality_score: string
  groove_cluster: string
  /** Date d'ajout ISO (AAAA-MM-JJ). */
  added: string
  /** Tags manuels de library.md, separes par des virgules. */
  tags: string
  has_audio: boolean
  has_stems: boolean
  has_bank: boolean
}

export interface Segment {
  start_s: number
  end_s: number
  duration_s: number
  rms_dbfs: number
  label: string
}

export interface CuePoint {
  time_s: number
  type: string
  confidence: number
  label: string | null
}

/** Gamme candidate (7.H), `scale` = nom KB SCALE de la DT2. */
export interface ScaleMatch {
  root: number
  root_name: string
  scale: string
  label: string
  notes: string[]
  score: number
}

export interface ScaleResult extends ScaleMatch {
  margin: number
  uncertain: boolean
  candidates: ScaleMatch[]
}

/** Accord d'une mesure ; `label` = « N » sans contenu tonal. */
export interface BarChord {
  bar: number
  start_s: number
  end_s: number
  label: string
  root: number | null
  quality: string | null
  confidence: number
}

export interface SectionProgression { label: string; start_s: number; end_s: number; chords: string[] }

export interface Harmony {
  analyzed_at: string
  source: string
  scale: ScaleResult
  chords: BarChord[]
  progression: SectionProgression[]
}

export interface TrackDetail extends TrackSummary {
  tempo_bpm: number | null
  time_signature: string | null
  bar_times: number[]
  segments: Segment[]
  cues: CuePoint[]
  fields: Record<string, string>
  /** Absent tant que harmony.py n'a pas tourne sur le morceau. */
  harmony: Harmony | null
  /** Reglage DT2 de la gamme, ex. « KB SCALE = DORIAN, ROOT NOTE = F » (§8.5.2). */
  keyboard_setup: string | null
}

export interface Trig { step: number; velocity: number; note: number | null }

export interface BankTrack {
  index: number
  role: string
  source: string
  active: boolean
  level: number
  trigs: Trig[]
}

export interface Pattern {
  slot: number
  label: string
  start_s: number
  end_s: number
  bars: number
  steps: number
  repeats: number
  tracks: BankTrack[]
}

/** Section deduite des tracks (7.B2), jouee par un slot ; plusieurs sections peuvent partager un slot. */
export interface Section {
  index: number
  label: string
  bar: number
  bars: number
  start_s: number
  end_s: number
  pattern_slot: number
  active: number[]
}

export interface Phrase { start_s: number; bar: number; pattern_slot: number; active: number[] }

export interface Bank {
  slug: string
  artist: string
  title: string
  bpm: number
  time_signature: string
  steps_per_bar: number
  from_stems: boolean
  phrase_bars: number
  bar_times_s: number[]
  patterns: Pattern[]
  /** Absent des banks generees avant 7.B2. */
  sections?: Section[]
  /** Ordre de jeu des slots, ex. [1, 2, 1, 3]. */
  chain?: number[]
  mutes: Phrase[]
  generated_at: string
}

/** Section de la base de connaissance qui contient tous les termes (Phase 7.D). */
export interface KbHit {
  path: string
  title: string
  heading: string
  anchor: string
  snippet: string
  score: number
}

/** Paragraphe du manuel PDF et sa page (7.F). */
export interface ManualRef { section: string; title: string; page: number }

export interface KbNote {
  path: string
  title: string
  markdown: string
  /** References du frontmatter `manuel`. */
  manual: ManualRef[]
  /** Tous les § resolus de la note (frontmatter + texte), par numero. */
  manual_index: Record<string, ManualRef>
}

export interface KbEntry { path: string; title: string; ordre: number; statut: string }
export interface KbLot { number: number; name: string; notes: KbEntry[] }

/** Candidat d'acquisition (7.I), miroir de grab.CandidateInfo. */
export interface Candidate {
  source: string
  url: string
  title: string
  uploader: string
  duration_s: number
  codec: string
  abr: number
  /** Debit pondere par codec, ou LOSSLESS. */
  quality: string
  match: number
  score: number
}

export interface GrabRequest {
  url: string
  analyze_quality: boolean
  stems: boolean
  bank: boolean
  folder?: string | null
}

export type JobStatus = 'queued' | 'running' | 'done' | 'error' | 'skipped'
export interface JobStep { name: string; label: string; status: JobStatus; detail: string }

/** Job d'acquisition + analyse, suivi par polling (jobs.Job). */
export interface Job {
  id: string
  request: GrabRequest
  status: JobStatus
  steps: JobStep[]
  slug: string | null
  created: boolean | null
  error: string
  created_at: string
  finished_at: string | null
}

/** Envoi d'une track a la DT2 (7.E, scripts/dt2_midi.py). */
export interface Dt2Ports { inputs: string[]; outputs: string[]; default: string | null; error: string | null }
export interface Dt2SendRequest { slug: string; slot: number; track: number; port: string; channel: number; octave: number }
export type Dt2SendStatus = 'waiting' | 'sending' | 'done' | 'cancelled' | 'error'
export interface Dt2SendState {
  id: string
  request: Dt2SendRequest
  role: string
  steps: number
  trigs: number
  status: Dt2SendStatus
  step: number
  detail: string
  warning: string
  created_at: string
  finished_at: string | null
}

/** Bibliotheque de samples DT2 (7.J2, 7.J4, 7.J5, scripts/samples.py). */
export type SampleStatus = 'pending' | 'keep' | 'drop'
export interface SampleEntry {
  source: string
  family: string           // genre (tag) ou SAMPLE (7.J8)
  code: string
  sub: string              // sous-categorie, '' = racine du code
  folder: string           // dossier final (case) : DRUMS/BD/HARD ; '' = non classe
  pack: string
  name: string
  duration: number | null
  rank: number
  status: SampleStatus
  selected: boolean
  flags: string[] | null
  bpm: number | null       // tempo mesure (boucle sans tempo dans le nom)
  bpm_est: boolean         // librosa seul, non confirme par la duree
  tags: string[]           // ceux du fichier et de son kit
  stars: number | null
  auto_tags: string[]      // inferes des dossiers (7.J6)
  note?: string | null     // classe de hauteur en dieses (7.J7)
  note_hz?: number | null  // fondamentale mesuree
  note_src?: 'nom' | 'mesure' | 'incertaine' | null
  overflow: boolean        // reserve hors plafond, vue par kit (7.J5)
}
/** Fichier hors des cases : non classe ou en corbeille. */
export interface LooseSample {
  source: string
  pack: string
  tags: string[]
  stars: number | null
  auto_tags: string[]
}
/** Barre de recherche (7.J6) : ET entre facettes, OU dans une facette. */
export interface RebuildStatus {
  status: 'idle' | 'running' | 'done' | 'error'
  started_at: string | null
  finished_at: string | null
  error: string
  candidates: number
  selected: number
  reserve: number
  unclassified: number
}

/** Tranche de tempo (borne basse, « <90 » pour la premiere) et fichiers (7.K). */
export interface FacetBpm { band: string; count: number }

export interface SampleFilter {
  q?: string
  tags?: string[]
  kits?: string[]
  section?: 'rhythm' | 'melodic'
  codes?: string[]
  kind?: 'oneshot' | 'loop'
  minStars?: number
  notes?: string[]         // classes de hauteur en dieses (7.J7)
  bpms?: string[]          // tranches de tempo (7.K, vue de droite)
}
/** Tag propose par la barre : groupe genre / instrument / mot (inferes) ou manuel. */
export interface FacetTag { tag: string; group: string; count: number }
/** Part de la roue chromatique (7.J7). */
export interface FacetNote { note: string; count: number }
/** Kit = prefixe de chemin (pack / sous-dossier), bilan pour les pads (7.J5). */
export interface SampleKit {
  kit: string
  pack: string
  label: string
  candidates: number
  selected: number
  keep: number
  reserve: number
  unclassified: number
  trashed: number
  trashed_kit: boolean
}
export interface SampleKits { kits: SampleKit[]; tags: Record<string, string[]> }
/** Bilan de l'export vers <MEDIA>/Live/samples (7.J3). */
export interface SampleExportReport {
  dest: string
  dry_run: boolean
  files: number
  bytes: number
  copied: string[]
  unchanged: number
  removed: string[]
  missing: string[]
  conflicts: string[]
}
/** Case = dossier final du +Drive (7.J8) : DRUMS/BD/HARD, LOOPS/BR, FX/RISE, VX. */
export interface SampleCell {
  folder: string
  branch: string
  code: string
  sub: string
  quota: number | null
  candidates: number
  selected: number
  keep: number
  drop: number
  to_listen: number
  flagged: number
  reserve: number          // hors plafond
}

// --- Sound design (Phase 8) : miroir de analyzer/sounddesign.py -----------

export interface ParamSpec {
  name: string
  label: string
  min: number
  max: number
  default: number
  unit: string
  scale: 'lin' | 'log'
  step: number | null
  help: string
  /** Libelles des valeurs 0..n-1 : selecteur (type de filtre), pas potard. */
  choices: string[] | null
}
export interface DeviceSpec { type: string; label: string; help: string; params: ParamSpec[] }
export interface SdDevice { type: string; params: Record<string, number>; bypass: boolean }
export interface SdChain { name: string; mute: boolean; gain_db: number; devices: SdDevice[] }
export interface SdPreset {
  id: string
  treatment: string
  label: string
  description: string
  settings: Record<string, number>
  chains: SdChain[]
  master: SdDevice[]
  output_peak_db: number | null
}
export interface TreatmentSpec {
  id: string
  label: string
  summary: string
  source_hint: string
  settings: ParamSpec[]
  notebook: string
}
export interface RenderRecord {
  file: string
  source: string
  preset: SdPreset
  sr: number
  seconds: number
  created_at: string
  /** Cle du manifeste si verse dans le pack Samples/SoundDesign (8.D). */
  versed: string | null
}

/** URL du manuel PDF ouvert a une page (visionneuse du navigateur). */
export const manualUrl = (page = 1) => `/api/manual#page=${page}`

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    // 422 de validation FastAPI : liste d'erreurs {loc, msg}
    const detail = Array.isArray(body.detail) ? body.detail.map((d: { msg: string }) => d.msg).join(' ; ') : body.detail
    throw new Error(detail ?? `${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

const enc = encodeURIComponent

/** Parametres de la barre de recherche, prefixes de `&` (vide sans filtre). */
function fq(f: SampleFilter = {}): string {
  const q = new URLSearchParams()
  if (f.q) q.set('q', f.q)
  for (const t of f.tags ?? []) q.append('tags', t)
  for (const k of f.kits ?? []) q.append('kits', k)
  for (const c of f.codes ?? []) q.append('codes', c)
  for (const n of f.notes ?? []) q.append('notes', n)
  for (const b of f.bpms ?? []) q.append('bpms', b)
  if (f.section) q.set('section', f.section)
  if (f.kind) q.set('kind', f.kind)
  if (f.minStars) q.set('min_stars', String(f.minStars))
  const s = q.toString()
  return s ? `&${s}` : ''
}

function samplePost(action: string, body: object): Promise<SampleCell[]> {
  return fetch(`/api/samples/${action}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
    .then(r => json<SampleCell[]>(r))
}

export const api = {
  tracks: () => fetch('/api/tracks').then(r => json<TrackSummary[]>(r)),
  track: (slug: string) => fetch(`/api/tracks/${enc(slug)}`).then(r => json<TrackDetail>(r)),
  bank: (slug: string) => fetch(`/api/tracks/${enc(slug)}/bank`).then(r => json<Bank>(r)),
  generateBank: (slug: string) =>
    fetch(`/api/tracks/${enc(slug)}/bank`, { method: 'POST' }).then(r => json<Bank>(r)),
  audioUrl: (slug: string) => `/api/tracks/${enc(slug)}/audio`,
  kbSearch: (q: string) => fetch(`/api/kb/search?q=${enc(q)}`).then(r => json<KbHit[]>(r)),
  kbNote: (path: string) => fetch(`/api/kb/note?path=${enc(path)}`).then(r => json<KbNote>(r)),
  kbToc: () => fetch('/api/kb/toc').then(r => json<KbLot[]>(r)),
  grabSearch: (query: string) =>
    fetch('/api/grab/search', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query }) })
      .then(r => json<Candidate[]>(r)),
  grab: (req: GrabRequest) =>
    fetch('/api/grab', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(req) })
      .then(r => json<Job>(r)),
  job: (id: string) => fetch(`/api/jobs/${enc(id)}`).then(r => json<Job>(r)),
  dt2Ports: () => fetch('/api/dt2/ports').then(r => json<Dt2Ports>(r)),
  dt2Send: (req: Dt2SendRequest) =>
    fetch('/api/dt2/send', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(req) })
      .then(r => json<Dt2SendState>(r)),
  dt2SendStatus: () => fetch('/api/dt2/send').then(r => json<Dt2SendState | null>(r)),
  dt2SendCancel: () => fetch('/api/dt2/send', { method: 'DELETE' }).then(r => json<Dt2SendState | null>(r)),
  sampleCells: (f: SampleFilter = {}, kit = '') =>
    fetch(`/api/samples?${kit ? `kit=${enc(kit)}` : ''}${fq(f)}`).then(r => json<SampleCell[]>(r)),
  sampleCell: (folder: string, kit = '', overflow = false, f: SampleFilter = {}) =>
    fetch(`/api/samples/cell?folder=${enc(folder)}${kit ? `&kit=${enc(kit)}` : ''}${overflow ? '&overflow=true' : ''}${fq(f)}`).then(r => json<SampleEntry[]>(r)),
  sampleLoose: (which: 'unclassified' | 'trash', kit = '', f: SampleFilter = {}) =>
    fetch(`/api/samples/loose?which=${which}${kit ? `&kit=${enc(kit)}` : ''}${fq(f)}`).then(r => json<LooseSample[]>(r)),
  sampleKitTree: (kit: string, f: SampleFilter = {}) =>
    fetch(`/api/samples/kit/tree?kit=${enc(kit)}${fq(f)}`).then(r => json<{ entries: SampleEntry[]; unclassified: LooseSample[] }>(r)),
  /** Vue par type (7.K) : fichiers du filtre par case, reduits a un kit si donne. */
  sampleTree: (f: SampleFilter, kit = '') =>
    fetch(`/api/samples/tree?kit=${enc(kit)}${fq(f)}`).then(r => json<SampleEntry[]>(r)),
  sampleKits: (f: SampleFilter = {}) => fetch(`/api/samples/kits?${fq(f)}`).then(r => json<SampleKits>(r)),
  sampleFacets: () => fetch('/api/samples/facets').then(r => json<FacetTag[]>(r)),
  sampleBpms: (f: SampleFilter = {}, kit = '') =>
    fetch(`/api/samples/bpms?kit=${enc(kit)}${fq(f)}`).then(r => json<FacetBpm[]>(r)),
  sampleNotes: (f: SampleFilter = {}, kit = '') =>
    fetch(`/api/samples/notes?kit=${enc(kit)}${fq(f)}`).then(r => json<FacetNote[]>(r)),
  sampleKitTrash: (kit: string) => samplePost('kit/trash', { kit }),
  sampleKitRestore: (kit: string) => samplePost('kit/restore', { kit }),
  sampleKitTags: (kit: string, add: string[], remove: string[] = []) => samplePost('kit/tags', { kit, add, remove }),
  sampleTags: () => fetch('/api/samples/tags').then(r => json<string[]>(r)),
  // actions par lot : toutes renvoient la grille complete (sans filtre)
  sampleStatus: (sources: string[], status: SampleStatus) => samplePost('status', { sources, status }),
  sampleMove: (sources: string[], code: string, sub: string) => samplePost('move', { sources, code, sub }),
  sampleFolders: () => fetch('/api/samples/folders').then(r => json<string[]>(r)),
  /** Reanalyse de la bibliotheque de samples (7.K) : lancement puis suivi. */
  sampleRebuild: () => fetch('/api/samples/rebuild', { method: 'POST' }).then(r => json<RebuildStatus>(r)),
  sampleRebuildStatus: () => fetch('/api/samples/rebuild').then(r => json<RebuildStatus>(r)),
  /** Cree un sous-dossier manuel d'un code (7.K) ; renvoie les dossiers cibles. */
  sampleFolderAdd: (code: string, sub: string) =>
    fetch('/api/samples/folders', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code, sub }) })
      .then(r => json<string[]>(r)),
  sampleStars: (sources: string[], stars: number | null) => samplePost('stars', { sources, stars }),
  sampleTagsEdit: (sources: string[], add: string[], remove: string[] = []) => samplePost('tags', { sources, add, remove }),
  sampleTrash: (sources: string[]) => samplePost('trash', { sources }),
  sampleRestore: (sources: string[]) => samplePost('restore', { sources }),
  sampleExport: (dryRun: boolean) =>
    fetch('/api/samples/export', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ dry_run: dryRun }) })
      .then(r => json<SampleExportReport>(r)),
  sampleAudioUrl: (source: string) => `/api/samples/audio?source=${enc(source)}`,
  manualOutline: () => fetch('/api/manual/outline').then(r => json<Record<string, ManualRef>>(r)),
  sdTreatments: () => fetch('/api/sounddesign/treatments').then(r => json<TreatmentSpec[]>(r)),
  sdDevices: () => fetch('/api/sounddesign/devices').then(r => json<DeviceSpec[]>(r)),
  sdPresets: (treatment: string) => fetch(`/api/sounddesign/presets/${enc(treatment)}`).then(r => json<SdPreset[]>(r)),
  sdSavePreset: (p: SdPreset) =>
    fetch(`/api/sounddesign/presets/${enc(p.treatment)}/${enc(p.id)}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p) })
      .then(r => json<SdPreset>(r)),
  /** Boucle rendue en WAV, sans ecriture disque. */
  sdPreview: async (preset: SdPreset, source: string, signal?: AbortSignal): Promise<ArrayBuffer> => {
    const r = await fetch('/api/sounddesign/preview', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ preset, source }), signal })
    if (!r.ok) await json(r)   // leve avec le detail de l'API
    return r.arrayBuffer()
  },
  sdRender: (preset: SdPreset, source: string) =>
    fetch('/api/sounddesign/render', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ preset, source }) })
      .then(r => json<RenderRecord>(r)),
  sdRenders: (treatment: string) => fetch(`/api/sounddesign/renders?treatment=${enc(treatment)}`).then(r => json<RenderRecord[]>(r)),
  sdRenderAudioUrl: (file: string) => `/api/sounddesign/renders/audio?file=${enc(file)}`,
  /** Copie le rendu dans le pack Samples/SoundDesign ; reanalyse a lancer ensuite. */
  sdVerse: (file: string) =>
    fetch('/api/sounddesign/verse', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ file }) })
      .then(r => json<RenderRecord>(r)),
  sdNotebook: (treatment: string) =>
    fetch(`/api/sounddesign/notebook/${enc(treatment)}`).then(r => json<{ path: string; markdown: string }>(r)),
}

/** Minuscules sans accents (meme regle que kb.normalize). */
export function normalize(s: string): string {
  return s.normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase()
}

/** Ancre de titre (meme regle que kb.slugify). */
export function slugify(s: string): string {
  return normalize(s).replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
}

/** 0:00 */
export function mmss(s: number): string {
  const t = Math.max(0, Math.floor(s))
  return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, '0')}`
}

/** Accord en cours a t (recherche dichotomique), null hors grille. */
export function chordAt(chords: BarChord[], t: number): BarChord | null {
  let lo = 0
  let hi = chords.length - 1
  while (lo <= hi) {
    const mid = (lo + hi) >> 1
    if (chords[mid].end_s <= t) lo = mid + 1
    else if (chords[mid].start_s > t) hi = mid - 1
    else return chords[mid]
  }
  return null
}

/** Couleurs de segments, alignees sur visualize.py (SPEC Phase 5). */
export const SEGMENT_COLORS: Record<string, string> = {
  intro: '#b0b0b0',
  build: '#f59e0b',
  peak: '#ef4444',
  main: '#3b82f6',
  breakdown: '#8b5cf6',
  outro: '#555555',
}
