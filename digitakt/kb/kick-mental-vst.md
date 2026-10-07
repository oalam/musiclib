---
tags: [digitakt, kb]
theme: Kick mental / acidcore fabriqué en VST
lot: 3
ordre: 31
manuel: "§13.1.1, §13.6.7, A.2.1 (p68, 73, 93)"
os: "1.17"
statut: draft
---

# Kick mental / acidcore : fabriqué en VST, joué sur la DT2

**En une phrase** : le kickbass mental (long, accordé, très saturé) se
fabrique plus facilement au Mac avec un synthé et une chaîne de distorsion
VST ; on le fige en sample, nommé avec sa note, puis il devient le kick
invariant de la track 1 (doctrine §3, §11).

## Gestes rapides

| Étape | Où |
|---|---|
| Synthétiser le kick | synthé VST (sinus + enveloppe de pitch) ou synthé de kick dédié |
| Saturer | chaîne de distorsion / clipper VST, souvent en plusieurs étages |
| Mesurer la note | accordeur ou analyseur sur la **queue** (doctrine §11) |
| Exporter | WAV mono, `kick_mental_F#.wav` |
| Envoyer sur la DT2 | Elektron Transfer > EXPLORE > Samples, glisser-déposer (converti en 16 bits / 48 kHz) |
| Ou échantillonner directement | Overbridge, `[SAMPLING]` `SRC` = USB (cf. [[sampling-resampling]]) |
| Jouer | track 1, machine ONESHOT (cf. [[machines-src]]) |

## Pas à pas : du VST à la track 1

1. Dans le DAW, au tempo du set : un sinus avec une enveloppe de pitch
   rapide (le « click »), puis une queue longue qui tient la note.
2. Saturer en deux étages (distorsion douce puis clipper) ; refiltrer le
   haut si le kick devient trop criard.
3. Régler la durée sur le tempo : à 190 BPM, une noire dure
   60 / 190 = 0,316 s ; la queue doit retomber avant le kick suivant, ou
   être coupée par l'AMP de la DT2.
4. Mesurer la note sur la queue, l'écrire dans le nom du fichier.
5. Transfer vers le +Drive, charger dans le projet, assigner à la track 1,
   `TUNE` = 0.
6. Sauvegarder en preset (`kick_mental_F#`) puis dans le kit du pattern
   modèle (doctrine §8).

## En live techno

- Préparer **une famille de kicks** par tonalité visée (F#, G, A) plutôt
  que de tordre un seul kick au `TUNE` (doctrine §11).
- Le kickbass mental tient souvent le rôle de la basse : la track 9 peut
  rester vide (grille §1 : une track vide reste vide).
- Garder une version plus courte du même kick pour les passages tribe :
  même son, moins de queue, place pour la basse en contretemps.
- Le rumble se fabrique ensuite **à partir de ce kick** (cf.
  [[rumble-grave]]).

## Pièges

- Un kick déjà limité à 0 dBFS au Mac sature encore à l'overdrive de la
  DT2 : exporter avec un peu de marge.
- L'export en 44,1 kHz est converti en 48 kHz par Transfer : sans
  conséquence audible, mais garder la source dans le vault (`library/`).
- Échantillonner via `SRC` = USB demande le mode `OVERBRIDGE` ou
  `USB AUDIO/MIDI` (cf. [[overbridge-live-vst]]) ; *à vérifier* : niveau
  d'entrée côté DAW avant la prise (normalisée ensuite).
- Les tutos utilisent des plugins payants (Serum 2, Kick 2) : la même
  chaîne se fait avec un synthé et une distorsion gratuits, à choisir.

## À essayer (5 min)

Un même kick en trois longueurs de queue (0,15 s, 0,25 s, 0,3 s), chargés
sur la track 1 avec la même basse en contretemps sur la 9 ; garder celui qui
laisse la basse respirer à 190 BPM.

Source : manuel DT2 OS 1.17, §13.1.1, §13.6.7, A.2.1 ; doctrine §3, §11.

## Vidéos

Ajoutées depuis [[../veille-live]] (2026-10-07), non visionnées ; tutos
DAW, la DT2 n'y apparaît pas.

- [#35 Tekno tutorial : make a mentalcore kick like Teksa](https://www.youtube.com/watch?v=8QSzn8qP-to) (vidéo entière) · DAW
- [#36 Tekno tutorial : ultimate acidcore & gabber kick in Serum 2](https://www.youtube.com/watch?v=C79Vux5iSIQ) (vidéo entière) · Serum 2
- [How to make acidcore / mentalcore kick bass in 7 min (Ableton, FR)](https://www.youtube.com/watch?v=H5GSTi9U8ck) (vidéo entière) · Ableton
- [Hardcore techno kicks (no bullshit tutorial)](https://www.youtube.com/watch?v=12SVqssNbrI) (vidéo entière) · outil non précisé
