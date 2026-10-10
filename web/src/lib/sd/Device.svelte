<script lang="ts">
  // Device facon Ableton Live : barre de titre (activateur = bypass, nom,
  // deplacer, retirer), corps grise quand desactive ; courbe de reponse pour
  // les filtres et EQ, puis une rangee de potards.
  import type { DeviceSpec, SdDevice } from '../api'
  import FilterCurve from './FilterCurve.svelte'
  import Knob from './Knob.svelte'
  import { isFilter } from './scale'

  let { device, spec, onmove, onremove }: {
    device: SdDevice
    spec: DeviceSpec | undefined
    onmove?: (delta: number) => void
    onremove?: () => void
  } = $props()

  const values = $derived(Object.fromEntries((spec?.params ?? []).map(p => [p.name, device.params[p.name] ?? p.default])))
  function set(name: string, v: number) { device.params[name] = v }
</script>

<section class="device" class:off={device.bypass}>
  <header>
    <button class="act" class:on={!device.bypass} onclick={() => (device.bypass = !device.bypass)}
      aria-pressed={!device.bypass} title={device.bypass ? 'Activer le device' : 'Désactiver le device (bypass)'}></button>
    <span class="title" title={spec?.help}>{spec?.label ?? device.type}</span>
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
        {#each spec.params as p (p.name)}
          {#if p.choices}
            <div class="choices" role="radiogroup" aria-label={p.label} title={p.help || p.label}>
              {#each p.choices as c, i (c)}
                <button role="radio" aria-checked={Math.round(values[p.name]) === i} class:on={Math.round(values[p.name]) === i}
                  disabled={device.bypass} onclick={() => set(p.name, i)}>{c}</button>
              {/each}
            </div>
          {:else}
            <Knob spec={p} value={values[p.name]} disabled={device.bypass} onchange={v => set(p.name, v)} />
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
  .off .body { opacity: 0.45; }
  .err { color: #dc2626; font-size: 12px; padding: 8px; margin: 0; }
</style>
