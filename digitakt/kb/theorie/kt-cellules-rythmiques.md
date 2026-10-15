---
tags: [digitakt, kb, theorie, kt]
theme: Cellules rythmiques
lot: 1
ordre: 1
styles: [tribe, acidcore, tekno, electro]
statut: draft
updated: 2026-10-15
---

# KT1 — Cellules rythmiques

**En une phrase** : une poignée de cellules de 8 ou 16 pas (tresillo,
cinquillo, claves, hémiole) suffit à construire tout l'ornement d'un
pattern tribe ; l'algorithme euclidien les engendre, la rotation les
déplace, et le choix de la cellule décide si le motif pousse vers le temps
ou s'en écarte.

## Signature

Patterns théoriques (16 pas = 1 mesure 4/4 en doubles croches) et, en
regard, le pattern moyen de la passe `rhythm_signature` du hub
([[_index]], sortie du 2026-10-15, 7 à 8 morceaux par style).

| Élément | Théorique | Mesuré (moyenne) | Lecture |
|---|---|---|---|
| Kick tribe / acid (sub) | `X...X...X...X...` | tribe `Xxx.X.x.Xx..Xxxx`, acid `X.xxX.x.X.x.X.x.` | four-on-floor ; la basse en contretemps de croche (`..x.`) descend sous 200 Hz et apparaît dans le sub |
| Ornement (mid) | tresillo `x..x..x.` par demi-mesure | acid `X.xXx.xxX.xxX.xx`, tekno `Xx.XXxxXX.xXX.xX` | les pas 4, 8, 12, 16 (le « a » qui précède chaque temps) ressortent dans les trois styles |
| Hats (high) | `x.x.x.x.x.x.x.x.` | tribe `Xx.Xx.xxXx.xX.xx` | croches, et une anticipation sur le « a » |

Tempo : tribe 160-180, acid core 170-200, tekno 150-185 (fourchettes de
[[../../veille-theorie]] §B). Les patterns mesurés sont repliés sur 16 pas,
la phase du premier temps n'est pas garantie : lire les *motifs*, pas la
position absolue.

## Vocabulaire

- **Cellule** : motif court (4, 8 ou 16 pas) répété ou tourné pour
  fabriquer une ligne ; on en combine deux ou trois, rarement plus.
- **Tresillo** `x..x..x.` (3+3+2) : trois coups sur 8 pas, le dernier
  intervalle plus court ; base du dembow, des kicks breakbeat et de la
  basse galop.
- **Cinquillo** `x.xx.xx.` : cinq coups sur 8 pas, le tresillo auquel on
  ajoute les deux pas qui suivent les coups 2 et 3.
- **Clave son 3-2** `x..x..x...x.x...` : tresillo sur la première
  demi-mesure, deux coups sur la seconde ; **clave rumba**
  `x..x...x..x.x...` : le troisième coup recule d'un pas.
- **2-3** : la clave jouée à partir de sa seconde moitié
  (`..x.x...x..x..x.`) ; même cellule, rotation de 8 pas.
- **Hémiole** : 3 contre 2 sur un même cycle, `x.x.x.` contre `x..x..` sur
  6 pas ; en 12 pas, trois coups de 4 contre quatre coups de 3.
- **E(k, n)** (Toussaint, Bjorklund) : k coups répartis le plus
  régulièrement possible sur n pas ; E(3, 8) = tresillo, E(5, 8) =
  cinquillo.
- **Rotation** : décaler la cellule de r pas sur son cycle sans changer
  ses intervalles ; c'est elle qui transforme un 3-2 en 2-3.
- **Anticipation** (pickup) : coup placé sur le pas qui précède un temps
  (le « a ») ; il tire vers le temps au lieu de le suivre.

## Pourquoi ça marche

**Concret d'abord.** Un kick tribe en `X...X...X...X...` et des toms en
tresillo sur 8 pas : les toms tombent sur les pas 1, 4, 7 puis 9, 12, 15.
Le coup 4 précède le temps 2 d'un pas, le coup 7 tombe sur le « et » du
temps 2, le coup 12 précède le temps 4. Deux coups sur trois sont donc hors
temps, et l'un d'eux est une anticipation : c'est exactement ce que la
passe mesure sur les morceaux de référence (énergie sur les pas 4, 8, 12,
16, `swing` 0,7 à 0,95 dans le hub). Le groove tribe n'est pas un shuffle
en retard, c'est une cellule qui pousse vers le temps suivant.

**Table E(k, n)** (formes canoniques de Toussaint ; les autres formes
s'obtiennent par rotation) :

| E(k, n) | Pattern | Nom usuel | Usage DT2 |
|---|---|---|---|
| E(3, 8) | `x..x..x.` | tresillo | toms (7), basse galop (9) |
| E(5, 8) | `x.xx.xx.` | cinquillo | perc B (8) dense |
| E(3, 4) | `x.xx` | | tom court sur 4 pas |
| E(4, 7) | `x.x.x.x` | | perc sur 7 pas, polymétrie (KT2) |
| E(5, 12) | `x..x.x..x.x.` | Venda | hats sur 12 pas |
| E(5, 16) | `x..x..x..x..x...` | bossa nova | perc A sur une mesure |
| E(7, 16) | `x..x.x.x..x.x.x.` | samba | ride (4) ou perc B |
| E(9, 16) | `x.xx.x.x.xx.x.x.` | | hats « cassés » |

Correction au passage : [[../../veille-theorie]] §A1 note E(7, 16) comme
`x..x..x..x..x...`, qui ne compte que 5 coups ; c'est E(5, 16).

**Pourquoi l'euclidien sonne « traditionnel »** : répartir k coups sur n
pas au plus régulièrement donne des intervalles qui ne diffèrent que de 1
(3+3+2, jamais 4+2+2). L'oreille entend une pulsation presque régulière
contrariée une fois par cycle ; c'est la dose de tension que les claves
afro-cubaines ont fixée empiriquement (Toussaint 2005 en catalogue une
quarantaine).

**Rotation et sens de la cellule.** La même suite d'intervalles 3+3+2
tournée d'un pas (`.x..x..x`) ne contient plus de coup sur le 1 : le motif
« flotte ». Tournée de 3 pas (`x.x..x..`), elle commence par deux coups
serrés : le motif « part ». Sur la DT2 le paramètre `RO1` (fiche
[[../euclidien]]) tourne la cellule en direct ; écouter les 8 rotations
d'un tresillo vaut une leçon.

**Les deux cellules de 4 pas : contretemps et anticipation.** Avant
toute cellule de 8 ou 16 pas, un temps de four-on-floor se découpe en
quatre pas, `1 e et a`. Le kick tient le `1` ; les deux cellules les plus
courantes de la techno placent un coup sur l'une des trois autres
positions : le **contretemps** `..x.` (le « et », la place du hat ouvert
et de la basse tribe, la syncope de base) et l'**anticipation** `...x`
(le « a », la place des toms tribe et des accents acid, qui tire vers le
temps suivant). Répétées quatre fois, elles donnent `..x...x...x...x.` et
`...x...x...x...x` ; mêlées à un tresillo, elles en sont les
constituants (le tresillo contient un « a » au pas 4 et un « et » au pas
7). Le rôle des hats dans cette syncope est détaillé dans KT3.

**Hémiole** : sur une track de 6 pas (KT2 pour la polymétrie), `x.x.x.`
contre `x..x..` ; en 12 pas, hats `x...x...x...` contre perc `x..x..x..x..`.
Les deux cycles se retrouvent tous les 12 pas ; c'est la cellule de la
techno « broken » 3+3+4+3+3 (KT16) et des rolls en triolets
(`RATE` 1/12, fiche [[../microtiming-retrigs]]).

## Sur la DT2

Grille de la [[../../doctrine]] §1 : kick 1, clap 3, hat fermé 5, perc A 7,
perc B 8, basse 9. Geste euclidien : fiche [[../euclidien]].

1. **Huit rotations du tresillo (5 min).** Kick 1 en 16 pas. Track 7 en
   mode euclidien, `PL1` = 3, `LEN` = 8 (PER TRACK, fiche
   [[../page-setup]]). Tourner `RO1` de 0 à 7, une mesure chacune, en
   notant les deux rotations qui groovent et celle qui flotte. Garder la
   meilleure en la convertissant (`[FUNC]` + `EUC` off).
2. **Banque de claves (10 min).** Track 8 en 16 pas, à la main : clave
   son 3-2, puis rumba (le coup du pas 7 va au pas 8), puis 2-3 (tout
   tourné de 8 pas). Sous chacune, basse 9 en `..x...x...x...x.`. Écouter
   laquelle « répond » à la basse et laquelle se superpose à elle.
3. **Anticipation contre temps (5 min).** Hat fermé 5 en `x.x.x.x.x.x.x.x.`.
   Ajouter sur la track 7 un seul coup sur le pas 4, puis le déplacer sur
   le pas 5 (temps 2), puis sur le pas 6. Le pas 4 tire, le 5 double le
   clap, le 6 traîne. C'est le mécanisme du « a » des morceaux de
   référence.

## Pièges

- Poser le premier coup d'une cellule sur le pas 1 **et** garder le kick
  sur le 1 : la cellule double le kick et perd sa tension ; tourner d'un ou
  deux pas.
- Deux cellules euclidiennes de même longueur sur deux tracks (par exemple
  deux E(3, 8)) : sans rotation différente, elles se doublent.
- En mode euclidien, les trigs posés à la main sont cachés et la
  conversion les supprime (fiche [[../euclidien]]) ; faire la banque de
  claves à la main, pas en euclidien.
- Le repliage sur 16 pas de la passe `rhythm_signature` cale le maximum,
  pas le temps 1 : un pattern mesuré qui « commence » sur le pas 1 n'est
  pas forcément calé sur le kick.

## Ressources

- Toussaint, *The Euclidean Algorithm Generates Traditional Musical
  Rhythms* (Bridges 2005) : <https://cgm.cs.mcgill.ca/~godfried/publications/banff.pdf> `[?]`
- Wikipedia, *Euclidean rhythm* : <https://en.wikipedia.org/wiki/Euclidean_rhythm> `[V]`
- Wikipedia, *Tresillo (rhythm)* : <https://en.wikipedia.org/wiki/Tresillo_(rhythm)> `[V]`
- Wikipedia, *Clave (rhythm)* : <https://en.wikipedia.org/wiki/Clave_(rhythm)> `[V]`
- Wikipedia, *Hemiola* : <https://en.wikipedia.org/wiki/Hemiola> `[V]`
- Groove Pizza (MusEDLab) : <https://apps.musedlab.org/groovepizza/> `[?]` ;
  la géométrie d'une cellule sur un cercle de 16 pas.
- Livre : Toussaint, *The Geometry of Musical Rhythm* (CRC, 2013), catalogue
  vérifié, pas de PDF libre.

## Liens

[[_index]] · [[../euclidien]] · [[../polymetrie]] · [[../page-setup]] ·
[[../../doctrine]] §1 · [[../../veille-theorie]] §A1 · KT2
[[kt-polymetrie-polyrythmie]] · KT3 [[kt-swing-microtiming]] · patches
Tidal [[../../../technique/patches/tribe]]
