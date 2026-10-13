---
tags: [digitakt, kb]
theme: One-shots mélodiques depuis un synthé (basses, leads, accords)
lot: 3
ordre: 36
manuel: "§8.4, §9.1, §13.1, A.2.1, A.2.3 (p25, 29, 68, 93-96)"
os: "1.17"
statut: draft
---

# One-shots mélodiques depuis un synthé

**En une phrase** : enregistrer un son **brut, juste, stable, sur une note
connue**, et laisser à la DT2 l'enveloppe, le filtre, les effets et la
transposition ; c'est ce qui permet de le jouer dans la gamme du morceau.

## Ce que la DT2 impose

| La DT2… | Donc le sample… |
|---|---|
| joue le sample à sa hauteur d'origine sur la note 60 (manuel §8.4) | est enregistré sur une **note connue**, écrite dans son nom : `bass_reese_C.wav` (doctrine §11) |
| transpose en ONESHOT en changeant la vitesse de lecture | reste vers ±5 demi-tons (±12 au plus) : vers l'aigu plus court et plus brillant, vers le grave plus long et plus terne |
| a des tracks audio **monophoniques** | est **sec** : la note suivante coupe la queue, une reverb enregistrée est tronquée ; un accord = un sample |
| règle AMP, FLTR et envois par pas (p-locks) | n'a ni enveloppe de filtre marquée ni effets enregistrés |
| lit du 48 kHz / 16 bits, 400 Mo par projet (manuel §9.1) | est en mono quand c'est possible (moitié moins de place) |

## Gestes rapides

| Action | Où |
|---|---|
| Tenir une note | page SRC, `PLAY` = FORWARD LOOP, `LOOP` dans la partie stable, `LEN` de trig long |
| Transposer | `TUNE` (SRC) : appuyer en tournant = demi-tons |
| Échantillonner un synthé du Mac | `[SAMPLING]`, `SRC` = USB, `CHAN` = MONO, `R.STRT` au seuil (cf. [[sampling-resampling]]) |
| Changer de sample par pas | sample lock (`SAMP`) ou preset lock (cf. [[preset-pool]]) |

## Pas à pas : une basse et un lead depuis un synthé

1. **Synthé** : accordé à 440 Hz ; sans vibrato ni LFO libre sur la
   hauteur (une modulation de hauteur à l'attaque est acceptable si la note
   se stabilise ensuite) ; **remise à zéro de la phase des oscillateurs** à
   chaque note (*key sync* / *osc reset*), sinon chaque prise a une attaque
   différente ; vélocité désactivée, prise au maximum.
2. **Son** : filtre assez ouvert, sans reverb ni delay, peu de chorus.
   Basse en **mono strict** (un unisson très large s'effondre en mono et le
   grave devient flou) ; un lead peut être en stéréo.
3. **Note de référence** : la tonique de l'acte si elle est connue (`TUNE`
   reste à 0, aucune déformation), sinon C. Avec C : `TUNE` = tonique − C,
   en demi-tons, ramené entre −6 et +6 (même calcul que
   [[controleur-maschine]]).
4. **Longueur** :
   - basse : 0,5 à 1 s avec un decay naturel (doctrine §9 : attaque
     franche, decay court) ; garder des harmoniques au-dessus du
     fondamental, sinon elle disparaît sur une petite sono ;
   - lead ou nappe à tenir : 2 à 4 s, avec une **partie centrale stable**
     (ni mouvement de filtre ni LFO non synchronisé), pour la boucler.
5. **Fichier** : 48 kHz / 16 bits ; l'attaque au tout début, sans silence
   avant (un vide de 10 ms décale le groove) ; court fondu en fin ; crêtes
   vers −1 dBFS et niveau perçu homogène entre samples, pour les échanger
   par preset lock sans saut de volume.
6. **DT2** : machine ONESHOT, sample sur la track 9 (basse) ou 10 (lead).
   Pour le lead : `PLAY` = FORWARD LOOP, `LOOP` dans la partie stable ; la
   durée suit le `LEN` de trig et l'enveloppe AMP (`HLD`, `DEC`).
7. **Écrire la ligne** en STEP (cf. [[enregistrement-quantize]], tuto 2)
   ou depuis les pads de la Maschine (groupes de gammes,
   [[controleur-maschine]]).

## Couvrir une large tessiture

La DT2 n'a pas de multi-sample par zones de notes : enregistrer deux ou
trois samples à l'octave (`lead_C3`, `lead_C4`, `lead_C5`), les mettre dans
le pool et passer de l'un à l'autre par **preset lock** (cf.
[[preset-pool]], cas 2). Chacun ne sert qu'à ±5 demi-tons autour de sa
note.

## Accords (dub techno)

Un sample par accord (min7, min9, sus), enregistré sur sa **fondamentale**
avec des notes resserrées. Transposé, l'accord garde sa forme et se déplace
en bloc (doctrine §11) : i → ♭VI → ♭VII = `TUNE` 0, −4, −2 (♭VI = 8
demi-tons au-dessus, soit 8 − 12 = −4 ; ♭VII = 10 − 12 = −2). Ce sont des
accords **parallèles** : un min7 transposé sur ♭VI sort de la gamme, c'est
la couleur dub techno, pas une harmonie diatonique.

## En live techno

- La ligne acid avec glides et accents ne se fait pas en one-shot : track
  MIDI vers le VST, ou boucle figée en STRETCH (cf. [[midi-vst]]).
- Plusieurs couleurs d'une même basse : le traitement **variations** de la
  vue Sound design (8.I) rend un one-shot en 4 à 32 tranches qui évoluent
  progressivement ; machine GRID, une couleur par pas (cf.
  [[slice-breaks]]).
- Basse et kick dans la même tonalité : accorder d'abord le kick, la basse
  suit (doctrine §11).

## Pièges

- **Noms d'octave** : chez Elektron, la note 60 s'appelle **C5** (manuel
  §8.4) ; beaucoup de DAW l'appellent C3 ou C4. Nommer les samples d'après
  le DAW et le noter une fois pour toutes.
- Échantillonner en USB avec `R.STRT` au seuil évite le silence avant
  l'attaque, mais un seuil trop haut mange le début d'une attaque douce.
- `FORWARD LOOP` sur une partie qui bouge = un « hoquet » à chaque tour :
  choisir `LOOP` sur un passage stable, au passage par zéro.
- Un `DEC` AMP court coupe la boucle avant la fin du `LEN` de trig.
- **À vérifier sur la machine** : jusqu'où une basse repitchée reste
  propre (±5 demi-tons supposé) ; si le `TUNE` en ONESHOT est
  parfaitement juste au demi-ton.

## À essayer (5 min)

Une basse sur C, 0,8 s, mono. Track 9, ligne en contretemps en STEP
(pas 3, 7, 11, 15), puis `TUNE` = −3 et +2 : écouter où le timbre commence
à se déformer.

Source : manuel DT2 OS 1.17, §8.4, §9.1, §13.1, A.2.1, A.2.3.
