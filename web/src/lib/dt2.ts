// Facade Digitakt II (7.G) : hub des controles, de leurs fonctions secondaires
// ([FUNC] + touche), des fiches KB / § du manuel et des numeros MIDI (annexe B).
// Source : manuel DT2 OS 1.17, §3.1 (facade), §11 et annexe A (parametres),
// annexe B (CC / NRPN). Ordre des knobs = ordre du texte du manuel, a verifier
// sur la machine (meme statut draft que les fiches).

const KB = (name: string) => `digitakt/kb/${name}.md`

/** Fonction d'un controle (primaire ou secondaire) et ou la documenter. */
export interface Func {
  label: string
  text: string
  /** Fiche KB (chemin du corpus). */
  kb?: string
  /** Paragraphe du manuel, ex. "10.8.6". */
  manual?: string
}

export interface Control {
  id: string
  /** Libelle serigraphie. */
  label: string
  /** Numero de la legende du §3.1. */
  ref: number
  main: Func
  /** Fonction secondaire, ecrite en orange sur la facade. */
  func?: Func
}

export const CONTROLS: Record<string, Control> = Object.fromEntries(([
  { id: 'volume', label: 'MAIN VOLUME', ref: 1,
    main: { label: 'Volume principal', text: 'Volume des sorties principales et du casque.', kb: KB('mixer-setup'), manual: '3.1' } },
  { id: 'preset', label: 'PRESET/KIT', ref: 2,
    main: { label: 'Menu PRESET/KIT', text: 'Gestion des presets et des kits.', kb: KB('presets-kits-pool'), manual: '9.3' },
    func: { label: 'PERFORM KIT', text: 'Mode Perform Kit.', kb: KB('perform-kit-temp-save'), manual: '10.10' } },
  { id: 'settings', label: 'SETTINGS', ref: 3,
    main: { label: 'Menu SETTINGS', text: 'Projets, configuration MIDI, réglages système.', kb: KB('projet-sauvegarde'), manual: '14' },
    func: { label: 'SAVE PROJECT', text: 'Sauvegarde le projet en cours.', kb: KB('projet-sauvegarde'), manual: '14.1' } },
  { id: 'sampling', label: 'SAMPLING', ref: 4,
    main: { label: 'Menu SAMPLING', text: 'Échantillonnage des entrées ou du resampling interne.', kb: KB('sampling-resampling'), manual: '13.1' },
    func: { label: 'SAMPLES', text: 'Menu SAMPLES (gestion des samples).', kb: KB('sampling-resampling'), manual: '13' } },
  { id: 'tempo', label: 'TEMPO', ref: 5,
    main: { label: 'Menu TEMPO', text: 'Tempo global ou du pattern, swing, métronome.', kb: KB('tempo-metronome'), manual: '7.3' },
    func: { label: 'TAP TEMPO', text: 'Tap tempo.', kb: KB('tempo-metronome'), manual: '7.3' } },
  { id: 'no', label: 'NO', ref: 6,
    main: { label: 'NO', text: 'Sortir d’un menu, revenir d’un cran, refuser.', manual: '6.1' },
    func: { label: 'RELOAD', text: 'Recharge le pattern actif depuis sa sauvegarde temporaire.', kb: KB('perform-kit-temp-save'), manual: '10.8.6' } },
  { id: 'yes', label: 'YES', ref: 7,
    main: { label: 'YES', text: 'Entrer dans un sous-menu, sélectionner, confirmer.', manual: '6.1' },
    func: { label: 'TEMP SAVE', text: 'Sauvegarde temporaire du pattern actif.', kb: KB('perform-kit-temp-save'), manual: '10.8.6' } },
  { id: 'knobs', label: 'DATA ENTRY A-H', ref: 8,
    main: { label: 'Knobs DATA ENTRY', text: 'Valeurs des paramètres de la page active ; appuyer-tourner = pas plus grands. Trig key maintenue + knob = parameter lock.', kb: KB('parameter-preset-locks'), manual: '6.2' } },
  { id: 'p-trig', label: 'TRIG', ref: 9,
    main: { label: 'TRIG PARAMETERS', text: 'Note, vélocité, longueur, conditions du trig (2 pages).', kb: KB('fill-conditions'), manual: '11.2' },
    func: { label: 'QUANTIZE', text: 'Menu QUANTIZE.', kb: KB('enregistrement-quantize'), manual: '10.6' } },
  { id: 'p-src', label: 'SRC', ref: 9,
    main: { label: 'SRC', text: 'Paramètres de la machine source (sample) ; canal, programme sur une track MIDI.', kb: KB('machines-src'), manual: '11.4' },
    func: { label: 'MACHINE', text: 'Choix de la machine SRC / FLTR.', kb: KB('machines-src'), manual: '11.4' } },
  { id: 'p-fltr', label: 'FLTR', ref: 9,
    main: { label: 'FLTR', text: 'Filtre et son enveloppe (2 pages) ; CC 1-8 sur une track MIDI.', kb: KB('filtres'), manual: '11.5' },
    func: { label: 'SETUP', text: 'Menu SETUP (track et pattern).', kb: KB('mixer-setup'), manual: '9.8' } },
  { id: 'p-amp', label: 'AMP', ref: 9,
    main: { label: 'AMP', text: 'Enveloppe d’amplitude, pan, volume ; CC 9-16 sur une track MIDI.', kb: KB('amp-overdrive-bitreduction'), manual: '11.7' },
    func: { label: 'SEQUENCER', text: 'Menu SEQUENCER (mode euclidien).', kb: KB('euclidien'), manual: '10.3' } },
  { id: 'p-fx', label: 'FX', ref: 9,
    main: { label: 'FX', text: 'Bit reduction, overdrive, SRR, niveaux de send.', kb: KB('amp-overdrive-bitreduction'), manual: '11.8' },
    func: { label: 'SEND FX', text: 'Delay, reverb, chorus, compresseur.', kb: KB('send-fx-compresseur'), manual: '12.1' } },
  { id: 'p-mod', label: 'MOD', ref: 9,
    main: { label: 'MOD', text: 'LFO de la track (3 pages, 2 sur une track MIDI).', kb: KB('lfo'), manual: '11.9' },
    func: { label: 'MIXER', text: 'Pages du mixer interne et externe.', kb: KB('mixer-setup'), manual: '12.6' } },
  { id: 'leds', label: 'PATTERN PAGE', ref: 10,
    main: { label: 'LEDs de page', text: 'Nombre de pages du pattern et page active ; la LED clignote sur la page qui joue.', kb: KB('page-setup'), manual: '10.7' } },
  { id: 'arrows', label: 'ARROWS', ref: 11,
    main: { label: 'Flèches', text: 'Navigation dans les menus ; [LEFT]/[RIGHT] + [PTN] changent de bank.', manual: '6.1' } },
  { id: 'page', label: 'PAGE', ref: 12,
    main: { label: 'PAGE', text: 'Page suivante du pattern ; maintenu = mode FILL.', kb: KB('fill-conditions'), manual: '10.8.4' },
    func: { label: 'PAGE SETUP', text: 'Longueur et échelle du pattern.', kb: KB('page-setup'), manual: '10.7' } },
  { id: 'trigs', label: 'TRIG 1-16', ref: 13,
    main: { label: 'Trig keys', text: 'Poser / enlever des trigs, choisir track, pattern, song avec [TRK] [PTN] [SONG], clavier en mode KEYBOARD.', manual: '8.1' },
    func: { label: 'QUICK MUTE', text: 'Mute rapide des tracks.', kb: KB('mutes'), manual: '8.5.3' } },
  { id: 'song', label: 'SONG', ref: 14,
    main: { label: 'SONG', text: 'Choix du song 1-16 avec les trig keys.', kb: KB('song-mode'), manual: '10.9' },
    func: { label: 'SONG EDIT', text: 'Écran d’édition du song.', kb: KB('song-mode'), manual: '10.9.1' } },
  { id: 'ptn', label: 'PTN', ref: 15,
    main: { label: 'PTN', text: 'Choix du pattern (trig keys) et de la bank ([LEFT]/[RIGHT]).', kb: KB('patterns-chaines'), manual: '10.1.1' },
    func: { label: 'BANK', text: 'Sélection de la bank.', kb: KB('patterns-chaines'), manual: '10.1.1' } },
  { id: 'trk', label: 'TRK', ref: 16,
    main: { label: 'TRK', text: '[TRK] + trig key = choisir la track à éditer.', kb: KB('tracks-midi'), manual: '8.5.4' },
    func: { label: 'MUTE', text: 'Mode MUTE : les trig keys mutent les tracks.', kb: KB('mutes'), manual: '8.5.3' } },
  { id: 'stop', label: 'STOP', ref: 17,
    main: { label: 'STOP', text: 'Arrête la lecture ; PLAY reprend au début du pattern.', kb: KB('patterns-chaines'), manual: '10.1.2' },
    func: { label: 'PASTE', text: 'Coller.', kb: KB('copier-coller'), manual: '6.4' } },
  { id: 'play', label: 'PLAY', ref: 18,
    main: { label: 'PLAY', text: 'Lance la lecture ; second appui = pause.', kb: KB('patterns-chaines'), manual: '10.1.2' },
    func: { label: 'CLEAR', text: 'Effacer.', kb: KB('copier-coller'), manual: '6.4' } },
  { id: 'record', label: 'RECORD', ref: 19,
    main: { label: 'RECORD', text: 'GRID RECORDING ; + [PLAY] = LIVE RECORDING ; + [STOP] = STEP RECORDING.', kb: KB('enregistrement-quantize'), manual: '10.2.2' },
    func: { label: 'COPY', text: 'Copier.', kb: KB('copier-coller'), manual: '6.4' } },
  { id: 'keyboard', label: 'KEYBOARD', ref: 20,
    main: { label: 'KEYBOARD', text: 'Mode clavier : les trig keys jouent la track en chromatique.', manual: '8.5.1' },
    func: { label: 'KEYBOARD SETUP', text: 'Gamme, note fondamentale, fold du clavier.', manual: '8.5.2' } },
  { id: 'func', label: 'FUNC', ref: 21,
    main: { label: 'FUNC', text: 'Maintenu + une touche = fonction secondaire (en orange). Ici : bascule.', manual: '6.2.3' } },
  { id: 'level', label: 'LEVEL/DATA', ref: 22,
    main: { label: 'LEVEL/DATA', text: 'Niveau de la track active ; défilement des listes.', kb: KB('mixer-setup'), manual: '3.1' },
    func: { label: 'PRESET MANAGER', text: 'Gestionnaire de presets ; ouvre aussi le pool pour les preset locks.', kb: KB('presets-kits-pool'), manual: '9.2' } },
  { id: 'screen', label: 'SCREEN', ref: 23,
    main: { label: 'Écran', text: 'Page active, paramètres, menus.', manual: '6.1' } },
] satisfies Control[]).map(c => [c.id, c]))

/** Parametre d'un knob A-H et son pilotage MIDI (annexe B, sur le canal de la track). */
export interface Param {
  key: string
  name: string
  cc?: number
  /** NRPN MSB:LSB. */
  nrpn?: string
  /** Numero lu dans l'annexe sans colonne sure (extraction PDF), a verifier. */
  raw?: number
}

export interface ParamPage {
  id: string
  /** Touche PARAMETER qui ouvre la page. */
  key: string
  title: string
  manual: string
  kb: string
  /** Remarque affichee sous les knobs (machine par defaut, positions). */
  note?: string
  params: (Param | null)[]
}

const p = (key: string, name: string, cc?: number, nrpn?: string): Param => ({ key, name, cc, nrpn })
const lfo = (n: number, cc: number[], lsb: number[]): (Param | null)[] => [
  p('SPD', 'Speed', cc[0], `1:${lsb[0]}`), p('MULT', 'Multiplier', cc[1], `1:${lsb[1]}`),
  p('FADE', 'Fade In/Out', cc[2], `1:${lsb[2]}`), p('DEST', 'Destination', cc[3], `1:${lsb[3]}`),
  p('WAVE', 'Waveform', cc[4], `1:${lsb[4]}`), p('SPH', 'Start Phase', cc[5], `1:${lsb[5]}`),
  p('MODE', 'Trig Mode', cc[6], `1:${lsb[6]}`), p('DEP', `Depth LFO ${n}`, cc[7], `1:${lsb[7]}`),
]

/** Pages de parametres d'une track audio ; plusieurs appuis sur la touche = page suivante. */
export const PARAM_PAGES: ParamPage[] = [
  { id: 'trig1', key: 'p-trig', title: 'TRIG 1', manual: '11.2', kb: KB('fill-conditions'),
    params: [p('NOTE', 'Note', 3, '3:0'), p('VEL', 'Velocity', 4, '3:1'), p('LEN', 'Length', 5, '3:2'),
      p('PROB', 'Probability'), { key: 'LFO.T', name: 'LFO Trig', raw: 14 },
      { key: 'FLT.T', name: 'Filter Trig', raw: 13 }, p('FILL', 'Fill'), p('COND', 'Condition')] },
  { id: 'trig2', key: 'p-trig', title: 'TRIG 2', manual: '11.3', kb: KB('microtiming-retrigs'),
    note: '6 paramètres sur cette page : position sur les knobs à vérifier.',
    params: [p('RTRG', 'Retrig'), p('VFAD', 'Velocity Fade'), p('LEN', 'Retrig Length'), p('RATE', 'Retrig Rate'),
      p('PTIM', 'Portamento Time', 9, '3:7'), p('PORT', 'Portamento On/Off', 65, '3:8'), null, null] },
  { id: 'src', key: 'p-src', title: 'SRC · ONESHOT', manual: '11.4', kb: KB('machines-src'),
    note: 'Machine par défaut ONESHOT (annexe A.2.1) ; C sans libellé dans le manuel, CC 24 = Sample Bank Select.',
    params: [p('TUNE', 'Tune', 16, '1:0'), p('PLAY', 'Play Mode', 17, '1:1'), null, p('SAMP', 'Sample Slot', 19, '1:8'),
      p('STRT', 'Start (knob E)', 20, '1:4'), p('LEN', 'Length (knob F)', 21, '1:5'), p('LOOP', 'Loop (knob G)', 22, '1:6'),
      p('LEV', 'Sample Level', 23, '1:7')] },
  { id: 'fltr1', key: 'p-fltr', title: 'FLTR 1 · MULTI-MODE', manual: '11.5', kb: KB('filtres'),
    note: 'Machine par défaut MULTI-MODE (annexe A.3.1) ; F et G changent avec la machine.',
    params: [p('ATK', 'Attack', 70, '1:16'), p('DEC', 'Decay', 71, '1:17'), p('SUS', 'Sustain', 72, '1:18'),
      p('REL', 'Release', 73, '1:19'), p('FREQ', 'Frequency', 74, '1:20'), p('RESO', 'Resonance', 75, '1:21'),
      p('TYPE', 'Type', 76, '1:22'), p('ENV', 'Env. Depth', 77, '1:23')] },
  { id: 'fltr2', key: 'p-fltr', title: 'FLTR 2 · BASE-WIDTH', manual: '11.6', kb: KB('filtres'),
    note: '6 paramètres ; Env. Delay et Env. Depth tous deux en NRPN 1:23 dans l’annexe, à tester.',
    params: [p('DEL', 'Env. Delay', 91, '1:23'), p('KEY.T', 'Key Tracking', 92, '1:69'), p('BASE', 'Base', 26, '1:51'),
      p('WIDTH', 'Width', 27, '1:52'), p('BW.RT', 'Base-Width Routing'), p('RSET', 'Env. Reset', 111, '1:68'), null, null] },
  { id: 'amp', key: 'p-amp', title: 'AMP', manual: '11.7', kb: KB('amp-overdrive-bitreduction'),
    note: '9 paramètres dans le manuel pour 8 knobs : VOL (CC 89, NRPN 1:39) hors grille, position à vérifier.',
    params: [p('ATK', 'Attack', 79, '1:30'), p('HOLD', 'Hold', 80, '1:31'), p('DEC', 'Decay', 81, '1:32'),
      p('SUS', 'Sustain', 82, '1:33'), p('REL', 'Release', 83, '1:34'), p('RSET', 'Env. Reset', 88, '1:41'),
      p('MODE', 'Env. Mode', 87, '1:40'), p('PAN', 'Pan', 90, '1:38')] },
  { id: 'fx', key: 'p-fx', title: 'FX', manual: '11.8', kb: KB('amp-overdrive-bitreduction'),
    note: 'BR, OVER, SRR, ROUT : un seul numéro dans l’annexe (CC ou NRPN ?), à vérifier au moniteur MIDI.',
    params: [{ key: 'BR', name: 'Bit Reduction', raw: 54 }, { key: 'OVER', name: 'Overdrive', raw: 57 },
      { key: 'SRR', name: 'Sample Rate Reduction', raw: 55 }, { key: 'ROUT', name: 'SRR Routing', raw: 56 },
      p('DEL', 'Delay Send', 84, '1:36'), p('REV', 'Reverb Send', 85, '1:37'), p('CHR', 'Chorus Send', 12, '1:35'),
      p('OD.RT', 'Overdrive Routing')] },
  { id: 'mod1', key: 'p-mod', title: 'MOD 1 · LFO 1', manual: '11.9', kb: KB('lfo'),
    note: 'SPD et DEP en haute résolution (CC LSB 58 / 59).',
    params: lfo(1, [102, 103, 104, 105, 106, 107, 108, 109], [42, 43, 44, 45, 46, 47, 48, 49]) },
  { id: 'mod2', key: 'p-mod', title: 'MOD 2 · LFO 2', manual: '11.10', kb: KB('lfo'),
    note: 'SPD et DEP en haute résolution (CC LSB 60 / 61).',
    params: lfo(2, [112, 113, 114, 115, 116, 117, 118, 119], [50, 51, 52, 53, 54, 55, 56, 57]) },
  { id: 'mod3', key: 'p-mod', title: 'MOD 3 · LFO 3', manual: '11.11', kb: KB('lfo'),
    note: 'Absent sur les tracks MIDI ; SPD et DEP en haute résolution (CC LSB 62 / 63).',
    params: lfo(3, [78, 52, 53, 28, 29, 30, 31, 86], [58, 59, 60, 61, 62, 70, 71, 72]) },
]

export const KNOBS = 'ABCDEFGH'

/** Pages ouvertes par une touche PARAMETER, dans l'ordre des appuis successifs. */
export const pagesOf = (key: string) => PARAM_PAGES.filter(pg => pg.key === key)

/** Libelle MIDI d'un parametre, ex. « CC 74 · NRPN 1:20 ». */
export function midiLabel(param: Param): string {
  if (param.raw !== undefined) return `n° ${param.raw} (CC ou NRPN ? à vérifier)`
  const parts = [param.cc !== undefined ? `CC ${param.cc}` : '', param.nrpn ? `NRPN ${param.nrpn}` : '']
  return parts.filter(Boolean).join(' · ') || 'pas de CC / NRPN dans l’annexe B'
}
