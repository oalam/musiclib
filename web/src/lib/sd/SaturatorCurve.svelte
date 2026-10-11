<script lang="ts" module>
  // Courbes du Saturator, portees de scripts/analyzer/saturation.py
  // (Saturator._shape, _analog_clip, _waveshaper) : a tenir synchrones.
  const clip1 = (u: number) => Math.min(1, Math.max(-1, u))
  const analogClip = (u: number) => u / (1 + Math.abs(u) ** 2.5) ** 0.4

  function waveshaper(u: number, p: Record<string, number>): number {
    const v = clip1(u)
    const lin = p.ws_lin, curve = p.ws_curve
    let s = lin * v + curve * (1.5 * v - 0.5 * v ** 3)
    if (lin + curve > 1) s /= Math.max(lin + curve, 1e-6)
    s += 0.5 * p.ws_depth * Math.sin(Math.PI * (1 + 15 * p.ws_period) * v)
    s *= 1 - p.ws_damp * Math.exp(-((v / 0.15) ** 2))
    return (1 - p.ws_drive) * v + p.ws_drive * s
  }

  function shape(u: number, p: Record<string, number>): number {
    switch (Math.round(p.curve)) {
      case 0: return analogClip(u)
      case 1: return Math.sin(clip1(u) * Math.PI / 2)
      case 2: { const v = clip1(u); return 5 * v / (1 + 4 * Math.abs(v)) }
      case 3: return Math.tanh(u)
      case 4: return u / (1 + Math.abs(u) ** 8) ** 0.125
      case 5: return Math.sin(u * Math.PI / 2)
      case 6: return clip1(u)
      default: return waveshaper(u, p)
    }
  }

  /** Transfert statique entree -> sortie (sans Color : les etageres sont neutres sur un signal propre). */
  export function transfer(x: number, p: Record<string, number>): number {
    let y = shape(x * 10 ** (p.drive_db / 20), p)
    const clip = Math.round(p.post_clip)
    if (clip === 1) y = analogClip(y)
    else if (clip === 2) y = clip1(y)
    y *= 10 ** (p.output_db / 20)
    const mix = p.dry_wet / 100
    return (1 - mix) * x + mix * y
  }
</script>

<script lang="ts">
  // Courbe de transfert facon Saturator de Live : entree en abscisse
  // (-1..1, avant Drive), sortie en ordonnee ; diagonale = son inchange.
  // Glisser verticalement sur la courbe regle le Drive (Maj = fin).
  import type { ParamSpec } from '../api'
  import { fmt, fromNorm, toNorm } from './scale'

  let { params, specs, disabled = false, onchange }: {
    params: Record<string, number>
    specs: ParamSpec[]
    disabled?: boolean
    onchange: (name: string, v: number) => void
  } = $props()

  const W = 200
  const H = 84
  const Y_MAX = 1.3   // marge au-dessus de 0 dBFS (Output positif)
  const px = (x: number) => ((x + 1) / 2) * W
  const py = (y: number) => ((Y_MAX - Math.min(Y_MAX, Math.max(-Y_MAX, y))) / (2 * Y_MAX)) * H

  const path = $derived.by(() => {
    const pts: string[] = []
    for (let i = 0; i <= 200; i++) {
      const x = -1 + (2 * i) / 200
      pts.push(`${i ? 'L' : 'M'}${px(x).toFixed(1)} ${py(transfer(x, params)).toFixed(1)}`)
    }
    return pts.join(' ')
  })

  const drive = $derived(specs.find(s => s.name === 'drive_db')!)
  let drag: { y: number; n: number } | null = null
  function down(e: PointerEvent) {
    if (disabled) return
    ;(e.currentTarget as Element).setPointerCapture(e.pointerId)
    drag = { y: e.clientY, n: toNorm(drive, params.drive_db) }
  }
  function move(e: PointerEvent) {
    if (!drag) return
    const n = drag.n + (drag.y - e.clientY) / (e.shiftKey ? 1500 : 180)
    onchange('drive_db', fromNorm(drive, Math.min(1, Math.max(0, n))))
  }
</script>

<svg class="curve" class:disabled width={W} height={H} viewBox="0 0 {W} {H}" role="img"
  aria-label="Courbe de transfert, Drive {fmt(drive, params.drive_db)}"
  onpointerdown={down} onpointermove={move} onpointerup={() => (drag = null)} onpointercancel={() => (drag = null)}
  ondblclick={() => !disabled && onchange('drive_db', drive.default)}>
  <title>Courbe de transfert (entrée → sortie). Glisser verticalement : Drive (Maj = fin), double-clic : défaut</title>
  <line class="grid" x1={px(0)} x2={px(0)} y1="0" y2={H} />
  <line class="grid" x1="0" x2={W} y1={py(0)} y2={py(0)} />
  <line class="grid ceil" x1="0" x2={W} y1={py(1)} y2={py(1)} />
  <line class="grid ceil" x1="0" x2={W} y1={py(-1)} y2={py(-1)} />
  <line class="diag" x1={px(-1)} y1={py(-1)} x2={px(1)} y2={py(1)} />
  <path class="line" d={path} />
  <text x="3" y={H - 3}>Drive {fmt(drive, params.drive_db)}</text>
</svg>

<style>
  .curve { display: block; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; cursor: ns-resize; touch-action: none; }
  .grid { stroke: var(--border); stroke-width: 1; }
  .grid.ceil { stroke-dasharray: 2 3; stroke: var(--muted); opacity: 0.6; }
  .diag { stroke: var(--muted); stroke-width: 1; stroke-dasharray: 3 3; opacity: 0.6; }
  .line { fill: none; stroke: var(--accent); stroke-width: 1.8; stroke-linejoin: round; }
  text { font-size: 8px; fill: var(--muted); font-family: var(--mono, monospace); }
  .disabled { cursor: default; }
  .disabled .line { stroke: var(--muted); }
</style>
