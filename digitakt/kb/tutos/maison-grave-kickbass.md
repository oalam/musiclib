---
tags: [digitakt, kb, tutos]
theme: Grave sur Mac, ch. 5, tuto kickbass : Vital saturé ou sinus, Kick 3, limite de tempo vers le kick-sub, validation
lot: 4
ordre: 5
source: "échange de travail du 2026-10-29 (stack retenue) ; chapitre détaché du tuto le 2026-10-31"
auteur: Tom (stack), rédaction à vérifier dans Reaper
modele: DT2
os: "1.17"
stack: [Reaper, Vital, Maschine Drumsynth Kick, Kick 3, iZotope Trash Lite, SPAN, ReaComp, Acid V]
parent: maison-sounddesign-grave-reaper
statut: draft
updated: 2026-10-31
---

# Grave sur Mac, ch. 5 — Le kickbass, le kick qui est la basse

Chapitre 5 du tuto « sound design préparatoire » (lot 4 de [[_index]]).
Le hub [[maison-sounddesign-grave-reaper]] porte les arbitrages (§0), la stack et
les notions Reaper (§1), les pièges (§8) et les exercices (§9). Les numéros
de section sont ceux du tuto entier : un renvoi « §n » vise le chapitre n,
avec le lien de sa fiche quand ce n'est pas celle-ci.

## 5. Tuto kickbass : le kick qui est la basse

Référence mesurée (KT23) : Neurotribe à 161,5 BPM, pitch envelope 84 →
57 Hz en 130 ms, harmoniques 120-300 Hz à -5,5 dB (saturé), sub tenu à -8
dB sur toute la seconde moitié du temps ; Six ou Sept à 143,6, click puis
sinus pur 57 → 50 Hz, harmoniques à -17 dB. Deux kickbass, deux chaînes.

### 5.1 Vital

1. Piste KICKBASS, Vital : OSC 1 sinus, voices 1, phase fixe ([[maison-grave-kick]] §3.3).
2. ENV 1 (ampli) : decay long, **release 5-10 ms**, et la **longueur de la
   note MIDI** égale au temps moins 10-20 ms (à 165 BPM, 364 - 15 = 349 ms) :
   la note s'arrête juste avant le kick suivant, la queue ne mange pas
   l'attaque suivante. Sur la DT2 ce sera l'AMP de la track 1 qui coupe.
3. ENV 2 sur Transpose, +24 à +30 demi-tons, decay 100-130 ms (Neurotribe)
   ou 20-40 ms puis sinus pur (Six ou Sept).
4. **Version saturée** (free party) : filtre ladder, drive haut, puis
   distorsion Vital Soft Clip, puis Trash sur la bande 3/4 ([[maison-grave-projet-reaper]] §2.4, coupure
   basse du splitter à 90 Hz pour que le sinus reste intact), passe-bas final 300 Hz
   (LOWPASS 4 sur la DT2). Cible : harmoniques 120-300 Hz à -5 ou -6 dB du
   fondamental sur SPAN.
5. **Version sinus** (club) : pas de Trash, un seul étage de Soft Clip très
   léger pour les harmoniques à -15 dB ; le click vient d'OSC 2 ([[maison-grave-kick]] §3.3).
6. Hauteur : la note MIDI jouée est la tonique ; les progressions se feront
   par p-lock de `TUNE` sur la DT2 (tonique 4 mesures, quinte 4 mesures,
   KT5), donc **un seul export par note**, pas de glissando.

### 5.2 Kick 3

Même chose en dessinant : enveloppe de volume de la couche sub avec un
plateau qui dure jusqu'au temps suivant (lire les ms), enveloppe de pitch
courte, note d'arrivée = tonique, harmoniques du sub poussées pour la
version saturée ; Trash en aval sur la bande 3/4 ([[maison-grave-projet-reaper]] §2.4). L'option de suivre la hauteur de
la seule queue (pitch tracking des sub tails) sert ici : la queue suit la
note MIDI, le click reste fixe.

### 5.3 Tempo et limite

Entre 160 et 170 BPM le temps fait 353 à 375 ms : c'est exactement la
zone du kickbass saturé de référence (Neurotribe, 161,5), et c'est aussi
sa limite haute. À 170, une queue qui tient encore -8 dB à 300 ms laisse
53 ms avant le kick suivant : assez si la note MIDI s'arrête à 340 ms,
trop peu si la saturation allonge la queue. L'autre option à ce tempo est
le **kick-sub** (sinus écrêté court, sans note tenue, Floxytek, KT23) :
Vital, sinus, decay 150-200 ms, Hard Clip fort, pas de Trash. Rendre les
deux à 170 et comparer ; en dessous de 165 le kickbass saturé gagne
presque toujours.

### 5.4 Valider un kickbass

Tenue du sub entre deux kicks (SPAN, 30-100 Hz) **au-dessus de -10 dB** de
l'attaque, sans trou ni battement ; rien sur la piste BASS ni RUMBLE (une
seule architecture) ; sur la DT2, la 9 et la 2 restent vides. Export
`kickbass_<sat|sin>_<note>_<bpm>.wav`.

## Liens

[[maison-sounddesign-grave-reaper]] · [[maison-grave-rumble]] · [[maison-grave-basse]]

#digitakt #kb #tutos #sounddesign
