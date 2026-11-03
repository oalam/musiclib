---
tags: [digitakt, kb, tutos]
theme: Grave sur Mac, ch. 4, tuto rumble : chaîne plug-in par plug-in sur la piste RUMBLE, deux départs de passe-haut, variante sample, couche sinus, rendu boucle ou un coup
lot: 4
ordre: 4
source: "échange de travail du 2026-10-29 (stack retenue) ; chapitre détaché du tuto le 2026-10-31"
auteur: Tom (stack), rédaction à vérifier dans Reaper
modele: DT2
os: "1.17"
stack: [Reaper, Vital, Maschine Drumsynth Kick, Kick 3, iZotope Trash Lite, SPAN, ReaComp, Acid V]
parent: maison-sounddesign-grave-reaper
statut: draft
updated: 2026-10-31
---

# Grave sur Mac, ch. 4 — Le rumble, reverb saturée duckée par le kick

Chapitre 4 du tuto « sound design préparatoire » (lot 4 de [[_index]]).
Le hub [[maison-sounddesign-grave-reaper]] porte les arbitrages (§0), la stack et
les notions Reaper (§1), les pièges (§8) et les exercices (§9). Les numéros
de section sont ceux du tuto entier : un renvoi « §n » vise le chapitre n,
avec le lien de sa fiche quand ce n'est pas celle-ci.

## 4. Tuto rumble : la reverb saturée, duckée par le kick

Même recette que la chaîne `Rumble` de [[../../../sounddesign/rumble]] (Freeverb,
passe-bas, tanh, passe-bas, passe-haut, duck) et que la doctrine §9, avec
les plug-ins de Reaper. Deux départs possibles pour le passe-haut avant la
reverb (désaccord des sources, [[../rumble-grave]]) : les deux
se rendent et se comparent.

### 4.1 Chaîne sur la piste RUMBLE

| Étape | Plug-in | Réglage de départ | Pourquoi |
|---|---|---|---|
| 1. Entrée | send KICK → RUMBLE, pré-fader, canaux 1/2 | 0 dB | le kick sec reste sur KICK, la reverb n'entend que lui |
| 2. Passe-haut avant reverb | ReaEQ, **une seule bande** de type High Pass, posée sur le kick qui arrive par le send, **avant** qu'il n'entre dans la reverb ; la piste KICK n'est pas touchée | **départ A** : fréquence 30 Hz ; **départ B** : fréquence 120 Hz. Même bande, deux valeurs, jamais les deux à la fois ; détail sous le tableau | ce filtre décide de ce que la reverb étale. A ne retire que l'infra : le sub du kick entre dans la queue, le rumble tient lui-même le 40-60 Hz entre les coups (Futureproof, hard techno 140-150). B retient le sub : la queue ne contient que le corps, le rumble vit en 100-250 Hz avec le passe-bas de l'étape 4, le 20-60 Hz reste au kick seul (Myloops, doctrine §9, KT5). Les sources se contredisent et aucune n'est écrite pour 160-170 BPM : rendre les deux (exercice 2) ; à nos tempos B est le défaut, A demande plus de ducking et accumule du sub entre les coups sur un gros système |
| 3. Reverb | ReaVerbate | wet 100 %, dry 0, room size grand, **dampening** 0,5-0,6 (sombre), pre-delay 0, **width 0** | queue de 1,5 à 2 s à 160-170 BPM (la croche vaut 176-187 ms, le temps 353-375 ms : les queues doivent se chevaucher d'un temps à l'autre sans s'accumuler sur la mesure) ; jamais au-delà de 3-4 s ; aucune modulation dans la queue (ReaVerbate n'en a pas) |
| 4. Passe-bas après reverb | ReaEQ, low-pass 24 dB/oct | 200-250 Hz (rumble qui pousse, `gritty`) ou 130-170 Hz (rond, `deep`) | ce qui distingue un rumble d'une reverb de kick |
| 5. Saturation | Trash Lite | style doux (tube, tape), drive 10-16 dB (`deep`) à 20-26 dB (`gritty`), **mix 30-50 %** | harmoniques 80-160 Hz audibles sur petit système ; après la reverb (Futureproof), le fizz se juge au téléphone |
| 6. Second passe-bas | ReaEQ, low-pass 24 dB/oct, résonance légère | 150-200 Hz | retire les harmoniques aiguës créées en 5 ; avec de la résonance, le rumble « parle » |
| 7. Passe-haut | ReaEQ, high-pass | 30-40 Hz (50-60 si le kick a déjà beaucoup de sub) | l'infra-grave consomme de la puissance sans être entendu |
| 8. Ducking | ReaComp, sidechain ([[maison-grave-projet-reaper]] §2.3) | 24-30 dB de creux pour que le kick sorte seul (10-12 dB si le rumble reste présent sous le kick), attaque 1-2 ms, release une croche | la pompe qui fait « rouler » |
| 9. Mono | ReaVerbate « Stereo width » à 0 ; pour un item audio, clic droit > Item properties > Channel mode = Mono (downmix) ; pour un instrument, unisson 1 à la source | | mono sous 120 Hz |
| 10. Niveau | fader | le rumble **sous** le kick ; sur la DT2 la 2 se règle sous la 1 après coup | une prise normalisée ment sur le niveau |

**Régler le passe-haut dans ReaEQ (étape 2), à l'écran.** ReaEQ s'ouvre
avec plusieurs bandes par défaut ; il n'en faut qu'une.

1. Onglet **1** : Type = **High Pass** ; Frequency = **30** (départ A) ou
   **120** (départ B). Le champ Gain ne compte pas pour un passe-haut.
2. Toujours sur la bande 1, régler **Bandwidth** pour que la courbe
   descende sans remonter au-dessus de 0 dB (1,7 oct convient, vérifié à
   l'écran le 2026-10-30) : une valeur plus grande fait résonner le
   filtre, avec une bosse de plusieurs dB juste au-dessus de la coupure,
   qui gonfle le sub du kick avant la reverb, l'inverse du but.
3. Onglets **2**, 3, 4 s'il y en a : **Remove band**. Une cloche à 0 dB ne
   fait rien, et un shelf par défaut fausse la comparaison.
4. Bouton **+** à côté de « No preset » : enregistrer `rumble HPF A 30`,
   passer la fréquence à 120, enregistrer `rumble HPF B 120`. Les deux se
   rappellent dans le menu déroulant ; rendre la boucle avec chacun
   (exercice 2) et écouter au même niveau sous le kick.
5. Le passe-bas de l'étape 4 va dans la **seconde** ReaEQ, après
   ReaVerbate, pas dans celle-ci.

Le preset `deep` de la chaîne Python (dampening 0,6, drive 14 dB, retour
220 ms, 150 BPM) et `gritty` (dampening 0,3, drive 26 dB, bande +4 dB à
120 Hz, retour 140 ms, écrit pour 185 BPM) donnent deux cibles A/B, à
relancer au tempo de la bank : rendre le même
kick avec les deux (`sounddesign.py`) et avec Reaper, comparer au même
niveau.

### 4.2 Variante par sample (poids constant)

Un drone, un bruit filtré ou un field recording de la branche TONAL de la
banque, sur une piste RUMBLE-S : passe-haut 30 Hz, passe-bas 200-250 Hz,
Trash doux, même ReaComp que le rumble, mixé 3 à 6 dB sous le niveau où on
l'entend seul. Combinaison cible (Myloops, via rumble-grave) : le rumble par
reverb pour le mouvement, la couche sample pour le poids.

### 4.3 Couche sinus

Vital sur une piste SUB-R : sinus **une octave sous** la fondamentale du
kick (F#0 = 23,1 Hz pour un kick en F#1 ; à 46,2 / 2), attaque 200 ms,
mixé 10-12 dB sous le rumble, ducké pareil. Uniquement sur un vrai sub ;
à retirer si le système ne descend pas (passe-haut du rig à 35-40 Hz,
[[../../../technique/sound-system-free-party]]).

### 4.4 Rendu du rumble pour la DT2

Deux formats, comme dans [[../../../sounddesign/rumble]] :

- **Boucle** : sélection temporelle d'exactement 1 ou 2 mesures (à 165 BPM,
  2 mesures = 2 × 4 × 60 / 165 = 2,909 s), kick muté dans le master,
  rendu de la piste RUMBLE ; la boucle part et finit dans le creux du
  ducking. Sur la DT2 : track 2 en lecture loop, un trig par mesure.
- **Un coup** : un seul kick, rendu d'un temps (0,364 s à 165) plus un
  fondu de 20 ms. Sur la DT2 : un trig sur chaque pas du kick, fills
  compris (doctrine §9).

Nom `rumble_<preset>_<note>_<bpm>.wav` ; rendre une version par tempo,
jamais de time-stretch sur la machine. Après versement dans la library, le
rendu prend un nom DT2 en miroir du kick (`RM 165 ... `, circuit 8.L2 dans
[[../../../sounddesign/rumble]]).

### 4.5 Valider un rumble

Sous le kick, au casque : le kick garde son attaque (sinon ducking plus
profond ou plus rapide, rumble baissé de 2-3 dB) ; entre deux kicks, le
30-100 Hz remonte sans dépasser l'attaque ; en mono, rien ne disparaît ;
au téléphone, le grondement s'entend encore par ses harmoniques. La table
de dépannage est dans [[../rumble-grave]].

## Liens

[[maison-sounddesign-grave-reaper]] · [[maison-grave-kick]] · [[maison-grave-kickbass]]

#digitakt #kb #tutos #sounddesign
