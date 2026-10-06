---
tags: [digitakt, kb]
theme: Mode euclidien
lot: 2
ordre: 10
manuel: "§10.3, §10.7 (p44-46)"
os: "1.17"
statut: draft
---

# Mode euclidien

**En une phrase** : deux générateurs répartissent N coups aussi régulièrement
que possible sur la longueur de la track ; rotation et opérateur logique les
combinent : idéal pour des percs tribe qui tournent sans les poser à la main.

## Gestes rapides

| Action | Touches |
|---|---|
| Menu SEQUENCER | `[FUNC] + [AMP]` |
| Activer / couper | `EUC` on / off (`[REC]` passe au bleu) |
| Convertir en trigs normaux | maintenir `[FUNC]` en coupant `EUC` |

Paramètres : `PL1`, `PL2` (nombre de coups de chaque générateur), `LEN`
(longueur, en mode PER TRACK seulement), `RO1`, `RO2` (rotation de chaque
générateur), `TRO` (rotation des deux), `OP` : `OR` (tous les coups), `XOR`
(sauf coïncidences), `AND` (coïncidences seules), `SUB` (1 moins 2).

## Pas à pas : perc tribe 3 contre 8

1. Track 7 (perc A), `[FUNC] + [AMP]`, `EUC` on.
2. `PL1` = 3, `PL2` = 0, en PER TRACK `LEN` = 8 (cf. [[page-setup]]) : le
   tresillo `x..x..x.`.
3. `RO1` pour placer le premier coup hors du kick.
4. Track 8 : `PL1` = 5, `LEN` = 16, `TRO` à l'oreille : les deux percs se
   croisent.
5. Locker la vélocité ou le pitch sur les trigs générés si besoin.

## En live techno

- Recettes de départ : 3 sur 8 (tresillo), 5 sur 16, 7 sur 16, 5 sur 12
  contre un kick en 16 : la base tribe.
- Deux générateurs en `XOR` sur la même track : un motif plus dense mais
  sans doublons.
- Tourner `TRO` en jouant donne une variation sans changer de pattern.
- Une fois le motif trouvé, le **convertir** (`[FUNC]` + `EUC` off) pour
  pouvoir l'éditer à la main et le copier.

## Pièges

- En mode euclidien, impossible d'ajouter des note trigs à la main (les
  parameter locks restent possibles sur les trigs générés).
- Les trigs posés avant sont cachés, et réapparaissent à la sortie, sauf
  conversion avec `[FUNC]`, qui les **supprime**.
- `LEN` n'apparaît qu'en PER TRACK.

## À essayer (5 min)

Track 7 en 3/8, track 8 en 5/16, puis tourner `TRO` de la track 8 sur une
boucle de 4 mesures et noter les deux réglages qui sonnent le mieux.

Source : manuel DT2 OS 1.17, §10.3, §10.7.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=3710) : « Euclidean sequencer » (1:01:50) · DT2, 2024
- [Synthackers — Digitakt II Euclidean Mode](https://youtu.be/uUjW6s3nuug) (vidéo entière) · DT2, 2024
- [Optoproductions — Digitakt 2 Euclidean Sequencer Tutorial](https://youtu.be/j29cOWAzDyY) (vidéo entière) · DT2, 2024
- [loopop — DIGITAKT II vs OG Digitakt, detailed tutorial](https://youtu.be/nepWmWsq84g?t=750) : « Euclidean seq » (12:30) · DT2, 2024
