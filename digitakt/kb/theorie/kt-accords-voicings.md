---
tags: [digitakt, kb, theorie, kt]
theme: Accords, voicings, rythme harmonique
lot: 2
ordre: 8
styles: [dub techno, detroit, trance, tribe]
statut: draft
updated: 2026-10-15
---

# KT8 — Accords, voicings, rythme harmonique

**En une phrase** : en techno un accord est une couleur posée sur la
tonique du grave, rarement une progression ; ce qui compte est la
qualité (min7, min9, sus, quinte nue), l'étagement des notes (voicing
ouvert, pas de doublure grave) et la lenteur du changement (toutes les 4
à 16 mesures), et la DT2, monophonique par track, impose ses propres
façons de le faire.

## Signature

| Élément | Théorique | Mesuré | Lecture |
|---|---|---|---|
| Tribe, acid, tekno | quinte nue sur la tonique, pas de tierce | accords `5` et `sus2` dans 27 morceaux sur 32 ; kodaman D5 seul, luche G#5 / G#sus2 | la tierce est absente : ni majeur ni mineur, une tonique et sa quinte |
| Mouvement de basse | i → iv → v en quintes nues | berio `C#5 F#sus2 G#5`, neurotribe `Esus2 F5`, dizrupt `F#5 C#sus2` | les « progressions » détectées sont des mouvements de fondamentale, pas des accords |
| Dub, techno lente | min7 / min9, voicing ouvert, un accord sur 16-64 mesures | polar inertia `D#sus2 Em`, kangding ray `D#5 E5` | deux accords à un demi-ton, lents ; le seul vrai rythme harmonique de la passe |
| DnB | 1-2 accords mineurs | document one `D#5 D#m` en alternance, noisia `E Em Esus2` | tierce qui apparaît et disparaît sur la même fondamentale |

Passe harmonique : `scripts/kt_signatures.py --harmony`, table dans
[[_index]]. Lecture : la techno du terrain ne joue presque pas
d'accords ; quand elle en joue, ils bougent par la **fondamentale**
(tonique, quarte, quinte, b2) et gardent la même qualité.

## Vocabulaire

- **Accord** : trois notes ou plus entendues ensemble ; **triade** =
  fondamentale, tierce, quinte.
- **Qualité** : majeur (tierce majeure), mineur (tierce mineure), sus2 /
  sus4 (la tierce remplacée par la seconde ou la quarte), dim (quinte
  diminuée), quinte nue ou power chord (pas de tierce).
- **Extension** : note ajoutée au-dessus de la triade ; 7 (min7 : A C E
  G), 9 (min9 : + B), 11 (min11 : + D).
- **Voicing** : répartition des notes de l'accord dans les octaves ;
  **fermé** (toutes dans une octave), **ouvert** (étalées sur deux ou
  trois), **sans doublure grave** (la fondamentale n'est pas rejouée sous
  200 Hz, le kick la tient).
- **Renversement** : la note la plus basse du voicing n'est pas la
  fondamentale (A C E → C E A).
- **Rythme harmonique** : fréquence des changements d'accord ; une
  mesure en pop, 4 à 64 mesures en techno.
- **Pédale** : note tenue (la tonique au grave) pendant que les accords
  changent au-dessus.
- **Stab** : accord joué court, souvent échantillonné d'un seul coup
  (dub techno, Detroit).
- **Camelot** : roue des tonalités (1A à 12B) de `setbuilder.py` ; voisins
  = même numéro, ±1, ou même numéro en changeant la lettre.

## Pourquoi ça marche

**Concret d'abord : le même accord, quatre voicings.** Tonalité A, accord
Am7 (A C E G).

| Voicing | Notes de bas en haut | Effet |
|---|---|---|
| Fermé | A2 C3 E3 G3 | compact, « clavier » ; brouille sous 200 Hz |
| Ouvert | A2 E3 C4 G4 | aéré, chaque note lisible |
| Sans doublure grave | E3 G3 C4 (le A est au kick) | le stab dub techno : le kick fait la fondamentale |
| Renversé, ouvert | C3 G3 E4 (A au kick) | la tierce en bas colore sans alourdir |

La règle du grave (KT5) s'applique aux accords : **aucune note d'accord
sous 200 Hz**, la fondamentale est déjà là, tenue par le kick et la
basse. Les voicings sans doublure grave sont ceux de Basic Channel.

**Les qualités utiles et leur couleur.**

| Qualité | Sur A | Couleur | Styles |
|---|---|---|---|
| Quinte nue (A5) | A E | ni majeur ni mineur, dur | tribe, hard techno, hardcore |
| sus2 (Asus2) | A B E | ouvert, flottant | tekno, techno lente |
| sus4 (Asus4) | A D E | suspendu, veut résoudre | passages, risers |
| min (Am) | A C E | sombre, posé | DnB, techno |
| min7 (Am7) | A C E G | doux, « dub » | dub techno, Detroit |
| min9 (Am9) | A C E G B | lumineux dans le sombre | dub techno, deep |
| min11 (Am11) | A C E G B D | nappe entière | ambient, breaks |
| dim (Adim) | A C Eb | triton inclus, instable | industrial, transitions |

La passe harmonique confirme ce que le terrain fait : **quinte nue et
sus2** presque partout (27 morceaux sur 32), la tierce réservée aux
styles lents. Pour le live : un sus2 sur la track 13 colore un plateau
tribe sans dire mineur ; un min9 est une bascule vers le dub.

**Progressions : lentes, par la fondamentale, sur pédale.** La doctrine
§11 donne trois progressions types ; en degrés sur A :

| Progression | Accords sur A | Couleur | Rythme harmonique |
|---|---|---|---|
| Pédale i | Am7 seul | transe | jamais, ou une note qui bouge (KT7) |
| Dorien i7 → IV7 | Am7 → D7 | dub, Detroit | 4 à 8 mesures |
| Mineur i → bVI → bVII | Am → F → G | « trance », épique | 4 mesures |
| Phrygien i → bII | Am → Bb | tension mentale | 8 à 16 mesures |
| Quintes nues i → iv → v | A5 → D5 → E5 | tekno, hardcore (Berio) | 2 à 4 mesures |

Le générateur acid 9.A connaît les mêmes progressions en degrés
(`PROGRESSIONS` : I-VI-VII-I, I-IV-V-I, I-VII-VI-VII, I-V, I-IV, pédale).
À 190 BPM, 1 mesure = 4 × 60 / 190 = 1,263 s : un changement toutes les
8 mesures = toutes les 10,1 s, toutes les 16 = 20,2 s. Plus vite, la salle
entend une chanson ; plus lentement, elle entend une texture (exercice 3
de la veille, §A2).

**Accords sur une machine monophonique.** Une track audio de la DT2 joue
une note à la fois. Trois voies (doctrine §11) :

1. **sample d'accord transposé** : un stab Am7 échantillonné, joué par
   `NOTE` ou `TUNE` ; la qualité ne change pas, la fondamentale si. C'est
   la méthode dub techno, et sa limite : transposer de plus de 5 demi-tons
   change le timbre ;
2. **une voix par track** : 10, 11, 13 jouent chacune une note de
   l'accord ; trois tracks pour une triade, le voicing est libre, et les
   mutes permettent de retirer la tierce en live ;
3. **track MIDI** (16) : jusqu'à 4 notes par pas vers un synthé externe
   (fiche [[../tracks-midi]]).

**Camelot entre les parties.** Dans un morceau, pas de changement de
tonalité (KT6). Entre deux banks du set, `setbuilder.py` note la
compatibilité : même case 1,0, relatif (même numéro, lettre changée)
0,9, voisin ±1 (quinte ou quarte) 0,85, ±2 encore mixable 0,55. En live,
le passage A mineur (8A) → E mineur (9A) ou D mineur (7A) se prépare avec
une **note pivot** (E est dans les deux) tenue par le drone pendant le
pattern pont (doctrine §11, §13).

## Sur la DT2

Grille de la [[../../doctrine]] §1 : lead 10, drone 11, Id1 13, Id2 14,
MIDI 16. Gestes : [[../keyboard-gammes]], [[../parameter-preset-locks]],
[[../sampling-resampling]] (figer un stab), [[../send-fx-compresseur]]
(delay du stab).

1. **Une voix par track (10 min).** Tonique A au kick. Track 11 : E tenu ;
   track 13 : C ; track 10 : G, les trois sur le pas 1 en notes longues.
   Am7 sans doublure grave. Muter la 13 : A5 avec septième ; remuter,
   passer la 13 sur B par p-lock : Am9 ouvert. Un accord qui change par
   les mutes, sans nouveau pattern.
2. **Stab transposé (10 min).** Resampler l'accord de l'exercice 1 en un
   sample (fiche [[../sampling-resampling]]), le charger sur la 13 en
   stab court avec delay 3/16 (KT14). P-lock `NOTE` : 0 pendant 8 mesures,
   puis +5 (quarte) 8 mesures, puis 0. Le rythme harmonique le plus lent
   qui sonne encore « progression ».
3. **Rythme harmonique (5 min).** Même stab, changement toutes les 2
   mesures, puis 8, puis 16 (conditions `A:B` sur deux trigs, fiche
   [[../fill-conditions]]). Noter le seuil où ça passe de « chanson » à
   « texture ».

## Pièges

- Un accord fermé joué en entier sur une track grave fait de la bouillie
  sous 200 Hz : voicing ouvert, fondamentale au kick (KT5).
- Transposer un sample d'accord de plus de 5 demi-tons change son timbre
  et sa durée (Repitch) : une famille de stabs par tonalité, comme les
  kicks.
- Trois tracks pour un accord, c'est trois tracks de moins pour le reste :
  réserver aux parties dub, ou passer par la track MIDI.
- Un changement d'accord hors du 1 d'une phrase de 4 ou 8 mesures sonne
  comme une erreur (KT9, doctrine §6).
- Camelot ne sait rien des modes : A phrygien et A éolien sont la même
  case 8A ; la bascule de mode se gère à l'oreille.

## Ressources

- Ableton, *Learning Music* (accords, voicings, inversions, septièmes) :
  <https://learningmusic.ableton.com/> `[V]`
- Attack Magazine, Synth Secrets *Dub techno synth chords* :
  <https://www.attackmagazine.com/technique/synth-secrets/dub-techno-synth-chords/> `[V]`
- Attack Magazine, Beat Dissected *Basic Channel-style dub techno* :
  <https://www.attackmagazine.com/technique/beat-dissected/basic-channel-style-dub-techno/> `[V]`
  (accord D#m échantillonné, delays pointés).
- Attack Magazine, Passing Notes *Further Chords* (index) :
  <https://www.attackmagazine.com/technique/passing-notes/> `[V]`
- Hooktheory Trends (probabilités d'enchaînements, culture pop) :
  <https://www.hooktheory.com/trends> `[V]`
- Mixed In Key, *Camelot Wheel* :
  <https://mixedinkey.com/workflows/how-to-use-the-camelot-wheel/> `[R]`
- Code : `scripts/analyzer/keys.py` (`key_compatibility`),
  `scripts/analyzer/acid.py` (`PROGRESSIONS`).

## Liens

[[_index]] · [[../keyboard-gammes]] · [[../parameter-preset-locks]] ·
[[../sampling-resampling]] · [[../send-fx-compresseur]] ·
[[../tracks-midi]] · [[../fill-conditions]] · [[../../doctrine]] §11,
§13 · [[../../../SPEC]] Phase 4 (Camelot) · KT5
[[kt-tonalite-du-grave]] · KT6 [[kt-modes-techno]] · KT9
[[kt-phrasage-tension]] · KT14 (dub techno), à rédiger
