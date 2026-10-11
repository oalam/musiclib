<script lang="ts">
  // Boite « Source » d'une chaine (8.J), en tete de ses devices : couche lue
  // (0 = source principale), decalage de l'attaque apres calage automatique
  // sur celle de la source, et gain de fin (↗) : le melange des couches varie
  // dans le temps, ou d'une tranche a l'autre en variations.
  import type { ParamSpec, SdChain } from '../api'
  import type { FocusSample } from '../focus.svelte'
  import Knob from './Knob.svelte'

  let { chain, layers, slices = false }: {
    chain: SdChain
    layers: FocusSample[]
    slices?: boolean
  } = $props()

  const OFFSET: ParamSpec = { name: 'offset_ms', label: 'Décalage', min: -50, max: 50, default: 0, unit: 'ms',
    scale: 'lin', step: 0.5, choices: null,
    help: 'Attaque de la chaîne par rapport à celle de la source, après calage automatique (+ = plus tard)' }
  const GAIN: ParamSpec = { name: 'gain_db_end', label: slices ? 'tranche N' : 'gain fin', min: -60, max: 24, default: 0,
    unit: 'dB', scale: 'lin', step: null, choices: null, help: 'Gain atteint en fin de rendu (ou à la dernière tranche)' }

  const layer = $derived(chain.layer ?? 0)
  function setLayer(i: number) { if (i) chain.layer = i; else delete chain.layer }
  function setOffset(v: number) { if (v) chain.offset_ms = v; else delete chain.offset_ms }
  function toggleGainEnd() {
    if (chain.gain_db_end === undefined) chain.gain_db_end = chain.gain_db
    else delete chain.gain_db_end
  }
</script>

<section class="src">
  <header><span class="title">Source</span></header>
  <select class="small" value={layer} onchange={e => setLayer(Number(e.currentTarget.value))}
    title="Sample lu par cette chaîne : la source, ou une couche ajoutée">
    <option value={0}>Source</option>
    {#each layers as l, i (l.source)}<option value={i + 1}>C{i + 1} · {l.name}</option>{/each}
    {#if layer > layers.length}<option value={layer} disabled>C{layer} · absente</option>{/if}
  </select>
  {#if layer > layers.length}<p class="err">Couche C{layer} absente : l'ajouter (+ couche) ou changer de source.</p>{/if}
  <div class="knobs">
    <Knob spec={OFFSET} value={chain.offset_ms ?? 0} onchange={setOffset} />
    <div class="param" class:auto={chain.gain_db_end !== undefined}>
      {#if chain.gain_db_end !== undefined}
        <Knob spec={GAIN} value={chain.gain_db_end} onchange={v => (chain.gain_db_end = v)} />
      {/if}
      <button class="autob" class:on={chain.gain_db_end !== undefined} onclick={toggleGainEnd}
        aria-pressed={chain.gain_db_end !== undefined}
        title={chain.gain_db_end !== undefined ? 'Retirer l\'automation du gain' : slices
          ? 'Mélange variable : le gain de la chaîne va de son fader (tranche 2) à une valeur de fin (dernière tranche)'
          : 'Mélange variable : le gain de la chaîne va de son fader à une valeur de fin sur la durée du rendu'}>↗ gain</button>
    </div>
  </div>
</section>

<style>
  .src { border: 1px solid var(--border); border-radius: 5px; background: var(--panel-2); padding: 4px 6px 6px; display: flex; flex-direction: column; gap: 6px; min-width: 120px; max-width: 170px; }
  header { display: flex; align-items: center; gap: 4px; }
  .title { font-size: 12px; font-weight: 600; }
  select { max-width: 100%; }
  .knobs { display: flex; gap: 6px; justify-content: center; align-items: flex-start; }
  .param { display: flex; flex-direction: column; align-items: center; gap: 2px; }
  .param.auto { background: color-mix(in srgb, var(--accent) 10%, transparent); border-radius: 4px; }
  .autob { padding: 0 5px; font-size: 10px; line-height: 14px; background: none; border-color: transparent; color: var(--muted); }
  .autob.on { color: var(--accent); border-color: var(--accent); }
  .err { color: #dc2626; font-size: 11px; margin: 0; }
  .small { font-size: 12px; }
</style>
