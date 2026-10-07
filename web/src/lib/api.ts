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
  manualOutline: () => fetch('/api/manual/outline').then(r => json<Record<string, ManualRef>>(r)),
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
