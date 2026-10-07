---
tags: [digitakt, kb]
theme: Polymétrie pour le groove tribe
lot: 2
ordre: 29
manuel: "§10.7, §10.7.1, §10.3 (p44-46)"
os: "1.17"
statut: draft
---

# Polymétrie pour le groove tribe

**En une phrase** : donner à certaines tracks une longueur différente de
16 pas (3, 5, 6, 7, 12…) pour que leurs motifs glissent contre le kick et
ne retombent ensemble qu'au bout de plusieurs mesures : du mouvement sans
toucher au pattern.

## Gestes rapides

| Action | Touches |
|---|---|
| PAGE SETUP | `[FUNC] + [PAGE]` |
| Passer en PER TRACK | `[FUNC] + [YES]` dans le menu (cf. [[page-setup]]) |
| Longueur de la track active | `[TRIG]` du dernier pas voulu |
| Point de remise à zéro commun | `RESET` (longueur maître du pattern) |

## Recettes

Le motif d'une track de N pas revient en phase avec le kick (16 pas) au bout
de ppcm(N, 16) pas :

| Track | Longueur | Retour en phase | Effet |
|---|---|---|---|
| Hat fermé (4) | 12 | ppcm(12, 16) = 48 pas = 3 mesures | balancement ternaire sur un kick droit |
| Perc A (7) | 6 | ppcm(6, 16) = 48 pas = 3 mesures | tresillo qui tourne |
| Perc B (8) | 7 | ppcm(7, 16) = 112 pas = 7 mesures | motif qui ne se répète presque jamais |
| Id1 (12) | 14 | ppcm(14, 16) = 112 pas = 7 mesures | mélodie qui se décale lentement (doctrine §12) |
| Trio 3-5-7 (7, 8, 12) | 3, 5, 7 | ppcm(3, 5, 7) = 105 pas | texture « vivante » à petite dose |

## Pas à pas : tribe 6 contre 16

1. Copie du pattern modèle, `[FUNC] + [PAGE]`, PER TRACK.
2. Kick (1), clap (3), basse (9) : 16 pas, ce sont les repères.
3. Track 7 : 6 pas, deux toms `x..x.x`. Track 4 : 12 pas, hats sur les
   pas 1, 4, 7, 10.
4. `RESET` du pattern à 64 pas (4 mesures) : tout repart ensemble au début
   de chaque phrase de 4 mesures, malgré les 48 pas de cycle.
5. Écouter 8 mesures, puis rendre une perc en euclidien sur 5 pas (cf.
   [[euclidien]]) pour comparer.

## En live techno

- **Repères droits, ornements impairs** : kick, clap, basse et rumble
  toujours sur 16 ; seules les percs, hats et Id deviennent polymétriques.
- Le `RESET` calé sur la phrase (64 ou 128 pas) garde les bascules de mutes
  sur le 1 (doctrine §6, principe 6).
- Démuter une perc en 7 pas au milieu d'un long plateau : le groove
  « change » sans aucun nouveau son.

## Pièges

- `A:B` des conditions compte les tours de la **track** : une track de 12
  pas en `1:4` ne joue pas toutes les 4 mesures (cf. [[fill-conditions]]).
- Copier un pattern copie les longueurs : le pattern modèle doit rester en
  16 partout.
- Trop de longueurs impaires à la fois = bouillie : une ou deux tracks
  polymétriques suffisent.

## À essayer (5 min)

Même boucle tribe, track 7 successivement en 6, 7 puis 12 pas, 8 mesures
chaque fois ; noter la longueur qui pousse le plus à danser.

Source : manuel DT2 OS 1.17, §10.7, §10.3.

## Vidéos

Ajoutées depuis [[../veille-live]] (2026-10-07), non visionnées.

- [3-5-7 polymeter — Digitakt](https://www.youtube.com/watch?v=qQF71MdaQ-Y) (vidéo entière) · DT1
- [Digitakt polyphonic and polymetric demo](https://www.youtube.com/watch?v=cBjD0ReQ72Q) (vidéo entière) · DT1
- [Get the max out of 1 pattern (Digitakt tutorial #8)](https://www.youtube.com/watch?v=bynEIvTpydA) (vidéo entière) · DT1
- [How to keep your boring loop endlessly spicy with polymeters](https://www.youtube.com/watch?v=0SPaGLLlBsM) (vidéo entière) · machine non précisée
