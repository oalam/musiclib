<script lang="ts">
  import { api, type Bank, type TrackDetail, type TrackSummary } from './lib/api'
  import TrackList from './lib/TrackList.svelte'
  import Player from './lib/Player.svelte'
  import BankView from './lib/BankView.svelte'

  let tracks = $state<TrackSummary[]>([])
  let selected = $state<string | null>(null)
  let detail = $state<TrackDetail | null>(null)
  let bank = $state<Bank | null>(null)
  let bankState = $state<'idle' | 'loading' | 'missing' | 'generating' | 'error'>('idle')
  let bankError = $state('')
  let currentTime = $state(0)
  let listError = $state('')
  let player: Player | undefined = $state()

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
      bank = await api.generateBank(selected)
      bankState = 'idle'
      tracks = tracks.map(t => (t.slug === selected ? { ...t, has_bank: true } : t))
    } catch (e) {
      bankState = 'error'
      bankError = e instanceof Error ? e.message : String(e)
    }
  }
</script>

<div class="layout">
  <aside>
    {#if listError}<p class="err">API injoignable : {listError}. Lance <code>python scripts/api.py</code>.</p>{/if}
    <TrackList {tracks} {selected} onselect={select} />
  </aside>
  <main>
    {#if detail}
      {#key detail.slug}
        <Player bind:this={player} track={detail} bind:currentTime
          bars={bank?.bar_times_s?.length ? bank.bar_times_s : detail.bar_times}
          sections={bank?.sections?.length ? bank.sections : undefined} />
      {/key}
      {#if bank}
        <div class="bankbar">
          <span class="muted small">Bank générée le {new Date(bank.generated_at).toLocaleString('fr-FR')}</span>
          <button class="small" onclick={generate} disabled={bankState === 'generating'}>
            {bankState === 'generating' ? 'Analyse en cours…' : 'Régénérer la bank'}
          </button>
          {#if bankState === 'error'}<span class="err">{bankError}</span>{/if}
        </div>
        <BankView {bank} {currentTime} onseek={t => player?.seek(t)} />
      {:else if bankState === 'missing' || bankState === 'error'}
        <div class="empty">
          <p>Pas encore de bank Digitakt pour ce morceau.
            {#if !detail.has_stems}<span class="muted">Sans stems, la détection part du mix (plus bruitée) : <code>python stems.py {detail.slug} --cleanup</code>.</span>{/if}
          </p>
          <button onclick={generate}>Générer la bank</button>
          {#if bankState === 'error'}<p class="err">{bankError}</p>{/if}
        </div>
      {:else if bankState === 'generating'}
        <p class="empty muted">Analyse en cours (quelques secondes)…</p>
      {/if}
    {:else}
      <p class="empty muted">Choisis un morceau dans la liste.</p>
    {/if}
  </main>
</div>

<style>
  .layout { display: grid; grid-template-columns: 320px 1fr; height: 100%; }
  aside { border-right: 1px solid var(--border); background: var(--panel); min-height: 0; overflow: hidden; display: flex; flex-direction: column; }
  main { overflow-y: auto; min-width: 0; }
  .empty { padding: 24px 16px; }
  .bankbar { display: flex; gap: 10px; align-items: center; justify-content: flex-end; padding: 10px 16px 0; flex-wrap: wrap; }
  .small { font-size: 12px; }
  .err { color: #dc2626; padding: 0 10px; font-size: 12px; }
  @media (max-width: 760px) {
    .layout { grid-template-columns: 1fr; grid-template-rows: 40vh 1fr; }
    aside { border-right: 0; border-bottom: 1px solid var(--border); }
  }
</style>
