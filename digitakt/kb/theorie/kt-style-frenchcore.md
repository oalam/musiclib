---
tags: [digitakt, kb, theorie, kt]
theme: Frenchcore / hardcore / bouncy
lot: 3
ordre: 12
styles: [frenchcore, hardcore, gabber, bouncy]
statut: draft
updated: 2026-10-15
---

# KT12 — Frenchcore / hardcore / bouncy

**En une phrase** : le frenchcore est un four-on-floor à 180-220 BPM dont
le kick, clippé jusqu'à la dent de scie, est devenu un instrument
mélodique (pitched kick) et dont la basse offbeat `.xxx` remplit tout
l'espace entre les kicks ; le hardcore classique garde le kick fixe et
la basse dans le kick (kickbass), et le bouncy ajoute le galop
`x..xx..x`.

## Signature

Références ([[_index]], grabs du 2026-10-15) : frenchcore Dr. Peacock
*Trip to Russia*, Sefa *Leven is Lijden*, Imperials *Ravage*, Maissouille &
Kriptonic *Rock the Beat* (The Sickest Squad remix, seul proxy « bouncy »),
tous à 198,8 BPM (sidecars réanalysés avec le tempo de la library, le
détecteur les lisait à 100,4) ; hardcore Maureen *Kompet x Jiggle* (215,3,
réanalysée) et Mad Dog *Wild for the Night* (161,5).

| Élément | Théorique | Mesuré | Lecture |
|---|---|---|---|
| Tempo | hardcore 160-200, frenchcore 180-220 | frenchcore 198,8 (× 4), hardcore 215,3 et 161,5 | à 199 BPM, 1 pas = 60 / 198,8 / 4 = 75,5 ms ; le détecteur lit la moitié, à corriger à la main (KT4) |
| Kick + basse offbeat (sub) | kick `X...` + basse `.xxx` | Sefa `X.xXX.xXx.xXx..X`, Dr. Peacock `.x..x.xxXX.xX..x` | Sefa : kick sur chaque temps puis coups sur les pas 3-4, la basse `.xxx` vue à moitié (le pas 2 est mangé par la queue du kick) ; sub plein, aucun trou |
| Galop | `x..xx..x` | Mad Dog `xxX..xX..xX..XX.`, Imperials `XX.X.x...X..x..x` | cellule `x..` enchaînée : le tresillo (KT1) appliqué au kick |
| Médium | hoover, screech | Imperials `XXXxxXX.XXXxx.XX`, Maureen `XxxXX.xXXxXxXxxx` | mid presque plein : hoovers et basse saturée occupent tout |
| Syncope | pression continue | `sync` 0,64-0,71 (frenchcore), 0,59 (Maureen) | le style le plus syncopé des styles cœur : presque tout tombe hors des temps, le kick seul les tient |
| Anticipation | droit | `swing` Sefa 0,87, Maissouille 0,85 ; Dr. Peacock 0,39, Imperials 0,26 | deux écoles : basse qui pousse vers le temps, ou basse qui suit (KT3) |
| Harmonie | mineur, progression portée par le pitch du kick | Dr. Peacock `Bm B5 Bm B5`, Sefa `Bsus2 G#m G#5 A C#5`, Maissouille `G5 Gdim C#5 Gdim`, Maureen `C#5 Csus2 D5` | la tierce apparaît (Bm), les fondamentales bougent i → bVI → bVII (Sefa : B, G#, A), le triton G → C# chez Maissouille : c'est le kick qui change de note (KT8) |

## Vocabulaire

- **Pitched kick** : kick accordé dont la note change par p-lock de
  `TUNE` pour jouer la progression ; le kick est la basse et la mélodie.
- **Kick en trois couches** : click (2-5 kHz), corps (100-300 Hz), sub
  (50 Hz), fabriqués séparément puis resamplés en un sample (veille §B3,
  forum Renoise).
- **Clipping** : écrêtage dur qui transforme le sinus du kick en quasi
  carré, donc en son harmonique, donc mélodique.
- **Gating de la queue** : couper la queue du kick avant le pas suivant
  pour laisser la place à la basse offbeat.
- **Offbeat bassline** : basse `.xxx.xxx.xxx.xxx`, trois doubles
  croches après chaque kick, jamais sur le temps ; distordue, souvent
  la même note que le kick.
- **Galop** : cellule `x..xx..x` (ou `x..x..x..x..` enchaîné), le
  tresillo de KT1 appliqué au kick ; signature du bouncy.
- **Hoover** : son de synthé en dents de scie désaccordées avec
  portamento (Alpha Juno) ; **screech** : lead aigu saturé.
- **Gabber** : hardcore hollandais à 160-190, kick distordu carré, 4/4
  strict.
- **Bouncy** : hardcore / frenchcore 2022+ au kick rebondissant (pitch
  envelope marqué, KT10) et au galop ; non sourcé par écrit.
- **Breaks en 3/4 ou 5/8** : mesures impaires dans les breakdowns
  (Wikipedia *Frenchcore*), influence classique.

## Pourquoi ça marche

**Concret d'abord : kick et basse à 200 BPM.** 1 pas = 60 / 200 / 4 =
75 ms. Kick sur le pas 1, 75 ms de kick puis la basse sur les pas 2, 3,
4 (`.xxx`), chacun 75 ms : le grave est occupé 100 % du temps, par un
seul instrument accordé sur une seule note (KT5). C'est le mur de son
frenchcore : pas de silence dans le sub, mais pas deux notes non plus.
Le gating de la queue du kick à 70 ms est ce qui rend la basse lisible.

**Pourquoi le kick devient mélodique.** Un sinus clippé devient un carré,
et un carré a des harmoniques impaires (3, 5, 7 fois la fondamentale) :
un kick à 55 Hz clippé fait entendre 165, 275, 385 Hz. Le kick a donc
une note perceptible bien au-dessus du sub, et transposer le sample de
deux ou trois demi-tons change une **mélodie**, pas seulement un
« boum ». Le frenchcore en fait sa progression : i → bVI → bVII (KT8)
jouée par le kick lui-même, un accord par 4 mesures, par p-lock de
`TUNE` sur la track 1. Maureen mesure C#5 → Csus2 → D5 → C#5 : des
demi-tons autour de la tonique, en quintes nues, portés par le kick.

**La basse offbeat est la rolling bass de la trance.** `.xxx` à 140
(trance) et `.xxx` à 200 (frenchcore) sont la même cellule (veille §C6,
KT19) : trois doubles croches après le kick, filtre mouvant. Le passage
trance → frenchcore se fait en montant le tempo et la distorsion, la
cellule ne change pas. C'est la passerelle de KT4 appliquée au grave.

**Le galop du bouncy.** Mad Dog mesure dans le sub `xxX..xX..xX..XX.` :
une cellule `x..` enchaînée, c'est-à-dire E(5, 16) ou le tresillo
prolongé (KT1). Le kick n'est plus sur les temps mais sur un cycle de 3
pas qui se recale tous les 16 : la polymétrie de KT2 dans le kick
lui-même. Un galop `x..xx..x` par temps double la densité du kick sans
le mettre en double-time (KT4) : deux coups rapprochés puis un vide, ce
qui rebondit. Imperials (`XX.X.x...X..x..x`) montre la même cellule à
199 BPM. Le bouncy, non sourcé par écrit, n'a pour l'instant qu'un proxy
dans la library.

**Hardcore monolithique.** Chez Maureen (réanalysée à 215 BPM), mid et
high sont presque pleins (`XxxXX.xXXxXxXxxx`) et le sub se concentre sur
deux temps : une seule idée rythmique, martelée sur toutes les bandes. Pas de percs en appel-réponse (KT9),
pas de polymétrie : la variation vient du pitch du kick, des hoovers et
des breaks. Le hardcore est l'inverse du tribe sur ce point : le tribe
varie la rythmique sur un kick fixe, le hardcore varie la hauteur sur une
rythmique fixe.

**Breaks impairs.** Les breakdowns frenchcore passent volontiers en 3/4
(12 pas) ou 5/8 (10 pas) sur une mélodie de synthé « classique », puis le
4/4 revient au drop : sur la DT2, un pattern de break de 12 ou 10 pas
(PER PATTERN, fiche [[../page-setup]]) chaîné avec le pattern principal,
avec `CHANGE` pour la bascule (fiche [[../patterns-chaines]]).

## Sur la DT2

Grille de la [[../../doctrine]] §1 : kick 1, rumble 2 (ou click), sub 13
le temps de fabriquer, basse 9. Gestes : [[../sampling-resampling]],
[[../amp-overdrive-bitreduction]], [[../parameter-preset-locks]],
[[../page-setup]], [[../fill-conditions]].

1. **Kick en trois couches (10 min).** Track 1 click (sample court,
   passe-haut 2 kHz), track 2 corps (kick sec, passe-bande 100-300 Hz),
   track 13 sub (sinus ou kick filtré bas, 50 Hz, accordé). Les trois sur
   le pas 1, muter tout le reste, resampler une mesure (fiche
   [[../sampling-resampling]]), charger le résultat sur la 1, overdrive
   en deux étages. Nommer avec la note.
2. **Offbeat bassline et pitched kick (10 min).** 200 BPM, kick sur les
   temps, AMP du kick coupé à 70 ms. Basse 9 `.xxx.xxx.xxx.xxx`, même
   note que le kick, overdrive. Puis p-lock `TUNE` du kick : 0 sur 4
   mesures, −4 (bVI) sur 4, −2 (bVII) sur 4, 0 sur 4 ; la basse suit par
   les mêmes locks. La progression est jouée par le grave.
3. **Galop (5 min).** Kick seul : trigs 1, 4, 7, 10, 13 (E(5, 16)) puis
   `x..xx..x` par demi-mesure (trigs 1, 4, 5, 8, 9, 12, 13, 16). Comparer
   avec le 4/4 à la même vitesse ; passer le galop en `3:4` pour qu'il
   ne tourne qu'une mesure sur quatre (fiche [[../fill-conditions]]).

## Pièges

- Kick long **et** basse offbeat : le kick doit être coupé avant le pas
  2, sinon kick et basse se masquent dans le sub (KT5) ; gating de la
  queue.
- Transposer un kick clippé de plus de 3-4 demi-tons change son timbre :
  une famille de kicks par tonalité, ou une progression serrée (demi-ton,
  ton, comme Maureen).
- Trois couches resamplées à pleine échelle saturent encore à
  l'overdrive de la DT2 : garder de la marge avant resampling (fiche
  [[../kick-mental-vst]]).
- Le galop en double-time ressenti : à 200 BPM, `x..xx..x` par temps
  fatigue vite ; par demi-mesure ou en condition `3:4` seulement.
- Le tag `genre` de la library (« hardcore », « breakbeat ») ne
  distingue pas frenchcore, gabber et bouncy : trier à l'oreille après
  grab.
- Le bouncy n'a qu'un proxy (la remix de Maissouille par The Sickest
  Squad) : la colonne galop s'appuie sur Mad Dog et Imperials, à confirmer
  sur un vrai bouncy 2022+.

## Ressources

- Wikipedia, *Frenchcore* : <https://en.wikipedia.org/wiki/Frenchcore> `[V]`
- Wikipedia, *Hardcore (EDM)* :
  <https://en.wikipedia.org/wiki/Hardcore_(electronic_dance_music_genre)> `[?]`
- Forum Renoise, kicks gabber en couches :
  <https://forum.renoise.com/t/making-gabber-kicks-and-making-them-not-take-over-your-mix/44325> `[V]`
- Ableton, *Sara Landry high-end hard techno* (kick en premier,
  distorsion multi-étages) :
  <https://www.ableton.com/en/blog/sara-landry-high-end-hard-techno/> `[V]`
- Aucune source écrite sur le bouncy 2022+ : passe `rhythm_signature` du
  hub (« Grabs du lot 3 »).

## Liens

[[_index]] · [[../../doctrine]] §3, §9, §11 · [[../sampling-resampling]]
· [[../amp-overdrive-bitreduction]] · [[../parameter-preset-locks]] ·
[[../page-setup]] · [[../patterns-chaines]] · [[../fill-conditions]] ·
[[../kick-mental-vst]] · KT1 [[kt-cellules-rythmiques]] · KT4
[[kt-halftime-passerelles]] · KT5 [[kt-tonalite-du-grave]] · KT8
[[kt-accords-voicings]] · KT10 [[kt-style-tribe]] · KT19 (trance, à
rédiger)
