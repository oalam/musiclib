---
tags: [digitakt, kb, theorie, kt]
theme: Hard techno et schranz
lot: 3
ordre: 13
styles: [hard techno, schranz, hard groove]
statut: draft
updated: 2026-10-15
---

# KT13 — Hard techno et schranz

**En une phrase** : le hard techno moderne (150-160) est un four-on-floor
à double kick, un kick court sur le temps et un rumble à longue queue
ducké entre les coups, dont la pression vient de la basse en
contretemps, des hats offbeat et d'un shaker en doubles croches, et dont
la ligne mélodique tourne sur 3 mesures contre 4 ; cette KT cadre la
**rythmique**, le son du rumble est dans [[../rumble-grave]] et
[[../../../sounddesign/rumble]].

## Signature

Références ([[_index]], grabs du 2026-10-15) : hard techno Beauz *Bel
Mercy (hard techno remix)* (161,5), Sara Landry & Shlømo *Play With Me*
(160,7), 999999999 *300000003* (136, sans doute lu en dessous), I Hate
Models *Daydream* (136) ; schranz Chris Liebing & André Walter *American
Madness* (134) et DJ Rush *Motherfucking Bass* (136), tempos à vérifier à
l'oreille.

| Élément | Théorique | Mesuré | Lecture |
|---|---|---|---|
| Tempo | 150-160, schranz 150-170 | 160,7-161,5 (Beauz, Sara Landry), 134-136 (les quatre autres) | deux générations : le hard techno 2023+ à 160, les classiques lus à 135 (probablement 140-150 réels) |
| Kick + rumble (sub) | kick `X...X...X...X...`, rumble `.xxx.xxx.xxx.xxx` | Sara Landry `X...X...X...X.x.`, Beauz `.XxxxxxXxx..xXx.`, moyenne `Xx.xx.x.X..xXx.x` | deux écritures : kick net et rumble ducké (Sara Landry), ou sub continu où le rumble remplit tout (Beauz) |
| Basse, pression (mid) | `..x...x...x...x.` ou `.xxx` | moyenne `X.xXxxxXx..Xxx.X`, Sara Landry `XxXXx.xXXx.XX.xx` | mid chargé sur les pas 3-4 : contretemps et « a », la pression |
| Hats, shaker (high) | hat ouvert `..x...x...x...x.`, shaker `xxxxxxxxxxxxxxxx` | moyenne `X.XxxxXxXxxxXXXx`, 999999999 `X.xxXXXXXX.XXXX.` | high presque continu : le shaker en doubles croches, plus dense que le tribe |
| Schranz (sub) | boucles roulantes | Liebing `XXxxX.X.Xxx.X.X.`, DJ Rush `X.xxXxx.XxXXxxx.`, `sync` 0,58-0,69 | kick sur les temps et roulements entre : la percussion roule, pas de trou |
| Harmonie | atonal ou mineur sur une tonique | Beauz `E5 G#dim E Fdim`, Sara Landry E phrygien `Fsus2 Fm Gsus2 F#m`, 999999999 `G#sus2 G# … Dsus2`, IHM `G#dim Am`, Liebing `G5 Gsus2` | pédale de quinte nue et tensions de demi-ton ou de triton au-dessus (KT6, KT7) : phrygien et diminué sur un grave fixe |
| Syncope, anticipation | droit, pression continue | `sync` 0,50-0,64 ; `swing` Sara Landry 0,75, 999999999 0,64, IHM 0,55, Beauz 0,37 | trois sur quatre **anticipent** comme le tribe ; Beauz, qui suit, est l'exception (voir ci-dessous) |

## Vocabulaire

- **Double kick** : deux sons de kick superposés, un court et punchy sur
  le temps, un long et réverbéré (le rumble) qui remplit l'intervalle.
- **Rumble** : queue de kick réverbérée, saturée, passe-bas, duckée par
  le kick (doctrine §9, fiche [[../rumble-grave]]).
- **Sidechain** : compression du rumble déclenchée par le kick ; il
  gonfle entre les coups.
- **Pression** : sensation de grave continu sous un kick qui respire ;
  vient du rumble et de la basse en contretemps, pas du volume.
- **Offbeat hat** : hat ouvert sur le « et » (`..x.`), le contretemps
  classique.
- **Shaker 16es** : doubles croches continues à vélocités variables, le
  « moteur » du haut du spectre.
- **Ligne sur 3 mesures** : lead ou acid de 48 pas contre un kick de 16 ;
  polymétrie de KT2 (ppcm 48).
- **Schranz** : hard techno allemand des années 2000 (150-170), boucles
  distordues, percussions roulantes, sans mélodie.
- **Hard groove** : variante aux percussions latines et tribales,
  moins saturée.
- **Reverse kick** : kick inversé posé juste avant le temps 1 d'une
  phrase ; effet de transition.

## Pourquoi ça marche

**Concret d'abord : le double kick en chiffres.** À 155 BPM, 1 pas =
60 / 155 / 4 = 96,8 ms, un temps = 387 ms. Kick court : 80 ms. Rumble :
queue de 300 ms, duckée pendant les 80 ms du kick, qui gonfle ensuite et
retombe juste avant le kick suivant. Le sub est donc occupé 387 ms sur
387, par le kick puis par sa propre queue : c'est ce que mesure la
signature de Beauz (`.XxxxxxXxx..xXx.`, sub presque sans trou) et c'est
la **pression**. Comparer au tribe (KT10) où le sub est `X...X...` avec
une basse offbeat : le hard techno n'a pas de trou dans le grave, le
tribe en a.

**Pourquoi un seul instrument dans le grave.** Kick et rumble sont le
même sample (doctrine §9) : même note, même timbre, une seule
fondamentale (KT5). La basse « pression » en contretemps est souvent le
rumble lui-même en `.xxx` passe-bas, ou une note tenue à l'octave. C'est
le cadre rythmique de cette KT : **le grave est une seule voix, qui
respire au rythme du kick**. Le son du rumble, lui, est traité ailleurs
(fiche [[../rumble-grave]], notebook [[../../../sounddesign/rumble]],
presets par banque de live 8.L2).

**Anticiper ou suivre : les deux groove du hard techno.** Avec un seul
morceau (Beauz, `swing` 0,37), la première version de cette KT concluait
que le hard techno « suit » le temps, à l'inverse du tribe. Les trois
références ajoutées disent le contraire : Sara Landry 0,75, 999999999
0,64, I Hate Models 0,55 mettent l'énergie sur le « a », avant le temps,
comme le tribe et le mental (KT3, KT10, KT11). Ce qui distingue le hard
techno n'est donc pas le sens du groove mais la **pression** : un sub
plein (`sync` 0,50-0,64) et un haut du spectre presque continu (shaker),
là où le tribe laisse des trous. Beauz, avec son rumble qui gonfle après
le kick et son hat ouvert sur le « et », est la version « qui suit » :
elle existe, mais c'est une option, pas la règle. Sur la DT2, les deux se
programment : trigs de rumble et de hat ouvert sur les pas 2-3 du temps
pour suivre, trigs de shaker accentués et de basse sur le pas 4 pour
anticiper ; ne pas mélanger les deux sur le même pattern.

**Hats offbeat et shaker.** Le hat ouvert sur le contretemps est le
balancier ; le shaker en 16 doubles croches à vélocités variables (KT3,
exercice 3) donne la continuité dans l'aigu, comme le rumble dans le
grave. Le high mesuré (`.xX.XxXxx.X.xXX.`) montre cette densité avec des
creux : le shaker n'est pas plat, ses vélocités font le motif.

**Ligne sur 3 mesures contre 4.** Sara Landry (Ableton) pose un lead de 3
mesures sur un kick de 4 : 48 pas contre 64, retour en phase tous les
ppcm(48, 64) = 192 pas = 12 mesures (KT2). Sur la DT2 en PER TRACK, c'est
une track 10 de 48 pas (3 pages) dans un pattern de 64 : la ligne glisse
d'une mesure par phrase de 4, et se réaligne toutes les 12. Harmonie
atonale ou mineure sur une tonique ; Beauz joue des `dim` (triton, KT7)
entre des quintes nues : tension industrielle sur un grave fixe.

**Forme.** Intro 16-32, plateaux de 16 ou 32, break de 8 à 16 avec le
kick coupé mais le rumble ou la pression maintenus, retour (KT9). Le
reverse kick sur la 15 (doctrine §5) juste avant le 1 du drop. Schranz et
hard groove ne sont pas sourcés par écrit ; les deux schranz grabés
confirment les boucles roulantes (sub `XXxxX.X.Xxx.X.X.`, `sync` 0,58-0,69).

## Sur la DT2

Grille de la [[../../doctrine]] §1 : kick 1, rumble 2, hat fermé 6, hat
ouvert 7, perc 4 (shaker), basse 9, lead 10, FX 15. Gestes :
[[../rumble-grave]], [[../send-fx-compresseur]] (sidechain),
[[../microtiming-retrigs]], [[../page-setup]] (48 pas), [[../fill-conditions]].

1. **Double kick et pression (10 min).** 155 BPM, kick 1 court (AMP 80
   ms), rumble 2 sur les mêmes pas avec ducking (`SCS` = TRK1, fiche
   [[../send-fx-compresseur]]), puis rumble en `.xxx` passe-bas. Comparer
   les deux : même pas que le kick = respiration, `.xxx` = pression. Puis
   sans ducking : entendre la bouillie.
2. **Groove qui suit (5 min).** Hat ouvert 7 sur les pas 3, 7, 11, 15 ;
   shaker 8 en 16 pas, vélocités 100 / 40 / 70 / 40 par temps, micro
   timing 0 puis +3 ticks sur les pas pairs (fiche
   [[../microtiming-retrigs]]), `PRE` / `NEI` pour des variations. Le
   groove tombe après le temps ; comparer avec les hats tribe de KT10
   (pickup sur le « a »).
3. **Ligne sur 3 mesures (10 min).** Pattern de 64 pas, `[FUNC] + [PAGE]`,
   PER TRACK, track 10 à 48 pas : ligne de 2-3 notes en pentatonique
   avec un `dim` (b5) sur la dernière mesure. Écouter 12 mesures, le
   temps du réalignement ; puis `RESET` à 64 pour forcer le retour à
   chaque phrase.

## Pièges

- Kick et rumble à deux notes différentes : battement dans le sub (KT5) ;
  le rumble est fait **du** kick, même `TUNE`.
- Rumble sans ducking : la pression devient de la boue ; le sidechain est
  la respiration du style.
- Juger le rumble sur des enceintes de bureau : toujours trop fort ;
  casque ou sub (fiche [[../rumble-grave]]).
- Le repliage de la passe cale le maximum, pas le temps 1 : sur un sub
  continu (Beauz) la phase est inconnue ; lire les motifs. Les tempos de
  999999999, I Hate Models et des deux schranz (134-136) sont sans doute
  lus en dessous : vérifier à l'oreille avant de s'en servir en set.
- Ligne de 48 pas et conditions `A:B` : les tours comptent sur 48, pas
  sur 64 (fiche [[../fill-conditions]], KT2).
- Risque de doublon avec [[../rumble-grave]] : cette KT ne parle que de
  placement et de groove ; le son, la recette et les presets restent dans
  la fiche et le notebook.

## Ressources

- Attack Magazine, Beat Dissected *Dark techno rumble* :
  <https://www.attackmagazine.com/technique/beat-dissected/dark-techno-rumble/> `[V]`
- Ableton, *Sara Landry high-end hard techno* :
  <https://www.ableton.com/en/blog/sara-landry-high-end-hard-techno/> `[V]`
  (kick en premier, distorsion multi-étages, lead sur 3 mesures).
- Production Music Live, *rumbling techno kick (Johannes Menzel)* :
  <https://productionmusiclive.com/blogs/news/6-steps-to-create-that-rumbling-techno-kick-you-love-with-johannes-menzel> `[R]`
- Sinee, *Next generation hard techno* :
  <https://sinee.de/en/next-generation-hard-techno-how-to-make-a-track/HTMAT-007/> `[R]` (payant).
- Schranz et hard groove : non sourcés par écrit.

## Liens

[[_index]] · [[../../doctrine]] §5, §9, §10 · [[../rumble-grave]] ·
[[../send-fx-compresseur]] · [[../microtiming-retrigs]] ·
[[../page-setup]] · [[../fill-conditions]] ·
[[../../../sounddesign/rumble]] · KT2 [[kt-polymetrie-polyrythmie]] ·
KT3 [[kt-swing-microtiming]] · KT5 [[kt-tonalite-du-grave]] · KT7
[[kt-tensions-lignes]] · KT10 [[kt-style-tribe]] · KT16 (industrial, à
rédiger)
