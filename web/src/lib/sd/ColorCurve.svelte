<script lang="ts">
  // Courbe Color du Saturator facon Live : accentuation avant la courbe,
  // etagere grave (noeud 1 : Freq Lo / Amt Lo) et aigue (noeud 2 : Freq Hi /
  // Amt Hi), +/- COLOR_DB a +/- 100 % (saturation.py) ; au-dessus de 0 dB la
  // bande sature plus, en dessous moins. Glisser un noeud : x = frequence,
  // y = quantite ; double-clic = valeurs par defaut.
  import type { ParamSpec } from '../api'
  import { F_MAX, F_MIN, fmt, fromNorm, shelfDb, toNorm } from './scale'

  let { params, specs, disabled = false, onchange }: {
    params: Record<string, number>
    specs: ParamSpec[]
    disabled?: boolean
    onchange: (name: string, v: number) => void
  } = $props()

  const COLOR_DB = 15   // Saturator.COLOR_DB
  const W = 240
  const H = 64
  const DB = 18         // demi-hauteur affichee
  const fx = (f: number) => (Math.log(f / F_MIN) / Math.log(F_MAX / F_MIN)) * W
  const dy = (db: number) => ((DB - Math.min(DB, Math.max(-DB, db))) / (2 * DB)) * H
  const gain = (amt: number) => (amt / 100) * COLOR_DB
  const spec = (name: string) => specs.find(s => s.name === name)!

  const total = (f: number) =>
    shelfDb('low', params.freq_lo, gain(params.amt_lo), f) + shelfDb('high', params.freq_hi, gain(params.amt_hi), f)
  const path = $derived.by(() => {
    const pts: string[] = []
    for (let i = 0; i <= 120; i++) {
      const f = F_MIN * (F_MAX / F_MIN) ** (i / 120)
      pts.push(`${i ? 'L' : 'M'}${fx(f).toFixed(1)} ${dy(total(f)).toFixed(1)}`)
    }
    return pts.join(' ')
  })
  const nodes = $derived([
    { n: 1, f: 'freq_lo', a: 'amt_lo', x: fx(params.freq_lo), y: dy(gain(params.amt_lo)) },
    { n: 2, f: 'freq_hi', a: 'amt_hi', x: fx(params.freq_hi), y: dy(gain(params.amt_hi)) },
  ])

  let active: (typeof nodes)[number] | null = null
  function nearest(e: PointerEvent) {
    const r = (e.currentTarget as SVGSVGElement).getBoundingClientRect()
    const x = ((e.clientX - r.left) / r.width) * W
    return nodes.reduce((a, b) => (Math.abs(b.x - x) < Math.abs(a.x - x) ? b : a))
  }
  function at(e: PointerEvent) {
    if (!active) return
    const r = (e.currentTarget as SVGSVGElement).getBoundingClientRect()
    const nx = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width))
    const fs = spec(active.f), as = spec(active.a)
    onchange(active.f, fromNorm(fs, toNorm(fs, F_MIN * (F_MAX / F_MIN) ** nx)))
    const db = DB - (((e.clientY - r.top) / r.height) * 2 * DB)
    onchange(active.a, fromNorm(as, toNorm(as, (db / COLOR_DB) * 100)))
  }
  function reset(e: MouseEvent) {
    if (disabled) return
    const k = nearest(e as PointerEvent)
    onchange(k.f, spec(k.f).default)
    onchange(k.a, spec(k.a).default)
  }
</script>

<svg class="curve" class:disabled width={W} height={H} viewBox="0 0 {W} {H}" role="img"
  aria-label="Courbe Color : grave {fmt(spec('amt_lo'), params.amt_lo)} sous {fmt(spec('freq_lo'), params.freq_lo)}, aigu {fmt(spec('amt_hi'), params.amt_hi)} au-dessus de {fmt(spec('freq_hi'), params.freq_hi)}"
  onpointerdown={e => { if (disabled) return; (e.currentTarget as Element).setPointerCapture(e.pointerId); active = nearest(e); at(e) }}
  onpointermove={at} onpointerup={() => (active = null)} onpointercancel={() => (active = null)} ondblclick={reset}>
  <title>Color : glisser un nœud (1 grave, 2 aigu) ; double-clic = défaut</title>
  {#each [100, 1000, 10000] as f (f)}<line class="grid" x1={fx(f)} x2={fx(f)} y1="0" y2={H} />{/each}
  <line class="grid zero" x1="0" x2={W} y1={dy(0)} y2={dy(0)} />
  <path class="fill" d="{path} L{W} {dy(0)} L0 {dy(0)} Z" />
  <path class="line" d={path} />
  {#each nodes as k (k.n)}
    <circle class="node" cx={k.x} cy={k.y} r="6" />
    <text class="num" x={k.x} y={k.y + 3}>{k.n}</text>
  {/each}
  <text x="3" y={H - 3}>100</text><text x={fx(1000) + 3} y={H - 3}>1k</text><text x={fx(10000) + 3} y={H - 3}>10k</text>
</svg>

<style>
  .curve { display: block; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; cursor: crosshair; touch-action: none; margin-bottom: 4px; }
  .grid { stroke: var(--border); stroke-width: 1; }
  .grid.zero { stroke-dasharray: 2 3; stroke: var(--muted); }
  .fill { fill: var(--accent); opacity: 0.12; }
  .line { fill: none; stroke: var(--accent); stroke-width: 1.8; }
  .node { fill: var(--panel); stroke: var(--accent); stroke-width: 1.5; }
  .num { font-size: 8px; font-weight: 700; fill: var(--accent); text-anchor: middle; }
  text { font-size: 8px; fill: var(--muted); }
  .disabled { cursor: default; }
  .disabled .line, .disabled .node { stroke: var(--muted); }
  .disabled .fill { fill: var(--muted); }
</style>
