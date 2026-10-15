---
tags: [digitakt, kb, theorie, kt]
theme: Modes de la techno
lot: 2
ordre: 6
styles: [tribe, acidcore, dub techno, trance, psy]
statut: draft
updated: 2026-10-15
---

# KT6 — Modes de la techno

**En une phrase** : la techno ne module pas, elle change de couleur ;
cinq modes sur une même tonique (éolien, phrygien, dorien, phrygien
dominant, mineur harmonique) couvrent tout le terrain, et comme le grave
ne bouge pas (KT5), passer de l'un à l'autre ne coûte qu'un réglage de
gamme sur les tracks mélodiques.

## Signature

| Élément | Théorique | Mesuré | Lecture |
|---|---|---|---|
| Tribe | pentatonique mineure ou éolien sur la tonique | kodaman D pentatonique mineure (0,81), apre F pentatonique mineure, floxytek F **phrygien** (0,61) | peu de notes, la pentatonique domine ; un phrygien net chez Floxytek |
| Acid core / mental | phrygien, b2 en slide | neurotribe `Esus2 F5` (mouvement de demi-ton), luche G# mineur harmonique | le demi-ton tonique → b2 est bien là, en mouvement de basse |
| Tekno rapide | pentatonique mineure | 4 morceaux sur 6 en pentatonique mineure (G#, G#, F#) | le détecteur préfère la pentatonique quand la gamme n'est pas remplie |
| Techno lente, dub | dorien ou éolien, min7 / min9 | kangding ray E éolien (0,93), polar inertia E mineur harmonique | les seuls scores nets de la passe : plus de notes jouées, gamme identifiable |

Passe harmonique : `scripts/kt_signatures.py --harmony`, table dans
[[_index]]. Lecture globale : **pentatonique** (mineure, ou majeure relative, que
le détecteur ne distingue pas) **ou blues** dans 25 cas sur 32, « incertain »
dans 17 : les morceaux n'utilisent que 3 à 5
notes, et c'est le choix de la sixième ou de la deuxième qui fait le mode.

## Vocabulaire

- **Mode** : une gamme de sept notes définie par ses intervalles depuis la
  tonique ; même tonique, intervalles différents = couleur différente.
- **Degré** : rang d'une note dans le mode (1 tonique, 5 quinte) ; **b2**,
  **b3**, **b6**, **b7** = degrés abaissés d'un demi-ton par rapport au
  majeur.
- **Éolien** (mineur naturel) : 1 2 b3 4 5 b6 b7 ; la couleur par défaut.
- **Phrygien** : 1 b2 b3 4 5 b6 b7 ; la b2 à un demi-ton de la tonique,
  oppressante.
- **Dorien** : 1 2 b3 4 5 6 b7 ; la sixte majeure éclaire le mineur.
- **Phrygien dominant** : 1 b2 3 4 5 b6 b7 ; b2 et tierce majeure, la
  couleur orientale de la psy.
- **Mineur harmonique** : 1 2 b3 4 5 b6 7 ; la sensible (7 majeure) tire
  vers la tonique.
- **Pentatonique mineure** : 1 b3 4 5 b7 ; cinq notes sans demi-ton, sans
  risque, sans couleur modale.
- **Note caractéristique** : le degré qui distingue un mode de l'éolien
  (b2 pour le phrygien, 6 pour le dorien).
- **Tonique fixe** : changer de mode sans changer de tonique ; la doctrine
  §11 l'impose à l'intérieur d'un morceau.

## Pourquoi ça marche

**Concret d'abord : les cinq modes sur A.**

| Mode | Notes sur A | Formule | Note caractéristique | Couleur, styles |
|---|---|---|---|---|
| Éolien | A B C D E F G | 1 2 b3 4 5 b6 b7 | aucune (référence) | sombre neutre ; techno, tribe |
| Phrygien | A Bb C D E F G | 1 b2 b3 4 5 b6 b7 | Bb (b2) | oppressant ; acid core, hard techno, industrial |
| Dorien | A B C D E F# G | 1 2 b3 4 5 6 b7 | F# (6) | ouvert, « dub » ; dub techno, Detroit |
| Phrygien dominant | A Bb C# D E F G | 1 b2 3 4 5 b6 b7 | Bb et C# | oriental ; psy, trance dure |
| Mineur harmonique | A B C D E F G# | 1 2 b3 4 5 b6 7 | G# (7) | dramatique ; trance, cinématique |

Lecture : quatre modes sur cinq ne diffèrent de l'éolien que **par une
note**. Passer d'éolien à phrygien, c'est baisser le B en Bb ; d'éolien à
dorien, monter le F en F#. C'est pourquoi un même pattern de huit notes
change de visage quand on en déplace une seule (exercice 2).

**Pourquoi la tonique fixe.** Le grave tient une seule note (KT5). Changer
de tonalité (A vers C) oblige à réaccorder kick, rumble et basse, donc à
changer de presets ; la doctrine §11 réserve cela aux jonctions entre
parties. Changer de **mode** sur la même tonique ne touche que les tracks
10, 11, 13 et 14 : le kick ne bouge pas, la salle entend une couleur qui
tourne, pas un nouveau morceau. Sur la DT2, c'est `KB SCALE` dans
KEYBOARD SETUP, par track et sauvé dans le pattern (fiche
[[../keyboard-gammes]]) : deux patterns copiés l'un de l'autre, éolien
puis phrygien, font une bascule de mode en une pression.

**La b2 phrygienne.** À un demi-ton au-dessus de la tonique, la b2 est
l'intervalle le plus dissonant de la gamme (rapport 16:15). Jouée en
slide depuis la tonique sur une acid line (KT11), ou en mouvement de
basse `Esus2 → F5` comme chez Neurotribe, elle fait « mental » à elle
seule. Le phrygien dominant y ajoute la tierce majeure : l'intervalle
Bb-C# (une seconde augmentée, 3 demi-tons) est le son de la psy et des
gammes orientales.

**Le dorien et la sixte.** Monter la b6 en 6 majeure retire au mineur son
côté plaintif : l'accord i7 (A C E G) avec un IV7 (D F# A C) sonne jazz
ou dub. C'est la couleur de Basic Channel et de Detroit (KT14, KT16) ;
elle demande des accords, pas seulement une ligne.

**Ce que disent les morceaux.** La passe trouve surtout de la
pentatonique mineure (A C D E G sur A) : cinq notes sans demi-ton,
c'est-à-dire **aucune note caractéristique**. Ce n'est pas une erreur de
détection, c'est la pratique : une ligne tribe de trois notes (1, b3, 5
ou 1, 4, 5) n'affirme aucun mode. Le mode n'apparaît que lorsqu'on ajoute
la deuxième ou la sixième ; Floxytek *Micro Tribe* en F phrygien est le
cas où la b2 est jouée. Pour le musicien : partir de la pentatonique,
puis **choisir** la note qui colore.

## Sur la DT2

Grille de la [[../../doctrine]] §1 : basse 9, lead 10, drone 11, Id1 13.
Geste : fiche [[../keyboard-gammes]] (KEYBOARD SETUP, `KB SCALE`,
`ROOT NOTE`, `KB FOLD`, `NOTE PARAM` = SCALE).

1. **Les cinq couleurs (10 min).** Tonique du kick (par exemple F#, KT5).
   Track 10, `ROOT NOTE` F#, `KB FOLD` ON. Jouer la même phrase de huit
   notes en LIVE RECORDING avec `KB SCALE` = AEOLIAN, puis copier le
   pattern quatre fois et passer la gamme en PHRYGIAN, DORIAN, PHRYGIAN
   DOMINANT, HARMONIC MINOR (fiche [[../copier-coller]]). Chaîner les cinq
   patterns, 8 mesures chacun, en nommant la couleur à voix haute.
2. **Une note qui change tout (5 min).** Ligne de 8 pas sur 10 en
   pentatonique mineure (1, b3, 4, 5, b7). Remplacer une seule note par la
   b2 (phrygien), puis par la 6 (dorien), puis par la 7 (mineur
   harmonique), par p-lock de `NOTE`. Le reste ne bouge pas.
3. **Drone et mode (5 min).** Track 11 : tonique tenue (sample Stretch ou
   note longue). Track 10 en phrygien au-dessus pendant 16 mesures, puis
   dorien 16 mesures. Le drone ne change pas, la salle entend une
   modulation.

## Pièges

- `KB SCALE` contraint ce qu'on joue et le pas du bouton `NOTE`, pas les
  notes déjà enregistrées : changer de gamme ne transpose rien, il faut
  rejouer ou relocker (fiche [[../keyboard-gammes]]).
- Un LFO sur le pitch n'est pas quantifié sur la gamme : les notes
  aléatoires dans le mode passent par des locks de `NOTE` avec `PROB`
  (doctrine §11).
- Phrygien dominant et mineur harmonique ont deux demi-tons consécutifs
  autour de la tonique : à 190 BPM, une ligne qui les enchaîne vite
  devient criarde ; les garder pour les slides et les notes tenues.
- Le mode n'existe que si la note caractéristique est **jouée** : une
  ligne de trois notes en « phrygien » sans la b2 est une pentatonique.
- Le relatif majeur (C majeur pour A éolien) partage toutes ses notes :
  une ligne qui insiste sur C et G fait basculer la tonique perçue. Tenir
  la tonique au grave (KT5).

## Ressources

- Ableton, *Learning Music* (gammes, modes) :
  <https://learningmusic.ableton.com/> `[V]`
- Ableton, *Theory Hacks* leçon 2 (Scale device, phrygien dominant) :
  <https://www.ableton.com/de/classroom/support/theory-hacks/lesson-2/> `[V]`
- Tomas George, leçon *Phrygian* (CreativeLive) :
  <https://site.creativelive.com/class/music-theory-for-electronic-producers-tomas-george/lessons/phrygian> `[R]`
- musictheory.net, leçons sur les gammes et intervalles :
  <https://www.musictheory.net/lessons> `[V]`
- Manuel DT2 OS 1.17, §8.5.2 (KEYBOARD SETUP), annexe D (36 gammes).
- Module `scripts/analyzer/harmony.py` : `SCALES` (formules) et détection
  de gamme des sidecars.

## Liens

[[_index]] · [[../keyboard-gammes]] · [[../copier-coller]] ·
[[../../doctrine]] §11, §13 (tribe vers mental) · KT5
[[kt-tonalite-du-grave]] · KT7 [[kt-tensions-lignes]] · KT8
[[kt-accords-voicings]] · KT11 (acid core), KT19 (trance / psy), à
rédiger · générateur acid 9.A (`scripts/analyzer/acid.py`, `--scale`)
