<script lang="ts">
  // Courbe de reponse d'un filtre / EQ facon Auto Filter / EQ Eight : axe
  // log 20 Hz - 20 kHz, noeud a attraper (x = coupure, y = gain ou resonance).
  import type { ParamSpec } from '../api'
  import { F_MAX, F_MIN, type FilterType, cutoffParam, fmt, fromNorm, responseDb, toNorm, verticalParam } from './scale'

  let { type, params, specs, disabled = false, onchange }: {
    type: FilterType
    params: Record<string, number>
    specs: ParamSpec[]
    disabled?: boolean
    onchange: (name: string, v: number) => void
  } = $props()

  const W = 220
  const H = 80
  const DB_TOP = 18
  const DB_BOT = -36
  const fx = (f: number) => (Math.log(f / F_MIN) / Math.log(F_MAX / F_MIN)) * W
  const dy = (db: number) => ((DB_TOP - Math.min(DB_TOP, Math.max(DB_BOT, db))) / (DB_TOP - DB_BOT)) * H

  const cut = $derived(cutoffParam(type))
  const vert = $derived(verticalParam(type))
  const cutSpec = $derived(specs.find(s => s.name === cut)!)
  const vertSpec = $derived(vert ? specs.find(s => s.name === vert) ?? null : null)

  const path = $derived.by(() => {
    const pts: string[] = []
    for (let i = 0; i <= 120; i++) {
      const f = F_MIN * (F_MAX / F_MIN) ** (i / 120)
      pts.push(`${i ? 'L' : 'M'}${fx(f).toFixed(1)} ${dy(responseDb(type, params, f)).toFixed(1)}`)
    }
    return pts.join(' ')
  })
  const node = $derived({ x: fx(params[cut]), y: dy(responseDb(type, params, params[cut])) })

  let drag = false
  function at(e: PointerEvent) {
    const svg = (e.currentTarget as SVGSVGElement).getBoundingClientRect()
    const nx = (e.clientX - svg.left) / svg.width
    const f = F_MIN * (F_MAX / F_MIN) ** Math.min(1, Math.max(0, nx))
    onchange(cut, fromNorm(cutSpec, toNorm(cutSpec, f)))
    if (vertSpec) {
      const ny = 1 - (e.clientY - svg.top) / svg.height
      if (vert === 'gain_db') {
        const db = DB_BOT + ny * (DB_TOP - DB_BOT)
        onchange(vert, fromNorm(vertSpec, toNorm(vertSpec, db)))
      } else onchange(vert!, fromNorm(vertSpec, ny))
    }
  }
</script>

<svg class="curve" class:disabled width={W} height={H} viewBox="0 0 {W} {H}" role="img"
  aria-label="Courbe {type} : {fmt(cutSpec, params[cut])}"
  onpointerdown={e => { if (disabled) return; (e.currentTarget as Element).setPointerCapture(e.pointerId); drag = true; at(e) }}
  onpointermove={e => drag && at(e)} onpointerup={() => (drag = false)} onpointercancel={() => (drag = false)}>
  {#each [100, 1000, 10000] as f (f)}<line class="grid" x1={fx(f)} x2={fx(f)} y1="0" y2={H} />{/each}
  <line class="grid zero" x1="0" x2={W} y1={dy(0)} y2={dy(0)} />
  <path class="fill" d="{path} L{W} {H} L0 {H} Z" />
  <path class="line" d={path} />
  <circle class="node" cx={node.x} cy={node.y} r="5" />
  <text x="3" y={H - 3}>100</text><text x={fx(1000) + 3} y={H - 3}>1k</text><text x={fx(10000) + 3} y={H - 3}>10k</text>
</svg>

<style>
  .curve { display: block; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; cursor: crosshair; touch-action: none; }
  .grid { stroke: var(--border); stroke-width: 1; }
  .grid.zero { stroke-dasharray: 2 3; stroke: var(--muted); }
  .fill { fill: var(--accent); opacity: 0.12; }
  .line { fill: none; stroke: var(--accent); stroke-width: 1.8; }
  .node { fill: var(--panel); stroke: var(--accent); stroke-width: 2; }
  text { font-size: 8px; fill: var(--muted); }
  .disabled { cursor: default; }
  .disabled .line, .disabled .node { stroke: var(--muted); }
  .disabled .fill { fill: var(--muted); }
</style>
