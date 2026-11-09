# Changelog — mk-brain

Format [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Chaque slice
de `SPEC.md` § Phases = une entrée balisée `[N]` et une version mineure.

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
