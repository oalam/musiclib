<script lang="ts">
  // Vue Sound design (Phase 8.C) : rack facon Ableton Live. Tranches de
  // mixage = chaines (fader de gain, activateur = mute, solo d'ecoute), clic
  // sur le nom pour afficher ses devices ; devices en ligne (activateur =
  // bypass, potards, courbe des filtres). La boucle se re-rend a chaque
  // reglage pendant la lecture. Le solo n'est pas enregistre dans le preset.
  import { onDestroy } from 'svelte'
  import { createMarked, escapeHtml, replaceWikilinks } from './markdown'
  import { api, slugify, type DeviceSpec, type RenderRecord, type SdPreset, type SdTarget, type TreatmentSpec } from './api'
  import { focus } from './focus.svelte'
  import { remote } from './remote.svelte'
  import Device from './sd/Device.svelte'
  import Fader from './sd/Fader.svelte'
  import Knob from './sd/Knob.svelte'
  import { Looper } from './sd/looper'

  // la source est le sample en cours de la vue Samples (8.E) : on la change la-bas
  let { ongotosamples }: { ongotosamples?: () => void } = $props()

  const KEY = 'ui:sd'
  type Saved = { treatment?: string; preset?: string }
  let mem: Saved = {}
  try { mem = JSON.parse(localStorage.getItem(KEY) ?? '{}') } catch { /* stockage indisponible */ }
  function remember(patch: Saved) {
    mem = { ...mem, ...patch }
    try { localStorage.setItem(KEY, JSON.stringify(mem)) } catch { /* stockage indisponible */ }
  }

  let treatments = $state<TreatmentSpec[]>([])
  let catalogue = $state<Record<string, DeviceSpec>>({})
  let treatment = $state<TreatmentSpec | null>(null)
  let presets = $state<SdPreset[]>([])
  let preset = $state<SdPreset | null>(null)
  let saved = $state('')                       // JSON du preset tel qu'enregistre
  let selected = $state<number | 'master'>(0)  // chaine affichee dans le rack
  let solo = $state<string[]>([])
  let error = $state('')
  let renders = $state<RenderRecord[]>([])

  const dirty = $derived(preset !== null && JSON.stringify(preset) !== saved)

  // --- Chargement -----------------------------------------------------------
  Promise.all([api.sdTreatments(), api.sdDevices()]).then(([t, d]) => {
    treatments = t
    catalogue = Object.fromEntries(d.map(s => [s.type, s]))
    const first = t.find(x => x.id === mem.treatment) ?? t[0]
    if (first) void openTreatment(first)
  }).catch(e => (error = String(e)))

  async function openTreatment(t: TreatmentSpec) {
    treatment = t
    remember({ treatment: t.id })
    notebook = ''
    api.sdNotebook(t.id).then(n => (notebook = n.markdown)).catch(() => (notebook = ''))
    presets = await api.sdPresets(t.id)
    const p = presets.find(x => x.id === mem.preset) ?? presets[0]
    if (p) openPreset(p)
    renders = await api.sdRenders(t.id)
  }

  function openPreset(p: SdPreset): boolean {
    if (dirty && !confirm('Le preset en cours a des modifications non enregistrées. Les abandonner ?')) return false
    preset = structuredClone($state.snapshot(p)) as SdPreset
    saved = JSON.stringify(preset)
    selected = preset.chains.findIndex(c => !c.mute)
    if (selected < 0) selected = 0
    solo = []
    remember({ preset: p.id })
    return true
  }

  function revert() {
    const p = presets.find(x => x.id === preset?.id)
    if (p) { preset = structuredClone($state.snapshot(p)) as SdPreset; saved = JSON.stringify(preset) }
  }

  // --- Notebook (8.D) : note du vault, wikilinks en texte ---------------------
  let notebook = $state('')
  let notebookEl: HTMLElement | undefined = $state()
  const marked = createMarked()
  const notebookHtml = $derived(notebook
    ? marked.parse(replaceWikilinks(notebook.replace(/^---\n[\s\S]*?\n---\n/, ''),
        (target, alias) => escapeHtml(alias || target.split('/').pop() || target)), { async: false })
    : '')
  /** « ? » d'un device : titre du notebook qui commence par son nom (Passe-bas -> Passe-bas (avant…)). */
  function help(label: string) {
    const slug = slugify(label)
    const h = [...(notebookEl?.querySelectorAll('h3, h2') ?? [])].find(e => e.id.startsWith(slug))
    h?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    h?.classList.add('flash')
    setTimeout(() => h?.classList.remove('flash'), 1200)
  }

  // --- Enregistrement -------------------------------------------------------
  let saveAs = $state<{ id: string; label: string } | null>(null)
  async function save(target?: { id: string; label: string }) {
    if (!preset) return
    const body = $state.snapshot(preset) as SdPreset
    if (target) { body.id = target.id; body.label = target.label }
    try {
      const p = await api.sdSavePreset(body)
      presets = await api.sdPresets(p.treatment)
      preset = structuredClone(p)
      saved = JSON.stringify(preset)
      saveAs = null
      error = ''
      remember({ preset: p.id })
    } catch (e) { error = e instanceof Error ? e.message : String(e) }
  }

  // --- Chaines et devices ---------------------------------------------------
  const devices = $derived(preset ? (selected === 'master' ? preset.master : preset.chains[selected]?.devices ?? []) : [])
  function moveDevice(i: number, delta: number) {
    const j = i + delta
    if (j < 0 || j >= devices.length) return
    ;[devices[i], devices[j]] = [devices[j], devices[i]]
  }
  let adding = $state('')
  function addDevice() {
    if (!adding) return
    devices.push({ type: adding, params: {}, bypass: false })
    adding = ''
  }
  function addChain() {
    if (!preset) return
    let n = preset.chains.length + 1
    while (preset.chains.some(c => c.name === `Chaîne ${n}`)) n++
    preset.chains.push({ name: `Chaîne ${n}`, mute: false, gain_db: 0, devices: [] })
    selected = preset.chains.length - 1
  }
  function removeChain(i: number) {
    if (!preset || !confirm(`Retirer la chaîne « ${preset.chains[i].name} » et ses devices ?`)) return
    solo = solo.filter(s => s !== preset!.chains[i].name)
    preset.chains.splice(i, 1)
    selected = 0
  }
  let renaming = $state<number | null>(null)
  function toggleSolo(name: string) {
    solo = solo.includes(name) ? solo.filter(s => s !== name) : [...solo, name]
  }

  // --- Source : sample en cours de la vue Samples (8.E) ---------------------
  const source = $derived(focus.sample?.source ?? null)
  const sourceName = $derived(focus.sample?.name ?? '')
  // nom DT2 du rendu, propose par l'API (nom de la source, code du traitement,
  // tempo) et modifiable ; une autre source repart du nom propose
  let target = $state<SdTarget | null>(null)
  let name = $state('')
  let nameEdited = $state(false)
  const bpm = $derived(preset?.settings.bpm)
  $effect(() => { void source; nameEdited = false })
  $effect(() => {
    const t = treatment?.id, s = source, b = bpm
    if (!t || !s) { target = null; return }
    let stale = false
    api.sdTarget(t, s, b).then(r => {
      if (stale) return
      target = r
      if (!nameEdited) name = r.name
    }).catch(e => { if (!stale) error = e instanceof Error ? e.message : String(e) })
    return () => { stale = true }
  })
  let sourceAudio: HTMLAudioElement | undefined = $state()
  function auditionSource() {
    if (!source || !sourceAudio) return
    looper.stop()
    sourceAudio.src = api.sampleAudioUrl(source)
    void sourceAudio.play()
  }

  // --- Ecoute ---------------------------------------------------------------
  const looper = new Looper()
  let playing = $state(false)
  let busy = $state(false)
  looper.onstate = p => { playing = p; if (p) remote.played('sounddesign') }

  /** Preset envoye a l'API : le solo d'ecoute mute les autres chaines. */
  const payload = $derived.by(() => {
    if (!preset) return null
    const p = $state.snapshot(preset) as SdPreset
    if (solo.length) for (const c of p.chains) c.mute = c.mute || !solo.includes(c.name)
    return p
  })

  let seq = 0
  let abort: AbortController | null = null
  let lastKey = ''   // reglages de la boucle qui joue (evite un re-rendu identique)
  const keyOf = () => JSON.stringify(payload) + source
  async function preview() {
    if (!payload || !source) return
    const id = ++seq
    lastKey = keyOf()
    abort?.abort()
    abort = new AbortController()
    busy = true
    try {
      const data = await api.sdPreview(payload, source, abort.signal)
      const buf = await looper.decode(data)
      if (id !== seq) return
      sourceAudio?.pause()
      looper.play(buf)
      error = ''
    } catch (e) {
      if (e instanceof DOMException && e.name === 'AbortError') return
      if (id === seq) error = e instanceof Error ? e.message : String(e)
    } finally {
      if (id === seq) busy = false
    }
  }
  function playPause() { if (playing) looper.stop(); else void preview() }

  // re-rendu a chaud : tout reglage pendant la lecture relance l'ecoute
  let liveTimer: ReturnType<typeof setTimeout> | undefined
  $effect(() => {
    const key = keyOf()
    if (!playing || key === lastKey) return
    clearTimeout(liveTimer)
    liveTimer = setTimeout(() => void preview(), 180)
  })

  let verseMsg = $state('')
  async function verseRender(file: string) {
    try {
      const rec = await api.sdVerse(file)
      renders = renders.map(r => (r.file === file ? rec : r))
      await api.sampleRebuild()   // range le fichier (override DRUMS/RM/<sous>) dans la vue Samples
      verseMsg = `Versé : « ${rec.name} » vers ${rec.sub ? `DRUMS/RM/${rec.sub}` : 'DRUMS/RM'} ; réanalyse de la bibliothèque lancée.`
      error = ''
    } catch (e) { error = e instanceof Error ? e.message : String(e) }
  }

  async function renderToDisk() {
    if (!payload || !source) return
    busy = true
    try {
      const rec = await api.sdRender(payload, source, name.trim())
      renders = await api.sdRenders(rec.preset.treatment)
      error = ''
    } catch (e) { error = e instanceof Error ? e.message : String(e) }
    finally { busy = false }
  }
  let renderAudio: HTMLAudioElement | undefined = $state()
  let renderPlaying = $state<string | null>(null)
  function playRender(file: string) {
    if (!renderAudio) return
    looper.stop()
    if (renderPlaying === file) { renderAudio.pause(); renderPlaying = null; return }
    renderAudio.src = api.sdRenderAudioUrl(file)
    renderAudio.loop = true
    void renderAudio.play()
    renderPlaying = file
  }

  // deck de la telecommande : precedent / suivant = preset voisin
  const unregister = remote.register('sounddesign', {
    get label() { return preset ? `${preset.label}${sourceName ? ` — ${sourceName}` : ''}` : '' },
    get playing() { return playing },
    get looping() { return true },
    playPause,
    pause: () => looper.stop(),
    toggleLoop: () => {},
    prev: () => stepPreset(-1),
    next: () => stepPreset(1),
  })
  function stepPreset(delta: number) {
    const i = presets.findIndex(p => p.id === preset?.id)
    const p = presets[(i + delta + presets.length) % presets.length]
    if (p) openPreset(p)
  }
  onDestroy(() => { unregister(); looper.stop() })

  function onkey(e: KeyboardEvent) {
    const t = e.target as HTMLElement
    if (t.closest('.sd') === null || ['INPUT', 'SELECT', 'TEXTAREA'].includes(t.tagName)) return
    if (e.code === 'Space') { e.preventDefault(); playPause() }
  }
</script>

<svelte:window onkeydown={onkey} />

<div class="sd">
  <header class="bar">
    <label class="small">Traitement
      <select value={treatment?.id} onchange={e => { const t = treatments.find(x => x.id === e.currentTarget.value); if (t) void openTreatment(t) }}>
        {#each treatments as t (t.id)}<option value={t.id}>{t.label}</option>{/each}
      </select>
    </label>
    <label class="small">Preset
      <select value={preset?.id} onchange={e => { const p = presets.find(x => x.id === e.currentTarget.value); if (!p || !openPreset(p)) e.currentTarget.value = preset?.id ?? '' }}>
        {#each presets as p (p.id)}<option value={p.id}>{p.label}</option>{/each}
      </select>
    </label>
    {#if dirty}<span class="dirty small">modifié</span>{/if}
    <button class="small" onclick={() => save()} disabled={!dirty} title="Écrase le preset du vault (versionné par git)">Enregistrer</button>
    <button class="small" onclick={() => (saveAs = { id: `${preset?.id ?? 'preset'}_2`, label: `${preset?.label ?? ''} (2)` })} disabled={!preset}>Enregistrer sous…</button>
    <button class="small" onclick={revert} disabled={!dirty}>Rétablir</button>
    <span class="grow"></span>
    <button class="play" class:on={playing} onclick={playPause} disabled={!source || !preset}
      title="Écouter la boucle (Espace) ; elle se re-rend à chaque réglage">{playing ? '■ Stop' : '▶ Écouter'}</button>
    <button class="small" onclick={renderToDisk} disabled={!source || !preset || busy || !name.trim()}
      title="Écrit le wav 48 kHz / 24 bits et son sidecar dans SoundDesign/">Rendre sur disque</button>
    {#if busy}<span class="muted small">rendu…</span>{/if}
  </header>

  {#if saveAs}
    <form class="saveas" onsubmit={e => { e.preventDefault(); if (saveAs) void save(saveAs) }}>
      <label class="small">Id <input bind:value={saveAs.id} pattern="[a-z0-9_]{'{1,40}'}" required title="minuscules, chiffres, _" /></label>
      <label class="small">Nom <input bind:value={saveAs.label} required /></label>
      <button class="small" type="submit">Enregistrer</button>
      <button class="small" type="button" onclick={() => (saveAs = null)}>Annuler</button>
      {#if presets.some(p => p.id === saveAs?.id)}<span class="dirty small">remplace le preset existant</span>{/if}
    </form>
  {/if}

  {#if error}<p class="err">{error}</p>{/if}

  <div class="source">
    <span class="small muted">Source</span>
    {#if source}
      <span class="mono small" title={source}>{sourceName || source}</span>
      <span class="muted small">{focus.sample?.folder}</span>
      <button class="small" onclick={auditionSource} title="Écouter le sample d'origine (A/B)">▶ source</button>
    {:else}
      <span class="muted small">Aucun sample en cours : en choisir un dans la vue Samples ({treatment?.source_hint ?? '…'}).</span>
    {/if}
    <button class="small" onclick={() => ongotosamples?.()}
      title="Le traitement s'applique au sample en cours de la vue Samples">Changer dans Samples</button>
    <audio bind:this={sourceAudio}></audio>
    <span class="grow"></span>
    <label class="small" title="Nom affiché par la DT2 (18 caractères), proposé à partir de la source">Nom DT2
      <input class="mono name" bind:value={name} oninput={() => (nameEdited = true)} maxlength="18" size="18"
        pattern={"[A-Za-z0-9#][A-Za-z0-9 #._+\\-]*"} disabled={!source} /></label>
    {#if nameEdited && target}<button class="small" onclick={() => { name = target!.name; nameEdited = false }} title="Revenir au nom proposé : {target.name}">↺</button>{/if}
    {#if target}<span class="muted small" title="Dossier du rendu une fois versé dans les samples">→ {target.folder}</span>{/if}
  </div>

  {#if preset && treatment}
    <div class="rack">
      <section class="panel settings">
        <h3>{treatment.label}</h3>
        <div class="knobs">
          {#each treatment.settings as s (s.name)}
            <Knob spec={s} value={preset.settings[s.name] ?? s.default} onchange={v => (preset!.settings[s.name] = v)} />
          {/each}
          {#if treatment.settings.some(s => s.name === 'bpm')}
            <span class="muted small dur mono" title="durée de la boucle = mesures × 4 × 60 / bpm">
              {((preset.settings.bars ?? 1) * 4 * 60 / (preset.settings.bpm ?? 150)).toFixed(3)} s
            </span>
          {/if}
        </div>
      </section>

      <section class="panel mixer" aria-label="Chaînes">
        {#each preset.chains as c, i (i)}
          <div class="strip" class:sel={selected === i}>
            <Fader label={c.name} value={c.gain_db} muted={c.mute} onchange={v => (c.gain_db = v)} />
            {#if renaming === i}
              <input class="rename small" value={c.name} onkeydown={e => { if (e.key === 'Enter') e.currentTarget.blur(); if (e.key === 'Escape') renaming = null }}
                onblur={e => { const v = e.currentTarget.value.trim(); if (v && !preset!.chains.some((o, j) => j !== i && o.name === v)) c.name = v; renaming = null }} />
            {:else}
              <button class="cname small" onclick={() => (selected = i)} ondblclick={() => (renaming = i)} title="Afficher ses devices ; double-clic pour renommer">{c.name}</button>
            {/if}
            <div class="btns">
              <button class="tact" class:on={!c.mute} onclick={() => (c.mute = !c.mute)} aria-pressed={!c.mute} title={c.mute ? 'Activer la chaîne' : 'Couper la chaîne (mute, enregistré)'}>{i + 1}</button>
              <button class="tsolo" class:on={solo.includes(c.name)} onclick={() => toggleSolo(c.name)} title="Solo d'écoute (non enregistré)">S</button>
            </div>
            <button class="mini" onclick={() => removeChain(i)} title="Retirer la chaîne">×</button>
          </div>
        {/each}
        <div class="strip master" class:sel={selected === 'master'}>
          <div class="masterbox">
            <span class="small muted">Crête</span>
            <span class="mono small">{preset.output_peak_db === null ? 'brut' : `${preset.output_peak_db} dB`}</span>
            <label class="small" title="Normaliser la crête de la boucle">
              <input type="checkbox" checked={preset.output_peak_db !== null} onchange={e => (preset!.output_peak_db = e.currentTarget.checked ? -1 : null)} /> norm.</label>
          </div>
          <button class="cname small" onclick={() => (selected = 'master')}>Master</button>
        </div>
        <button class="add small" onclick={addChain} title="Ajouter une chaîne parallèle">+ chaîne</button>
      </section>

      <section class="panel chain">
        <h3>{selected === 'master' ? 'Master' : preset.chains[selected]?.name} <span class="muted small">{selected === 'master' ? 'après la somme des chaînes' : 'chaîne parallèle'}</span></h3>
        <div class="devices">
          {#each devices as d, i (i + d.type)}
            <Device device={d} spec={catalogue[d.type]} onmove={delta => moveDevice(i, delta)} onremove={() => devices.splice(i, 1)}
              onhelp={() => help(catalogue[d.type]?.label ?? d.type)} />
            <span class="arrow" aria-hidden="true">→</span>
          {/each}
          <div class="adder">
            <select class="small" bind:value={adding}>
              <option value="">+ device…</option>
              {#each Object.values(catalogue) as s (s.type)}<option value={s.type} title={s.help}>{s.label}</option>{/each}
            </select>
            <button class="small" onclick={addDevice} disabled={!adding}>Ajouter</button>
          </div>
        </div>
      </section>
    </div>

    <div class="lower">
      <section class="panel notebook">
        <p class="small muted nbpath">Notebook — <code>{treatment.notebook}</code> · {preset.label} : {preset.description}</p>
        {#if notebookHtml}
          <article class="md" bind:this={notebookEl}>{@html notebookHtml}</article>
        {:else}
          <p>{treatment.summary}</p>
          <p class="small muted">Sample attendu : {treatment.source_hint}. Notebook absent du vault.</p>
        {/if}
      </section>
      <section class="panel renders">
        <h3>Rendus <span class="muted small">SoundDesign/{treatment.id}</span></h3>
        <audio bind:this={renderAudio} onended={() => (renderPlaying = null)}></audio>
        {#if verseMsg}<p class="small muted">{verseMsg}</p>{/if}
        <ul>
          {#each renders as r (r.file)}
            <li>
              <button class="small" class:on={renderPlaying === r.file} onclick={() => playRender(r.file)}>{renderPlaying === r.file ? '■' : '▶'}</button>
              <span class="mono small fname" title={`${r.file}\n${r.source}\n${r.created_at}`}>{r.name || r.file.split('/').pop()}</span>
              <span class="muted small">{r.seconds.toFixed(2)} s</span>
              {#if r.versed}<span class="versed small" title={`Samples/${r.versed}`}>versé</span>
              {:else if r.name}<button class="small" onclick={() => verseRender(r.file)} title="Copier dans le pack Samples/SoundDesign et ranger en {r.sub ? `DRUMS/RM/${r.sub}` : 'DRUMS/RM'}">Verser</button>
              {:else}<span class="muted small" title="Rendu antérieur au nommage DT2 : le re-rendre pour le verser">sans nom</span>{/if}
            </li>
          {:else}<li class="muted small">Aucun rendu pour l'instant.</li>{/each}
        </ul>
      </section>
    </div>
  {/if}
</div>

<style>
  .sd { height: 100%; overflow-y: auto; padding: 10px 14px 24px; display: flex; flex-direction: column; gap: 10px; }
  .bar, .source, .saveas { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .bar label, .saveas label { display: flex; align-items: center; gap: 6px; }
  .grow { flex: 1; }
  .dirty { color: var(--accent); }
  .play { min-width: 96px; font-weight: 600; }
  .source label { display: flex; align-items: center; gap: 6px; }
  .name:invalid { border-color: #dc2626; }
  .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 6px; padding: 8px 10px; }
  h3 { margin: 0 0 8px; font-size: 13px; }
  .rack { display: flex; gap: 10px; align-items: stretch; min-width: 0; }
  .settings { flex: none; width: 150px; }
  .settings .knobs { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }
  .dur { width: 100%; text-align: center; }
  .mixer { flex: none; display: flex; gap: 4px; align-items: flex-end; }
  .strip { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 4px 2px; border-radius: 4px; border: 1px solid transparent; }
  .strip.sel { border-color: var(--accent); background: var(--panel-2); }
  .cname { padding: 1px 6px; max-width: 70px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .rename { width: 70px; padding: 1px 4px; }
  .btns { display: flex; gap: 2px; }
  .tact, .tsolo { padding: 0 6px; font-size: 11px; line-height: 18px; min-width: 22px; }
  .tact.on { background: #e5b80b; border-color: #e5b80b; color: #1c1c1c; }   /* activateur jaune facon Live */
  .tsolo.on { background: #3b82f6; border-color: #3b82f6; color: #fff; }
  .mini { padding: 0 5px; font-size: 12px; background: none; border-color: transparent; color: var(--muted); }
  .masterbox { display: flex; flex-direction: column; align-items: center; gap: 4px; height: 160px; justify-content: center; }
  .add { align-self: flex-end; margin: 0 0 4px 6px; }
  .chain { flex: 1; min-width: 0; }
  .devices { display: flex; align-items: flex-start; gap: 6px; overflow-x: auto; padding-bottom: 6px; }
  .arrow { align-self: center; color: var(--muted); }
  .adder { display: flex; flex-direction: column; gap: 6px; align-self: center; }
  .lower { display: grid; grid-template-columns: minmax(0, 2fr) minmax(0, 1fr); gap: 10px; align-items: start; }
  .renders { position: sticky; top: 0; }
  .nbpath { margin: 0 0 4px; }
  .md { line-height: 1.55; max-width: 820px; }
  .md :global(h1) { font-size: 20px; margin: 4px 0 10px; }
  .md :global(h2) { font-size: 16px; margin: 18px 0 6px; border-bottom: 1px solid var(--border); padding-bottom: 3px; }
  .md :global(h3) { font-size: 14px; margin: 14px 0 4px; scroll-margin-top: 8px; border-radius: 3px; transition: background 0.4s; }
  .md :global(h3.flash) { background: color-mix(in srgb, var(--accent) 25%, transparent); }
  .md :global(table) { border-collapse: collapse; font-size: 12px; margin: 6px 0; }
  .md :global(th), .md :global(td) { border: 1px solid var(--border); padding: 3px 8px; text-align: left; vertical-align: top; }
  .md :global(th) { background: var(--panel-2); }
  .md :global(code) { font-size: 12px; background: var(--panel-2); padding: 0 3px; border-radius: 3px; }
  .md :global(a) { color: var(--accent); }
  .versed { color: var(--accent); }
  .renders ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px; max-height: 200px; overflow-y: auto; }
  .renders li { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
  .fname { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; }
  .small { font-size: 12px; }
  .err { color: #dc2626; font-size: 12px; margin: 0; }
  @media (max-width: 900px) {
    .rack { flex-direction: column; }
    .settings { width: auto; }
    .mixer { overflow-x: auto; }
    .lower { grid-template-columns: 1fr; }
  }
</style>
