<script lang="ts">
  import { api, mmss, SEGMENT_COLORS, type Bank, type BankTrack, type ManualRef, type Pattern } from './api'
  import { CONTROLS, KNOBS, midiLabel, PARAM_PAGES, pagesOf, type Func, type Param } from './dt2'

  let { bank, currentTime, playing, onseek, onplay, onstop, onhelp }: {
    bank: Bank
    currentTime: number
    playing: boolean
    onseek: (t: number) => void
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

  // 7.G : facade complete. Les controles qui ont un sens dans le front agissent,
  // les autres affichent leur legende ; en mode AIDE, un clic ouvre la fiche.
  let func = $state(false)
  let help = $state(false)
  let focus = $state<{ id: string; param?: number }>({ id: 'screen' })
  let pageId = $state('trig1')
  let lastStep = $state(-1)
  let outline = $state<Record<string, ManualRef>>({})
  api.manualOutline().then(o => (outline = o)).catch(() => { /* manuel absent : liens masques */ })

  const paramPage = $derived(PARAM_PAGES.find(pg => pg.id === pageId) ?? PARAM_PAGES[0])
  const focused = $derived(CONTROLS[focus.id])
  const focusedParam = $derived(focus.param !== undefined ? paramPage.params[focus.param] : null)
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

  function pressKey(i: number) {
    if (help) { act('trigs'); return }
    focus = { id: 'trigs' }
    if (func) { func = false; return }  // QUICK MUTE : legende seule, les mutes viennent de la bank
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
  {#snippet hw(id: string, primary?: () => void, secondary?: () => void, lit = false, cls = '')}
    {@const c = CONTROLS[id]}
    <button class="hw {cls}" class:lit class:hasfunc={!!c.func} class:sel={focus.id === id}
      onmouseenter={() => (focus = { id })} onclick={() => act(id, primary, secondary)}>
      {c.label}{#if c.func}<span class="sub">{c.func.label}</span>{/if}
    </button>
  {/snippet}
  {#snippet knob(id: string, label: string, value: number | null, onclick: () => void, onenter: () => void, sel: boolean, big = false)}
    <button class="knob" class:big class:sel class:known={value !== null}
      style="--a: {value === null ? 0 : -135 + (270 * value) / 127}deg"
      aria-label="{label}" onmouseenter={onenter} {onclick}>
      <span class="cap"></span><span class="klabel">{label}</span>
    </button>
  {/snippet}

  <div class="dt" class:funcmode={func} class:helpmode={help} aria-label="Façade Digitakt II">
    <div class="top">
      <div class="menu">
        {@render knob('volume', 'VOLUME', null, () => act('volume'), () => (focus = { id: 'volume' }), focus.id === 'volume')}
        <div class="menukeys">
          {@render hw('preset')}
          {@render hw('settings')}
          {@render hw('sampling')}
          {@render hw('tempo')}
        </div>
      </div>

      <div class="screen mono" role="presentation" onmouseenter={() => (focus = { id: 'screen' })}>
        <div class="bar">
          <span class="tag">{patName(pattern.slot)}</span>
          <span class="name">{pattern.label.toUpperCase()}</span>
          <span class="bpm">{playing ? '▶' : '■'} ♩{bank.bpm.toFixed(1)}</span>
        </div>
        {#if mode === 'trig'}
          <div class="row big">T{String(track.index).padStart(2, '0')} {track.role.toUpperCase()} <span class="pgt">{paramPage.title}</span></div>
          <div class="params">
            {#each paramPage.params as param, i}
              <span class:hl={focus.id === 'knobs' && focus.param === i}>
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

      <div class="data">
        {@render knob('level', 'LEVEL', null, () => act('level'), () => (focus = { id: 'level' }), focus.id === 'level', true)}
        <div class="pair stack">
          {@render hw('no')}
          {@render hw('yes')}
        </div>
      </div>

      <div class="entry">
        <div class="knobs">
          {#each KNOBS as k, i}
            {@const param = paramPage.params[i]}
            {@render knob('knobs', k, paramValue(param), () => pressKnob(i), () => (focus = { id: 'knobs', param: i }),
              focus.id === 'knobs' && focus.param === i)}
          {/each}
        </div>
        <div class="pkeys">
          {#each ['p-trig', 'p-src', 'p-fltr', 'p-amp', 'p-fx', 'p-mod'] as id}
            {@render hw(id, () => pressParamKey(id), undefined, paramPage.key === id, 'pkey')}
          {/each}
        </div>
      </div>
    </div>

    <div class="mid">
      <button class="hw front" class:lit={help} title="Mode aide : un clic ouvre la fiche ou le manuel"
        onclick={() => (help = !help)}>AIDE ?</button>
      <button class="hw front" class:lit={follow} title="Spécifique au front : la page et le pattern suivent la lecture"
        onclick={() => (follow = !follow)}>FOLLOW</button>
      <div class="leds" role="group" aria-label="Pages" onmouseenter={() => (focus = { id: 'leds' })}>
        {#each Array(8) as _, i}
          <button class="led" class:lit={page === i} class:play={page !== i && currentStep >= 0 && Math.floor(currentStep / 16) === i}
            disabled={i >= pages} aria-label="page {i + 1}"
            onclick={() => act('leds', () => { page = i; follow = false })}></button>
        {/each}
      </div>
      <div class="arrows" role="group" aria-label="Flèches" onmouseenter={() => (focus = { id: 'arrows' })}>
        <button class="hw arr up" aria-label="UP" onclick={() => act('arrows')}>▲</button>
        <button class="hw arr left" aria-label="LEFT" onclick={() => act('arrows', () => pressArrow(-1))}>◀</button>
        <button class="hw arr down" aria-label="DOWN" onclick={() => act('arrows')}>▼</button>
        <button class="hw arr right" aria-label="RIGHT" onclick={() => act('arrows', () => pressArrow(1))}>▶</button>
      </div>
      {@render hw('page', () => { page = (page + 1) % pages; follow = false })}
    </div>

    <div class="bottom">
      <div class="side">
        {@render hw('record')}
        {@render hw('play', onplay, undefined, playing)}
        {@render hw('stop', () => onstop(playingStart))}
        {@render hw('trk', () => (mode = mode === 'trk' ? 'trig' : 'trk'), () => (mode = mode === 'mute' ? 'trig' : 'mute'), mode === 'trk' || mode === 'mute')}
        {@render hw('ptn', () => (mode = mode === 'ptn' ? 'trig' : 'ptn'), () => (mode = 'ptn'), mode === 'ptn')}
        {@render hw('song')}
        {@render hw('func', undefined, undefined, func)}
        {@render hw('keyboard')}
      </div>

      <div class="keys" role="group" aria-label="Trig keys" onmouseenter={() => (focus = { id: 'trigs' })}>
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

  <div class="legend" aria-live="polite">
    {#if focusedParam !== null && focus.param !== undefined}
      {@const ref = manualRef(paramPage)}
      <div class="lh"><span class="kbd mono">{KNOBS[focus.param]}</span> <b>{focusedParam.key}</b> · {focusedParam.name}
        <span class="muted">· page {paramPage.title}</span></div>
      <div class="ltext mono">{midiLabel(focusedParam)} <span class="muted">· canal de la track</span></div>
      {#if paramPage.note}<div class="muted small">{paramPage.note}</div>{/if}
      <div class="links">
        <button class="small" onclick={() => onhelp(paramPage.kb)}>Fiche</button>
        {#if ref}<button class="small" onclick={() => onhelp(undefined, ref.page)}>Manuel §{ref.section} p{ref.page}</button>{/if}
      </div>
    {:else if focus.param !== undefined}
      <div class="lh"><span class="kbd mono">{KNOBS[focus.param]}</span> <span class="muted">sans paramètre sur la page {paramPage.title}</span></div>
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
    <div class="muted small hint">{help ? 'AIDE active : un clic ouvre la fiche (ou le manuel).' : 'Survol = légende ; FUNC puis une touche = fonction secondaire ; AIDE ? = clic vers la fiche.'}</div>
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
    padding: 16px; max-width: 980px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
    color: var(--silk);
  }
  .dt button { font: inherit; color: inherit; }
  .top { display: flex; gap: 14px; flex-wrap: wrap; align-items: flex-start; margin-bottom: 10px; }
  .menu { display: flex; flex-direction: column; align-items: center; gap: 10px; }
  .menukeys { display: grid; grid-template-columns: repeat(2, auto); gap: 8px; }
  .data { display: flex; flex-direction: column; align-items: center; gap: 10px; }
  .entry { display: flex; flex-direction: column; gap: 10px; }
  .knobs { display: grid; grid-template-columns: repeat(4, 44px); gap: 6px 10px; }
  .pkeys { display: grid; grid-template-columns: repeat(6, auto); gap: 5px; }
  .pkey { padding: 6px 5px !important; min-width: 0; }

  /* potards : capuchon sombre, trait blanc = position (centre si valeur inconnue) */
  .knob { all: unset; cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 2px; }
  .knob .cap {
    position: relative; width: 34px; height: 34px; border-radius: 50%;
    background: radial-gradient(circle at 40% 35%, #4a4a48, #1a1a1a 70%);
    border: 1px solid #000; box-shadow: 0 3px 0 #000, inset 0 1px 0 rgba(255, 255, 255, 0.1);
  }
  .knob .cap::after {
    content: ''; position: absolute; left: 50%; top: 3px; width: 2px; height: 11px; margin-left: -1px;
    background: #8a8a86; border-radius: 1px; transform-origin: 50% 14px; transform: rotate(var(--a));
  }
  .knob.known .cap::after { background: #fff; }
  .knob.big .cap { width: 44px; height: 44px; }
  .knob.big .cap::after { transform-origin: 50% 19px; height: 14px; }
  .knob .klabel { font-size: 10px; color: var(--silk); }
  .knob.sel .cap, .knob:hover .cap { border-color: #777; }
  .knob.sel .klabel { color: #fff; }

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

  .mid { display: flex; align-items: center; justify-content: flex-end; gap: 14px; flex-wrap: wrap; margin-bottom: 14px; }
  .mid .front { border-style: dashed; flex-direction: row; }
  .mid .front + .front { margin-right: auto; }
  .arrows { display: grid; grid-template-columns: repeat(3, 26px); grid-template-rows: repeat(2, 22px); gap: 3px; }
  .arr { padding: 0 !important; font-size: 9px !important; }
  .arr.up { grid-column: 2; grid-row: 1; }
  .arr.left { grid-column: 1; grid-row: 2; }
  .arr.down { grid-column: 2; grid-row: 2; }
  .arr.right { grid-column: 3; grid-row: 2; }
  .leds { display: grid; grid-template-columns: repeat(4, 12px); gap: 8px 10px; }
  .led { width: 12px; height: 12px; padding: 0; border-radius: 50%; background: #8a8a86; border: 1px solid #000; box-shadow: inset 0 -2px 2px rgba(0, 0, 0, 0.4); }
  .led:disabled { opacity: 0.3; cursor: default; }
  .led.play { background: #2f7a3b; }
  .led.lit { background: var(--led-green); box-shadow: 0 0 8px var(--led-green); }
  .pair { display: flex; gap: 8px; }
  .pair.stack { flex-direction: column; }

  .hw {
    font-size: 11px !important; letter-spacing: 0.04em; padding: 8px 12px; color: #bdbdb8 !important;
    background: linear-gradient(#2e2e2e, #222); border: 1px solid var(--key-edge); border-radius: 6px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 3px 0 #000;
  }
  .hw { display: flex; flex-direction: column; align-items: center; gap: 3px; }
  .hw.lit { color: #fff !important; box-shadow: inset 0 -3px 0 var(--led-red), 0 3px 0 #000; }
  .hw.sel { border-color: #777; }
  .funcmode .hw.hasfunc .sub { color: #ffc46b; text-shadow: 0 0 6px rgba(233, 162, 59, 0.6); }
  .funcmode .hw:not(.hasfunc):not(.lit) { opacity: 0.55; }
  .helpmode .hw, .helpmode .knob, .helpmode .key { cursor: help; }
  .hw:hover, .key:hover, .led:hover:not(:disabled) { border-color: #555; }

  .bottom { display: flex; gap: 14px; align-items: flex-start; flex-wrap: wrap; }
  .side { display: grid; grid-template-columns: repeat(3, 64px); gap: 10px 8px; align-content: start; }
  .side .hw { padding: 8px 4px 4px; }
  .sub { font-size: 9px; color: var(--func); letter-spacing: 0; }

  .screen .pgt { float: right; font-size: 11px; font-weight: 400; opacity: 0.8; }
  .params { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0 6px; font-size: 11px; margin: 2px 0; }
  .params span { white-space: nowrap; overflow: hidden; }
  .params b { font-weight: 400; opacity: 0.6; margin-right: 4px; }
  .params .hl { background: var(--lcd); color: var(--lcd-bg); }

  .legend {
    max-width: 980px; margin-top: 8px; padding: 8px 12px; min-height: 92px; box-sizing: border-box;
    border: 1px solid var(--border); border-radius: 6px; background: var(--panel); font-size: 13px;
  }
  .legend .lh { margin-bottom: 2px; }
  .legend .kbd { font-size: 12px; }
  .legend .fn { color: var(--func, #e9a23b); font-weight: 700; font-size: 11px; }
  .legend .links { display: flex; gap: 6px; margin-top: 4px; }
  .legend .hint { margin-top: 4px; }

  /* 16 trig keys en 2 rangees de 8 : chiffre souligne, LED = contour + chiffre */
  .keys { flex: 1 1 320px; display: grid; grid-template-columns: repeat(8, 1fr); gap: 12px; }
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
    .side { grid-template-columns: repeat(3, 52px); }
    .knobs { grid-template-columns: repeat(4, 38px); }
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
