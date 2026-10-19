---
tags: [digitakt, kb, theorie, kt]
theme: Backbeat, half-time, passerelles de tempo
lot: 1
ordre: 4
styles: [tribe, dnb, dubstep, jungle]
statut: draft
updated: 2026-10-15
---

# KT4 — Backbeat, half-time, passerelles de tempo

**En une phrase** : le tempo affiché n'est pas le tempo ressenti, c'est la
place du backbeat qui le fixe ; un live à 180-190 BPM contient donc déjà
un 90-95 en half-time, et c'est par là, plus que par le BPM, qu'il
s'ouvre vers la DnB et le dubstep.

## Signature

| Élément | Théorique | Mesuré | Lecture |
|---|---|---|---|
| Backbeat four-on-floor | kick `X...X...X...X...`, clap `....X.......X...` | tribe clap dans le mid `Xxxxx.xxXx.xXxxx` (pas 1, 9 dominants) | le repliage cale le maximum : les pas 1 et 9 mesurés sont les temps 2 et 4 ou 1 et 3, la phase n'est pas garantie |
| Half-time | kick `X.........X.....`, snare `........X.......` | dubstep sub `X...Xx..Xxx.X...`, excision `x...X...x...x...` | un seul coup fort par mesure chez Excision : le half-time ; les trois autres « dubstep » de la library sont en 4/4, tag bruité |
| DnB 2-step | kick `X.........X.....`, snare `....X.......X...` | dnb sub `Xxx..xxxx.x...xX`, `sync` 0,52-0,70 | sub cassé, syncope la plus haute de la library |
| Amen | kick `X.x.......Xx....`, snare `....X..g.g..X..g` | tim reaper sub `XX...XXXxx...xxX` | le double kick 11-12 ressort ; détail dans [[../slice-breaks]] |

Tempo (fourchettes de [[../../veille-theorie]] §C5) : dubstep 140, ressenti
70 ; DnB 170-175, ressenti 85-87 ; jungle 160-175 ; tribe 160-180, mental
180-200.

Fait mesuré qui illustre la KT : la réanalyse des sidecars entre les deux
passes du hub a fait passer Liberté Naturel *Tracknard* de 184,6 à
90,7 BPM (2 × 90,7 = 181,4) et Maureen *Kompet x Jiggle* de 215,3 à 108,2
(2 × 108,2 = 216,4). Le détecteur hésite entre le tempo et sa moitié
parce que le morceau contient réellement les deux.

## Vocabulaire

- **Backbeat** : accent sur les temps 2 et 4 (clap ou snare, pas 5 et 13)
  ; c'est lui que la salle compte, pas le kick.
- **Four-on-floor** : kick sur les quatre temps ; backbeat sur 2 et 4.
- **Half-time** : même BPM, backbeat sur le temps 3 seulement (pas 9) ;
  ressenti à la moitié du tempo.
- **Double-time** : même BPM, kick et backbeat deux fois plus denses
  (clap sur les « et ») ; ressenti au double.
- **2-step** : pattern DnB à deux kicks, le second juste avant le snare du
  temps 4 (pas 11), snare sur 2 et 4.
- **Tempo ressenti** : celui qu'on bat du pied, fixé par le backbeat ;
  l'analyse librosa peut rendre l'un ou l'autre.
- **Passerelle** : relation simple entre deux tempos (moitié, double,
  3/4, 4/3, voisinage à moins de 10 %) qui permet de passer de l'un à
  l'autre sans rupture.
- **Pattern pont** : pattern sans kick (nappe, reverb, riser) pendant
  lequel le tempo change (doctrine §13).
- **Nudge** : décalage temporaire du tempo de 10 % (manuel §7.3,
  `[LEFT]` / `[RIGHT]` maintenus), pour caler sur une source externe.

## Pourquoi ça marche

**Concret d'abord : le même pattern, deux tempos ressentis.** Kick 1 en
`X...X...X...X...` et clap 3 sur 5 et 13 à 180 BPM : four-on-floor, on
compte 180. Déplacer le clap sur le seul pas 9 et retirer les kicks des
pas 5 et 13 : rien d'autre n'a changé, on compte 90. Les hats en doubles
croches sont devenus des triples croches ressenties, le kick du pas 1 est
devenu « le » kick de la mesure. C'est tout le mécanisme du half-time : la
salle compte les backbeats, pas les pas.

**Les passerelles du live, en chiffres.**

| Depuis | Vers | Relation | Arithmétique |
|---|---|---|---|
| tribe 180 | dubstep ressenti 90 | moitié | 180 / 2 = 90 |
| mental 190 | half-time 95 | moitié | 190 / 2 = 95 |
| mental 190 | DnB 175 | voisinage | 175 / 190 = 0,921, écart de 7,9 %, dans le nudge de 10 % |
| dubstep 140 | tekno 186,7 | 3 contre 4 | 140 × 4 / 3 = 186,7 |
| tekno 190 | dubstep 142,5 | 3 contre 4 | 190 × 3 / 4 = 142,5 |
| DnB 174 | ressenti 87 | moitié | 174 / 2 = 87 ; 87 est à 3 BPM du 90 du tribe en half-time |

**Pourquoi 140 et 186,7 se superposent.** À 140 BPM, 1 pas = 60 / 140 / 4
= 0,1071 s ; trois pas = 3 × 0,1071 = 0,3214 s. À 186,7 BPM, 1 pas =
60 / 186,7 / 4 = 0,0804 s ; quatre pas = 4 × 0,0804 = 0,3214 s. Trois
doubles croches à 140 durent exactement quatre doubles croches à 186,7 :
un delay pointé 3/16 à 140 (le classique du dubstep et du dub techno,
KT14) tombe sur la grille de doubles croches d'un tekno à 186,7. C'est la
polyrythmie 3 contre 4 de KT2 utilisée comme **passerelle** : un pattern
dubstep dont les hats sont en 3/16 peut être réécrit à 186,7 en 4/16 sans
que la salle entende le changement de tempo.

**Pourquoi le half-time ouvre vers la DnB.** Une DnB à 174 se compte à 87
(doctrine §13) ; un tribe à 180 joué en half-time se compte à 90. Les deux
ressentis sont à 3 BPM l'un de l'autre. Le chemin naturel : tribe 180 en
four-on-floor, passage en half-time (clap sur 9) pendant 16 mesures, break
DnB sur Id1 (fiche [[../slice-breaks]]) sous le kick tribe, puis retrait
du kick tribe et 2-step sur la 1. Le tempo affiché n'a pas bougé, ou de
6 BPM au plus. L'inverse ouvre vers le dubstep : du half-time à 180 (90
ressenti) au dubstep à 140 (70 ressenti), il reste un saut de 20 BPM
ressentis, à prendre par un pattern pont ou par la passerelle 3/4
(180 × 3 / 4 = 135, à 5 BPM de 140).

**Amen et 2-step : le backbeat tient, le kick casse.** Dans l'Amen (fiche
[[../slice-breaks]], première mesure), les snares restent sur 5 et 13 ; ce
sont les kicks qui se déplacent (1, 3, 11, 12). Dans le 2-step DnB, idem :
snare 5 et 13, kicks 1 et 11. Le `sync` de 0,52 à 0,70 des morceaux DnB du
hub mesure cette syncope du sub pendant que le backbeat reste fixe : la
règle pour écrire un break, c'est **snare fixe, kick libre**, l'inverse du
tribe où le kick est fixe et l'ornement libre.

**Ce que le détecteur de BPM nous apprend.** Librosa a donné 184,6 puis
90,7 pour le même morceau de tribe : la moitié du tempo est une lecture
légitime du signal parce que le clap sur 2 et 4 d'un four-on-floor à 181
est aussi un backbeat à 90,7. Le `setbuilder.py` (SPEC Phase 4) tolère
déjà les rapports 1:2 ; à l'oreille, le choix du tempo affiché est un
choix de ressenti, pas une mesure.

## Sur la DT2

Grille de la [[../../doctrine]] §1 : kick 1, clap 3, hat fermé 6, basse 9,
Id1 5. Tempo : fiche [[../tempo-metronome]] ; vitesse par track : fiche
[[../page-setup]].

1. **Même pattern, deux ressentis (5 min).** 180 BPM, kick `X...X...X...X...`,
   clap sur 5 et 13, hats 16 pas. Copier le pattern dans le slot suivant
   (fiche [[../copier-coller]]) : clap sur 9 seul, kicks sur 1 et 11 (le
   2-step). Chaîner les deux, 8 mesures chacun, en comptant à voix haute :
   180 puis 90. Variante : track 6 à `SPEED` 1/2X, le hat passe en croches
   ressenties sans changer un trig.
2. **La passerelle 3/4 (10 min).** 140 BPM, kick sur 1, snare sur 9, hats
   sur 1, 4, 7, 10, 13, 16 (le 3/16, fiche [[../euclidien]] avec E(6, 16)
   ou à la main). Passer le tempo à 187 (`[TEMPO]`, knob A) et poser dans
   un second pattern les hats en `x.x.x.x.x.x.x.x.` : le flux de hats est
   le même, à 1 ms près. Chaîner 140 puis 187 avec un pattern pont sans
   kick entre les deux (doctrine §13).
3. **Tribe vers DnB sans changer de tempo (10 min).** 180 BPM, pattern
   tribe four-on-floor ; pattern 2 : même kick, clap sur 9 ; pattern 3 :
   break Amen sur Id1 5 en 16 tranches (fiche [[../slice-breaks]]) sous
   le kick en half-time ; pattern 4 : kick tribe muté, 2-step sur la 1
   (pas 1 et 11), snare sur 5 et 13. Quatre patterns, zéro changement de
   tempo, un set qui est passé de la tribe à la DnB. Retour par le chemin
   inverse.

## Pièges

- La DT2 n'a pas de « half-time » global : c'est un pattern à écrire, ou
  `SPEED` 1/2X track par track ; à 1/2X, la track joue ses 16 pas sur 2
  mesures, donc ses conditions `A:B` comptent deux fois moins vite (fiche
  [[../fill-conditions]]).
- Changer le BPM d'un pattern à l'autre en mode PATTERN tempo donne un
  saut net à la bascule : réservé aux ruptures assumées ; pour une
  transition douce, pattern pont et nudge, ou song avec `ROW TEMPO` (fiche
  [[../song-mode]]).
- Un break DnB échantillonné à 174 joué à 180 est 3,4 % trop rapide
  (180 / 174 = 1,034) : caler avec `TUNE` ou STRETCH avant de trancher
  (fiche [[../machines-src]]).
- Le kick du set reste sur la track 1 même en DnB (grille §1) ; le break
  vit sur une Id. Sinon les mutes du live ne veulent plus rien dire.
- Le tag `genre` de la library est bruité : trois « dubstep » sur quatre
  de la passe du hub sont des 4/4 à 152. Trier à l'oreille avant KT18.

## Ressources

- Attack Magazine, Beat Dissected *Mystik dubstep* :
  <https://www.attackmagazine.com/technique/beat-dissected/mystik-dubstep/> `[V]`
- Ableton, *Beats Dissected* (présentation, dont le 2-step) :
  <https://www.ableton.com/en/blog/beats-dissected-diverse-drum-beat-tutorials-attack-magazine/> `[V]`
- EDMProd, *How to make jungle* :
  <https://www.edmprod.com/how-to-make-jungle-music/> `[V]`
- MusicRadar, *Amen-style break* :
  <https://musicradar.com/tuition/tech/how-to-program-an-amen-style-break-637374> `[R]`
- Manuel DT2 OS 1.17, §7.3 (tempo, nudge 10 %, swing), §10.7 (longueur et
  vitesse par track), §A.2 (SLICE).
- Livre : Butler, *Unlocking the Groove* (Indiana UP, 2006), sur le rôle
  du DJ et les transitions.

## Liens

[[_index]] · [[../slice-breaks]] · [[../tempo-metronome]] ·
[[../page-setup]] · [[../song-mode]] · [[../machines-src]] ·
[[../../doctrine]] §1, §13 · KT2 [[kt-polymetrie-polyrythmie]] · KT3
[[kt-swing-microtiming]] · KT18 (dubstep / DnB, à rédiger) · patches Tidal
[[../../../technique/patches/dnb]], [[../../../technique/patches/dubstep]]
