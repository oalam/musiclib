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

1. Charger un break d'une mesure **coupée exactement** (début sur le premier
   kick, fin juste avant le kick suivant), machine SLICE, CREATE SLICE GRID
   16 **sans détection de transitoires** (H) : grille égale, une tranche par
   double croche, donc tranche n = pas n.
2. Track 12 (Id1, doctrine §1), 16 trigs, CREATE LINEAR LOCKS : le break
   rejoue tel quel.
3. Locker `SLICE` sur quelques trigs (kick et snare échangés, ghost
   répété), `LEN` = 2 sur un trig pour un roulement.
4. Variante en LIVE REC, trig mode SLICES : jouer les tranches aux touches,
   quantize auto active (cf. [[enregistrement-quantize]]).
5. CREATE RANDOM LOCKS sur une copie du pattern : version « réservoir »
   (slots 13-15, doctrine §2). Détail ci-dessous.

### Focus étape 5 : trois réservoirs tirés au sort

**Pourquoi** : les slots 13-15 sont les patterns à sortir si l'énergie
retombe ou si la salle en redemande (doctrine §2). Le tirage aléatoire donne
un break haché sans le réécrire ; le socle (tracks 1-11, 14-16) reste
identique, donc mutes et fills restent valables.

Exemple de rangement : le break des étapes 1-3 vit en B04 (bank B = DnB,
doctrine §13), les réservoirs en B13, B14, B15.

1. **Dupliquer** : `[PTN]`, `[TRIG 4] + [RECORD]` (copie B04), puis
   `[TRIG 13] + [STOP]`, `[TRIG 14] + [STOP]`, `[TRIG 15] + [STOP]`
   (cf. [[copier-coller]]). `[FUNC] + [SETTINGS]` : projet sauvé, B04
   intact quoi qu'il arrive.
2. **Choisir les trigs avant le tirage** (en GRID, track 12) : le hasard ne
   touche que les trigs posés, c'est donc le placement qui fixe le phrasé.
   - B13 « dense » : les 16 trigs gardés.
   - B14 « aéré » : 8 trigs (pas 1, 3, 5… 15) ; `LEN` = 2 sur chacun pour
     combler les trous avec la tranche suivante.
   - B15 « ancré » : 16 trigs, tirage puis squelette rétabli (point 5).
3. **Tirer** (pattern en lecture, track 12 active) : `[SRC]`, `[YES]`
   (menu SLICE), `[DOWN]` jusqu'à CREATE RANDOM LOCKS, `[YES]`. **Chaque
   `[YES]` refait un tirage** (manuel §A.2.6) : écouter une mesure, relancer
   tant que ça ne groove pas. À 172 BPM, une mesure = 4 × 60 / 172 =
   1,395 s ; dix tirages écoutés ≈ 10 × 1,395 = 14 s.
4. **Figer un bon tirage** : `[NO]` pour sortir du menu, **puis**
   `[FUNC] + [YES]` (temp save, cf. [[perform-kit-temp-save]]). Si un
   tirage suivant est moins bon, `[FUNC] + [NO]` ramène le précédent : il
   n'y a pas d'« annuler » du tirage.
5. **Ancrer (B15)** : relocker `SLICE` à la main sur les quatre appuis de
   l'amen. En grille égale, chaque appui reprend sa propre tranche (pas n →
   `SLICE` n) : pas 1 → 1, pas 5 → 5, pas 11 → 11, pas 13 → 13. Les 12
   autres pas gardent leur tranche tirée au sort : on entend toujours
   « boum… tak… boum-boum tak », le hasard ne joue que sur les ghosts et
   les hats.

   Première mesure de l'amen en 16 pas (transcription courante, à confirmer
   à la préécoute) ; X = appui, x = coup secondaire, g = ghost :

   | Pas | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
   |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
   | Hat | x | | x | | x | | x | | x | | x | | x | | x | |
   | Kick | **X** | | x | | | | | | | | **X** | x | | | | |
   | Snare | | | | | **X** | | | g | | g | | | **X** | | | g |

   Appuis : kick 1 (la mesure démarre), snare 5 et 13 (temps 2 et 4, le
   backbeat), kick 11 suivi du 12 (le double kick syncopé, signature de
   l'amen).
6. `[FUNC] + [SETTINGS]` : le tirage n'est gardé qu'une fois le projet
   sauvé (le temp save ne survit pas au changement de projet).

**En jeu** : B04 → B13 quand la salle monte, B14 pour respirer sans
couper le break, B15 pour revenir vers B04 sans rupture (même kick, même
snare).

**À vérifier sur la machine** : que RANDOM LOCKS écrase bien les locks
`SLICE` posés à la main à l'étape 3 et conserve les locks `LEN` ; qu'une
tranche peut sortir plusieurs fois (tirage avec remise) ou non.

## En live techno

- Le break vit sur une **Id** (12 ou 13), jamais sur la 1 : le kick du set
  reste sur la 1, même en DnB (grille §1).
- **Demi-temps** : un break DnB à 172 se sent à 86 ; le jouer sous un kick
  tribe ralenti fait le pont (doctrine §13, transitions de tempo).
- `SLICE` en `NOTE` + mode keyboard : jouer le break comme un instrument.
- Conditions sur les trigs de tranches (`1:2`, `FILL`) : le break se
  désarticule seulement pendant le fill (cf. [[fill-conditions]]).

## Pièges

- Grille égale et sample mal coupé : si le break ne fait pas exactement une
  mesure, les tranches glissent par rapport aux pas et tranche n ≠ pas n.
  Ajuster début et fin du sample avant CREATE SLICE GRID.
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
