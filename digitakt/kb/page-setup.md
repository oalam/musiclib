---
tags: [digitakt, kb]
theme: Page setup (longueur, vitesse, changement)
lot: 1
manuel: "§10.7 (p45-47)"
os: "1.17"
statut: draft
---

# Page setup : longueur, vitesse, changement de pattern

**En une phrase** : fixe la longueur du pattern (jusqu'à 128 pas = 8 pages),
sa vitesse, et, en mode par track, quand le pattern suivant prend la main.

## Gestes rapides

| Action | Touches |
|---|---|
| Ouvrir PAGE SETUP | `[FUNC] + [PAGE]` |
| Basculer PER PATTERN / PER TRACK | `[FUNC] + [YES]` (dans le menu) |
| Longueur rapide | `[PAGE]` répété (pages), `[TRIG]` (pas) |
| Longueur musicale (2/16 à 128/128) | `[FUNC] + [UP]/[DOWN]` |
| Changer de page en édition | `[PAGE]` + `[LEFT]/[RIGHT]` ou `[TRIG]` allumé |

## Pas à pas

1. `[FUNC] + [PAGE]`. Par défaut : **PER PATTERN**, toutes les tracks ont la
   même longueur.
2. `LENGTH` : nombre de pas. Une bank générée en 8 mesures = 128 pas (8
   pages), en 4 mesures = 64.
3. `SPEED` : 1X par défaut. 2X = double-croches deviennent des triples
   (résolution 1/32), 3/4X = triolets.
4. Pour des longueurs différentes par track : `[FUNC] + [YES]` → **PER
   TRACK**. Colonne TRACK = longueur / vitesse de la track active ; colonne
   PATTERN = `CHANGE` et `RESET`.
5. `CHANGE` : au bout de combien de pas un pattern en file d'attente démarre.
   `RESET` : au bout de combien de pas toutes les tracks repartent du pas 1
   (`INF` = jamais).

## En live techno

- Allonger un pattern **recopie** les pages existantes : poser d'abord une
  mesure qui tourne, puis passer à 64 ou 128 pas, et ne varier que la
  dernière page (fill).
- Un pattern de 128 pas attend jusqu'à 8 mesures (environ 10 s à 190 BPM)
  avant de céder la place. En PER TRACK, `CHANGE` à 16 ou 32 permet de
  basculer toutes les 1 ou 2 mesures sans raccourcir le pattern.
- Tribe : hats ou percs sur 12 ou 6 pas en PER TRACK contre un kick sur 16 =
  polyrythmie qui tourne ; `RESET` à 64 la remet en phase toutes les 4
  mesures.

## Pièges

- Avec `RESET` sur `INF` et `CHANGE` sur `OFF`, le pattern suivant ne
  démarre **jamais**.
- `CHANGE` plus court que `RESET` l'emporte.
- `SPEED` 2X double aussi la vitesse de lecture des LFO calés sur le
  sequencer (à vérifier en lot 3).

## À essayer (5 min)

Passer en PER TRACK, mettre la track 4 (hats) sur 12 pas et le kick sur 16 :
écouter le décalage, puis `RESET` sur 48 et entendre la remise en phase.

Source : manuel DT2 OS 1.17, §10.7, §17.
