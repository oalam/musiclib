---
tags: [digitakt, kb, theorie, kt]
theme: Swing, microtiming, ghost notes, densité
lot: 1
ordre: 3
styles: [tribe, acidcore, tekno, hard techno]
statut: draft
updated: 2026-10-15
---

# KT3 — Swing, microtiming, ghost notes, densité

**En une phrase** : le groove d'une boucle droite vient de trois leviers
indépendants, le décalage temporel (swing global ou micro timing par
trig), la vélocité (accents et ghost notes) et la densité (combien de
coups, décidés par les conditions), et sur un four-on-floor c'est aux
hats que revient la syncope, le fermé qui tient la grille et l'ouvert qui
marque le contretemps ; en tribe à 190 BPM, les morceaux de
référence montrent que le levier dominant n'est pas le swing mais
l'anticipation, un coup placé sur le pas qui précède le temps.

## Signature

| Élément | Théorique | Mesuré | Lecture |
|---|---|---|---|
| Hats droits | `x.x.x.x.x.x.x.x.` | tekno high `xx.Xxx.Xx.xXx.xX` | les pas 4, 8, 12, 16 accentués : anticipation, pas retard |
| Hats shuffle 56 % | `x.x.x.x.x.x.x.x.` avec les pas pairs retardés | tribe `swing` 0,70-0,88, acid 0,76-0,95 | le « a » porte plus d'énergie que le « e » dans 13 morceaux sur 21 |
| Ghost notes | `..g...g...g...g.` à vélocité 20-40 | mid acid `X.xXx.xxX.xxX.xx` : des `x` entre les `X` | un fond faible et continu sous les accents |
| Contre-exemple | | floxytek `swing` 0,20-0,26, diuko303 0,27 | énergie sur le « e » : motifs qui suivent le temps, à écouter pour comparer |
| Hat ouvert offbeat | `..x...x...x...x.` | hard techno high `.xX.XxXxx.X.xXX.`, `sync` 0,64 | le contretemps (pas 3, 7, 11, 15) porte la syncope ; `sync` = part d'énergie hors des temps |
| Hats par style (high) | tribe croches, acid 16es, DnB continu | tribe `Xx.Xx.xxXx.xX.xx`, acid `xxxXxxxXxxxXx.xX`, dnb `XxxxxxxxxXxX.xXx` | la bande high est le pattern de hats : c'est elle qui dit le style au-dessus d'un même kick |

Rappel de la métrique du hub ([[_index]]) : `swing` = part d'énergie sur le
« a » (4e double croche de chaque temps) contre le « e » (2e) ; 0,5 =
équilibré, plus de 0,5 = le coup qui précède le temps domine. Ce n'est
**pas** le pourcentage de swing de la machine.

## Vocabulaire

- **Swing (machine)** : retard appliqué aux pas pairs du pattern,
  exprimé en pourcentage de la croche ; DT2 de 50 % (droit) à 80 %
  (`[TEMPO]`, knob D, manuel §7.3).
- **Binaire / ternaire** : croche coupée en 2 (50 %) ou en 3 (66 %, le
  « e » recule jusqu'au troisième triolet).
- **Shuffle** : swing léger à moyen (54-60 %) sur les hats seuls.
- **Micro timing** : décalage d'un seul trig avant ou après son pas, en
  ticks, stocké dans le pattern (manuel §10.4 ; fiche
  [[../microtiming-retrigs]]).
- **Anticipation** (pickup) : coup posé sur le pas qui précède le temps ;
  il crée la poussée sans décaler quoi que ce soit (KT1).
- **Syncope** : accent sur une position faible (le « et », le « a »)
  alors que la position forte (le temps) reste vide ou plus faible ; la
  métrique `sync` du hub mesure la part d'énergie hors des temps.
- **Contretemps** (offbeat) : la syncope la plus simple, un coup sur le
  « et » de chaque temps (`..x.`) ; c'est la place du hat ouvert et de la
  basse tribe.
- **Hat fermé / hat ouvert** : le fermé (5) tient la grille en croches ou
  doubles croches, l'ouvert (6) marque le contretemps et se coupe au hat
  fermé suivant (choke) ; un seul ouvert bien placé vaut un empilement
  (doctrine §1).
- **Accent** : trig à vélocité pleine, souvent doublé d'une ouverture de
  filtre ; **ghost note** : trig à vélocité faible qui texture sans
  marquer.
- **Densité rythmique** : nombre de coups par mesure ; **densité
  spectrale** : énergie répartie dans le spectre ; l'énergie perçue dépend
  des deux.
- **Condition de trig** : règle qui décide si un trig joue (`PROB`, `A:B`,
  `FILL`, `PRE`, `NEI`) ; c'est un réglage de densité dans le temps
  (fiche [[../fill-conditions]]).
- **Humanisation** : petites variations de timing et de vélocité qui
  évitent la répétition exacte ; Danielsen montre qu'au-delà des
  millisecondes, le **timbre de l'attaque** porte autant le feel.

## Pourquoi ça marche

**Le swing en millisecondes, concret d'abord.** À 190 BPM, 1 pas =
60 / 190 / 4 = 0,0789 s = 78,9 ms et une croche = 157,9 ms. Le
pourcentage de swing place le second pas de chaque croche à s % de la
croche ; le retard par rapport au droit vaut (s − 50) / 100 × 157,9 ms :

| Swing | Retard du pas pair à 190 BPM | Retard à 130 BPM (croche = 230,8 ms) | Sensation |
|---|---|---|---|
| 50 % | 0 ms | 0 ms | droit |
| 54 % | 0,04 × 157,9 = 6,3 ms | 0,04 × 230,8 = 9,2 ms | à peine, « vivant » |
| 58 % | 0,08 × 157,9 = 12,6 ms | 0,08 × 230,8 = 18,5 ms | shuffle net |
| 66 % | 0,16 × 157,9 = 25,3 ms | 0,16 × 230,8 = 36,9 ms | ternaire |
| 80 % | 0,30 × 157,9 = 47,4 ms | 0,30 × 230,8 = 69,2 ms | presque sur le pas suivant |

Lecture : un même pourcentage pèse deux fois moins de millisecondes à
190 qu'à 130. C'est pourquoi le shuffle house (58-62 %) devient flou en
tekno rapide : à 190 BPM, le 58 % ne représente que 12,6 ms, trop peu
pour être entendu comme un ternaire, assez pour brouiller les hats. Les
fiches et la veille convergent sur 50-56 % pour le tribe.

**Conventions de pourcentage.** MPC, Logic et la DT2 : 50 % = droit.
Cubase, FL Studio : 0 % = droit. Roger Linn (MPC) a fixé la convention du
pourcentage de la croche ; la DT2 l'applique à tous les pas pairs du
pattern, kick compris (voir Pièges).

**Micro timing** : un trig à la fois, avant ou après le pas. Plage
affichée −23 / +23 ticks sur la DT2 (à vérifier sur la machine ; si un pas
vaut 24 ticks, 1 tick à 190 BPM = 78,9 / 24 = 3,3 ms). Usages : hats en
léger retard (+2 à +4 ticks, soit 6 à 13 ms) qui « tirent » ; une perc en
avance (−3 ticks) qui pousse ; un clap en retard de +6 ticks (20 ms) pour
un « layback ». Danielsen (*Presence and Pleasure*, sur James Brown et
D'Angelo) : l'oreille lit des écarts de 5 à 20 ms comme du feel, pas comme
des erreurs, à condition que la référence (kick, snare) reste stable.

**Ce que disent les morceaux de référence.** La passe `rhythm_signature`
du hub donne un `swing` de 0,70 à 0,95 pour 13 des 21 morceaux tribe, acid
core et tekno : l'énergie de l'ornement tombe sur le « a », le pas qui
précède le temps. Avec un swing machine, l'énergie reculerait vers le
« e » retardé et la métrique descendrait sous 0,5. Les morceaux font donc
l'inverse d'un shuffle : ils **anticipent**. C'est le tresillo de KT1 (un
coup sur le pas 4) et la basse en contretemps ; en tekno rapide, le groove
est une question de **placement de trigs**, pas de pourcentage. Les
contre-exemples (Floxytek à 0,20-0,26) montrent le motif inverse, une
énergie sur le « e », donc un feel qui suit le temps : à écouter côte à
côte avec Nailik (0,95) pour entendre la différence.

**Vélocité : accents et ghosts.** Un pattern de hats à 16 pas joué à
vélocité égale est une machine à coudre ; le même pattern avec les pas 1,
5, 9, 13 à 100, les pas 3, 7, 11, 15 à 70 et le reste à 30 devient une
ligne. Sur la DT2 la vélocité est un paramètre de trig (`VEL`, page TRIG
1), lockable par trig, et le preset peut router la vélocité vers le filtre
ou le volume : un accent est alors plus brillant, pas seulement plus
fort. Les ghost notes de clap (vélocité 20-35 sur les pas 4 et 12 autour
du backbeat, KT4) donnent le feel « drum and bass » sans changer un seul
placement.

**Les hats : la syncope habite le haut du spectre.** Sur un
four-on-floor, le kick occupe les temps ; tout ce qui syncope doit donc
vivre entre les temps et au-dessus du grave, et c'est le rôle des hats.
Trois couches, trois fonctions :

| Couche | Pattern | Fonction | Track |
|---|---|---|---|
| Hat fermé en doubles croches | `xxxxxxxxxxxxxxxx` à vélocités variées | la **grille** : rend audibles les 16 pas, donc rend lisibles les syncopes des autres tracks | 5 |
| Hat fermé en croches | `x.x.x.x.x.x.x.x.` | la grille allégée ; le « e » et le « a » restent vides, donc disponibles | 5 |
| Hat ouvert au contretemps | `..x...x...x...x.` | la **syncope de base** : un coup sur chaque « et », le balancier ; il se coupe au hat fermé suivant | 6 |
| Hat ou ride sur le « a » | `...x...x...x...x` | l'**anticipation** : tire vers le temps suivant (tribe, acid) | 5 ou 4 |
| Ride | croches ou noires | couleur de plein régime, sort en breakdown (doctrine §1) | 4 |

Le contretemps `..x.` est la syncope la plus simple : l'oreille tient le
temps grâce au kick, le hat ouvert tombe exactement à l'opposé, et
l'alternance kick-hat fait le balancement house et techno. Déplacer ce
hat d'un pas en arrière (sur le « a », `...x`) change le balancement en
poussée : c'est toute la différence entre un groove qui suit (Beauz, hat sur
le « et », `swing` 0,37) et un groove qui précède (tribe, coups sur le
« a », `swing` 0,70-0,88) ; les deux existent en hard techno (KT13). Avec un même kick, le pattern de
hats décide du style : la bande high mesurée du hub est la plus
différente d'un style à l'autre (tribe `Xx.Xx.xxXx.xX.xx` en croches
avec le « a », acid `xxxXxxxXxxxXx.xX` en doubles croches accentuées sur
le « a », DnB `XxxxxxxxxXxX.xXx` presque continu).

Deux règles pour la DT2 : le hat fermé en doubles croches n'est pas plat,
ses vélocités dessinent la syncope (exercice 3 : 100 / 30 / 70 / 30 ou
100 / 30 / 30 / 70 selon que l'accent va sur le « et » ou le « a ») ; et
le hat ouvert est **un** trig par temps au plus, coupé par le fermé
(choke, même voix ou AMP courte), sinon le haut du spectre se bouche et
la syncope disparaît dans la masse. La syncope se mesure dans le hub
par `sync` : 0,35 à 0,52 en tribe (peu d'énergie hors temps, la syncope
est dans les toms), 0,50 à 0,64 en hard techno (rumble et shaker entre
les temps), 0,64 à 0,71 en frenchcore, 0,52 à 0,70 en DnB (le kick lui-même syncope, KT4).

**Densité comme levier de tension.** La veille et la doctrine §6 le
disent : retrancher crée autant d'énergie qu'ajouter. Les conditions
rendent la densité **variable dans le temps** sans changer de pattern :
`PROB` 60 % sur une perc ghost (la boucle ne se répète jamais tout à
fait), `1:4` sur un hat ouvert (une mesure sur quatre), `FILL` sur un roll
(densité maximale à la demande), `A:B` en appel / réponse entre deux
tracks (KT9). Un retrig (fiche [[../microtiming-retrigs]]) est une pointe
de densité sur un seul pas. La densité spectrale compte autant : retirer
le ride (4) et le hat ouvert (6) vide le haut du spectre, l'énergie
perçue chute même si le nombre de coups est identique.

## Sur la DT2

Grille de la [[../../doctrine]] §1 : kick 1, clap 3, hat fermé 5, hat
ouvert 6, perc A 7, perc B 8.

1. **Seuil du swing à 190 (5 min).** Kick 1, clap 3 sur 5 et 13, hat
   fermé 5 en 16 pas à vélocité égale. `[TEMPO]`, knob D : 50, 54, 58, 66,
   8 mesures chacun. Noter le pourcentage où le hat « vit » et celui où il
   se brouille. Refaire à 130 BPM : les seuils montent.
2. **Swing contre anticipation (10 min).** Même boucle, swing à 50.
   Variante A : micro timing +3 ticks sur les hats des pas pairs (fiche
   [[../microtiming-retrigs]]). Variante B : micro timing à 0, mais perc A
   7 avec un coup sur les pas 4, 8, 12, 16 à vélocité 60. A tire, B
   pousse. B est le groove des morceaux de référence.
3. **Vélocité seule (5 min).** Hat fermé 5, 16 pas, `VEL` 100 sur 1, 5,
   9, 13, `VEL` 70 sur 3, 7, 11, 15, `VEL` 30 ailleurs (locks par trig).
   Puis `PROB` 60 % sur les trigs à 30 (fiche [[../fill-conditions]]).
   Sans aucun swing, la boucle respire.
4. **Le hat ouvert décide du style (5 min).** Kick 1, hat fermé 5 en
   croches. Hat ouvert 6 sur 3, 7, 11, 15 (le « et ») : balancement
   techno. Le déplacer sur 4, 8, 12, 16 (le « a ») : poussée tribe. Le
   mettre sur les deux : bouché. Puis un seul hat ouvert par mesure, sur
   le pas 15 seulement : la syncope devient un turnaround (KT9). AMP du
   hat ouvert courte pour qu'il se coupe au fermé suivant.

## Pièges

- Le swing du pattern s'applique à **toutes** les tracks, kick et rumble
  compris : sur une boucle four-on-floor, les pas pairs du kick ne jouent
  pas, donc le kick ne bouge pas ; mais une basse en `..x.` sur les pas
  pairs recule avec les hats. Vérifier à chaque changement de swing.
- Kick et rumble : jamais de micro timing, ils sont la référence (fiche
  [[../microtiming-retrigs]]). Un micro timing sur le clap est un choix de
  feel ; sur le kick, une erreur.
- La quantize de l'enregistrement live recale aussi le micro timing (fiche
  [[../enregistrement-quantize]]).
- `VFAD` d'un retrig part du `VEL` du trig : un ghost en retrig s'éteint
  avant la fin.
- La métrique `swing` du hub et le pourcentage de la machine sont deux
  choses : la première décrit l'énergie du « a », la seconde retarde le
  « e ».

## Ressources

- Attack Magazine, *DAW & Drum Machine Swing* (Passing Notes) :
  <https://www.attackmagazine.com/technique/passing-notes/daw-drum-machine-swing/> `[V]`
  (swing de Roger Linn, conventions de pourcentage).
- Elektronauts, *Digitakt unofficial guide* :
  <https://www.elektronauts.com/t/digitakt-unofficial-guide/40705> `[V]`
  (conditions, humanisation).
- Manuel DT2 OS 1.17, §7.3 (swing 51-80 %), §10.4 (micro timing), §10.5
  (retrigs), §11.2 (TRIG PAGE 1, `VEL`, `PROB`, `COND`).
- Livre : Danielsen, *Presence and Pleasure: The Funk Grooves of James
  Brown and Parliament* (Wesleyan UP, 2006) ; catalogue vérifié.
- Livre : Butler, *Unlocking the Groove* (Indiana UP, 2006).

## Liens

[[_index]] · [[../microtiming-retrigs]] · [[../fill-conditions]] ·
[[../enregistrement-quantize]] · [[../tempo-metronome]] · [[../../doctrine]]
§1, §6 · KT1 [[kt-cellules-rythmiques]] · KT4 [[kt-halftime-passerelles]]
· KT9 (phrasage, à rédiger) · [[../../../scripts/README|rhythm_signature.py]]
