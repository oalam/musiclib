<script lang="ts">
  import { mmss, SEGMENT_COLORS, type Bank, type BankTrack, type Pattern } from './api'

  let { bank, currentTime, onseek }: {
    bank: Bank
    currentTime: number
    onseek: (t: number) => void
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
  type Mode = 'trig' | 'trk' | 'mute' | 'ptn'
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

  function pressKey(i: number) {
    if (mode === 'trig') { if (page * 16 + i < pattern.steps) seekStep(page * 16 + i) }
    else if (mode === 'trk') { selectedTrack = i + 1; mode = 'trig' }  // comme relacher TRK
    else if (mode === 'mute') selectedTrack = i + 1
    else {
      const p = bank.patterns.find(p => p.slot === i + 1)
      if (p) { selectedSlot = p.slot; follow = false; onseek(p.start_s) }
    }
  }
</script>

<section class="bank">
  <div class="dt" aria-label="Façade Digitakt II">
    <div class="top">
      <div class="screen mono">
        <div class="bar">
          <span class="tag">{patName(pattern.slot)}</span>
          <span class="name">{pattern.label.toUpperCase()}</span>
          <span class="bpm">♩{bank.bpm.toFixed(1)}</span>
        </div>
        {#if mode === 'trig'}
          <div class="row big">T{String(track.index).padStart(2, '0')} {track.role.toUpperCase()}</div>
          <div class="row">{track.trigs.length} TRIGS · LEN {pattern.steps} · x{pattern.repeats}</div>
          <div class="row dim">PAGE {page + 1}:{pages} · STEP {currentStep >= 0 ? String(currentStep + 1).padStart(3, '0') : '---'}</div>
        {:else if mode === 'trk'}
          <div class="row big">TRACK</div>
          <div class="row">CHOISIR UNE TRACK (1-16)</div>
          <div class="row dim">ACTUELLE T{String(track.index).padStart(2, '0')} {track.role.toUpperCase()}</div>
        {:else if mode === 'mute'}
          <div class="row big">MUTE MODE</div>
          <div class="row">{unmuted.size}/16 TRACKS ACTIVES</div>
          <div class="row dim">{currentPhrase >= 0 && liveActive ? `PHRASE ${currentPhrase + 1}/${bank.mutes.length}` : 'ETAT DU PATTERN'}</div>
        {:else}
          <div class="row big">BANK {BANKS[bankLetter]}</div>
          <div class="row">{bank.patterns.length} PATTERNS · {playingPattern ? `PLAY ${patName(playingPattern.slot)}` : 'STOP'}</div>
          <div class="banks" aria-label="Lettre de bank">
            {#each BANKS as l, i}
              <button class:sel={bankLetter === i} onclick={() => setBankLetter(i)}>{l}</button>
            {/each}
          </div>
        {/if}
        <div class="row dim foot">{bank.from_stems ? 'STEMS' : 'MIX'} · {pattern.bars} BAR{pattern.bars > 1 ? 'S' : ''} · {mmss(pattern.start_s)}-{mmss(pattern.end_s)} · {mmss(currentTime)}</div>
      </div>

      <div class="ctrl">
        <div class="leds" aria-label="Pages">
          {#each Array(8) as _, i}
            <button class="led" class:lit={page === i} class:play={page !== i && currentStep >= 0 && Math.floor(currentStep / 16) === i}
              disabled={i >= pages} aria-label="page {i + 1}" onclick={() => { page = i; follow = false }}></button>
          {/each}
        </div>
        <div class="pair">
          <button class="hw" class:lit={follow} onclick={() => (follow = !follow)}>FOLLOW</button>
          <button class="hw" onclick={() => { page = (page + 1) % pages; follow = false }}>PAGE</button>
        </div>
      </div>
    </div>

    <div class="bottom">
      <div class="side">
        {#each [['trk', 'TRK', 'Track'], ['mute', 'MUTE', 'Mute Mode'], ['ptn', 'PTN', 'Bank']] as [m, k, sub]}
          <button class="hw side-key" class:lit={mode === m} onclick={() => (mode = mode === m ? 'trig' : m as Mode)}>
            {k}<span class="sub">{sub}</span>
          </button>
        {/each}
      </div>

      <div class="keys">
        {#each Array(16) as _, i}
          {#if mode === 'trig'}
            {@const s = page * 16 + i}
            {@const trig = s < pattern.steps ? trigAt(track, s) : undefined}
            <button class="key" class:off={s >= pattern.steps} class:red={!!trig} class:cursor={s === currentStep}
              style={trig ? `--v: ${0.45 + (0.55 * trig.velocity) / 127}` : ''}
              title={trig ? `pas ${s + 1} · vel ${trig.velocity}${trig.note !== null ? ' · ' + noteName(trig.note) : ''}` : `pas ${s + 1}`}
              onclick={() => pressKey(i)}>
              <span class="n">{i + 1}</span>
              {#if trig && trig.note !== null && track.index > 8}<span class="note">{noteName(trig.note)}</span>{/if}
            </button>
          {:else if mode === 'trk'}
            {@const t = pattern.tracks.find(t => t.index === i + 1)}
            <button class="key" class:off={!t?.trigs.length} class:red={track.index === i + 1}
              title="{i + 1} {t?.role ?? ''}" onclick={() => pressKey(i)}>
              <span class="n">{i + 1}</span><span class="note">{t?.role ?? ''}</span>
            </button>
          {:else if mode === 'mute'}
            {@const t = pattern.tracks.find(t => t.index === i + 1)}
            <button class="key" class:off={!t?.trigs.length} class:green={!!t?.trigs.length && unmuted.has(i + 1)}
              title="{i + 1} {t?.role ?? ''}" onclick={() => pressKey(i)}>
              <span class="n">{i + 1}</span><span class="note">{t?.role ?? ''}</span>
            </button>
          {:else}
            {@const p = bank.patterns.find(p => p.slot === i + 1)}
            <button class="key" class:off={!p} class:white={!!p} class:red={p?.slot === pattern.slot}
              class:blink={playingPattern?.slot === i + 1}
              title={p ? `${patName(p.slot)} · ${p.label} · ${mmss(p.start_s)}` : ''} onclick={() => pressKey(i)}>
              <span class="n">{i + 1}</span>{#if p}<span class="note">{p.label}</span>{/if}
            </button>
          {/if}
        {/each}
      </div>
    </div>
  </div>

  {#if sections.length}
    <div class="chain" aria-label="Ordre de jeu">
      <span class="muted small">Chaîne</span>
      {#each sections as s (s.index)}
        <button class="link mono" class:cur={playingSection?.index === s.index}
          style="--c: {SEGMENT_COLORS[s.label] ?? '#888888'}"
          title="{s.label} · {mmss(s.start_s)} · {s.bars} mes. · tracks {s.active.join(' ')}"
          onclick={() => { selectedSlot = s.pattern_slot; onseek(s.start_s) }}>
          {patName(s.pattern_slot)}
        </button>
      {/each}
    </div>
  {/if}

  <h2>Vue d'ensemble <span class="muted small">({patName(pattern.slot)}, toutes les tracks, clic = sélection)</span></h2>
  <div class="grid-wrap">
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
          <div class="cell" class:beat={s % 4 === 0} class:pagestart={s % 16 === 0 && s > 0}
            class:cursor={s === currentStep} class:melodic={t.index > 8} class:muted
            class:trig={!!trig}
            style={trig ? `--v: ${0.35 + (0.65 * trig.velocity) / 127}` : ''}
            title={trig ? `pas ${s + 1} · vel ${trig.velocity}${trig.note !== null ? ' · ' + noteName(trig.note) : ''}` : ''}>
          </div>
        {/each}
      {/each}
    </div>
  </div>

  <h2>Partition de mutes <span class="muted small">(phrases de {bank.phrase_bars} mesures, clic = saut)</span></h2>
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
</section>

<style>
  .bank { padding: 12px 16px; }
  .chain { display: flex; gap: 3px; flex-wrap: wrap; align-items: center; margin: 10px 0 6px; }
  .chain .link { font-size: 11px; padding: 2px 5px; border-bottom: 3px solid var(--c); }
  .chain .link.cur { outline: 1px solid var(--accent); }
  .small { font-size: 12px; }
  h2 { font-size: 14px; margin: 18px 0 6px; }

  /* facade DT2 : toujours sombre, comme la machine, quel que soit le theme */
  .dt {
    --face: #1c1c1c; --key: #262626; --key-edge: #0a0a0a; --silk: #d8d8d4; --func: #e9a23b;
    --led-red: #ff3b3b; --led-green: #4cff6a; --lcd: #9fd0ff; --lcd-bg: #07142a;
    background: linear-gradient(#262626, var(--face));
    border: 1px solid #000; border-radius: 10px;
    padding: 16px; max-width: 780px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
    color: var(--silk);
  }
  .dt button { font: inherit; color: inherit; }
  .top { display: flex; gap: 16px; flex-wrap: wrap; align-items: stretch; margin-bottom: 18px; }

  /* ecran : fond bleu nuit, bandeau inverse en tete comme l'UI du DT2 */
  .screen {
    flex: 1 1 280px; background: var(--lcd-bg); border: 6px solid #0d0d0d; border-radius: 4px;
    box-shadow: inset 0 0 0 1px #24324a; padding: 6px 8px;
    color: var(--lcd); font-size: 12px; line-height: 1.5;
  }
  .bar { display: flex; align-items: center; gap: 6px; background: var(--lcd); color: var(--lcd-bg); padding: 1px 4px; font-weight: 700; margin-bottom: 4px; }
  .bar .tag { border: 1px solid var(--lcd-bg); padding: 0 3px; font-size: 10px; }
  .bar .name { font-size: 15px; letter-spacing: 0.03em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .bar .bpm { margin-left: auto; font-size: 11px; }
  .screen .row { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .screen .big { font-size: 16px; font-weight: 700; }
  .screen .dim { opacity: 0.6; }
  .screen .foot { font-size: 10px; margin-top: 2px; }
  .banks { display: grid; grid-template-columns: repeat(16, 1fr); gap: 2px; margin: 2px 0; }
  .banks button { all: unset; cursor: pointer; text-align: center; font-size: 10px; border: 1px solid #24324a; }
  .banks button.sel { background: var(--lcd); color: var(--lcd-bg); }

  .ctrl { display: flex; flex-direction: column; justify-content: flex-end; align-items: flex-end; gap: 12px; }
  .leds { display: grid; grid-template-columns: repeat(4, 12px); gap: 8px 10px; }
  .led { width: 12px; height: 12px; padding: 0; border-radius: 50%; background: #8a8a86; border: 1px solid #000; box-shadow: inset 0 -2px 2px rgba(0, 0, 0, 0.4); }
  .led:disabled { opacity: 0.3; cursor: default; }
  .led.play { background: #2f7a3b; }
  .led.lit { background: var(--led-green); box-shadow: 0 0 8px var(--led-green); }
  .pair { display: flex; gap: 8px; }

  .hw {
    font-size: 11px !important; letter-spacing: 0.04em; padding: 8px 12px; color: #bdbdb8 !important;
    background: linear-gradient(#2e2e2e, #222); border: 1px solid var(--key-edge); border-radius: 6px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 3px 0 #000;
  }
  .hw.lit { color: #fff !important; box-shadow: inset 0 -3px 0 var(--led-red), 0 3px 0 #000; }
  .hw:hover, .key:hover, .led:hover:not(:disabled) { border-color: #555; }

  .bottom { display: flex; gap: 14px; align-items: flex-start; }
  .side { display: flex; flex-direction: column; gap: 14px; }
  .side-key { display: flex; flex-direction: column; align-items: center; gap: 4px; min-width: 64px; padding: 8px 6px 4px; }
  .sub { font-size: 9px; color: var(--func); letter-spacing: 0; }

  /* 16 trig keys en 2 rangees de 8 : chiffre souligne, LED = contour + chiffre */
  .keys { flex: 1; display: grid; grid-template-columns: repeat(8, 1fr); gap: 12px; }
  .key {
    position: relative; aspect-ratio: 1; min-width: 0; padding: 0;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    background: linear-gradient(#2c2c2c, #1e1e1e); border: 1px solid var(--key-edge); border-radius: 8px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.07), 0 4px 0 #000;
  }
  .key .n {
    font-size: clamp(12px, 2.4vw, 22px); line-height: 1; color: #d8d8d4;
    border-bottom: 2px solid currentColor; padding-bottom: 2px;
  }
  .key .note { position: absolute; bottom: 4px; left: 2px; right: 2px; font-size: 9px; color: #9a9a96;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .key.off .n { opacity: 0.35; }
  .key.white .n { color: #fff; }
  .key.red {
    box-shadow: inset 0 0 0 3px #111, inset 0 0 0 5px rgba(255, 59, 59, var(--v, 1)), 0 0 10px rgba(255, 59, 59, calc(var(--v, 1) * 0.35)), 0 4px 0 #000;
  }
  .key.red .n { color: var(--led-red); text-shadow: 0 0 6px rgba(255, 59, 59, 0.6); }
  .key.green { box-shadow: inset 0 0 0 3px #111, inset 0 0 0 5px var(--led-green), 0 0 10px rgba(76, 255, 106, 0.3), 0 4px 0 #000; }
  .key.green .n { color: var(--led-green); }
  .key.cursor { background: linear-gradient(#5a5a56, #444); }
  .key.blink { animation: blink 0.5s steps(1) infinite; }
  @keyframes blink { 50% { box-shadow: inset 0 0 0 3px #111, inset 0 0 0 5px var(--led-green), 0 4px 0 #000; } }
  @media (prefers-reduced-motion: reduce) { .key.blink { animation: none; } }
  @media (max-width: 560px) {
    .keys { gap: 6px; }
    .side-key { min-width: 48px; }
    .key .note { display: none; }
  }

  .grid-wrap, .mutes-wrap { overflow-x: auto; max-width: 100%; }
  .grid {
    display: grid;
    grid-template-columns: 130px repeat(var(--cols), minmax(9px, 1fr));
    gap: 2px 1px;
    min-width: calc(130px + var(--cols) * 10px);
  }
  .label { all: unset; cursor: pointer; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 6px; line-height: 18px; }
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
