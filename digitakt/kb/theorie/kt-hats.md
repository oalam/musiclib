---
tags: [digitakt, kb, theorie, kt]
theme: Hats, ride et haut du spectre
lot: 1
ordre: 20
styles: [tribe, acidcore, tekno, hard techno, dnb]
statut: draft
updated: 2026-10-15
---

# KT20 — Hats, ride et haut du spectre

**En une phrase** : sur un four-on-floor le kick tient les temps et le
grave, donc tout ce qui syncope et tout ce qui dit la vitesse vit dans
les hats ; le hat fermé est la grille, le hat ouvert la syncope, la ride
la couleur de plein régime, et la bande high mesurée sur les morceaux de
référence est celle qui change le plus d'un style à l'autre : au-dessus
d'un même kick, ce sont les hats qui disent le style.

## Signature

Bande high (plus de 2 kHz) de la passe `rhythm_signature` du hub
([[_index]]), moyennes par style ; convention `1 e et a` par temps, pas
1 = temps, pas 2 = « e », pas 3 = « et », pas 4 = « a ».

| Style | Théorique | Mesuré (moyenne high) | Lecture |
|---|---|---|---|
| Tribe | fermé en croches, ouvert sur le « et » | `Xx.Xx.xxXx.xX.xx` | croches (pas 1, 3) avec le « a » relevé (pas 4, 8, 12) : la grille tribe anticipe |
| Acid core / mental | fermé en 16es, accents sur le « a » | `xxxXxxxXxxxXx.xX` | 16es presque continues, accent net sur chaque « a » : le hat pousse avec l'acid |
| Tekno rapide | croches, ouvert sur le « et » | `xx.Xxx.Xx.xXx.xX` | « a » accentué, « et » creux : l'ouvert est rare, le fermé anticipe |
| Frenchcore | 16es, hoover dans le high | `xx.xxXXXxxxx..xX` | plein sauf le pas 3 : le haut est saturé par les synthés, les hats comptent peu |
| Hard techno | shaker 16es, ouvert sur le « et » | `X.XxxxXxXxxxXXXx` | presque continu avec des creux de vélocité : le shaker est le moteur |
| Schranz | roulements | `xx.X.X.Xxx.Xxx.X` | accents alternés : la percussion roule, le hat fait partie du roulement |
| DnB | hats continues, ghost | `XxxxxxxxxXxX.xXx` | continu, deux creux : le break vit dans le high autant que dans le kick |
| Dubstep | 3/16 ou croches lentes | `x..XxxxXx..Xx..x` | un coup sur deux temps : le half-time se lit aussi dans les hats (KT4) |

Lecture globale : le kick (sub) est quasi identique de tribe à hard
techno ; la bande high ne l'est jamais. C'est elle que la salle utilise
pour sentir la vitesse (16es = vite, croches = posé) et le style.

## Vocabulaire

- **Hat fermé** (closed hat, track 5) : court, 6-12 kHz, tient la grille
  en croches ou en doubles croches.
- **Hat ouvert** (open hat, track 6) : long, 5-10 kHz, marque le
  contretemps ; **choke** : coupé net par le hat fermé suivant.
- **Ride** (track 4) : cymbale continue, 4-10 kHz, couleur de plein
  régime, sort en breakdown (doctrine §1).
- **Shaker** (track 8) : doubles croches continues à vélocités
  variables ; le hat fermé du hard techno.
- **Grille** : subdivision rendue audible (croches ou 16es) ; sans grille
  les syncopes des autres tracks ne sont pas lisibles.
- **Contretemps** : le « et » (pas 3 du temps), place du hat ouvert ;
  **anticipation** : le « a » (pas 4), place de l'accent tribe (KT1, KT3).
- **Vélocité de grille** : profil de vélocité sur 4 pas (par exemple
  100 / 30 / 70 / 30) qui dessine la syncope sans ajouter de trig.
- **Densité spectrale** : énergie du haut du spectre ; retirer ride et
  hat ouvert baisse l'énergie perçue sans toucher au rythme (KT3, KT9).
- **Masquage** : hats et acid line se disputent 2-8 kHz ; l'un des deux
  doit céder (filtre, vélocité ou pas).

## Pourquoi ça marche

**Concret d'abord : trois boucles, même kick.** Kick 1 en
`X...X...X...X...` à 170 BPM. Boucle A : hat fermé 5 en croches, hat
ouvert 6 sur les pas 3, 7, 11, 15 : techno, balancement. Boucle B : hat
fermé en 16es, vélocités 100 / 30 / 30 / 70, pas d'ouvert : tribe, ça
pousse. Boucle C : shaker 8 en 16es 100 / 40 / 70 / 40, hat ouvert sur
le « et », ride 4 en croches : hard techno, pression. Rien n'a changé
sous 2 kHz. C'est l'exercice 1.

**Pourquoi la syncope habite le haut.** Un four-on-floor à 160-200 BPM
occupe les temps avec le kick et le grave avec kick, rumble et basse
(KT5). Il ne reste, pour contredire la pulsation (KT2), que les pas entre
les temps et le spectre au-dessus de 2 kHz. Les hats y sont seuls, ou
presque : ils portent la syncope **par défaut**. Le contretemps `..x.`
est la syncope la plus simple (KT1) : le kick tient le temps, le hat
ouvert tombe à l'opposé, l'alternance fait le balancement. Déplacer ce
coup sur le « a » (`...x`) transforme le balancement en poussée : c'est
le tribe, et la passe du hub le mesure (`swing` 0,70-0,88, énergie sur
le « a »).

**La grille rend les autres lisibles.** Une acid line en 15 pas (KT11),
un tom en 7 pas (KT2) ou une clave (KT1) ne se lisent que si l'oreille
a une référence de subdivision. Le hat fermé en 16es est cette référence
: il ne syncope pas, il **montre** la grille sur laquelle les autres
syncopent. D'où la règle : plus les autres tracks sont polymétriques ou
clairsemées, plus le hat fermé doit être régulier. Inversement, un hat
fermé en croches laisse les « e » et « a » vides, donc disponibles pour
les percs.

**Vélocités : la syncope sans trig supplémentaire.** Un hat en 16es à
vélocité égale est une machine à coudre (KT3). Le profil sur 4 pas
décide de la sensation :

| Profil (1 e et a) | Sensation | Style |
|---|---|---|
| 100 / 30 / 70 / 30 | balancement, accent sur le « et » | techno, house |
| 100 / 30 / 30 / 70 | poussée, accent sur le « a » | tribe, acid |
| 100 / 60 / 100 / 60 | croches marquées, 16es en fond | hard techno, shaker |
| 100 / 100 / 100 / 100 | plat, machine | à éviter sauf effet |
| 100 / 0 / 70 / 0 | croches (les 16es retirées) | tekno, tribe posé |

Sur la DT2, c'est `VEL` par trig (locks), et la vélocité routée vers le
filtre ou le volume dans le preset pour qu'un accent soit plus brillant,
pas seulement plus fort.

**Le hat ouvert : un seul, et coupé.** Le hat ouvert dure ; deux ouverts
qui se chevauchent bouchent 5-10 kHz et la syncope disparaît dans la
masse. Règle : un ouvert par temps au plus, le plus souvent un par
demi-mesure ou un par mesure (pas 15 : il devient un turnaround, KT9),
et sa queue coupée avant le fermé suivant. La DT2 n'a pas de groupe de
choke entre tracks : la coupure se fait par l'AMP du hat ouvert
(decay réglé pour mourir avant le pas suivant, fiche
[[../oneshots-synthe]]), ou en mettant fermé et ouvert **sur la même
track** (preset lock du sample ouvert sur les pas voulus, fiche
[[../parameter-preset-locks]]) : une track monophonique coupe
naturellement le son précédent. À vérifier sur la machine : le
comportement exact de la coupure en preset lock.

**Polymétrie et euclidien sur les hats.** Le hat est le meilleur
candidat à la polymétrie (KT2) : track 5 en 12 pas sur un kick en 16
donne un balancement ternaire qui se recale toutes les 3 mesures ; E(5,
12) `x..x.x..x.x.` (KT1) sur 12 pas est le hat « cassé » ; E(7, 16) sur
16 fait un hat samba. Le kick ne bouge pas, les repères restent (règle de
[[../polymetrie]] : repères droits, ornements impairs), et c'est au hat
que ça s'entend le plus parce qu'il est continu.

**Swing et micro timing.** KT3 donne les chiffres : à 170-190 BPM,
54-56 % de swing valent 6 à 10 ms, perceptibles mais discrets ; 58 % et
plus brouille. Le micro timing de +2 à +4 ticks sur les hats des pas
pairs « tire » sans toucher au kick. Les morceaux de référence n'en
font presque pas : leur groove est dans le placement sur le « a » et
dans la vélocité, pas dans le retard.

**Ride et densité spectrale.** La ride (4) ajoute une nappe continue
dans 4-10 kHz : c'est le « plein régime » du plateau le plus fort. La
retirer sur le 1 d'une phrase baisse l'énergie perçue sans changer un
seul coup ; la remettre fait monter. Avec le hat ouvert, c'est le
premier levier de soustraction (KT9) parce qu'il ne touche ni au kick ni
à la basse.

**Masquage avec l'acid et les synthés.** La bande high du frenchcore
(`xx.xxXXXxxxx..xX`) est pleine : hoovers et screeches occupent 2-8 kHz
et les hats y comptent peu. Même chose avec une acid line résonante dont
le cutoff monte (KT11) : les hats disparaissent. Deux réponses : filtrer
les hats plus haut (passe-haut 8 kHz) ou les raréfier en croches pendant
que le lead monte, et les ramener en 16es quand il redescend.

## Sur la DT2

Grille de la [[../../doctrine]] §1 : ride 4, hat fermé 5, hat ouvert 6,
shaker sur perc B 8. Gestes : [[../parameter-preset-locks]] (vélocités,
preset lock), [[../microtiming-retrigs]], [[../polymetrie]],
[[../euclidien]], [[../fill-conditions]], [[../oneshots-synthe]] (AMP).

1. **Trois boucles, même kick (10 min).** Les boucles A, B, C du
   paragraphe « concret d'abord », dans trois patterns copiés du même
   kick (fiche [[../copier-coller]]). Chaîner, 8 mesures chacune, nommer
   le style à voix haute. Puis mélanger : hats de B sous l'ouvert de A.
2. **Profils de vélocité (5 min).** Hat fermé 5 en 16es, `VEL` lockée
   selon les cinq profils du tableau, 4 mesures chacun. Garder les deux
   qu'on sait reconnaître les yeux fermés.
3. **Un ouvert, coupé (5 min).** Hat ouvert 6 sur 3, 7, 11, 15, AMP decay
   long : bouché. Decay réduit jusqu'à ce que chaque ouvert meure avant
   le fermé suivant. Puis un seul ouvert sur le pas 15 : turnaround.
   Variante : ouvert en preset lock sur la track 5, comparer la coupure.
4. **Hat polymétrique (5 min).** Track 5 à 12 pas, E(5, 12), `RESET` à
   64. Trois mesures pour le recalage ; `1:4` sur le hat ouvert pour
   marquer la phrase malgré le cycle de 3.

## Pièges

- Deux hats ouverts qui se chevauchent, ou ouvert et ride ensemble à
  pleine vélocité : 5-10 kHz bouché, la syncope s'entend plus.
- Hat fermé plat à 100 partout : la grille écrase les autres syncopes au
  lieu de les montrer.
- Swing machine à 58 % et plus à 170-190 BPM : flou (KT3).
- Hats en 16es **et** acid line résonante en montée : masquage ; l'un
  des deux cède.
- La DT2 n'a pas de choke entre tracks : prévoir la coupure (AMP ou même
  track), sinon le hat ouvert déborde sur le temps suivant.
- Le repliage de la passe cale le maximum : un `X` au pas 1 de la bande
  high n'est pas forcément sur le temps du kick ; lire les motifs.

## Ressources

- Attack Magazine, Beat Dissected (index, un beat par style avec ses
  hats en 16 pas) :
  <https://www.attackmagazine.com/technique/beat-dissected/> `[V]`
- Attack Magazine, *DAW & Drum Machine Swing* :
  <https://www.attackmagazine.com/technique/passing-notes/daw-drum-machine-swing/> `[V]`
- Attack Magazine, *Polyrhythms* (hats en 6/8 sur kick 4/4) :
  <https://www.attackmagazine.com/technique/passing-notes/polyrhythms/> `[V]`
- Manuel DT2 OS 1.17, §11.2 (TRIG PAGE 1, `VEL`), §11.6 (AMP), §10.4
  (micro timing), §10.7 (longueur par track).

## Liens

[[_index]] · [[../../doctrine]] §1, §6 · [[../parameter-preset-locks]]
· [[../microtiming-retrigs]] · [[../polymetrie]] · [[../euclidien]] ·
[[../fill-conditions]] · [[../oneshots-synthe]] · [[../copier-coller]] ·
KT1 [[kt-cellules-rythmiques]] · KT2 [[kt-polymetrie-polyrythmie]] · KT3
[[kt-swing-microtiming]] · KT9 [[kt-phrasage-tension]] · KT10
[[kt-style-tribe]] · KT13 [[kt-style-hard-techno]] · KT21
[[kt-basses]]
