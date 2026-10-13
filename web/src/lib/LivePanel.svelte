<script lang="ts">
  // Panneau du live (7.L2), troisieme colonne de la vue Samples : selecteur de
  // live (library/lives/<live>.json), jauge de RAM du projet au format DT2,
  // grille banques x branches (0-COMMON en tete), liste du dossier ou de la
  // banque choisie, renommage DT2 en place, export rejouable vers 00-live.
  // Ajout : glisser des samples de la liste sur une ligne de banque, ou L sur
  // la banque active (selection, sinon sample en cours). Un sample pris par
  // deux banques ou plus part dans 0-COMMON (regle de l'API).
  import { onMount } from 'svelte'
  import { api, type LiveItem, type LiveSummary, type SampleExportReport } from './api'

  let {
    play,
    inLive = $bindable(new Map<string, string[]>()),
  }: {
    /** Ecoute d'un sample du live dans le lecteur de la vue Samples ; url : rendu accorde. */
    play: (source: string, url?: string) => void
    /** source -> banques du live choisi (badges de la liste de la lib). */
    inLive?: Map<string, string[]>
  } = $props()

  const COMMON = '0-COMMON'
  const BRANCHES = ['DRUMS', 'TONAL', 'LOOPS', 'FX', 'VX']   // lives.LIVE_BRANCHES
  const CAP = 64                                              // lives.LIVE_CAP
  const NAME_MAX = 18
  const TUNABLE = ['BD', 'RM', 'BS', 'PD', 'ST']              // lives.TUNABLE
  const LIVE_KEY = 'ui:live'
  const NEW = ':new'

  let names = $state<string[]>([])
  let current = $state('')
  let sum = $state<LiveSummary | null>(null)
  let error = $state('')
  let busy = $state(false)
  // banque active (cible de L) et dossier ouvert (<BANQUE>/<BRANCHE>, '' : toute la banque)
  let bank = $state(COMMON)
  let folder = $state('')
  let dropBank = $state<string | null>(null)
  // creation et edition des banques
  let creating = $state(false)
  let newName = $state('')
  let newPack = $state('')
  let newBanks = $state('A-HALF B-DNB C-TRIBE D-RESPI E-SATURE F-JOKER')
  let editingBanks = $state(false)
  let banksText = $state('')
  // tonalite d'une banque, saisie en place (double-clic sur la banque)
  let keying = $state<string | null>(null)
  let keyText = $state('')
  // renommage DT2 en place
  let renaming = $state<string | null>(null)
  let renameText = $state('')
  // bilan du dernier accordage (banque -> message)
  let tuneInfo = $state<{ bank: string; text: string } | null>(null)
  let report = $state<SampleExportReport | null>(null)
  let exporting = $state(false)

  const rows = $derived(sum ? [COMMON, ...sum.live.banks] : [])
  const byPath = $derived(new Map((sum?.folders ?? []).map(f => [f.path, f])))
  const shown = $derived.by((): LiveItem[] => {
    const items = sum?.live.items ?? []
    const list = folder ? items.filter(i => `${i.folder}/${i.branch}` === folder) : items.filter(i => i.folder === bank)
    return [...list].sort((a, b) => BRANCHES.indexOf(a.branch) - BRANCHES.indexOf(b.branch) || a.name.localeCompare(b.name))
  })
  const tunable = $derived((sum?.live.items ?? []).filter(i => i.folder === bank && TUNABLE.includes(i.code)))
  const shifted = $derived(tunable.some(i => i.shift))
  const ratio = $derived(sum ? sum.ram / sum.ram_limit : 0)
  const rowFiles = (b: string) => (sum?.folders ?? []).filter(f => f.path.split('/')[0] === b).reduce((n, f) => n + f.files, 0)
  // plusieurs banques -> le sample est rangé dans 0-COMMON, d'ou l'info « aussi en »
  const usedBy = (b: string) => (sum?.live.items ?? []).filter(i => i.folder === COMMON && i.banks.includes(b)).length

  const mo = (b: number) => `${(b / 1e6).toLocaleString('fr-FR', { maximumFractionDigits: 1 })} Mo`
  const fail = (e: unknown) => { error = e instanceof Error ? e.message : String(e) }

  function apply(s: LiveSummary) {
    sum = s
    inLive = new Map(s.live.items.map(i => [i.source, i.banks]))
    if (!rows.includes(bank)) { bank = s.live.banks[0] ?? COMMON; folder = '' }
    if (folder && !byPath.has(folder)) folder = ''
    error = ''
  }

  async function run(fn: () => Promise<LiveSummary>): Promise<boolean> {
    if (busy) return false
    busy = true
    try { apply(await fn()); return true } catch (e) { fail(e); return false } finally { busy = false }
  }

  async function choose(name: string) {
    report = null
    editingBanks = false
    renaming = null
    if (name === NEW) { creating = true; return }
    creating = false
    current = name
    try { localStorage.setItem(LIVE_KEY, name) } catch { /* stockage indisponible */ }
    if (!name) { sum = null; inLive = new Map(); return }
    bank = COMMON
    folder = ''
    await run(() => api.live(name))
    bank = sum?.live.banks[0] ?? COMMON
  }

  const splitBanks = (t: string) => t.split(/[\s,]+/).map(b => b.trim().toUpperCase()).filter(Boolean)

  async function create() {
    const name = newName.trim().toLowerCase()
    if (!name) return
    if (!(await run(() => api.liveCreate(name, splitBanks(newBanks), newPack.trim().toLowerCase())))) return
    names = await api.lives()
    creating = false
    newName = ''
    await choose(name)
  }

  function startBanks() {
    banksText = sum?.live.banks.join(' ') ?? ''
    editingBanks = true
  }

  async function saveBanks() {
    if (!sum) return
    const banks = splitBanks(banksText)
    const lost = sum.live.items.filter(i => !i.banks.some(b => b === COMMON || banks.includes(b)))
    if (lost.length && !confirm(`${lost.length} sample(s) n'ont plus de banque et sortent du live. Continuer ?`)) return
    if (await run(() => api.liveBanks(current, banks))) editingBanks = false
  }

  /** Ajout a une banque (L ou depot) ; tout ou rien cote API. */
  /** Tempo de la banque active (Espace tenu dans la vue Samples), null sans live ou sans tempo. */
  export function tempo(): number | null {
    return sum?.live.tempos[bank] ?? null
  }

  async function saveTempo(ev: Event) {
    const v = (ev.target as HTMLInputElement).value.trim()
    const bpm = v ? Number(v.replace(',', '.')) : null
    if (bpm !== null && !Number.isFinite(bpm)) return
    await run(() => api.liveTempo(current, bank, bpm))
  }

  export async function add(sources: string[], to: string = bank) {
    if (!current || !sources.length) return
    if (await run(() => api.liveAdd(current, sources, to))) { bank = to; folder = '' }
  }

  const remove = (sources: string[], from: string | null) => run(() => api.liveRemove(current, sources, from))

  function startKey(b: string) {
    keying = b
    keyText = sum?.live.keys[b] ?? ''
  }

  async function saveKey() {
    const b = keying
    if (!b) return
    if (await run(() => api.liveKey(current, b, keyText))) keying = null
  }

  function onKeyKey(e: KeyboardEvent) {
    if (e.key === 'Enter') { e.preventDefault(); saveKey() }
    else if (e.key === 'Escape') { e.preventDefault(); keying = null }
  }

  async function tune(reset: boolean) {
    const b = bank
    if (!(await run(() => api.liveTune(current, b, reset)))) return
    const items = (sum?.live.items ?? []).filter(i => i.folder === b && TUNABLE.includes(i.code))
    const moved = items.filter(i => i.shift).length
    const unknown = items.filter(i => !i.note).length
    tuneInfo = { bank: b, text: reset ? `${items.length} remis à leur hauteur d'origine`
      : `${moved} transposé${moved > 1 ? 's' : ''}, ${items.length - moved - unknown} déjà dans le ton`
        + (unknown ? `, ${unknown} sans note connue` : '') }
  }

  /** Ecoute telle qu'exportee : rendu varispeed de l'API si le sample est accorde. */
  function listen(it: LiveItem) {
    play(it.source, it.shift ? api.liveAudioUrl(current, it.source, it.shift) : undefined)
  }

  const fmtShift = (n: number) => (n > 0 ? `+${n}` : `${n}`)

  function startRename(it: LiveItem) {
    renaming = it.source
    renameText = it.name
  }

  async function saveRename() {
    const source = renaming
    if (!source) return
    if (await run(() => api.liveRename(current, source, renameText))) renaming = null
  }

  function onRenameKey(e: KeyboardEvent) {
    if (e.key === 'Enter') { e.preventDefault(); saveRename() }
    else if (e.key === 'Escape') { e.preventDefault(); renaming = null }
  }

  function onFormKey(e: KeyboardEvent, ok: () => void, cancel: () => void) {
    if (e.key === 'Enter') { e.preventDefault(); ok() }
    else if (e.key === 'Escape') { e.preventDefault(); cancel() }
  }

  async function runExport(dryRun: boolean) {
    if (exporting || !current) return
    exporting = true
    try { report = await api.liveExport(current, dryRun); error = '' } catch (e) { fail(e) } finally { exporting = false }
  }

  // depot : sources posees par la liste de la vue Samples (text/plain, une par ligne)
  function onDragOver(ev: DragEvent, b: string) {
    if (!current || !ev.dataTransfer?.types.includes('text/plain')) return
    ev.preventDefault()
    ev.dataTransfer.dropEffect = 'copy'
    dropBank = b
  }

  function onDrop(ev: DragEvent, b: string) {
    ev.preventDefault()
    dropBank = null
    const sources = (ev.dataTransfer?.getData('text/plain') ?? '').split('\n').filter(Boolean)
    add(sources, b)
  }

  onMount(async () => {
    try {
      names = await api.lives()
      let last = ''
      try { last = localStorage.getItem(LIVE_KEY) ?? '' } catch { /* stockage indisponible */ }
      if (last && names.includes(last)) await choose(last)
    } catch (e) { fail(e) }
  })
</script>

<section class="live zone">
  <header>
    <h3>Live</h3>
    <select value={creating ? NEW : current} onchange={e => choose((e.target as HTMLSelectElement).value)} disabled={busy}>
      <option value="">aucun</option>
      {#each names as n}<option value={n}>{n}</option>{/each}
      <option value={NEW}>nouveau live…</option>
    </select>
    {#if sum?.live.pack}<span class="muted small" title="pack des samples maison du live">pack {sum.live.pack}</span>{/if}
  </header>
  {#if error}<p class="err">{error}</p>{/if}

  {#if creating}
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="form small" onkeydown={e => onFormKey(e, create, () => (creating = false))}>
      <label>Nom <!-- svelte-ignore a11y_autofocus --><input autofocus placeholder="solaris" maxlength="32" bind:value={newName} /></label>
      <label>Pack <input placeholder="slr" maxlength="4" bind:value={newPack} title="pack des samples maison (2 à 4 caractères), optionnel" /></label>
      <label class="wide">Banques <input bind:value={newBanks} title="séparées par des espaces ; 0-COMMON est implicite" /></label>
      <span>
        <button class="small" disabled={!newName.trim() || busy} onclick={create}>Créer</button>
        <button class="small" onclick={() => (creating = false)}>Annuler</button>
      </span>
    </div>
  {:else if sum}
    {@const s = sum}
    <div class="gauge" title="RAM estimée au format envoyé par Transfer (48 kHz, 16 bits) : {s.ram.toLocaleString('fr-FR')} o sur {s.ram_limit.toLocaleString('fr-FR')} o">
      <div class="bar" class:warn={ratio > 0.8} class:over={ratio > 1} style="width: {Math.min(ratio, 1) * 100}%"></div>
    </div>
    <p class="small gauge-txt" class:err={ratio > 1}>
      RAM {mo(s.ram)} / {mo(s.ram_limit)} ({Math.round(ratio * 100)} %) · {s.live.items.length} samples
      {#if s.unknown_ram}<span class="muted"> · {s.unknown_ram} non mesuré{s.unknown_ram > 1 ? 's' : ''}</span>{/if}
    </p>

    {#if editingBanks}
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div class="form small" onkeydown={e => onFormKey(e, saveBanks, () => (editingBanks = false))}>
        <!-- svelte-ignore a11y_autofocus -->
        <label class="wide">Banques <input autofocus bind:value={banksText} title="ordre du live, séparées par des espaces" /></label>
        <span>
          <button class="small" disabled={busy} onclick={saveBanks}>Enregistrer</button>
          <button class="small" onclick={() => (editingBanks = false)}>Annuler</button>
        </span>
      </div>
    {/if}

    <table class="grid small">
      <thead>
        <tr>
          <th><button class="small link" title="Renommer, ajouter, retirer, réordonner les banques" onclick={startBanks}>banques…</button></th>
          {#each BRANCHES as br}<th>{br}</th>{/each}
        </tr>
      </thead>
      <tbody>
        {#each rows as b (b)}
          <tr class:active={bank === b} class:over={dropBank === b}
            ondragover={e => onDragOver(e, b)} ondragleave={() => { if (dropBank === b) dropBank = null }} ondrop={e => onDrop(e, b)}>
            <th>
              {#if keying === b}
                <!-- svelte-ignore a11y_autofocus -->
                <span class="keyedit">{b} (<input autofocus maxlength="12" placeholder="Fa m" bind:value={keyText} onkeydown={onKeyKey} onblur={() => (keying = null)} />)</span>
              {:else}
              <button class="bank" class:on={bank === b && !folder}
                title="{b} : {rowFiles(b)} fichiers{b === COMMON ? ' (samples de plusieurs banques)' : usedBy(b) ? `, plus ${usedBy(b)} rangés dans ${COMMON}` : ''} · clic : banque active (L), double-clic : tonalité, dépôt : ajout"
                onclick={ev => { if (ev.detail < 2) { bank = b; folder = '' } }} ondblclick={() => startKey(b)}><span class="bname">{b}</span>{#if s.live.keys[b]}<span class="key" title={s.live.keys[b]}>({s.live.keys[b]})</span>{/if}</button>
              {/if}
            </th>
            {#each BRANCHES as br}
              {@const f = byPath.get(`${b}/${br}`)}
              <td>
                {#if f}
                  <button class="cnt" class:on={folder === f.path} class:cap={f.over_cap}
                    title="{f.path} : {f.files} fichiers, {mo(f.ram)}{f.over_cap ? ` · plus de ${CAP} fichiers dans le dossier` : ''}"
                    onclick={() => { bank = b; folder = f.path }}>{f.files}</button>
                {:else}<span class="muted">·</span>{/if}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>

    <!-- depot sur la liste : ajout a la banque en cours -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="dropzone" class:over={dropBank === ':list'}
      ondragover={e => onDragOver(e, ':list')} ondragleave={() => { if (dropBank === ':list') dropBank = null }}
      ondrop={e => onDrop(e, bank)}>
    <h4 class="small">
      {folder ? folder.replace('/', ' / ') : bank}
      {#if s.live.keys[bank]}<span class="key">({s.live.keys[bank]})</span>{/if}
      <span class="muted">· {shown.length} fichier{shown.length > 1 ? 's' : ''}</span>
      <label class="bpm muted" title="Tempo de {bank} : Espace tenu relance le sample en cours à chaque temps">
        <input type="number" min="30" max="300" step="0.1" placeholder="—" value={s.live.tempos[bank] ?? ''}
          onchange={saveTempo} onkeydown={e => { if (e.key === 'Enter' || e.key === 'Escape') (e.target as HTMLElement).blur() }} /> BPM
      </label>
      {#if tunable.length}
        <button class="small link" disabled={busy || !s.live.keys[bank]}
          title={s.live.keys[bank] ? `Ramène les kicks, rumbles, basses, pads et stabs de ${bank} sur la tonique de ${s.live.keys[bank]} (varispeed à l'export, la lib n'est pas touchée)` : `Saisir d'abord la tonalité de ${bank} (double-clic sur la banque)`}
          onclick={() => tune(false)}>accorder</button>
        {#if shifted}<button class="small link" disabled={busy} title="Remet les samples de {bank} à leur hauteur d'origine" onclick={() => tune(true)}>désaccorder</button>{/if}
      {/if}
    </h4>
    {#if tuneInfo && tuneInfo.bank === bank}<p class="small muted tuneinfo">{tuneInfo.text}</p>{/if}
    <ul class="items small">
      {#each shown as it (it.source)}
        <li>
          {#if renaming === it.source}
            <!-- svelte-ignore a11y_autofocus -->
            <input class="rename mono" autofocus maxlength={NAME_MAX} bind:value={renameText} onkeydown={onRenameKey} onblur={() => (renaming = null)} />
            <span class="muted">{renameText.length}/{NAME_MAX}</span>
          {:else}
            <button class="pick mono" title="{it.source} · clic : écouter, double-clic : renommer"
              onclick={ev => { if (ev.detail < 2) listen(it) }} ondblclick={() => startRename(it)}>{it.name}</button>
          {/if}
          {#if !folder}<span class="muted br">{it.branch}</span>{/if}
          {#if it.shift}<span class="flag shift" title="{it.note} → transposé de {fmtShift(it.shift)} demi-ton{Math.abs(it.shift) > 1 ? 's' : ''} à l'export (varispeed ; clic sur le nom : écoute accordée)">{fmtShift(it.shift)}</span>{/if}
          {#if it.ram == null}<span class="flag" title="en-tête illisible : RAM non comptée">ram ?</span>{/if}
          <span class="banks">
            {#each it.banks as b}
              <span class="tag" class:here={b === bank}>{b}<button class="untag" disabled={busy} title="Retirer de {b}"
                onclick={() => remove([it.source], b)}>×</button></span>
            {/each}
          </span>
          <button class="untag out" disabled={busy} title="Retirer du live" onclick={() => remove([it.source], null)}>retirer</button>
        </li>
      {:else}
        <li class="muted">Vide : glisse des samples ici ou sur une ligne de banque, ou <kbd>L</kbd> pour la banque active.</li>
      {/each}
    </ul>
    </div>

    <div class="foot">
      <button class="small" disabled={exporting || !s.live.items.length}
        title="Copie le live vers Live/00-live/{s.live.name} (banque / branche / nom DT2), à synchroniser avec Transfer"
        onclick={() => runExport(true)}>{exporting ? 'Export…' : 'Exporter…'}</button>
    </div>
    {#if report}
      {@const r = report}
      <div class="export small">
        <strong>{r.dry_run ? 'Bilan de l’export' : 'Export terminé'}</strong>
        <span class="muted">→ {r.dest}</span>
        <p>
          {r.files} fichiers ({mo(r.bytes)}) : {r.copied.length} {r.dry_run ? 'à copier' : 'copiés'},
          {r.unchanged} inchangés, {r.removed.length} {r.dry_run ? 'à retirer' : 'retirés'}.
        </p>
        {#if r.missing.length}<p class="err">Sources absentes ({r.missing.length}) : {r.missing.slice(0, 5).join(', ')}</p>{/if}
        {#if r.conflicts.length}<p class="err">Fichiers posés à la main, non écrasés ({r.conflicts.length}) : {r.conflicts.slice(0, 5).join(', ')}</p>{/if}
        {#if r.dry_run}
          <button class="small" disabled={exporting || (!r.copied.length && !r.removed.length)}
            onclick={() => runExport(false)}>{exporting ? 'Copie…' : 'Copier'}</button>
        {/if}
        <button class="small" onclick={() => (report = null)}>{r.dry_run ? 'Annuler' : 'Fermer'}</button>
      </div>
    {/if}
  {:else if !error}
    <p class="muted small">Choisis un live ou crées-en un : une sélection de la lib rangée par banque, exportée vers <span class="mono">Live/00-live</span>.</p>
  {/if}
</section>

<style>
  .live { display: flex; flex-direction: column; gap: 6px; min-height: 0; overflow-y: auto; box-sizing: border-box; border: 1px solid var(--border); border-radius: 6px; padding: 8px 10px; }
  header { display: flex; gap: 8px; align-items: center; }
  h3 { margin: 0; font-size: 14px; }
  h4 { display: flex; gap: 6px; align-items: baseline; margin: 6px 0 0; font-weight: 600; }
  .bpm { margin-left: auto; font-weight: 400; white-space: nowrap; }
  .bpm input { width: 4.5em; font-size: 12px; }
  .form { display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: center; padding: 6px 8px; border: 1px solid var(--accent); border-radius: 4px; background: var(--panel); }
  .form label { display: flex; gap: 4px; align-items: center; }
  .form label.wide { flex: 1 1 100%; }
  .form label.wide input { flex: 1; }
  .form input { width: 8em; }
  .gauge { height: 8px; border-radius: 4px; background: var(--cell-off); overflow: hidden; }
  .bar { height: 100%; background: var(--rhythm); }
  .bar.warn { background: var(--accent); }
  .bar.over { background: #dc2626; }
  .gauge-txt { margin: 0; }
  .grid { border-collapse: collapse; width: 100%; }
  .grid th, .grid td { padding: 1px 3px; text-align: center; border-bottom: 1px solid var(--border); }
  .grid thead th { font-weight: 500; color: var(--muted); font-size: 10px; }
  .grid td { width: 2.4em; padding: 1px; }
  .grid tbody th { text-align: left; }
  .grid tr.active th .bank { font-weight: 600; }
  .grid tr.over { outline: 2px dashed var(--accent); outline-offset: -2px; }
  .bank { display: inline-flex; align-items: baseline; gap: 4px; max-width: 100%; border: 0; background: none; padding: 1px 4px; font-family: ui-monospace, monospace; font-size: 12px; text-align: left; white-space: nowrap; cursor: pointer; color: var(--text); }
  .bname { flex: none; }
  .bank.on { background: var(--accent); color: #fff; border-radius: 3px; }
  .key { min-width: 0; overflow: hidden; text-overflow: ellipsis; font-family: system-ui, sans-serif; font-size: 11px; font-weight: 400; opacity: 0.8; }
  .flag.shift { background: #2563eb; font-variant-numeric: tabular-nums; }
  .tuneinfo { margin: 0 0 4px; }
  .keyedit { font-family: ui-monospace, monospace; font-size: 12px; white-space: nowrap; }
  .keyedit input { width: 5.5em; font-size: 12px; }
  .cnt { min-width: 2.4em; padding: 0 4px; font-size: 12px; }
  .cnt.cap { border-color: #dc2626; color: #dc2626; }
  .link { border: 0; background: none; color: var(--muted); text-decoration: underline; padding: 0; cursor: pointer; }
  .dropzone { border-radius: 4px; padding-bottom: 6px; }
  .dropzone.over { outline: 2px dashed var(--accent); outline-offset: 2px; }
  .items { list-style: none; margin: 0; padding: 0; min-height: 2em; }
  .items li { display: flex; gap: 6px; align-items: center; padding: 2px 0; border-bottom: 1px solid var(--border); }
  .items li > * { flex: none; }
  .items li.muted { display: block; }
  .items li > .pick, .items li > .rename { flex: 1 1 auto; min-width: 0; }
  .pick { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; border: 0; background: none; padding: 0; cursor: pointer; color: var(--text); text-align: left; }
  .pick:hover { color: var(--accent); }
  .rename { width: 14em; font-size: 12px; }
  .mono { font-family: ui-monospace, monospace; }
  .br { font-size: 11px; }
  .banks { display: inline-flex; gap: 3px; }
  .tag { display: inline-flex; align-items: center; gap: 2px; padding: 0 4px; border: 1px solid var(--border); border-radius: 3px; font-size: 11px; }
  .tag.here { border-color: var(--accent); }
  .untag { border: 0; background: none; padding: 0 2px; cursor: pointer; color: var(--muted); font-size: 11px; }
  .untag:hover { color: #dc2626; }
  .flag { font-size: 10px; padding: 0 3px; border-radius: 3px; background: #dc2626; color: #fff; }
  .foot { display: flex; justify-content: flex-end; margin-top: 4px; }
  .export { padding: 8px 10px; border: 1px solid var(--accent); border-radius: 4px; background: var(--panel); }
  .export p { margin: 6px 0; }
  .err { color: #dc2626; font-size: 12px; margin: 0; }
</style>
