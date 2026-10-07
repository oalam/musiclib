<script lang="ts">
  // Bibliotheque des samples DT2 (7.J2, 7.J4) : grille famille x code, puis
  // une liste (case, non classes ou corbeille). Dans une case : les retenus a
  // ecouter (keep / drop au clavier) et la reserve ; un drop fait monter le
  // candidat suivant (selection recalculee par l'API). Selection multiple
  // (Cmd, Maj), barre d'outils, glisser-deposer vers une case ou la corbeille.
  import { onDestroy, onMount } from 'svelte'
  import WaveSurfer from 'wavesurfer.js'
  import { api, type LooseSample, type SampleCell, type SampleEntry, type SampleStatus } from './api'

  const FLAG_HELP: Record<string, string> = {
    muet: 'crête sous -40 dBFS',
    faible: 'crête sous -18 dBFS : gain à remonter',
    sature: 'plateaux à pleine échelle (écrêtage)',
    blanc: 'plus de 30 ms de silence en tête : le trig traîne',
    long: 'frappe de plus de 2 s (queue, reverb ou boucle mal rangée)',
    illisible: 'fichier non décodable',
  }
  const VIEW_KEY = 'ui:sample-cell'
  // colonnes : one-shots puis boucles en dernier (memes codes qu'analyzer/samples.py)
  const LOOPS = ['BR', 'DL', 'PL', 'ML', 'BL']
  const ONESHOTS = ['BD', 'SD', 'CP', 'RS', 'HH', 'OH', 'CY', 'TM', 'PC', 'BS', 'ST', 'PD', 'FX', 'VX']
  const CODE_ORDER = [...ONESHOTS, ...LOOPS]
  const FAMILIES = ['HARDCORE', 'JUNGLE', 'TRIBE', 'TECHNO', 'DUBSTEP', 'AUTRES', 'UNIVERSEL', 'SAMPLE']
  const codeRank = (c: string) => (CODE_ORDER.includes(c) ? CODE_ORDER.indexOf(c) : CODE_ORDER.length)

  type Loose = 'unclassified' | 'trash'
  type View = { kind: 'cell'; family: string; code: string } | { kind: Loose }

  let cells = $state<SampleCell[]>([])
  let counts = $state({ unclassified: 0, trash: 0 })
  let allTags = $state<string[]>([])
  let error = $state('')
  let view = $state<View | null>(null)
  let entries = $state<SampleEntry[]>([])
  let cursor = $state<string | null>(null)    // source du sample en cours
  let sel = $state<Set<string>>(new Set())    // selection multiple (Cmd / Maj)
  let anchor: string | null = null            // origine d'une plage Maj-clic
  let showReserve = $state(false)
  let busy = $state(false)
  let autoplay = $state(true)
  // filtres (grille et liste) : tag exact, etoiles minimum
  let filterTag = $state('')
  let minStars = $state(0)
  let tagInput = $state('')
  let tagField: HTMLInputElement | undefined = $state()
  // changement de case (M) : statut garde, rang en fin de case
  let moving = $state<{ sources: string[]; label: string; family: string; code: string } | null>(null)
  let moveSelect: HTMLSelectElement | undefined = $state()
  // glisser-deposer : sources tirees, cible survolee ("FAM/CODE" ou "trash")
  let dragging = $state<string[] | null>(null)
  let dropKey = $state<string | null>(null)

  let container: HTMLDivElement | undefined = $state()
  let ws: WaveSurfer | null = null

  const current = $derived(view?.kind === 'cell' ? view : null)
  // toutes les familles, meme vides (TRIBE attend son pack) : cibles de rangement
  const families = $derived([...FAMILIES, ...new Set(cells.map(c => c.family).filter(f => !FAMILIES.includes(f)))])
  const codes = $derived([...new Set(cells.map(c => c.code))].sort((a, b) => codeRank(a) - codeRank(b)))
  const byKey = $derived(new Map(cells.map(c => [`${c.family}/${c.code}`, c])))
  const shown = $derived(entries.filter(matches))
  const chosen = $derived(shown.filter(e => e.selected))
  const reserve = $derived(shown.filter(e => !e.selected))
  // ordre de navigation : la selection, puis la reserve si elle est depliee
  const visible = $derived(showReserve ? [...chosen, ...reserve] : chosen)
  const totals = $derived(cells.reduce((a, c) => ({
    selected: a.selected + c.selected, keep: a.keep + c.keep, toListen: a.toListen + c.to_listen,
  }), { selected: 0, keep: 0, toListen: 0 }))
  const targetCount = $derived(sel.size || (cursor ? 1 : 0))

  function filterOn(): boolean { return filterTag !== '' || minStars > 0 }

  function matches(e: SampleEntry): boolean {
    return (!filterTag || e.tags.includes(filterTag)) && (e.stars ?? 0) >= minStars
  }

  function cssVar(name: string): string {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  }

  function fail(e: unknown) {
    error = e instanceof Error ? e.message : String(e)
  }

  function looseRow(l: LooseSample, i: number): SampleEntry {
    const name = (l.source.split('/').pop() ?? l.source).replace(/\.wav$/i, '')
    return { source: l.source, family: '', code: '', pack: l.pack, name, duration: null, rank: i + 1,
      status: 'pending', selected: true, flags: null, bpm: null, bpm_est: false, tags: l.tags, stars: l.stars }
  }

  // grille (filtree), compteurs hors case et tags connus
  async function refresh() {
    try {
      const [c, u, t, tags] = await Promise.all([
        api.sampleCells({ tag: filterTag || undefined, minStars: minStars || undefined }),
        api.sampleLoose('unclassified'), api.sampleLoose('trash'), api.sampleTags(),
      ])
      cells = c
      counts = { unclassified: u.length, trash: t.length }
      allTags = tags
      error = ''
    } catch (e) {
      fail(e)
    }
  }

  async function loadEntries() {
    const v = view
    if (!v) { entries = []; return }
    // une case videe (tout deplace) n'existe plus : liste vide
    entries = v.kind === 'cell'
      ? await api.sampleCell(v.family, v.code).catch(() => [])
      : (await api.sampleLoose(v.kind)).map(looseRow)
  }

  async function open(v: View) {
    view = v
    sel = new Set()
    moving = null
    const key = v.kind === 'cell' ? `${v.family}/${v.code}` : `:${v.kind}`
    try { localStorage.setItem(VIEW_KEY, key) } catch { /* stockage indisponible */ }
    await loadEntries()
    const first = visible.find(e => e.status === 'pending') ?? visible[0]
    pick(first?.source ?? null)
  }

  function pick(source: string | null) {
    cursor = source
    if (!source || !ws) return
    ws.load(api.sampleAudioUrl(source)).catch(() => { /* chargement remplace par le suivant */ })
    document.getElementById(`s-${CSS.escape(source)}`)?.scrollIntoView({ block: 'nearest' })
  }

  function step(delta: number) {
    if (!visible.length) return
    const i = visible.findIndex(e => e.source === cursor)
    const j = i < 0 ? 0 : Math.min(Math.max(i + delta, 0), visible.length - 1)
    pick(visible[j].source)
  }

  const ordered = $derived(families.flatMap(f => codes.map(c => byKey.get(`${f}/${c}`)).filter((c): c is SampleCell => c !== undefined)))

  function stepCell(delta: number) {
    if (!ordered.length) return
    const i = current ? ordered.findIndex(c => c.family === current.family && c.code === current.code) : -1
    const c = ordered[(i + delta + ordered.length) % ordered.length]
    open({ kind: 'cell', family: c.family, code: c.code })
  }

  function targets(): string[] {
    return sel.size ? [...sel] : cursor ? [cursor] : []
  }

  /** Action par lot : sur la selection, sinon le sample en cours. Le curseur
   *  reste s'il est encore dans la liste, sinon passe au suivant. */
  async function act(fn: (sources: string[]) => Promise<unknown>, sources: string[] = targets()): Promise<boolean> {
    if (!sources.length || busy) return false
    busy = true
    const before = visible.map(e => e.source)
    try {
      await fn(sources)
      sel = new Set()
      await Promise.all([refresh(), loadEntries()])
      if (!visible.some(e => e.source === cursor)) {
        const i = before.indexOf(cursor ?? '')
        const next = before.slice(i + 1).find(s => visible.some(e => e.source === s))
        pick(next ?? visible[0]?.source ?? null)
      }
      return true
    } catch (e) {
      fail(e)
      return false
    } finally {
      busy = false
    }
  }

  async function decide(status: SampleStatus) {
    if (!current) return
    const single = sel.size ? null : cursor
    if (!(await act(s => api.sampleStatus(s, status))) || !single || status === 'pending') return
    // ecoute : prochain retenu encore a ecouter apres celui-ci, sinon le premier
    const pend = entries.filter(e => e.selected && e.status === 'pending')
    const order = entries.map(e => e.source)
    const after = pend.find(e => order.indexOf(e.source) > order.indexOf(single))
    pick((after ?? pend[0])?.source ?? single)
  }

  const stars = (n: number | null) => act(s => api.sampleStars(s, n))
  const toTrash = (sources?: string[]) => act(api.sampleTrash, sources)
  const restore = () => act(api.sampleRestore)

  async function addTag() {
    const t = tagInput.trim()
    if (!t) return
    if (await act(s => api.sampleTagsEdit(s, [t]))) tagInput = ''
    tagField?.blur()
  }

  function startMove() {
    const sources = targets()
    if (!sources.length || view?.kind === 'trash') return
    const one = entries.find(e => e.source === sources[0])
    moving = {
      sources,
      label: sources.length > 1 ? `${sources.length} samples` : one?.name ?? sources[0],
      family: current?.family ?? 'UNIVERSEL',
      code: current?.code ?? 'PC',
    }
    queueMicrotask(() => moveSelect?.focus())
  }

  async function confirmMove() {
    if (!moving) return
    const m = moving
    if (current && m.family === current.family && m.code === current.code) { moving = null; return }
    if (await act(s => api.sampleMove(s, m.family, m.code), m.sources)) moving = null
  }

  function onMoveKey(e: KeyboardEvent) {
    if (e.key === 'Enter') { e.preventDefault(); confirmMove() }
    else if (e.key === 'Escape') { e.preventDefault(); moving = null }
  }

  function onTagKey(e: KeyboardEvent) {
    if (e.key === 'Enter') { e.preventDefault(); addTag() }
    else if (e.key === 'Escape') { e.preventDefault(); tagField?.blur() }
  }

  // clic : ecouter ; Cmd-clic : ajouter / retirer de la selection ; Maj-clic : plage
  function onRowClick(ev: MouseEvent, source: string) {
    if (ev.metaKey || ev.ctrlKey) {
      const s = new Set(sel)
      if (!s.size && cursor && cursor !== source) s.add(cursor)
      if (s.has(source)) s.delete(source)
      else s.add(source)
      sel = s
      anchor = source
      return
    }
    const from = anchor ?? cursor
    if (ev.shiftKey && from) {
      const order = visible.map(e => e.source)
      const [a, b] = [order.indexOf(from), order.indexOf(source)].sort((x, y) => x - y)
      if (a >= 0) sel = new Set([...sel, ...order.slice(a, b + 1)])
      return
    }
    sel = new Set()
    anchor = source
    pick(source)
  }

  function onDragStart(ev: DragEvent, source: string) {
    const sources = sel.has(source) ? [...sel] : [source]
    ev.dataTransfer?.setData('text/plain', sources.join('\n'))
    if (ev.dataTransfer) ev.dataTransfer.effectAllowed = 'move'
    dragging = sources
  }

  function onDragEnd() {
    dragging = null
    dropKey = null
  }

  function onDragOver(ev: DragEvent, key: string) {
    if (!dragging) return
    ev.preventDefault()
    dropKey = key
  }

  function onDrop(ev: DragEvent, target: { family: string; code: string } | 'trash') {
    ev.preventDefault()
    const sources = dragging
    onDragEnd()
    if (!sources) return
    if (target === 'trash') toTrash(sources)
    else act(s => api.sampleMove(s, target.family, target.code), sources)
  }

  async function setFilter() {
    await refresh()
    if (!visible.some(e => e.source === cursor)) pick(visible[0]?.source ?? null)
  }

  function onkey(e: KeyboardEvent) {
    const t = e.target as HTMLElement | null
    if (moving) return
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable)) return
    if (document.querySelector('aside.panel, aside.kb')) return
    const k = e.key
    if ((e.metaKey || e.ctrlKey) && (k === 'a' || k === 'A')) { sel = new Set(visible.map(x => x.source)); e.preventDefault(); return }
    if (e.metaKey || e.ctrlKey || e.altKey) return
    const trashView = view?.kind === 'trash'
    if (k === 'k' || k === 'K') decide('keep')
    else if (k === 'd' || k === 'D') decide('drop')
    else if (k === 'u' || k === 'U') { if (trashView) restore(); else decide('pending') }
    else if (k === 'ArrowDown') step(1)
    else if (k === 'ArrowUp') step(-1)
    else if (k === 'ArrowRight') stepCell(1)
    else if (k === 'ArrowLeft') stepCell(-1)
    else if (k === ' ') { ws?.stop(); ws?.play() }
    else if (k === 'r' || k === 'R') showReserve = !showReserve
    else if (k === 'm' || k === 'M') startMove()
    else if (k === 't' || k === 'T') tagField?.focus()
    else if (k >= '0' && k <= '5') stars(k === '0' ? null : Number(k))
    else if ((k === 'Delete' || k === 'Backspace') && !trashView) toTrash()
    else if (k === 'Escape') sel = new Set()
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
    await refresh()
    let last: string | null = null
    try { last = localStorage.getItem(VIEW_KEY) } catch { /* stockage indisponible */ }
    if (last === ':unclassified' || last === ':trash') return open({ kind: last.slice(1) as Loose })
    const c = (last && byKey.get(last)) || cells.find(x => x.to_listen > 0) || cells[0]
    if (c) await open({ kind: 'cell', family: c.family, code: c.code })
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
      Les chiffres d’une case : à écouter / retenus{filterOn() ? ' (filtrés)' : ''}.
    </p>
    <div class="filters small">
      <label>tag
        <select bind:value={filterTag} onchange={setFilter}>
          <option value="">tous</option>
          {#each allTags as t}<option value={t}>{t}</option>{/each}
        </select>
      </label>
      <label>étoiles
        <select bind:value={minStars} onchange={setFilter}>
          <option value={0}>toutes</option>
          {#each [1, 2, 3, 4, 5] as n}<option value={n}>{'★'.repeat(n)}{n < 5 ? ' et +' : ''}</option>{/each}
        </select>
      </label>
    </div>
    {#if error}<p class="err">{error}</p>{/if}
    <table class:dragging={dragging !== null}>
      <thead><tr><th></th>{#each codes as code}<th class:loop={LOOPS.includes(code)} class:first={code === LOOPS.find(l => codes.includes(l))}>{code}</th>{/each}</tr></thead>
      <tbody>
        {#each families as fam}
          <tr>
            <th class:empty={!cells.some(c => c.family === fam)}
              title={cells.some(c => c.family === fam) ? '' : 'aucun sample : glisse-en un ici ou M'}>{fam}</th>
            {#each codes as code}
              {@const c = byKey.get(`${fam}/${code}`)}
              {@const key = `${fam}/${code}`}
              <!-- svelte-ignore a11y_no_static_element_interactions -->
              <td class:first={code === LOOPS.find(l => codes.includes(l))} class:over={dropKey === key}
                ondragover={e => onDragOver(e, key)} ondragleave={() => { if (dropKey === key) dropKey = null }}
                ondrop={e => onDrop(e, { family: fam, code })}>
                {#if c}
                  <button class="cell" class:done={c.to_listen === 0}
                    class:on={current?.family === fam && current?.code === code}
                    title="{fam}/{code} : {c.candidates} candidats, {c.keep} gardés, {c.drop} écartés, {c.flagged} signalés"
                    onclick={() => open({ kind: 'cell', family: fam, code })}>{c.to_listen}/{c.selected}</button>
                {:else}
                  <span class="slot" title="{fam}/{code}"></span>
                {/if}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
    <div class="loose">
      <button class="small" aria-pressed={view?.kind === 'unclassified'}
        title="Fichiers sans code : glisse-les vers une case (ou M)"
        onclick={() => open({ kind: 'unclassified' })}>Non classés ({counts.unclassified})</button>
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <span class="trash-drop" class:over={dropKey === 'trash'}
        ondragover={e => onDragOver(e, 'trash')} ondragleave={() => { if (dropKey === 'trash') dropKey = null }}
        ondrop={e => onDrop(e, 'trash')}>
        <button class="small" aria-pressed={view?.kind === 'trash'}
          title="Sons rejetés partout, restaurables, jamais supprimés du disque"
          onclick={() => open({ kind: 'trash' })}>Corbeille ({counts.trash})</button>
      </span>
    </div>
  </section>

  <section class="detail">
    <header>
      <strong>{current ? `${current.family} / ${current.code}` : view?.kind === 'unclassified' ? 'Non classés' : view?.kind === 'trash' ? 'Corbeille' : 'Choisis une case'}</strong>
      {#if current}
        {@const c = byKey.get(`${current.family}/${current.code}`)}
        {#if c}<span class="muted small">quota {c.quota ?? 'tout'} · {c.keep} gardés · {c.drop} écartés · {c.candidates} candidats</span>{/if}
      {:else if view}
        <span class="muted small">{shown.length} fichiers</span>
      {/if}
      <label class="small"><input type="checkbox" bind:checked={autoplay} /> lecture auto</label>
    </header>
    <div class="wave" bind:this={container}></div>
    <div class="toolbar small">
      <span class="count">{sel.size ? `${sel.size} sélectionnés` : cursor ? 'sample en cours' : 'rien'}</span>
      {#if view?.kind === 'trash'}
        <button class="small" disabled={!targetCount || busy} onclick={restore}>Restaurer</button>
      {:else}
        {#if current}
          <button class="small" disabled={!targetCount || busy} onclick={() => decide('keep')}>Garder</button>
          <button class="small" disabled={!targetCount || busy} onclick={() => decide('drop')}>Écarter</button>
        {/if}
        <button class="small" disabled={!targetCount || busy} onclick={startMove}>Case…</button>
        <button class="small" disabled={!targetCount || busy} onclick={() => toTrash()}>Corbeille</button>
      {/if}
      <span class="stars-bar">
        {#each [1, 2, 3, 4, 5] as n}<button class="star" disabled={!targetCount || busy} title="{n} étoile{n > 1 ? 's' : ''} ({n})" onclick={() => stars(n)}>{'★'.repeat(n)}</button>{/each}
        <button class="star" disabled={!targetCount || busy} title="Retirer la note (0)" onclick={() => stars(null)}>×</button>
      </span>
      <input class="tag-in" list="sample-tags" placeholder="tag (T)" bind:this={tagField} bind:value={tagInput}
        onkeydown={onTagKey} disabled={!targetCount} />
      <datalist id="sample-tags">{#each allTags as t}<option value={t}></option>{/each}</datalist>
      <button class="small" disabled={!targetCount || !tagInput.trim() || busy} onclick={addTag}>Tagger</button>
    </div>
    <p class="keys muted small">
      {#if current}<kbd>K</kbd> garder · <kbd>D</kbd> écarter · <kbd>U</kbd> annuler · {/if}
      {#if view?.kind === 'trash'}<kbd>U</kbd> restaurer · {:else}<kbd>Suppr</kbd> corbeille · <kbd>M</kbd> case · {/if}
      <kbd>1</kbd>…<kbd>5</kbd> étoiles, <kbd>0</kbd> sans · <kbd>T</kbd> tag ·
      <kbd>↑</kbd><kbd>↓</kbd> sample · <kbd>←</kbd><kbd>→</kbd> case · <kbd>Espace</kbd> rejouer · <kbd>R</kbd> réserve ·
      <kbd>⌘</kbd>/<kbd>Maj</kbd>-clic sélection, <kbd>⌘A</kbd> tout, <kbd>Échap</kbd> aucun · glisser vers une case ou la corbeille
    </p>
    {#if moving}
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div class="move" onkeydown={onMoveKey}>
        <span class="small">Ranger <span class="name">{moving.label}</span> dans</span>
        <select bind:this={moveSelect} bind:value={moving.family}>
          {#each FAMILIES as f}<option value={f}>{f}</option>{/each}
        </select>
        <select bind:value={moving.code}>
          {#each CODE_ORDER as c}<option value={c}>{c}{LOOPS.includes(c) ? ' (boucle)' : ''}</option>{/each}
        </select>
        <button class="small" onclick={confirmMove} disabled={busy}>Ranger</button>
        <button class="small" onclick={() => (moving = null)}>Annuler</button>
        <span class="muted small">statut gardé, rangé en fin de case · <kbd>Entrée</kbd> / <kbd>Échap</kbd></span>
      </div>
    {/if}
    <ol class="list">
      {#each visible as e, i (e.source)}
        {#if showReserve && i === chosen.length && reserve.length}<li class="sep muted small">Réserve ({reserve.length})</li>{/if}
        <li id="s-{e.source}" class="row {e.status}" class:cur={e.source === cursor} class:out={!e.selected}
          class:sel={sel.has(e.source)} draggable={view?.kind !== 'trash'}
          ondragstart={ev => onDragStart(ev, e.source)} ondragend={onDragEnd}>
          <button class="pick" onclick={ev => onRowClick(ev, e.source)}>
            {#if current}<span class="rank muted">{e.rank}</span>{/if}
            <span class="name">{e.name}</span>
            {#if e.stars}<span class="stars" title="{e.stars} étoile{e.stars > 1 ? 's' : ''}">{'★'.repeat(e.stars)}</span>{/if}
            <span class="dur muted small">{fmt(e.duration)}</span>
            {#if e.bpm_est}<span class="est" title="tempo estimé par l’audio, non confirmé par la durée">~{e.bpm} bpm</span>{/if}
            {#each e.flags ?? [] as f}<span class="flag" title={FLAG_HELP[f] ?? f}>{f}</span>{/each}
            <span class="src muted small" title={e.source}>{e.source}</span>
          </button>
          {#each e.tags as t}
            <span class="tag small">{t}<button class="untag" title="Retirer le tag {t}"
              onclick={() => act(s => api.sampleTagsEdit(s, [], [t]), [e.source])}>×</button></span>
          {/each}
          <span class="status small">{e.status === 'keep' ? 'gardé' : e.status === 'drop' ? 'écarté' : ''}</span>
        </li>
      {/each}
    </ol>
    {#if current && !showReserve && reserve.length}
      <button class="small" onclick={() => (showReserve = true)}>Afficher la réserve ({reserve.length})</button>
    {/if}
    {#if view && !visible.length}<p class="muted small">{filterOn() ? 'Aucun sample ne répond au filtre.' : 'Liste vide.'}</p>{/if}
  </section>
</div>

<style>
  .samples { display: grid; grid-template-columns: minmax(0, auto) minmax(0, 1fr); gap: 16px; padding: 12px 16px; height: 100%; min-height: 0; }
  .grid { overflow: auto; }
  .filters { display: flex; gap: 10px; margin: 0 0 6px; }
  table { border-collapse: collapse; font-size: 12px; }
  th { font-weight: 600; padding: 2px 4px; text-align: left; }
  thead th { text-align: center; font-family: ui-monospace, Menlo, monospace; }
  td { padding: 1px; }
  th.empty { color: var(--muted); font-weight: 400; }
  th.loop { color: var(--melodic); }
  .first { border-left: 2px solid var(--border); padding-left: 6px; }
  .cell { width: 44px; font: 11px ui-monospace, Menlo, monospace; padding: 3px 0; border: 1px solid var(--border); background: var(--panel); color: var(--text); border-radius: 3px; cursor: pointer; }
  .cell.done { background: var(--cell-off); color: var(--muted); }
  .cell.on { outline: 2px solid var(--accent); }
  .slot { display: block; width: 44px; height: 21px; border-radius: 3px; }
  table.dragging .slot { border: 1px dashed var(--border); }
  td.over .cell, td.over .slot { outline: 2px dashed var(--accent); background: var(--panel-2); }
  .loose { display: flex; gap: 8px; margin-top: 10px; }
  .trash-drop { border-radius: 4px; }
  .trash-drop.over { outline: 2px dashed #dc2626; }
  .detail { display: flex; flex-direction: column; min-height: 0; min-width: 0; }
  .detail header { display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; }
  .detail header label { margin-left: auto; }
  .wave { margin: 8px 0 4px; border: 1px solid var(--border); border-radius: 4px; background: var(--panel); min-height: 80px; }
  .toolbar { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin: 4px 0; }
  .toolbar .count { min-width: 9em; color: var(--muted); }
  .stars-bar { display: inline-flex; gap: 2px; }
  .star { font-size: 11px; padding: 1px 4px; color: #b45309; }
  .tag-in { width: 9em; font-size: 12px; }
  .keys { margin: 4px 0 8px; }
  kbd { font-family: ui-monospace, Menlo, monospace; font-size: 11px; border: 1px solid var(--border); border-radius: 3px; padding: 0 4px; }
  .list { list-style: none; margin: 0; padding: 0; overflow-y: auto; flex: 1; min-height: 0; }
  .row { display: flex; align-items: center; gap: 6px; border-bottom: 1px solid var(--border); user-select: none; }
  .row.cur { background: var(--panel-2); box-shadow: inset 3px 0 0 var(--accent); }
  .row.sel { background: color-mix(in srgb, var(--accent) 18%, transparent); }
  .row.keep .name { color: var(--rhythm); }
  .row.drop { opacity: 0.5; }
  .row.drop .name { text-decoration: line-through; }
  .row.out:not(.drop) { opacity: 0.75; }
  .pick { flex: 1; min-width: 0; display: flex; gap: 8px; align-items: baseline; background: none; border: 0; padding: 5px 6px; text-align: left; color: var(--text); cursor: pointer; }
  .rank { width: 2.5em; text-align: right; font: 11px ui-monospace, Menlo, monospace; }
  .name { font-family: ui-monospace, Menlo, monospace; white-space: pre; }
  .stars { color: #b45309; font-size: 11px; }
  .dur { width: 5em; }
  .est { font-size: 10px; padding: 0 5px; border-radius: 8px; border: 1px dashed var(--muted); color: var(--muted); }
  .flag { font-size: 10px; padding: 0 5px; border-radius: 8px; background: #fde68a; color: #713f12; }
  .tag { display: inline-flex; align-items: center; gap: 2px; font-size: 10px; padding: 0 2px 0 6px; border-radius: 8px; border: 1px solid var(--border); color: var(--muted); white-space: nowrap; }
  .untag { border: 0; background: none; color: var(--muted); padding: 0 3px; cursor: pointer; font-size: 10px; }
  .src { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; flex: 1; }
  .status { width: 4em; color: var(--muted); }
  .move { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; padding: 6px 8px; margin-bottom: 6px; border: 1px solid var(--accent); border-radius: 4px; background: var(--panel); }
  .sep { padding: 10px 6px 4px; }
  .small { font-size: 12px; }
  .err { color: #dc2626; font-size: 12px; }
  @media (max-width: 900px) {
    .samples { grid-template-columns: 1fr; height: auto; }
    .list { max-height: 60vh; }
  }
</style>
