---
tags: [digitakt, kb, tutos]
theme: Groove tribe à 143 BPM démonté (kick glissant qui tient le sub, stab à la tierce mineure en contretemps, charley accentué) et le battement entre la queue du kick et le stab
lot: 3
ordre: 3
source: "[[../../../refs/Groove tribe 143 BPM — analyse et recette Reaper DT2]] (analyse d'un extrait de live du 2026-11-01)"
auteur: Tom (extrait, analyse), rédaction à vérifier à la machine et dans Reaper
modele: DT2
os: "1.17"
statut: draft
updated: 2026-11-02
---

# Maison 3 — Groove tribe à 143 : le battement entre la queue du kick et le stab

**En une phrase** : dans un extrait de live tribe à 143,25 BPM, le
« roulement » du sub n'est ni un LFO, ni un sidechain, ni une basse qui
bouge : c'est le **battement à ~12 Hz** entre la queue du kick posée sur
A#1 (59 Hz) et un stab de sub à C#2 (71,75 Hz), une tierce mineure
au-dessus, posé sur chaque contretemps ; trois sons séquencés (kick, stab,
charley) et un phénomène acoustique qui naît de leur chevauchement.

L'analyse complète (méthode, chronologie au sample près, références
croisées) est dans
[[../../../refs/Groove tribe 143 BPM — analyse et recette Reaper DT2]] ;
cette fiche n'en garde que ce qui se programme. Fiches des gestes :
[[../lfo]] (glissando par LFO `ONE`), [[../microtiming-retrigs]],
[[../parameter-preset-locks]], [[../fill-conditions]], [[../filtres]],
[[../keyboard-gammes]]. Théorie : [[../theorie/kt-tonalite-du-grave]]
(KT5, battement), [[../theorie/kt-kickbass-contre-kick-basse]] (KT23,
architecture kick-sub), [[../theorie/kt-basses]] (KT21, basse en
contretemps), [[../theorie/kt-style-tribe]] (KT10).

## Sur notre grille

| Élément de l'extrait | Track | Rôle doctrine §1 | Remarque |
|---|---|---|---|
| Kick glissant à queue longue, se pose sur A#1 | 1 | kick | c'est le kick qui tient le sub sur le temps : architecture **kick-sub** de KT23, pas de rumble (la 2 reste vide) |
| Stab de sub C#2 sur 3, 7, 11, 15 | 9 | basse en contretemps (§9) | attaque franche, ~150 ms, retombé avant le kick suivant : exactement la basse en contretemps de la doctrine, mais accordée à la **tierce mineure** du kick, pas à la tonique ni à la quinte |
| Charley fermé en croches, contretemps fort | 6 | hat fermé | pas de hat ouvert dans le pattern (7 vide) |
| Crash ou open hat one-shot, 3e temps du break | 7 (ou 8 si c'est un crash) | hat ouvert / ride | une seule fois en 12 mesures |
| Rien sur 2 et 4 | 3 vide | clap / snare | toute la tension vient du contretemps ; un clap sur 2 et 4 casserait le côté roulant |

Deux écarts avec nos habitudes, à garder en tête :

- **L'intervalle du grave.** KT5 dit que la tierce « vit au-dessus de
  120 Hz » et que deux fondamentales proches s'annulent par battement ; la
  doctrine §11 accorde la basse sur la tonique ou la quinte. Ici le
  battement est **recherché** : à 59 et 71,75 Hz, l'écart de 12 Hz donne
  une pulsation un peu plus rapide que les doubles croches, qui fait
  rouler la basse sans la rendre carrée. L'intervalle kick / stab **est**
  le réglage du groove (recette 2).
- **Le contretemps en avance.** [[../microtiming-retrigs]] propose des
  hats en léger retard ; ici stab et charley du contretemps sont **~15 ms
  en avance** sur la grille, et le charley du temps ~6 ms en avance. Le
  kick, lui, tient la grille, conforme à la règle.

Le tempo (143) est sous notre terrain (160-170 BPM, README). Le mécanisme
se transpose, mais la fenêtre de chevauchement se resserre : à 165 BPM le
temps fait 60 / 165 = 364 ms, le contretemps tombe à 182 ms, un stab de
150 ms s'éteint à 332 ms, avant le kick suivant ; il reste ~180 ms de
cohabitation avec la queue du kick, soit deux lobes de battement au lieu de
quatre. La queue du kick doit donc encore sonner à 350 ms, ce qui rejoint
la limite de tempo de [[maison-grave-kickbass]] §5.3. À vérifier à
l'oreille : si le roulement disparaît à 165, allonger le decay du kick
avant de toucher à autre chose.

## Le piège physique, avant de câbler

Le battement **ne se programme pas** : il apparaît quand deux sinus de
hauteurs proches sonnent **en même temps**. Trois conditions, et chacune
peut le tuer :

1. **Le kick doit tenir sa note.** Après le glissando (~120 Hz → 59 Hz en
   ~110 ms), la queue est un sinus quasi pur encore à -4 dB à 200 ms et
   audible jusqu'au kick suivant. Un kick court et sec (doctrine §11 :
   « pas de note perceptible ») ne battra avec rien.
2. **Le stab doit chevaucher la queue à niveau comparable.** S'il est
   10 dB plus bas ou plus haut que la queue, on entend un son puis l'autre,
   pas la pulsation.
3. **L'écart doit rester petit.** À l'unisson le sub est lisse ; à la
   quinte (~29 Hz d'écart) le battement devient une rugosité ; à la tierce
   mineure (~12 Hz) c'est un tremolo. C'est un sinus contre un sinus : des
   harmoniques en plus brouillent la lecture.

Si on ne l'entend pas : allonger le decay du kick ou monter le stab, **pas
ajouter un LFO**. Un LFO de volume donnerait des lobes sur la grille ; les
lobes de l'original tombent entre les doubles croches (185, 270, 345,
410 ms pour des pas à 105, 209, 314 ms), signe qu'ils ne sont pas
séquencés.

Unité du micro timing sur la DT2 : 1/384 de mesure. À 143,25 BPM la
mesure fait 4 × 419 = 1 676 ms, soit 4,4 ms par cran ; -3 crans = -13 ms,
-4 = -17 ms. À 165 BPM, 4 × 364 / 384 = 3,8 ms par cran : -4 crans pour
retrouver les -15 ms.

## Recettes

Tempo 143 (ou 143,25 pour coller à l'extrait), pattern 16 pas, trois
tracks. Les valeurs sont des points de départ à ajuster sur le sound
system, pas des réglages lus dans l'enregistrement. Grille (`X` fort,
`x` faible, `.` rien) :

```text
                 1 . . . 2 . . . 3 . . . 4 . . .
1  KICK          X . . . X . . . X . . . X . . .
9  STAB (C#2)    . . X . . . X . . . X . . . X .
6  CHARLEY       x . X . x . X . x . X . x . X .
```

Rien ne tombe sur les 16e 2 et 4 (le « e » et le « a ») ; c'est le
contretemps qui porte l'accent, pas le temps.

### 1. Le kick qui fait le sub (track 1)

- **Source** : fichier 04 (kick isolé) ou un kick de la lib à queue
  longue ([[../kick-mental-vst]], [[maison-grave-kick]]).
- **Résultat** : à chaque temps, un glissando d'une octave qui se pose sur
  A#1 et tient jusqu'au temps suivant ; seul, le sub est lisse (fichier
  05).
- **Pas à pas** :
  1. Trigs sur 1, 5, 9, 13, micro timing 0 (le kick tient la grille).
  2. Page SRC : `TUNE` pour que la **queue** (pas l'attaque) se pose sur
     A#1 à 59 Hz, ou B1 si on reste en 440 Hz (l'extrait est ~40 cents
     au-dessus). Mesurer sur la queue avec SPAN ou ReaTune via Overbridge
     (doctrine §11). Fixer la tonique du pattern sur cette note
     ([[../keyboard-gammes]]).
  3. Page AMP : `DEC` long, la queue doit encore sonner à 350 ms (un
     temps à 143 fait 419 ms, à 165 364 ms).
  4. Page FLTR : passe-bas fermé juste au-dessus de l'attaque, pour
     n'avoir qu'un sinus après le clic ; le clic lui-même reste entre
     400 Hz et 2 kHz.
  5. Si le sample n'a pas de glissando : `[MOD]` LFO 1, `DEST` = SRC
     `TUNE`, `WAVE` = EXP, `MODE` = `ONE`, `DEP` négatif, vitesse réglée
     pour ~100 ms de descente ([[../lfo]] ; un temps = `SPD` × `MULT` =
     512, ~100 ms est le quart d'un temps, donc ~2048 au départ puis à
     l'oreille). `LFO.T` ON sur les trigs du kick.
- **Attention** : le fichier 04 a **perdu son clic d'attaque**, parti dans
  la piste charley au découpage (même instant, même bande). Pour un kick
  complet, lui remettre un transient (couche click de
  [[maison-grave-kick]]) ou prendre un kick de la lib et ne garder du 04
  que la hauteur cible.
- **Chez nous** : c'est l'architecture **kick-sub** de KT23 ; la track 2
  reste vide, pas de rumble, sinon deux sinus de plus dans la même zone
  et le battement devient boue.

### 2. Le stab à la tierce mineure (track 9)

- **Source** : fichier 06 (stab isolé, sub quasi pur) ou un sinus
  ([[../oneshots-synthe]], [[maison-grave-basse]] §6.1 pour un one-shot
  Vital).
- **Résultat** : dès que le stab entre, le sub se met à rouler (fichier
  08 : kick + stab réassemblés, le wobble réapparaît).
- **Pas à pas** :
  1. Trigs sur 3, 7, 11, 15.
  2. Page SRC : `TUNE` = note du kick **+ 3 demi-tons** (C#2 si le kick
     est sur A#1). Accorder le kick d'abord, le stab par rapport à lui.
  3. Page AMP : `ATK` 0, `DEC` ~150 ms, pas de sustain ; le stab doit être
     éteint vers 340 ms, avant le kick suivant (doctrine §9).
  4. Page FLTR : passe-bas ouvert juste assez pour laisser l'attaque ;
     pas d'overdrive, le stab doit rester un sinus (un peu de 2e et 3e
     harmonique dans l'original, pas plus).
  5. Micro timing **-3 à -4** sur les quatre trigs (`[TRIG]` +
     `[LEFT]`), soit ~15 ms d'avance.
  6. Niveau : la queue du kick et le stab cohabitent ~200 ms à niveau
     comparable ; régler `VOL` jusqu'à entendre quatre lobes par temps
     (deux à 165).
- **Attention** : la basse en contretemps de la doctrine §9 est
  « passe-haut un peu monté, laisse le sub au kick ». Ici c'est l'inverse
  voulu : le stab **est** dans le sub, à 72 Hz. Ne pas lui mettre le
  passe-haut par réflexe.
- **Chez nous** : tester l'intervalle montre le phénomène mieux que
  n'importe quelle explication. Même pattern, `TUNE` du stab à +0
  (unisson : lisse), +3 (tierce mineure : tremolo), +7 (quinte :
  rugosité). Le choix de l'intervalle est un réglage de groove à part
  entière, à noter sur le preset du stab.

### 3. Le charley en croches, accent au contretemps (track 6)

- **Source** : fichiers 11 (coup du temps) et 12 (coup du contretemps),
  ou un charley fermé sombre de la lib.
- **Résultat** : une croche régulière où le contretemps est 30 % plus
  fort et presque deux fois plus long (fichier 13).
- **Pas à pas** :
  1. Trigs sur toutes les croches : 1, 3, 5, 7, 9, 11, 13, 15.
  2. Page TRIG : `VEL` ~70 sur les temps (1, 5, 9, 13), 110-127 sur les
     contretemps.
  3. P-lock AMP `DEC` plus long sur les contretemps (~70 ms contre ~40 ms
     sur les temps) : maintenir le trig, tourner `DEC`
     ([[../parameter-preset-locks]]).
  4. Page FLTR : passe-bas vers 3-4 kHz pour la couleur sombre
     (centroïde ~1,6 kHz, énergie surtout 400-800 Hz dans l'original).
  5. Micro timing **-1** sur les temps, **-3 à -4** sur les contretemps.
- **Attention** : le fichier 11 contient le clic du kick (même instant,
  même bande, voir recette 1). L'extrait ne contient rien au-dessus de
  8 kHz : impossible de dire si le charley est sombre par choix ou par
  captation. Sur un sound system, l'essayer aussi plus ouvert.
- **Chez nous** : KT20 ([[../theorie/kt-hats]]) donne le hat fermé comme
  grille et l'ouvert comme contretemps ; ici le fermé fait les deux,
  l'accent de vélocité remplace le changement de sample. La 7 reste
  libre pour le one-shot du break.

### 4. Arrangement sur 12 mesures : mutes, ghosts, niveau

- **Source** : mesures 1 à 12 de l'extrait ; le pattern est identique
  d'un bout à l'autre, seuls bougent les trigs de kick, le niveau du sub
  et un one-shot.
- **Résultat** : un plateau de 3 mesures, un break d'une mesure, une
  reprise, une densification progressive, une amorce de fill.
- **Pas à pas** :
  1. **Mesures 1-3** : pattern plein, sub à fond.
  2. **Mesure 4, break** : un second pattern (ou la seconde séquence de
     [[elektronauts-seconde-sequence]]) avec le kick amputé
     `X x . . X . x x X . x . X . . x`, `VOL` des tracks 1 et 9 **baissé
     de ~10 dB plutôt que muté** (le sub reste présent dans l'original),
     un crash ou open hat sur la track 7 au 3e temps (pas 9).
  3. **Mesures 5-6** : retour au pattern plein.
  4. **Mesures 7-11, densification** : ghosts de kick sur le 2e ou 3e
     pas après chaque temps (pas 2-3, 6-7, 10-11, 14-15), `VEL` basse,
     `DEC` locké court (sinon le ghost relance la queue et casse le
     battement), condition `25%` ou `A:B` pour qu'ils n'arrivent pas tous
     à la fois ([[../fill-conditions]]).
  5. **Mesures 5 → 12, fade du sub** : le niveau du sub descend
     d'environ 7 dB sur 8 mesures. Geste de live : `LEVEL` des tracks 1
     et 9 au knob, ou passe-haut du filtre qu'on remonte sur les deux.
  6. **Mesure 12** : temps 2 et 4 du kick affaiblis (`VEL` lockée),
     doubles croches intermédiaires qui remontent : amorce de fill ou de
     transition ([[elektronauts-transitions]]).
- **Chez nous** : c'est la montée par mutes et niveau de la doctrine §4
  et §6, sans jamais changer de note ni de pattern de base ; la tension
  se joue sur la **présence** du sub, pas sur sa hauteur.

### 5. Variante : kick court et vraie note de basse

- **Résultat** : le même groove avec un kick libre (court, claquant), le
  sub tenu par la track 9 ; architecture **kick + basse** de KT23.
- **Pas à pas** :
  1. Track 1 : kick court, pas de glissando nécessaire.
  2. Track 9 : trig supplémentaire sur 1, 5, 9, 13 avec `TUNE` locké sur
     A#1 (la note du kick) et `DEC` long (la queue doit atteindre le
     contretemps et au-delà) ; les trigs 3, 7, 11, 15 gardent C#2 et le
     decay court.
  3. Même micro timing que la recette 2 sur les contretemps, 0 sur les
     temps.
- **Attention** : la 9 joue alors deux notes qui se chevauchent sur une
  machine monophonique par track : la note A#1 est coupée à l'entrée du
  stab C#2 si le sample n'a pas de release. *À vérifier à la machine* :
  si la coupure tue le battement, mettre la note tenue sur la track 2 (à
  la place du rumble, même zone) et garder la 9 pour le stab.
- **Chez nous** : plus de liberté sur le kick, mais la 9 ne peut plus
  servir à autre chose ; c'est le choix d'architecture de KT23, à faire
  avant le sound design.

### 6. Vérifier dans Reaper

- **Résultat** : le pattern reconstruit à côté de l'original, pour
  démonter le groove et contrôler ses réglages DT2 contre la référence.
- **Pas à pas** :
  1. Projet à 143,25 BPM, grille 1/16, quatre pistes : Kick, Stab,
     Charley, Original (fichier 01, mutée par défaut). Un bus Sub où Kick
     et Stab envoient, avec un ReaEQ passe-bas à 160 Hz qu'on active pour
     isoler le grave (projet modèle : [[maison-grave-projet-reaper]]).
  2. ReaSamplOmatic5000 sur chaque piste avec les one-shots 04, 06, 11,
     12, mode « Note (semitone shifted) » ; les samples sont déjà à la
     bonne hauteur, note de base = note jouée. Pour synthétiser : ReaSynth
     en sinus pur pour le stab (C#2, attack 0, decay 150 ms, sustain 0) et
     pour la queue de kick (A#1, release long) ; le glissando est plus
     simple en gardant le sample.
  3. MIDI, un item d'une mesure par piste en boucle. Kick : notes sur
     chaque temps, vélocité fixe. Stab : notes sur les « et », durée
     1/16, puis toutes sélectionnées et décalées de -15 ms (Nudge en ms,
     ou snap désactivé). Charley : toutes les croches, vélocité ~70 sur
     les temps et ~115 sur les contretemps, -15 ms sur les contretemps,
     -6 ms sur les temps.
  4. Mesurer : sur le bus Sub, SPAN ou ReaEQ en affichage spectre montre
     les deux pics à 59 et 72 Hz pendant la seconde moitié du temps ;
     ReaTune sur Kick confirme la note d'atterrissage. Pour entendre le
     battement sans ambiguïté, Rate du projet à 50 % ou fichier 10.
  5. Tester l'intervalle : transposition du stab dans ReaSamplOmatic5000
     (0, +3, +7), bus Sub en boucle.
  6. Exporter vers la DT2 : chaque piste en one-shot 48 kHz / 16 bits mono
     ([[maison-grave-rendu-dt2]]), ou directement le kick avec sa queue
     longue pour la version « kick qui fait le sub ».

## Sons isolés

Quinze fichiers (44,1 kHz, 16 bits, mono, normalisés ; les boucles font
4 mesures à 143,25 BPM), pour l'instant dans
`~/Downloads/sons_isoles_live/` (archive `sons_isoles_live.zip`), destination
dans la lib à arbitrer. Ordre d'écoute conseillé : 02 → 10 → 05 → 07 → 08
→ 13 → 14 → 15.

| Fichier | Contenu | Ce qu'il démontre |
|---|---|---|
| 01_original_2mesures | 2 mesures brutes | la référence |
| 02_original_sub_only_lowpass160 | l'original coupé à 160 Hz | le roulement du sub tel quel |
| 03_temps_moyenne_boucle | le temps moyen (28 temps alignés) bouclé | ce qui est séquencé, sans le bruit de salle |
| 04_kick_seul_oneshot / 05_kick_seul_boucle | kick isolé, one-shot et boucle | glissando + queue à 59 Hz ; seul, le sub est lisse |
| 06_stab_seul_oneshot / 07_stab_seul_boucle | stab isolé | le stab C#2, sub quasi pur |
| 08_kick_plus_stab_boucle | les deux réassemblés | le wobble réapparaît : preuve que c'est un battement |
| 09_temps_moyenne_demi_vitesse / 10_sub_only_demi_vitesse | une octave plus bas, moitié moins vite | le battement à 6 Hz devient évident, et on entend qu'il n'est pas sur les doubles croches |
| 11_charley_temps_oneshot / 12_charley_contretemps_oneshot | coup du temps, coup du contretemps | le même son, le contretemps plus fort et plus long ; le coup du temps contient le clic du kick |
| 13_charley_seul_boucle | les croches seules | l'accent sur le contretemps |
| 14_kit_complet_boucle | kick + stab + charley | la reconstruction complète |
| 15_reconstruction_vs_original | 2 mesures reconstruites, silence, 2 mesures d'origine | ce que la décomposition capture et ce qu'elle laisse (résidu ~18 % en RMS : salle, ghosts, variations) |

Réserves : l'enregistrement est très compressé (pic à 0 dBFS, RMS à
-8 dB) et vide au-dessus de 8 kHz ; les hauteurs et les placements sont
fiables, les niveaux relatifs et la couleur du charley le sont moins. Les
ghosts de kick des mesures 7-11 et le one-shot du break n'ont pas été
isolés. Méthode détaillée dans la note de `refs/`.

## À essayer (5 min)

Écouter 05 (kick seul, lisse) puis 08 (kick + stab, ça roule). Sur la DT2,
recettes 1 et 2 seulement, puis le test d'intervalle : `TUNE` du stab à
+0, +3, +7 sur le même pattern, au casque puis sur le sub. Noter
l'intervalle qui roule le mieux sur le sound system ; ce n'est pas
forcément +3 une fois le kick remplacé par un des nôtres.

## Liens

[[../../../refs/Groove tribe 143 BPM — analyse et recette Reaper DT2]] ·
[[../theorie/kt-tonalite-du-grave]] · [[../theorie/kt-kickbass-contre-kick-basse]] ·
[[../theorie/kt-basses]] · [[../theorie/kt-hats]] · [[../theorie/kt-style-tribe]] ·
[[../lfo]] · [[../microtiming-retrigs]] · [[../parameter-preset-locks]] ·
[[../fill-conditions]] · [[../filtres]] · [[../keyboard-gammes]] ·
[[../kick-mental-vst]] · [[maison-grave-kick]] · [[maison-grave-kickbass]] ·
[[maison-grave-basse]] · [[maison-grave-projet-reaper]] ·
[[maison-grave-rendu-dt2]] · [[elektronauts-seconde-sequence]] ·
[[elektronauts-transitions]] · [[../../doctrine]] §1, §4, §9, §11
