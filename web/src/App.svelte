<script lang="ts">
  import { api, type Bank, type TrackDetail, type TrackSummary } from './lib/api'
  import TrackList from './lib/TrackList.svelte'
  import Player from './lib/Player.svelte'
  import BankView from './lib/BankView.svelte'
  import KbPanel from './lib/KbPanel.svelte'

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

  // liste des morceaux repliable pour laisser toute la largeur a la DT2 (memorise)
  let showList = $state(true)
  try { showList = localStorage.getItem('ui:list') !== '0' } catch { /* stockage indisponible */ }
  function toggleList() {
    showList = !showList
    try { localStorage.setItem('ui:list', showList ? '1' : '0') } catch { /* stockage indisponible */ }
  }

  api.tracks().then(t => (tracks = t)).catch(e => (listError = String(e)))

  async function select(slug: string) {
    selected = slug
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

<div class="app">
<header class="topbar">
  <button class="small" onclick={toggleList} aria-pressed={showList}
    title="Afficher / masquer la liste des morceaux">{showList ? '◀ Morceaux' : '▶ Morceaux'}</button>
  <strong>Digitakt II</strong>
  <span class="muted small">morceaux → banks → set</span>
  <nav>
    <button class="small" onclick={() => kbPanel?.show()} title="Fiches par lot et recherche">
      Base de connaissance <kbd>/</kbd>
    </button>
    <button class="small" onclick={() => kbPanel?.openManual(1)}>Manuel PDF</button>
  </nav>
</header>
<div class="layout" class:full={!showList}>
  {#if showList}
  <aside>
    {#if listError}<p class="err">API injoignable : {listError}. Lance <code>python scripts/api.py</code>.</p>{/if}
    <TrackList {tracks} {selected} onselect={select} />
  </aside>
  {/if}
  <main>
    {#if detail}
      {#snippet playerView()}
        {#key detail?.slug}
          {#if detail}
            <Player bind:this={player} track={detail} bind:currentTime bind:playing
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
      <p class="empty muted">Choisis un morceau dans la liste{showList ? '' : ' (bouton ▶ Morceaux)'}.</p>
    {/if}
  </main>
</div>
</div>
<KbPanel bind:this={kbPanel} />

<style>
  .app { display: flex; flex-direction: column; height: 100%; }
  .topbar { display: flex; align-items: center; gap: 10px; padding: 8px 16px; border-bottom: 1px solid var(--border); background: var(--panel); }
  .topbar nav { margin-left: auto; display: flex; gap: 6px; }
  kbd { font-family: ui-monospace, Menlo, monospace; font-size: 11px; border: 1px solid var(--border); border-radius: 3px; padding: 0 4px; margin-left: 4px; }
  .layout { display: grid; grid-template-columns: 320px 1fr; flex: 1; min-height: 0; }
  .layout.full { grid-template-columns: 1fr; }
  aside { border-right: 1px solid var(--border); background: var(--panel); min-height: 0; overflow: hidden; display: flex; flex-direction: column; }
  main { overflow-y: auto; min-width: 0; }
  .empty { padding: 24px 16px; }
  .bankbar { display: flex; gap: 10px; align-items: center; justify-content: center; padding: 0 16px 16px; flex-wrap: wrap; }
  .small { font-size: 12px; }
  .err { color: #dc2626; padding: 0 10px; font-size: 12px; }
  @media (max-width: 760px) {
    .layout { grid-template-columns: 1fr; grid-template-rows: 40vh 1fr; }
    .layout.full { grid-template-rows: 1fr; }
    aside { border-right: 0; border-bottom: 1px solid var(--border); }
  }
</style>
