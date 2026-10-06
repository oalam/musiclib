---
tags: [digitakt, kb]
theme: LFO (dont le riser one-shot de la track 15)
lot: 3
ordre: 15
manuel: "§11.9-11.11, annexe C (p58-60, 114)"
os: "1.17"
statut: draft
---

# LFO, dont le riser one-shot de la track 15

**En une phrase** : trois LFO par track (deux sur MIDI) modulent les
paramètres SRC, FLTR, AMP et FX ; en mode `ONE`, un LFO devient une
enveloppe lente calée sur le tempo : c'est la base du riser.

## Gestes rapides

| Action | Touches |
|---|---|
| LFO 1 / 2 / 3 | `[MOD]` (puis `[MOD]` ou `[UP]/[DOWN]`) |
| Choisir la destination | knob `DEST`, préécoute en survolant, `[YES]` |
| Sauter par section de destinations | `[FUNC]` + tourner `DEST` |

Paramètres : `SPD` (bipolaire), `MULT` (× tempo ou × 120 BPM fixe), `FADE`
(négatif = fade-in, positif = fade-out), `DEST`, `WAVE` (TRI, SINE, SQR,
SAW, RND bipolaires ; EXPO, RAMP unipolaires), `SPH` (phase de départ),
`MODE` (FRE, TRG, HLD, ONE, HLF), `DEP` (profondeur, bipolaire).

Durée d'un cycle en pas (`MULT` calé sur le BPM) : `SPD` 8 × `MULT` 16 =
16 pas (1 mesure) ; `SPD` 4 × 16 = 32 pas ; `SPD` 2 × 16 = 64 pas (4 mesures).

## Pas à pas : riser de 4 mesures (track 15)

1. Track 15 : un bruit blanc ou une reverb resamplée, ONESHOT en boucle.
2. `[MOD]` LFO 1 : `DEST` = filtre `FREQ`, `WAVE` = RAMP (ou EXPO, montée
   plus tardive), `MODE` = ONE, `SPD` 2, `MULT` 16, `DEP` positif.
3. LFO 2 : `DEST` = AMP `VOL`, même vitesse, `MODE` ONE : le volume monte
   avec le filtre.
4. Un seul trig au premier pas des 4 dernières mesures avant le drop, avec
   `LEN` de trig long.
5. Impact sur le pas 1 du pattern suivant (doctrine §5).

## En live techno

- `MODE` TRG sur un LFO de filtre à `SPD` 32 : un « wah » rejoué à chaque
  note, calé au tempo.
- `WAVE` RND + `DEST` pan ou `FREQ` sur les hats : du mouvement sans
  programmer de locks.
- Un LFO peut moduler un autre LFO (LFO 2 / 3 → paramètres du LFO 1) :
  vitesse qui accélère sur un riser.
- `LFO.T` (page TRIG) et les locks de trig permettent de ne relancer le LFO
  que sur certains trigs.

## Pièges

- Pas de destination directe vers les effets d'envoi globaux (temps de delay,
  taille de reverb) : seulement les **niveaux d'envoi** par track.
- `MULT` réglé sur la valeur fixe (120 BPM) = LFO qui ne suit plus le tempo.
- `FADE` et `MODE` ONE se combinent mal : tester à l'oreille.

## À essayer (5 min)

Faire le riser ci-dessus sur 1 mesure (`SPD` 8) puis 4 mesures (`SPD` 2),
comparer RAMP et EXPO, garder la version préférée comme preset.

Source : manuel DT2 OS 1.17, §11.9-11.11, annexe C.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [Synthackers — Digitakt II LFO Deep Dive](https://youtu.be/8Dn7kXQtcKg) (vidéo entière) · DT2, 2024
- [Synthackers — Digitakt II LFO Deep Dive](https://youtu.be/8Dn7kXQtcKg?t=819) : « Trig Locking LFO Parameters » (13:39) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=1957) : « Modulating a hihat - predictably » (32:37) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=3353) : « Parameter locking a modulation » (55:53) · DT2, 2024
