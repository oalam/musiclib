<script lang="ts">
  import { api, mmss, type Candidate, type Job } from './api'

  let { onadded }: { onadded: (slug: string, created: boolean) => void } = $props()

  let open = $state(false)
  let query = $state('')
  let searching = $state(false)
  let candidates = $state<Candidate[] | null>(null)
  let picked = $state('')
  let stems = $state(false)
  let bank = $state(false)
  let folder = $state('')
  let job = $state<Job | null>(null)
  let error = $state('')
  let input: HTMLInputElement | undefined = $state()

  const running = $derived(job !== null && (job.status === 'queued' || job.status === 'running'))
  /** Etat lu par la barre du haut. */
  export const busy = () => running

  export function show() {
    open = true
    queueMicrotask(() => input?.focus())
  }

  async function search(e: Event) {
    e.preventDefault()
    if (!query.trim() || searching) return
    searching = true
    error = ''
    candidates = null
    try {
      candidates = await api.grabSearch(query.trim())
      picked = candidates[0]?.url ?? ''  // le meilleur score est preselectionne
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    } finally {
      searching = false
    }
  }

  async function start() {
    if (!picked || running) return
    error = ''
    try {
      job = await api.grab({ url: picked, analyze_quality: true, stems, bank: bank, folder: folder.trim() || null })
      poll(job.id)
    } catch (err) {
      error = err instanceof Error ? err.message : String(err)
    }
  }

  function poll(id: string) {
    const timer = setInterval(async () => {
      try {
        const fresh = await api.job(id)
        job = fresh
        if (fresh.status === 'done' || fresh.status === 'error') {
          clearInterval(timer)
          if (fresh.status === 'done' && fresh.slug) onadded(fresh.slug, !!fresh.created)
        }
      } catch (err) {
        clearInterval(timer)  // api.py redemarre : l'etat du job est perdu
        error = err instanceof Error ? err.message : String(err)
      }
    }, 1000)
  }

  function reset() {
    job = null
    candidates = null
    picked = ''
    query = ''
    error = ''
    queueMicrotask(() => input?.focus())
  }

  const MARK: Record<string, string> = { queued: '·', running: '…', done: '✓', error: '✗', skipped: '–' }
</script>

{#if open}
<aside class="panel" aria-label="Ajouter un morceau">
  <header>
    <strong>Ajouter un morceau</strong>
    <button class="small" onclick={() => (open = false)} title="Fermer (le job continue)">Fermer</button>
  </header>

  <form onsubmit={search}>
    <input bind:this={input} type="search" bind:value={query} disabled={running}
      placeholder="Artiste - titre, ou URL YouTube / SoundCloud" />
    <button type="submit" disabled={searching || running || !query.trim()}>
      {searching ? 'Recherche…' : 'Rechercher'}
    </button>
  </form>
  {#if searching}<p class="muted small">Interrogation de YouTube et SoundCloud (une quinzaine de secondes)…</p>{/if}

  {#if candidates && !job}
    {#if candidates.length === 0}
      <p class="muted">Aucun candidat avec un format audio.</p>
    {:else}
      <ul class="cands">
        {#each candidates as c (c.url)}
          <li>
            <label class:sel={c.url === picked} class:weak={c.match < 0.5}>
              <input type="radio" name="cand" value={c.url} bind:group={picked} />
              <span class="title">{c.title}</span>
              <span class="meta mono">
                {c.source} · {c.codec} {c.abr}k · qualité {c.quality} · pertinence {Math.round(c.match * 100)} %
                {#if c.duration_s}· {mmss(c.duration_s)}{/if}
                {#if c.uploader}· {c.uploader}{/if}
              </span>
              <a href={c.url} target="_blank" rel="noopener noreferrer" class="small">ouvrir</a>
            </label>
          </li>
        {/each}
      </ul>
      <fieldset>
        <label><input type="checkbox" checked disabled /> Analyse complète + visuel</label>
        <label><input type="checkbox" bind:checked={stems} /> Stems Demucs (quelques minutes)</label>
        <label><input type="checkbox" bind:checked={bank} /> Bank Digitakt + harmonie</label>
        <label class="folder" title="Style (ex. shatta, tribe, dub) : range le fichier et corrige le BPM détecté (×2 / ÷2) dans la plage du style">
          Dossier / style <input bind:value={folder} placeholder="déduit du genre" /></label>
      </fieldset>
      <button class="go" onclick={start} disabled={!picked}>Télécharger et analyser</button>
    {/if}
  {/if}

  {#if job}
    <ol class="steps">
      {#each job.steps as s (s.name)}
        <li class={s.status}><span class="mark">{MARK[s.status]}</span> {s.label}
          {#if s.detail}<div class="err small">{s.detail}</div>{/if}
        </li>
      {/each}
    </ol>
    {#if job.status === 'queued'}<p class="muted small">En attente d'un autre ajout (un job à la fois).</p>{/if}
    {#if job.status === 'done'}
      <p>{job.created ? 'Ajouté' : 'Mis à jour'} : <code>{job.slug}</code></p>
    {/if}
    {#if !running}<button onclick={reset}>Nouvel ajout</button>{/if}
  {/if}

  {#if error}<p class="err">{error}</p>{/if}
</aside>
{/if}

<style>
  .panel {
    position: fixed; top: 0; right: 0; bottom: 0; z-index: 20; width: min(520px, 100vw);
    background: var(--panel); border-left: 1px solid var(--border); box-shadow: -4px 0 16px rgb(0 0 0 / 0.15);
    padding: 12px 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px;
  }
  header { display: flex; align-items: center; justify-content: space-between; }
  form { display: flex; gap: 6px; }
  form input { flex: 1; min-width: 0; }
  .cands { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px; }
  .cands label {
    display: grid; grid-template-columns: auto 1fr auto; column-gap: 8px; align-items: baseline;
    padding: 6px 8px; border: 1px solid var(--border); border-radius: 4px; cursor: pointer;
  }
  .cands label.sel { border-color: var(--accent); box-shadow: inset 3px 0 0 var(--accent); }
  .cands label.weak .title { color: var(--muted); }
  .cands .meta { grid-column: 2 / 4; font-size: 11px; color: var(--muted); }
  .cands a { grid-row: 1; grid-column: 3; }
  .title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  fieldset { border: 1px solid var(--border); border-radius: 4px; display: flex; flex-direction: column; gap: 4px; padding: 8px; margin: 0; }
  .folder { display: flex; gap: 6px; align-items: center; }
  .go { align-self: flex-start; }
  .steps { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 3px; }
  .steps .mark { display: inline-block; width: 1.2em; font-family: ui-monospace, Menlo, monospace; }
  .steps .running { color: var(--accent); font-weight: 600; }
  .steps .skipped, .steps .queued { color: var(--muted); }
  .steps .error { color: #dc2626; }
  .small { font-size: 12px; }
  .err { color: #dc2626; }
  .mono { font-family: ui-monospace, Menlo, monospace; }
</style>
