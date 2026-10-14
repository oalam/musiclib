<script lang="ts">
  // Panneau du live (7.L2), troisieme colonne de la vue Samples : selecteur de
  // live (library/lives/<live>.json), jauge de RAM du projet au format DT2,
  // grille banques x branches (0-COMMON en tete), liste du dossier ou de la
  // banque choisie, renommage DT2 en place, export rejouable vers 00-live.
  // Ajout : glisser des samples de la liste sur une ligne de banque, ou L sur
  // la banque active (selection, sinon sample en cours). Un sample pris par
  // deux banques ou plus part dans 0-COMMON (regle de l'API).
  import { onMount } from 'svelte'
  import { api, type LiveItem, type LiveSummary, type SampleExportReport, type SdPreset } from './api'
  import { focus } from './focus.svelte'

  let {
    play,
    inLive = $bindable(new Map<string, string[]>()),
    focused = false,
  }: {
    /** Ecoute d'un sample du live dans le lecteur de la vue Samples ; url : rendu accorde. */
    play: (source: string, url?: string) => void
    /** source -> banques du live choisi (badges de la liste de la lib). */
    inLive?: Map<string, string[]>
    /** fleches et Espace de la vue Samples agissent sur la liste de la banque */
    focused?: boolean
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
  let tuneInfo = $state('')
  let report = $state<SampleExportReport | null>(null)
  let exporting = $state(false)
  // rumbles de la banque active (8.L2) : presets associes, generation, bilan
  const RUMBLES_MAX = 5                                       // lives.RUMBLE_PRESETS_MAX
  let rumblePresets = $state<SdPreset[]>([])                  // presets du traitement rumble, charges au besoin
  let editingRumbles = $state(false)
  let rumbleSel = $state<string[]>([])
  let rumbling = $state(false)
  let rumbleInfo = $state('')
  const bankRumbles = $derived(sum?.live.rumbles[bank] ?? [])

  const rows = $derived(sum ? [COMMON, ...sum.live.banks] : [])
  const byPath = $derived(new Map((sum?.folders ?? []).map(f => [f.path, f])))
  const shown = $derived.by((): LiveItem[] => {
    const items = sum?.live.items ?? []
    const list = folder ? items.filter(i => `${i.folder}/${i.branch}` === folder) : items.filter(i => i.folder === bank)
    return [...list].sort((a, b) => BRANCHES.indexOf(a.branch) - BRANCHES.indexOf(b.branch) || a.name.localeCompare(b.name))
  })
  // accordage global du live : one-shots tonals, banques avec tonalite
  const tunable = $derived((sum?.live.items ?? []).filter(i => TUNABLE.includes(i.code)))
  const shifted = $derived(tunable.some(i => i.shift))
  const keyed = $derived(rows.filter(b => sum?.live.keys[b]))
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
    tuneInfo = ''
    rumbleInfo = ''
    editingRumbles = false
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

  /** Accorde (ou desaccorde) tout le live : chaque banque sur sa tonalite. */
  async function tune(reset: boolean) {
    if (!(await run(() => api.liveTune(current, reset)))) return
    const live = sum!.live
    const items = live.items.filter(i => TUNABLE.includes(i.code))
    if (reset) { tuneInfo = `${items.length} remis à leur hauteur d'origine`; return }
    const inKey = items.filter(i => live.keys[i.folder])
    const moved = inKey.filter(i => i.shift).length
    const unknown = inKey.filter(i => !i.note).length
    const keyless = [...new Set(items.filter(i => !live.keys[i.folder]).map(i => i.folder))]
    tuneInfo = `${moved} transposé${moved > 1 ? 's' : ''}, ${inKey.length - moved - unknown} déjà dans le ton`
      + (unknown ? `, ${unknown} sans note connue` : '')
      + (keyless.length ? ` · sans tonalité : ${keyless.join(', ')}` : '')
  }

  /** Presets de rumble de la banque active : coche parmi ceux du traitement rumble. */
  async function startRumbles() {
    if (!rumblePresets.length) {
      try { rumblePresets = await api.sdPresets('rumble') } catch (e) { fail(e); return }
    }
    rumbleSel = [...bankRumbles]
    editingRumbles = true
  }

  function toggleRumble(id: string) {
    rumbleSel = rumbleSel.includes(id) ? rumbleSel.filter(p => p !== id)
      : rumbleSel.length < RUMBLES_MAX ? [...rumbleSel, id] : rumbleSel
  }

  async function saveRumbles() {
    if (await run(() => api.liveRumbles(current, bank, rumbleSel))) editingRumbles = false
  }

  /** Un rumble par kick de la banque et par preset associe, au tempo de la banque ; rejouable. */
  async function runRumbles() {
    if (rumbling || !current || bank === COMMON) return
    rumbling = true
    try {
      const r = await api.liveRumblesRun(current, bank)
      const n = (xs: string[], w: string) => `${xs.length} ${w}${xs.length > 1 ? 's' : ''}`
      rumbleInfo = `${bank} à ${r.bpm} BPM, ${r.kicks} kick${r.kicks > 1 ? 's' : ''} × ${r.presets.join(', ')} : `
        + `${n(r.rendered, 'rendu')}, ${n(r.reused, 'réutilisé')}, ${n(r.added, 'ajouté')}, ${n(r.unchanged, 'inchangé')}`
        + (r.replaced.length ? `, ${n(r.replaced, 'remplacé')} (autre tempo)` : '')
        + (r.skipped.length ? ` · ignorés : ${r.skipped.join(' ; ')}` : '')
      apply(await api.live(current))
    } catch (e) { fail(e) } finally { rumbling = false }
  }

  /** Ecoute telle qu'exportee : rendu varispeed de l'API si le sample est accorde. */
  // sample en cours de la liste (fleches haut / bas quand le panneau a le clavier)
  let cur = $state<string | null>(null)

  function listen(it: LiveItem) {
    cur = it.source
    // source du sound design (8.E) : le sample ecoute ici, meme hors de la liste de la lib
    focus.set({ source: it.source, name: it.name, code: it.code, folder: `${current}/${it.folder}` })
    play(it.source, it.shift ? api.liveAudioUrl(current, it.source, it.shift) : undefined)
    queueMicrotask(() => document.getElementById(`live-${it.source}`)?.scrollIntoView({ block: 'nearest' }))
  }

  /** Fleche haut / bas : sample precedent / suivant de la liste affichee. */
  export function step(delta: number) {
    if (!shown.length) return
    const i = shown.findIndex(it => it.source === cur)
    listen(shown[i < 0 ? 0 : Math.min(Math.max(i + delta, 0), shown.length - 1)])
  }

  /** Fleche gauche / droite : banque precedente / suivante, premier sample joue. */
  export function stepBank(delta: number) {
    if (!rows.length) return
    const i = rows.indexOf(bank)
    bank = rows[(i + delta + rows.length) % rows.length]
    folder = ''
    if (shown.length) listen(shown[0])
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
    {#if sum && !creating}
      {@const live = sum.live}
      <!-- accorder / desaccorder : un seul bouton a bascule, allume quand le live est accorde -->
      <button class="small tune" class:on={shifted} aria-pressed={shifted}
        disabled={busy || !tunable.length || (!shifted && !keyed.length)}
        title={shifted ? 'Live accordé · clic : remet tout le live à sa hauteur d\'origine'
          : !tunable.length ? 'Aucun kick, rumble, basse, pad ni stab à accorder'
          : keyed.length ? `Ramène les kicks, rumbles, basses, pads et stabs de chaque banque sur la tonique de sa tonalité (${keyed.map(b => `${b} : ${live.keys[b]}`).join(', ')}) ; une banque sans tonalité garde la hauteur d'origine. Varispeed à l'export, la lib n'est pas touchée.`
          : 'Saisir d\'abord la tonalité des banques (double-clic sur une banque)'}
        onclick={() => tune(shifted)}><svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true"><path d="M5 1.5v5a3 3 0 0 0 6 0v-5M8 9.5V14.5M6 14.5h4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>{shifted ? 'Accordé' : 'Accorder'}</button>
      <button class="small exp" disabled={exporting || !live.items.length}
        title="Copie le live vers Live/00-live/{live.name} (banque / branche / nom DT2), à synchroniser avec Transfer"
        onclick={() => runExport(true)}><svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true"><path d="M8 2v8M4.5 6.5 8 10l3.5-3.5M2.5 11.5v2h11v-2" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>{exporting ? 'Export…' : 'Exporter…'}</button>
    {/if}
  </header>
  {#if error}<p class="err">{error}</p>{/if}
  {#if report && !creating}
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
    {#if tuneInfo}<p class="small muted tuneinfo">{tuneInfo} <button class="untag" title="Fermer" onclick={() => (tuneInfo = '')}>×</button></p>{/if}

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
      {#if bank !== COMMON}
        <button class="small link" disabled={busy}
          title="Presets de rumble de {bank} ({RUMBLES_MAX} au plus) : un rumble par kick et par preset, au tempo de la banque. Aucun preset : aucun rumble."
          onclick={startRumbles}>rumbles : {bankRumbles.length ? bankRumbles.join(', ') : 'aucun'}</button>
        <button class="small rum" disabled={rumbling || busy || !bankRumbles.length || !s.live.tempos[bank]}
          title={!bankRumbles.length ? 'Associer d\'abord des presets de rumble à la banque'
            : !s.live.tempos[bank] ? 'Saisir d\'abord le tempo de la banque'
            : `Rend un rumble par kick de ${bank} et par preset (${bankRumbles.join(', ')}) à ${s.live.tempos[bank]} BPM, le verse dans Samples/SoundDesign et l'ajoute à la banque. Rejouable : un rumble déjà rendu est réutilisé.`}
          onclick={runRumbles}><svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true"><path d="M1.5 8h2l1.5-4 2 8 2-6 1.5 2h4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>{rumbling ? 'Rumbles…' : 'Rumbles'}</button>
      {/if}
    </h4>
    {#if editingRumbles}
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div class="form small" onkeydown={e => onFormKey(e, saveRumbles, () => (editingRumbles = false))}>
        {#each rumblePresets as p (p.id)}
          <label title={p.description}><input type="checkbox" checked={rumbleSel.includes(p.id)}
            disabled={!rumbleSel.includes(p.id) && rumbleSel.length >= RUMBLES_MAX}
            onchange={() => toggleRumble(p.id)} /> {p.label} <span class="muted mono">{p.id}</span></label>
        {:else}
          <span class="muted">Aucun preset de rumble : en créer un dans la vue Sound design.</span>
        {/each}
        <span>
          <button class="small" disabled={busy} onclick={saveRumbles}>Enregistrer</button>
          <button class="small" onclick={() => (editingRumbles = false)}>Annuler</button>
        </span>
      </div>
    {/if}
    {#if rumbleInfo}<p class="small muted tuneinfo">{rumbleInfo} <button class="untag" title="Fermer" onclick={() => (rumbleInfo = '')}>×</button></p>{/if}
    <ul class="items small">
      {#each shown as it (it.source)}
        <li id="live-{it.source}" class:cur={it.source === cur} class:kbd={focused && it.source === cur}>
          {#if renaming === it.source}
            <!-- svelte-ignore a11y_autofocus -->
            <input class="rename mono" autofocus maxlength={NAME_MAX} bind:value={renameText} onkeydown={onRenameKey} onblur={() => (renaming = null)} />
            <span class="muted">{renameText.length}/{NAME_MAX}</span>
          {:else}
            <button class="pick mono" title="{it.source} · clic : écouter, double-clic : renommer"
              onclick={ev => { if (ev.detail < 2) listen(it) }} ondblclick={() => startRename(it)}>{it.name}</button>
          {/if}
          {#if !folder}<span class="muted br">{it.branch}</span>{/if}
          {#if it.rumble}<span class="muted br" title="rumble généré pour la banque : preset {it.rumble}{s.live.tempos[bank] ? `, ${s.live.tempos[bank]} BPM` : ''}, kick {it.parent}">{s.live.tempos[bank] ?? '—'} · {it.rumble}</span>{/if}
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
        <li class="muted">Vide : glisse des samples ici ou sur une ligne de banque, ou <kbd>L</kbd> (sélection) / <kbd>Entrée</kbd> (sample en cours) pour la banque active.</li>
      {/each}
    </ul>
    </div>
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
  .items li.cur .pick { color: var(--accent); }
  .items li.kbd { background: color-mix(in srgb, var(--accent) 14%, transparent); }
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
  .tune, .exp, .rum { display: inline-flex; align-items: center; gap: 5px; font-weight: 600; }
  .rum { border-color: var(--rhythm); color: var(--rhythm); font-size: 11px; padding: 0 6px; }
  .rum:hover:not(:disabled) { background: var(--rhythm); color: #fff; }
  .tune { margin-left: auto; border-color: #2563eb; color: #2563eb; }
  .tune.on { background: #2563eb; color: #fff; }
  .exp { background: var(--accent); border-color: var(--accent); color: #fff; }
  .tune:hover:not(:disabled), .exp:hover:not(:disabled) { filter: brightness(1.1); }
  .export { padding: 8px 10px; border: 1px solid var(--accent); border-radius: 4px; background: var(--panel); }
  .export p { margin: 6px 0; }
  .err { color: #dc2626; font-size: 12px; margin: 0; }
</style>
