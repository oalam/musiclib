<script lang="ts">
  import WaveSurfer from 'wavesurfer.js'
  import RegionsPlugin from 'wavesurfer.js/plugins/regions'
  import { api, mmss, SEGMENT_COLORS, type TrackDetail } from './api'

  let { track, currentTime = $bindable(0) }: {
    track: TrackDetail
    currentTime?: number
  } = $props()

  let container: HTMLDivElement
  let ws: WaveSurfer | null = null
  let playing = $state(false)
  let duration = $state(0)
  let loading = $state(true)
  let error = $state<string | null>(null)

  /** Saute a `t` secondes (appele par la vue bank / la partition de mutes). */
  export function seek(t: number) {
    ws?.setTime(t)
  }

  function cssVar(name: string): string {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  }

  $effect(() => {
    const slug = track.slug
    const segments = track.segments
    loading = true
    error = null
    playing = false
    const regions = RegionsPlugin.create()
    const inst = WaveSurfer.create({
      container,
      url: api.audioUrl(slug),
      height: 96,
      waveColor: cssVar('--wave'),
      progressColor: cssVar('--wave-progress'),
      cursorColor: cssVar('--accent'),
      barWidth: 2,
      barGap: 1,
      normalize: true,
      plugins: [regions],
    })
    inst.on('ready', () => {
      loading = false
      duration = inst.getDuration()
      for (const s of segments) {
        regions.addRegion({
          start: s.start_s,
          end: s.end_s,
          color: (SEGMENT_COLORS[s.label] ?? '#888888') + '33',
          content: s.label,
          drag: false,
          resize: false,
        })
      }
    })
    regions.on('region-clicked', (region, e) => {
      e.stopPropagation()
      inst.setTime(region.start)
    })
    inst.on('timeupdate', t => { currentTime = t })
    inst.on('play', () => { playing = true })
    inst.on('pause', () => { playing = false })
    inst.on('error', err => { error = String(err); loading = false })
    ws = inst
    return () => inst.destroy()
  })

  function onkey(e: KeyboardEvent) {
    const target = e.target as HTMLElement
    if (target.tagName === 'INPUT' || target.tagName === 'SELECT') return
    if (e.code === 'Space') { e.preventDefault(); ws?.playPause() }
    if (e.code === 'ArrowLeft') ws?.setTime(Math.max(0, (ws?.getCurrentTime() ?? 0) - 10))
    if (e.code === 'ArrowRight') ws?.setTime((ws?.getCurrentTime() ?? 0) + 10)
  }
</script>

<svelte:window onkeydown={onkey} />

<section class="player">
  <header>
    <div>
      <h1>{track.artist} — {track.title}</h1>
      <p class="muted mono">
        {track.bpm ? Math.round(parseFloat(track.bpm)) : '?'} BPM · {track.key || '?'}
        · {track.time_signature ?? '?'} · {track.genre || '?'}
        {#if track.mood}· {track.mood}{/if}
      </p>
    </div>
    <div class="transport">
      <button class:on={playing} onclick={() => ws?.playPause()} disabled={loading}>
        {playing ? 'Pause' : 'Lecture'}
      </button>
      <span class="mono">{mmss(currentTime)} / {mmss(duration)}</span>
    </div>
  </header>
  <div class="wave" bind:this={container}></div>
  {#if loading}<p class="muted small">Chargement et décodage de l'audio…</p>{/if}
  {#if error}<p class="small err">Erreur audio : {error}</p>{/if}
  {#if track.cues.length}
    <div class="cues">
      {#each track.cues as c}
        <button class="small" onclick={() => seek(c.time_s)}>{c.type} <span class="mono">{mmss(c.time_s)}</span></button>
      {/each}
    </div>
  {/if}
  <p class="muted small">Espace : lecture / pause · flèches : ±10 s · clic sur une section : saut au début</p>
</section>

<style>
  .player { padding: 12px 16px; border-bottom: 1px solid var(--border); background: var(--panel); }
  header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
  h1 { font-size: 17px; margin: 0; }
  header p { margin: 2px 0 8px; font-size: 12px; }
  .transport { display: flex; align-items: center; gap: 10px; }
  .wave { width: 100%; }
  .wave :global([part~="region-content"]) { font-size: 11px; padding: 2px 4px; color: var(--muted); }
  .cues { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
  .small { font-size: 12px; }
  .err { color: #dc2626; }
  p.small { margin: 6px 0 0; }
</style>
