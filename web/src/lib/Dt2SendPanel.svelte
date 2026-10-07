<script lang="ts">
  import { onDestroy } from 'svelte'
  import { api, type BankTrack, type Dt2Ports, type Dt2SendState, type Pattern } from './api'

  /** Envoi de la track selectionnee a la DT2 (7.E) : la DT2 mene, un passage. */
  let { slug, pattern, track, patternName, onhelp }: {
    slug: string
    pattern: Pattern
    track: BankTrack
    /** Nom du pattern tel qu'affiche sur la facade (ex. A01). */
    patternName: string
    onhelp: (path?: string, page?: number) => void
  } = $props()

  const CHANNEL_KEY = 'dt2-auto-channel'

  let open = $state(false)
  let ports = $state<Dt2Ports | null>(null)
  let port = $state('')
  let channel = $state<number | null>(readChannel())
  let send = $state<Dt2SendState | null>(null)
  let error = $state('')
  let timer: ReturnType<typeof setInterval> | undefined

  const active = $derived(send !== null && (send.status === 'waiting' || send.status === 'sending'))
  const mine = $derived(send !== null && send.request.slug === slug
    && send.request.slot === pattern.slot && send.request.track === track.index)
  const validChannel = $derived(channel !== null && Number.isInteger(channel) && channel >= 1 && channel <= 16)
  const canSend = $derived(!active && !!port && validChannel && track.trigs.length > 0)

  const STATUS: Record<string, string> = {
    waiting: 'En attente du Start de la DT2…',
    sending: 'Envoi en cours',
    done: 'Envoyé',
    cancelled: 'Annulé',
    error: 'Erreur',
  }

  function readChannel(): number | null {
    try {
      const v = Number(localStorage.getItem(CHANNEL_KEY))
      return v >= 1 && v <= 16 ? v : null
    } catch { return null }
  }

  function saveChannel() {
    if (!validChannel) return
    try { localStorage.setItem(CHANNEL_KEY, String(channel)) } catch { /* stockage indisponible */ }
  }

  async function loadPorts() {
    error = ''
    try {
      ports = await api.dt2Ports()
      if (!port || !ports.outputs.includes(port)) port = ports.default ?? ''
      send = await api.dt2SendStatus()
      if (send && (send.status === 'waiting' || send.status === 'sending')) poll()
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  }

  function toggle(e: Event) {
    open = (e.currentTarget as HTMLDetailsElement).open
    if (open && ports === null) loadPorts()
  }

  async function start() {
    if (!canSend || channel === null) return
    error = ''
    saveChannel()
    try {
      send = await api.dt2Send({ slug, slot: pattern.slot, track: track.index, port, channel })
      poll()
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  }

  async function cancel() {
    try { send = await api.dt2SendCancel() } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  }

  function poll() {
    clearInterval(timer)
    timer = setInterval(async () => {
      try {
        send = await api.dt2SendStatus()
        if (!send || (send.status !== 'waiting' && send.status !== 'sending')) clearInterval(timer)
      } catch (err) {
        error = err instanceof Error ? err.message : String(err)
        clearInterval(timer)
      }
    }, 250)
  }

  onDestroy(() => clearInterval(timer))
</script>

<details class="send" ontoggle={toggle}>
  <summary>Envoyer à la DT2 <span class="muted small mono">T{String(track.index).padStart(2, '0')} {track.role}
    · {patternName} · {pattern.steps} pas · {track.trigs.length} trigs</span></summary>

  <div class="body">
    <ol class="howto small">
      <li>Sélectionner la track : <span class="mono">[TRK] + [TRIG {track.index}]</span></li>
      <li>Longueur du pattern : <span class="mono">{pattern.steps} pas</span> (page SCALE)</li>
      <li>Track vide : les trigs déjà présents restent en place (seuls les pas joués sont remplacés)</li>
      <li>Armer l'envoi ici, puis <span class="mono">[RECORD] + [PLAY]</span> sur la machine
        (quantize conseillée : <span class="mono">[RECORD]</span> + double <span class="mono">[PLAY]</span>)</li>
    </ol>

    <div class="row">
      <label>Port
        <select bind:value={port} disabled={active}>
          {#if !ports?.outputs.length}<option value="">aucun port</option>{/if}
          {#each ports?.outputs ?? [] as p (p)}<option value={p}>{p}</option>{/each}
        </select>
      </label>
      <button class="small" onclick={loadPorts} disabled={active} title="Relire les ports MIDI">↻</button>
      <label title="Valeur de [SETTINGS] > MIDI CONFIG > CHANNELS > AUTO CHANNEL, pas le numéro de track : ce canal pilote la track active">AUTO CHANNEL
        <input type="number" min="1" max="16" bind:value={channel} disabled={active} placeholder="1-16" />
      </label>
      {#if active}
        <button onclick={cancel}>Annuler</button>
      {:else}
        <button class="go" onclick={start} disabled={!canSend}>Armer l'envoi</button>
      {/if}
    </div>

    {#if !track.trigs.length}<p class="muted small">Cette track n'a aucun trig dans le pattern.</p>{/if}
    {#if !validChannel}<p class="muted small">Renseigner l'AUTO CHANNEL réglé sur la DT2, pas le numéro de track (mémorisé dans ce navigateur).</p>{/if}
    {#if ports?.error}<p class="err small">{ports.error}</p>{/if}

    {#if send}
      <p class="status {send.status}">
        <b>{STATUS[send.status]}</b>
        {#if !mine}<span class="muted small">(T{String(send.request.track).padStart(2, '0')} {send.role}, pattern {String(send.request.slot).padStart(2, '0')})</span>{/if}
        {#if send.status === 'sending'}<span class="mono">pas {send.step + 1}/{send.steps}</span>{/if}
        {#if send.detail && send.status !== 'sending'}<span class="small">· {send.detail}</span>{/if}
      </p>
      {#if send.warning}<p class="err small">{send.warning}</p>{/if}
      {#if send.status === 'sending'}<progress max={send.steps} value={send.step + 1}></progress>{/if}
    {/if}

    {#if error}<p class="err small">{error}</p>{/if}
    <p class="small muted">Réglages DT2 requis :
      <button class="link small" onclick={() => onhelp('digitakt/kb/midi-config.md')}>fiche Configuration MIDI</button>
      (INPUT / OUTPUT = USB, RECEIVE NOTES, CLOCK SEND, TRANSPORT SEND).</p>
  </div>
</details>

<style>
  .send { border: 1px solid var(--border); border-radius: 4px; padding: 4px 8px; margin: 6px 0; }
  summary { cursor: pointer; font-weight: 600; }
  summary .small { font-weight: normal; }
  .body { display: flex; flex-direction: column; gap: 6px; padding-top: 6px; }
  .howto { margin: 0; padding-left: 1.4em; }
  .row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
  .row label { display: flex; gap: 4px; align-items: center; }
  .row input[type='number'] { width: 4.5em; }
  .row select { max-width: 220px; }
  .status { margin: 0; display: flex; gap: 6px; align-items: baseline; flex-wrap: wrap; }
  .status.sending, .status.waiting { color: var(--accent); }
  .status.error { color: #dc2626; }
  progress { width: 100%; }
  .link { background: none; border: none; padding: 0; color: var(--accent); cursor: pointer; text-decoration: underline; }
  .small { font-size: 12px; }
  .muted { color: var(--muted); }
  .err { color: #dc2626; margin: 0; }
  .mono { font-family: ui-monospace, Menlo, monospace; }
  p { margin: 0; }
</style>
