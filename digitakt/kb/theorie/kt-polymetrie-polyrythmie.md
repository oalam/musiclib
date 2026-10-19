---
tags: [digitakt, kb, theorie, kt]
theme: Polymétrie, polyrythmie, dissonance métrique
lot: 1
ordre: 2
styles: [tribe, acidcore, hypnotique, hard techno]
statut: draft
updated: 2026-10-16
---

# KT2 — Polymétrie, polyrythmie, dissonance métrique

**En une phrase** : la polymétrie superpose des cycles de longueurs
différentes qui ne se réalignent qu'au ppcm, la polyrythmie superpose des
subdivisions différentes d'un même cycle, et les deux produisent la même
chose pour la salle : une pulsation stable que quelque chose contrarie à
intervalle régulier, ce que Krebs et Butler appellent la dissonance
métrique.

## Signature

| Élément | Théorique | Mesuré | Lecture |
|---|---|---|---|
| Repères | kick `X...X...X...X...`, clap `....X.......X...` | acid sub `X.xxX.x.X.x.X.x.` | four-on-floor dans tous les styles cœur |
| Ornement polymétrique | perc A en 6 pas `x..x.x`, perc B en 7 pas `x.x.x.x` | invisible dans le repliage | le repliage sur 16 pas moyenne un cycle de 7 pas sur 7 mesures : il ne reste qu'un fond `x` uniforme |
| Polyrythmie 3:4 | hats sur 12 pas `x...x...x...` | tribe high `Xx.Xx.xxXx.xX.xx` | les pas 1-2, 4-5 et 9-10, 12-13 par paires évoquent un cycle de 3 pas, à confirmer à l'oreille |

Les morceaux de référence ([[_index]], passe du 2026-10-15) ont tous une
`pulse_clarity` de 0,90 à 0,95 : la pulsation reste franche, la
polymétrie ne la brouille pas. C'est la règle : repères droits, ornements
impairs (fiche [[../polymetrie]]).

## Vocabulaire

- **Polymétrie** : deux cycles de longueurs différentes (16 pas et 12 pas)
  à la même vitesse de pas ; ils dérivent et se retrouvent au ppcm.
- **Polyrythmie** : deux subdivisions différentes du même cycle (3 coups
  et 4 coups dans une mesure) ; elles se retrouvent à chaque cycle.
- **ppcm** : plus petit commun multiple des longueurs ; le nombre de pas
  avant que tout retombe ensemble.
- **Cycle premier** : longueur sans diviseur commun avec 16 (3, 5, 7, 9,
  11, 13, 15) ; le ppcm est alors le produit, et le motif met N mesures à
  revenir.
- **Dissonance métrique** (Krebs) : conflit entre la pulsation de
  référence et une couche qui la contredit ; Butler l'applique à l'EDM.
- **Dissonance de groupement** : la couche a une période différente
  (3 pas contre 4) ; notée G3/4.
- **Dissonance de déplacement** : la couche a la même période mais
  décalée (un motif de 4 pas commencé sur le pas 2) ; notée D+1.
- **Réalignement** : le pas où tous les cycles retombent ensemble ; en
  live, le `RESET` du pattern le force (fiche [[../polymetrie]]).
- **Quasi-polyrythmie** : une cellule euclidienne qui approche une
  subdivision impossible sur la grille (E(3, 8) comme 3 contre 2).

## Pourquoi ça marche

**Concret d'abord.** Kick en 16 pas, perc A en 12 pas avec deux toms
`x..x.x......`. Les toms reviennent sur le kick tous les ppcm(12, 16)
pas : 12 = 2² × 3, 16 = 2⁴, ppcm = 2⁴ × 3 = 48 pas = 3 mesures. Pendant
ces 3 mesures les toms tombent une fois sur le temps, une fois sur le
« et », une fois sur le « a » : trois sensations différentes avec un seul
motif. À 190 BPM, 1 pas = 60 / 190 / 4 = 0,0789 s, donc 48 pas = 3,79 s.

**Table des cycles contre 16 pas** (vitesse de pas identique) :

| Longueur | ppcm avec 16 | Mesures | Durée à 190 BPM | Effet |
|---|---|---|---|---|
| 12 | 48 | 3 | 48 × 0,0789 = 3,8 s | balancement ternaire |
| 6 | 48 | 3 | 3,8 s | tresillo qui tourne |
| 10 | 80 | 5 | 80 × 0,0789 = 6,3 s | motif qui recule de 6 pas par mesure |
| 5 | 80 | 5 | 6,3 s | perc qui avance d'un pas par mesure |
| 14 | 112 | 7 | 112 × 0,0789 = 8,8 s | mélodie qui se décale lentement |
| 7 | 112 | 7 | 8,8 s | ne se répète presque jamais |
| 9 | 144 | 9 | 144 × 0,0789 = 11,4 s | idem, plus lent |
| 15 | 240 | 15 | 240 × 0,0789 = 18,9 s | une double croche de retard par mesure |
| 3, 5, 7 ensemble | 105 | 6,6 | 105 × 0,0789 = 8,3 s | texture vivante, à petite dose |

Lecture : une longueur **paire** (6, 10, 12, 14) partage un facteur 2 avec
16 et revient vite ; une longueur **impaire** revient en N mesures. Le
15 est le cas limite utile : le motif glisse d'un pas par mesure, l'acid
line en 15 pas de [[../../veille-theorie]] §B2 (KT11) exploite exactement
cela.

**Le motif 3 / 5 / 7 (Bonas Buden, « 3-5-7 Polymeter », Digitakt, 2021).**
Vidéo sans voix, analysée image par image et par autocorrélation des
attaques par bande (2026-10-16) ; la page SCALE n'apparaît jamais à
l'écran, les longueurs viennent de l'écoute et de la mesure.

- **Trois tracks à longueurs premières entre elles**, une par registre :
  basse en 3 pas, médium en 5 pas, aigu en 7 pas, master à 16 (ou `INF`),
  un ou deux trigs par track. C'est le cas « 3, 5, 7 ensemble » de la
  table, mais sans repère droit : rien n'est en 16, c'est la version
  pure du motif.
- **Il ne touche plus au séquenceur.** Toute la démo se joue sur la page
  mixer (niveaux de track), en mute mode (pads, 2:30 à 3:10) et sur une
  page de timbre (4:05) : une boucle qui vit seule, lui dose ce qu'on en
  entend. Sa description le dit : la polymétrie est triviale sur Digitakt,
  la polyrythmie vraie ne s'obtient que par retrigs et micro-timing.
- **Mesuré** : pas de 16e de 0,1224 s, soit 60 / (4 × 0,1224) = 122,5
  BPM. Bande 150-600 Hz : période de 3 pas (la basse). Bande 600-2500 Hz :
  périodes de 3,5, 7, 14, 21 et 35 pas (l'élément en 7, deux coups
  dedans). Bande grave : période la plus nette à 21 pas = 3 × 7, le
  croisement des deux. Le 5 n'est pas isolé par les bandes, il est tenu
  par l'écoute seule.
- **Arithmétique** : les trois tracks se réalignent au ppcm(3, 5, 7) = 105
  pas = 105 / 16 = 6,56 mesures ; avec le master à 16, tout retombe au
  ppcm(16, 105) = 1680 pas = 105 mesures, soit 1680 × 0,1224 = 205,6 s à
  122,5 BPM, presque la durée de la vidéo. La corrélation à 105 pas ne
  vaut que 0,06 : le réalignement complet est inaudible, il n'y a pas de
  « résolution » au sens de Butler, seulement une texture.
- **Transposition au terrain** : à 190 BPM, 105 pas = 105 × 0,0789 = 8,3 s
  et 1680 pas = 132,6 s. La basse en 3 flotte, recevable à 122 mais elle
  retire le grave du kick en free party (Pièges) ; garder kick, rumble et
  basse en 16 et réserver 3 / 5 / 7 à deux tracks d'ornement, c'est la
  règle de dose ci-dessous.

**Polyrythmie sur la grille.** La grille de 16 pas ne contient pas 3
coups égaux par mesure (16 / 3 = 5,33 pas). Trois voies sur la DT2 :

1. changer la vitesse de la track (`SPEED` 3/4X ou 3/2X, fiche
   [[../page-setup]]) : une track à 3/4X joue 12 pas pendant que le kick
   en joue 16, donc 3 coups de 4 pas contre 4 temps ;
2. les retrigs en triolets (`RATE` 1/12, 1/24, fiche
   [[../microtiming-retrigs]]) : la polyrythmie vit à l'intérieur d'un
   seul trig ;
3. la quasi-polyrythmie euclidienne : E(3, 8) `x..x..x.` approche 3 contre
   2 (coups aux pas 1, 4, 7 au lieu de 1, 3,67, 6,33) ; l'oreille accepte
   l'arrondi, et c'est le tresillo (KT1).

**Dissonance métrique, la grille de lecture de Butler.** Le groove n'est
pas « du désordre » mais un conflit mesurable entre la pulsation et une
couche. Deux familles :

- **groupement** G3/4 : une track de 3 pas (ou un E(3, 8), ou un delay
  pointé 3/16) contre un kick en 4 ; c'est la polymétrie et la polyrythmie
  vues plus haut ;
- **déplacement** D+1 : le même motif que le kick, décalé d'un pas ; sur la
  DT2 c'est la basse en contretemps (`..x.` contre `x...`, D+2) ou une
  perc copiée du kick et tournée d'un pas (D+1).

Butler montre que la techno installe la pulsation d'abord, puis ajoute une
dissonance, puis la **résout** (retour du kick, réalignement sur le 1 d'une
phrase) : la tension vient du conflit, le soulagement du réalignement.
Les mutes (doctrine §4) et le `RESET` sont les outils de cette résolution.

**La règle de dose** : une seule couche dissonante à la fois, pendant au
moins 8 mesures, pour que la salle l'entende comme une intention et non
comme une erreur. Deux couches impaires simultanées sur des cycles
premiers entre eux (5 et 7) se retrouvent tous les 35 pas, hors de toute
phrase : réservé aux textures (track 11) ou à Id2 à faible niveau.

## Sur la DT2

Grille de la [[../../doctrine]] §1 ; geste : fiche [[../polymetrie]]
(PER TRACK, longueur, `RESET`).

1. **Entendre le ppcm (5 min).** Kick 1 en 16, perc 4 en 12 pas avec
   `x..x.x......`, `RESET` à `INF`. Compter les mesures jusqu'au retour des
   toms sur le temps : 3. Passer la track 4 à 7 pas avec `x.x.x.x` : 7
   mesures. Passer à 15 pas : chaque mesure, les toms reculent d'un pas ;
   noter la mesure où ça « bascule » à l'oreille.
2. **Groupement contre déplacement (10 min).** Kick 1 en 16. Track 5 (Id1) :
   copier le pattern du kick (fiche [[../copier-coller]]) et le reposer
   décalé d'un pas (D+1), écouter 8 mesures ; puis reposer le même motif
   en 3 pas `x..` (G3/4), 8 mesures. Le premier donne un flam qui
   « traîne », le second une perc qui tourne. Muter l'un puis l'autre sur
   le 1 d'une phrase : le soulagement est le même.
3. **Polyrythmie 3 contre 4 (5 min).** Hat fermé 6 en 16 pas
   `x...x...x...x...`. Passer la track 6 à `SPEED` 3/4X : trois hats par
   mesure contre quatre kicks, puis revenir à 1X avec un E(3, 8) sur le
   même hat (fiche [[../euclidien]]). Comparer la polyrythmie exacte et la
   quasi-polyrythmie ; garder celle qui tient à 190.
4. **Le motif 3 / 5 / 7 (10 min).** Kick 1 en 16 avec le rumble. Track 4
   (perc grave) en 3 pas `x..`, track 5 (perc médium, Id1) en 5 pas `x....`,
   track 7 (hat ouvert ou métal) en 7 pas `x..x...`, `RESET` à `INF`. Jouer la
   boucle à la page mixer uniquement : monter une track, en couper une
   autre au mute, sans toucher aux trigs, 2 minutes. Puis couper le kick
   8 mesures et le ramener sur le 1 d'une phrase : c'est la résolution que
   Bonas Buden ne fait jamais, et la différence entre texture et groove.

## Pièges

- `A:B` compte les tours de la **track** : une perc en 12 pas en `1:4`
  joue tous les 48 pas, pas toutes les 4 mesures (fiche
  [[../fill-conditions]]).
- `RESET` à 64 force le réalignement à chaque phrase de 4 mesures : un
  cycle de 7 pas n'ira jamais au bout de ses 7 mesures ; choisir entre
  « cycle complet » (`INF`) et « phrases propres » (64 ou 128).
- `SPEED` 3/4X change aussi la vitesse des LFO calés sur le tempo (fiche
  [[../page-setup]]).
- Kick, rumble, clap et basse restent en 16 : une basse en 15 pas met le
  grave hors du kick une mesure sur deux, ce que le compresseur master ne
  rattrape pas (doctrine §9).
- Le repliage de la passe `rhythm_signature` sur 16 pas ne voit pas la
  polymétrie : son absence dans les tables du hub ne prouve rien.

## Ressources

- Butler, *Unlocking the Groove* (Indiana UP, 2006), chapitres sur la
  dissonance métrique et la forme comme processus ; catalogue vérifié,
  pas de PDF libre.
- London, *Hearing in Time* (OUP, 2004 / 2012) : la perception de la
  métrique comme attente ; catalogue.
- Attack Magazine, *Polyrhythms* (Passing Notes) :
  <https://www.attackmagazine.com/technique/passing-notes/polyrhythms/> `[V]`
- Ableton, *New Horizons in Music: Polyrhythms* (Loop 2017) :
  <https://www.ableton.com/en/blog/new-horizons-music-polyrhythms> `[V]`
- Wikipedia, *Hemiola* : <https://en.wikipedia.org/wiki/Hemiola> `[V]`
- Bonas Buden, *3-5-7 Polymeter - Digitakt* (2021, 4:50, sans voix) :
  <https://www.youtube.com/watch?v=qQF71MdaQ-Y> `[V]` ; analysé par images
  et autocorrélation, voir le motif 3 / 5 / 7 ci-dessus.
- Production Music Live, *hypnotic polymetric lead* :
  <https://productionmusiclive.com/blogs/news/hypnotic-polymetric-lead-in-analog-melodic-techno-ableton-tutorial> `[V]`

## Liens

[[_index]] · [[../polymetrie]] · [[../euclidien]] · [[../page-setup]] ·
[[../fill-conditions]] · [[../microtiming-retrigs]] · [[../../doctrine]]
§1, §4, §12 · KT1 [[kt-cellules-rythmiques]] · KT3
[[kt-swing-microtiming]] · KT15 (hypnotique, à rédiger)
