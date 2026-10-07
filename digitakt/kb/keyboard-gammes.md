---
tags: [digitakt, kb]
theme: Mode keyboard, gammes et tonique
lot: 2
ordre: 26
manuel: "§8.5.1, §8.5.2, §11.2, §14.7.6, annexe D (p25-26, 53, 82, 115)"
os: "1.17"
statut: draft
---

# Mode keyboard, gammes et tonique

**En une phrase** : les touches de trig jouent le preset de la track active
en notes ; KEYBOARD SETUP fixe la gamme et la tonique, et le bouton `NOTE`
peut suivre cette gamme : c'est l'outil machine de la tonalité (doctrine
§11).

## Gestes rapides

| Action | Touches |
|---|---|
| Mode keyboard on / off | `[KEYBOARD]` |
| Track jouée | `[TRK] + [TRIG 1-16]` |
| Transposer d'une octave | `[KEYBOARD] + [UP]` / `[DOWN]` (ou `[UP]` / `[DOWN]` seuls si `U/D KEY MODE` = KB OCT) |
| Menu KEYBOARD SETUP | `[FUNC] + [KEYBOARD]` ; `[NO]` pour sortir |
| Note d'un trig hors gamme / dans la gamme | page TRIG, appuyer en tournant DATA ENTRY A |
| Comportement du bouton `NOTE` | SETTINGS > PERSONALIZE > `NOTE PARAM` : CHRO ou SCALE |

KEYBOARD SETUP : `KB SCALE` (gamme de la track), `ROOT NOTE` (tonique),
`KB FOLD` (toutes les touches jouent une note de la gamme : `[TRIG 9]` = la
plus grave, montée jusqu'à 16 puis 1-8 ; touches bleues = mêmes notes à
l'octave). Réglages **sauvés dans le pattern**.

Gammes utiles au terrain (annexe D, 36 au total) : DORIAN, PHRYGIAN,
AEOLIAN (MINOR), PENTATONIC MINOR, HARMONIC MINOR, PHRYGIAN DOMINANT,
DORIAN b2, HUNGARIAN MINOR, ULTRAPHRYGIAN.

## Pas à pas : caler un pattern sur la note du kick

1. Mesurer la note du kick (queue, pas attaque) : Overbridge + accordeur ou
   analyseur (cf. [[audio-routing-overbridge]]), par exemple F#.
2. Track 9 (basse), `[FUNC] + [KEYBOARD]` : `KB SCALE` = PHRYGIAN,
   `ROOT NOTE` = F#, `KB FOLD` = ON.
3. Refaire 2 sur les tracks 10, 12, 13 (lead, Id) : la gamme est par track.
4. `NOTE PARAM` = SCALE : tourner `NOTE` sur un trig ne sort plus de la
   gamme.
5. En GRID, poser des trigs sur la 10, locker `NOTE` (cf.
   [[parameter-preset-locks]]), ajouter du trig chance ou des conditions
   (cf. [[fill-conditions]]) : mélodie aléatoire mais dans le mode.

## En live techno

- `KB FOLD` = ON : impossible de jouer une fausse note en LIVE RECORDING,
  les 16 touches sont toutes dans la gamme.
- Changer de mode sur la même tonique (dorien → phrygien, doctrine §11) =
  changer `KB SCALE` dans le pattern suivant ; les notes déjà lockées ne
  bougent pas, seules les nouvelles suivent la gamme.
- Le keyboard pilote aussi une track MIDI : même gamme pour un synthé
  externe (cf. [[tracks-midi]]).

## Pièges

- `KB SCALE` contraint ce qu'on **joue** et le pas du bouton `NOTE`, pas les
  notes déjà enregistrées : changer de gamme ne transpose rien.
- La portion de clavier visible (l'octave) n'est **pas** sauvée dans le
  pattern, contrairement à la gamme et à la tonique.
- Un LFO sur le pitch n'est pas quantifié sur la gamme (doctrine §11) :
  passer par des locks de `NOTE`.
- `NOTE PARAM` est un réglage global (PERSONALIZE), pas par pattern.

## À essayer (5 min)

Track 10, PHRYGIAN sur la note du kick, `KB FOLD` ON, jouer 4 mesures en
LIVE RECORDING avec la quantize auto (cf. [[enregistrement-quantize]]),
puis passer `KB SCALE` en DORIAN sur une copie du pattern et comparer.

Source : manuel DT2 OS 1.17, §8.5.1, §8.5.2, §11.2, §14.7.6, annexe D.
