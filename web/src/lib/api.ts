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

export interface TrackDetail extends TrackSummary {
  tempo_bpm: number | null
  time_signature: string | null
  bar_times: number[]
  segments: Segment[]
  cues: CuePoint[]
  fields: Record<string, string>
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

/** URL du manuel PDF ouvert a une page (visionneuse du navigateur). */
export const manualUrl = (page = 1) => `/api/manual#page=${page}`

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail ?? `${res.status} ${res.statusText}`)
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

/** Couleurs de segments, alignees sur visualize.py (SPEC Phase 5). */
export const SEGMENT_COLORS: Record<string, string> = {
  intro: '#b0b0b0',
  build: '#f59e0b',
  peak: '#ef4444',
  main: '#3b82f6',
  breakdown: '#8b5cf6',
  outro: '#555555',
}
