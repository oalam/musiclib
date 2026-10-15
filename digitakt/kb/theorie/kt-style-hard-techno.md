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

Référence disponible ([[_index]]) : Beauz *Bel Mercy (hard techno
remix)*, 161,5 BPM, un seul morceau. **À compléter après grab** de deux
ou trois références (hub, « À grabber ») : la colonne mesurée n'est pas
une moyenne.

| Élément | Théorique | Mesuré (Beauz) | Lecture |
|---|---|---|---|
| Tempo | 150-160, schranz 150-170 | 161,5 | dans la fourchette haute |
| Kick + rumble (sub) | kick `X...X...X...X...`, rumble `.xxx.xxx.xxx.xxx` | `.XxxxxxXxx..xXx.` | sub quasi continu : le rumble remplit tout ; le repliage n'a pas calé le downbeat (phase non garantie) |
| Basse, pression (mid) | `..x...x...x...x.` ou `.xxx` | `x.Xx.xXX...xxXxx` | mid chargé sur les pas 3-4 et 7-8 : contretemps et « a » |
| Hats, shaker (high) | hat ouvert `..x...x...x...x.`, shaker `xxxxxxxxxxxxxxxx` | `.xX.XxXxx.X.xXX.` | high dense avec des creux : le shaker à vélocités variables |
| Harmonie | atonal ou mineur sur une tonique | B blues, `E5 E E5 G#dim E Fdim E G#dim` | quintes nues et accords diminués (triton, KT7) : la tension industrielle sur une tonique fixe |
| Syncope, swing | droit, pression continue | `sync` 0,64, `swing` 0,37 | énergie **après** le temps (le « e »), à l'inverse du tribe : le rumble suit le kick |

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

**Énergie après le temps.** Le `swing` mesuré de Beauz (0,37) est le seul
sous 0,5 des styles cœur : l'énergie tombe sur le « e », après le temps,
pas sur le « a » avant. C'est le rumble qui gonfle après le kick, et le
hat ouvert sur le « et ». Le tribe et le mental **anticipent** (KT3,
KT10, KT11), le hard techno **suit** : deux groove opposés sur le même
four-on-floor. Sur la DT2, ce sont les pas 2-3 de chaque temps qui
portent les trigs (rumble, hat ouvert), pas le pas 4.

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
hard groove ne sont pas sourcés par écrit : à documenter après grab.

## Sur la DT2

Grille de la [[../../doctrine]] §1 : kick 1, rumble 2, hat fermé 5, hat
ouvert 6, perc B 8 (shaker), basse 9, lead 10, FX 15. Gestes :
[[../rumble-grave]], [[../send-fx-compresseur]] (sidechain),
[[../microtiming-retrigs]], [[../page-setup]] (48 pas), [[../fill-conditions]].

1. **Double kick et pression (10 min).** 155 BPM, kick 1 court (AMP 80
   ms), rumble 2 sur les mêmes pas avec ducking (`SCS` = TRK1, fiche
   [[../send-fx-compresseur]]), puis rumble en `.xxx` passe-bas. Comparer
   les deux : même pas que le kick = respiration, `.xxx` = pression. Puis
   sans ducking : entendre la bouillie.
2. **Groove qui suit (5 min).** Hat ouvert 6 sur les pas 3, 7, 11, 15 ;
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
- Un seul morceau de référence : la colonne mesurée de la signature ne
  vaut pas moyenne, et le repliage n'a pas calé le temps 1 (sub continu).
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
