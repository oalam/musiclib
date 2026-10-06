<script lang="ts">
  import { tick, type Snippet } from 'svelte'
  import { api, chordAt, mmss, SEGMENT_COLORS, type Bank, type BankTrack, type Harmony, type ManualRef, type Pattern } from './api'
  import { CONTROLS, KNOBS, midiLabel, PARAM_PAGES, pagesOf, SILK, type Func, type Param } from './dt2'

  let { bank, harmony = null, currentTime, playing, player, onseek, onloop, onplay, onstop, onhelp }: {
    bank: Bank
    /** Gamme et accords du morceau (7.H), affiches en mode KEYBOARD. */
    harmony?: Harmony | null
    currentTime: number
    playing: boolean
    /** Lecteur rendu sous la facade, dans le meme bloc que la vue d'ensemble. */
    player?: Snippet
    onseek: (t: number) => void
    /** Boucle du lecteur sur une section (double-clic dans la chaine). */
    onloop: (start: number, end: number) => void
    onplay: () => void
    /** Arret et retour au debut du pattern en cours. */
    onstop: (t: number) => void
    /** Ouvre une fiche KB (chemin) ou, a defaut, le manuel a une page. */
    onhelp: (path?: string, page?: number) => void
  } = $props()

  let selectedSlot = $state(1)
  let follow = $state(true)

  const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
  const noteName = (n: number) => `${NOTE_NAMES[n % 12]}${Math.floor(n / 12) - 1}`

  // repli sans grille de mesures (ancienne bank) : tempo median, leger flottement
  // possible si le morceau accelere
  const stepDur = $derived(bank.bpm > 0 ? 60 / bank.bpm / 4 : 0)

  // section en cours (7.B2) ; repli sur les patterns pour les banks anterieures
  const sections = $derived(bank.sections ?? [])
  const playingSection = $derived(
    sections.find(s => currentTime >= s.start_s && currentTime < s.end_s) ?? null)
  const playingPattern = $derived(
    playingSection
      ? bank.patterns.find(p => p.slot === playingSection.pattern_slot) ?? null
      : bank.patterns.find(p => currentTime >= p.start_s && currentTime < p.end_s) ?? null)
  /** Debut du passage en cours du pattern (un slot peut etre joue plusieurs fois). */
  const playingStart = $derived(playingSection?.start_s ?? playingPattern?.start_s ?? 0)

  $effect(() => {
    if (follow && playingPattern) selectedSlot = playingPattern.slot
  })

  const pattern = $derived<Pattern>(
    bank.patterns.find(p => p.slot === selectedSlot) ?? bank.patterns[0])

  const bars = $derived(bank.bar_times_s ?? [])

  /** Index de la mesure contenant t (recherche dichotomique), -1 hors grille. */
  function barAt(t: number): number {
    if (bars.length < 2 || t < bars[0] || t >= bars[bars.length - 1]) return -1
    let lo = 0
    let hi = bars.length - 1
    while (hi - lo > 1) {
      const mid = (lo + hi) >> 1
      if (bars[mid] <= t) lo = mid
      else hi = mid
    }
    return lo
  }

  const currentStep = $derived.by(() => {
    if (!playingPattern || playingPattern.slot !== pattern.slot) return -1
    const spb = bank.steps_per_bar
    const b = barAt(currentTime)
    const b0 = barAt(playingStart + 0.01)
    if (b >= 0 && b0 >= 0) {
      // grille reelle (beats recales sur le kick) : pas de derive
      const frac = (currentTime - bars[b]) / (bars[b + 1] - bars[b])
      return ((b - b0) % pattern.bars) * spb + Math.min(spb - 1, Math.floor(frac * spb))
    }
    if (stepDur <= 0) return -1
    return Math.floor((currentTime - playingStart) / stepDur) % pattern.steps
  })

  const currentPhrase = $derived.by(() => {
    let idx = -1
    bank.mutes.forEach((ph, i) => { if (ph.start_s <= currentTime) idx = i })
    return idx
  })
  const liveActive = $derived(
    currentPhrase >= 0 && playingPattern?.slot === pattern.slot
      ? new Set(bank.mutes[currentPhrase].active) : null)

  const pages = $derived(Math.ceil(pattern.steps / 16))
  let page = $state(0)
  $effect(() => {
    // page courante qui suit le curseur, comme les LEDs de page de la DT
    if (follow && currentStep >= 0) page = Math.floor(currentStep / 16)
    else if (page >= pages) page = 0
  })
  const pageSteps = $derived([...Array(16).keys()].map(i => i + page * 16))

  // facade DT2 : une track a la fois sur les 16 trig keys
  type Mode = 'trig' | 'trk' | 'mute' | 'ptn' | 'kb'
  let mode = $state<Mode>('trig')
  let selectedTrack = $state(1)
  const track = $derived(pattern.tracks.find(t => t.index === selectedTrack) ?? pattern.tracks[0])

  // lettre de bank choisie pour ranger le morceau sur la machine (A01-P16),
  // memorisee par morceau ; un slot > 16 deborde sur la lettre suivante
  const BANKS = 'ABCDEFGHIJKLMNOP'
  let bankLetter = $state(0)
  $effect(() => {
    try { bankLetter = Number(localStorage.getItem(`dt-bank:${bank.slug}`) ?? 0) || 0 } catch { bankLetter = 0 }
  })
  function setBankLetter(i: number) {
    bankLetter = i
    try { localStorage.setItem(`dt-bank:${bank.slug}`, String(i)) } catch { /* stockage indisponible */ }
  }
  const patName = (slot: number) =>
    `${BANKS[(bankLetter + Math.floor((slot - 1) / 16)) % 16]}${String(((slot - 1) % 16) + 1).padStart(2, '0')}`

  // 7.H : mode KEYBOARD = gamme du morceau sur les trig keys, rangee basse en
  // touches blanches, rangee haute en noires (clavier chromatique, §8.5.1)
  const KB_LAYOUT = [null, 1, 3, null, 6, 8, 10, null, 0, 2, 4, 5, 7, 9, 11, 0]
  // miroir de analyzer/harmony.py CHORDS (intervalles par qualite)
  const CHORD_INTERVALS: Record<string, number[]> = {
    maj: [0, 4, 7], min: [0, 3, 7], sus2: [0, 2, 7], sus4: [0, 5, 7], dim: [0, 3, 6], '5': [0, 7],
  }
  const chord = $derived(harmony ? chordAt(harmony.chords, currentTime) : null)
  const scalePcs = $derived(new Set(harmony?.scale.notes.map(n => NOTE_NAMES.indexOf(n)) ?? []))
  const chordPcs = $derived(new Set(chord?.root != null && chord.quality
    ? (CHORD_INTERVALS[chord.quality] ?? []).map(i => (chord.root! + i) % 12) : []))
  const sectionChords = $derived(harmony?.progression.find(p => currentTime >= p.start_s && currentTime < p.end_s)?.chords ?? [])

  function trigAt(track: BankTrack, step: number) {
    return track.trigs.find(t => t.step === step)
  }

  /** Tracks jouees : etat live de la phrase, sinon tracks actives du pattern. */
  const unmuted = $derived(liveActive ?? new Set(pattern.tracks.filter(t => t.active).map(t => t.index)))

  /** Saut au debut du pas `step` du pattern selectionne (grille de mesures si dispo). */
  function seekStep(step: number) {
    const spb = bank.steps_per_bar
    const b0 = barAt(pattern.start_s + 0.01)
    const b = b0 + Math.floor(step / spb)
    if (b0 >= 0 && b + 1 < bars.length) {
      onseek(bars[b] + ((step % spb) / spb) * (bars[b + 1] - bars[b]))
    } else if (stepDur > 0) {
      onseek(pattern.start_s + step * stepDur)
    }
  }

  // 7.G : facade complete. Les controles qui ont un sens dans le front agissent,
  // les autres affichent leur legende ; en mode AIDE, un clic ouvre la fiche.
  let func = $state(false)
  let help = $state(false)
  // legende : le clic epingle un controle (focus), le survol n'en montre qu'un
  // apercu, apres un court delai et efface en sortie, pour pouvoir traverser la
  // facade jusqu'aux liens sans perdre le controle epingle
  type Focus = { id: string; param?: number }
  let focus = $state<Focus>({ id: 'screen' })
  let hover = $state<Focus | null>(null)
  let hoverTimer: ReturnType<typeof setTimeout> | undefined
  const shown = $derived(hover ?? focus)
  function peek(f: Focus) {
    clearTimeout(hoverTimer)
    hoverTimer = setTimeout(() => (hover = f), 120)
  }
  function unpeek() {
    clearTimeout(hoverTimer)
    hover = null
  }
  let pageId = $state('trig1')
  let lastStep = $state(-1)
  let outline = $state<Record<string, ManualRef>>({})
  api.manualOutline().then(o => (outline = o)).catch(() => { /* manuel absent : liens masques */ })

  /** Boite centree en (cx, cy), w x h, en unites du dessin du §3.1 (834 x 682) -> % du panneau. */
  const at = (cx: number, cy: number, w: number, h = w) =>
    `left: ${((cx - w / 2) / 834) * 100}%; top: ${((cy - h / 2) / 682) * 100}%; ` +
    `width: ${(w / 834) * 100}%; height: ${(h / 682) * 100}%`

  const paramPage = $derived(PARAM_PAGES.find(pg => pg.id === pageId) ?? PARAM_PAGES[0])
  const focused = $derived(CONTROLS[shown.id])
  const focusedParam = $derived(shown.param !== undefined ? paramPage.params[shown.param] : null)
  /** Fonction montree par la legende : secondaire quand FUNC est allume. */
  const shownFunc = $derived<Func>(func && focused.func ? focused.func : focused.main)

  // valeurs connues de la bank : note et velocite du trig sous le curseur (page TRIG 1)
  const valueTrig = $derived(trigAt(track, currentStep >= 0 ? currentStep : lastStep))
  function paramValue(param: Param | null): number | null {
    if (pageId !== 'trig1' || !param || !valueTrig) return null
    if (param.key === 'VEL') return valueTrig.velocity
    if (param.key === 'NOTE') return valueTrig.note
    return null
  }
  const shownValue = (param: Param | null, v: number | null) =>
    v === null ? '--' : param?.key === 'NOTE' ? noteName(v) : String(v)

  const manualRef = (f: { manual?: string }) => (f.manual ? outline[f.manual] : undefined)

  function openDoc(f: Func | { kb?: string; manual?: string }) {
    const ref = manualRef(f)
    if (f.kb) onhelp(f.kb)
    else if (ref) onhelp(undefined, ref.page)
  }

  /** Appui sur un controle : legende, puis fiche (mode AIDE) ou action (primaire / FUNC). */
  function act(id: string, primary?: () => void, secondary?: () => void) {
    focus = { id }
    const c = CONTROLS[id]
    if (help) { openDoc(func && c.func ? c.func : c.main); func = false; return }
    if (id === 'func') { func = !func; return }
    if (func) { secondary?.(); func = false }
    else primary?.()
  }

  function pressParamKey(key: string) {
    const pgs = pagesOf(key)
    const i = pgs.findIndex(pg => pg.id === pageId)
    pageId = pgs[(i + 1) % pgs.length].id  // appuis successifs = page suivante
    mode = 'trig'
  }

  function pressKnob(i: number) {
    focus = { id: 'knobs', param: i }
    if (help) openDoc(paramPage)
  }

  function pressArrow(dir: -1 | 1) {
    // [PTN] + [LEFT]/[RIGHT] change de bank, comme sur la machine
    if (mode === 'ptn') setBankLetter((bankLetter + dir + 16) % 16)
  }

  // vue d'ensemble : quand le curseur sort de la partie visible, la grille defile
  // jusqu'a la mesure en cours (calee a gauche) ; seulement en FOLLOW
  let gridWrap: HTMLDivElement | undefined = $state()
  $effect(() => {
    const step = currentStep
    if (!follow || step < 0 || !gridWrap) return
    const wrap = gridWrap
    const barStep = step - (step % bank.steps_per_bar)
    tick().then(() => {
      const cell = wrap.querySelector<HTMLElement>(`.cell[data-s="${step}"]`)
      const bar = wrap.querySelector<HTMLElement>(`.cell[data-s="${barStep}"]`)
      const label = wrap.querySelector<HTMLElement>('.label')
      if (!cell || !bar || !label) return
      const left = wrap.scrollLeft + label.offsetWidth
      const right = wrap.scrollLeft + wrap.clientWidth
      if (cell.offsetLeft < left || cell.offsetLeft + cell.offsetWidth > right) {
        wrap.scrollTo({ left: bar.offsetLeft - label.offsetWidth, behavior: 'smooth' })
      }
    })
  })

  // onglets sous le lecteur : vue d'ensemble ou partition de mutes (memorise)
  let tab = $state<'grid' | 'mutes'>('grid')
  try { if (localStorage.getItem('ui:bank-tab') === 'mutes') tab = 'mutes' } catch { /* stockage indisponible */ }
  function setTab(t: 'grid' | 'mutes') {
    tab = t
    try { localStorage.setItem('ui:bank-tab', t) } catch { /* stockage indisponible */ }
  }

  function pressKey(i: number) {
    if (help) { act('trigs'); return }
    focus = { id: 'trigs' }
    if (func || mode === 'kb') { func = false; return }  // QUICK MUTE / clavier : legende seule : legende seule, les mutes viennent de la bank
    if (mode === 'trig') { if (page * 16 + i < pattern.steps) { lastStep = page * 16 + i; seekStep(lastStep) } }
    else if (mode === 'trk') { selectedTrack = i + 1; mode = 'trig' }  // comme relacher TRK
    else if (mode === 'mute') selectedTrack = i + 1
    else {
      const p = bank.patterns.find(p => p.slot === i + 1)
      if (p) { selectedSlot = p.slot; follow = false; onseek(p.start_s) }
    }
  }
</script>

<section class="bank">
  {#snippet glyph(name: string)}
    <svg class="glyph" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
      {#if name === 'preset'}<path d="M5 7h9M5 11h9M5 15h5M18 5v10" /><circle cx="16" cy="16" r="2" />
      {:else if name === 'settings'}<circle cx="12" cy="12" r="6.5" stroke-width="3" stroke-dasharray="2.2 1.9" /><circle cx="12" cy="12" r="2.5" />
      {:else if name === 'sampling'}<path d="M4 10v4M7 7v10M10 9v6M13 5v14M16 8v8M19 10v4" />
      {:else if name === 'tempo'}<path d="M7 20h10L13.5 5h-3zM12 15l5-8" />
      {:else if name === 'keyboard'}<rect x="4" y="5" width="16" height="14" rx="1" /><path d="M8 5v8M12 5v8M16 5v8M8 13v6M12 13v6M16 13v6" stroke-width="2.6" />
      {:else if name === 'record'}<circle cx="12" cy="12" r="6.5" />
      {:else if name === 'play'}<path d="M8 5.5v13l10-6.5z" />
      {:else if name === 'stop'}<rect x="6" y="6" width="12" height="12" rx="1" />
      {:else if name === 'up'}<path d="M7 16l5-9 5 9" />
      {:else if name === 'down'}<path d="M7 8l5 9 5-9" />
      {:else if name === 'left'}<path d="M16 6l-8 6 8 6" />
      {:else if name === 'right'}<path d="M8 6l8 6-8 6" />{/if}
    </svg>
  {/snippet}
  {#snippet hw(id: string, box: [number, number, number, number], o: { primary?: () => void; secondary?: () => void; lit?: boolean; icon?: string; silk?: string; label?: string; cls?: string } = {})}
    {@const c = CONTROLS[id]}
    {@const silk = o.silk ?? SILK[id]}
    <button class="hw {o.cls ?? ''}" class:lit={o.lit} class:hasfunc={!!c.func} class:sel={focus.id === id && focus.param === undefined}
      class:icon={!!o.icon} style={at(...box)} aria-label={o.label ?? c.label}
      onmouseenter={() => peek({ id })} onmouseleave={unpeek} onclick={() => act(id, o.primary, o.secondary)}>
      {#if o.icon}{@render glyph(o.icon)}{:else}<span class="kl">{c.label}</span>{/if}
      {#if silk}<span class="sub">{silk}</span>{/if}
    </button>
  {/snippet}
  {#snippet knob(box: [number, number, number], label: string, value: number | null, onclick: () => void, onenter: () => void, sel: boolean, sub = '')}
    <button class="knob" class:sel class:known={value !== null} style="{at(...box)}; --a: {value === null ? 0 : -135 + (270 * value) / 127}deg"
      aria-label={label} onmouseenter={onenter} onmouseleave={unpeek} {onclick}>
      <span class="cap"></span><span class="klabel">{label}{#if sub}<span class="sub2">{sub}</span>{/if}</span>
    </button>
  {/snippet}

  <div class="cols">
  <div class="col-dt">
  <div class="fronttools">
    <button class="small" class:on={help} title="Mode aide : un clic sur un contrôle ouvre sa fiche ou le manuel"
      onclick={() => (help = !help)}>Aide ?</button>
    <button class="small" class:on={follow} title="Spécifique au front : la page et le pattern suivent la lecture"
      onclick={() => (follow = !follow)}>Follow</button>
  </div>

  <!-- implantation et echelle reprises du dessin du §3.1 (panneau de 834 x 682 unites) -->
  <div class="dt" class:funcmode={func} class:helpmode={help} aria-label="Façade Digitakt II">
    <div class="ports" aria-hidden="true">
      {#each [[60, 'Phones'], [135, 'L · Out · R'], [250, 'L · In · R'], [349, 'MIDI In'], [427, 'MIDI Out'], [504, 'MIDI Thru'], [589, 'USB'], [663, 'DC In'], [748, 'Power']] as [x, t]}
        <span style="left: {(Number(x) / 834) * 100}%">{t}</span>
      {/each}
    </div>

    {@render knob([68, 126, 52], 'Main Volume', null, () => act('volume'), () => peek({ id: 'volume' }), focus.id === 'volume')}
    {@render knob([68, 223, 52], 'Level/Data', null, () => act('level'), () => peek({ id: 'level' }), focus.id === 'level', SILK.level)}

    <div class="bezel" style={at(264, 184, 284, 196)}><span class="brand">Digitakt II</span></div>
    <div class="screen mono" role="presentation" style={at(263.5, 175, 237, 130)}
      onmouseenter={() => peek({ id: 'screen' })} onmouseleave={unpeek}>
        <div class="bar">
          <span class="tag">{patName(pattern.slot)}</span>
          <span class="name">{pattern.label.toUpperCase()}</span>
          <span class="bpm">{playing ? '▶' : '■'} ♩{bank.bpm.toFixed(1)}</span>
        </div>
        {#if mode === 'trig'}
          <div class="row big">T{String(track.index).padStart(2, '0')} {track.role.toUpperCase()} <span class="pgt">{paramPage.title}</span></div>
          <div class="params">
            {#each paramPage.params as param, i}
              <span class:hl={shown.id === 'knobs' && shown.param === i}>
                <b>{param?.key ?? '·'}</b>{param ? shownValue(param, paramValue(param)) : ''}
              </span>
            {/each}
          </div>
          <div class="row dim">PAGE {page + 1}:{pages} · STEP {currentStep >= 0 ? String(currentStep + 1).padStart(3, '0') : lastStep >= 0 ? String(lastStep + 1).padStart(3, '0') : '---'} · {track.trigs.length} TRIGS · x{pattern.repeats}</div>
        {:else if mode === 'trk'}
          <div class="row big">TRACK</div>
          <div class="row">CHOISIR UNE TRACK (1-16)</div>
          <div class="row dim">ACTUELLE T{String(track.index).padStart(2, '0')} {track.role.toUpperCase()}</div>
        {:else if mode === 'mute'}
          <div class="row big">MUTE MODE</div>
          <div class="row">{unmuted.size}/16 TRACKS ACTIVES</div>
          <div class="row dim">{currentPhrase >= 0 && liveActive ? `PHRASE ${currentPhrase + 1}/${bank.mutes.length}` : 'ETAT DU PATTERN'}</div>
        {:else if mode === 'kb'}
          <div class="row big">KB SETUP <span class="pgt">§8.5.2</span></div>
          {#if harmony}
            <div class="row">SCALE {harmony.scale.scale}</div>
            <div class="row">ROOT {harmony.scale.root_name}{harmony.scale.uncertain ? ' ? INCERTAINE' : ''} <span class="dim">· {harmony.scale.notes.join(' ')}</span></div>
            <div class="row dim">{chord && chord.label !== 'N' ? `ACCORD ${chord.label} · MES ${chord.bar + 1}` : 'ACCORD --'}{sectionChords.length ? ` · ${sectionChords.join(' ')}` : ''}</div>
          {:else}
            <div class="row">PAS D'ANALYSE HARMONIQUE</div>
            <div class="row dim">python harmony.py {bank.slug}</div>
          {/if}
        {:else}
          <div class="row big">BANK {BANKS[bankLetter]} <span class="pgt">◀ ▶ = BANK</span></div>
          <div class="row">{bank.patterns.length} PATTERNS · {playingPattern ? `PLAY ${patName(playingPattern.slot)}` : 'STOP'}</div>
          <div class="banks" aria-label="Lettre de bank">
            {#each BANKS as l, i}
              <button class:sel={bankLetter === i} onclick={() => setBankLetter(i)}>{l}</button>
            {/each}
          </div>
        {/if}
        <div class="row dim foot">{bank.from_stems ? 'STEMS' : 'MIX'} · {pattern.bars} BAR{pattern.bars > 1 ? 'S' : ''} · {mmss(pattern.start_s)}-{mmss(pattern.end_s)} · {mmss(currentTime)}</div>
    </div>

    {#each KNOBS as k, i}
      {@const param = paramPage.params[i]}
      {@render knob([460 + 102 * (i % 4), i < 4 ? 126 : 223, 50], k, paramValue(param), () => pressKnob(i),
        () => peek({ id: 'knobs', param: i }), focus.id === 'knobs' && focus.param === i)}
    {/each}
    {#each ['p-trig', 'p-src', 'p-fltr', 'p-amp', 'p-fx', 'p-mod'] as id, i}
      {@render hw(id, [458 + 62 * i, 308, 44, 44], { primary: () => pressParamKey(id), lit: paramPage.key === id })}
    {/each}

    {@render hw('func', [78, 349, 68, 42], { lit: func, cls: 'func' })}
    {#each [['preset', 170], ['settings', 233], ['sampling', 295], ['tempo', 358]] as [id, x]}
      {@render hw(String(id), [Number(x), 349, 44, 44], { icon: String(id) })}
    {/each}

    {@render hw('keyboard', [78, 410, 44, 44], { icon: 'keyboard', primary: () => (mode = mode === 'kb' ? 'trig' : 'kb'),
      secondary: () => (mode = 'kb'), lit: mode === 'kb' })}
    {@render hw('record', [182, 411, 68, 42], { icon: 'record' })}
    {@render hw('play', [264, 411, 68, 42], { icon: 'play', primary: onplay, lit: playing })}
    {@render hw('stop', [346, 411, 68, 42], { icon: 'stop', primary: () => onstop(playingStart) })}

    {@render hw('yes', [458, 380, 44, 44])}
    {@render hw('no', [458, 442, 44, 44])}

    {@render hw('arrows', [582, 380, 44, 44], { icon: 'up', silk: 'Trig Mode', label: 'UP' })}
    <span class="silk" style="left: {(612 / 834) * 100}%; top: {(374 / 682) * 100}%">↕ KB Octave</span>
    {@render hw('arrows', [520, 442, 44, 44], { icon: 'left', silk: 'µTime−', label: 'LEFT', primary: () => pressArrow(-1) })}
    {@render hw('arrows', [582, 442, 44, 44], { icon: 'down', silk: 'Trig Mode', label: 'DOWN' })}
    {@render hw('arrows', [645, 442, 44, 44], { icon: 'right', silk: 'µTime+', label: 'RIGHT', primary: () => pressArrow(1) })}

    {#each Array(8) as _, i}
      <button class="led" class:lit={page === i} class:play={page !== i && currentStep >= 0 && Math.floor(currentStep / 16) === i}
        style={at(722 + 23 * (i % 4), i < 4 ? 372 : 395, 13)} disabled={i >= pages} aria-label="page {i + 1}"
        onmouseenter={() => peek({ id: 'leds' })} onmouseleave={unpeek}
        onclick={() => act('leds', () => { page = i; follow = false })}></button>
    {/each}
    {@render hw('page', [756, 442, 68, 42], { primary: () => { page = (page + 1) % pages; follow = false } })}

    {@render hw('trk', [78, 481, 68, 42], { primary: () => (mode = mode === 'trk' ? 'trig' : 'trk'),
      secondary: () => (mode = mode === 'mute' ? 'trig' : 'mute'), lit: mode === 'trk' || mode === 'mute' })}
    {@render hw('ptn', [78, 547, 68, 42], { primary: () => (mode = mode === 'ptn' ? 'trig' : 'ptn'),
      secondary: () => (mode = 'ptn'), lit: mode === 'ptn' })}
    {@render hw('song', [78, 612, 68, 42])}

    <span class="silk tm" style="left: {(469 / 834) * 100}%; top: {(568 / 682) * 100}%">
      <i>⋮·······</i> Track/Mute <i>·······⋮</i></span>
    {#each Array(16) as _, i}
      {@const box = at(182 + 82 * (i % 8), i < 8 ? 524 : 611, 68)}
      {#if mode === 'trig'}
        {@const s = page * 16 + i}
        {@const trig = s < pattern.steps ? trigAt(track, s) : undefined}
        <button class="key" class:beat={i % 4 === 0} class:off={s >= pattern.steps} class:red={!!trig} class:cursor={s === currentStep}
          style="{box}{trig ? `; --v: ${0.45 + (0.55 * trig.velocity) / 127}` : ''}"
          title={trig ? `pas ${s + 1} · vel ${trig.velocity}${trig.note !== null ? ' · ' + noteName(trig.note) : ''}` : `pas ${s + 1}`}
          onmouseenter={() => peek({ id: 'trigs' })} onmouseleave={unpeek} onclick={() => pressKey(i)}>
          <span class="n">{i + 1}</span>
          {#if trig && trig.note !== null && track.index > 8}<span class="note">{noteName(trig.note)}</span>{/if}
        </button>
      {:else if mode === 'trk' || mode === 'mute'}
        {@const t = pattern.tracks.find(t => t.index === i + 1)}
        <button class="key" class:beat={i % 4 === 0} class:off={!t?.trigs.length}
          class:red={mode === 'trk' && track.index === i + 1} class:green={mode === 'mute' && !!t?.trigs.length && unmuted.has(i + 1)}
          style={box} title="{i + 1} {t?.role ?? ''}"
          onmouseenter={() => peek({ id: 'trigs' })} onmouseleave={unpeek} onclick={() => pressKey(i)}>
          <span class="n">{i + 1}</span><span class="note">{t?.role ?? ''}</span>
        </button>
      {:else if mode === 'kb'}
        {@const pc = KB_LAYOUT[i]}
        <button class="key" class:off={pc === null || !scalePcs.has(pc)} class:white={pc !== null && scalePcs.has(pc)}
          class:red={pc !== null && pc === harmony?.scale.root} class:green={pc !== null && chordPcs.has(pc) && pc !== harmony?.scale.root}
          style={box} title={pc === null ? '' : `${NOTE_NAMES[pc]}${scalePcs.has(pc) ? ' · dans la gamme' : ''}${chordPcs.has(pc) ? ' · accord en cours' : ''}`}
          onmouseenter={() => peek({ id: 'trigs' })} onmouseleave={unpeek} onclick={() => pressKey(i)}>
          <span class="n">{i + 1}</span>{#if pc !== null}<span class="note">{NOTE_NAMES[pc]}</span>{/if}
        </button>
      {:else}
        {@const p = bank.patterns.find(p => p.slot === i + 1)}
        <button class="key" class:beat={i % 4 === 0} class:off={!p} class:white={!!p} class:red={p?.slot === pattern.slot}
          class:blink={playingPattern?.slot === i + 1} style={box}
          title={p ? `${patName(p.slot)} · ${p.label} · ${mmss(p.start_s)}` : ''}
          onmouseenter={() => peek({ id: 'trigs' })} onmouseleave={unpeek} onclick={() => pressKey(i)}>
          <span class="n">{i + 1}</span>{#if p}<span class="note">{p.label}</span>{/if}
        </button>
      {/if}
    {/each}
  </div>

  <div class="legend" aria-live="polite">
    {#if focusedParam !== null && shown.param !== undefined}
      {@const ref = manualRef(paramPage)}
      <div class="lh"><span class="kbd mono">{KNOBS[shown.param]}</span> <b>{focusedParam.key}</b> · {focusedParam.name}
        <span class="muted">· page {paramPage.title}</span></div>
      <div class="ltext mono">{midiLabel(focusedParam)} <span class="muted">· canal de la track</span></div>
      {#if paramPage.note}<div class="muted small">{paramPage.note}</div>{/if}
      <div class="links">
        <button class="small" onclick={() => onhelp(paramPage.kb)}>Fiche</button>
        {#if ref}<button class="small" onclick={() => onhelp(undefined, ref.page)}>Manuel §{ref.section} p{ref.page}</button>{/if}
      </div>
    {:else if shown.param !== undefined}
      <div class="lh"><span class="kbd mono">{KNOBS[shown.param]}</span> <span class="muted">sans paramètre sur la page {paramPage.title}</span></div>
    {:else}
      <div class="lh"><span class="kbd mono">[{focused.label}]</span> <b>{shownFunc.label}</b>
        <span class="muted">· n°{focused.ref} du §3.1{func && focused.func ? ' · fonction FUNC' : ''}</span></div>
      <div class="ltext">{shownFunc.text}</div>
      {#if focused.func && !func}<div class="small"><span class="fn">FUNC</span> {focused.func.label} : {focused.func.text}</div>{/if}
      <div class="links">
        {#if shownFunc.kb}<button class="small" onclick={() => onhelp(shownFunc.kb)}>Fiche</button>{/if}
        {#if manualRef(shownFunc)}
          {@const ref = manualRef(shownFunc)!}
          <button class="small" onclick={() => onhelp(undefined, ref.page)}>Manuel §{ref.section} p{ref.page}</button>
        {/if}
      </div>
    {/if}
    <div class="muted small hint">{hover ? 'Aperçu : clic pour épingler la légende.' : 'Épinglé : la légende reste en traversant la façade.'}
      {help ? 'AIDE active : un clic ouvre la fiche (ou le manuel).' : 'FUNC puis une touche = fonction secondaire ; AIDE ? = clic vers la fiche.'}</div>
  </div>

  </div>

  <div class="col-rest">
  <div class="deck">
  {@render player?.()}
  {#if sections.length}
    <div class="chain" aria-label="Ordre de jeu">
      <span class="muted small" title="Clic = saut, double-clic = boucle sur la section">Chaîne</span>
      {#each sections as s (s.index)}
        <button class="link mono" class:cur={playingSection?.index === s.index}
          style="--c: {SEGMENT_COLORS[s.label] ?? '#888888'}"
          title="{s.label} · {mmss(s.start_s)} · {s.bars} mes. · tracks {s.active.join(' ')} · double-clic = boucle"
          onclick={() => { selectedSlot = s.pattern_slot; onseek(s.start_s) }}
          ondblclick={() => onloop(s.start_s, s.end_s)}>
          {patName(s.pattern_slot)}
        </button>
      {/each}
    </div>
  {/if}

  <div class="tabs" role="tablist" aria-label="Vue de la bank">
    <button role="tab" aria-selected={tab === 'grid'} class:on={tab === 'grid'} onclick={() => setTab('grid')}>
      Vue d'ensemble <span class="muted small">{patName(pattern.slot)} · {pattern.bars} mesure{pattern.bars > 1 ? 's' : ''} · joué ×{pattern.repeats}</span>
    </button>
    <button role="tab" aria-selected={tab === 'mutes'} class:on={tab === 'mutes'} onclick={() => setTab('mutes')}>
      Mutes <span class="muted small">{bank.mutes.length} phrases × {bank.phrase_bars} mes.</span>
    </button>
  </div>
  {#if tab === 'grid'}
  <p class="muted small hint">16 tracks × {pattern.steps} pas · clic sur une track = sélection</p>
  <div class="grid-wrap" bind:this={gridWrap}>
    <div class="grid" style="--cols: {pattern.steps}">
      {#each pattern.tracks as t (t.index)}
        {@const muted = liveActive !== null && t.trigs.length > 0 && !liveActive.has(t.index)}
        <button class="label" class:empty={!t.trigs.length} class:muted class:sel={t.index === track.index}
          title={t.source} onclick={() => (selectedTrack = t.index)}>
          <span class="idx mono" class:melodic={t.index > 8}>{t.index}</span> {t.role}
          {#if muted}<span class="m">M</span>{/if}
        </button>
        {#each Array(pattern.steps) as _, s}
          {@const trig = trigAt(t, s)}
          <div class="cell" data-s={s} class:beat={s % 4 === 0} class:pagestart={s % 16 === 0 && s > 0}
            class:cursor={s === currentStep} class:melodic={t.index > 8} class:muted
            class:trig={!!trig}
            style={trig ? `--v: ${0.35 + (0.65 * trig.velocity) / 127}` : ''}
            title={trig ? `pas ${s + 1} · vel ${trig.velocity}${trig.note !== null ? ' · ' + noteName(trig.note) : ''}` : ''}>
          </div>
        {/each}
      {/each}
    </div>
  </div>
  {:else}
  <p class="muted small hint">Clic = saut à la phrase</p>
  <div class="mutes-wrap">
    <div class="mutes" style="--n: {bank.mutes.length}">
      {#each Array(16) as _, row}
        <div class="mlabel mono" class:melodic={row >= 8}>{row + 1}</div>
        {#each bank.mutes as ph, i}
          <button class="mcell" class:on={ph.active.includes(row + 1)} class:melodic={row >= 8}
            class:cur={i === currentPhrase} class:newpat={i > 0 && bank.mutes[i - 1].pattern_slot !== ph.pattern_slot}
            title="{mmss(ph.start_s)} · pattern {patName(ph.pattern_slot)}" aria-label="phrase {mmss(ph.start_s)} track {row + 1}"
            onclick={() => onseek(ph.start_s)}></button>
        {/each}
      {/each}
    </div>
  </div>
  {/if}
  </div>
  </div>
  </div>
</section>

<style>
  /* empile par defaut ; deux colonnes quand la place le permet (liste des morceaux
     repliee ou grand ecran) : DT2 figee a gauche, a la hauteur de l'ecran, le reste a droite */
  .bank { padding: 12px 16px; container-type: inline-size; }
  .cols { display: flex; flex-direction: column; align-items: center; }
  .col-dt, .col-rest { width: 100%; max-width: 900px; box-sizing: border-box; }
  .col-rest > * { max-width: 100%; }
  @container (min-width: 1150px) {
    .cols { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr); gap: 20px; align-items: start; }
    .col-dt { position: sticky; top: 0; max-width: calc((100vh - 260px) * 834 / 682); justify-self: end; }
    .col-rest { max-width: none; }
    .col-rest .deck { margin-top: 0; }
  }
  .deck { margin-top: 14px; border: 1px solid var(--border); border-radius: 6px; background: var(--panel); padding: 0 12px 12px; }
  .deck .chain { margin-top: 10px; }
  .deck :global(.player) { border-bottom: 0; background: none; padding: 12px 0 0; }
  .chain { display: flex; gap: 3px; flex-wrap: wrap; align-items: center; margin: 10px 0 6px; }
  .chain .link { font-size: 11px; padding: 2px 5px; border-bottom: 3px solid var(--c); }
  .chain .link.cur { outline: 1px solid var(--accent); }
  .small { font-size: 12px; }
  .tabs { display: flex; gap: 4px; margin: 14px 0 6px; border-bottom: 1px solid var(--border); overflow-x: auto; }
  .tabs button {
    font-size: 14px; font-weight: 600; padding: 6px 10px; background: none; border: 0;
    border-bottom: 2px solid transparent; border-radius: 0; margin-bottom: -1px; cursor: pointer; white-space: nowrap;
  }
  .tabs button.on { background: none; color: var(--text); border-bottom-color: var(--accent); }
  .tabs .small { font-weight: 400; margin-left: 4px; }
  .hint { margin: 0 0 6px; }

  /* facade DT2 : toujours sombre, comme la machine, quel que soit le theme.
     Implantation absolue au dessin du §3.1 ; --u = 1 unite du dessin (834 de large). */
  .fronttools { display: flex; gap: 6px; max-width: 900px; margin-bottom: 6px; }
  .fronttools .on { outline: 2px solid var(--accent); }
  .dt {
    --face: #1c1c1c; --key-edge: #0a0a0a; --silk: #d8d8d4; --func: #e9a23b; --func-key: #f5c518;
    --led-red: #ff3b3b; --led-green: #4cff6a; --lcd: #9fd0ff; --lcd-bg: #07142a;
    container-type: inline-size;
    position: relative; width: 100%; max-width: 900px; aspect-ratio: 834 / 682;
    background: linear-gradient(#272727, var(--face));
    border: 1px solid #000; border-radius: 1.4%;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
    color: var(--silk);
  }
  .dt > * { position: absolute; box-sizing: border-box; }
  .dt { --u: calc(100cqw / 834); }
  .dt button { font: inherit; color: inherit; }
  .ports { left: 0; right: 0; top: calc(var(--u) * 8); height: 0; }
  .ports span { position: absolute; transform: translateX(-50%); font-size: calc(var(--u) * 8); color: #8a8a86; white-space: nowrap; }
  .silk { font-size: calc(var(--u) * 9.5); color: #9a9a96; white-space: nowrap; transform: translateY(-50%); }
  .silk.tm { transform: translate(-50%, -50%); color: var(--silk); }
  .silk.tm i { font-style: normal; color: #6a6a66; letter-spacing: 0.1em; }

  .bezel { background: #0d0d0d; border-radius: calc(var(--u) * 3); }
  .brand { position: absolute; left: calc(var(--u) * 23); bottom: calc(var(--u) * 10); font: 700 calc(var(--u) * 19) / 1 system-ui, sans-serif; color: #f2f2ee; letter-spacing: -0.02em; }

  /* ecran : fond bleu nuit, bandeau inverse en tete comme l'UI du DT2 */
  .screen {
    background: var(--lcd-bg); box-shadow: inset 0 0 0 1px #24324a; padding: calc(var(--u) * 5) calc(var(--u) * 6);
    color: var(--lcd); font-size: calc(var(--u) * 9.5); line-height: 1.45; overflow: hidden;
  }
  .bar { display: flex; align-items: center; gap: calc(var(--u) * 4); background: var(--lcd); color: var(--lcd-bg); padding: 0 calc(var(--u) * 3); font-weight: 700; margin-bottom: calc(var(--u) * 3); }
  .bar .tag { border: 1px solid var(--lcd-bg); padding: 0 calc(var(--u) * 2); font-size: calc(var(--u) * 8); }
  .bar .name { font-size: calc(var(--u) * 12); letter-spacing: 0.03em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .bar .bpm { margin-left: auto; font-size: calc(var(--u) * 9); }
  .screen .row { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .screen .big { font-size: calc(var(--u) * 12.5); font-weight: 700; }
  .screen .dim { opacity: 0.6; }
  .screen .foot { font-size: calc(var(--u) * 8); margin-top: calc(var(--u) * 1); }
  .screen .pgt { float: right; font-size: calc(var(--u) * 8.5); font-weight: 400; opacity: 0.8; }
  .banks { display: grid; grid-template-columns: repeat(16, 1fr); gap: 1px; margin: 1px 0; }
  .banks button { all: unset; cursor: pointer; text-align: center; font-size: calc(var(--u) * 8); border: 1px solid #24324a; }
  .banks button.sel { background: var(--lcd); color: var(--lcd-bg); }
  .params { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0 calc(var(--u) * 4); font-size: calc(var(--u) * 9); }
  .params span { white-space: nowrap; overflow: hidden; }
  .params b { font-weight: 400; opacity: 0.6; margin-right: calc(var(--u) * 3); }
  .params .hl { background: var(--lcd); color: var(--lcd-bg); }

  /* potards : capuchon qui tourne, trait = position (en haut si valeur inconnue) */
  .knob { padding: 0; border: 0; background: none; cursor: pointer; overflow: visible; }
  .knob .cap {
    position: absolute; inset: 0; border-radius: 50%; transform: rotate(var(--a));
    background: radial-gradient(circle, #3c3c3a 0, #262625 60%, #141414 100%);
    border: 1px solid #000; box-shadow: 0 calc(var(--u) * 2.5) 0 #000;
  }
  .knob .cap::after {
    content: ''; position: absolute; left: 50%; top: 7%; width: 6%; height: 28%; margin-left: -3%;
    background: #8a8a86; border-radius: 1px;
  }
  .knob.known .cap::after { background: #fff; }
  .knob.sel .cap, .knob:hover .cap { border-color: #888; }
  .klabel {
    position: absolute; top: calc(100% + var(--u) * 4); left: 50%; transform: translateX(-50%);
    font-size: calc(var(--u) * 9.5); white-space: nowrap; text-align: center; line-height: 1.25;
  }
  .knob.sel .klabel { color: #fff; }
  .sub2 { display: block; color: var(--func); }

  .hw {
    padding: 0; display: flex; align-items: center; justify-content: center; overflow: visible;
    font-size: calc(var(--u) * 9.5) !important; letter-spacing: 0.02em; color: #c8c8c4 !important;
    background: linear-gradient(#323232, #232323); border: 1px solid var(--key-edge); border-radius: calc(var(--u) * 7);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 calc(var(--u) * 2.5) 0 #000;
  }
  .hw .glyph { width: 52%; height: 52%; }
  .hw .sub {
    position: absolute; top: calc(100% + var(--u) * 4); left: 50%; transform: translateX(-50%);
    font-size: calc(var(--u) * 9); color: var(--func); white-space: nowrap; letter-spacing: 0;
  }
  .hw.lit { color: #fff !important; box-shadow: inset 0 calc(var(--u) * -3) 0 var(--led-red), 0 calc(var(--u) * 2.5) 0 #000; }
  .hw.sel { border-color: #888; }
  /* FUNC : touche a serigraphie jaune, comme les fonctions secondaires */
  .hw.func { color: var(--func-key) !important; }
  .hw.func.lit { box-shadow: inset 0 calc(var(--u) * -3) 0 var(--func-key), 0 0 10px rgba(245, 197, 24, 0.35), 0 calc(var(--u) * 2.5) 0 #000; }
  .hw:hover, .key:hover, .led:hover:not(:disabled) { border-color: #666; }
  .funcmode .hw.hasfunc .sub { color: #ffc46b; text-shadow: 0 0 6px rgba(233, 162, 59, 0.6); }
  .funcmode .hw:not(.hasfunc):not(.lit) { opacity: 0.55; }
  .helpmode .hw, .helpmode .knob, .helpmode .key { cursor: help; }

  .led { padding: 0; border-radius: 50%; background: #6a6a66; border: 1px solid #000; box-shadow: inset 0 -1px 2px rgba(0, 0, 0, 0.4); }
  .led:disabled { opacity: 0.3; cursor: default; }
  .led.play { background: #2f7a3b; }
  .led.lit { background: var(--led-green); box-shadow: 0 0 8px var(--led-green); }

  /* 16 trig keys : chiffre souligne, cadre sur 1 / 5 / 9 / 13, LED = contour + chiffre */
  .key {
    padding: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;
    background: linear-gradient(#2e2e2e, #1f1f1f); border: 1px solid var(--key-edge); border-radius: calc(var(--u) * 7);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.07), 0 calc(var(--u) * 3) 0 #000;
  }
  .key.beat::before {
    content: ''; position: absolute; inset: 20%; border: calc(var(--u) * 1.5) solid #8a8a86; border-radius: calc(var(--u) * 2); pointer-events: none;
  }
  .key .n {
    font-size: calc(var(--u) * 21); line-height: 1; color: #d8d8d4;
    border-bottom: calc(var(--u) * 2) solid currentColor; padding-bottom: calc(var(--u) * 1.5);
  }
  .key .note { position: absolute; bottom: calc(var(--u) * 3); left: 2px; right: 2px; font-size: calc(var(--u) * 8); color: #9a9a96;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: center; }
  .key.off .n { opacity: 0.35; }
  .key.white .n { color: #fff; }
  .key.red {
    box-shadow: inset 0 0 0 calc(var(--u) * 3) #111, inset 0 0 0 calc(var(--u) * 5) rgba(255, 59, 59, var(--v, 1)), 0 0 10px rgba(255, 59, 59, calc(var(--v, 1) * 0.35)), 0 calc(var(--u) * 3) 0 #000;
  }
  .key.red .n { color: var(--led-red); text-shadow: 0 0 6px rgba(255, 59, 59, 0.6); }
  .key.green { box-shadow: inset 0 0 0 calc(var(--u) * 3) #111, inset 0 0 0 calc(var(--u) * 5) var(--led-green), 0 0 10px rgba(76, 255, 106, 0.3), 0 calc(var(--u) * 3) 0 #000; }
  .key.green .n { color: var(--led-green); }
  .key.cursor { background: linear-gradient(#5a5a56, #444); }
  .key.blink { animation: blink 0.5s steps(1) infinite; }
  @keyframes blink { 50% { box-shadow: inset 0 0 0 calc(var(--u) * 3) #111, inset 0 0 0 calc(var(--u) * 5) var(--led-green), 0 calc(var(--u) * 3) 0 #000; } }
  @media (prefers-reduced-motion: reduce) { .key.blink { animation: none; } }

  .legend {
    max-width: 900px; margin-top: 8px; padding: 8px 12px; min-height: 92px; box-sizing: border-box;
    border: 1px solid var(--border); border-radius: 6px; background: var(--panel); font-size: 13px;
  }
  .legend .lh { margin-bottom: 2px; }
  .legend .kbd { font-size: 12px; }
  .legend .fn { color: var(--func, #e9a23b); font-weight: 700; font-size: 11px; }
  .legend .links { display: flex; gap: 6px; margin-top: 4px; }
  .legend .hint { margin-top: 4px; }

  .grid-wrap, .mutes-wrap { overflow-x: auto; max-width: 100%; }
  .grid-wrap { position: relative; }
  .grid {
    display: grid;
    grid-template-columns: 130px repeat(var(--cols), minmax(9px, 1fr));
    gap: 2px 1px;
    min-width: calc(130px + var(--cols) * 10px);
  }
  .label { all: unset; position: sticky; left: 0; z-index: 1; background: var(--panel); cursor: pointer; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 6px; line-height: 18px; }
  .label.empty { color: var(--muted); opacity: 0.6; }
  .label.muted { opacity: 0.45; }
  .label.sel { color: var(--accent); }
  .idx { display: inline-block; width: 18px; color: var(--rhythm); }
  .idx.melodic { color: var(--melodic); }
  .m { font-size: 10px; margin-left: 4px; padding: 0 3px; border: 1px solid var(--muted); border-radius: 2px; }
  .cell { height: 18px; background: var(--cell-off); border-radius: 2px; }
  .cell.beat { box-shadow: inset 0 -2px 0 var(--border); }
  .cell.pagestart { margin-left: 4px; }
  .cell.trig { background: var(--rhythm); opacity: var(--v); }
  .cell.trig.melodic { background: var(--melodic); }
  .cell.muted.trig { opacity: 0.2; }
  .cell.cursor { outline: 2px solid var(--accent); outline-offset: -1px; }

  .mutes {
    display: grid;
    grid-template-columns: 24px repeat(var(--n), 14px);
    gap: 1px;
  }
  .mlabel { font-size: 10px; color: var(--rhythm); line-height: 10px; }
  .mlabel.melodic { color: var(--melodic); }
  .mcell { height: 10px; padding: 0; border: 0; border-radius: 1px; background: var(--cell-off); }
  .mcell.on { background: var(--rhythm); }
  .mcell.on.melodic { background: var(--melodic); }
  .mcell.newpat { box-shadow: inset 2px 0 0 var(--muted); }
  .mcell.cur { outline: 1px solid var(--accent); }
</style>
