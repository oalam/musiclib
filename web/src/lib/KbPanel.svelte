<script lang="ts">
  import { tick } from 'svelte'
  import { Marked } from 'marked'
  import { api, manualUrl, normalize, slugify, type KbHit, type KbLot, type KbNote } from './api'

  let open = $state(false)
  // sommaire par lot, fiche, ou manuel PDF (7.F)
  let view = $state<'toc' | 'note' | 'manual'>('toc')
  let toc = $state<KbLot[]>([])
  let manualPage = $state(1)
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
      // liens externes (videos des fiches) : nouvel onglet, sinon l'app est remplacee
      link({ href, title, tokens }) {
        const ext = /^https?:\/\//.test(href)
        return `<a href="${escapeHtml(href)}"${title ? ` title="${escapeHtml(title)}"` : ''}${ext ? ' target="_blank" rel="noopener"' : ''}>${this.parser.parseInline(tokens)}</a>`
      },
      heading({ tokens, depth, text }) {
        return `<h${depth} id="${slugify(text)}">${this.parser.parseInline(tokens)}</h${depth}>`
      },
    },
  })
  const DOCTRINE = 'digitakt/doctrine.md'
  const known = $derived(new Set([DOCTRINE, ...toc.flatMap(l => l.notes.map(n => n.path))]))

  /** Wikilink Obsidian -> lien interne vers la fiche si elle est dans le corpus, texte sinon. */
  function wikilink(target: string, alias: string): string {
    const base = target.split('#')[0].split('/').pop() ?? target
    const path = base === 'doctrine' ? DOCTRINE : `digitakt/kb/${base}.md`
    const label = alias || base
    return known.has(path) ? `[${label}](#kb:${path})` : label
  }
  const html = $derived(note
    ? marked.parse(note.markdown.replace(/\[\[([^\]|]+)\|?([^\]]*)\]\]/g,
        (_, target: string, alias: string) => wikilink(target, alias)),
      { async: false })
    : '')

  // les § cites dans le texte deviennent des liens vers la page du manuel
  $effect(() => {
    void html
    const index = note?.manual_index ?? {}
    const inDoctrine = note?.path === DOCTRINE
    if (!body) return
    const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT, {
      acceptNode: n => (n.parentElement?.closest('a, code, pre, button') ? NodeFilter.FILTER_REJECT
        : /§\d/.test(n.nodeValue ?? '') ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP),
    })
    const nodes: Text[] = []
    while (walker.nextNode()) nodes.push(walker.currentNode as Text)
    for (const node of nodes) {
      const frag = document.createDocumentFragment()
      let last = 0
      const text = node.nodeValue ?? ''
      // « [[../doctrine]] §1 » : le mot doctrine est dans le lien qui precede
      const before = node.previousSibling?.textContent ?? ''
      for (const m of text.matchAll(/§(\d+(?:\.\d+)*)/g)) {
        // meme regle que kb.is_doctrine_ref : « doctrine §3 » vise la doctrine
        const doctrine = (inDoctrine && !m[1].includes('.'))
          || /doctrine\]*\s*\(?\s*$/i.test((before + text.slice(0, m.index)).slice(-30))
        const ref = doctrine ? null : index[m[1]]
        if (!doctrine && !ref) continue
        frag.append(text.slice(last, m.index))
        const a = document.createElement('a')
        if (ref) {
          a.href = manualUrl(ref.page)
          a.className = 'man'
          a.dataset.page = String(ref.page)
          a.title = `Manuel : ${ref.title} · p${ref.page}`
        } else {
          a.href = `#kb:${DOCTRINE}#${m[1]}-`
          a.title = `Doctrine, section ${m[1]}`
        }
        a.textContent = m[0]
        frag.append(a)
        last = m.index + m[0].length
      }
      if (last === 0) continue
      frag.append(text.slice(last))
      node.replaceWith(frag)
    }
  })

  /** Clics dans la fiche : § -> manuel, wikilink -> autre fiche. */
  function onNoteClick(e: MouseEvent) {
    const a = (e.target as HTMLElement).closest('a')
    if (!a) return
    if (a.classList.contains('man')) {
      e.preventDefault()
      openManual(Number(a.dataset.page))
    } else if (a.getAttribute('href')?.startsWith('#kb:')) {
      e.preventDefault()
      const [path, section] = a.getAttribute('href')!.slice(4).split('#')
      openPath(path, section)
    }
  }

  /** Ouvre une fiche ; `section` = debut d'ancre (ex. « 3- » pour « ## 3. Conseils »). */
  export async function openPath(path: string, section?: string) {
    open = true
    try {
      if (note?.path !== path) note = await api.kbNote(path)
      view = 'note'
      error = ''
      await tick()
      const target = section ? body?.querySelector(`[id^="${CSS.escape(section)}"]`) : null
      if (target) target.scrollIntoView({ block: 'start' })
      else body?.scrollTo({ top: 0 })
    } catch (e) {
      error = e instanceof Error ? e.message : String(e)
    }
  }

  export function openManual(page = 1) {
    open = true
    manualPage = page
    view = 'manual'
  }

  async function loadToc() {
    if (toc.length) return
    try { toc = await api.kbToc() } catch (e) { error = e instanceof Error ? e.message : String(e) }
  }

  function onkey(e: KeyboardEvent) {
    const tag = (e.target as HTMLElement).tagName
    if (e.key === '/' && tag !== 'INPUT' && tag !== 'SELECT' && tag !== 'TEXTAREA') {
      e.preventDefault()
      show()
    } else if (e.key === 'Escape' && open && e.target === input) {
      open = false
    }
  }

  export async function show() {
    open = true
    loadToc()
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
      view = 'note'
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

{#if open}
  <aside class="kb" class:wide={view === 'manual'} aria-label="Base de connaissance">
    <header>
      <input bind:this={input} bind:value={q} oninput={onInput} type="search"
        placeholder="Chercher dans la KB et la doctrine…" aria-label="Recherche" />
      <button class="small" class:on={view === 'toc'} onclick={() => { view = 'toc'; loadToc() }}>Sommaire</button>
      <button class="small" class:on={view === 'manual'} onclick={() => openManual(view === 'manual' ? manualPage : 1)}>Manuel</button>
      <button class="small" onclick={() => (open = false)} title="Fermer (Échap)">×</button>
    </header>
    {#if error}<p class="err">{error}</p>{/if}
    {#if q.trim()}
      <ul class="hits">
        {#each hits as h (h.path + h.anchor)}
          <li>
            <button class="hit" class:cur={note?.path === h.path} onclick={() => openHit(h)}>
              <span class="where small muted">{h.title}{h.heading ? ' › ' + h.heading : ''}</span>
              <span class="snip small">{#each highlight(h.snippet) as p}{#if p.on}<mark>{p.t}</mark>{:else}{p.t}{/if}{/each}</span>
            </button>
          </li>
        {:else}
          <li class="muted small none">Aucun résultat.</li>
        {/each}
      </ul>
    {/if}

    {#if view === 'toc'}
      <div class="toc">
        <p class="muted small">Fiches dans l'ordre de préparation d'un set. Touche <kbd>/</kbd> pour chercher.</p>
        <button class="hit" onclick={() => openPath(DOCTRINE)}><span>Doctrine (grille des 16 tracks, banks, mutes)</span></button>
        {#each toc as lot (lot.number)}
          <h3>Lot {lot.number} · {lot.name}</h3>
          <ul>
            {#each lot.notes as n (n.path)}
              <li>
                <button class="hit row" class:cur={note?.path === n.path} onclick={() => openPath(n.path)}>
                  <span class="mono muted">{n.ordre}</span> <span>{n.title}</span>
                  {#if n.statut}<span class="st small" class:draft={n.statut === 'draft'}>{n.statut}</span>{/if}
                </button>
              </li>
            {/each}
          </ul>
        {/each}
      </div>
    {:else if view === 'note' && note}
      <div class="note" bind:this={body} onclick={onNoteClick} role="presentation">
        <p class="path mono small muted">
          <button class="back small" onclick={() => (view = 'toc')}>← Sommaire</button> {note.path}
        </p>
        {#if note.manual.length}
          <div class="refs" aria-label="Pages du manuel">
            <span class="small muted">Manuel</span>
            {#each note.manual as r (r.section)}
              <button class="ref small" title={r.title} onclick={() => openManual(r.page)}>
                <span class="mono">§{r.section}</span> {r.title.toLowerCase()} <span class="mono muted">p{r.page}</span>
              </button>
            {/each}
          </div>
        {/if}
        <!-- eslint-disable-next-line svelte/no-at-html-tags : notes locales, HTML brut echappe -->
        {@html html}
      </div>
    {:else if view === 'manual'}
      <div class="manual">
        <div class="mbar small">
          {#if note}<button class="small" onclick={() => (view = 'note')}>← {note.title}</button>{/if}
          <span class="muted">Manuel Digitakt II (OS 1.17) · page {manualPage}</span>
          <a class="small" href={manualUrl(manualPage)} target="_blank" rel="noopener">Nouvel onglet ↗</a>
        </div>
        {#key manualPage}
          <iframe title="Manuel Digitakt II" src={manualUrl(manualPage)}></iframe>
        {/key}
      </div>
    {/if}
  </aside>
{/if}

<style>
  .kb {
    position: fixed; top: 0; right: 0; bottom: 0; z-index: 20; width: min(440px, 100vw);
    display: flex; flex-direction: column; background: var(--panel);
    border-left: 1px solid var(--border); box-shadow: -8px 0 24px rgb(0 0 0 / 0.15);
  }
  .kb.wide { width: min(960px, 100vw); }
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
  .toc { flex: 1; overflow-y: auto; padding: 4px 4px 24px; }
  .toc > p { padding: 6px 10px 0; margin: 0 0 6px; }
  .toc h3 { font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); margin: 14px 10px 4px; }
  .toc ul { list-style: none; margin: 0; padding: 0; }
  .hit.row { flex-direction: row; align-items: baseline; gap: 8px; }
  .hit.row .mono { width: 18px; text-align: right; }
  .st { margin-left: auto; padding: 0 5px; border-radius: 3px; border: 1px solid var(--border); color: var(--muted); }
  .st.draft { border-color: color-mix(in srgb, var(--accent) 50%, transparent); }
  kbd { font-family: ui-monospace, Menlo, monospace; border: 1px solid var(--border); border-radius: 3px; padding: 0 4px; }
  .back { padding: 1px 6px; margin-right: 6px; }
  .refs { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; margin: 4px 0 8px; }
  .ref { padding: 2px 6px; }
  .note :global(a.man) { color: var(--accent); text-decoration: underline dotted; }
  .manual { flex: 1; display: flex; flex-direction: column; min-height: 0; }
  .mbar { display: flex; gap: 10px; align-items: center; padding: 6px 10px; border-bottom: 1px solid var(--border); flex-wrap: wrap; }
  .mbar a { margin-left: auto; color: var(--accent); }
  iframe { flex: 1; width: 100%; border: 0; background: #525659; }
  .small { font-size: 12px; }
  .err { color: #dc2626; padding: 0 10px; font-size: 12px; }
</style>
