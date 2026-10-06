<script lang="ts">
  import { tick } from 'svelte'
  import { Marked } from 'marked'
  import { api, normalize, slugify, type KbHit, type KbNote } from './api'

  let open = $state(false)
  let q = $state('')
  let hits = $state<KbHit[]>([])
  let note = $state<KbNote | null>(null)
  let error = $state('')
  let input: HTMLInputElement | undefined = $state()
  let body: HTMLDivElement | undefined = $state()
  let timer: ReturnType<typeof setTimeout> | undefined

  // notes locales du vault : HTML brut echappe, ancres = slugify (meme regle que kb.py),
  // wikilinks Obsidian rendus en texte
  const escapeHtml = (s: string) =>
    s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  const marked = new Marked({
    renderer: {
      html({ text }) { return escapeHtml(text) },
      heading({ tokens, depth, text }) {
        return `<h${depth} id="${slugify(text)}">${this.parser.parseInline(tokens)}</h${depth}>`
      },
    },
  })
  const html = $derived(note
    ? marked.parse(note.markdown.replace(/\[\[([^\]|]+)\|?([^\]]*)\]\]/g,
        (_, target: string, alias: string) => alias || target.split('/').pop() || target),
      { async: false })
    : '')

  function onkey(e: KeyboardEvent) {
    const tag = (e.target as HTMLElement).tagName
    if (e.key === '/' && tag !== 'INPUT' && tag !== 'SELECT' && tag !== 'TEXTAREA') {
      e.preventDefault()
      show()
    } else if (e.key === 'Escape' && open && e.target === input) {
      open = false
    }
  }

  async function show() {
    open = true
    await tick()
    input?.focus()
    input?.select()
  }

  function onInput() {
    clearTimeout(timer)
    timer = setTimeout(async () => {
      if (!q.trim()) { hits = []; return }
      try {
        hits = await api.kbSearch(q)
        error = ''
      } catch (e) {
        error = e instanceof Error ? e.message : String(e)
      }
    }, 150)
  }

  async function openHit(h: KbHit) {
    try {
      if (note?.path !== h.path) note = await api.kbNote(h.path)
      error = ''
      await tick()
      const target = h.anchor ? body?.querySelector(`#${CSS.escape(h.anchor)}`) : null
      if (target) target.scrollIntoView({ block: 'start' })
      else body?.scrollTo({ top: 0 })
    } catch (e) {
      error = e instanceof Error ? e.message : String(e)
    }
  }

  /** Decoupe l'extrait en morceaux surlignes (sans tenir compte des accents). */
  function highlight(text: string): { t: string; on: boolean }[] {
    const terms = normalize(q).split(/\s+/).filter(Boolean)
    const norm = normalize(text)
    const on = new Array(text.length).fill(false)
    for (const term of terms) {
      for (let i = norm.indexOf(term); i >= 0; i = norm.indexOf(term, i + 1)) {
        for (let k = i; k < i + term.length; k++) on[k] = true
      }
    }
    const parts: { t: string; on: boolean }[] = []
    for (let i = 0; i < text.length; i++) {
      const last = parts[parts.length - 1]
      if (last && last.on === on[i]) last.t += text[i]
      else parts.push({ t: text[i], on: on[i] })
    }
    return parts
  }
</script>

<svelte:window onkeydown={onkey} />

{#if !open}
  <button class="toggle small" title="Base de connaissance Digitakt (/)" onclick={show}>KB</button>
{:else}
  <aside class="kb" aria-label="Base de connaissance">
    <header>
      <input bind:this={input} bind:value={q} oninput={onInput} type="search"
        placeholder="Chercher dans la KB et la doctrine…" aria-label="Recherche" />
      <button class="small" onclick={() => (open = false)} title="Fermer (Échap)">×</button>
    </header>
    {#if error}<p class="err">{error}</p>{/if}
    <ul class="hits">
      {#each hits as h (h.path + h.anchor)}
        <li>
          <button class="hit" class:cur={note?.path === h.path} onclick={() => openHit(h)}>
            <span class="where small muted">{h.title}{h.heading ? ' › ' + h.heading : ''}</span>
            <span class="snip small">{#each highlight(h.snippet) as p}{#if p.on}<mark>{p.t}</mark>{:else}{p.t}{/if}{/each}</span>
          </button>
        </li>
      {:else}
        {#if q.trim()}<li class="muted small none">Aucun résultat.</li>{/if}
      {/each}
    </ul>
    {#if note}
      <div class="note" bind:this={body}>
        <p class="path mono small muted">{note.path}</p>
        <!-- eslint-disable-next-line svelte/no-at-html-tags : notes locales, HTML brut echappe -->
        {@html html}
      </div>
    {/if}
  </aside>
{/if}

<style>
  .toggle { position: fixed; right: 16px; bottom: 16px; z-index: 20; font-family: ui-monospace, Menlo, monospace; }
  .kb {
    position: fixed; top: 0; right: 0; bottom: 0; z-index: 20; width: min(440px, 100vw);
    display: flex; flex-direction: column; background: var(--panel);
    border-left: 1px solid var(--border); box-shadow: -8px 0 24px rgb(0 0 0 / 0.15);
  }
  header { display: flex; gap: 6px; padding: 10px; border-bottom: 1px solid var(--border); }
  header input { flex: 1; min-width: 0; }
  .hits { list-style: none; margin: 0; padding: 0; max-height: 38%; overflow-y: auto; border-bottom: 1px solid var(--border); }
  .hit { display: flex; flex-direction: column; gap: 2px; width: 100%; text-align: left; border: 0; border-radius: 0; padding: 6px 10px; background: none; }
  .hit:hover, .hit.cur { background: var(--bg); }
  .snip { line-height: 1.35; }
  mark { background: color-mix(in srgb, var(--accent) 30%, transparent); color: inherit; }
  .none { padding: 8px 10px; }
  .note { flex: 1; overflow-y: auto; padding: 4px 14px 24px; font-size: 13px; line-height: 1.5; }
  .note :global(h1) { font-size: 17px; }
  .note :global(h2) { font-size: 15px; scroll-margin-top: 8px; }
  .note :global(h3) { font-size: 13px; scroll-margin-top: 8px; }
  .note :global(table) { border-collapse: collapse; font-size: 12px; }
  .note :global(td), .note :global(th) { border: 1px solid var(--border); padding: 2px 6px; }
  .note :global(pre) { overflow-x: auto; font-size: 12px; }
  .small { font-size: 12px; }
  .err { color: #dc2626; padding: 0 10px; font-size: 12px; }
</style>
