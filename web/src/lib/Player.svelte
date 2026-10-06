<script lang="ts">
  import WaveSurfer from 'wavesurfer.js'
  import RegionsPlugin, { type Region } from 'wavesurfer.js/plugins/regions'
  import { api, mmss, SEGMENT_COLORS, type TrackDetail } from './api'

  let { track, bars = [], sections, currentTime = $bindable(0), playing = $bindable(false) }: {
    track: TrackDetail
    /** Debuts de mesure (s) : la boucle se cale dessus. Vide = pas de calage. */
    bars?: number[]
    /** Structure a afficher (celle de la bank) ; defaut = segments du sidecar. */
    sections?: { start_s: number; end_s: number; label: string }[]
    currentTime?: number
    /** Etat de lecture, lu par le transport de la facade (7.G). */
    playing?: boolean
  } = $props()

  let container: HTMLDivElement
  let ws: WaveSurfer | null = null
  let regions: RegionsPlugin | null = null
  let loopRegion: Region | null = null
  let duration = $state(0)
  let loading = $state(true)
  let error = $state<string | null>(null)

  // boucle : bornes calees sur les mesures
  let loop = $state<{ start: number; end: number; nBars: number } | null>(null)
  let loopOn = $state(true)
  let prevTime = 0

  // zoom molette : px par seconde (0 = ajuste a la largeur)
  let zoom = $state(0)
  let viewStart = $state(0)
  let viewEnd = $state(0)
  const MAX_ZOOM = 600

  function fitZoom(): number {
    return duration > 0 ? container.clientWidth / duration : 1
  }

  function updateView(start?: number, end?: number) {
    if (start !== undefined && end !== undefined) {
      viewStart = start
      viewEnd = end
      return
    }
    const px = zoom > 0 ? zoom : fitZoom()
    viewStart = (ws?.getScroll() ?? 0) / px
    viewEnd = viewStart + container.clientWidth / px
  }

  function setZoom(next: number) {
    const fit = fitZoom()
    zoom = next <= fit * 1.01 ? 0 : Math.min(MAX_ZOOM, next)
    ws?.zoom(zoom)
    requestAnimationFrame(() => updateView())
  }

  function onwheel(e: WheelEvent) {
    // geste horizontal (trackpad) : on laisse defiler ; vertical : zoom
    if (Math.abs(e.deltaX) > Math.abs(e.deltaY) || duration <= 0) return
    e.preventDefault()
    const current = zoom > 0 ? zoom : fitZoom()
    setZoom(current * Math.exp(-e.deltaY * 0.002))
  }

  /** Saute a `t` secondes (appele par la vue bank / la partition de mutes). */
  export function seek(t: number) {
    ws?.setTime(t)
  }

  /** [PLAY] de la facade : lecture / pause, comme un second appui sur la machine. */
  export function playPause() {
    ws?.playPause()
  }

  /** [STOP] de la facade : arret et retour en `t` (debut du pattern en cours). */
  export function stop(t: number) {
    ws?.pause()
    ws?.setTime(t)
  }

  function cssVar(name: string): string {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  }

  function nearestBar(t: number): number {
    let best = 0
    for (let i = 1; i < bars.length; i++) {
      if (Math.abs(bars[i] - t) < Math.abs(bars[best] - t)) best = i
    }
    return best
  }

  /** Cale une region sur un nombre entier de mesures (au moins 1). */
  function snap(region: Region) {
    let start = region.start
    let end = region.end
    let nBars = 0
    if (bars.length > 1) {
      const i0 = Math.min(nearestBar(start), bars.length - 2)
      const i1 = Math.max(nearestBar(end), i0 + 1)
      start = bars[i0]
      end = bars[i1]
      nBars = i1 - i0
    }
    region.setOptions({ start, end, content: nBars ? `${nBars} mes.` : 'boucle' })
    loop = { start, end, nBars }
  }

  function setLoopBars(nBars: number) {
    if (!loop || !loopRegion || bars.length < 2 || nBars < 1) return
    const i0 = nearestBar(loop.start)
    const i1 = Math.min(i0 + nBars, bars.length - 1)
    loopRegion.setOptions({ start: bars[i0], end: bars[i1] })
    snap(loopRegion)
  }

  /** Boucle sur [start, end] (double-clic sur un maillon de la chaine), calee sur les mesures. */
  export function setLoop(start: number, end: number) {
    regions?.addRegion({ start, end, color: 'rgba(232, 89, 12, 0.22)' })  // -> region-created
  }

  export function clearLoop() {
    regions?.clearRegions()
    loopRegion = null
    loop = null
  }

  // non passif : sinon preventDefault est ignore et la page defile en zoomant
  $effect(() => {
    container.addEventListener('wheel', onwheel, { passive: false })
    return () => container.removeEventListener('wheel', onwheel)
  })

  $effect(() => {
    const slug = track.slug
    loading = true
    error = null
    playing = false
    loop = null
    loopRegion = null
    const reg = RegionsPlugin.create()
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
      plugins: [reg],
    })
    inst.on('ready', () => {
      loading = false
      duration = inst.getDuration()
      zoom = 0
      updateView(0, duration)
    })
    inst.on('scroll', (start, end) => updateView(start, end))
    // glisser sur la forme d'onde = nouvelle boucle ; un simple clic = seek
    reg.enableDragSelection({ color: 'rgba(232, 89, 12, 0.22)' }, 4)
    reg.on('region-created', region => {
      for (const r of reg.getRegions()) if (r !== region) r.remove()
      loopRegion = region
      loopOn = true
      snap(region)
      inst.setTime(region.start)
    })
    reg.on('region-updated', region => snap(region))
    reg.on('region-clicked', (region, e) => {
      e.stopPropagation()
      inst.setTime(region.start)
    })
    inst.on('timeupdate', t => {
      if (loop && loopOn && prevTime < loop.end && t >= loop.end) {
        inst.setTime(loop.start)
        t = loop.start
      }
      prevTime = t
      currentTime = t
    })
    inst.on('play', () => { playing = true })
    inst.on('pause', () => { playing = false })
    inst.on('error', err => { error = String(err); loading = false })
    ws = inst
    regions = reg
    return () => inst.destroy()
  })

  function onkey(e: KeyboardEvent) {
    const target = e.target as HTMLElement
    if (target.tagName === 'INPUT' || target.tagName === 'SELECT') return
    if (e.code === 'Space') { e.preventDefault(); ws?.playPause() }
    if (e.code === 'ArrowLeft') ws?.setTime(Math.max(0, (ws?.getCurrentTime() ?? 0) - 10))
    if (e.code === 'ArrowRight') ws?.setTime((ws?.getCurrentTime() ?? 0) + 10)
    if (e.code === 'KeyL' && loop) loopOn = !loopOn
    if (e.code === 'Escape') clearLoop()
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

  {#if duration > 0}
    <div class="sections" aria-label="Sections">
      {#each (sections ?? track.segments).filter(s => s.end_s > viewStart && s.start_s < viewEnd) as s}
        <button class="section" title="{s.label} · {mmss(s.start_s)}"
          style="left: {((Math.max(s.start_s, viewStart) - viewStart) / (viewEnd - viewStart)) * 100}%; width: {((Math.min(s.end_s, viewEnd) - Math.max(s.start_s, viewStart)) / (viewEnd - viewStart)) * 100}%; --c: {SEGMENT_COLORS[s.label] ?? '#888888'}"
          onclick={() => seek(s.start_s)}>{s.label}</button>
      {/each}
    </div>
  {/if}

  <div class="tools">
    <span class="mono small muted">zoom {zoom > 0 ? `x${(zoom / fitZoom()).toFixed(1)}` : 'ajusté'}</span>
    {#if zoom > 0}<button class="small" onclick={() => setZoom(0)}>Ajuster</button>{/if}
    {#if loop}
      <button class:on={loopOn} onclick={() => (loopOn = !loopOn)}>Boucle {loopOn ? 'ON' : 'OFF'}</button>
      <span class="mono small">
        {loop.nBars ? `${loop.nBars} mesure${loop.nBars > 1 ? 's' : ''}` : 'non calée'}
        · {mmss(loop.start)}–{mmss(loop.end)}
      </span>
      {#if loop.nBars}
        <button class="small" onclick={() => setLoopBars(Math.max(1, Math.floor(loop!.nBars / 2)))}>÷2</button>
        <button class="small" onclick={() => setLoopBars(loop!.nBars * 2)}>×2</button>
      {/if}
      <button class="small" onclick={clearLoop}>Retirer</button>
    {:else}
      <span class="muted small">Glisser sur la forme d'onde pour créer une boucle {bars.length > 1 ? 'calée sur les mesures' : '(pas de grille de mesures pour ce morceau)'}.</span>
    {/if}
    {#each track.cues as c}
      <button class="small" onclick={() => seek(c.time_s)}>{c.type} <span class="mono">{mmss(c.time_s)}</span></button>
    {/each}
  </div>

  {#if loading}<p class="muted small">Chargement et décodage de l'audio…</p>{/if}
  {#if error}<p class="small err">Erreur audio : {error}</p>{/if}
  <p class="muted small">Clic : position · glisser : boucle · molette : zoom · Espace : lecture / pause · flèches : ±10 s · L : boucle on/off · Échap : retirer la boucle</p>
</section>

<style>
  .player { padding: 12px 16px; border-bottom: 1px solid var(--border); background: var(--panel); }
  header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
  h1 { font-size: 17px; margin: 0; }
  header p { margin: 2px 0 8px; font-size: 12px; }
  .transport { display: flex; align-items: center; gap: 10px; }
  .wave { width: 100%; }
  .wave :global([part~="region-content"]) { font-size: 11px; padding: 2px 4px; color: var(--accent); font-weight: 600; }
  .sections { position: relative; height: 18px; margin-top: 4px; overflow: hidden; }
  .section {
    position: absolute; top: 0; height: 18px; padding: 0 4px; border: 0; border-radius: 0;
    background: color-mix(in srgb, var(--c) 35%, transparent);
    border-left: 2px solid var(--c);
    font-size: 10px; text-align: left; overflow: hidden; white-space: nowrap; color: var(--text);
  }
  .section:hover { background: color-mix(in srgb, var(--c) 60%, transparent); }
  .tools { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; margin-top: 8px; }
  .small { font-size: 12px; }
  .err { color: #dc2626; }
  p.small { margin: 6px 0 0; }
</style>
