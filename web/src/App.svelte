<script lang="ts">
  // Coquille de l'app : barre generale (telecommande du deck en focus),
  // panneau lateral minimisable (Morceaux, Samples, Sound design, Knowledge) ; les vues
  // visitees restent montees (lecture qui continue, etat garde).
  import { tick } from 'svelte'
  import { remote } from './lib/remote.svelte'
  import { api, type Bank, type TrackDetail, type TrackSummary } from './lib/api'
  import TrackList from './lib/TrackList.svelte'
  import Player from './lib/Player.svelte'
  import BankView from './lib/BankView.svelte'
  import KbPanel from './lib/KbPanel.svelte'
  import GrabPanel from './lib/GrabPanel.svelte'
  import SampleView from './lib/SampleView.svelte'
  import SoundDesignView from './lib/SoundDesignView.svelte'

  let tracks = $state<TrackSummary[]>([])
  let selected = $state<string | null>(null)
  let detail = $state<TrackDetail | null>(null)
  let bank = $state<Bank | null>(null)
  let bankState = $state<'idle' | 'loading' | 'missing' | 'generating' | 'error'>('idle')
  let bankError = $state('')
  let currentTime = $state(0)
  let playing = $state(false)
  let listError = $state('')
  let player: Player | undefined = $state()
  let kbPanel: KbPanel | undefined = $state()
  let kbPage: KbPanel | undefined = $state()
  let grabPanel: GrabPanel | undefined = $state()
  let trackList: TrackList | undefined = $state()
  let looping = $state(false)
  let autoplay = $state(false)

  // morceau ajoute (7.I) : liste rechargee, puis ouverture du morceau
  async function added(slug: string) {
    tracks = await api.tracks()
    if (!showList) toggleList()
    await select(slug)
  }

  // derniere proposition du filtre : recherche en ligne sous la liste
  function online(q: string) {
    if (!showList) toggleList()
    grabPanel?.searchFor(q)
  }

  // vue principale (memorisee) ; samples, sound design et knowledge montees a la premiere visite
  type View = 'tracks' | 'samples' | 'sounddesign' | 'knowledge'
  const VIEWS: View[] = ['tracks', 'samples', 'sounddesign', 'knowledge']
  let initial: View = 'tracks'
  try {
    const v = localStorage.getItem('ui:view') as View | null
    if (v && VIEWS.includes(v)) initial = v
  } catch { /* stockage indisponible */ }
  let view = $state<View>(initial)
  let visited = $state<Record<View, boolean>>({ tracks: true, samples: initial === 'samples', sounddesign: initial === 'sounddesign', knowledge: initial === 'knowledge' })
  if (initial !== 'knowledge') remote.focus = initial
  function setView(v: View) {
    // second clic sur Morceaux : replie / deplie la liste
    if (v === 'tracks' && view === 'tracks') toggleList()
    view = v
    visited[v] = true
    if (v !== 'knowledge') remote.focus = v
    try { localStorage.setItem('ui:view', v) } catch { /* stockage indisponible */ }
  }

  /** Bouton source de la barre : ouvre la vue et y met la telecommande (sans replier la liste). */
  function showView(v: 'tracks' | 'samples') {
    if (view !== v) setView(v)
    remote.focus = v
  }

  async function knowledge(page?: number) {
    setView('knowledge')
    await tick()
    if (page) kbPage?.openManual(page)
    else kbPage?.show()
  }

  // panneau lateral : icones seules ou icones + libelles (memorise)
  let railMini = $state(false)
  try { railMini = localStorage.getItem('ui:rail') === 'mini' } catch { /* stockage indisponible */ }
  function toggleRail() {
    railMini = !railMini
    try { localStorage.setItem('ui:rail', railMini ? 'mini' : 'full') } catch { /* stockage indisponible */ }
  }

  // deck « morceaux » de la telecommande
  remote.register('tracks', {
    get label() { return detail ? `${detail.artist} — ${detail.title}` : '' },
    get playing() { return playing },
    get looping() { return looping },
    playPause: () => player?.playPause(),
    pause: () => player?.pause(),
    toggleLoop: () => player?.toggleLoop(),
    prev: () => stepTrack(-1),
    next: () => stepTrack(1),
  })
  $effect(() => { if (playing) remote.played('tracks') })

  /** Morceau voisin dans l'ordre de la liste filtree ; la lecture continue. */
  function stepTrack(delta: number) {
    const slug = trackList?.neighbor(delta)
    if (slug) select(slug, playing)
  }

  function onkey(e: KeyboardEvent) {
    const t = e.target as HTMLElement
    if (t.tagName === 'INPUT' || t.tagName === 'SELECT' || t.tagName === 'TEXTAREA' || t.isContentEditable) return
    if (e.key === '/') { e.preventDefault(); knowledge() }
    // en Knowledge, Espace pilote la telecommande (les vues masquees ignorent le clavier)
    else if (e.code === 'Space' && view === 'knowledge') { e.preventDefault(); remote.deck?.playPause() }
  }

  // liste des morceaux repliable pour laisser toute la largeur a la DT2 (memorise)
  let showList = $state(true)
  try { showList = localStorage.getItem('ui:list') !== '0' } catch { /* stockage indisponible */ }
  function toggleList() {
    showList = !showList
    try { localStorage.setItem('ui:list', showList ? '1' : '0') } catch { /* stockage indisponible */ }
  }

  // dernier morceau ouvert, rouvert au chargement s'il est toujours dans la library
  const LAST_KEY = 'ui:last-slug'
  api.tracks().then(t => {
    tracks = t
    let last: string | null = null
    try { last = localStorage.getItem(LAST_KEY) } catch { /* stockage indisponible */ }
    if (last && !selected && t.some(x => x.slug === last)) select(last)
  }).catch(e => (listError = String(e)))

  async function select(slug: string, play = false) {
    autoplay = play
    playing = false
    selected = slug
    try { localStorage.setItem(LAST_KEY, slug) } catch { /* stockage indisponible */ }
    detail = null
    bank = null
    currentTime = 0
    bankState = 'loading'
    detail = await api.track(slug)
    try {
      bank = await api.bank(slug)
      bankState = 'idle'
    } catch {
      bankState = 'missing'
    }
  }

  async function generate() {
    if (!selected) return
    bankState = 'generating'
    try {
      const slug = selected
      bank = await api.generateBank(slug)
      bankState = 'idle'
      // harmonie recalculee avec la bank (7.H) : mise a jour des seuls champs
      // concernes, sans remplacer detail (le lecteur rechargerait l'audio)
      const fresh = await api.track(slug)
      if (detail && detail.slug === slug) {
        detail.harmony = fresh.harmony
        detail.keyboard_setup = fresh.keyboard_setup
      }
      tracks = tracks.map(t => (t.slug === selected ? { ...t, has_bank: true } : t))
    } catch (e) {
      bankState = 'error'
      bankError = e instanceof Error ? e.message : String(e)
    }
  }
</script>

<svelte:window onkeydown={onkey} />

{#snippet icon(name: string)}
  <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    {#if name === 'tracks'}<path d="M9 18V5l11-2v13" /><circle cx="6" cy="18" r="3" /><circle cx="17" cy="16" r="3" />
    {:else if name === 'samples'}<rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" />
    {:else if name === 'sounddesign'}<circle cx="7" cy="8" r="3" /><path d="M7 8 8.5 6.5" /><circle cx="17" cy="8" r="3" /><path d="m17 8-1.5-1.5" /><path d="M5 15v6M12 13v8M19 17v4" /><path d="M3 15h4M10 13h4M17 17h4" />
    {:else if name === 'knowledge'}<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z" /><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5" />
    {:else if name === 'prev'}<path d="M19 20 9 12l10-8z" fill="currentColor" /><path d="M5 19V5" />
    {:else if name === 'next'}<path d="m5 4 10 8-10 8z" fill="currentColor" /><path d="M19 5v14" />
    {:else if name === 'play'}<path d="m7 4 13 8-13 8z" fill="currentColor" />
    {:else if name === 'pause'}<rect x="6" y="4" width="4" height="16" fill="currentColor" /><rect x="14" y="4" width="4" height="16" fill="currentColor" />
    {:else if name === 'loop'}<path d="m17 2 4 4-4 4" /><path d="M3 11v-1a4 4 0 0 1 4-4h14" /><path d="m7 22-4-4 4-4" /><path d="M21 13v1a4 4 0 0 1-4 4H3" />
    {:else if name === 'collapse'}<path d="m15 18-6-6 6-6" />
    {:else if name === 'expand'}<path d="m9 18 6-6-6-6" />
    {/if}
  </svg>
{/snippet}

<div class="app">
<header class="toolbar">
  <strong>Digitakt II</strong>
  <div class="remote" role="group" aria-label="Télécommande">
    <div class="seg small" role="group" aria-label="Source">
      <button aria-pressed={remote.focus === 'tracks'} onclick={() => showView('tracks')}
        title="Vue Morceaux, télécommande sur le morceau">Morceau</button>
      <button aria-pressed={remote.focus === 'samples'} onclick={() => showView('samples')}
        title="Vue Samples, télécommande sur le sample">Sample</button>
    </div>
    {#if remote.deck}
      {@const d = remote.deck}
      <button class="ic" onclick={() => d.prev()} disabled={!d.label} title={remote.focus === 'tracks' ? 'Morceau précédent de la liste' : remote.focus === 'sounddesign' ? 'Preset précédent' : 'Sample précédent'}>{@render icon('prev')}</button>
      <button class="ic" class:on={d.playing} onclick={() => d.playPause()} disabled={!d.label} title="Lecture / pause">{@render icon(d.playing ? 'pause' : 'play')}</button>
      <button class="ic" class:on={d.looping} onclick={() => d.toggleLoop()} disabled={!d.label} aria-pressed={d.looping}
        title={remote.focus === 'tracks' ? 'Boucle : région calée si elle existe, sinon morceau entier' : 'Boucle du sample'}>{@render icon('loop')}</button>
      <button class="ic" onclick={() => d.next()} disabled={!d.label} title={remote.focus === 'tracks' ? 'Morceau suivant de la liste' : remote.focus === 'sounddesign' ? 'Preset suivant' : 'Sample suivant'}>{@render icon('next')}</button>
      <span class="now small" title={d.label}>{d.label || 'rien de chargé'}</span>
    {/if}
  </div>
  <nav>
    <button class="small" onclick={() => knowledge(1)}>Manuel PDF</button>
  </nav>
</header>
<div class="body">
  <nav class="rail" class:mini={railMini} aria-label="Sections">
    <button aria-pressed={view === 'tracks'} onclick={() => setView('tracks')}
      title={view === 'tracks' ? (showList ? 'Replier la liste des morceaux' : 'Déplier la liste des morceaux') : 'Morceaux'}>
      {@render icon('tracks')}<span>Morceaux</span></button>
    <button aria-pressed={view === 'samples'} onclick={() => setView('samples')} title="Samples : écoute garder / écarter">
      {@render icon('samples')}<span>Samples</span></button>
    <button aria-pressed={view === 'sounddesign'} onclick={() => setView('sounddesign')} title="Sound design : traitements par chaînes de plugins (rumble…)">
      {@render icon('sounddesign')}<span>Sound design</span></button>
    <button aria-pressed={view === 'knowledge'} onclick={() => knowledge()} title="Knowledge : fiches, doctrine, manuel (/)">
      {@render icon('knowledge')}<span>Knowledge</span></button>
    <button class="fold" onclick={toggleRail} title={railMini ? 'Afficher les libellés' : 'Réduire aux icônes'}>
      {@render icon(railMini ? 'expand' : 'collapse')}<span>Réduire</span></button>
  </nav>
  <div class="views">
<div class="layout" class:full={!showList} class:off={view !== 'tracks'}>
  <aside class:off={!showList}>
    {#if listError}<p class="err">API injoignable : {listError}. Lance <code>python scripts/api.py</code>.</p>{/if}
    <TrackList bind:this={trackList} {tracks} {selected} onselect={select} ononline={online} />
    <GrabPanel bind:this={grabPanel} onadded={added} />
  </aside>
  <main>
    {#if detail}
      {#snippet playerView()}
        {#key detail?.slug}
          {#if detail}
            <Player bind:this={player} track={detail} bind:currentTime bind:playing bind:looping {autoplay}
              bars={bank?.bar_times_s?.length ? bank.bar_times_s : detail.bar_times}
              sections={bank?.sections?.length ? bank.sections : undefined} />
          {/if}
        {/key}
      {/snippet}
      {#if bank}
        <BankView {bank} harmony={detail.harmony} {currentTime} {playing} player={playerView} onseek={t => player?.seek(t)}
          onloop={(start, end) => player?.setLoop(start, end)} onplay={() => player?.playPause()} onstop={t => player?.stop(t)}
          onhelp={(path, page) => (path ? kbPanel?.openPath(path) : page && kbPanel?.openManual(page))} />
        <div class="bankbar">
          <span class="muted small">Bank générée le {new Date(bank.generated_at).toLocaleString('fr-FR')}</span>
          <button class="small" onclick={generate} disabled={bankState === 'generating'}>
            {bankState === 'generating' ? 'Analyse en cours…' : 'Régénérer la bank et l’harmonie'}
          </button>
          {#if bankState === 'error'}<span class="err">{bankError}</span>{/if}
        </div>
      {:else}
        {@render playerView()}
      {/if}
      {#if bank}
        <!-- bank affichee ci-dessus -->
      {:else if bankState === 'missing' || bankState === 'error'}
        <div class="empty">
          <p>Pas encore de bank Digitakt pour ce morceau.
            {#if !detail.has_stems}<span class="muted">Sans stems, la détection part du mix (plus bruitée) : <code>python stems.py {detail.slug} --cleanup</code>.</span>{/if}
          </p>
          <button onclick={generate}>Générer la bank et l’harmonie</button>
          {#if bankState === 'error'}<p class="err">{bankError}</p>{/if}
        </div>
      {:else if bankState === 'generating'}
        <p class="empty muted">Analyse en cours (bank puis harmonie, une vingtaine de secondes)…</p>
      {/if}
    {:else}
      <p class="empty muted">Choisis un morceau dans la liste{showList ? '' : ' (icône Morceaux du panneau latéral)'}.</p>
    {/if}
  </main>
</div>
{#if visited.samples}<div class="samples-main" class:off={view !== 'samples'}><SampleView /></div>{/if}
{#if visited.sounddesign}<div class="sd-main" class:off={view !== 'sounddesign'}><SoundDesignView ongotosamples={() => showView('samples')} /></div>{/if}
{#if visited.knowledge}<div class="kb-main" class:off={view !== 'knowledge'}><KbPanel page bind:this={kbPage} /></div>{/if}
  </div>
</div>
</div>
<KbPanel bind:this={kbPanel} />

<style>
  .app { display: flex; flex-direction: column; height: 100%; }
  .toolbar { display: flex; align-items: center; gap: 14px; padding: 6px 16px; border-bottom: 1px solid var(--border); background: var(--panel); }
  .toolbar nav { margin-left: auto; display: flex; gap: 6px; }
  .remote { display: flex; align-items: center; gap: 4px; min-width: 0; flex: 1; }
  .remote .seg { margin-right: 6px; }
  .ic { display: inline-flex; align-items: center; justify-content: center; padding: 4px 8px; }
  .ic.on { background: var(--accent); border-color: var(--accent); color: #fff; }
  .now { margin-left: 6px; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--muted); }
  .seg { display: inline-flex; }
  .seg button { border-radius: 0; padding: 3px 8px; }
  .seg button:first-child { border-radius: 4px 0 0 4px; }
  .seg button:last-child { border-radius: 0 4px 4px 0; margin-left: -1px; }
  .seg button[aria-pressed='true'] { border-color: var(--accent); color: var(--accent); position: relative; }
  .body { display: flex; flex: 1; min-height: 0; }
  .rail { display: flex; flex-direction: column; gap: 2px; padding: 8px 6px; width: 150px; flex: none; border-right: 1px solid var(--border); background: var(--panel); }
  .rail button { display: flex; align-items: center; gap: 10px; border: 0; background: none; padding: 8px 10px; text-align: left; color: var(--muted); }
  .rail button:hover { background: var(--panel-2); color: var(--text); }
  .rail button[aria-pressed='true'] { color: var(--accent); background: var(--panel-2); box-shadow: inset 3px 0 0 var(--accent); }
  .rail .fold { margin-top: auto; }
  .rail.mini { width: 48px; }
  .rail.mini span { display: none; }
  .views { flex: 1; min-width: 0; min-height: 0; display: flex; flex-direction: column; }
  .off { display: none !important; }
  .samples-main, .sd-main, .kb-main { flex: 1; min-height: 0; overflow: hidden; }
  .layout { display: grid; grid-template-columns: 320px 1fr; flex: 1; min-height: 0; }
  .layout.full { grid-template-columns: 1fr; }
  aside { border-right: 1px solid var(--border); background: var(--panel); min-height: 0; overflow: hidden; display: flex; flex-direction: column; }
  main { overflow-y: auto; min-width: 0; }
  .empty { padding: 24px 16px; }
  .bankbar { display: flex; gap: 10px; align-items: center; justify-content: center; padding: 0 16px 16px; flex-wrap: wrap; }
  .small { font-size: 12px; }
  .err { color: #dc2626; padding: 0 10px; font-size: 12px; }
  @media (max-width: 760px) {
    .rail { width: 48px; }
    .rail span { display: none; }
    .now { display: none; }
    .layout { grid-template-columns: 1fr; grid-template-rows: 40vh 1fr; }
    .layout.full { grid-template-rows: 1fr; }
    aside { border-right: 0; border-bottom: 1px solid var(--border); }
  }
</style>
