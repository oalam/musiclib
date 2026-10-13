# Live Digitakt 2 — doctrine free party

Oct 13, 2026 · @tom

## Structure du set

Un live de 1h15 à 1h30 qui reste entre 160 et 175 BPM : l'énergie monte par la densité, la saturation et la tonalité, pas par le tempo.

| Section | Tempo (BPM) | Durée | Rôle |
| --- | --- | --- | --- |
| Half-time / dubstep | 160 (ressenti 80) | 10-15 min | Ouverture lourde et lente |
| Drum and bass | 162-168 | 15-20 min | Ça s'ouvre, vers la jungle et les rollers |
| Tribe | 165-170 | 20-25 min | Cœur du set |
| Respiration mental | 170 | 5-10 min | On retire de l'énergie, tension sans kick |
| Tribe saturé | 170-175 | 15-20 min | Finish massif |

- **Half-time → DnB** : même tempo, on change seulement la rythmique de batterie (kick sur 1, snare sur 3 → breakbeat full-time).
- **DnB → tribe** : bascule breakbeat → 4x4 sur un break. On mute la batterie DnB, puis on rentre la kick tribe seule.
- **Tempo** : on le monte à la main par petites touches pendant les breaks, +1 à 2 BPM à la fois. À l'intérieur d'une section, on y touche le moins possible.

## Progression harmonique

Une tonique stable par section, et on monte d'un ton (+2 demi-tons) pour relancer : fa → sol → la. L'harmonie passe par la fondamentale (sub, kick accordée, acid), pas par des accords.

| Section | Tonalité | Couleur | Sub (octave 1) |
| --- | --- | --- | --- |
| Half-time | Fa mineur | Basse lente, peu de notes | \~44 Hz |
| Drum and bass | Fa phrygien | Ajout de sol bémol, reese fa/sol bémol | \~44 Hz |
| Tribe | Sol mineur | Acid en sol, kick accordée en sol | \~49 Hz |
| Respiration mental | Sol phrygien | Drone sur sol, triton (ré bémol) | \~49 Hz |
| Tribe saturé | La mineur | Kick saturée et acid en la | \~55 Hz |

**Pivots (notes communes pour changer de tonalité)**

- **Fa → sol** : do ou si bémol. Drone sur do pendant un break, sub coupé, puis kick et sub relancés en sol.
- **Sol → la** : ré. Ré bien présent pendant la respiration, filtre et résonance qui montent, silence d'un temps ou d'une mesure, puis retombée en la.

**Accordage sur la Digitakt**

- Kicks et rumble accordés sur la tonique de la section, via le pitch de la piste.
- Samples acid enregistrés en fa, transposés de +2 ou +4 demi-tons par p-lock ou au niveau de la piste.

## Organisation de la Digitakt 2

Six banques dans un seul projet : une par section, plus une pour les jokers. Même disposition de pistes partout, pour que les mutes et la Control All tombent toujours au même endroit.

**Disposition des pistes (identique dans tous les patterns)**

| Piste | Rôle |
| --- | --- |
| T1 | Kick |
| T2 | Sub |
| T3 | Rumble (sections tribe) |
| T4 | Snare / clap |
| T5-T6 | Hats |
| T7-T8 | Percs |
| T9 | Acid |
| T10 | Drone / nappe |
| T11 | FX |
| T12-T13 | Breaks découpés |

**Banques**

| Banque | Section | Patterns | Contenu clé |
| --- | --- | --- | --- |
| A | Half-time, 160, fa | 6-8 | Intro drone seul, beat half-time, variations, montée, bascule full-time (même kit) |
| B | DnB, 162-168, fa phrygien | 8-10 | Breaks découpés, reese fa/sol bémol, variations de plus en plus sales ; dernier pattern hybride avec kick régulière |
| C | Tribe, 165-170, sol | 10-12 | Premier pattern pivot (drone sur do, sub coupé), acid, percs tribales, rolls, triolets |
| D | Respiration, 170, sol phrygien | 4-6 | Kick allégée ou coupée, drone sol, acid filtrée, triton ; dernier pattern = montée sur ré + silence |
| E | Tribe saturé, 170-175, la | 8-10 | Kick saturée, sub propre, acid saturée, rolls de kick ; vrai pattern de fin |
| F | Jokers et secours | 8-12 | Un break par section, « kick + sub seuls » en fa, sol et la, variations en réserve |

**Samples à préparer**

- Kicks accordées en fa, sol et la, en versions propre et saturée
- Rumbles accordés (et éventuellement un kick + rumble fusionné en la pour le finish)
- Sub : une sinusoïde ou un reese, transposé par p-lock
- Notes de 303 (normale, accent, slide) et mesures acid à découper
- Drones et nappes sur do, ré et sol
- Snares, claps, hats, percs tribales, toms
- Breaks à découper
- FX : impacts, montées de bruit, voix ou ambiances

Tout doit tenir dans la mémoire sample d'un seul projet : surveille-la au fur et à mesure.

### Arborescence des samples sur le +Drive

Un dossier par banque, puis un niveau BRANCHE (DRUMS, TONAL, LOOPS, FX, VX), sans dossier par code : le préfixe du nom regroupe les fichiers au tri alphabétique. Les sons partagés entre banques vivent dans 0-COMMON, jamais dupliqués.

```
00-live/solaris/
├── 0-COMMON/
│   ├── DRUMS/   BD F Hard 01 slr · BD G Hard 01 slr · BD A Sat 01 slr · RM G Roll 01 slr · RM A Roll 01 slr
│   ├── TONAL/   BS F Sine slr · BS F Reese 01 slr · PD C Drone 01 slr · PD D Drone 01 slr · PD G Drone 01 slr
│   └── FX/      FX Rise 01 slr · FX Impact 01 slr
├── A-HALF/
│   ├── DRUMS/   CP… HH… PC… SD…
│   └── TONAL/   BS… (wobbles)
├── B-DNB/
│   ├── DRUMS/   HH… PC… SD…
│   ├── TONAL/   BS… (reese fa / sol bémol)
│   └── LOOPS/   BR 160 Amen 01 slr · BR 170 Think 01 slr
├── C-TRIBE/
│   ├── DRUMS/   HH… OH… PC… TM…
│   ├── TONAL/   BS G 303 Acc slr · BS G 303 Sld slr
│   └── LOOPS/   BL 168 AcidG1 slr
├── D-RESPI/
│   ├── TONAL/   PD…
│   └── LOOPS/   BL… (acid filtrée)
├── E-SATURE/
│   ├── DRUMS/   BD A KickRm 01 slr · CP… PC… SD…
│   └── LOOPS/   BL 172 AcidA1 slr
└── F-JOKER/
    ├── FX/
    └── VX/
```

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
- **Tribe** : rolls de kick et de toms, hats en triolets
- **Respiration** : montées de drone et de résonance
- **Tribe saturé** : roll de kick qui accélère, coupure sèche, retombée sur le temps 1

**Monter l'énergie sans accélérer** : doubles kicks, hats en triolets, résonance de l'acid qui s'ouvre, patterns raccourcis (16 → 8 → 4 pas) avant un drop.

## Rumble, sub et acid

**Rumble** : sur sa propre piste dans les sections tribe, pour pouvoir le muter, le filtrer et l'accorder en live.

- Il démarre juste après l'attaque de la kick (attaque d'enveloppe douce ou léger décalage du début du sample) : effet de pompage sans sidechain.
- Il est accordé sur la même note que la kick.
- Dans les patterns avec rumble, le sub est coupé ou allégé, car ils occupent la même zone.
- Option pour le finish : un sample kick + rumble fusionné en la, compact et en phase, qui libère une piste.

**Sub** : propre et sans distorsion, même sous une kick très saturée. Sinon le bas du spectre devient flou sur un gros système son.

**Acid samplée** : deux méthodes, toutes deux suivent le tempo.

- **Mesures découpées** : une mesure enregistrée au tempo de sa section, découpée en 16 slices rejouées pas à pas.
- **Notes isolées** : notes de 303 (normale, accent, slide) rejouées par p-locks de pitch, avec filtre et résonance de la piste. Plus long à préparer, plus vivant.
- À tempo élevé, régler l'enveloppe d'amplitude pour éviter clics et chevauchements de slices.
- L'acid monte bien en intensité avec un overdrive poussé : à garder pour le tribe saturé.

## Checklist de préparation

- [ ] Samples préparés et rangés par section (voir la liste plus haut)
- [ ] Presets sauvegardés : kicks, rumbles, sub, acid, drones
- [ ] Pattern maître de chaque section (A à E)
- [ ] Variations et fills de la banque A
- [ ] Variations et fills de la banque B
- [ ] Variations et fills de la banque C
- [ ] Variations de la banque D, avec la montée finale
- [ ] Variations et fills de la banque E, avec le pattern de fin
- [ ] Banque F : breaks, « kick + sub seuls » en fa, sol et la, réserves
- [ ] Transitions travaillées : half-time → DnB, DnB → tribe, fa → sol, respiration → finish
- [ ] Raccourci du mode fill maîtrisé sans regarder
- [ ] Une répétition complète enregistrée, durée et transitions vérifiées
- [ ] Projet sauvegardé sur ordinateur, au moins deux copies
- [ ] Fiche papier : ordre des banques, tempos, patterns clés
