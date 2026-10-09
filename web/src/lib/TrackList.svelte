<script lang="ts">
  // Liste des morceaux : champ de filtre partage (texte libre, tags en puces,
  // historique des filtres, et en dernier la recherche en ligne pour ajouter
  // un morceau absent), tri par date d'ajout / alpha / BPM / key / energy.
  // Tags = genre + energy + mood (sans le « ? » d'inference) + colonne tags ;
  // plusieurs tags se combinent en ET.
  import type { TrackSummary } from './api'
  import { loadHistory, pushHistory } from './history'

  let { tracks, selected, onselect, ononline }: {
    tracks: TrackSummary[]
    selected: string | null
    onselect: (slug: string) => void
    /** Recherche YouTube / SoundCloud pre-remplie (ajout d'un morceau). */
    ononline: (query: string) => void
  } = $props()

  type Sort = 'alpha' | 'date' | 'bpm' | 'key' | 'energy'
  interface Filter { q: string; tags: string[]; sort: Sort; bank: boolean; stems: boolean }
  type Recall = { q: string; tags: string[] }
  type Sug = { kind: 'tag'; value: string; count: number } | { kind: 'history'; value: Recall } | { kind: 'online'; value: string }

  const FILTER_KEY = 'ui:track-filter'
  const HISTORY_KEY = 'ui:track-history'
  const ENERGY = ['low', 'medium', 'high', 'peak']

  let saved: Partial<Filter> = {}
  try { saved = JSON.parse(localStorage.getItem(FILTER_KEY) ?? '{}') } catch { /* stockage indisponible */ }
  let f = $state<Filter>({ q: '', tags: [], sort: 'alpha', bank: false, stems: false, ...saved })
  $effect(() => {
    const snap = JSON.stringify(f)
    try { localStorage.setItem(FILTER_KEY, snap) } catch { /* stockage indisponible */ }
  })

  let history = $state<Recall[]>(loadHistory<Recall>(HISTORY_KEY))
  let focused = $state(false)
  let suggestIdx = $state(-1)
  let field: HTMLInputElement | undefined = $state()

  const recallTokens = (r: Recall) => [...(r.q.trim() ? [`q:${r.q.trim().toLowerCase()}`] : []), ...r.tags.map(t => `t:${t}`)]
  function remember() {
    history = pushHistory(HISTORY_KEY, history, { q: f.q.trim(), tags: [...f.tags] }, recallTokens)
  }

  const clean = (s: string) => s.trim().replace(/\?+$/, '').trim().toLowerCase()
  function tagsOf(t: TrackSummary): string[] {
    const parts = [t.genre, t.energy, ...t.mood.split(','), ...(t.tags ?? '').split(',')]
    return [...new Set(parts.map(clean).filter(Boolean))]
  }
  const tagMap = $derived(new Map(tracks.map(t => [t.slug, tagsOf(t)])))
  const tagCounts = $derived.by(() => {
    const c = new Map<string, number>()
    for (const ts of tagMap.values()) for (const x of ts) c.set(x, (c.get(x) ?? 0) + 1)
    return c
  })

  const filtered = $derived.by(() => {
    const q = f.q.trim().toLowerCase()
    const list = tracks.filter(t => {
      const ts = tagMap.get(t.slug) ?? []
      return (!q || `${t.artist} ${t.title} ${t.key} ${ts.join(' ')}`.toLowerCase().includes(q))
        && f.tags.every(x => ts.includes(x))
        && (!f.bank || t.has_bank)
        && (!f.stems || t.has_stems)
    })
    const alpha = (a: TrackSummary, b: TrackSummary) => a.artist.localeCompare(b.artist) || a.title.localeCompare(b.title)
    const by: Record<Sort, (a: TrackSummary, b: TrackSummary) => number> = {
      alpha,
      date: (a, b) => (b.added ?? '').localeCompare(a.added ?? '') || alpha(a, b),
      bpm: (a, b) => (parseFloat(a.bpm) || 0) - (parseFloat(b.bpm) || 0),
      key: (a, b) => a.key.localeCompare(b.key),
      energy: (a, b) => ENERGY.indexOf(b.energy) - ENERGY.indexOf(a.energy),
    }
    return [...list].sort(by[f.sort])
  })

  const suggestions = $derived.by((): Sug[] => {
    if (!focused) return []
    const q = f.q.trim().toLowerCase()
    const out: Sug[] = []
    if (q) {
      const tags = [...tagCounts].filter(([t]) => t.includes(q) && !f.tags.includes(t))
        .sort((a, b) => b[1] - a[1]).slice(0, 8)
      for (const [value, count] of tags) out.push({ kind: 'tag', value, count })
    }
    const past = history.filter(r => !q || recallTokens(r).some(t => t.includes(q)))
    for (const r of past.slice(0, q ? 3 : 6)) out.push({ kind: 'history', value: r })
    if (q) out.push({ kind: 'online', value: f.q.trim() })
    return out
  })

  function apply(sg: Sug) {
    if (sg.kind === 'tag') {
      f.tags = [...f.tags, sg.value]
      f.q = ''
      remember()
    } else if (sg.kind === 'history') {
      f.q = sg.value.q
      f.tags = [...sg.value.tags]
      remember()
    } else {
      ononline(sg.value)
      field?.blur()
    }
    suggestIdx = -1
  }

  function dropTag(t: string) {
    f.tags = f.tags.filter(x => x !== t)
  }

  function onkey(e: KeyboardEvent) {
    if (e.key === 'ArrowDown') { suggestIdx = Math.min(suggestIdx + 1, suggestions.length - 1); e.preventDefault() }
    else if (e.key === 'ArrowUp') { suggestIdx = Math.max(suggestIdx - 1, -1); e.preventDefault() }
    else if (e.key === 'Enter') {
      const sg = suggestions[suggestIdx] ?? (suggestions[0]?.kind === 'tag' ? suggestions[0] : undefined)
      if (sg) apply(sg)
      else { remember(); field?.blur() }
      e.preventDefault()
    }
    else if (e.key === 'Escape') { f.q = ''; field?.blur(); e.preventDefault() }
    else if (e.key === 'Backspace' && !f.q && f.tags.length) dropTag(f.tags[f.tags.length - 1])
  }

  function pick(slug: string) {
    remember()  // filtre ayant mene a un morceau : retenu dans l'historique
    onselect(slug)
  }

  /** Morceau voisin du morceau ouvert dans l'ordre affiche (prev / next de la telecommande). */
  export function neighbor(delta: number): string | null {
    const playable = filtered.filter(t => t.has_audio)
    if (!playable.length) return null
    const i = playable.findIndex(t => t.slug === selected)
    if (i < 0) return playable[delta > 0 ? 0 : playable.length - 1].slug
    return playable[i + delta]?.slug ?? null
  }

  /** Focus du champ (raccourci, ouverture de la liste). */
  export function focus() {
    field?.focus()
  }
</script>

<div class="list">
  <div class="filters">
    <div class="search-in">
      {#each f.tags as t (t)}
        <span class="chip">{t}<button class="untag" title="Retirer" onclick={() => dropTag(t)}>×</button></span>
      {/each}
      <input bind:this={field} type="search" bind:value={f.q} onkeydown={onkey}
        oninput={() => (suggestIdx = -1)} onfocus={() => (focused = true)} onblur={() => (focused = false)}
        placeholder={f.tags.length ? 'affiner…' : 'Filtrer : artiste, titre, tag… ou chercher en ligne'} />
      {#if suggestions.length}
        <ul class="suggest">
          {#each suggestions as sg, i (sg.kind + JSON.stringify(sg.value))}
            <li><button class:on={i === suggestIdx} onmousedown={ev => { ev.preventDefault(); apply(sg) }}>
              {#if sg.kind === 'tag'}
                <span class="chip">{sg.value}</span><span class="muted small">tag · {sg.count}</span>
              {:else if sg.kind === 'history'}
                <span class="muted" aria-hidden="true">↺</span>
                {#if sg.value.q}<span>« {sg.value.q} »</span>{/if}
                {#each sg.value.tags as t (t)}<span class="chip">{t}</span>{/each}
              {:else}
                <span class="online">Chercher « {sg.value} » en ligne</span><span class="muted small">YouTube / SoundCloud</span>
              {/if}
            </button></li>
          {/each}
        </ul>
      {/if}
    </div>
    <div class="row">
      <div class="seg small" role="group" aria-label="Tri">
        <button aria-pressed={f.sort === 'date'} onclick={() => (f.sort = 'date')} title="Derniers ajoutés en tête">Date</button>
        <button aria-pressed={f.sort === 'alpha'} onclick={() => (f.sort = 'alpha')} title="Artiste puis titre">A→Z</button>
      </div>
      <select class="small" value={f.sort === 'date' || f.sort === 'alpha' ? '' : f.sort} aria-label="Autre tri"
        onchange={ev => { const v = (ev.target as HTMLSelectElement).value as Sort | ''; if (v) f.sort = v }}>
        <option value="" disabled>trier par…</option>
        <option value="bpm">BPM</option>
        <option value="key">Key</option>
        <option value="energy">Energy</option>
      </select>
      <label class="small"><input type="checkbox" bind:checked={f.stems} /> stems</label>
      <label class="small"><input type="checkbox" bind:checked={f.bank} /> bank</label>
      <span class="muted count">{filtered.length}/{tracks.length}</span>
    </div>
  </div>
  <ul class="tracks">
    {#each filtered as t (t.slug)}
      <li>
        <button class:sel={t.slug === selected} onclick={() => pick(t.slug)} disabled={!t.has_audio}>
          <span class="title">{t.artist} — {t.title}</span>
          <span class="meta mono">
            {t.bpm ? Math.round(parseFloat(t.bpm)) : '?'} · {t.key || '?'}
            {#if t.energy}· {t.energy}{/if}
            {#if f.sort === 'date' && t.added}· {t.added}{/if}
            {#if t.has_stems}<span class="badge">stems</span>{/if}
            {#if t.has_bank}<span class="badge bank">bank</span>{/if}
          </span>
        </button>
      </li>
    {:else}
      {#if f.q.trim()}
        <li class="none">
          <button class="online-btn" onclick={() => ononline(f.q.trim())}>Chercher « {f.q.trim()} » en ligne</button>
        </li>
      {/if}
    {/each}
  </ul>
</div>

<style>
  .list { display: flex; flex-direction: column; height: 100%; min-height: 0; }
  .filters { padding: 10px; display: flex; flex-direction: column; gap: 6px; border-bottom: 1px solid var(--border); }
  .search-in { position: relative; display: flex; flex-wrap: wrap; gap: 4px; align-items: center; border: 1px solid var(--border); border-radius: 4px; padding: 3px 6px; background: var(--panel); }
  .search-in input { flex: 1; min-width: 120px; border: 0; padding: 2px; background: none; outline: none; }
  .suggest { position: absolute; top: 100%; left: 0; right: 0; z-index: 10; list-style: none; margin: 2px 0 0; padding: 2px 0; background: var(--panel); border: 1px solid var(--border); border-radius: 4px; box-shadow: 0 6px 16px rgb(0 0 0 / 0.15); max-height: 320px; overflow-y: auto; }
  .suggest button { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; width: 100%; border: 0; border-radius: 0; background: none; padding: 4px 8px; text-align: left; }
  .suggest button.on, .suggest button:hover { background: var(--panel-2); }
  .chip { display: inline-flex; align-items: center; gap: 2px; font-size: 11px; padding: 1px 7px; border-radius: 9px; border: 1px solid var(--border); white-space: nowrap; }
  .search-in > .chip { padding-right: 2px; border-color: var(--accent); }
  .untag { border: 0; background: none; padding: 0 4px; font-size: 12px; line-height: 1; color: var(--muted); }
  .online { color: var(--accent); }
  .row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .seg { display: inline-flex; }
  .seg button { border-radius: 0; padding: 2px 8px; }
  .seg button:first-child { border-radius: 4px 0 0 4px; }
  .seg button:last-child { border-radius: 0 4px 4px 0; margin-left: -1px; }
  .seg button[aria-pressed='true'] { border-color: var(--accent); color: var(--accent); position: relative; }
  .count { margin-left: auto; font-size: 12px; }
  .tracks { list-style: none; margin: 0; padding: 0; overflow-y: auto; flex: 1; }
  .tracks li button {
    width: 100%; text-align: left; border: 0; border-bottom: 1px solid var(--border);
    border-radius: 0; background: transparent; padding: 6px 10px;
    display: flex; flex-direction: column; gap: 1px;
  }
  .tracks li button:hover { background: var(--panel-2); }
  .tracks li button.sel { background: var(--panel-2); box-shadow: inset 3px 0 0 var(--accent); }
  .tracks li.none { padding: 10px; }
  .tracks li button.online-btn { color: var(--accent); border: 1px dashed var(--accent); border-radius: 4px; }
  .title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .meta { font-size: 12px; color: var(--muted); }
  .badge { margin-left: 6px; font-size: 10px; padding: 0 4px; border: 1px solid var(--border); border-radius: 3px; }
  .badge.bank { border-color: var(--accent); color: var(--accent); }
  .small { font-size: 12px; }
</style>
