---
tags: [digitakt, kb]
theme: Grid, live et step recording, quantize
lot: 2
ordre: 6
manuel: "§10.2, §10.6, §17 (p41-44, 45, 89)"
os: "1.17"
statut: draft
---

# Grid, live et step recording, quantize

**En une phrase** : trois façons de remplir un pattern : poser les trigs sur
la grille (GRID), jouer en temps réel (LIVE), ou avancer pas à pas (STEP) ;
la quantize recale ce qui a été joué hors grille.

## Gestes rapides

| Action | Touches |
|---|---|
| GRID RECORDING on / off | `[RECORD]` (rouge fixe) |
| Note trig / lock trig (GRID) | `[TRIG]` / `[FUNC] + [TRIG]` |
| LIVE RECORDING | `[RECORD] + [PLAY]` (rouge clignotant) |
| Quantize auto en live on / off | `[RECORD]` + double `[PLAY]` |
| STEP RECORDING | `[RECORD] + [STOP]` (double clignotement) |
| STEP : STANDARD ↔ JUMP | `[RECORD]` + double `[STOP]` |
| STEP : choisir le pas actif | `[TRIG n]`, ou `[LEFT]/[RIGHT]` |
| STEP : poser un trig sur la track n au pas actif | `[FUNC] + [TRIG n]` |
| STEP : poser une note sur la track active | `[KEYBOARD]` (on), puis `[KEYBOARD]` maintenu + `[TRIG]` |
| STEP : silence ou effacer, puis avancer | `[NO]` |
| Décaler tous les trigs de la track d'un pas | `[FUNC] + [LEFT]/[RIGHT]` (GRID) |
| Boucler certaines pages seulement | `[PAGE]` + `[TRIG 9-16]` (GRID), `[PAGE] + [NO]` pour revenir |
| Effacer en live ce qui passe | `[NO]` + `[TRIG]` de la track, maintenus |
| Menu QUANTIZE | `[FUNC] + [TRIG PARAMETERS]` |

## GRID ou STEP ?

**GRID pour le rythme, STEP pour les notes.** En GRID, une note demande
plusieurs gestes : poser le trig, le maintenir, tourner `NOTE` (un
p-lock), et on n'entend la ligne qu'en relançant la lecture. En STEP, une
note = une touche : en mode KEYBOARD, les touches forment un clavier, la
note est posée au pas actif et le curseur avance seul. On écrit à son
rythme, séquenceur arrêté, sans être calé en temps réel comme en LIVE.

| | GRID | STEP |
|---|---|---|
| Pour | kick, hats, percs (socle) | basse, lead, motifs Id |
| Lecture | tout le pattern d'un coup sur les 16 touches | une note après l'autre, curseur qui avance |
| Hauteur | p-lock `NOTE` trig par trig | une touche du clavier |
| Gamme | à surveiller | seules les touches allumées jouent : avec `KB SCALE` fixé (dorien, phrygien…, cf. [[keyboard-gammes]]), pas de fausse note |
| Silences, corrections | toucher le pas | `[NO]` (silence) ou `[LEFT]/[RIGHT]` pour sauter / revenir |
| Édition fine | conditions, probabilités, micro-timing, p-locks sur trigs existants, lock trigs, plusieurs pages | non |

**Accords** (tracks MIDI uniquement) : jusqu'à 4 notes par trig, via les
paramètres `NOT2`-`NOT4` de la page TRIG ou un clavier MIDI externe (manuel
§10.2.2, §10.2.3). Un clavier externe sur l'AUTO CHANNEL saisit aussi pas
à pas en STEP (§10.2.4).

**En pratique** : GRID pour le socle (tuto 1), STEP pour les notes de la
basse, du lead et des Id (tuto 2), puis retour en GRID pour affiner
(conditions, probabilités, p-locks de son).

## Tuto 1 : recopier une grille de bank en GRID

1. Ouvrir la note de la bank (`library/digitakt/<slug>.md`) ou la vue bank
   du front, pattern voulu.
2. Sur la DT2 : `[RECORD]`, `[TRK] + [TRIG 1]` (kick).
3. Poser les `x` de la page 1 avec les `[TRIG]`. Page suivante : `[PAGE]`.
4. Track suivante (`[TRK] + [TRIG n]`), recommencer. Écouter avec `[PLAY]`.
5. `[RECORD]` pour sortir, `[FUNC] + [SETTINGS]` pour sauver.

## Tuto 2 : la basse en contretemps en STEP RECORDING

But : une ligne de basse sur la track 9, une note sur chaque contretemps
(doctrine §9). Sur 16 pas, les temps tombent sur 1, 5, 9, 13 ; le
contretemps est deux pas après : 1 + 2 = 3, 5 + 2 = 7, 9 + 2 = 11,
13 + 2 = 15.

```
pas     1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
kick    X  .  .  .  X  .  .  .  X  .  .  .  X  .  .  .
basse   .  .  o  .  .  .  o  .  .  .  o  .  .  .  o  .
touche  NO NO K  NO NO NO K  NO NO NO K  NO NO NO K  NO
```

(K = `[KEYBOARD]` maintenu + touche de la note.)

**A. Mode STANDARD (un appui = un pas)**

1. `[TRK] + [TRIG 9]` : la basse devient la track active (touche rouge).
2. `[RECORD] + [STOP]` : STEP RECORDING, `[RECORD]` clignote deux fois.
   Si le mode JUMP est resté actif, `[RECORD]` + double `[STOP]` repasse
   en STANDARD.
3. `[TRIG 1]` : le pas 1 devient le pas actif (vert, double clignotement).
4. `[KEYBOARD]` : clavier chromatique allumé (gamme et racine : cf.
   [[keyboard-gammes]]).
5. Suivre la ligne « touche » du tableau : `[NO]` laisse un silence et
   avance ; `[KEYBOARD]` maintenu + une touche allumée pose la note et
   avance. Seize appuis = une mesure.
6. `[PLAY]` pour écouter pendant qu'on écrit, `[STOP]` arrête la lecture
   sans quitter le STEP.
7. **Corriger une note** : `[TRIG 7]` (pas actif), `[KEYBOARD]` + nouvelle
   note. Les locks déjà posés sur ce trig restent.
8. **Accent** : page TRIG (`[TRIG PARAMETERS]`), maintenir `[TRIG 15]`,
   tourner `VEL` ; le trig clignote rouge, il est locké.
9. `[RECORD]` pour sortir, `[FUNC] + [SETTINGS]` pour sauver (le temp save
   `[FUNC] + [YES]` ne marche pas en STEP).

**B. Mode JUMP (la durée fait avancer)**

`[RECORD]` + double `[STOP]` : JUMP. Le `LEN` de la page TRIG fixe la durée
de la note posée **et** le saut : 1/16 = 1 pas, 1/8 = 2, 1/4 = 4. Chaque
trig reçoit un lock de `LEN`.

- Variante dub, une note tenue par temps : `LEN` = 1/4, quatre notes
  posent la mesure (4 × 4 = 16 pas).
- Ligne qui rebondit : changer `LEN` entre deux notes, par exemple 1/8 +
  1/16 + 1/16 = 2 + 1 + 1 = 4 pas par temps, sans compter les silences.

**C. Percs une par une avec `[FUNC] + [TRIG n]`**

En STANDARD, `[FUNC] + [TRIG n]` pose un trig sur la track n au pas actif,
puis avance : un appel / réponse tribe entre perc A et perc B s'écrit d'une
traite. Au pas 1 : `[FUNC] + [TRIG 7]`, `[NO]`, `[FUNC] + [TRIG 8]`,
`[NO]`… (tracks 7 et 8, doctrine §1).

**Astuce** : `[YES]` maintenu pendant qu'on pose un trig verrouille sa
durée sur le temps d'appui.

**À vérifier sur la machine** : en JUMP, de combien `[NO]` fait avancer
(un pas ou `LEN`) ; si `[FUNC] + [TRIG n]` change la track active ; si
la note sonne au moment où on la pose (pattern arrêté).

## Tuto 3 : jouer une perc en LIVE puis la caler

But : un rim tribe sur la track 7 qui garde un peu de groove.

1. `[TRK] + [TRIG 7]`, puis `[RECORD] + [PLAY]` : LIVE, le séquenceur
   tourne. Si l'écran affiche la quantize auto active, `[RECORD]` + double
   `[PLAY]` pour la couper.
2. Jouer `[TRIG 7]` sur deux ou trois tours de boucle.
3. Raté : maintenir `[NO]` + `[TRIG 7]` pendant le passage à effacer.
4. `[PLAY]` : sortie du LIVE, la lecture continue.
5. `[FUNC] + [TRIG PARAMETERS]` (QUANTIZE), `[TRIG 7]` pour choisir la
   track, monter `TRACK` (knob E ou H, l'écran le montre) jusqu'à entendre
   le calage. 0 = brut,
   valeur haute = sur la grille. `PATTERN` agit sur toutes les tracks.
6. `[NO]` pour sortir, `[FUNC] + [SETTINGS]` pour sauver.

## En live techno

- **GRID** pour les drums des banks générées : rapide, exact, la grille
  `x...` du draft se lit comme les `[TRIG]`.
- **LIVE** pour ce qui doit groover (percs tribe, lead) : jouer sur la
  boucle, quantize auto coupée, puis doser la quantize après coup (TRACK ou
  PATTERN, 0 = brut, valeur haute = calé).
- **STEP** pour la basse et les lignes à notes (tuto 2) : on écrit
  pattern arrêté ou en lecture, sans contrainte de jeu ; JUMP quand les
  durées comptent.
- Si une boucle importée tombe un pas trop tôt ou trop tard (premier temps
  mal détecté), `[FUNC] + [LEFT]/[RIGHT]` décale toute la track.

## Pièges

- Appui court sur un trig existant = le supprime ; appui long = l'édite.
- Le préroll du métronome ne joue qu'en LIVE (cf. [[tempo-metronome]]).
- En STEP, `[FUNC] + [YES]` / `[NO]` n'ont pas leur effet habituel
  (sauvegarde / rechargement temporaires désactivés).
- Copier une track et copier un pattern utilisent la même combinaison :
  dépend de GRID on / off (cf. [[copier-coller]]).

## À essayer (5 min)

Recopier en GRID la page 1 du kick et des hats d'un pattern de bank, puis
passer en LIVE avec quantize auto coupée, jouer un rim sur la track 7, et
monter la quantize TRACK jusqu'à entendre le calage.

Source : manuel DT2 OS 1.17, §10.2, §10.6, §17.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [Synthackers — Mastering Recording Modes](https://youtu.be/VOXnpUoH_nQ) (vidéo entière) · DT2, 2024
- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=1749) : « LIVE recording » (29:09) · DT2, 2024
- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=2220) : « GRID recording » (37:00) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=1356) : « Quantising live recording » (22:36) · DT2, 2024
- [Braintree56 — Recording Modes, Note Locks, Trig Locks](https://youtu.be/3ClMEjaKO5A?t=700) : « Step Recording » (11:40) · DT1, principe identique, 2023
