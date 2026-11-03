---
tags: [digitakt, kb, tutos]
theme: Grave sur Mac, ch. 6, tuto basse : Vital en contretemps (one-shot par note), trois couches Attack Magazine, ligne Acid V, validation
lot: 4
ordre: 6
source: "échange de travail du 2026-10-29 (stack retenue) ; chapitre détaché du tuto le 2026-10-31"
auteur: Tom (stack), rédaction à vérifier dans Reaper
modele: DT2
os: "1.17"
stack: [Reaper, Vital, Maschine Drumsynth Kick, Kick 3, iZotope Trash Lite, SPAN, ReaComp, Acid V]
parent: maison-sounddesign-grave-reaper
statut: draft
updated: 2026-10-31
---

# Grave sur Mac, ch. 6 — La basse, la 9 en contretemps et la ligne acid

Chapitre 6 du tuto « sound design préparatoire » (lot 4 de [[_index]]).
Le hub [[maison-sounddesign-grave-reaper]] porte les arbitrages (§0), la stack et
les notions Reaper (§1), les pièges (§8) et les exercices (§9). Les numéros
de section sont ceux du tuto entier : un renvoi « §n » vise le chapitre n,
avec le lien de sa fiche quand ce n'est pas celle-ci.

## 6. Tuto basse : la 9 en contretemps, et la ligne acid

En architecture kick + basse, la basse porte le sub entre les kicks (le
stem bass de Tekotak est à +17,5 dB du sub du kick, KT23) ; en kick +
rumble, elle vit au-dessus (80-250 Hz, KT5), passe-haut monté. Dans les
deux cas : attaque franche, decay court, retombée avant le kick suivant,
**la double-croche du kick vide** (Attack Magazine : c'est un placement de
trigs, pas un compresseur).

### 6.1 Basse Vital en contretemps (track 9, one-shot BS)

1. Piste BASS, Vital, **voices 1**, legato, portamento 0 (ou court pour un
   slide ponctuel), OSC 1 sinus ou triangle, OSC 2 en dent de scie à -12 dB
   pour les harmoniques, phase fixe, unisson 1.
2. ENV 1 : attaque 2-5 ms (franche, sans clic), decay 120-200 ms à 165 BPM (le temps fait 364 ms)
   (moins qu'un temps : 324 ms), sustain 0 ; **pas de release** longue.
3. Filtre ladder ou diode, cutoff 150-400 Hz, enveloppe de filtre (ENV 3)
   rapide pour le claquement, résonance modérée ; drive du filtre pour le
   mordant (doctrine §9 : la rondeur est une variation, pas la base).
4. ReaEQ en aval : **passe-haut 60-80 Hz** si un rumble ou un kick long tient
   le sub, 30 Hz si la basse porte le sub (kick court) ; passe-bas 350 Hz
   sur la couche mid (Attack : synthé HPF 65 / LPF 350).
5. JS Saturation léger, puis ReaComp sidechainé par KICK avec les mêmes
   réglages que le rumble ([[maison-grave-projet-reaper]] §2.3). Sur la DT2 : `SCS` = TRK1 pour la 9 aussi.
6. Item MIDI `..x...x...x...x.` sur la tonique, puis variante tonique /
   quinte (`..x...x...x...y.`). Comparer avec le kick : propre sur la
   tonique et la quinte, brouillé sur la tierce (KT5, exercice 2).
7. Export **one-shot par note** : une note de 200 ms rendue seule, nommée
   `bass_sub_F#.wav`, `bass_sub_C#.wav` (quinte) ; sur la DT2, machine
   ONESHOT, `TUNE` 0, trigs en contretemps. Variante boucle (BL) : rendre
   une mesure complète avec le ducking, pour une 9 qui « roule ».

### 6.2 Trois couches (Attack Magazine)

Quand une seule basse ne tient pas : **sub** = la queue du kick elle-même,
passe-bas 80 Hz (c'est le kickbass en version douce) ; **synthé** Vital
HPF 65 / LPF 350 ; **percussive** = le kick envoyé dans un delay à la
double-croche (ReaDelay, 1/16, feedback bas, passe-bas 200 Hz), le « rumble
en contretemps » de [[maison-rumble-dans-le-kick]].
Sur la DT2 ces trois couches ne tiennent pas sur une track : choisir
laquelle est la 9, figer les autres dans le kick ou le rumble.

### 6.3 Ligne acid, Acid V (track 10, et basse acid)

1. Piste ACID, Acid V ; séquence interne ou item MIDI de 16 pas sur le mode
   de la bank (phrygien sur la tonique, [[../keyboard-gammes]]).
   Dent de scie pour l'acid tribe, carré pour un son plus rond.
2. Cutoff bas, résonance haute, env mod fort, decay court ; accents sur
   deux ou trois pas, un slide par mesure au plus. Le drive interne d'Acid V
   pour le grain ; Trash en parallèle ([[maison-grave-projet-reaper]] §2.4) pour l'acid core.
3. **Passe-haut** ReaEQ à 120-200 Hz dès que le grave est tenu par un
   kickbass ou un rumble : la ligne acid est une ligne, pas une basse (KT7,
   KT11). En **acid tribe** sans kickbass, Acid V peut être la basse en
   contretemps elle-même (`X.x.X.x.` du sub quand la basse descend sous
   200 Hz, KT5) : alors passe-haut à 40-60 Hz et ReaComp sidechainé.
4. Pour la DT2, deux voies : rendre des one-shots par note (track 10 en
   audio, un sample par degré), ou garder Acid V live sur le Mac séquencé
   par une track MIDI ([[../midi-vst]]).

### 6.4 Valider une basse

Avec le kick, au casque : aucun battement (sinon la note est fausse de
quelques hertz, KT5) ; la double-croche du kick reste vide ; le kick garde
son attaque ; sur SPAN, la basse n'ajoute rien sous 60 Hz quand un rumble
ou un kickbass y est déjà.

## Liens

[[maison-sounddesign-grave-reaper]] · [[maison-grave-kickbass]] · [[maison-grave-rendu-dt2]]

#digitakt #kb #tutos #sounddesign
