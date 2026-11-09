# Changelog — mk-brain

Format [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Chaque slice
de `SPEC.md` § Phases = une entrée balisée `[N]` et une version mineure.

## [0.7.1] - 2026-11-09

### Corrigé

- [5] 5.B En live, la track sélectionnée (SELECT + pad) n'était repérée
  que SELECT tenu : son pad reste allumé à mi-intensité (`leds.selected`,
  0.5), plein à la frappe.

## [0.7.0] - 2026-11-09

### Ajouté

- [5] 5.B `modes.py` : modes live / design ; SHIFT + CONTROL tenus 1 s
  proposent l'autre mode, appui sur l'encodeur maître = confirmer (5 s,
  tout autre bouton annule) ; refusé en live transport lancé, à la
  proposition comme à la confirmation.
- [5] 5.B Moteur : live = pads en rythmique, GROUP seul sans effet ;
  design = disposition par GROUP ou PAD MODE (B chromatique au départ),
  encodeurs sur l'AUTO CHANNEL avec rappel `DT2 en LIVE REC ?`, SELECT +
  pad 16 permis ; quantize propre à chaque mode (off en design).
- [5] 5.B LED : CONTROL pleine en design ou proposition en attente,
  atténuée en live ; PAD MODE en design ; GROUP éteints en live arrêté.
- [5] 5.B `play` : écran gauche bordé avec bandeau `DESIGN`, proposition
  de bascule sur l'écran droit (`display.text_image(..., framed=)`).

## [0.6.2] - 2026-11-09

### Ajouté

- [5] 5.A Banque inconnue au lancement : PATTERN + GROUP A-H la choisit
  sans rien envoyer (LED GROUP = banque tant que PATTERN est tenu) ; la
  banque apprise d'un PC est journalisée.

## [0.6.1] - 2026-11-09

### Corrigé

- [5] 5.A Saut de valeur après un bouton tourné sur la DT2 : elle envoie
  ses boutons sur l'AUTO CHANNEL, pas sur le canal de la track ; ces CC
  vont désormais à la track sélectionnée sur la MK2 (mute ignoré).

## [0.6.0] - 2026-11-09

### Ajouté

- [5] 5.A `faders.py` : valeurs des 8 paramètres par track (64 si jamais
  vues), apprises des CC reçus de la DT2 (`ENCODER DEST` / `MUTE DEST` =
  `INT + EXT`), « hors prise » après un changement de pattern, restes de
  rotation cumulés (4 unités brutes par cran), mutes.
- [5] 5.A Moteur : 8 encodeurs → CC sur le canal de la track
  sélectionnée ; SELECT + pad = track des encodeurs, MUTE + pad = CC 94,
  PATTERN + pad = Program Change dans la banque du dernier PC reçu
  (refusé, « banque ? », tant qu'aucun n'est arrivé) ; un pad frappé avec
  un modificateur ne joue pas de note ; track de l'AUTO CHANNEL refusée.
- [5] 5.A LED : SELECT, MUTE, PATTERN atténués, pleins tenus ; MUTE tenu =
  tracks ouvertes allumées, mutées éteintes ; SELECT tenu = track choisie.
- [5] 5.A MIDI : envoi de CC et Program Change, réception des CC ;
  config `encoders` (page, `mute_cc`, `raw_per_step`) et
  `midi.program_channel` ; `play` affiche la track et le dernier geste.

## [0.5.1] - 2026-11-09

### Corrigé

- [4] Écrans peu lisibles (6 lu comme 8) : texte en police vectorielle
  intégrée à Pillow (présente aussi sur le Pi), taille 13, toujours
  5 lignes, au lieu de la police bitmap fine ; gras (1 px) réservé aux
  libellés (`text_image(..., bold=)`) : disposition et alerte dans `play`.

## [0.5.0] - 2026-11-09

### Ajouté

- [4] `phrase.py` : compteur de phrases pur (mesure 1-32/64, numéro de
  phrase, temps, cap 16/32/64, 4 dernières mesures, compte à rebours
  `-2` / `-1`, blocs de 8 mesures), remise à zéro différée à la barre
  suivante, nom de pattern depuis le Program Change (`36` → `C05`).
- [4] Moteur : Start, Stop et Program Change reçus de la DT2
  (`midi_io.feed_engine`) ; PC transport lancé = mesure 1 à la barre
  suivante, ignoré à l'arrêt, oublié si un Stop suit ; SHIFT + PLAY =
  mesure 1, SHIFT + GROUP n = début du bloc n, à la barre suivante.
- [4] LED : transport lancé, GROUP A-H = un bloc de 8 mesures allumé de
  plus toutes les 8 mesures, le bloc clignote au temps pendant la dernière
  mesure avant un cap ; PLAY pulse sur le 1.
- [4] `play` : écran droit `mesure/longueur` et pattern en gros, `*` dans
  les 4 dernières mesures, `-2` / `-1` avant un cap ; recalages, Start et
  Stop journalisés avec la position.
- [4] Config : `play.phrase` (32 ou 64), `leds.phrase` (couleur).

## [0.4.0] - 2026-11-09

### Ajouté

- [3] `quantize.py` : quantize « nearest » 1/16 et 1/8 (moitié du pas =
  immédiat), swing 50-75 % sur les 16ᵉ impairs.
- [3] `repeat.py` : 8 divisions du note repeat (1/4 à 1/64, triolets).
- [3] Moteur : messages datés confiés à l'ordonnanceur ; GRID fait défiler
  off / 1/16 / 1/8 ; SWING + encodeur maître règle le swing ; NOTE REPEAT
  tenu + pad = repeat, vélocité = pression courante, boutons d'écran 1-8 =
  division, SHIFT + NOTE REPEAT verrouille ; note off jamais avant sa note
  on quantizée ; LED GRID, SWING, NOTE REPEAT et division.
- [3] `play` : état `Q16 SW50 R1/16` à l'écran gauche, division en très
  gros pendant NOTE REPEAT ; section `play:` de la config (réglages de
  départ).
- [3] `ClockTracker.ticks_at` : position fractionnaire d'un instant.
- [3] Diagnostic par frappe dans `play` : position, pas visé, écart en
  ms, décision (immédiat ou retardé).
- [3] Essai sur la DT2 : frappes avant le pas posées sur la grille ; la
  quantize de l'enregistrement reste à la DT2 (décidé, cf. `SPEC.md`).

## [0.3.1] - 2026-11-09

### Modifié

- [1] Courbe de vélocité : `gamma` 0,6 → 0,4 et `full_scale` 2500 → 2000,
  les frappes légères sortaient à 2-14.

## [0.3.0] - 2026-11-09

### Ajouté

- [2] `clock.py` : suivi de la clock DT2 par régression linéaire sur 24
  ticks (période, phase, BPM à 0,1), Start / Continue / Stop, position
  mesure.temps.pas, détection du sysex Elektron (Transfer ouvert), écart
  d'arrivée des ticks à la prévision.
- [2] `scheduler.py` : envoi à l'instant cible (sommeil puis attente active
  sur 0,5 ms), écart d'envoi mesuré, abandon au-delà de 20 ms de retard.
- [2] `midi_io.py` : entrée DT2 horodatée dans le callback, `feed_clock`.
- [2] `mk-brain clock [--bench-note N --every T]` : BPM, transport,
  bilan de gigue ; banc d'envoi d'une note sur la grille.
- [2] `mk-brain play` : BPM, transport et position à l'écran gauche, note
  jouée avec degré et nom (`pad 3 -> b3 (D#5, 63)`), alerte Transfer ou
  clock absente.
- [2] Banc sur la DT2 : BPM à 0,1 près, envoi à 0,17 ms rms (p99
  0,72 ms), sans flam à l'oreille (constats dans `SPEC.md`).

### Corrigé

- [2] Ordonnanceur en retard de 1,3 ms en moyenne : attentes découpées
  (2 ms), attente active de 2 ms qui cède le GIL, bascule de fil à 0,2 ms.

## [0.2.0] - 2026-11-09

### Ajouté

- [1] `config/default.yaml` et `config.py` (Pydantic, `ConfigError`) :
  AUTO CHANNEL, courbe de vélocité, couleurs des rôles, des familles et
  des 16 tracks, dispositions A-H du template DT2 Pads.
- [1] `layouts.py` : note et couleur de chaque pad (rythmique pad n =
  track n, chromatique, gammes), courbe pression → vélocité.
- [1] `engine.py` : moteur pur, vélocité = pression maximale sur une
  fenêtre de 2 ms après l'attaque, note off sur la note réellement jouée,
  LED vives à la frappe et atténuées au repos ; GROUP A-H choisit la
  disposition (provisoire, à revoir à la slice 5).
- [1] `midi_io.py` (mido + python-rtmidi, `MidiError`) et
  `mk-brain play [--dry-run]`.
- [1] Essai sur la DT2 : tracks 1-16 en disposition A, gamme sur la track
  active une fois l'AUTO CHANNEL de la DT2 passé de 10 à 16.

### Modifié

- [1] Disposition A : pad n = track n sur les 16 pads (décision « Pads en
  live »), au lieu des tracks 1-8 doublées du template 7.D.

## [0.1.0] - 2026-11-09

### Ajouté

- [0] Paquet `mk-brain` (Python 3.12, hidapi, Pillow ; ruff, mypy strict,
  pytest) et CLI `mk-brain`.
- [0] `hid_mk2.py` : décodage des rapports MK2 repris de cabl (boutons et
  encodeurs 0x01, pads 0x20), rapports LED 0x80/0x81/0x82, accès hidapi,
  exceptions typées `Mk2NotFoundError`, `Mk2OpenError`, `Mk2ReportError`.
- [0] `display.py` : image Pillow 1 bit → 8 rapports `0xE0|écran` de 256
  octets, mire de test.
- [0] `mk-brain list` et `mk-brain spike` : mire sur les deux écrans,
  balayage des LED, écho des contrôles (LED et écran droit), bilan des
  contrôles jamais vus.
- [0] Essai sur la MK2 : mire nette sur les deux écrans, LED justes,
  48 boutons, 16 pads et 9 encodeurs décodés (constats dans `SPEC.md`).

### Modifié

- [0] Bouton `MAIN` de cabl renommé `MASTER_PUSH` (appui sur l'encodeur
  maître, vérifié).
