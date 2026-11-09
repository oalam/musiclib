---
# Fiche des banques pour mk-brain (mk-brain/SPEC.md § Projets) : source de
# `mk-brain convert`, qui écrit mk-brain/projects/solaris.yaml. Tonalités et
# tempos recoupés avec library/lives/solaris.json (keys, tempos) : une
# divergence est une erreur. Modes : eolien, phrygien, dorien,
# mineur-harmonique, phrygien-dominant, penta-mineure, chromatique.
mkbrain:
  live: library/lives/solaris.json
  defaults: {phrase: 32}
  banks:
    A-HALF:
      title: Half-time
      desc: Ouverture lourde et lente, basse lente, peu de notes
      tempo: 160
      tonique: F
      mode: eolien
    B-DNB:
      title: Drum and bass
      desc: Ça s'ouvre, vers la jungle et les rollers, reese fa / sol bémol
      tempo: 165
      tonique: F
      mode: phrygien
    C-GROOVE:
      title: Groove tribe
      desc: Kick glissant la#, stab à la tierce, charley ; paliers vers 152
      tempo: 143
      tonique: A#
      mode: eolien
    D-ACID:
      title: Acid
      desc: L'acid entre en la#, percs, kick-sub ; paliers vers 162
      tempo: 152
      tonique: A#
      mode: eolien
    E-TRIBE:
      title: Tribe
      desc: Cœur du set, rumble, couleur phrygienne ; fin en respiration
      tempo: 162
      tonique: A#
      mode: phrygien
    F-MENTAL:
      title: Mental
      desc: Tension hypnotique en do, drone et acid, kick sèche
      tempo: 168
      tonique: C
      mode: eolien
    G-JOKER:
      title: Jokers
      desc: Breaks et secours, kick + sub seuls en fa, la# et do
      tempo: 165
      tonique: A#
      mode: chromatique
---

# Live Digitakt 2 — doctrine free party

Oct 13, 2026 · @tom

## Structure du set

Un live de 1h20 à 1h50 qui reste entre 160 et 168 BPM, avec une seule exception voulue : après la DnB, une retombée à 143 sur le groove tribe en la# ([[kb/tutos/maison-groove-tribe-battement]], testé le 2026-11-04 : c'est en la# que ça sonne), qui remonte ensuite par paliers, par l'acid à 152, jusqu'au tribe à 162. Partout ailleurs l'énergie monte par la densité, la saturation et la tonalité, pas par le tempo. Plan des banques révisé le 2026-11-06 (A Half-time, B DnB, C Groove, D Acid, E Tribe, F Mental, G Jokers) : la respiration devient la fin de E, le finish devient une section mental en do à 168.

| Section | Tempo (BPM) | Durée | Rôle |
| --- | --- | --- | --- |
| Half-time / dubstep | 160 (ressenti 80) | 10-15 min | Ouverture lourde et lente |
| Drum and bass | 165 | 15-20 min | Ça s'ouvre, vers la jungle et les rollers |
| Groove tribe | 143 → 152 | 10-15 min | Retombée sur le groove kick-sub en la# (kick glissant, stab à la tierce, charley), trois tracks, puis montée par paliers de 2 BPM |
| Acid | 152 → 162 | 10-15 min | Palier de la montée : l'acid entre en la#, percs ; toujours kick-sub, pas de rumble ; paliers de 2 BPM jusqu'à 162 |
| Tribe | 162 | 20-25 min | Cœur du set, le rumble entre avec la banque, couleur phrygienne ; fin en respiration (tension sans kick, triton) |
| Mental | 168 | 15-20 min | Tension hypnotique en do, sans saturation massive ; fin du set |

l'intro peut durer longtemps avec que de la bass et des voies lancinantes. Puis le coeur battant .
on peut ensuite amener des kick lourds et distordus. Une simple ligne de basse avec des harmoniques accélérés et c'est pas mal. un delay profond qui larcene les voies

- **Half-time → DnB** : même tempo, on change seulement la rythmique de batterie (kick sur 1, snare sur 3 → breakbeat full-time).
- **DnB → groove** : sous une note tenue, pas sous un break. Dernier pattern DnB hybride à 165 : breakbeat muté, stab do# puis kick la# déjà entrés dans la gamme de fa phrygien (ils en sont la sixte bémol et la quarte), kick et sub de la DnB coupés, note tenue, tempo descendu à 143 d'un coup pendant la tenue (rien de séquencé ne l'entend), puis le kick glissant se pose seul en la#, stab sur les contretemps, charley en croches.
- **Groove → acid → tribe** : la montée se fait en deux banques, pas dans la banque tribe (réglée pour 162 : kick à rumble, ducking à la croche). Le battement du groove est acoustique et son stab fait 150 ms quel que soit le tempo. Groove : 152 − 143 = 9 BPM, paliers de 2 (145, 147, 149, 151, puis 152), un toutes les 32 mesures (1,6 s la mesure à 150 BPM, donc 51 s par palier), environ 4 minutes. À 152 l'acid entre en la#, même gamme, avec les percs : banque D, toujours kick-sub, le stab tient. Acid : 162 − 152 = 10 BPM, 5 paliers de 2, environ 4 minutes (1,5 s la mesure à 157 BPM, 48 s par palier). À 162 le rumble entre avec la banque E : l'architecture passe de kick-sub à kick + rumble à ce moment-là, une seule à la fois (KT23), et le battement du stab cesse.
- **Tempo** : on le monte à la main par petites touches pendant les breaks, +1 à 2 BPM à la fois. À l'intérieur d'une section, on y touche le moins possible ; la montée C → D → E est le seul passage où il bouge en continu.

## Progression harmonique

Une tonique stable par section, et on monte pour relancer : fa → la# → do. Fa → la# est une quarte ascendante (fa est la quinte de la#), la# → do un ton. Le la# est fixé par le groove (testé, c'est là qu'il sonne) ; les autres tonalités ont été recalées autour de lui le 2026-11-04. L'harmonie passe par la fondamentale (sub, kick accordée, acid), pas par des accords.

| Section | Tonalité | Couleur | Sub (octave 1) |
| --- | --- | --- | --- |
| Half-time | Fa mineur | Basse lente, peu de notes | \~44 Hz |
| Drum and bass | Fa phrygien | Ajout de sol bémol, reese fa/sol bémol | \~44 Hz |
| Groove tribe | La# mineur | Kick glissant posé sur la#, stab de sub à la tierce mineure (do#), charley | \~58 Hz |
| Acid | La# mineur | Acid en la#, kick-sub en la#, pas de rumble | \~58 Hz |
| Tribe | La# phrygien | Rumble en la#, kick accordée en la#, do bémol frotté ; fin en respiration : drone sur la#, triton (mi) | \~58 Hz |
| Mental | Do mineur | Drone et acid en do, kick sèche ; le kick à 65 Hz est en haut de la zone 40-65 Hz de KT5 (do 1 à 32,7 Hz sort sous l'accord des caissons) | \~65 Hz (do 2) |

**Notes par section** (notation anglaise : F = fa, G = sol, A = la, ♭ = bémol)

Le mode donne les notes jouables ; la hauteur décide qui a le droit de les
jouer (KT5 [[kb/theorie/kt-tonalite-du-grave]], [[doctrine]] §11) : sous
120 Hz la tonique seule, la quinte étant la seule autre note stable du grave ;
la tierce et la seconde vivent au-dessus. `KB SCALE` et `ROOT NOTE` se
règlent par track (9, 10, 12, 13) dans KEYBOARD SETUP, `KB FOLD` ON, et sont
sauvés dans le pattern ([[kb/keyboard-gammes]]) : chaque banque porte sa gamme.

| Section | KB SCALE, ROOT NOTE | Notes de la gamme | Kick 1, rumble / sub 2 | Basse 9 (80-250 Hz) | Acid 10, Id, voix : couleur du mode |
| --- | --- | --- | --- | --- | --- |
| Half-time | AEOLIAN (MINOR), F | F G A♭ B♭ C D♭ E♭ | F1 seul (43,7 Hz) | F2, C (quinte), F3 ; E♭ (♭7) en note de passage | A♭ et D♭ (♭3, ♭6), peu de notes, lentes |
| Drum and bass | PHRYGIAN, F | F G♭ A♭ B♭ C D♭ E♭ | F1 seul (43,7 Hz) | F2, C ; reese F / G♭ au-dessus de 80 Hz | G♭ (♭2) frottée contre F : c'est la note phrygienne |
| Groove tribe | AEOLIAN (MINOR), A# | B♭ C D♭ E♭ F G♭ A♭ | B♭1 seul (58,3 Hz), kick glissant à queue longue | stab D♭2 (71,8 Hz) sur les contretemps : la **tierce mineure dans le sub**, écart assumé à KT5 et au §11 de [[doctrine]], c'est le battement (~13 Hz) qui fait le roulement | rien d'autre : trois tracks (1, 9, 6) |
| Acid | AEOLIAN (MINOR), A# | B♭ C D♭ E♭ F G♭ A♭ | B♭1 seul (58,3 Hz), kick-sub | B♭2, F (quinte), B♭3 ; A♭ (♭7) en passage | D♭ et G♭ (♭3, ♭6) ; acid en B♭ |
| Tribe | PHRYGIAN, A# | B♭ C♭ D♭ E♭ F G♭ A♭ | B♭1 seul (58,3 Hz) ; en fin, ou rien, kick coupée | B♭2, F ; en fin, drone sur B♭ | C♭ = B (♭2) frottée ; le triton E de la fin est **hors gamme** : trig en `NOTE` chromatique (`NOTE PARAM` CHRO) ou lock, pas au clavier replié |
| Mental | AEOLIAN (MINOR), C | C D E♭ F G A♭ B♭ | C2 seul (65,4 Hz) | C3, G (quinte) ; B♭ (♭7) en passage | E♭ et A♭ (♭3, ♭6) ; drone et acid en C |

- Fréquences depuis A1 = 440 / 8 = 55,0 Hz : F1 = 55 × 2^(-4/12) = 43,7 Hz,
  B♭1 = 55 × 2^(1/12) = 58,3 Hz, C2 = 55 × 2^(3/12) = 65,4 Hz ; l'octave
  au-dessus double (F2 87,3, B♭2 116,5, C3 130,8 Hz), c'est la zone de la
  basse 9. Période d'un cycle du sub (1000 / f) : F1 22,9 ms, B♭1 17,2 ms,
  C2 15,3 ms ; un kick de 364 ms en F contient 364 / 22,9 = 16 cycles, un
  kickbass de 328 ms en C2 en contient 21, une queue de 80 ms n'en a que 3
  ou 4, trop peu pour entendre la note (KT5 : c'est alors la basse qui la
  donne).
- La tierce de la section (A♭, D♭, E♭) et la seconde phrygienne (G♭, C♭) ne
  descendent jamais dans le sub : elles brouillent le grave (KT5, exercice 2).
  Jouées une octave plus haut, elles redeviennent lisibles. **Une seule
  exception, voulue** : le stab D♭2 du groove, tierce mineure de B♭1 posée
  dans le sub sur les contretemps ; le battement à ~13 Hz entre la queue du
  kick et le stab est précisément le roulement du groove
  ([[kb/tutos/maison-groove-tribe-battement]]). Il cesse quand le rumble
  entre.
- Les pivots en degrés : B♭ et D♭ = quarte et sixte bémol de F phrygien,
  tonique et tierce de B♭ mineur (tout le groove est contenu dans la gamme
  de la DnB) ; F = quinte de B♭ et quarte de C, et tonique de l'ouverture.
  Les deux gammes voisines contiennent la note pivot, le drone peut la tenir
  pendant le changement sans sortir d'aucune des deux.
- Samples acid : enregistrer une série par tonalité (F, B♭, C). Les anciens
  samples en F demanderaient +5 et +7 demi-tons, trop pour une boucle
  découpée et de quoi changer le caractère du filtre sur une note isolée ;
  le +2 / +4 de l'ancienne progression F → G → A ne vaut plus.

**Durées au tempo de chaque section** (temps = 60 / BPM, croche = temps / 2,
double-croche = temps / 4, mesure = 4 temps ; pour une fourchette de tempo,
les deux bornes)

| Section | BPM | Temps | Croche | Double-croche | Mesure | Repères |
| --- | --- | --- | --- | --- | --- | --- |
| Half-time | 160 | 375 ms | 187,5 ms | 93,8 ms | 1 500 ms | kick lourde jusqu'à un temps (375 ms), snare sur le 3 ; ressenti 80 BPM, le « temps » perçu fait 750 ms |
| Drum and bass | 165 | 363,6 ms | 181,8 ms | 90,9 ms | 1 455 ms | reese tenue 1 à 2 mesures ; break découpé à la double-croche |
| Groove tribe | 143 / 152 | 419,6 / 394,7 ms | 209,8 / 197,4 ms | 104,9 / 98,7 ms | 1 678 / 1 579 ms | stab ~150 ms sur 3, 7, 11, 15, retombé avant le kick suivant ; kick glissant à queue longue qui tient le sub ; palier de +2 BPM toutes les 32 mesures |
| Acid | 152 / 162 | 394,7 / 370,4 ms | 197,4 / 185,2 ms | 98,7 / 92,6 ms | 1 579 / 1 481 ms | mesures acid enregistrées à 152, découpées en 16 slices pour suivre les paliers ; enveloppe d'amplitude à resserrer en montant |
| Tribe | 162 | 370,4 ms | 185,2 ms | 92,6 ms | 1 481 ms | kick à rumble 130-200 ms, release du ducking une croche, basse 9 en contretemps decay 120-200 ms ; en fin, drone sans mesure, delay sur la croche pointée (3 × 92,6 = 278 ms) ou la noire |
| Mental | 168 | 357,1 ms | 178,6 ms | 89,3 ms | 1 429 ms | delay sur la croche pointée (3 × 89,3 = 268 ms) ; un kickbass éventuel au plus un temps moins 15 ms (357 − 15 = 342 ms), au-delà la queue mange le kick suivant |

**Pivots (notes communes pour changer de tonalité)**

- **Fa → la#** (DnB → groove) : si bémol et ré bémol, les deux notes du groove, déjà dans fa phrygien. Stab do# puis kick la# entrent sous la DnB, kick et sub de fa coupés, note tenue, tempo à 143, le kick glissant se pose en la#.
- **La# → do** (fin de E → F) : fa, quinte de la# et quarte de do, la note qui ouvre le set. Fa tenue pendant la respiration, filtre et résonance qui montent, silence d'un temps ou d'une mesure, puis retombée en do.

**Accordage sur la Digitakt**

- Kicks et rumble accordés sur la tonique de la section (fa, la#, do), un sample par tonalité, jamais repitché de plus de deux ou trois demi-tons ([[doctrine]] §11) ; le kick glissant du groove est un sample à part, en la#.
- Samples acid enregistrés dans chaque tonalité (fa, la#, do), pas transposés.

## Organisation de la Digitakt 2

Sept banques dans un seul projet : une par section, dans l'ordre de jeu A → F, plus G pour les jokers (H libre). Même disposition de pistes partout, pour que les mutes et la Control All tombent toujours au même endroit. Réorganisation des banques décidée le 2026-11-04, plan révisé le 2026-11-06 (D Acid, E Tribe, F Mental) et reporté le même jour dans `library/lives/solaris.json` ; reste le +Drive.

**Disposition des pistes (identique dans tous les patterns)** : la grille 16 tracks de [[doctrine]] §1 fait foi (1 kick, 2 rumble / sub, 3 clap / snare, 4 ride, 5-6 hats, 7-8 percs, 9 basse, 10 lead / acid, 11 atmo / drone, 12 vocal, 13-14 Id1 / Id2, 15 FX, 16 réserve).

**Banques**

| Banque | Section | Patterns | Contenu clé |
| --- | --- | --- | --- |
| A | Half-time, 160, fa | 6-8 | Intro drone seul, beat half-time, variations, montée, bascule full-time (même kit) |
| B | DnB, 165, fa phrygien | 8-10 | Breaks découpés, reese fa/sol bémol, variations de plus en plus sales ; dernier pattern hybride avec kick régulière |
| C | Groove tribe, 143 → 152, la# | 4-6 | Groove nu (kick glissant la#, stab do#, charley), variantes, paliers de tempo ; kit propre, sans rumble |
| D | Acid, 152 → 162, la# | 6-8 | L'acid entre (notes de 303 et mesures en la#), percs ; kick-sub, pas de rumble ; paliers de tempo, dernier pattern où le rumble s'annonce |
| E | Tribe, 162, la# phrygien | 10-14 | Rumble, percs tribales, rolls, triolets, do bémol ; derniers patterns en respiration : kick allégée ou coupée, drone la#, acid filtrée, triton mi, montée sur fa + silence |
| F | Mental, 168, do | 8-10 | Tension hypnotique : kick en do (do 2), sub propre, drone et acid en do, résonance qui monte, sans saturation massive ; vrai pattern de fin |
| G | Jokers et secours | 8-12 | Un break par section, « kick + sub seuls » en fa, la# et do, variations en réserve |

**Samples à préparer**

- Kicks accordées en fa, la# et do, en versions propre et saturée (famille par tonalité, lot 4 de [[kb/tutos/_index]] dans Live) ; le kick glissant du groove en la#, à part
- Rumbles accordés en la# et do (et éventuellement un kick + rumble fusionné en do pour le finish)
- Sub : une sinusoïde ou un reese, transposé par p-lock ; le stab de sub du groove en do#
- Notes de 303 (normale, accent, slide) et mesures acid, enregistrées en fa, la# et do
- Drones et nappes sur fa, la# et do
- Snares, claps, hats, percs tribales, toms
- Breaks à découper
- FX : impacts, montées de bruit, voix ou ambiances

Tout doit tenir dans la mémoire sample d'un seul projet : surveille-la au fur et à mesure.

### Arborescence des samples sur le +Drive

Un dossier par banque, à plat (SPEC 7.L5) : une banque de patterns = une banque RAM de la DT2 (127 slots) = un dossier, que l'on sélectionne et charge d'un coup dans sa banque RAM (`[FUNC] + [YES]` au chargement). Pas de sous-dossier par branche ni par code : le préfixe du nom regroupe les fichiers au tri alphabétique. Un sample n'est que dans une banque.

Le kit par défaut `0-KIT` tient 16 samples, un par track de la grille de [[doctrine]] §1, numérotés par track. Chargé en premier dans la banque RAM A, il occupe les slots A01 à A16, ceux sur lesquels pointe tout pattern vide : c'est la couleur de départ du live. Il a sa propre tonalité (celle de la banque qui ouvre le set, fa pour solaris) ; un pattern d'une autre banque corrige par le TUNE de la track ou un sample lock vers un son de sa banque.

```
00-live/solaris/
├── 0-KIT/      01 BD F Hard 01 slr · 02 RM F Roll 01 slr · 03 SD Tribe 01 slr · 04 PC… · 05 BR 170 Think slr · 06 HH… · 07 OH… · 08 CY Ride slr · 09 BS F Sine slr · 10 ST… · 11 PD F Drone slr · 12 VX… · 13 BL 168 AcidF1 slr · 14 ML… · 15 FX Rise 01 slr · 16 FX Impact 01 slr
├── A-HALF/     BD F Kick 03 rth · BS F Wrap 01 bas · CP… HH… PC… SD… · DL 140 Dubs 02 rth · FX… VX…
├── B-DNB/      BD F Kicks rth · BR 160 Amen 01 slr · BR 170 Think 01 slr · BS F Reese 01 slr · HH… PC… SD… · FX…
├── C-GROOVE/   BD A# Glide 01 slr · BS C# Stab 01 slr · HH Tribe 01 … (trois tracks, kit court)
├── D-ACID/     BS A# 303 Acc slr · BS A# 303 Sld slr · BL 152 AcidA#1 slr · PC… HH…
├── E-TRIBE/    BD A# Box 01 … · RM A# Box 01 … · PD A# Drone … · CY… HH… OH… PC… SD… · FX… VX…
├── F-MENTAL/   BD C … · RM C … · BL 168 AcidC1 slr · PD C Drone … · HH… SD… · FX… VX…
└── G-JOKER/    BD Tool 01 rth · SD Snares 01 909 · HH Clean 04 909 · FX… (ex 0-COMMON)
```

Les noms ci-dessus sont la cible. Migration du 2026-11-06 dans
`library/lives/solaris.json` : les kicks, rumbles et basses en sol et en la
des anciennes banques C-TRIBE, D-RESPI et E-SATURE sont sortis du live
(restés dans la lib), à refaire en la# et do ; leurs samples non accordés
sont passés en E-TRIBE (ex C-TRIBE) et F-MENTAL (ex D-RESPI et E-SATURE),
F-JOKER est devenu G-JOKER ; C-GROOVE et D-ACID sont vides.
Chargement d'un projet neuf : `0-KIT` dans la banque RAM A, puis `A-HALF` à
la suite dans A, `B-DNB` dans B, et ainsi de suite jusqu'à G. Plafond de
127 fichiers par banque (l'ancienne C-TRIBE était à 129 : le groove dans sa
propre banque évite d'y ajouter).

- **Noms** : nomenclature SPEC 7.J8, `<CODE> [BPM|note] <desc> <pack>`, 18 caractères max, code toujours en tête.
- **Note dans le nom** pour kicks, rumbles, sub et drones, pour retrouver d'un coup d'œil le fa, le sol ou le la.
- **Acid** : notes de 303 isolées en BS (TONAL), mesures en BL (LOOPS) avec le BPM en tête.
- **Pack `slr`** pour les enregistrements et resamplings du set ; les samples de la lib gardent leur pack d'origine.
- **RM** : rumbles passés par override, l'outil ne les déduit jamais du nom.
- **Plafond propre au live** : 64 fichiers par dossier (la lib plafonne à 16, 32 pour BR / DL / PL). Préparation des lives dans l'outil : SPEC « Décisions 7.L ».

## Kits, pattern maître et presets

Un pattern maître par section sert de kit : un jeu équilibré de samples réglés, dont on tire toutes les variations par copie.

1. Construire le pattern maître de la section : samples, niveaux, accordage, filtre, enveloppes, dans la disposition fixe des pistes.
2. Le sauvegarder comme kit si le firmware le permet. Sinon, le pattern maître lui-même joue ce rôle.
3. Le copier pour chaque variation, et ne changer que les trigs, les p-locks et les fills.
4. Si un son est amélioré en cours de route : le sauvegarder en preset, puis le recharger dans les autres patterns de la section.

**Presets indépendants** pour les sons qui doivent rester identiques ou qui sont transposés d'une section à l'autre : kicks, rumbles, sub, acid, drones. Pas besoin de preset pour chaque hat ou perc : le kit suffit.

**Effets** : les réglages des effets globaux (delay, reverb) restent à part. Les envois de chaque piste sont réglés dans le kit à des valeurs de base (souvent zéro, un peu de reverb sur percs et drone), pour qu'un changement de pattern ne coupe pas ou ne fasse pas exploser un effet.

**Attention en live** : un changement de pattern recharge les réglages enregistrés. Un filtre ouvert à la main peut se refermer d'un coup. Soit on ramène ses réglages avant de changer, soit on place ce saut sur une coupure ou un drop.

## Jeu live : enchaînements et fills

Tout s'enchaîne à la main, pas en mode song, pour pouvoir rallonger, raccourcir ou sauter sur un joker selon la foule.

**Enchaîner**

- Changements en file d'attente : le pattern suivant démarre à la fin du pattern en cours. Longueurs de 1 à 4 mesures pour pouvoir réagir vite.
- Chaînes courtes à l'intérieur d'une section (par exemple C1 → C2 → C3) pour garder les mains libres sur filtres et mutes.
- Mutes et fills avant de changer de pattern : souvent, ça suffit à créer le mouvement.
- Mode song seulement pour répéter (vérifier la durée globale), ou pour une transition très écrite. Celle-ci peut aussi tenir dans un seul pattern long.

**Fills : le principe**

- Trig **FILL** : ne joue qu'en mode fill (rolls, coupures, variations).
- Trig **!FILL** : disparaît en mode fill. À mettre sur kick ou sub des derniers pas pour créer un trou avant la retombée.
- Fill concentré sur les 4 à 8 derniers pas, avec retrig qui accélère, pitch qui monte, filtre qui s'ouvre, ou silence.
- Conditions en plus pour varier sans rien toucher : probabilité, 1:2, 1:4, 1ST.
- Raccourci du mode fill (maintenu ou verrouillé) à vérifier dans le manuel du firmware, et à travailler sans regarder.

**Un fill dans presque tous les patterns**

| Type de pattern | Fill |
| --- | --- |
| Boucle (on y reste longtemps) | Léger : variation de hats ou percs, petit roll |
| Sortie (avant un changement) | Fort : roll, coupure, montée |
| Respiration | Aucun, ou une montée de filtre |

2 ou 3 types de fills par section (un roll, un trou, une montée), répartis entre les patterns. Ne pas en abuser en live : un fill toutes les 2 mesures fatigue vite.

**Fills par section**

- **Half-time** : roll de snare, sub coupé sur la dernière mesure
- **DnB** : slices de break réarrangées ou pitchées, reese qui monte
- **Groove** : presque rien, c'est une boucle longue ; un trou de stab (trig !FILL sur la 9) ou un charley qui double, et le palier de tempo tient lieu de relance
- **Acid** : cutoff et résonance de l'acid qui s'ouvrent, accents ; le palier de tempo relance
- **Tribe** : rolls de kick et de toms, hats en triolets ; en fin de banque (respiration), montées de drone et de résonance
- **Mental** : montées de résonance, trous de kick (!FILL), drone qui monte ; dernier pattern = fin

**Monter l'énergie sans accélérer** : doubles kicks, hats en triolets, résonance de l'acid qui s'ouvre, patterns raccourcis (16 → 8 → 4 pas) avant un drop.

## Rumble, sub et acid

**Rumble** : sur sa propre piste dans les sections tribe, pour pouvoir le muter, le filtrer et l'accorder en live.

- Il démarre juste après l'attaque de la kick (attaque d'enveloppe douce ou léger décalage du début du sample) : effet de pompage sans sidechain.
- Il est accordé sur la même note que la kick.
- Dans les patterns avec rumble, le sub est coupé ou allégé, car ils occupent la même zone.
- Option pour F : un sample kick + rumble fusionné en do, compact et en phase, qui libère une piste.

**Sub** : propre et sans distorsion, même sous une kick très saturée. Sinon le bas du spectre devient flou sur un gros système son.

**Acid samplée** : deux méthodes, toutes deux suivent le tempo.

- **Mesures découpées** : une mesure enregistrée au tempo de sa section, découpée en 16 slices rejouées pas à pas.
- **Notes isolées** : notes de 303 (normale, accent, slide) rejouées par p-locks de pitch, avec filtre et résonance de la piste. Plus long à préparer, plus vivant.
- À tempo élevé, régler l'enveloppe d'amplitude pour éviter clics et chevauchements de slices.
- L'acid monte bien en intensité avec un overdrive poussé : à garder pour les pics du tribe (E), le mental (F) restant sans saturation massive.

## Checklist de préparation

- [ ] Samples préparés et rangés par section (voir la liste plus haut)
- [ ] Presets sauvegardés : kicks, rumbles, sub, acid, drones
- [ ] Pattern maître de chaque section (A à F)
- [ ] Variations et fills de la banque A
- [ ] Variations et fills de la banque B
- [ ] Banque C : groove nu en la#, variantes, paliers 143 → 152
- [ ] Banque D : entrée de l'acid en la#, paliers 152 → 162, dernier pattern où le rumble s'annonce
- [ ] Variations et fills de la banque E, avec la respiration et la montée finale sur fa
- [ ] Variations et fills de la banque F, avec le pattern de fin
- [ ] Banque G : breaks, « kick + sub seuls » en fa, la# et do, réserves
- [x] `solaris.json` réaligné sur les banques A à G et les tonalités fa, la#, do (2026-11-06)
- [ ] +Drive réaligné
- [ ] Transitions travaillées : half-time → DnB, DnB → groove (note tenue, tempo à 143), groove → acid (montée, entrée de l'acid), acid → tribe (entrée du rumble), fin de E → F (fa, retombée en do)
- [ ] Raccourci du mode fill maîtrisé sans regarder
- [ ] Une répétition complète enregistrée, durée et transitions vérifiées
- [ ] Projet sauvegardé sur ordinateur, au moins deux copies
- [ ] Fiche papier : [[solaris-pense-bete-p1.svg]] et [[solaris-pense-bete-p2.svg]] (deux pages A4 paysage en couleur, produites par `scripts/solaris_pense_bete.py`, dont les tableaux recopient cette doctrine ; à régénérer et réimprimer à chaque changement de tableau)
