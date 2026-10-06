---
tags: [digitakt, kb]
theme: Grid, live et step recording, quantize
lot: 2
ordre: 6
manuel: "§10.2, §10.6, §17 (p41-44, 45, 89)"
os: "1.17"
statut: draft
---

# Grid, live et step recording, quantize

**En une phrase** : trois façons de remplir un pattern : poser les trigs sur
la grille (GRID), jouer en temps réel (LIVE), ou avancer pas à pas (STEP) ;
la quantize recale ce qui a été joué hors grille.

## Gestes rapides

| Action | Touches |
|---|---|
| GRID RECORDING on / off | `[RECORD]` (rouge fixe) |
| Note trig / lock trig | `[TRIG]` / `[FUNC] + [TRIG]` |
| LIVE RECORDING | `[RECORD] + [PLAY]` (rouge clignotant) |
| Quantize auto en live on / off | `[RECORD]` + double `[PLAY]` |
| STEP RECORDING | `[RECORD] + [STOP]` (double clignotement) |
| Décaler tous les trigs de la track d'un pas | `[FUNC] + [LEFT]/[RIGHT]` (GRID) |
| Boucler certaines pages seulement | `[PAGE]` + `[TRIG 9-16]` (GRID), `[PAGE] + [NO]` pour revenir |
| Effacer en live ce qui passe | `[NO]` + `[TRIG]` de la track, maintenus |
| Menu QUANTIZE | `[FUNC] + [TRIG PARAMETERS]` |

## Pas à pas : recopier une grille de bank en GRID

1. Ouvrir la note de la bank (`library/digitakt/<slug>.md`) ou la vue bank
   du front, pattern voulu.
2. Sur la DT2 : `[RECORD]`, `[TRK] + [TRIG 1]` (kick).
3. Poser les `x` de la page 1 avec les `[TRIG]`. Page suivante : `[PAGE]`.
4. Track suivante (`[TRK] + [TRIG n]`), recommencer. Écouter avec `[PLAY]`.
5. `[RECORD]` pour sortir, `[FUNC] + [SETTINGS]` pour sauver.

## En live techno

- **GRID** pour les drums des banks générées : rapide, exact, la grille
  `x...` du draft se lit comme les `[TRIG]`.
- **LIVE** pour ce qui doit groover (percs tribe, lead) : jouer sur la
  boucle, quantize auto coupée, puis doser la quantize après coup (TRACK ou
  PATTERN, 0 = brut, valeur haute = calé).
- **STEP** (mode JUMP : `[RECORD]` + double `[STOP]`) pour une ligne de
  basse : la longueur `LEN` fait avancer d'autant de pas.
- Si une boucle importée tombe un pas trop tôt ou trop tard (premier temps
  mal détecté), `[FUNC] + [LEFT]/[RIGHT]` décale toute la track.

## Pièges

- Appui court sur un trig existant = le supprime ; appui long = l'édite.
- Le préroll du métronome ne joue qu'en LIVE (cf. [[tempo-metronome]]).
- En STEP, `[FUNC] + [YES]` / `[NO]` n'ont pas leur effet habituel
  (sauvegarde / rechargement temporaires désactivés).
- Copier une track et copier un pattern utilisent la même combinaison :
  dépend de GRID on / off (cf. [[copier-coller]]).

## À essayer (5 min)

Recopier en GRID la page 1 du kick et des hats d'un pattern de bank, puis
passer en LIVE avec quantize auto coupée, jouer un rim sur la track 7, et
monter la quantize TRACK jusqu'à entendre le calage.

Source : manuel DT2 OS 1.17, §10.2, §10.6, §17.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [Synthackers — Mastering Recording Modes](https://youtu.be/VOXnpUoH_nQ) (vidéo entière) · DT2, 2024
- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=1749) : « LIVE recording » (29:09) · DT2, 2024
- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=2220) : « GRID recording » (37:00) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=1356) : « Quantising live recording » (22:36) · DT2, 2024
- [Braintree56 — Recording Modes, Note Locks, Trig Locks](https://youtu.be/3ClMEjaKO5A?t=700) : « Step Recording » (11:40) · DT1, principe identique, 2023
