<script lang="ts">
  // Fader vertical de tranche de mixage (gain de chaine), facon Live :
  // graduations en dB, glisser (Maj = fin), molette, double-clic = 0 dB.
  let { label, value, min = -48, max = 12, muted = false, onchange }: {
    label: string
    value: number
    min?: number
    max?: number
    muted?: boolean
    onchange: (v: number) => void
  } = $props()

  const H = 120
  const TICKS = [12, 6, 0, -6, -12, -24, -36, -48]
  const y = (v: number) => ((max - Math.min(max, Math.max(min, v))) / (max - min)) * H

  let drag: { y: number; v: number } | null = null
  function set(v: number) {
    const r = Math.round(Math.min(max, Math.max(min, v)) * 10) / 10
    if (r !== value) onchange(r)
  }
  function down(e: PointerEvent) {
    ;(e.currentTarget as Element).setPointerCapture(e.pointerId)
    drag = { y: e.clientY, v: value }
  }
  function move(e: PointerEvent) {
    if (!drag) return
    set(drag.v + ((drag.y - e.clientY) / H) * (max - min) * (e.shiftKey ? 0.1 : 1))
  }
  function key(e: KeyboardEvent) {
    const d = e.shiftKey ? 0.1 : 1
    if (e.key === 'ArrowUp') { e.preventDefault(); set(value + d) }
    else if (e.key === 'ArrowDown') { e.preventDefault(); set(value - d) }
  }
</script>

<div class="fader" class:muted title="{label} : glisser (Maj = fin), double-clic = 0 dB">
  <svg width="44" height={H + 12} viewBox="-22 -6 44 {H + 12}"
    role="slider" tabindex="0" aria-label="Volume {label}" aria-valuemin={min} aria-valuemax={max} aria-valuenow={value}
    onpointerdown={down} onpointermove={move} onpointerup={() => (drag = null)} onpointercancel={() => (drag = null)}
    ondblclick={() => onchange(0)} onkeydown={key}
    onwheel={e => { e.preventDefault(); set(value - e.deltaY * (e.shiftKey ? 0.005 : 0.05)) }}>
    {#each TICKS.filter(t => t >= min && t <= max) as t (t)}
      <line class="tick" class:zero={t === 0} x1="-20" x2="-9" y1={y(t)} y2={y(t)} />
    {/each}
    <rect class="slot" x="-2" y="0" width="4" height={H} rx="2" />
    <rect class="fill" x="-2" y={y(value)} width="4" height={H - y(value)} rx="2" />
    <rect class="cap" x="-9" y={y(value) - 4} width="18" height="8" rx="2" />
  </svg>
  <span class="value mono">{value <= min ? '-inf' : `${value > 0 ? '+' : ''}${value.toFixed(1)}`}</span>
</div>

<style>
  .fader { display: flex; flex-direction: column; align-items: center; width: 56px; user-select: none; }
  svg { cursor: ns-resize; touch-action: none; outline: none; }
  svg:focus-visible .cap { stroke: var(--accent); }
  .tick { stroke: var(--border); }
  .tick.zero { stroke: var(--muted); }
  .slot { fill: var(--cell-off); }
  .fill { fill: var(--accent); }
  .muted .fill { fill: var(--muted); }
  .cap { fill: var(--panel); stroke: var(--muted); }
  .value { font-size: 10px; }
</style>
