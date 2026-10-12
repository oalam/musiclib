<script lang="ts">
  // Generateur acid (Phase 9.C), outil MIDI du sound design, inspire de Sting
  // (if-tah). Generate tire les couches allumees (notes, accent, gate, octave)
  // cote API, comme les « Randomize » de Sting ; une couche eteinte est gardee. Les potards de
  // tirage (Type, Density, octaves) ne relancent que leur couche, avec la meme
  // graine ; les autres (Steps, Offset, Accent, Gate, Swing, Transpose, Root,
  // Scale) changent la lecture sans retirer. Grille editable : clic = cycle
  // de valeurs, molette / fleches sur une note = degre suivant. Pendant la
  // lecture, chaque modification part au tour suivant (`/api/acid/play`).
  import { onDestroy, onMount } from 'svelte'
  import { api, type AcidLayer, type AcidParams, type AcidPlayerState, type AcidProgression, type AcidScale,
    type AcidSequence, type AcidStep, type Dt2Ports, type ParamSpec } from '../api'
  import Knob from './Knob.svelte'

  const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
  const LAYERS: { id: AcidLayer; label: string }[] = [
    { id: 'notes', label: 'Notes' }, { id: 'velocity', label: 'Accent' },
    { id: 'gate', label: 'Gate' }, { id: 'octave', label: 'Octave' },
  ]
  const DEFAULTS: AcidParams = {
    type: 8, density: 12, accent: 50, gate: 100, root: 0, scale: 'AEOLIAN (MINOR)', transpose: 0,
    octave_low: -1, octave_high: 1, base_note: 36, steps: 16, offset: 0, direction: 'forward',
    swing: 50, tie_mode: true, mode: 'algo', progression: [0, 5, 6, 0], chord_steps: 16, arp: 'up',
  }
  const SEQ_LEN = 32
  const ARPS: [AcidParams['arp'], string, string][] = [
    ['up', '↑', 'montant'], ['down', '↓', 'descendant'], ['updown', '↕', 'aller-retour'], ['random', '?', 'au hasard dans l’accord']]

  const knob = (name: string, label: string, min: number, max: number, def: number, unit = '', help = ''): ParamSpec =>
    ({ name, label, min, max, default: def, unit, scale: 'lin', step: 1, help, choices: null })
  // potards de tirage -> couche relancee
  const DRAW: [ParamSpec, AcidLayer][] = [
    [knob('type', 'Type', 1, 16, 8, '', '1 = pas conjoints et tonique fréquente, 16 = grands sauts'), 'notes'],
    [knob('density', 'Density', 1, 16, 12, '', 'pas joués sur 16'), 'gate'],
    [knob('octave_low', 'Oct low', -1, 2, -1), 'octave'],
    [knob('octave_high', 'Oct high', -1, 2, 1), 'octave'],
  ]
  const PLAY: ParamSpec[] = [
    knob('steps', 'Steps', 1, 32, 16, '', 'longueur de la boucle'),
    knob('offset', 'Offset', 0, 31, 0, '', 'premier pas joué (repère ▶ dans la grille)'),
    knob('accent', 'Accent', 0, 100, 50, '%', 'contraste des vélocités'),
    knob('gate', 'Gate', 1, 200, 100, '%', 'échelle des longueurs'),
    knob('swing', 'Swing', 50, 75, 50, '%', '50 = droit, 66 = ternaire'),
    knob('transpose', 'Transp.', -24, 24, 0, 'st'),
  ]

  const KEY = 'ui:acid'
  type Saved = {
    params?: AcidParams; seq?: AcidSequence; locks?: AcidLayer[]
    target?: 'dt2' | 'mac'; port?: string; channel?: number; bpm?: number; slideCc?: number | null
    bars?: number | null
  }
  let mem: Saved = {}
  try { mem = JSON.parse(localStorage.getItem(KEY) ?? '{}') } catch { /* stockage indisponible */ }

  let params = $state<AcidParams>({ ...DEFAULTS, ...mem.params })
  // sequence de 16 pas (avant 32) : la 2e mesure repete la 1re, comme l'API
  if (mem.seq && mem.seq.steps.length < SEQ_LEN) mem.seq.steps = [...mem.seq.steps, ...mem.seq.steps].slice(0, SEQ_LEN)
  let seq = $state<AcidSequence | null>(mem.seq ?? null)
  let locks = $state<AcidLayer[]>(mem.locks ?? [])
  let target = $state<'dt2' | 'mac'>(mem.target ?? 'mac')
  let port = $state(mem.port ?? '')
  let channel = $state(mem.channel ?? 1)
  let bpm = $state(mem.bpm ?? 140)
  let slideCc = $state<number | null>(mem.slideCc ?? null)
  let bars = $state<number | null>(mem.bars ?? null)
  let progs = $state<AcidProgression[]>([])
  let scales = $state<AcidScale[]>([])
  let ports = $state<Dt2Ports | null>(null)
  let player = $state<AcidPlayerState | null>(null)
  let error = $state('')

  $effect(() => {
    const s: Saved = { params: $state.snapshot(params), seq: $state.snapshot(seq) ?? undefined,
      locks: [...locks], target, port, channel, bpm, slideCc, bars }
    try { localStorage.setItem(KEY, JSON.stringify(s)) } catch { /* stockage indisponible */ }
  })

  const intervals = $derived(scales.find(s => s.name === params.scale)?.intervals ?? [0, 2, 3, 5, 7, 8, 10])
  const order = $derived(playOrder(params))
  const active = $derived(player !== null && (player.status === 'playing' || player.status === 'waiting'))

  /** Meme regle que `acid.play_order`. */
  function playOrder(p: AcidParams): number[] {
    const w = Array.from({ length: p.steps }, (_, i) => (p.offset + i) % SEQ_LEN)
    if (p.direction === 'backward') return w.reverse()
    if (p.direction === 'pendulum' && w.length > 2) return [...w, ...w.slice(1, -1).reverse()]
    return w
  }

  /** Meme regle que `acid.step_note` ; nom facon Elektron (60 = C5, comme la DT2). */
  function noteOf(st: AcidStep): number {
    const n = intervals.length
    const o = Math.floor(st.degree / n)
    const v = params.base_note + params.root + params.transpose + 12 * (o + st.octave) + intervals[st.degree - o * n]
    return Math.min(127, Math.max(0, v))
  }
  const noteName = (m: number) => `${NOTE_NAMES[m % 12]}${Math.floor(m / 12)}`

  async function run<T>(f: () => Promise<T>): Promise<T | undefined> {
    try { error = ''; return await f() } catch (e) { error = (e as Error).message }
  }

  async function generate() {
    const s = await run(() => api.acidGenerate({ params: $state.snapshot(params), seed: null,
      previous: seq ? $state.snapshot(seq) : null, locks: seq ? [...locks] : [] }))
    if (s) seq = s
  }

  /** Relance une couche apres un potard de tirage (meme graine, autres couches gardees). */
  async function redraw(layer: AcidLayer) {
    if (!seq) return
    const keep = LAYERS.map(l => l.id).filter(l => l !== layer || locks.includes(l))
    const s = await run(() => api.acidGenerate({ params: $state.snapshot(params), seed: seq!.seed,
      previous: $state.snapshot(seq), locks: keep }))
    if (s) seq = s
  }

  function setDraw(name: string, layer: AcidLayer, v: number) {
    const p = params as unknown as Record<string, number>
    p[name] = v
    if (name === 'octave_low' && params.octave_high < v) params.octave_high = v
    if (name === 'octave_high' && params.octave_low > v) params.octave_low = v
    void redraw(layer)
  }

  const progName = $derived(progs.find(g => g.degrees.join() === params.progression.join())?.name ?? '')
  function setArp(patch: Partial<AcidParams>) {
    Object.assign(params, patch)
    void redraw('notes')
  }

  const toggleLock = (l: AcidLayer) => (locks = locks.includes(l) ? locks.filter(x => x !== l) : [...locks, l])

  // --- grille ---
  const cycle = (v: number, lo: number, hi: number) => (v >= hi ? lo : v + 1)
  function nudge(st: AcidStep, d: number) {
    const n = intervals.length
    st.degree = Math.min(2 * n - 1, Math.max(-n, st.degree + d))
    st.on = true
  }
  function noteKey(e: KeyboardEvent, st: AcidStep) {
    if (e.key === 'ArrowUp') { e.preventDefault(); nudge(st, 1) }
    else if (e.key === 'ArrowDown') { e.preventDefault(); nudge(st, -1) }
    else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); st.on = !st.on }
  }
  const slides = (i: number) => {
    if (!seq || !params.tie_mode || !seq.steps[i].on || seq.steps[i].gate !== 2) return false
    const pos = order.indexOf(i)
    return pos >= 0 && pos + 1 < order.length && seq.steps[order[pos + 1]].on
  }

  // --- lecture ---
  function request() {
    return { sequence: { ...$state.snapshot(seq)!, params: $state.snapshot(params) },
      target, port, channel, bpm, slide_cc: slideCc, bars }
  }
  let lastSent = ''
  async function play() {
    if (!seq || !port) return
    const req = request()
    lastSent = JSON.stringify(req)
    const st = await run(() => api.acidPlay(req))
    if (st) { player = st; poll() }
  }
  async function stop() { player = (await run(() => api.acidStop())) ?? player }
  async function panic() { player = (await run(() => api.acidPanic())) ?? player }

  // pendant la lecture : toute modification part au tour suivant
  let pushTimer: ReturnType<typeof setTimeout> | undefined
  $effect(() => {
    if (!active || !seq) return
    const req = request()
    const key = JSON.stringify(req)
    if (key === lastSent) return
    clearTimeout(pushTimer)
    pushTimer = setTimeout(() => { lastSent = key; void run(() => api.acidPlay(req)).then(st => { if (st) player = st }) }, 150)
  })

  let pollTimer: ReturnType<typeof setInterval> | undefined
  function poll() {
    clearInterval(pollTimer)
    pollTimer = setInterval(async () => {
      const st = await api.acidState().catch(() => null)
      player = st
      if (!st || !['playing', 'waiting'].includes(st.status)) clearInterval(pollTimer)
    }, 200)
  }

  function pickPort() {
    const outs = ports?.outputs ?? []
    if (port && outs.includes(port)) return
    port = target === 'dt2' ? (ports?.default ?? outs[0] ?? '') : (outs.find(o => /IAC/i.test(o)) ?? '')
  }
  async function loadPorts() {
    ports = (await run(() => api.dt2Ports())) ?? null
    pickPort()
  }

  onMount(async () => {
    scales = (await run(() => api.acidScales())) ?? []
    progs = (await run(() => api.acidProgressions())) ?? []
    await loadPorts()
    player = (await api.acidState().catch(() => null))
    if (active) poll()
    if (!seq) await generate()
  })
  onDestroy(() => { clearInterval(pollTimer); clearTimeout(pushTimer) })
</script>

<div class="acid">
  <header class="bar">
    <strong>Acid · MIDI</strong>
    <button class="gen" onclick={generate} disabled={locks.length === LAYERS.length}
      title={locks.length === LAYERS.length ? 'Aucune couche à tirer : en allumer au moins une' : 'Retire les couches allumées (nouvelle graine)'}>Generate</button>
    <span class="locks" role="group" aria-label="Couches tirées par Generate">
      <span class="small muted">tirer :</span>
      {#each LAYERS as l (l.id)}
        <button class="small" class:on={!locks.includes(l.id)} aria-pressed={!locks.includes(l.id)} onclick={() => toggleLock(l.id)}
          title={locks.includes(l.id) ? `${l.label} gardé au prochain Generate (clic = le tirer)` : `${l.label} retiré au prochain Generate (clic = le garder)`}>{l.label}</button>
      {/each}
    </span>
    <span class="small muted">graine {seq?.seed ?? '—'}</span>
    <span class="grow"></span>
    <label class="small" title="Arrêt automatique après N mesures (pour échantillonner), ou boucle">Mesures
      <select bind:value={bars}>
        <option value={null}>∞</option>
        {#each [1, 2, 3, 4, 5, 6, 7, 8] as n (n)}<option value={n}>{n}</option>{/each}
      </select>
    </label>
    <button class="play" class:on={active} onclick={() => (active ? stop() : play())} disabled={!seq || !port}
      title={active ? 'Arrêter (coupe les notes)' : bars ? `Jouer ${bars} mesure(s) puis s'arrêter` : 'Jouer en boucle'}>{active ? '■ Stop' : '▶ Play'}</button>
    <button class="small" onclick={panic} title="All notes off sur les 16 canaux">Panique</button>
  </header>

  {#if error}<p class="err">{error}</p>{/if}

  <div class="row">
    <section class="panel knobs" aria-label="Tirage">
      <h3>Tirage</h3>
      <div class="kn">
        {#each DRAW as [s, layer] (s.name)}
          <Knob spec={s} value={(params as unknown as Record<string, number>)[s.name]} onchange={v => setDraw(s.name, layer, v)}
            disabled={s.name === 'type' && params.mode === 'arp'} />
        {/each}
      </div>
    </section>
    <section class="panel knobs" aria-label="Lecture">
      <h3>Lecture</h3>
      <div class="kn">
        {#each PLAY as s (s.name)}
          <Knob spec={s} value={(params as unknown as Record<string, number>)[s.name]}
            onchange={v => ((params as unknown as Record<string, number>)[s.name] = v)} />
        {/each}
      </div>
    </section>
    <section class="panel tone" aria-label="Mode des notes">
      <h3>Notes</h3>
      <div class="choices" role="radiogroup" aria-label="Mode">
        <button role="radio" aria-checked={params.mode === 'algo'} class:on={params.mode === 'algo'}
          onclick={() => setArp({ mode: 'algo' })} title="Marche aléatoire dans la gamme (Type)">Algo</button>
        <button role="radio" aria-checked={params.mode === 'arp'} class:on={params.mode === 'arp'}
          onclick={() => setArp({ mode: 'arp' })} title="Arpège des accords de la gamme">Arp</button>
      </div>
      {#if params.mode === 'arp'}
        <label class="small" title="Accords de la gamme, en degrés (I = tonique)">Progression
          <select value={progName} onchange={e => setArp({ progression: progs.find(g => g.name === (e.currentTarget as HTMLSelectElement).value)!.degrees })}>
            {#if !progName}<option value="">{params.progression.map(d => d + 1).join('-')}</option>{/if}
            {#each progs as g (g.name)}<option value={g.name}>{g.name}</option>{/each}
          </select>
        </label>
        <div class="choices" role="radiogroup" aria-label="Durée d'un accord">
          <button role="radio" aria-checked={params.chord_steps === 16} class:on={params.chord_steps === 16} onclick={() => setArp({ chord_steps: 16 })}>1 mesure</button>
          <button role="radio" aria-checked={params.chord_steps === 8} class:on={params.chord_steps === 8} onclick={() => setArp({ chord_steps: 8 })}>½ mesure</button>
        </div>
        <div class="choices" role="radiogroup" aria-label="Motif">
          {#each ARPS as [a, sym, label] (a)}
            <button role="radio" aria-checked={params.arp === a} class:on={params.arp === a} onclick={() => setArp({ arp: a })} title={label}>{sym}</button>
          {/each}
        </div>
      {/if}
    </section>
    <section class="panel tone" aria-label="Tonalité">
      <h3>Tonalité</h3>
      <label class="small">Root
        <select bind:value={params.root}>{#each NOTE_NAMES as n, i (n)}<option value={i}>{n}</option>{/each}</select>
      </label>
      <label class="small">Scale
        <select bind:value={params.scale}>{#each scales as s (s.name)}<option value={s.name}>{s.label}</option>{/each}</select>
      </label>
      <div class="choices" role="radiogroup" aria-label="Direction">
        {#each [['forward', '→'], ['backward', '←'], ['pendulum', '↔']] as [d, sym] (d)}
          <button role="radio" aria-checked={params.direction === d} class:on={params.direction === d}
            onclick={() => (params.direction = d as AcidParams['direction'])} title={d}>{sym}</button>
        {/each}
      </div>
      <label class="small" title="Pas long suivi d'un pas joué = note liée (slide)">
        <input type="checkbox" bind:checked={params.tie_mode} /> Tie (slides)</label>
    </section>
  </div>

  {#if seq}
    <section class="panel grid" aria-label="Séquence">
      {#each [0, 16] as b (b)}
        <div class="gridrows" style:--n="16">
          <span class="lab small muted">{b ? 'Mesure 2' : 'Mesure 1'}</span>
          {#each seq.steps.slice(b, b + 16) as _, j (j)}
            {@const i = b + j}
            <span class="num small" class:out={!order.includes(i)} class:now={active && player?.step === i} class:start={order[0] === i}
              title={order[0] === i ? 'Départ de la lecture (Offset)' : ''}>{order[0] === i ? (params.direction === 'backward' ? '◀' : '▶') : ''}{i + 1}</span>
          {/each}

          <span class="lab small muted">Note</span>
          {#each seq.steps.slice(b, b + 16) as st, j (j)}
            {@const i = b + j}
            <button class="cell note mono" class:off={!st.on} class:out={!order.includes(i)} class:now={active && player?.step === i}
              onclick={() => (st.on = !st.on)} onwheel={e => { e.preventDefault(); nudge(st, e.deltaY < 0 ? 1 : -1) }}
              onkeydown={e => noteKey(e, st)} title="Clic = joué / silence ; molette ou ↑↓ = degré">
              {st.on ? noteName(noteOf(st)) : '·'}
            </button>
          {/each}

          <span class="lab small muted">Accent</span>
          {#each seq.steps.slice(b, b + 16) as st, j (j)}
            {@const i = b + j}
            <button class="cell" class:out={!order.includes(i)} onclick={() => (st.accent = cycle(st.accent, 0, 2))}
              title="Accent {['aucun', 'moyen', 'fort'][st.accent]}">
              <span class="acc" style:opacity={st.on ? [0.15, 0.55, 1][st.accent] : 0.08}></span>
            </button>
          {/each}

          <span class="lab small muted">Gate</span>
          {#each seq.steps.slice(b, b + 16) as st, j (j)}
            {@const i = b + j}
            <button class="cell gate" class:out={!order.includes(i)} onclick={() => (st.gate = cycle(st.gate, 0, 2))}
              title="Longueur {['courte', 'normale', 'longue'][st.gate]}{slides(i) ? ' · slide vers le pas suivant' : ''}">
              <span class="len" class:dim={!st.on} style:width="{[25, 50, 100][st.gate]}%"></span>
              {#if slides(i)}<span class="tie">⌒</span>{/if}
            </button>
          {/each}

          <span class="lab small muted">Octave</span>
          {#each seq.steps.slice(b, b + 16) as st, j (j)}
            {@const i = b + j}
            <button class="cell mono small" class:out={!order.includes(i)}
              onclick={() => (st.octave = cycle(st.octave, params.octave_low, params.octave_high))}
              title="Octave (de {params.octave_low} à {params.octave_high})">{st.octave > 0 ? `+${st.octave}` : st.octave}</button>
          {/each}
        </div>
      {/each}
    </section>
  {/if}

  <section class="panel midi" aria-label="Sortie MIDI">
    <div class="choices" role="radiogroup" aria-label="Cible">
      <button role="radio" aria-checked={target === 'mac'} class:on={target === 'mac'} disabled={active}
        onclick={() => { target = 'mac'; port = ''; pickPort() }} title="Horloge interne vers un bus IAC (VST du Mac)">VST du Mac</button>
      <button role="radio" aria-checked={target === 'dt2'} class:on={target === 'dt2'} disabled={active}
        onclick={() => { target = 'dt2'; port = ''; pickPort() }} title="Suit le Start et l'horloge de la DT2">DT2</button>
    </div>
    <label class="small">Port
      <select bind:value={port} disabled={active}>
        <option value="">—</option>
        {#each ports?.outputs ?? [] as o (o)}<option value={o}>{o}</option>{/each}
      </select>
    </label>
    <button class="mini" onclick={loadPorts} title="Relire les ports MIDI">↻</button>
    <label class="small" title={target === 'dt2' ? 'AUTO CHANNEL ou CHAN d’une track MIDI de la DT2' : 'Canal écouté par le VST'}>Canal
      <input type="number" min="1" max="16" bind:value={channel} disabled={active} /></label>
    {#if target === 'mac'}<label class="small">BPM <input type="number" min="40" max="300" bind:value={bpm} /></label>{/if}
    <label class="small" title="CC envoyé à 127 sur une note atteinte par un slide, 0 sinon (vide = aucun)">CC slide
      <input type="number" min="0" max="127" value={slideCc ?? ''}
        oninput={e => { const v = (e.currentTarget as HTMLInputElement).value; slideCc = v === '' ? null : Number(v) }} /></label>
    <span class="grow"></span>
    {#if ports?.error}<span class="err small">{ports.error}</span>{/if}
    {#if !port && target === 'mac'}<span class="small muted">Aucun bus IAC : l’activer dans Configuration audio et MIDI.</span>{/if}
    {#if player}
      <span class="small" class:muted={!active} title={player.detail}>
        {player.status === 'waiting' ? 'en attente du Start de la DT2' : player.status === 'done' ? `terminé : ${player.detail}` : player.detail}{player.pending ? ' · changement au tour suivant' : ''}
        {player.status === 'playing' ? ` · tour ${player.cycles + 1}` : ''}
      </span>
      {#if player.warning}<span class="err small">{player.warning}</span>{/if}
    {/if}
  </section>
</div>

<style>
  .acid { display: flex; flex-direction: column; gap: 8px; min-width: 0; }
  .bar, .midi { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .grow { flex: 1; }
  .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 6px; padding: 8px 10px; }
  h3 { margin: 0 0 4px; font-size: 11px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
  .row { display: flex; gap: 8px; flex-wrap: wrap; }
  .kn { display: flex; gap: 4px; flex-wrap: wrap; }
  .tone { display: flex; flex-direction: column; gap: 6px; }
  .choices { display: flex; gap: 2px; }
  .choices button { padding: 1px 8px; font-size: 11px; border-radius: 2px; }
  .locks { display: flex; gap: 2px; align-items: center; }
  .gen { font-weight: 600; }
  .play { min-width: 76px; }
  .small { font-size: 12px; }
  .muted { color: var(--muted); }
  .mini { padding: 0 5px; font-size: 12px; background: none; border-color: transparent; color: var(--muted); }
  .err { color: #d55; }
  input[type='number'] { width: 52px; }
  .grid { overflow-x: auto; }
  .gridrows { display: grid; grid-template-columns: 52px repeat(var(--n), minmax(34px, 1fr)); gap: 2px; align-items: center; }
  .lab { text-align: right; padding-right: 6px; }
  .num { text-align: center; color: var(--muted); }
  .num.now { color: var(--accent); font-weight: 700; }
  .num.start { color: var(--text); font-weight: 600; }
  .grid { display: flex; flex-direction: column; gap: 8px; }
  .cell { height: 24px; padding: 0; font-size: 11px; border-radius: 2px; position: relative; overflow: hidden; }
  .note.off { color: var(--muted); }
  .note.now { outline: 2px solid var(--accent); outline-offset: -2px; }
  .cell.out, .num.out { opacity: 0.35; }
  .acc { display: block; width: 100%; height: 100%; background: var(--accent); }
  .gate { display: flex; align-items: stretch; }
  .len { display: block; height: 100%; background: var(--accent); opacity: 0.8; }
  .len.dim { background: var(--cell-off); }
  .tie { position: absolute; right: 1px; top: -3px; font-size: 14px; color: var(--text); }
</style>
