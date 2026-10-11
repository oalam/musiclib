<script lang="ts">
  // Forme d'onde du lecteur du sound design : crete min / max par colonne de
  // pixels (canaux melanges), grille des tranches en variations, tete de
  // lecture animee tant que `pos` renvoie une position (0..1).
  import { onDestroy } from 'svelte'

  let { buffer, pos, slices = 0, label = '' }: {
    buffer: AudioBuffer | null
    /** Position de lecture 0..1, null a l'arret. */
    pos: () => number | null
    slices?: number
    label?: string
  } = $props()

  let canvas: HTMLCanvasElement | undefined = $state()
  let width = $state(0)
  const HEIGHT = 72
  let head = $state<number | null>(null)

  /** Crete min / max de chaque colonne. */
  function peaks(buf: AudioBuffer, cols: number): Float32Array {
    const out = new Float32Array(cols * 2)
    const chans = Array.from({ length: buf.numberOfChannels }, (_, c) => buf.getChannelData(c))
    const step = buf.length / cols
    for (let x = 0; x < cols; x++) {
      let lo = 0, hi = 0
      const end = Math.min(buf.length, Math.floor((x + 1) * step))
      for (let i = Math.floor(x * step); i < end; i++) {
        let v = 0
        for (const ch of chans) v += ch[i]
        v /= chans.length
        if (v < lo) lo = v
        if (v > hi) hi = v
      }
      out[2 * x] = lo
      out[2 * x + 1] = hi
    }
    return out
  }

  $effect(() => {
    if (!canvas || !width) return
    const dpr = window.devicePixelRatio || 1
    canvas.width = Math.round(width * dpr)
    canvas.height = Math.round(HEIGHT * dpr)
    const g = canvas.getContext('2d')!
    g.setTransform(dpr, 0, 0, dpr, 0, 0)
    g.clearRect(0, 0, width, HEIGHT)
    const css = getComputedStyle(canvas)
    const mid = HEIGHT / 2
    g.fillStyle = css.getPropertyValue('--border') || '#444'
    g.fillRect(0, mid, width, 1)
    if (!buffer) return
    const p = peaks(buffer, Math.max(1, Math.floor(width)))
    g.fillStyle = css.getPropertyValue('--wave') || css.getPropertyValue('--accent') || '#e5b80b'
    for (let x = 0; x < p.length / 2; x++) {
      const y0 = mid - p[2 * x + 1] * mid, y1 = mid - p[2 * x] * mid
      g.fillRect(x, y0, 1, Math.max(1, y1 - y0))
    }
    if (slices > 1) {
      g.fillStyle = css.getPropertyValue('--muted') || '#888'
      for (let i = 1; i < slices; i++) g.fillRect(Math.round((i * width) / slices), 0, 1, HEIGHT)
    }
  })

  let raf = 0
  function tick() {
    head = pos()
    raf = requestAnimationFrame(tick)
  }
  raf = requestAnimationFrame(tick)
  onDestroy(() => cancelAnimationFrame(raf))
</script>

<div class="wave" bind:clientWidth={width} title={label}>
  <canvas bind:this={canvas} style:height="{HEIGHT}px"></canvas>
  {#if head !== null && buffer}<span class="head" style:left="{head * 100}%"></span>{/if}
  {#if !buffer}<span class="empty small muted">▶ Écouter pour afficher la forme d'onde</span>{/if}
  {#if buffer}<span class="dur small muted mono">{label ? `${label} · ` : ''}{buffer.duration.toFixed(3)} s</span>{/if}
</div>

<style>
  .wave { position: relative; width: 100%; background: var(--panel-2); border: 1px solid var(--border); border-radius: 4px; overflow: hidden; }
  canvas { display: block; width: 100%; }
  .head { position: absolute; top: 0; bottom: 0; width: 1px; background: var(--text, #fff); pointer-events: none; }
  .empty { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
  .dur { position: absolute; right: 6px; top: 2px; font-size: 10px; }
  .small { font-size: 12px; }
</style>
