// Sample en cours de la vue Samples (8.E) : la source du sound design. On le
// change dans la vue Samples ; il survit au rechargement (localStorage).
// Layering (8.J) : buffer de couches 1.. a cote de cette source (couche 0).
// « + couche » passe en mode choix : la vue Samples ne change plus la source,
// son sample en cours devient le candidat, ajoute par « Ajouter comme couche ».
// Badge « versé » d'un rendu : la vue Samples ouvre son dossier et le
// selectionne, sans en faire la source du sound design.

export interface FocusSample {
  source: string
  name: string
  code: string
  folder: string
}

const KEY = 'ui:sample-focus'
const LAYERS_KEY = 'ui:sd-layers'
export const MAX_LAYERS = 3   // couches en plus de la source (MAX_LAYERS - 1 du moteur)

function load<T>(key: string, fallback: T): T {
  try { return JSON.parse(localStorage.getItem(key) ?? 'null') ?? fallback } catch { return fallback }
}
function store(key: string, v: unknown) {
  try { localStorage.setItem(key, JSON.stringify(v)) } catch { /* stockage indisponible */ }
}

class Focus {
  sample = $state<FocusSample | null>(load(KEY, null))
  layers = $state<FocusSample[]>(load(LAYERS_KEY, []))
  picking = $state(false)
  candidate = $state<FocusSample | null>(null)
  private onpicked: (() => void) | null = null
  /** Sample a montrer dans la vue Samples (consomme par elle). */
  reveal = $state<{ folder: string; source: string } | null>(null)

  set(s: FocusSample | null) {
    if (this.picking) { this.candidate = s; return }
    if (s?.source === this.sample?.source && s?.name === this.sample?.name) return
    this.sample = s
    store(KEY, s)
  }

  /** Mode choix d'une couche ; `done` est rappele a l'ajout comme a l'annulation. */
  startPick(done: () => void) {
    this.picking = true
    this.candidate = null
    this.onpicked = done
  }

  endPick(add: boolean) {
    const c = this.candidate
    if (add && c && c.source !== this.sample?.source && !this.layers.some(l => l.source === c.source)
        && this.layers.length < MAX_LAYERS) {
      this.layers = [...this.layers, c]
      store(LAYERS_KEY, this.layers)
    }
    this.picking = false
    this.candidate = null
    const done = this.onpicked
    this.onpicked = null
    done?.()
  }

  show(folder: string, source: string) {
    this.reveal = { folder, source }
  }

  removeLayer(i: number) {
    this.layers = this.layers.filter((_, j) => j !== i)
    store(LAYERS_KEY, this.layers)
  }
}

export const focus = new Focus()
