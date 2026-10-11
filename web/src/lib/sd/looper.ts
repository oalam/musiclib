// Lecteur de boucle Web Audio : boucle sans trou (contrairement a <audio loop>)
// et remplacement a chaud d'un rendu par le suivant, a la meme phase, avec un
// court fondu enchaine (on tourne un potard pendant que ca joue, comme dans Live).

const FADE = 0.015

export class Looper {
  private ctx: AudioContext | null = null
  private node: { src: AudioBufferSourceNode; gain: GainNode } | null = null
  private startedAt = 0
  private duration = 0
  onstate: (playing: boolean) => void = () => {}

  get playing(): boolean { return this.node !== null }

  /** Position 0..1 dans la boucle qui joue, null a l'arret (tete de lecture). */
  phase(): number | null {
    if (!this.ctx || !this.node || !this.duration) return null
    return ((this.ctx.currentTime - this.startedAt) % this.duration) / this.duration
  }

  async decode(data: ArrayBuffer): Promise<AudioBuffer> {
    this.ctx ??= new AudioContext()
    return this.ctx.decodeAudioData(data)
  }

  /** Lance (ou remplace) la boucle ; garde la phase si une boucle joue deja. */
  play(buf: AudioBuffer) {
    const ctx = this.ctx!
    void ctx.resume()
    const now = ctx.currentTime
    const phase = this.node ? ((now - this.startedAt) % this.duration) / this.duration : 0
    const offset = phase * buf.duration
    this.fadeOut(now)
    const src = ctx.createBufferSource()
    src.buffer = buf
    src.loop = true
    const gain = ctx.createGain()
    gain.gain.setValueAtTime(0, now)
    gain.gain.linearRampToValueAtTime(1, now + FADE)
    src.connect(gain).connect(ctx.destination)
    src.start(now, offset)
    this.node = { src, gain }
    this.startedAt = now - offset
    this.duration = buf.duration
    this.onstate(true)
  }

  stop() {
    if (!this.ctx || !this.node) return
    this.fadeOut(this.ctx.currentTime)
    this.onstate(false)
  }

  private fadeOut(now: number) {
    if (!this.node) return
    const { src, gain } = this.node
    gain.gain.setValueAtTime(gain.gain.value, now)
    gain.gain.linearRampToValueAtTime(0, now + FADE)
    src.stop(now + FADE)
    this.node = null
  }
}
