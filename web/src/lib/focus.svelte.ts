// Sample en cours de la vue Samples (8.E) : la source du sound design. On le
// change dans la vue Samples ; il survit au rechargement (localStorage).

export interface FocusSample {
  source: string
  name: string
  code: string
  folder: string
}

const KEY = 'ui:sample-focus'

function load(): FocusSample | null {
  try { return JSON.parse(localStorage.getItem(KEY) ?? 'null') } catch { return null }
}

class Focus {
  sample = $state<FocusSample | null>(load())

  set(s: FocusSample | null) {
    if (s?.source === this.sample?.source && s?.name === this.sample?.name) return
    this.sample = s
    try { localStorage.setItem(KEY, JSON.stringify(s)) } catch { /* stockage indisponible */ }
  }
}

export const focus = new Focus()
