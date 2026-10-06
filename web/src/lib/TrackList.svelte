<script lang="ts">
  import type { TrackSummary } from './api'

  let { tracks, selected, onselect }: {
    tracks: TrackSummary[]
    selected: string | null
    onselect: (slug: string) => void
  } = $props()

  let query = $state('')
  let sortKey = $state<'artist' | 'bpm' | 'key' | 'energy' | 'added'>('artist')
  let onlyBank = $state(false)
  let onlyStems = $state(false)

  const ENERGY = ['low', 'medium', 'high', 'peak']

  const filtered = $derived.by(() => {
    const q = query.trim().toLowerCase()
    const list = tracks.filter(t =>
      (!q || `${t.artist} ${t.title} ${t.genre} ${t.key} ${t.mood}`.toLowerCase().includes(q))
      && (!onlyBank || t.has_bank)
      && (!onlyStems || t.has_stems))
    const by: Record<string, (a: TrackSummary, b: TrackSummary) => number> = {
      artist: (a, b) => a.artist.localeCompare(b.artist) || a.title.localeCompare(b.title),
      bpm: (a, b) => (parseFloat(a.bpm) || 0) - (parseFloat(b.bpm) || 0),
      key: (a, b) => a.key.localeCompare(b.key),
      energy: (a, b) => ENERGY.indexOf(b.energy) - ENERGY.indexOf(a.energy),
      added: () => 0,
    }
    return [...list].sort(by[sortKey])
  })
</script>

<div class="list">
  <div class="filters">
    <input type="search" placeholder="Filtrer (artiste, titre, genre, key…)" bind:value={query} />
    <div class="row">
      <select bind:value={sortKey} aria-label="Tri">
        <option value="artist">Artiste</option>
        <option value="bpm">BPM</option>
        <option value="key">Key</option>
        <option value="energy">Energy</option>
        <option value="added">Ordre library</option>
      </select>
      <label><input type="checkbox" bind:checked={onlyStems} /> stems</label>
      <label><input type="checkbox" bind:checked={onlyBank} /> bank</label>
      <span class="muted count">{filtered.length}/{tracks.length}</span>
    </div>
  </div>
  <ul>
    {#each filtered as t (t.slug)}
      <li>
        <button class:sel={t.slug === selected} onclick={() => onselect(t.slug)} disabled={!t.has_audio}>
          <span class="title">{t.artist} — {t.title}</span>
          <span class="meta mono">
            {t.bpm ? Math.round(parseFloat(t.bpm)) : '?'} · {t.key || '?'}
            {#if t.energy}· {t.energy}{/if}
            {#if t.has_stems}<span class="badge">stems</span>{/if}
            {#if t.has_bank}<span class="badge bank">bank</span>{/if}
          </span>
        </button>
      </li>
    {/each}
  </ul>
</div>

<style>
  .list { display: flex; flex-direction: column; height: 100%; min-height: 0; }
  .filters { padding: 10px; display: flex; flex-direction: column; gap: 6px; border-bottom: 1px solid var(--border); }
  .filters input[type="search"] { width: 100%; }
  .row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .count { margin-left: auto; font-size: 12px; }
  ul { list-style: none; margin: 0; padding: 0; overflow-y: auto; flex: 1; }
  li button {
    width: 100%; text-align: left; border: 0; border-bottom: 1px solid var(--border);
    border-radius: 0; background: transparent; padding: 6px 10px;
    display: flex; flex-direction: column; gap: 1px;
  }
  li button:hover { background: var(--panel-2); }
  li button.sel { background: var(--panel-2); box-shadow: inset 3px 0 0 var(--accent); }
  .title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .meta { font-size: 12px; color: var(--muted); }
  .badge { margin-left: 6px; font-size: 10px; padding: 0 4px; border: 1px solid var(--border); border-radius: 3px; }
  .badge.bank { border-color: var(--accent); color: var(--accent); }
</style>
