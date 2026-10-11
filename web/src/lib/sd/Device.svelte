<script lang="ts">
  // Device facon Ableton Live : barre de titre (activateur = bypass, nom,
  // deplacer, retirer), corps grise quand desactive ; courbe de reponse pour
  // les filtres et EQ, de transfert pour le Saturator, puis les potards.
  // Automation (8.H) : sur un device pedalboard, le bouton ↗ d'un potard
  // ajoute un second potard, la valeur atteinte en fin de rendu (params_end).
  import type { DeviceSpec, ParamSpec, SdDevice } from '../api'
  import FilterCurve from './FilterCurve.svelte'
  import Knob from './Knob.svelte'
  import SaturatorCurve from './SaturatorCurve.svelte'
  import { isFilter } from './scale'

  let { device, spec, slices = false, onmove, onremove, onhelp }: {
    device: SdDevice
    spec: DeviceSpec | undefined
    /** Traitement en tranches (variations, 8.I) : la valeur de fin est celle de la derniere tranche. */
    slices?: boolean
    onmove?: (delta: number) => void
    onremove?: () => void
    onhelp?: () => void
  } = $props()

  const values = $derived(Object.fromEntries((spec?.params ?? []).map(p => [p.name, device.params[p.name] ?? p.default])))
  function set(name: string, v: number) { device.params[name] = v }
  // Disposition facon Live, sans vide : selecteurs en bandeau compact
  // (bascule, segments ou menu), potards principaux en grille de 1-2 rangees
  // qui s'etend en largeur, parametres conditionnes par un selecteur
  // (Saturator : Color, Waveshaper) en sections de champs a barre.
  const active = (p: ParamSpec) => !p.active_when ||
    Object.entries(p.active_when).every(([k, vals]) => vals.includes(Math.round(values[k])))
  const shown = $derived((spec?.params ?? []).filter(active))
  const selectors = $derived(shown.filter(p => p.choices))
  const main = $derived(shown.filter(p => !p.choices && !p.active_when))
  const toggle = (p: ParamSpec) => p.choices!.length === 2 && p.choices![0] === 'Off' && p.choices![1] === 'On'
  const segmented = (p: ParamSpec) => p.choices!.length <= 4 && p.choices!.join('').length <= 16
  /** Sections conditionnelles : titre = le selecteur (bascule) ou le choix qui les active. */
  const sections = $derived.by(() => {
    const out = new Map<string, { title: string; params: ParamSpec[] }>()
    for (const p of shown) {
      if (p.choices || !p.active_when) continue
      const key = JSON.stringify(p.active_when)
      if (!out.has(key)) {
        const [k, vals] = Object.entries(p.active_when)[0]
        const sel = spec!.params.find(x => x.name === k)
        out.set(key, { title: !sel ? k : toggle(sel) ? sel.label : sel.choices?.[vals[0]] ?? sel.label, params: [] })
      }
      out.get(key)!.params.push(p)
    }
    // prefixe commun retire des noms (WS Drive -> Drive sous « Waveshaper »)
    return [...out.values()].map(s => {
      const first = s.params[0].label.split(' ')[0] + ' '
      const strip = s.params.length > 1 && s.params.every(p => p.label.startsWith(first))
      return { ...s, params: strip ? s.params.map(p => ({ ...p, label: p.label.slice(first.length) })) : s.params }
    })
  })
  const automated = (name: string) => device.params_end?.[name] !== undefined
  function toggleAuto(name: string) {
    if (automated(name)) {
      delete device.params_end![name]
      if (!Object.keys(device.params_end!).length) delete device.params_end
    } else {
      device.params_end = { ...(device.params_end ?? {}), [name]: values[name] }
    }
  }
</script>

{#snippet param(p: ParamSpec, bar: boolean)}
  <div class="param" class:auto={automated(p.name)} class:isbar={bar}>
    <div class="pair">
      <Knob spec={p} {bar} value={values[p.name]} disabled={device.bypass} onchange={v => set(p.name, v)} />
      {#if automated(p.name)}
        <Knob spec={{ ...p, label: slices ? 'tranche N' : 'fin' }} {bar} value={device.params_end![p.name]} disabled={device.bypass}
          onchange={v => (device.params_end![p.name] = v)} />
      {/if}
    </div>
    {#if spec?.automatable}
      <button class="autob" class:on={automated(p.name)} onclick={() => toggleAuto(p.name)} disabled={device.bypass}
        aria-pressed={automated(p.name)}
        title={automated(p.name) ? 'Retirer l\'automation' : slices
          ? 'Varier : le paramètre va de sa valeur (tranche 2, la 1 étant la source brute) à une autre (dernière tranche), avec l\'aléa du traitement'
          : 'Automatiser : le paramètre va de sa valeur à une valeur de fin sur la durée du rendu, selon la courbe du traitement'}>↗</button>
    {/if}
  </div>
{/snippet}

<section class="device" class:off={device.bypass}>
  <header>
    <button class="act" class:on={!device.bypass} onclick={() => (device.bypass = !device.bypass)}
      aria-pressed={!device.bypass} title={device.bypass ? 'Activer le device' : 'Désactiver le device (bypass)'}></button>
    <span class="title" title={spec?.help}>{spec?.label ?? device.type}</span>
    {#if onhelp}<button class="mini" onclick={onhelp} title="Explication dans le notebook">?</button>{/if}
    {#if onmove}
      <button class="mini" onclick={() => onmove(-1)} title="Déplacer vers la gauche">‹</button>
      <button class="mini" onclick={() => onmove(1)} title="Déplacer vers la droite">›</button>
    {/if}
    {#if onremove}<button class="mini" onclick={onremove} title="Retirer le device">×</button>{/if}
  </header>
  {#if !spec}
    <p class="err">device inconnu du catalogue : {device.type}</p>
  {:else}
    <div class="body">
      <div class="left">
        {#if selectors.length}
          <div class="strip">
            {#each selectors as p (p.name)}
              {@const cur = Math.round(values[p.name])}
              {#if toggle(p)}
                <button class="tog" class:on={cur === 1} aria-pressed={cur === 1} disabled={device.bypass}
                  title={p.help || p.label} onclick={() => set(p.name, cur === 1 ? 0 : 1)}>{p.label}</button>
              {:else if segmented(p)}
                <div class="seg" role="radiogroup" aria-label={p.label} title={p.help || p.label}>
                  <span class="slabel">{p.label}</span>
                  {#each p.choices! as c, i (c)}
                    <button role="radio" aria-checked={cur === i} class:on={cur === i}
                      disabled={device.bypass} onclick={() => set(p.name, i)}>{c}</button>
                  {/each}
                </div>
              {:else}
                <select class="menu" aria-label={p.label} title={p.help || p.label} disabled={device.bypass}
                  value={cur} onchange={e => set(p.name, +e.currentTarget.value)}>
                  {#each p.choices! as c, i (c)}<option value={i}>{c}</option>{/each}
                </select>
              {/if}
            {/each}
          </div>
        {/if}
        {#if isFilter(device.type)}
          <FilterCurve type={device.type} params={values} specs={spec.params} disabled={device.bypass} onchange={set} />
        {:else if device.type === 'saturator'}
          <SaturatorCurve params={values} specs={spec.params} disabled={device.bypass} onchange={set} />
        {/if}
        {#if main.length}
          <div class="knobs" class:two={main.length > 3}>
            {#each main as p (p.name)}{@render param(p, false)}{/each}
          </div>
        {/if}
      </div>
      {#if sections.length}
        <div class="sections">
          {#each sections as s (s.title)}
            <div class="section">
              <span class="stitle">{s.title}</span>
              <div class="bars">
                {#each s.params as p (p.name)}{@render param(p, true)}{/each}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</section>

<style>
  .device { flex: none; background: var(--panel); border: 1px solid var(--border); border-radius: 4px; min-width: 120px; display: flex; flex-direction: column; }
  header { display: flex; align-items: center; gap: 4px; padding: 3px 6px; background: var(--panel-2); border-bottom: 1px solid var(--border); border-radius: 4px 4px 0 0; }
  .title { flex: 1; font-size: 12px; font-weight: 600; white-space: nowrap; }
  .act { width: 12px; height: 12px; padding: 0; border-radius: 50%; background: var(--cell-off); border: 1px solid var(--muted); }
  .act.on { background: var(--accent); border-color: var(--accent); }
  .mini { padding: 0 5px; font-size: 12px; line-height: 16px; background: none; border-color: transparent; color: var(--muted); }
  .mini:hover { color: var(--text); }
  .body { padding: 6px 8px; display: flex; gap: 10px; align-items: flex-start; }
  .left { display: flex; flex-direction: column; gap: 6px; align-items: center; }
  .strip { display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; align-items: center; max-width: 260px; }
  .strip button, .menu { padding: 1px 6px; font-size: 11px; line-height: 15px; border-radius: 2px; }
  .menu { max-width: 120px; }
  .tog.on, .seg button.on { background: var(--accent); border-color: var(--accent); color: #fff; }
  .seg { display: flex; align-items: center; gap: 1px; }
  .slabel { font-size: 10px; color: var(--muted); margin-right: 3px; }
  .knobs { display: grid; grid-auto-flow: column; grid-template-rows: auto; gap: 2px 0; }
  .knobs.two { grid-template-rows: repeat(2, auto); }
  .sections { display: flex; flex-direction: column; gap: 6px; }
  .section { border: 1px solid var(--border); border-radius: 3px; padding: 3px 6px 5px; background: var(--panel-2); }
  .stitle { display: block; font-size: 10px; font-weight: 600; color: var(--muted); margin-bottom: 3px; }
  .bars { display: grid; grid-auto-flow: column; grid-template-rows: repeat(2, auto); gap: 3px 10px; justify-content: start; }
  .param { position: relative; display: flex; flex-direction: column; align-items: center; }
  .param.isbar { flex-direction: row; gap: 2px; }
  .param.isbar .pair { flex-direction: column; gap: 2px; }
  .param.auto { background: color-mix(in srgb, var(--accent) 10%, transparent); border-radius: 4px; }
  .pair { display: flex; }
  .param:not(.isbar) .autob { position: absolute; top: 12px; right: 0; }
  .autob { padding: 0 3px; font-size: 9px; line-height: 12px; background: none; border-color: transparent; color: var(--muted); opacity: 0.5; }
  .param:hover .autob, .autob.on { opacity: 1; }
  .autob.on { color: var(--accent); border-color: var(--accent); }
  .off .body { opacity: 0.45; }
  .err { color: #dc2626; font-size: 12px; padding: 8px; margin: 0; }
</style>
