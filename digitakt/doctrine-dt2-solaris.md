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
    B-FLATIRON:
      title: Flatiron
      desc: Half-time, ouverture lourde et lente
      tempo: 160
      tonique: F
      mode: mineur-harmonique
    C-DAVYL:
      title: Davyl
      desc: Techno, kick glissant la#, stab à la tierce, charley
      tempo: 142
      tonique: A#
      mode: eolien
    D-AVIRUS:
      title: A Virus
      desc: Acid en la# phrygien
      tempo: 154
      tonique: A#
      mode: phrygien
    E-NEPTUNE:
      title: Neptune
      desc: Tribe percussive et bruitée, retour en fa
      tempo: 160
      tonique: F
      mode: mineur-harmonique
    F-OMINOUS:
      title: Ominous
      desc: Drum and bass à gros kick régulier, fin du set
      tempo: 170
      tonique: F
      mode: phrygien
---

# Live Digitakt 2 — doctrine free party

Oct 13, 2026 · @tom

## Plan du set, révisé le 2026-11-26 (fait foi)

Cinq banques nommées, jouées dans l'ordre B → F, tempos fixes : le saut de tempo se fait d'un coup au changement de banque, plus de paliers. La banque A reste vide, pour que les cinq banques soient contiguës. Mental et Jokers sortent du set ; le groove tribe s'appelle désormais techno, sa musique ne change pas ; la DnB, à gros kick régulier typé tribe, ferme le set.

| Banque | Nom | Genre | Tempo (BPM) | Tonalité | KB SCALE, ROOT NOTE | Notes de la gamme | Kick et sub |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B | FLATIRON | Half-time | 160 (ressenti 80) | Fa mineur harmonique | HARMONIC MINOR, F *(nom à vérifier sur la machine)* | F G A♭ B♭ C D♭ E | F1 (43,7 Hz) |
| C | DAVYL | Techno (ex groove tribe) | 142 | La# (si♭) éolien | AEOLIAN (MINOR), A# | B♭ C D♭ E♭ F G♭ A♭ | B♭1 (58,3 Hz) |
| D | A VIRUS | Acid | 154 | La# (si♭) phrygien | PHRYGIAN, A# | B♭ C♭ D♭ E♭ F G♭ A♭ | B♭1 (58,3 Hz) |
| E | NEPTUNE | Tribe | 160 | Fa mineur harmonique | HARMONIC MINOR, F *(idem)* | F G A♭ B♭ C D♭ E | F1 (43,7 Hz) |
| F | OMINOUS | Drum and bass | 170 | Fa phrygien | PHRYGIAN, F | F G♭ A♭ B♭ C D♭ E♭ | F1 (43,7 Hz) |

- **Tempo** : 160 → 142 → 154 → 160 → 170, soit − 18 (142 − 160), + 12 (154 − 142), + 6 (160 − 154), + 10 (170 − 160). Après la retombée de l'ouverture il ne fait que monter, et 170, plafond du set, arrive à la fin. Au ressenti il monte d'un bout à l'autre : le half-time à 160 se ressent à 80, puis 142, 154, 160, 170.
- **Tonalités** : fa (B) → la# (C, D) → fa (E, F). Une quarte au-dessus au milieu du set, puis retour à la tonique d'ouverture ; fa est la quinte de la#. Le mineur harmonique diffère de l'éolien par sa septième : mi naturel au lieu de mi bémol.
- **Pivot B → C** : si bémol et ré bémol sont dans fa mineur harmonique, le stab et le kick en la# peuvent entrer sous le half-time. Le mi naturel est à éviter pendant le passage : c'est le triton de la#.
- **Fin E → F** : même tonique, le kick et le sub en fa de la tribe tiennent pendant que la DnB entre ; deux notes bougent (sol → sol bémol, mi → mi bémol).
- **Identifiants** (dossiers du +Drive, `library/lives/solaris.json`, projet mk-brain) : `B-FLATIRON`, `C-DAVYL`, `D-AVIRUS`, `E-NEPTUNE`, `F-OMINOUS`. Migration du 2026-11-26 : les 76 samples de `A-HALF` vont en `B-FLATIRON`, les 78 de `B-DNB` en `F-OMINOUS`, les 74 de `D-TRIBE` suivent la tribe en `E-NEPTUNE` (aucun sample accordable parmi eux, donc aucun réaccordage), `C-DAVYL` et `D-AVIRUS` sont vides, les 37 samples de `F-MENTAL` et les 23 de `G-JOKER` sont retirés du live (37 + 23 = 60 ; 304 − 60 = 244 restants, kit compris).
- **Sur la DT2** : deux banques de patterns à déplacer, dans cet ordre : OMINOUS de B vers F, puis FLATIRON de A vers B.

**Durées au tempo de chaque banque** (temps = 60 000 / BPM, croche = temps / 2, double-croche = temps / 4, mesure = 4 temps)

| Banque | BPM | Temps | Croche | Double-croche | Mesure |
| --- | --- | --- | --- | --- | --- |
| B, E | 160 | 375,0 ms | 187,5 ms | 93,8 ms | 1 500 ms |
| C | 142 | 422,5 ms | 211,3 ms | 105,6 ms | 1 690 ms |
| D | 154 | 389,6 ms | 194,8 ms | 97,4 ms | 1 558 ms |
| F | 170 | 352,9 ms | 176,5 ms | 88,2 ms | 1 412 ms |

## Structure du set

Un live de 1h05 à 1h30 en cinq banques à tempo fixe. Le tempo ne bouge plus à l'intérieur d'une banque : il retombe une fois, de 160 à 142 après l'ouverture, puis remonte de banque en banque jusqu'à 170. À l'intérieur d'une banque l'énergie monte par la densité, la saturation et la couleur du mode, pas par le tempo. Le la# de la techno est fixé par son groove ([[kb/tutos/maison-groove-tribe-battement]], testé le 2026-11-04 : c'est en la# que ça sonne ; le tuto est réglé à 143, la banque joue à 142).

| Banque | Section | Durée | Rôle |
| --- | --- | --- | --- |
| B Flatiron | Half-time / dubstep | 10-15 min | Ouverture lourde et lente |
| C Davyl | Techno | 10-15 min | Retombée sur le groove kick-sub en la# (kick glissant, stab à la tierce, charley), trois tracks |
| D A Virus | Acid | 20-25 min | Cœur du set : l'acid entre en la# phrygien ; fin en respiration (tension sans kick, triton) |
| E Neptune | Tribe | 10-15 min | Tribe percussive et bruitée, retour en fa, kickbass à longue queue |
| F Ominous | Drum and bass | 15-20 min | Gros kick régulier typé tribe sous les breaks ; fin du set |

Durées reprises de l'ancien plan en suivant le genre : 10 + 10 + 20 + 10 + 15 = 65 min au plus court, 15 + 15 + 25 + 15 + 20 = 90 min au plus long. Tempos et tonalités : tableau du plan, en tête.

l'intro peut durer longtemps avec que de la bass et des voies lancinantes. Puis le coeur battant .
on peut ensuite amener des kick lourds et distordus. Une simple ligne de basse avec des harmoniques accélérés et c'est pas mal. un delay profond qui larcene les voies

- **B → C, half-time → techno** : sous une note tenue, pas sous un break. Dernier pattern half-time à 160 : batterie mutée, stab do# puis kick la# déjà entrés dans la gamme de fa mineur harmonique (ils en sont la sixte bémol et la quarte), kick et sub de fa coupés, note tenue (pas le mi, triton de la#), tempo descendu à 142 d'un coup pendant la tenue (rien de séquencé ne l'entend), puis le kick glissant se pose seul en la#, stab sur les contretemps, charley en croches.
- **C → D, techno → acid** : même tonique, le kick en la# reste. Le saut de 142 à 154 se place sur une coupure ou une tenue ; la gamme passe de la# éolien à la# phrygien (le do devient do bémol) et l'acid entre.
- **D → E, acid → tribe** : par la respiration de la fin de D : kick allégée ou coupée, drone sur la#, acid filtrée, triton mi, fa tenue (quinte de la#), silence d'un temps ou d'une mesure, puis retombée en fa à 160 avec le kickbass à longue queue. Le mi, triton de la#, est aussi la sensible de fa : la tension de la respiration se résout sur la tonique de la tribe.
- **E → F, tribe → DnB** : même tonique, le kick et le sub en fa tiennent pendant que les breaks entrent ; le gros kick régulier de la DnB prolonge celui de la tribe. Deux notes bougent (sol → sol bémol, mi → mi bémol).
- **Tempo** : fixe dans une banque, on n'y touche pas. Les quatre sauts (− 18, + 12, + 6, + 10) se font d'un coup au changement de banque, sur une tenue, une coupure ou un drop.

## Progression harmonique

Une tonique stable par banque : fa → la# → fa. Fa → la# est une quarte ascendante (fa est la quinte de la#) ; le retour en fa se fait à la tribe et tient jusqu'à la fin. Le la# est fixé par le groove de la techno (testé, c'est là qu'il sonne). L'harmonie passe par la fondamentale (sub, kick accordée, acid), pas par des accords.

**Qui joue quelles notes** (notation anglaise : F = fa, G = sol, A = la, ♭ = bémol ; `KB SCALE`, `ROOT NOTE` et notes de chaque gamme : tableau du plan)

Le mode donne les notes jouables ; la hauteur décide qui a le droit de les
jouer (KT5 [[kb/theorie/kt-tonalite-du-grave]], [[doctrine]] §11) : sous
120 Hz la tonique seule, la quinte étant la seule autre note stable du grave ;
la tierce et la seconde vivent au-dessus. `KB SCALE` et `ROOT NOTE` se
règlent par track (9, 10, 12, 13) dans KEYBOARD SETUP, `KB FOLD` ON, et sont
sauvés dans le pattern ([[kb/keyboard-gammes]]) : chaque banque porte sa gamme.

| Banque | Kick 1, rumble / sub 2 | Basse 9 (80-250 Hz) | Acid 10, Id, voix : couleur du mode |
| --- | --- | --- | --- |
| B Flatiron, half-time | F1 seul (43,7 Hz) | F2, C (quinte), F3 ; E (sensible) en note de passage vers F | A♭ et D♭ (♭3, ♭6), peu de notes, lentes ; la seconde augmentée D♭ – E est la couleur du mineur harmonique |
| C Davyl, techno | B♭1 seul (58,3 Hz), kick glissant à queue longue | stab D♭2 (71,8 Hz) sur les contretemps : la **tierce mineure dans le sub**, écart assumé à KT5 et au §11 de [[doctrine]], c'est le battement (~13 Hz) qui fait le roulement | rien d'autre : trois tracks (1, 9, 6) |
| D A Virus, acid | B♭1 seul (58,3 Hz) ; en fin, ou rien, kick coupée | B♭2, F (quinte), B♭3 ; A♭ (♭7) en passage ; en fin, drone sur B♭ | acid en B♭ ; C♭ = B (♭2) frottée contre B♭, D♭ et G♭ (♭3, ♭6) ; le triton E de la fin est **hors gamme** : trig en `NOTE` chromatique (`NOTE PARAM` CHRO) ou lock, pas au clavier replié |
| E Neptune, tribe | F1 seul (43,7 Hz), kickbass à longue queue | F2, C (quinte) | percs bruitées ; D♭ (♭6) et E (sensible) |
| F Ominous, DnB | F1 seul (43,7 Hz) | F2, C ; reese F / G♭ au-dessus de 80 Hz | G♭ (♭2) frottée contre F : c'est la note phrygienne |

- Fréquences depuis A1 = 440 / 8 = 55,0 Hz : F1 = 55 × 2^(-4/12) = 43,7 Hz,
  B♭1 = 55 × 2^(1/12) = 58,3 Hz ; l'octave au-dessus double (F2 87,3,
  B♭2 116,5 Hz), c'est la zone de la basse 9. Période d'un cycle du sub
  (1000 / f) : F1 22,9 ms, B♭1 17,2 ms ; un kick de 364 ms en F contient
  364 / 22,9 = 16 cycles, le même en B♭ 364 / 17,2 = 21, une queue de 80 ms
  n'en a que 3 ou 4, trop peu pour entendre la note (KT5 : c'est alors la
  basse qui la donne).
- La tierce (A♭, D♭) et la seconde phrygienne (G♭, C♭) ne descendent jamais
  dans le sub : elles brouillent le grave (KT5, exercice 2). Jouées une
  octave plus haut, elles redeviennent lisibles. **Une seule exception,
  voulue** : le stab D♭2 de la techno, tierce mineure de B♭1 posée dans le
  sub sur les contretemps ; le battement à ~13 Hz entre la queue du kick et
  le stab est précisément le roulement du groove
  ([[kb/tutos/maison-groove-tribe-battement]]). C'est la signature de la
  banque C ; ré bémol est aussi dans la# phrygien, le garder ou non sous
  l'acid en D se décide à l'oreille.
- Les pivots en degrés : B♭ et D♭ = quarte et sixte bémol de F mineur
  harmonique, tonique et tierce de B♭ mineur (tout le groove de la techno
  est contenu dans la gamme du half-time) ; F = quinte de B♭ et tonique de
  l'ouverture comme de la fin. Les deux gammes voisines contiennent la note
  pivot, le drone peut la tenir pendant le changement sans sortir d'aucune
  des deux.
- Samples acid : enregistrer la série en la# (B♭), à 154. Les anciens
  samples en F demanderaient +5 demi-tons, trop pour une boucle découpée et
  de quoi changer le caractère du filtre sur une note isolée.

**Repères par banque** (durées du temps, de la croche et de la mesure : tableau du plan)

- **B Flatiron, 160** : kick lourde jusqu'à un temps (375 ms), snare sur le 3 ; ressenti 80 BPM, le « temps » perçu fait 2 × 375 = 750 ms.
- **C Davyl, 142** : stab ~150 ms sur 3, 7, 11, 15, retombé avant le kick suivant ; kick glissant à queue longue qui tient le sub.
- **D A Virus, 154** : mesures acid enregistrées à 154, découpées en 16 slices ; en fin, drone sans mesure, delay sur la croche pointée (3 × 97,4 = 292 ms) ou la noire (389,6 ms).
- **E Neptune, 160** : kickbass à longue queue, au plus un temps moins 15 ms, soit 375 − 15 = 360 ms, au-delà la queue mange le kick suivant ; basse 9 en contretemps, decay 120-200 ms.
- **F Ominous, 170** : reese tenue 1 à 2 mesures (1 412 à 2 824 ms) ; break découpé à la double-croche (88,2 ms).

**Pivots (notes communes pour changer de tonalité)**

- **Fa → la#** (B → C) : si bémol et ré bémol, les deux notes du groove, déjà dans fa mineur harmonique. Stab do# puis kick la# entrent sous le half-time, kick et sub de fa coupés, note tenue, tempo à 142, le kick glissant se pose en la#.
- **La# → fa** (fin de D → E) : fa, quinte de la# et tonique de la tribe, la note qui ouvre le set. Fa tenue pendant la respiration, filtre et résonance qui montent, silence d'un temps ou d'une mesure, puis retombée en fa. Notes communes à la# phrygien et fa mineur harmonique : si bémol, ré bémol, fa, la bémol.

**Accordage sur la Digitakt**

- Kicks et rumble accordés sur la tonique de la banque (fa ou la#), un sample par tonalité, jamais repitché de plus de deux ou trois demi-tons ([[doctrine]] §11) ; le kick glissant de la techno est un sample à part, en la#.
- Samples acid enregistrés en la#, pas transposés.

## Organisation de la Digitakt 2

Cinq banques de patterns dans un seul projet, une par section, dans l'ordre de jeu B → F ; A reste vide, G et H sont libres. Même disposition de pistes partout, pour que les mutes et la Control All tombent toujours au même endroit. Plan du 2026-11-26, reporté le même jour dans `library/lives/solaris.json` ; reste le +Drive.

**Disposition des pistes (identique dans tous les patterns)** : la grille 16 tracks de [[doctrine]] §1 fait foi (1 kick, 2 rumble / sub, 3 clap / snare, 4 perc, 5 hats, 6 cymbales, 7-8 Id1 appel / réponse, 9 basse, 10 séquence / acid, 11 atmo / drone, 12 vocal, 13-14 Id2 / Id3, 15 FX, 16 kick fantôme).

**Track 16, kick fantôme du sidechain** (décidé le 2026-11-26) : la réserve de la grille porte ici une copie du kick, retirée du main dans l'AUDIO ROUTING et mise en source du compresseur ([[doctrine]] §10). Le vrai kick (1) peut alors être muté ou passé en NOT FILL pendant un break sans arrêter le pompage. Ses trigs se posent sur la DT2 : avec l'AUTO CHANNEL sur le canal 16, la MK2 ne peut ni la sélectionner ni la muter (`mk-brain/SPEC.md`). La track 16 n'est donc plus disponible pour le Preset Pool dans ce set : le pool de FX vit sur la 15. *(À vérifier sur la machine : une track hors main déclenche-t-elle bien le sidechain ?)*

**Track 15, pool de FX** (décidé le 2026-11-26) : la track FX porte un petit jeu de presets du Preset Pool, pour varier les transitions sans prendre d'autre track ([[kb/preset-pool]], cas 3 et 5).

| Slot du pool | Preset | Rôle |
| --- | --- | --- |
| 1 | `FX-RISE-1` | Riser court, 1 mesure |
| 2 | `FX-RISE-4` | Riser long, 4 mesures |
| 3 | `FX-IMPACT` | Impact du premier temps |
| 4 | `FX-DOWN` | Downlifter, grosse reverb |
| 5 | `FX-REV` | Reverse, enveloppe propre |
| 6 | `FX-NOISE` | Bruit de transition |
| 7 | `FX-TEXT` | Texture ou voix noyée dans le delay |
| 8 | `FX-JOKER` | Libre |

- **Même ordre dans les cinq banques** : le pool est commun au projet, le geste ne change pas d'une banque à l'autre. Slots 1 à 8 seulement, pour rester sur la première page des touches.
- **Deux niveaux** : sample lock quand le son se contente des réglages de la track (un impact à la place d'un autre) ; preset lock quand il lui faut les siens (LFO du riser, enveloppe du reverse, envois du downlifter).
- **Deux usages** : écrit dans le pattern, par preset locks sur des trigs conditionnels (`FILL`, `1:4`, `1ST`) ; à la main, track 15 en trig mode Preset Pool (`[FUNC] + [UP]` / `[DOWN]`), les touches 1 à 8 jouent les huit presets. Sur la DT2 seulement : la MK2 ne peut pas choisir un preset du pool.
- **Une seule voix** : un impact coupe le riser en cours, ce qui convient sur un drop. Pour garder la queue du riser sous l'impact, l'impact passe en sample lock sur la 6, avec le crash.
- **Envois** : le preset emporte ses niveaux d'envoi delay et reverb, à régler dans chaque preset pour qu'un changement ne coupe ni ne fasse exploser l'effet.
- **Accordage** : FX non accordés par défaut (bruit, impacts). Un riser tonal demande une variante en fa et une en la#.
- *(À vérifier sur la machine : dans quelle banque RAM chargent les samples des presets du pool, et s'ils comptent dans ses 127 slots.)*

**Banques**

| Banque | Section | Patterns | Contenu clé |
| --- | --- | --- | --- |
| B | Flatiron, half-time, 160, fa mineur harmonique | 6-8 | Intro drone seul, beat half-time, variations, montée ; dernier pattern hybride où le stab do# et le kick la# entrent |
| C | Davyl, techno, 142, la# | 4-6 | Groove nu (kick glissant la#, stab do#, charley), variantes ; kit propre, sans rumble |
| D | A Virus, acid, 154, la# phrygien | 10-14 | L'acid entre (notes de 303 et mesures en la#), do bémol ; derniers patterns en respiration : kick allégée ou coupée, drone la#, acid filtrée, triton mi, montée sur fa + silence |
| E | Neptune, tribe, 160, fa mineur harmonique | 6-8 | Tribe percussive et bruitée : kickbass à longue queue en fa, percs tribales, rolls, triolets ; dernier pattern où les breaks s'annoncent |
| F | Ominous, DnB, 170, fa phrygien | 8-10 | Gros kick régulier, breaks découpés, reese fa/sol bémol, variations de plus en plus sales ; vrai pattern de fin |

Nombres de patterns repris de l'ancien plan en suivant le genre. Plus de banque de jokers : les breaks et les « kick + sub seuls » de secours, s'il en faut, vivent dans la banque de leur section.

**Samples à préparer**

- Kicks accordées en fa et la#, en versions propre et saturée (famille par tonalité, lot 4 de [[kb/tutos/_index]] dans Live) ; le kick glissant de la techno en la#, à part ; le kickbass à longue queue de la tribe en fa
- Rumbles accordés en fa (les 12 du live sont en `B-FLATIRON`), en la# s'il en faut sous l'acid
- Sub : une sinusoïde ou un reese, transposé par p-lock ; le stab de sub de la techno en do#
- Notes de 303 (normale, accent, slide) et mesures acid, enregistrées en la# à 154
- Drones et nappes sur fa et la#
- Snares, claps, hats, percs tribales, toms
- Breaks à découper
- FX : impacts, montées de bruit, voix ou ambiances

Tout doit tenir dans la mémoire sample d'un seul projet : surveille-la au fur et à mesure.

### Arborescence des samples sur le +Drive

Un dossier par banque, à plat (SPEC 7.L5) : une banque de patterns = une banque RAM de la DT2 (127 slots) = un dossier, que l'on sélectionne et charge d'un coup dans sa banque RAM (`[FUNC] + [YES]` au chargement). Pas de sous-dossier par branche ni par code : le préfixe du nom regroupe les fichiers au tri alphabétique. Un sample peut être dans plusieurs banques, chacune avec sa copie accordée (SPEC 7.L6).

Le kit par défaut `0-KIT` tient 16 samples, un par track de la grille de [[doctrine]] §1, numérotés par track. Chargé en premier dans la banque RAM A, il occupe les slots A01 à A16, ceux sur lesquels pointe tout pattern vide : c'est la couleur de départ du live. Il a sa propre tonalité (celle de la banque qui ouvre le set, fa pour solaris) ; un pattern d'une autre banque corrige par le TUNE de la track ou un sample lock vers un son de sa banque.

```
00-live/solaris/
├── 0-KIT/        01 BD F Hard 01 slr · 02 RM F Roll 01 slr · 03 SD Tribe 01 slr · 04 PC… · 05 BR 170 Think slr · 06 HH… · 07 OH… · 08 CY Ride slr · 09 BS F Sine slr · 10 ST… · 11 PD F Drone slr · 12 VX… · 13 BL… · 14 ML… · 15 FX Rise 01 slr · 16 BD F Hard 01 slr (kick fantôme)
├── B-FLATIRON/   BD F Kick 03 rth · BD F Flatir 01 gre · RM F Flat Grit gre · BS F Wrap 01 bas · HH… PC… SD… · DL 140 Dubs 02 rth · FX… VX…
├── C-DAVYL/      BD A# Glide 01 slr · BS C# Stab 01 slr · HH Tribe 01 … (trois tracks, kit court)
├── D-AVIRUS/     BS A# 303 Acc slr · BS A# 303 Sld slr · BL 154 AcidA#1 slr · PD A# Drone … · PC… HH…
├── E-NEPTUNE/    BD F Box 01 … · CP… CY… HH… PC… SD… · FX… VX…
└── F-OMINOUS/    BD F Kicks rth · BR 160 Amen 01 slr · BR 170 Think 01 slr · BS F Reese 01 slr · HH… PC… SD… · FX…
```

Les noms ci-dessus sont la cible. État de `library/lives/solaris.json` après
la migration du 2026-11-26 (détail dans le plan, en tête) : `0-KIT` 16,
`B-FLATIRON` 76, `C-DAVYL` 0, `D-AVIRUS` 0, `E-NEPTUNE` 74, `F-OMINOUS` 78,
soit 16 + 76 + 74 + 78 = 244. `E-NEPTUNE` n'a encore ni kick ni basse
accordés : son kickbass en fa est à faire, comme tout le contenu de C et D.
Le kit suivi est encore l'ancien (kick en sol#, tempo 165, slot 16 occupé
par une basse) : à reconstruire en fa, avec la copie du kick en 16.
Chargement d'un projet neuf : `0-KIT` dans la banque RAM A, qui ne reçoit
rien d'autre, puis `B-FLATIRON` dans B, et ainsi de suite jusqu'à
`F-OMINOUS` dans F. Plafond de 127 fichiers par banque.

- **Noms** : nomenclature SPEC 7.J8, `<CODE> [BPM|note] <desc> <pack>`, 18 caractères max, code toujours en tête.
- **Note dans le nom** pour kicks, rumbles, sub et drones, pour retrouver d'un coup d'œil le fa ou le la#.
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

Tout s'enchaîne à la main, pas en mode song, pour pouvoir rallonger ou raccourcir selon la foule.

**Enchaîner**

- Changements en file d'attente : le pattern suivant démarre à la fin du pattern en cours. Longueurs de 1 à 4 mesures pour pouvoir réagir vite.
- Chaînes courtes à l'intérieur d'une banque (par exemple C1 → C2 → C3) pour garder les mains libres sur filtres et mutes.
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

- **Half-time** (B) : roll de snare, sub coupé sur la dernière mesure
- **Techno** (C) : presque rien, c'est une boucle longue ; un trou de stab (trig !FILL sur la 9) ou un charley qui double
- **Acid** (D) : cutoff et résonance de l'acid qui s'ouvrent, accents ; en fin de banque (respiration), montées de drone et de résonance
- **Tribe** (E) : rolls de kick et de toms, hats en triolets
- **DnB** (F) : slices de break réarrangées ou pitchées, reese qui monte, trous de kick (!FILL) ; dernier pattern = fin

**Monter l'énergie sans accélérer** : doubles kicks, hats en triolets, résonance de l'acid qui s'ouvre, patterns raccourcis (16 → 8 → 4 pas) avant un drop.

## Rumble, sub et acid

**Rumble** : sur sa propre piste, pour pouvoir le muter, le filtrer et l'accorder en live. Dans le live, les 12 rumbles (gritty et tube, en fa) sont en B, sous le half-time ; la techno (C) n'en a pas, la tribe (E) amène plutôt un kickbass à longue queue. Rumble sous l'acid et sous la DnB : à décider à l'oreille.

- Il démarre juste après l'attaque de la kick (attaque d'enveloppe douce ou léger décalage du début du sample) : effet de pompage sans sidechain.
- Il est accordé sur la même note que la kick.
- Dans les patterns avec rumble, le sub est coupé ou allégé, car ils occupent la même zone.
- Option : un sample kick + rumble fusionné, compact et en phase, qui libère une piste.

**Sub** : propre et sans distorsion, même sous une kick très saturée. Sinon le bas du spectre devient flou sur un gros système son.

**Acid samplée** : deux méthodes, toutes deux suivent le tempo.

- **Mesures découpées** : une mesure enregistrée au tempo de sa section, découpée en 16 slices rejouées pas à pas.
- **Notes isolées** : notes de 303 (normale, accent, slide) rejouées par p-locks de pitch, avec filtre et résonance de la piste. Plus long à préparer, plus vivant.
- À tempo élevé, régler l'enveloppe d'amplitude pour éviter clics et chevauchements de slices.
- L'acid monte bien en intensité avec un overdrive poussé : à garder pour les pics de l'acid (D).

## Checklist de préparation

- [ ] Samples préparés et rangés par section (voir la liste plus haut)
- [ ] Presets sauvegardés : kicks, rumbles, sub, acid, drones
- [ ] Pool de FX : huit presets `FX-` sauvés et rangés dans les slots 1 à 8 du pool
- [ ] Pattern maître de chaque banque (B à F)
- [ ] Variations et fills de la banque B, avec le pattern hybride de sortie
- [ ] Banque C : groove nu en la# à 142, variantes
- [ ] Variations et fills de la banque D (acid), avec la respiration et la montée finale sur fa
- [ ] Banque E : entrée de la tribe en fa, kickbass à longue queue, dernier pattern où les breaks s'annoncent
- [ ] Variations et fills de la banque F, avec le pattern de fin
- [x] `solaris.json` réaligné sur les banques B à F et les tonalités fa et la# (2026-11-26)
- [ ] Kit `0-KIT` reconstruit en fa, copie du kick en track 16
- [ ] +Drive réaligné ; sur la DT2, OMINOUS de B vers F puis FLATIRON de A vers B
- [ ] Transitions travaillées : half-time → techno (note tenue, tempo à 142), techno → acid (saut à 154, do bémol), acid → tribe (respiration, fa tenue, retombée en fa à 160), tribe → DnB (kick et sub en fa tenus, saut à 170)
- [ ] Raccourci du mode fill maîtrisé sans regarder
- [ ] Une répétition complète enregistrée, durée et transitions vérifiées
- [ ] Projet sauvegardé sur ordinateur, au moins deux copies
- [ ] Fiche papier : [[solaris-pense-bete.svg]] (une page A4 paysage en couleur, produite par `scripts/solaris_pense_bete.py`, dont les tableaux recopient cette doctrine ; à régénérer et réimprimer à chaque changement de tableau)
