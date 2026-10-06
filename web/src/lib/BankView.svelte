<script lang="ts">
  import { mmss, type Bank, type BankTrack, type Pattern } from './api'

  let { bank, currentTime, onseek }: {
    bank: Bank
    currentTime: number
    onseek: (t: number) => void
  } = $props()

  let selectedSlot = $state(1)
  let follow = $state(true)
  let page = $state<number | 'all'>('all')

  const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
  const noteName = (n: number) => `${NOTE_NAMES[n % 12]}${Math.floor(n / 12) - 1}`

  // un pas = une double croche = 1/4 de beat (tempo median : leger flottement
  // possible si le morceau accelere, la grille Python suit les beats reels)
  const stepDur = $derived(bank.bpm > 0 ? 60 / bank.bpm / 4 : 0)

  const playingPattern = $derived(
    bank.patterns.find(p => currentTime >= p.start_s && currentTime < p.end_s) ?? null)

  $effect(() => {
    if (follow && playingPattern) selectedSlot = playingPattern.slot
  })

  const pattern = $derived<Pattern>(
    bank.patterns.find(p => p.slot === selectedSlot) ?? bank.patterns[0])

  const currentStep = $derived.by(() => {
    if (!playingPattern || playingPattern.slot !== pattern.slot || stepDur <= 0) return -1
    return Math.floor((currentTime - pattern.start_s) / stepDur) % pattern.steps
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
  const visibleSteps = $derived.by(() => {
    if (page === 'all' || page >= pages) return [...Array(pattern.steps).keys()]
    return [...Array(16).keys()].map(i => i + page * 16)
  })

  $effect(() => {
    // page courante qui suit le curseur, comme l'ecran de la DT
    if (follow && page !== 'all' && currentStep >= 0) page = Math.floor(currentStep / 16)
  })

  function trigAt(track: BankTrack, step: number) {
    return track.trigs.find(t => t.step === step)
  }
</script>

<section class="bank">
  <header>
    <div class="slots">
      {#each bank.patterns as p (p.slot)}
        <button class="slot" class:on={p.slot === pattern.slot} class:playing={playingPattern?.slot === p.slot}
          title="{p.label} · {mmss(p.start_s)} · {p.bars} mes. x{p.repeats}"
          onclick={() => { selectedSlot = p.slot; follow = false; onseek(p.start_s) }}>
          {String(p.slot).padStart(2, '0')}
        </button>
      {/each}
    </div>
    <label class="small"><input type="checkbox" bind:checked={follow} /> suivre la lecture</label>
  </header>

  <p class="muted small mono">
    Pattern {String(pattern.slot).padStart(2, '0')} · {pattern.label} · {mmss(pattern.start_s)}–{mmss(pattern.end_s)}
    · {pattern.bars} mesure(s) = {pattern.steps} pas · joué x{pattern.repeats}
    · {bank.bpm} BPM · source {bank.from_stems ? 'stems' : 'mix'}
  </p>

  <div class="pages">
    <button class="small" class:on={page === 'all'} onclick={() => (page = 'all')}>tout</button>
    {#each Array(pages) as _, i}
      <button class="small" class:on={page === i} class:cur={currentStep >= 0 && Math.floor(currentStep / 16) === i}
        onclick={() => (page = i)}>{i + 1}</button>
    {/each}
  </div>

  <div class="grid-wrap">
    <div class="grid" style="--cols: {visibleSteps.length}">
      {#each pattern.tracks as t (t.index)}
        {@const muted = liveActive !== null && t.trigs.length > 0 && !liveActive.has(t.index)}
        <div class="label" class:empty={!t.trigs.length} class:muted title={t.source}>
          <span class="idx mono" class:melodic={t.index > 8}>{t.index}</span> {t.role}
          {#if muted}<span class="m">M</span>{/if}
        </div>
        {#each visibleSteps as s}
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
            title="{mmss(ph.start_s)} · pattern {ph.pattern_slot}" aria-label="phrase {mmss(ph.start_s)} track {row + 1}"
            onclick={() => onseek(ph.start_s)}></button>
        {/each}
      {/each}
    </div>
  </div>
</section>

<style>
  .bank { padding: 12px 16px; }
  header { display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap; }
  .slots, .pages { display: flex; gap: 4px; flex-wrap: wrap; }
  .slot { font-family: ui-monospace, Menlo, monospace; padding: 4px 8px; }
  .slot.playing:not(.on) { border-color: var(--accent); }
  .pages { margin: 6px 0; }
  .pages .cur:not(.on) { border-color: var(--accent); }
  .small { font-size: 12px; }
  p.small { margin: 8px 0 0; }
  h2 { font-size: 14px; margin: 18px 0 6px; }

  .grid-wrap, .mutes-wrap { overflow-x: auto; max-width: 100%; }
  .grid {
    display: grid;
    grid-template-columns: 130px repeat(var(--cols), minmax(9px, 1fr));
    gap: 2px 1px;
    min-width: calc(130px + var(--cols) * 10px);
  }
  .label { font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 6px; line-height: 18px; }
  .label.empty { color: var(--muted); opacity: 0.6; }
  .label.muted { opacity: 0.45; }
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
