---
tags: [digitakt, kb]
theme: Machines SRC
lot: 3
ordre: 12
manuel: "§11.4, §13.4, annexe A.1-A.2 (p55, 70, 93-103)"
os: "1.17"
statut: draft
---

# Machines SRC : comment le sample est joué

**En une phrase** : chaque track choisit un moteur de lecture ; ONESHOT pour
les frappes, WERP / STRETCH / REPITCH pour des boucles calées sur le tempo,
SLICE / GRID pour découper une boucle, MIDI pour piloter un synthé.

## Gestes rapides

| Action | Touches |
|---|---|
| Menu MACHINE | `[FUNC] + [SRC]`, `[LEFT]/[RIGHT]` catégorie, `[UP]/[DOWN]`, `[YES]` |
| Page SRC 1 / 2 (forme d'onde) | `[SRC]`, puis `[SRC]` de nouveau |
| Accord à l'octave / au demi-ton | `[FUNC]` + tourner `TUNE` / appuyer en tournant |

| Machine | Usage | Paramètres clés |
|---|---|---|
| ONESHOT (défaut) | kick, clap, hats, one-shots | `TUNE`, `PLAY`, `STRT`, `LEN`, `LOOP` |
| WERP | boucle calée au tempo par segments | `SEG`, `MODE`, `BARS` |
| STRETCH | boucle calée au tempo par grains | `STRT`, `LEN`, `BARS` |
| REPITCH | boucle calée en changeant la hauteur | `BARS` |
| SLICE | tranches éditées à la main | `SLICE`, `LEN` |
| GRID | tranches égales automatiques | `SLICE`, `GRID` |
| MIDI | track MIDI vers un appareil externe | (cf. lot 5) |

## Pas à pas : caler une boucle de percs à 190 BPM

1. Track 8, `[FUNC] + [SRC]`, choisir STRETCH (garde la hauteur) ou
   REPITCH (garde le grain, change la hauteur).
2. `SAMP` : choisir la boucle ; `BARS` = sa longueur réelle en mesures.
3. Un seul trig au pas 1, `LEN` de trig long : la boucle suit le tempo.
4. Variante GRID : découper la boucle en 16 et rejouer les tranches dans un
   autre ordre (lock de `SLICE` par trig, cf. [[parameter-preset-locks]]).

## En live techno

- Kick, rumble, clap, hats : **ONESHOT**, toujours ; le reste se décide au
  son.
- Une boucle de breakbeat ou de percs tribe d'un autre tempo : STRETCH pour
  rester naturel, REPITCH pour l'effet « vinyle accéléré ».
- `PLAY` en REVERSE sur un crash ou une reverb resamplée = montée avant un
  drop, sans LFO.

## Pièges

- Changer de machine change les paramètres de la page SRC ; les locks posés
  sur l'ancienne machine ne s'appliquent plus forcément.
- En boucle (`FORWARD LOOP`), la durée dépend aussi du `LEN` de trig et de
  l'enveloppe AMP (`HOLD`, `DEC`) : un `DEC` court coupe la boucle.
- `TUNE` couvre ±5 octaves ; REPITCH n'a pas de `TUNE` (la hauteur suit le
  tempo).

## À essayer (5 min)

Même boucle sur trois tracks en STRETCH, REPITCH et WERP, à 190 BPM, puis
monter le tempo à 200 et écouter laquelle tient le mieux.

Source : manuel DT2 OS 1.17, §11.4, §13.4, annexe A.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [XNB — DIGITAKT II Machines](https://youtu.be/jcC623awE7E) (vidéo entière) · DT2, 2024
- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=4737) : « SRC page » (1:18:57) · DT2, 2024
- [loopop — DIGITAKT II vs OG Digitakt, detailed tutorial](https://youtu.be/nepWmWsq84g?t=505) : « Stretch machine » (8:25) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=4950) : « Track machines » (1:22:30) · DT2, 2024
