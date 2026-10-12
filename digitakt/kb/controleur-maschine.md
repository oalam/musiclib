---
tags: [digitakt, kb]
theme: Contrôleur MIDI externe (Maschine MK2, tout USB via le Mac)
lot: 5
ordre: 35
manuel: "§10.2.3, §10.2.4, §14.4.2, §14.4.3, §14.8.1 (p42-44, 79, 83)"
os: "1.17"
statut: draft
---

# Contrôleur MIDI externe : Maschine MK2 via le Mac

**En une phrase** : la Maschine MK2 passe en mode MIDI (Controller Editor),
un petit routeur MIDI sur le Mac renvoie ses notes vers la DT2 en USB, sur
l'**AUTO CHANNEL** : les pads jouent et enregistrent la track active, une
track à la fois, sans DAW.

```
Maschine MK2 --USB--> Mac (Controller Editor + routeur MIDI) --USB--> DT2
                       notes sur l'AUTO CHANNEL                track active
```

## Gestes rapides

| Où | Réglage |
|---|---|
| Maschine | mode MIDI : `SHIFT + CONTROL`, ou automatique au lancement de Controller Editor |
| Controller Editor | template MIDI : pads en `Note`, canal = AUTO CHANNEL de la DT2 |
| Mac | routeur : entrée = **`Maschine MK2 Virtual Input`**, sortie = `Elektron Digitakt II` |
| DT2 | `[SETTINGS]` > SYSTEM > USB CONFIG = `USB MIDI` (ou `USB AUDIO/MIDI`) |
| DT2 | MIDI CONFIG > PORT CONFIG : `INPUT FROM` = USB, `RECEIVE NOTES` = on |
| DT2 | MIDI CONFIG > CHANNELS : noter l'`AUTO CHANNEL` |
| DT2 | changer la track jouée : `[TRK] + [TRIG n]` |

## Pas à pas 1 : brancher et faire sonner

1. **Mac** : fermer le logiciel Maschine (sinon pas de bascule en mode
   MIDI), fermer Elektron Transfer (il perturbe l'USB, cf.
   [[midi-config]]).
2. **Maschine** : USB au Mac, lancer Controller Editor : la Maschine passe
   en mode MIDI (sinon `SHIFT + CONTROL`).
3. **Controller Editor** : charger le template `DT2 Pads` (ci-dessous).
   À la main sinon : pads en `Note`, tous sur l'AUTO CHANNEL.
4. **DT2** : USB au Mac, USB CONFIG, PORT CONFIG et AUTO CHANNEL comme dans
   le tableau.
5. **Routeur MIDI** (Audio MIDI Setup ne route pas d'un port à l'autre) :
   une appli gratuite (MIDIrouter, Midiot) ou le Python du projet :

   ```
   cd scripts && python dt2_midi.py --list-ports
   python -c "import mido; i=mido.open_input('<port Maschine>'); o=mido.open_output('Elektron Digitakt II'); [o.send(m) for m in i]"
   ```

   (`<port Maschine>` = **`Maschine MK2 Virtual Input`**, vérifié le
   2026-10-12 ; l'entrée `Maschine Controller MK2` ne transporte pas les
   notes du template. `Ctrl+C` pour arrêter.)
6. **Test** : `[TRK] + [TRIG 7]` sur la DT2, taper un pad : la perc A joue.

## Le template `DT2 Pads`

Fichier : `digitakt/maschine/DT2 Pads.ncm2` (Maschine MK2, dérivé du
template d'usine Battery 4). Les 16 pads envoient sur le **canal 10**
(AUTO CHANNEL de la DT2), vélocité active ; boutons, potards et molette
sont désactivés, pour qu'aucun CC ne touche les sons de la DT2. Les
boutons GROUP A-H changent de disposition :

| Groupe | Disposition | Usage | Notes (pad 1 → 16) |
|---|---|---|---|
| A | Rythmique | tracks 1-8 sur une page, sans changer de track active | 0-7, puis 0-7 (pads 9-16 en doublon) |
| B | Chromatique | tout, sans filet | 60 → 75 |
| C | Éolien (mineur naturel) | techno mélodique, i → ♭VI → ♭VII | 60 62 63 65 67 68 70 72… |
| D | Phrygien | sombre, oppressant, vers le mental | 60 61 63 65 67 68 70 72… |
| E | Dorien | dub techno, mélodique lumineuse | 60 62 63 65 67 69 70 72… |
| F | Mineur harmonique | sensible (7e majeure), tension | 60 62 63 65 67 68 71 72… |
| G | Phrygien dominant | mental, hard, couleur orientale | 60 61 64 65 67 68 70 72… |
| H | Penta mineure | riffs de basse et d'acid, aucune note faible | 60 63 65 67 70 72 75… |

Une gamme de 7 notes sur 16 pads = deux octaves (14 pads) + 2 notes.

**Couleurs des pads** (vive à la frappe, atténuée au repos) :

- Groupe A : rangée du bas (tracks 1-4) **rouge**, rangée 2 (tracks 5-8)
  **bleu**.
- Groupes B-H : **tonique rouge**, **tierce jaune** (mineure ou majeure),
  **quinte verte** (la basse joue tonique ou quinte, doctrine §11), le
  reste à la couleur de la famille (ci-dessous).
- Bouton GROUP par famille : orange = rythmique, blanc = chromatique,
  bleu = modes mineurs (C, D, E, F, H), violet = mode à tierce majeure
  (G, phrygien dominant).
- Doublons du groupe A : rangée 3 gris très sombre, rangée du haut rouge
  comme celle du bas.
- Couleurs des boutons GROUP : choisies dans Controller Editor et reprises
  telles quelles (`color-index` du groupe : 1, 18, 8, 12).
- Pad frappé : couleur vive, sinon atténuée. Il faut **LED on = For MIDI
  Out** dans Controller Editor (dans le fichier : `onIfDown="on"` sur le
  pad, `controller` des LEDs = note du pad). Sans ça, la LED attend un
  retour MIDI que la DT2 n'envoie pas, et le pad ne s'allume pas.

**Groupe A, la page rythmique** : les notes 0 à 15 déclenchent les
tracks 1 à 16 quelle que soit la track active (manuel §8.4), sur l'AUTO
CHANNEL (vérifié le 2026-10-12). Pads 1-8 = kick, rumble, clap, hat
fermé, hat ouvert, ride, perc A, perc B (grille doctrine §1) ; pads 9-16
rejouent les mêmes tracks, pour les rolls à deux mains.

**Importer** : USB branché, Controller Editor, ouvrir le fichier `.ncm2`
(menu File), le sélectionner comme template actif ; `SHIFT + CONTROL`
si la Maschine n'est pas en mode MIDI.

**Changer le canal** : sélectionner les 16 pads dans Controller Editor
et changer `Channel`, dans les 8 groupes.

**Choisir la tonalité** : le template ne contient pas de tonique, il donne
des **degrés** à partir de 60. La note 60 joue le sample à sa hauteur
d'origine (C5 = do central, manuel §8.4 ; plage 16-84) : pad 1 = la note
du sample. On
fixe donc la tonalité **sur la DT2**, avec `TUNE` (page SRC) de la track
jouée, pour que pad 1 = tonique du morceau (le kick donne la tonalité,
doctrine §11).

- Calcul : `TUNE` = tonique − note du sample, en demi-tons, ramené entre
  −6 et +6. Exemple : kick en F#, basse samplée en A : F# − A = 6 − 9 =
  −3, donc `TUNE` = −3 et le pad 1 joue F#.
- Samples nommés avec leur note (`bass_A.wav`, doctrine §11) : le calcul
  se fait sans accordeur.
- Changer de mode sur la même tonique (dorien → phrygien, doctrine §11) =
  changer de groupe sur la Maschine, sans toucher à la DT2.
- `ROOT NOTE` et `KB SCALE` de la DT2 règlent ses propres touches, pas les
  notes reçues (à vérifier).

## Pas à pas 2 : enregistrer une perc en LIVE depuis les pads

1. Track 7 active, `[RECORD] + [PLAY]` (LIVE), quantize auto au choix
   (cf. [[enregistrement-quantize]], tuto 3).
2. Jouer sur les pads : la vélocité des pads est enregistrée, en lock de
   `VEL` sur chaque trig (manuel §10.2.4) ; c'est l'intérêt face aux
   touches de la DT2.
3. `[PLAY]` pour sortir, track suivante (`[TRK] + [TRIG 8]`), nouveau
   passage : une track par passage.
4. Doser la quantize, `[FUNC] + [SETTINGS]` pour sauver.

## Pas à pas 3 : écrire une basse en STEP depuis les pads

1. Track 9 active, `[RECORD] + [STOP]` (STEP), `[TRIG 1]` = pas de départ.
2. Chaque pad pose sa note au pas actif et avance (cf.
   [[enregistrement-quantize]], tuto 2) ; `[NO]` sur la DT2 pour un silence.
3. Vélocité fixe plutôt que celle du pad : maintenir `[FUNC]` sur la DT2
   pendant qu'on joue la note (valeur `VEL` de la track).
4. Durée de la note sur le temps d'appui : maintenir `[YES]`.

## En live techno

- Pads sensibles : hats et percs tribe (tracks 4, 7, 8) avec une dynamique
  que les touches de la DT2 ne donnent pas.
- Une track à la fois : c'est la voie documentée et vérifiée (AUTO
  CHANNEL, cf. [[midi-config]]), cohérente avec la grille §1.
- Overbridge n'est **pas** nécessaire : il sert à l'audio (cf.
  [[overbridge-live-vst]]).

## Pièges

- Un seul mode USB à la fois sur la DT2 : en `OVERBRIDGE`, le manuel ne dit
  pas si le MIDI passe ; `USB MIDI` est la voie sûre.
- `INPUT FROM` = MIDI seul : la DT2 n'écoute que la prise DIN, rien ne
  passe par l'USB.
- Pads sur un autre canal que l'AUTO CHANNEL : ils visent la track réglée
  sur ce canal (CHANNELS), pas la track active, et leur enregistrement
  n'est pas documenté (cf. [[midi-config]]).
- `KB SCALE` de la DT2 ne s'applique qu'à ses touches (à vérifier) : la
  gamme se règle dans le template Controller Editor.
- **À vérifier sur la machine** : que le pad 1 est en bas à gauche ; que
  les coups du groupe A **s'enregistrent** en LIVE REC sur les tracks 1-8
  (ils sonnent, vérifié) ; si le routeur doit filtrer l'horloge MIDI.
- **Vérifié le 2026-10-12** : port `Maschine MK2 Virtual Input`, canal 10
  (mido affiche `channel=9`, numérotation 0-15), notes 0-7 = tracks 1-8.
- Vélocités très faibles à la frappe légère (5 à 26 relevés) : courbe de
  vélocité à ajuster dans Controller Editor si les pads sonnent trop bas.

## À essayer (5 min)

Pads 1-4 en notes 60, 62, 63, 65 sur l'AUTO CHANNEL ; track 7 en LIVE,
deux tours de boucle en variant la force de frappe, puis regarder les locks
`VEL` en GRID.

Sources : manuel DT2 OS 1.17, §10.2.3, §10.2.4, §14.4, §14.8.1 ;
[Native Instruments, passer un contrôleur en mode MIDI](https://support.native-instruments.com/support/solutions/articles/69000880031-native-instruments-switching-your-controller-to-midi-mode).
