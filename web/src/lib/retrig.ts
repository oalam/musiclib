// Relance d'un sample a chaque temps (noire) tant qu'une touche est tenue
// (Espace de la vue Samples, tempo de la banque active du live). Chaque coup
// est coupe au temps suivant, avec un fondu de 5 ms contre les clics ;
// ordonnancement Web Audio avec anticipation, independant des timers.

const LOOKAHEAD = 0.1     // s programmees d'avance
const TICK = 25           // ms entre deux passages de l'ordonnanceur
const FADE = 0.005        // s

let ctx: AudioContext | null = null
const buffers = new Map<string, Promise<AudioBuffer>>()
let timer: ReturnType<typeof setInterval> | null = null
let voices: { src: AudioBufferSourceNode; gain: GainNode }[] = []
let token = 0             // invalide un demarrage encore en chargement

function audio(): AudioContext {
  ctx ??= new AudioContext()
  return ctx
}

function load(url: string): Promise<AudioBuffer> {
  let p = buffers.get(url)
  if (!p) {
    p = fetch(url).then(r => r.arrayBuffer()).then(b => audio().decodeAudioData(b))
    p.catch(() => buffers.delete(url))
    buffers.set(url, p)
  }
  return p
}

function hit(buf: AudioBuffer, at: number, period: number) {
  const c = audio()
  const src = c.createBufferSource()
  const gain = c.createGain()
  src.buffer = buf
  src.connect(gain).connect(c.destination)
  const end = at + period
  if (buf.duration > period) {
    gain.gain.setValueAtTime(1, end - FADE)
    gain.gain.linearRampToValueAtTime(0, end)
  }
  src.start(at)
  src.stop(end)
  const v = { src, gain }
  voices.push(v)
  src.onended = () => { voices = voices.filter(x => x !== v) }
}

/** Demarre la relance de `url` a `bpm` ; un nouvel appel remplace le precedent. */
export async function start(url: string, bpm: number): Promise<void> {
  stop()
  const mine = ++token
  const c = audio()
  if (c.state === 'suspended') await c.resume()
  const buf = await load(url)
  if (mine !== token) return          // touche relachee pendant le chargement
  const period = 60 / bpm
  let next = c.currentTime + 0.01
  const schedule = () => {
    while (next < c.currentTime + LOOKAHEAD) {
      hit(buf, next, period)
      next += period
    }
  }
  schedule()
  timer = setInterval(schedule, TICK)
}

/** Arrete tout de suite (fondu court), y compris un demarrage en chargement. */
export function stop(): void {
  token++
  if (timer) clearInterval(timer)
  timer = null
  if (!ctx) return
  const now = ctx.currentTime
  for (const { src, gain } of voices) {
    gain.gain.cancelScheduledValues(now)
    gain.gain.setValueAtTime(gain.gain.value, now)
    gain.gain.linearRampToValueAtTime(0, now + FADE)
    try { src.stop(now + FADE) } catch { /* pas encore demarre : deja programme */ }
  }
  voices = []
}

export const running = () => timer !== null
