---
tags: [digitakt, kb, theorie, kt]
theme: Basses, rythmes et rôles
lot: 1
ordre: 21
styles: [tribe, acidcore, frenchcore, hard techno, dnb, dubstep]
statut: draft
updated: 2026-10-15
---

# KT21 — Basses : rythmes et rôles

**En une phrase** : la basse en contretemps est le réglage par défaut du
tribe (doctrine §9), pas une limite ; la seule contrainte réelle est de
ne pas occuper le pas du kick sans ducking, ce qui laisse douze pas sur
seize et une dizaine de rythmes de basse qui, à eux seuls, changent de
style, tandis que la note de la basse, elle, reste la tonique ou sa
quinte (KT5).

## Signature

Bande sub (20-200 Hz) de la passe `rhythm_signature` du hub
([[_index]]) : le kick y est, et la basse quand elle descend sous 200 Hz.
Lire ce qui reste **entre** les `X` du kick.

| Style | Rythme de basse théorique | Mesuré (sub) | Lecture |
|---|---|---|---|
| Tekno rapide | contretemps de croche `..x.` | moyenne `X.x.X.x.X.x.X.x.` | le cas d'école : kick sur le temps, basse sur le « et », rien d'autre |
| Acid core | contretemps ou kickbass seul | moyenne `X.xxX.x.X.x.X.x.` ; Nailik, KTC, Berio `X...X...X...X...` | moitié contretemps, moitié rien (le kickbass tient le grave, KT11) |
| Tribe | contretemps, rumble entre les kicks | moyenne `Xxx.X.x.Xx..Xxxx` ; Floxytek `XXx.XXx.` | sub plein sur les pas 2-3 : rumble et basse se relaient, plus le rebond du kick (KT10) |
| Frenchcore | `.xxx` après chaque kick | Sefa `X.xXX.xXx.xXx..X` | les pas 3-4 remplis : la basse offbeat, le pas 2 mangé par la queue du kick |
| Hard techno | `.xxx` ou tenue, duckée | moyenne `Xx.xx.x.X..xXx.x` ; Beauz `.XxxxxxXxx..xXx.` | sub presque continu : la pression, basse et rumble tenus sous le kick |
| Hardcore, bouncy | galop `x..xx..x` | Mad Dog `xxX..xX..xX..XX.` | cellule `x..` enchaînée dans le sub : le galop |
| DnB | sub tenue, kick cassé | moyenne `Xxx..xxxx.x...xX` | le sub ne suit pas le kick : note tenue sous un break syncopé |
| Dubstep | sub tenue, wobble | moyenne `X...Xx..Xxx.X...` | un ou deux appuis par mesure, le reste est la queue |

Lecture : les styles se distinguent au moins autant par le rythme de la
basse que par les hats (KT20). Quatre familles : contretemps (tekno,
tribe), remplissage (`.xxx`, frenchcore, trance, hard techno), galop
(bouncy), tenue (DnB, dubstep, dub) ; et l'absence (kickbass mental).

## Vocabulaire

- **Contretemps** (offbeat) : basse sur le « et » de chaque temps,
  `..x.` ; entre les kicks, jamais dessus.
- **Rolling bass** / **offbeat bassline** : `.xxx`, trois doubles
  croches après chaque kick ; trance à 140, frenchcore à 200 (KT4,
  KT12).
- **Galop** : `x..xx..x`, deux coups serrés puis un vide ; bouncy, hard
  bounce (KT1, KT12).
- **Basse tenue** (sustained sub) : une note qui dure une ou deux
  mesures sous un kick cassé ; DnB, dubstep, dub.
- **Kickbass** : le kick joue la basse, la track 9 reste vide (KT5,
  KT11).
- **Reese** : deux dents de scie désaccordées, basse médium de la DnB ;
  **wobble** : filtre modulé par un LFO calé sur le tempo (1/4, 1/8,
  1/8T), dubstep.
- **Gate / decay** : durée de la note ; à 190 BPM une double croche fait
  79 ms, une basse en contretemps doit retomber en 100-150 ms.
- **Ducking** (sidechain) : la basse baisse pendant le kick ; autorise
  le chevauchement que le contretemps évite (fiche
  [[../send-fx-compresseur]]).
- **Riff de basse** : motif de 2 à 4 notes sur 8 ou 16 pas qui identifie
  le morceau ; la basse comme Id (doctrine §12).
- **Appel-réponse kick / basse** : la basse répond au kick sur la
  seconde moitié de mesure ou sur la mesure paire (KT9).

## Pourquoi ça marche

**Concret d'abord : dix rythmes, une note.** Kick 1 en four-on-floor à
170 BPM, basse 9 sur la tonique (KT5), même son, decay court. Dix
patterns de 16 pas :

| # | Pattern | Nom | Sensation | Styles |
|---|---|---|---|---|
| 1 | `..x...x...x...x.` | contretemps | balancement, la basse rebondit sur le kick | tribe, tekno |
| 2 | `...x...x...x...x` | anticipation | poussée vers le temps suivant | tribe, acid |
| 3 | `..x.x.x...x.x.x.` | contretemps et « a » | plus dense, « galope » sans doublé | hardtek |
| 4 | `.xxx.xxx.xxx.xxx` | rolling | mur de son, pression | frenchcore, trance, hard techno |
| 5 | `x..xx..xx..xx..x` | galop | rebond, cheval | bouncy, hardcore |
| 6 | `..x..x..x..x..x.` | tresillo de basse | tourne, 3 contre 4 (KT2) | electro, tribe |
| 7 | `..x.....x.......` | deux appuis | aéré, la basse ponctue | techno lente, dub |
| 8 | `x_______x_______` | tenue (deux notes longues) | nappe, sub continu | DnB, dubstep |
| 9 | `..x...x.........` puis `........x...x.x.` | appel-réponse sur 2 mesures | dialogue avec le kick | tribe, hypnotique |
| 10 | `................` | absente (kickbass) | linéaire, martelé | mental |

Tous respectent la seule contrainte du grave : **pas de basse sur le pas
du kick** (pas 1, 5, 9, 13), sauf le 5 (galop) et le 8 (tenue), qui
n'existent qu'avec ducking ou avec un kick court. C'est l'exercice 1 : le
style change à chaque pattern, la note n'a pas bougé.

**Pourquoi le contretemps est le défaut, pas la règle.** La doctrine §9
arbitre « basse en contretemps » pour une raison physique (KT5) : à
180-200 BPM, un kick de 80-120 ms et une basse de 100-150 ms ne peuvent
pas cohabiter dans le sub sur le même pas sans se masquer. Le contretemps
est la façon la plus simple de séparer les deux **dans le temps**. Mais la
contrainte porte sur quatre pas sur seize ; les douze autres sont libres,
et le ducking (compresseur, `SCS` = TRK1) lève même cette contrainte en
baissant la basse pendant le kick. Le tribe en contretemps strict est une
**écriture**, choisie pour sa lisibilité en free party ; les rythmes 2, 3,
6 et 9 du tableau restent du tribe et ouvrent le groove.

**Ce que disent les morceaux.** La moyenne tekno `X.x.X.x.X.x.X.x.` est le
contretemps pur ; l'acid core est à moitié contretemps, à moitié vide
(kickbass) ; le tribe montre un sub plein sur les pas 2-3 (`Xxx.`), où se
mêlent rumble, basse et le rebond du kick (KT10). Sefa en frenchcore
(`X.xXX.xXx.xXx..X`) montre le `.xxx` à moitié : le pas 2 est mangé par
la queue du kick, les pas 3-4 ressortent. La DnB et le dubstep ont un sub
qui ne suit pas le kick : une note tenue, le kick cassé au-dessus (KT4).

**La basse comme voix rythmique.** Quand les percs sont rares (mental,
hard techno), la basse est la seule voix syncopée du grave : son rythme
**est** le groove. Trois leviers sans changer de note : la **longueur**
(un `..x.` à 80 ms claque, à 150 ms roule), la **vélocité** (accent sur
le « et » du temps 2 et 4, ghost ailleurs, KT3), les **conditions** (`PROB`
70 % sur un coup sur deux, `2:2` pour une variante une mesure sur deux,
KT9). Un riff de basse de deux notes sur 16 pas avec ces trois leviers
tient un plateau de 32 mesures.

**La basse comme voix harmonique.** La note de la basse est la tonique,
parfois la quinte (KT5), et son mouvement est le rythme harmonique du
morceau (KT8) : un pas sur la b2 toutes les 4 mesures fait phrygien
(KT6), une descente 1 → b7 → b6 sur trois phrases fait « trance ».
Changer la note de la basse est la façon la moins coûteuse de faire
bouger l'harmonie, parce que le kick reste sur la tonique et que la
basse est au-dessus de lui dans le spectre (80-250 Hz). Au-delà de deux
ou trois notes, c'est une ligne (KT7) et elle monte sur la track 10.

**Appel-réponse et silence.** Une basse qui joue la première mesure et se
tait la seconde (`1:2`), ou qui répond au kick sur les temps 3 et 4
seulement, crée une attente ; son retour est un micro-drop toutes les
deux mesures. Et couper la basse (mute de la 9) pendant 8 mesures en
gardant le kick est la soustraction la plus efficace après le kick
lui-même (doctrine §6, KT9).

## Sur la DT2

Grille de la [[../../doctrine]] §1 : kick 1, rumble 2, basse 9. Gestes :
[[../rumble-grave]] (basse en contretemps, partage des bandes),
[[../send-fx-compresseur]] (ducking), [[../keyboard-gammes]] (note),
[[../fill-conditions]], [[../parameter-preset-locks]], [[../lfo]]
(wobble).

1. **Dix rythmes, une note (15 min).** Les dix patterns du tableau, dans
   dix patterns copiés du même kick (fiche [[../copier-coller]]), basse
   9 sur la tonique, decay 120 ms. Chaîner, 8 mesures chacun. Noter les
   trois qui sonnent « tribe » et les trois qui sonnent « autre chose ».
2. **Ducking ou contretemps (5 min).** Pattern 4 (`.xxx`) puis pattern 8
   (tenue) sans ducking : bouillie. Compresseur en sidechain sur la 9
   (`SCS` = TRK1, fiche [[../send-fx-compresseur]]) : la basse respire
   sous le kick. Puis même ducking sur le pattern 1 : inutile, le
   contretemps suffit.
3. **Basse-Id (10 min).** Riff de deux notes (tonique, quinte) sur le
   pattern 3, `VEL` 110 sur les « et » des temps 2 et 4, 70 ailleurs,
   `PROB` 70 % sur les « a », `2:2` sur un coup supplémentaire au pas 16.
   Laisser tourner 32 mesures sans toucher aux percs : le groove vit sur
   la 9.

## Pièges

- Basse sur le pas du kick sans ducking : masquage et battement dans le
  sub (KT5) ; soit contretemps, soit sidechain.
- Decay trop long à 190 BPM : un `..x.` à 250 ms arrive sur le kick
  suivant ; viser 100-150 ms, la rondeur est une variation (doctrine §9).
- Basse et rumble sur les mêmes pas entre les kicks : deux fondamentales
  dans le sub ; le rumble prend les pas 2-3 ou la basse, pas les deux.
- Plus de trois notes : ce n'est plus une basse, c'est une ligne, et elle
  masque le kick ; la monter sur la 10.
- Le galop et la tenue demandent un kick court ou un ducking franc : sur
  un kickbass mental ils n'ont pas de place (track 9 vide, KT11).
- `PROB` sur la basse : jamais sur le coup qui tient la tonalité (le
  premier de la mesure), seulement sur les ghosts.

## Ressources

- Attack Magazine, Passing Notes *5 Tips To Improve Your Synth Basslines*
  (index) : <https://www.attackmagazine.com/technique/passing-notes/> `[V]`
- Attack Magazine, *How to make an acid house bassline* :
  <https://www.attackmagazine.com/technique/tutorials/how-to-make-an-acid-house-bassline/> `[V]`
- Forum Ableton, *rolling trance bass* :
  <https://forum.ableton.com/viewtopic.php?p=1083205> `[R]`
- Attack Magazine, Beat Dissected *Mystik dubstep* (sub et wobble) :
  <https://www.attackmagazine.com/technique/beat-dissected/mystik-dubstep/> `[V]`
- Manuel DT2 OS 1.17, §11.6 (AMP, decay), §12.6 (compresseur,
  sidechain), §11.2 (conditions, `PROB`).

## Liens

[[_index]] · [[../../doctrine]] §6, §9, §11, §12 · [[../rumble-grave]] ·
[[../send-fx-compresseur]] · [[../keyboard-gammes]] ·
[[../fill-conditions]] · [[../parameter-preset-locks]] · [[../lfo]] ·
[[../copier-coller]] · KT1 [[kt-cellules-rythmiques]] · KT3
[[kt-swing-microtiming]] · KT5 [[kt-tonalite-du-grave]] · KT8
[[kt-accords-voicings]] · KT9 [[kt-phrasage-tension]] · KT10
[[kt-style-tribe]] · KT11 [[kt-style-acidcore]] · KT12
[[kt-style-frenchcore]] · KT20 [[kt-hats]]
