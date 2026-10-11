<script lang="ts">
  // Device facon Ableton Live : barre de titre (activateur = bypass, nom,
  // deplacer, retirer), corps grise quand desactive ; courbe de reponse pour
  // les filtres et EQ, puis une rangee de potards. Automation (8.H) : sur un
  // device pedalboard, le bouton ↗ d'un potard ajoute un second potard, la
  // valeur atteinte en fin de rendu (params_end).
  import type { DeviceSpec, SdDevice } from '../api'
  import FilterCurve from './FilterCurve.svelte'
  import Knob from './Knob.svelte'
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
  // parametres masques tant que leur selecteur ne les active pas (Saturator : WS, Color)
  const shown = $derived((spec?.params ?? []).filter(p => !p.active_when ||
    Object.entries(p.active_when).every(([k, vals]) => vals.includes(Math.round(values[k])))))
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
      {#if isFilter(device.type)}
        <FilterCurve type={device.type} params={values} specs={spec.params} disabled={device.bypass} onchange={set} />
      {/if}
      <div class="knobs">
        {#each shown as p (p.name)}
          {#if p.choices}
            <div class="choices" role="radiogroup" aria-label={p.label} title={p.help || p.label}>
              <span class="clabel">{p.label}</span>
              {#each p.choices as c, i (c)}
                <button role="radio" aria-checked={Math.round(values[p.name]) === i} class:on={Math.round(values[p.name]) === i}
                  disabled={device.bypass} onclick={() => set(p.name, i)}>{c}</button>
              {/each}
            </div>
          {:else}
            <div class="param" class:auto={automated(p.name)}>
              <div class="pair">
                <Knob spec={p} value={values[p.name]} disabled={device.bypass} onchange={v => set(p.name, v)} />
                {#if automated(p.name)}
                  <Knob spec={{ ...p, label: slices ? 'tranche N' : 'fin' }} value={device.params_end![p.name]} disabled={device.bypass}
                    onchange={v => (device.params_end![p.name] = v)} />
                {/if}
              </div>
              {#if spec.automatable}
                <button class="autob" class:on={automated(p.name)} onclick={() => toggleAuto(p.name)} disabled={device.bypass}
                  aria-pressed={automated(p.name)}
                  title={automated(p.name) ? 'Retirer l\'automation' : slices
                    ? 'Varier : le paramètre va de sa valeur (tranche 2, la 1 étant la source brute) à une autre (dernière tranche), avec l\'aléa du traitement'
                    : 'Automatiser : le paramètre va de sa valeur à une valeur de fin sur la durée du rendu, selon la courbe du traitement'}>↗</button>
              {/if}
            </div>
          {/if}
        {/each}
      </div>
    </div>
  {/if}
</section>

<style>
  .device { flex: none; background: var(--panel); border: 1px solid var(--border); border-radius: 4px; min-width: 150px; display: flex; flex-direction: column; }
  header { display: flex; align-items: center; gap: 4px; padding: 3px 6px; background: var(--panel-2); border-bottom: 1px solid var(--border); border-radius: 4px 4px 0 0; }
  .title { flex: 1; font-size: 12px; font-weight: 600; white-space: nowrap; }
  .act { width: 12px; height: 12px; padding: 0; border-radius: 50%; background: var(--cell-off); border: 1px solid var(--muted); }
  .act.on { background: var(--accent); border-color: var(--accent); }
  .mini { padding: 0 5px; font-size: 12px; line-height: 16px; background: none; border-color: transparent; color: var(--muted); }
  .mini:hover { color: var(--text); }
  .body { padding: 8px; display: flex; flex-direction: column; gap: 8px; align-items: center; }
  .knobs { display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; max-width: 280px; }
  .choices { display: grid; grid-template-columns: repeat(2, auto); gap: 2px; width: 100%; justify-content: center; }
  .choices button { padding: 1px 8px; font-size: 11px; border-radius: 2px; }
  .clabel { grid-column: 1 / -1; text-align: center; font-size: 10px; color: var(--muted); }
  .param { display: flex; flex-direction: column; align-items: center; }
  .param.auto { background: color-mix(in srgb, var(--accent) 10%, transparent); border-radius: 4px; }
  .pair { display: flex; }
  .autob { padding: 0 5px; font-size: 10px; line-height: 14px; background: none; border-color: transparent; color: var(--muted); }
  .autob.on { color: var(--accent); border-color: var(--accent); }
  .off .body { opacity: 0.45; }
  .err { color: #dc2626; font-size: 12px; padding: 8px; margin: 0; }
</style>
