// Echelles des potards et courbes de filtre du sound design (Phase 8.C).
// Les bornes, unites et echelles viennent du catalogue de l'API (ParamSpec).

import type { ParamSpec } from '../api'

/** Valeur -> position normalisee 0..1 (lin ou log). */
export function toNorm(p: ParamSpec, v: number): number {
  const n = p.scale === 'log' ? Math.log(v / p.min) / Math.log(p.max / p.min) : (v - p.min) / (p.max - p.min)
  return Math.min(1, Math.max(0, n))
}

/** Position 0..1 -> valeur, arrondie au pas ou a 3 chiffres significatifs. */
export function fromNorm(p: ParamSpec, n: number): number {
  const c = Math.min(1, Math.max(0, n))
  const v = p.scale === 'log' ? p.min * (p.max / p.min) ** c : p.min + c * (p.max - p.min)
  if (p.step) return Math.min(p.max, Math.max(p.min, Math.round(v / p.step) * p.step))
  return Number(v.toPrecision(3))
}

/** Affichage facon Live : 1.20 kHz, 180 Hz, -6.0 dB, 40 ms, 0.85. */
export function fmt(p: ParamSpec, v: number): string {
  if (p.choices) return p.choices[Math.round(v)] ?? String(v)
  if (p.step) return `${p.step < 1 ? String(Math.round(v / p.step) * p.step) : Math.round(v)}${p.unit ? ` ${p.unit}` : ''}`
  switch (p.unit) {
    case 'Hz': return v >= 1000 ? `${(v / 1000).toFixed(v >= 10000 ? 1 : 2)} kHz` : `${v.toFixed(v < 100 ? 1 : 0)} Hz`
    case 'dB': return `${v > 0 ? '+' : ''}${v.toFixed(1)} dB`
    case 'ms': return v >= 1000 ? `${(v / 1000).toFixed(2)} s` : `${v.toFixed(v < 10 ? 1 : 0)} ms`
    case 's': return v < 1 ? `${(v * 1000).toFixed(0)} ms` : `${v.toFixed(2)} s`
    default: return v.toFixed(2)
  }
}

// --- Courbes de reponse (illustratives : modeles analogiques des filtres) ---

export const FILTER_TYPES = ['filter', 'highpass', 'lowpass', 'ladder_lp', 'low_shelf', 'peak'] as const
export type FilterType = (typeof FILTER_TYPES)[number]
export const isFilter = (t: string): t is FilterType => (FILTER_TYPES as readonly string[]).includes(t)

export const F_MIN = 20
export const F_MAX = 20000

/** Frequence de coupure et parametre vertical du noeud, selon le filtre. */
export function cutoffParam(t: FilterType): string {
  return t === 'ladder_lp' || t === 'filter' ? 'cutoff_hz' : 'cutoff_frequency_hz'
}
export function verticalParam(t: FilterType): string | null {
  if (t === 'ladder_lp' || t === 'filter') return 'resonance'
  if (t === 'low_shelf' || t === 'peak') return 'gain_db'
  return null
}

const lp2 = (x: number, q: number) => 1 / Math.hypot(1 - x * x, x / q)
const hp2 = (x: number, q: number) => (x * x) / Math.hypot(1 - x * x, x / q)
const bp2 = (x: number, q: number) => (x / q) / Math.hypot(1 - x * x, x / q)

/** Ordre des types du device `filter` (FILTER_MODES de sounddesign.py). */
const MODES = ['LP12', 'LP24', 'HP12', 'HP24', 'BP12', 'BP24']

/** Gain en dB a la frequence f. */
export function responseDb(t: FilterType, params: Record<string, number>, f: number): number {
  const fc = params[cutoffParam(t)]
  const x = f / fc
  let mag: number
  switch (t) {
    case 'lowpass': mag = 1 / Math.hypot(1, x); break                   // 1er ordre, 6 dB/oct
    case 'highpass': mag = x / Math.hypot(1, x); break
    case 'ladder_lp': mag = lp2(x, 0.5 + 6 * params.resonance) * lp2(x, 0.6); break   // ~24 dB/oct
    case 'filter': {
      const mode = MODES[Math.round(params.mode)] ?? 'LP24'
      const q = 0.5 + 6 * params.resonance
      const f2 = mode.startsWith('LP') ? lp2 : mode.startsWith('HP') ? hp2 : bp2
      mag = f2(x, q) * (mode.endsWith('24') ? f2(x, 0.6) : 1)   // 24 dB/oct = deux etages
      if (mode.startsWith('BP')) mag *= Math.sqrt(q)               // bp2 vaut 1 a la coupure : le pic suit la resonance
      break
    }
    case 'peak': {
      const a = 10 ** (params.gain_db / 40)
      const q = params.q
      mag = Math.hypot(1 - x * x, (x * a) / q) / Math.hypot(1 - x * x, x / (a * q))
      break
    }
    case 'low_shelf': {
      const a = 10 ** (params.gain_db / 40)
      const k = (Math.sqrt(a) * x) / params.q
      mag = (a * Math.hypot(a - x * x, k)) / Math.hypot(1 - a * x * x, k)
      break
    }
  }
  return 20 * Math.log10(Math.max(mag, 1e-6))
}
