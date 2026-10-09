// Telecommande de la barre generale : un deck par source (morceaux, samples).
// Chaque vue enregistre le sien (getters sur son propre etat, donc reactifs) ;
// la barre pilote le deck en focus. Une seule source joue a la fois.

export type Source = 'tracks' | 'samples'

export interface Deck {
  /** Ce qui est charge (artiste — titre, nom du sample) ; vide = rien. */
  readonly label: string
  readonly playing: boolean
  readonly looping: boolean
  playPause(): void
  pause(): void
  toggleLoop(): void
  prev(): void
  next(): void
}

class Remote {
  decks = $state.raw<Partial<Record<Source, Deck>>>({})
  focus = $state<Source>('tracks')

  /** Enregistre le deck d'une vue ; renvoie le desenregistrement (onDestroy). */
  register(source: Source, deck: Deck): () => void {
    this.decks = { ...this.decks, [source]: deck }
    return () => {
      if (this.decks[source] !== deck) return
      const { [source]: _, ...rest } = this.decks
      this.decks = rest
    }
  }

  /** A appeler au demarrage de la lecture d'une source : coupe les autres. */
  played(source: Source) {
    this.focus = source
    for (const [s, d] of Object.entries(this.decks) as [Source, Deck][]) {
      if (s !== source && d.playing) d.pause()
    }
  }

  get deck(): Deck | undefined {
    return this.decks[this.focus]
  }
}

export const remote = new Remote()
