<script lang="ts">
  // Colonne laterale du sound design (8.H) : traitements depliables sur
  // leurs presets ; la mini barre d'outils agit sur les presets (nouveau dans
  // le traitement ouvert, modifier nom / description, supprimer le preset
  // ouvert). Les traitements eux-memes sont definis dans le moteur.
  import type { SdPreset, TreatmentSpec } from '../api'

  let { treatments, presets, current, preset, dirty, onopen, onnew, onedit, ondelete }: {
    treatments: TreatmentSpec[]
    presets: Record<string, SdPreset[]>
    current: string | null          // traitement ouvert
    preset: string | null           // preset ouvert
    dirty: boolean
    onopen: (treatment: TreatmentSpec, preset: SdPreset) => void
    onnew: () => void
    onedit: () => void
    ondelete: () => void
  } = $props()

  let open = $state<Record<string, boolean>>({})
  const isOpen = (id: string) => open[id] ?? id === current
  const canDelete = $derived(!!current && (presets[current]?.length ?? 0) > 1)
</script>

{#snippet icon(name: 'new' | 'edit' | 'delete')}
  <svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    {#if name === 'new'}<path d="M12 5v14M5 12h14" />
    {:else if name === 'edit'}<path d="M4 20h4L19 9l-4-4L4 16z" /><path d="m13.5 6.5 4 4" />
    {:else}<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3" />{/if}
  </svg>
{/snippet}

<nav class="side" aria-label="Traitements et presets">
  <div class="tools" role="toolbar" aria-label="Presets">
    <span class="small muted head">Traitements</span>
    <button class="ic" onclick={onnew} disabled={!current} title="Nouveau preset dans le traitement ouvert">{@render icon('new')}</button>
    <button class="ic" onclick={onedit} disabled={!preset} title="Modifier le nom et la description du preset">{@render icon('edit')}</button>
    <button class="ic" onclick={ondelete} disabled={!canDelete}
      title={canDelete ? 'Supprimer le preset ouvert (versionné par git)' : 'Le dernier preset d\'un traitement ne se supprime pas'}>{@render icon('delete')}</button>
  </div>
  <ul class="tree">
    {#each treatments as t (t.id)}
      <li>
        <button class="tnode" class:cur={t.id === current} aria-expanded={isOpen(t.id)}
          onclick={() => (open[t.id] = !isOpen(t.id))} title={t.summary}>
          <span class="caret" aria-hidden="true">{isOpen(t.id) ? '▾' : '▸'}</span>
          <span class="tlabel">{t.label}</span>
          <span class="muted small mono" title={t.code ? 'Code DT2 et dossier du rendu versé' : 'Rangé avec la source (même code, même dossier)'}>{t.code ? `${t.code}${t.sub ? `/${t.sub}` : ''}` : '= source'}</span>
        </button>
        {#if isOpen(t.id)}
          <ul>
            {#each presets[t.id] ?? [] as p (p.id)}
              <li>
                <button class="pnode small" class:sel={t.id === current && p.id === preset}
                  onclick={() => onopen(t, p)} title={p.description || p.label}>
                  {p.label}{#if t.id === current && p.id === preset && dirty}<span class="dirty"> •</span>{/if}
                </button>
              </li>
            {:else}<li class="muted small empty">aucun preset</li>{/each}
          </ul>
        {/if}
      </li>
    {/each}
  </ul>
</nav>

<style>
  .side { display: flex; flex-direction: column; gap: 6px; min-height: 0; }
  .tools { display: flex; align-items: center; gap: 2px; padding-bottom: 4px; border-bottom: 1px solid var(--border); }
  .head { flex: 1; text-transform: uppercase; letter-spacing: 0.04em; font-size: 11px; }
  .ic { padding: 3px 5px; line-height: 0; background: none; border-color: transparent; color: var(--muted); }
  .ic:hover:not(:disabled) { color: var(--text); border-color: var(--border); }
  .ic:disabled { opacity: 0.35; }
  ul { list-style: none; margin: 0; padding: 0; }
  .tree { overflow-y: auto; display: flex; flex-direction: column; gap: 2px; }
  .tree ul { padding-left: 16px; display: flex; flex-direction: column; gap: 1px; margin: 2px 0 4px; }
  .tnode, .pnode { width: 100%; text-align: left; background: none; border-color: transparent; display: flex; align-items: center; gap: 6px; padding: 3px 6px; }
  .tnode { font-weight: 600; font-size: 13px; }
  .tnode.cur .tlabel { color: var(--accent); }
  .tlabel { flex: 1; }
  .caret { width: 10px; color: var(--muted); }
  .pnode { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block; }
  .pnode:hover, .tnode:hover { background: var(--panel-2); }
  .pnode.sel { background: var(--panel-2); border-color: var(--accent); }
  .dirty { color: var(--accent); }
  .empty { padding: 3px 6px; }
  .small { font-size: 12px; }
</style>
