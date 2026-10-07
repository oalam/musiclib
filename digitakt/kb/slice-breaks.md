---
tags: [digitakt, kb]
theme: Slice et breaks (ouvertures DnB / jungle)
lot: 3
ordre: 30
manuel: "A.2.5, A.2.6, §8.5.4 (p27, 97-101)"
os: "1.17"
statut: draft
---

# Slice et breaks : ouvertures DnB / jungle

**En une phrase** : découper un break (amen…) en tranches avec la machine
SLICE ou GRID, puis re-séquencer les tranches trig par trig : la matière
des parties DnB du set (doctrine §13).

## Gestes rapides

| Action | Touches |
|---|---|
| Machine SLICE ou GRID | `[FUNC] + [SRC]` (cf. [[machines-src]]) |
| Menu SLICE | `[SRC]` puis `[YES]` |
| Grille de tranches | CREATE SLICE GRID : nombre (E, `[FUNC]` + E = 2 / 4 / 8 / 16 / 32 / 64), détection de transitoires (H) |
| Éditer une tranche | EDIT SLICE POINTS : début (E), fin (H), boucle (D), `[FUNC]` = passage par zéro |
| Préécouter la tranche | `[FUNC] + [YES]` |
| Jouer les tranches aux touches | trig mode SLICES : `[FUNC] + [UP]` / `[DOWN]`, `[TRIG 1]` = tranche 1 |
| Répartir les tranches sur les trigs posés | CREATE LINEAR LOCKS / CREATE RANDOM LOCKS |

Paramètres : `SLICE` (tranche jouée, lockable ; NOTE = choisie au clavier),
`LEN` (nombre de tranches jouées à la suite), `GRID` (GRID : nombre de
tranches égales).

## Pas à pas : amen re-séquencé à 172

1. Charger un break d'une mesure, machine SLICE, CREATE SLICE GRID 16 avec
   détection de transitoires : une tranche par coup.
2. Track 12 (Id1, doctrine §1), 16 trigs, CREATE LINEAR LOCKS : le break
   rejoue tel quel.
3. Locker `SLICE` sur quelques trigs (kick et snare échangés, ghost
   répété), `LEN` = 2 sur un trig pour un roulement.
4. Variante en LIVE REC, trig mode SLICES : jouer les tranches aux touches,
   quantize auto active (cf. [[enregistrement-quantize]]).
5. CREATE RANDOM LOCKS sur une copie du pattern : version « réservoir »
   (slots 13-15, doctrine §2).

## En live techno

- Le break vit sur une **Id** (12 ou 13), jamais sur la 1 : le kick du set
  reste sur la 1, même en DnB (grille §1).
- **Demi-temps** : un break DnB à 172 se sent à 86 ; le jouer sous un kick
  tribe ralenti fait le pont (doctrine §13, transitions de tempo).
- `SLICE` en `NOTE` + mode keyboard : jouer le break comme un instrument.
- Conditions sur les trigs de tranches (`1:2`, `FILL`) : le break se
  désarticule seulement pendant le fill (cf. [[fill-conditions]]).

## Pièges

- Les points de tranches sont sauvés **avec le preset** : sauvegarder le
  preset, sinon le découpage est perdu au rechargement du sample.
- CREATE LINEAR / RANDOM LOCKS ne s'applique qu'aux **trigs déjà posés**.
- Hors SLICE et GRID, le trig mode SLICES ne joue que le sample entier sur
  `[TRIG 1]`.
- Un break joué à un autre tempo que l'original : STRETCH ou `TUNE` pour le
  caler avant de trancher (cf. [[machines-src]]).

## À essayer (5 min)

Amen en 16 tranches, 4 trigs seulement (pas 1, 5, 9, 13) en LINEAR LOCKS,
puis `LEN` = 4 sur chacun : le break entier rejoue à partir de 4 trigs.
Ensuite décaler un `SLICE` d'une tranche.

Source : manuel DT2 OS 1.17, A.2.5, A.2.6, §8.5.4.

## Vidéos

Ajoutées depuis [[../veille-live]] (2026-10-07), non visionnées.

- [Live Dispatch : diving into Digitakt II's Slice machine (Elektron)](https://www.youtube.com/watch?v=LYqHfMtR28U) (vidéo entière) · DT2
- [Hardware only jungle track breakdown // chopping breakbeats on the Digitakt](https://www.youtube.com/watch?v=Ww-NpzbYFpY) (vidéo entière) · DT1
- [Digitakt tutorial #1 : breakbeat science](https://www.youtube.com/watch?v=99XWrvT7y9Y) (vidéo entière) · DT1
- [Amen-break junglism on Elektron Digitakt](https://www.youtube.com/watch?v=bb0oJ1H-W-c) (vidéo entière) · DT1
