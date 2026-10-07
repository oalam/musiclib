<script lang="ts">
  // Ecoute des samples DT2 (7.J2) : grille famille x code, puis dans une case
  // les retenus a ecouter (keep / drop au clavier) et la reserve. Un drop fait
  // monter le candidat suivant (selection recalculee par l'API).
  import { onDestroy, onMount } from 'svelte'
  import WaveSurfer from 'wavesurfer.js'
  import { api, type SampleCell, type SampleEntry, type SampleStatus } from './api'

  const FLAG_HELP: Record<string, string> = {
    muet: 'crête sous -40 dBFS',
    faible: 'crête sous -18 dBFS : gain à remonter',
    sature: 'plateaux à pleine échelle (écrêtage)',
    blanc: 'plus de 30 ms de silence en tête : le trig traîne',
    long: 'frappe de plus de 2 s (queue, reverb ou boucle mal rangée)',
    illisible: 'fichier non décodable',
  }
  const CELL_KEY = 'ui:sample-cell'

  let cells = $state<SampleCell[]>([])
  let error = $state('')
  let current = $state<{ family: string; code: string } | null>(null)
  let entries = $state<SampleEntry[]>([])
  let cursor = $state<string | null>(null)    // source du sample en cours
  let showReserve = $state(false)
  let busy = $state(false)
  let autoplay = $state(true)

  let container: HTMLDivElement | undefined = $state()
  let ws: WaveSurfer | null = null

  const families = $derived([...new Set(cells.map(c => c.family))])
  const codes = $derived([...new Set(cells.map(c => c.code))])
  const byKey = $derived(new Map(cells.map(c => [`${c.family}/${c.code}`, c])))
  const chosen = $derived(entries.filter(e => e.selected))
  const reserve = $derived(entries.filter(e => !e.selected))
  // ordre de navigation : la selection, puis la reserve si elle est depliee
  const visible = $derived(showReserve ? [...chosen, ...reserve] : chosen)
  const totals = $derived(cells.reduce((a, c) => ({
    selected: a.selected + c.selected, keep: a.keep + c.keep, toListen: a.toListen + c.to_listen,
  }), { selected: 0, keep: 0, toListen: 0 }))

  function cssVar(name: string): string {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  }

  async function loadCells() {
    try {
      cells = await api.sampleCells()
      error = ''
    } catch (e) {
      error = e instanceof Error ? e.message : String(e)
    }
  }

  async function openCell(family: string, code: string) {
    current = { family, code }
    try { localStorage.setItem(CELL_KEY, `${family}/${code}`) } catch { /* stockage indisponible */ }
    entries = await api.sampleCell(family, code)
    const first = entries.find(e => e.selected && e.status === 'pending') ?? entries.find(e => e.selected)
    pick(first?.source ?? null)
  }

  function pick(source: string | null) {
    cursor = source
    if (!source || !ws) return
    ws.load(api.sampleAudioUrl(source)).catch(() => { /* chargement remplace par le suivant */ })
    document.getElementById(`s-${CSS.escape(source)}`)?.scrollIntoView({ block: 'nearest' })
  }

  function move(delta: number) {
    if (!visible.length) return
    const i = visible.findIndex(e => e.source === cursor)
    const j = i < 0 ? 0 : Math.min(Math.max(i + delta, 0), visible.length - 1)
    pick(visible[j].source)
  }

  function moveCell(delta: number) {
    if (!cells.length) return
    const i = current ? cells.findIndex(c => c.family === current!.family && c.code === current!.code) : -1
    const c = cells[(i + delta + cells.length) % cells.length]
    openCell(c.family, c.code)
  }

  async function decide(status: SampleStatus) {
    if (!cursor || busy) return
    busy = true
    const source = cursor
    try {
      entries = await api.sampleStatus(source, status)
      await loadCells()
      // suivant : prochain retenu encore a ecouter apres celui-ci, sinon le premier
      const pend = entries.filter(e => e.selected && e.status === 'pending')
      const order = entries.map(e => e.source)
      const after = pend.find(e => order.indexOf(e.source) > order.indexOf(source))
      if (status !== 'pending') pick((after ?? pend[0])?.source ?? source)
    } catch (e) {
      error = e instanceof Error ? e.message : String(e)
    } finally {
      busy = false
    }
  }

  function onkey(e: KeyboardEvent) {
    const t = e.target as HTMLElement | null
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return
    if (e.metaKey || e.ctrlKey || e.altKey || document.querySelector('aside.panel, aside.kb')) return
    const k = e.key
    if (k === 'k' || k === 'K') decide('keep')
    else if (k === 'd' || k === 'D') decide('drop')
    else if (k === 'u' || k === 'U') decide('pending')
    else if (k === 'ArrowDown') move(1)
    else if (k === 'ArrowUp') move(-1)
    else if (k === 'ArrowRight') moveCell(1)
    else if (k === 'ArrowLeft') moveCell(-1)
    else if (k === ' ') { ws?.stop(); ws?.play() }
    else if (k === 'r' || k === 'R') showReserve = !showReserve
    else return
    e.preventDefault()
  }

  onMount(async () => {
    if (!container) return
    ws = WaveSurfer.create({
      container,
      height: 80,
      waveColor: cssVar('--wave'),
      progressColor: cssVar('--wave-progress'),
      cursorColor: cssVar('--accent'),
      normalize: true,
    })
    ws.on('ready', () => { if (autoplay) ws?.play() })
    await loadCells()
    let last: string | null = null
    try { last = localStorage.getItem(CELL_KEY) } catch { /* stockage indisponible */ }
    const c = (last && byKey.get(last)) || cells.find(x => x.to_listen > 0) || cells[0]
    if (c) await openCell(c.family, c.code)
  })
  onDestroy(() => ws?.destroy())

  function fmt(d: number | null): string {
    return d == null ? '' : d < 10 ? `${d.toFixed(2)} s` : `${d.toFixed(1)} s`
  }
</script>

<svelte:window onkeydown={onkey} />

<div class="samples">
  <section class="grid">
    <p class="muted small">
      {totals.keep} gardés · {totals.toListen} à écouter sur {totals.selected} retenus.
      Les chiffres d’une case : à écouter / retenus.
    </p>
    {#if error}<p class="err">{error}</p>{/if}
    <table>
      <thead><tr><th></th>{#each codes as code}<th>{code}</th>{/each}</tr></thead>
      <tbody>
        {#each families as fam}
          <tr>
            <th>{fam}</th>
            {#each codes as code}
              {@const c = byKey.get(`${fam}/${code}`)}
              <td>
                {#if c}
                  <button class="cell" class:done={c.to_listen === 0}
                    class:on={current?.family === fam && current?.code === code}
                    title="{fam}/{code} : {c.candidates} candidats, {c.keep} gardés, {c.drop} écartés, {c.flagged} signalés"
                    onclick={() => openCell(fam, code)}>{c.to_listen}/{c.selected}</button>
                {/if}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </section>

  <section class="detail">
    <header>
      <strong>{current ? `${current.family} / ${current.code}` : 'Choisis une case'}</strong>
      {#if current}
        {@const c = byKey.get(`${current.family}/${current.code}`)}
        {#if c}<span class="muted small">quota {c.quota ?? 'tout'} · {c.keep} gardés · {c.drop} écartés · {c.candidates} candidats</span>{/if}
      {/if}
      <label class="small"><input type="checkbox" bind:checked={autoplay} /> lecture auto</label>
    </header>
    <div class="wave" bind:this={container}></div>
    <p class="keys muted small">
      <kbd>K</kbd> garder · <kbd>D</kbd> écarter · <kbd>U</kbd> annuler · <kbd>↑</kbd><kbd>↓</kbd> sample ·
      <kbd>←</kbd><kbd>→</kbd> case · <kbd>Espace</kbd> rejouer · <kbd>R</kbd> réserve
    </p>
    <ol class="list">
      {#each visible as e, i (e.source)}
        {#if showReserve && i === chosen.length}<li class="sep muted small">Réserve ({reserve.length})</li>{/if}
        <li id="s-{e.source}" class="row {e.status}" class:cur={e.source === cursor} class:out={!e.selected}>
          <button class="pick" onclick={() => pick(e.source)}>
            <span class="rank muted">{e.rank}</span>
            <span class="name">{e.name}</span>
            <span class="dur muted small">{fmt(e.duration)}</span>
            {#each e.flags ?? [] as f}<span class="flag" title={FLAG_HELP[f] ?? f}>{f}</span>{/each}
            <span class="src muted small" title={e.source}>{e.source}</span>
          </button>
          <span class="status small">{e.status === 'keep' ? 'gardé' : e.status === 'drop' ? 'écarté' : ''}</span>
        </li>
      {/each}
    </ol>
    {#if current && !showReserve && reserve.length}
      <button class="small" onclick={() => (showReserve = true)}>Afficher la réserve ({reserve.length})</button>
    {/if}
  </section>
</div>

<style>
  .samples { display: grid; grid-template-columns: minmax(0, auto) minmax(0, 1fr); gap: 16px; padding: 12px 16px; height: 100%; min-height: 0; }
  .grid { overflow: auto; }
  table { border-collapse: collapse; font-size: 12px; }
  th { font-weight: 600; padding: 2px 4px; text-align: left; }
  thead th { text-align: center; font-family: ui-monospace, Menlo, monospace; }
  td { padding: 1px; }
  .cell { width: 44px; font: 11px ui-monospace, Menlo, monospace; padding: 3px 0; border: 1px solid var(--border); background: var(--panel); color: var(--text); border-radius: 3px; cursor: pointer; }
  .cell.done { background: var(--cell-off); color: var(--muted); }
  .cell.on { outline: 2px solid var(--accent); }
  .detail { display: flex; flex-direction: column; min-height: 0; min-width: 0; }
  .detail header { display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; }
  .detail header label { margin-left: auto; }
  .wave { margin: 8px 0 4px; border: 1px solid var(--border); border-radius: 4px; background: var(--panel); min-height: 80px; }
  .keys { margin: 4px 0 8px; }
  kbd { font-family: ui-monospace, Menlo, monospace; font-size: 11px; border: 1px solid var(--border); border-radius: 3px; padding: 0 4px; }
  .list { list-style: none; margin: 0; padding: 0; overflow-y: auto; flex: 1; min-height: 0; }
  .row { display: flex; align-items: center; gap: 6px; border-bottom: 1px solid var(--border); }
  .row.cur { background: var(--panel-2); box-shadow: inset 3px 0 0 var(--accent); }
  .row.keep .name { color: var(--rhythm); }
  .row.drop { opacity: 0.5; }
  .row.drop .name { text-decoration: line-through; }
  .row.out:not(.drop) { opacity: 0.75; }
  .pick { flex: 1; min-width: 0; display: flex; gap: 8px; align-items: baseline; background: none; border: 0; padding: 5px 6px; text-align: left; color: var(--text); cursor: pointer; }
  .rank { width: 2.5em; text-align: right; font: 11px ui-monospace, Menlo, monospace; }
  .name { font-family: ui-monospace, Menlo, monospace; white-space: pre; }
  .dur { width: 5em; }
  .flag { font-size: 10px; padding: 0 5px; border-radius: 8px; background: #fde68a; color: #713f12; }
  .src { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; flex: 1; }
  .status { width: 4em; color: var(--muted); }
  .sep { padding: 10px 6px 4px; }
  .small { font-size: 12px; }
  .err { color: #dc2626; font-size: 12px; }
  @media (max-width: 900px) {
    .samples { grid-template-columns: 1fr; height: auto; }
    .list { max-height: 60vh; }
  }
</style>
