<script lang="ts">
  // Potard facon Ableton Live : nom au-dessus, valeur en dessous ; glisser
  // verticalement (Maj = fin), molette, fleches ; double-clic = valeur par
  // defaut. Arc depuis zero si le parametre est bipolaire (gain -24..+24).
  // Variante `bar` : champ a barre de Live (nom a gauche, valeur dans une
  // case remplie), pour les sections secondaires d'un device.
  import type { ParamSpec } from '../api'
  import { fmt, fromNorm, toNorm } from './scale'

  let { spec, value, disabled = false, bar = false, onchange }: {
    spec: ParamSpec
    value: number
    disabled?: boolean
    bar?: boolean
    onchange: (v: number) => void
  } = $props()

  const R = 16
  const C = 22
  const norm = $derived(toNorm(spec, value))
  const bipolar = $derived(spec.min < 0 && spec.max > 0 && spec.scale === 'lin')
  const from = $derived(bipolar ? toNorm(spec, 0) : 0)

  /** Point de l'arc a la position n (0..1 -> -135..+135 degres). */
  function pt(n: number): [number, number] {
    const a = ((-135 + 270 * n) * Math.PI) / 180
    return [C + R * Math.sin(a), C - R * Math.cos(a)]
  }
  function arc(a: number, b: number): string {
    const [lo, hi] = a < b ? [a, b] : [b, a]
    const [x1, y1] = pt(lo)
    const [x2, y2] = pt(hi)
    return `M ${x1} ${y1} A ${R} ${R} 0 ${(hi - lo) * 270 > 180 ? 1 : 0} 1 ${x2} ${y2}`
  }

  let drag: { y: number; n: number } | null = null
  function down(e: PointerEvent) {
    if (disabled) return
    ;(e.currentTarget as Element).setPointerCapture(e.pointerId)
    drag = { y: e.clientY, n: norm }
  }
  function move(e: PointerEvent) {
    if (!drag) return
    const span = e.shiftKey ? 1500 : 180   // pixels pour toute la course
    set(drag.n + (drag.y - e.clientY) / span)
  }
  function set(n: number) {
    const v = fromNorm(spec, n)
    if (v !== value) onchange(v)
  }
  function wheel(e: WheelEvent) {
    if (disabled) return
    e.preventDefault()
    set(norm - e.deltaY * (e.shiftKey ? 0.0002 : 0.002))
  }
  function key(e: KeyboardEvent) {
    const d = e.shiftKey ? 0.002 : 0.02
    if (e.key === 'ArrowUp' || e.key === 'ArrowRight') { e.preventDefault(); set(norm + (spec.step ? spec.step / (spec.max - spec.min) : d)) }
    else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') { e.preventDefault(); set(norm - (spec.step ? spec.step / (spec.max - spec.min) : d)) }
    else if (e.key === 'Delete' || e.key === 'Backspace') { e.preventDefault(); onchange(spec.default) }
  }
</script>

{#if bar}
  <div class="bar" class:disabled title={`${spec.label} : ${spec.help || fmt(spec, value)}\nGlisser (Maj = fin), double-clic = défaut (${fmt(spec, spec.default)})`}>
    <span class="name">{spec.label}</span>
    <div class="box" role="slider" tabindex={disabled ? -1 : 0} aria-label={spec.label}
      aria-valuemin={spec.min} aria-valuemax={spec.max} aria-valuenow={value} aria-valuetext={fmt(spec, value)}
      onpointerdown={down} onpointermove={move} onpointerup={() => (drag = null)} onpointercancel={() => (drag = null)}
      ondblclick={() => !disabled && onchange(spec.default)} onwheel={wheel} onkeydown={key}>
      <span class="fill" style:left="{Math.min(from, norm) * 100}%" style:width="{Math.abs(norm - from) * 100}%"></span>
      <span class="value mono">{fmt(spec, value)}</span>
    </div>
  </div>
{:else}
  <div class="knob" class:disabled title={`${spec.label} : ${spec.help || fmt(spec, value)}\nGlisser (Maj = fin), double-clic = défaut (${fmt(spec, spec.default)})`}>
    <span class="name">{spec.label}</span>
    <svg width={C * 2} height={C * 2 - 4} viewBox="0 0 {C * 2} {C * 2 - 4}"
      role="slider" tabindex={disabled ? -1 : 0} aria-label={spec.label}
      aria-valuemin={spec.min} aria-valuemax={spec.max} aria-valuenow={value} aria-valuetext={fmt(spec, value)}
      onpointerdown={down} onpointermove={move} onpointerup={() => (drag = null)} onpointercancel={() => (drag = null)}
      ondblclick={() => !disabled && onchange(spec.default)} onwheel={wheel} onkeydown={key}>
      <path class="track" d={arc(0, 1)} />
      {#if Math.abs(norm - from) > 0.001}<path class="val" d={arc(from, norm)} />{/if}
      <line class="ptr" x1={C} y1={C} x2={pt(norm)[0]} y2={pt(norm)[1]} />
    </svg>
    <span class="value mono">{fmt(spec, value)}</span>
  </div>
{/if}

<style>
  .knob { display: flex; flex-direction: column; align-items: center; width: 58px; user-select: none; }
  .name { font-size: 10px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 58px; }
  svg { cursor: ns-resize; touch-action: none; outline: none; }
  svg:focus-visible .track { stroke: var(--accent); }
  .track { fill: none; stroke: var(--cell-off); stroke-width: 3.5; stroke-linecap: round; }
  .val { fill: none; stroke: var(--accent); stroke-width: 3.5; stroke-linecap: round; }
  .ptr { stroke: var(--text); stroke-width: 2; stroke-linecap: round; }
  .value { font-size: 10px; }
  .disabled .val { stroke: var(--muted); }
  .disabled svg { cursor: default; }
  .bar { display: flex; align-items: center; gap: 4px; user-select: none; }
  .bar .name { width: 44px; text-align: right; flex: none; }
  .box { position: relative; width: 62px; height: 15px; border: 1px solid var(--border); border-radius: 2px;
    background: var(--panel); cursor: ns-resize; touch-action: none; outline: none; overflow: hidden; }
  .box:focus-visible { border-color: var(--accent); }
  .fill { position: absolute; top: 0; bottom: 0; background: color-mix(in srgb, var(--accent) 45%, transparent); }
  .box .value { position: relative; display: block; text-align: center; line-height: 15px; }
  .disabled .fill { background: var(--cell-off); }
  .disabled .box { cursor: default; }
</style>
