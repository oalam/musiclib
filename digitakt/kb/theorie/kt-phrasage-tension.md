---
tags: [digitakt, kb, theorie, kt]
theme: Phrasage et tension
lot: 2
ordre: 9
styles: [tribe, acidcore, hypnotique, dnb]
statut: draft
updated: 2026-10-26
---

# KT9 — Phrasage et tension

**En une phrase** : la techno se compte en phrases de 4, 8, 16 et 32
mesures, tout changement tombe sur le 1 d'une phrase, et la tension se
fabrique par soustraction, retour et appel-réponse plus que par ajout ;
en live, les mutes et les conditions de trig sont les outils de cette
forme, et le pattern n'est que la matière.

## Signature

| Élément | Théorique | Mesuré | Lecture |
|---|---|---|---|
| Phrase | 8 mesures = 128 pas = un pattern de 8 pages | `beats` et `structure` des sidecars : sections de 16 à 64 mesures (berio : main 189 s, breakdown 21 s, main 67 s) | les sections sont des multiples de 8 mesures, le breakdown dure 16 mesures |
| Breakdown | kick coupé 8 à 16 mesures | berio : deux breakdowns, 16 mesures puis 1 mesure (un trou de kick) | rarement plus de 16 mesures sans kick à 160-190 BPM |
| Appel et réponse | deux tracks en `1:2` / `2:2` | tribe mid `Xxxxx.xxXx.xXxxx` contre high `Xx.Xx.xxXx.xX.xx` | des creux complémentaires (pas 6 du mid, pas 3 et 6 du high) : les couches se répondent |
| Turnaround | variation sur la dernière mesure d'une phrase | non visible dans le repliage sur 16 pas | à écouter sur les références, 4e mesure de chaque phrase |

Durées à 190 BPM : 1 mesure = 4 × 60 / 190 = 1,263 s ; 4 mesures = 5,1 s ;
8 = 10,1 s ; 16 = 20,2 s ; 32 = 40,4 s. À 170 BPM : 1 mesure = 1,412 s,
32 mesures = 45,2 s.

## Vocabulaire

- **Phrase** : groupe de 4, 8, 16 ou 32 mesures que la salle compte sans
  le savoir ; le **1** de la phrase est le moment où un changement paraît
  naturel.
- **Plateau** : phrase ou suite de phrases sans changement de matière ;
  le tribe vit en plateaux de 8 à 16 mesures.
- **Build** : montée de densité rythmique et spectrale vers un point ;
  **breakdown** : kick coupé, la tension vient de l'absence ; **drop** :
  retour du kick et de la basse.
- **Soustraction** : construire en retirant (mutes) plutôt qu'en ajoutant ;
  le retour d'un élément fait plus d'effet que son entrée.
- **Appel et réponse** : deux motifs qui alternent sur deux cycles (un
  tour sur deux chacun) ou sur deux moitiés de mesure.
- **Turnaround** : variation de la dernière mesure d'une phrase qui
  annonce le retour au 1 (fill, retrig, note tendue, silence).
- **Fill** : densité maximale sur une ou deux mesures, à la demande
  (`FILL`).
- **Densité spectrale** : quantité d'énergie dans chaque bande ; retirer
  le haut (ride, hats ouverts) baisse l'énergie perçue sans toucher au
  rythme (KT3).
- **Arc** : courbe d'énergie d'un morceau ou d'un set (doctrine §6,
  principe 1).

## Pourquoi ça marche

**Concret d'abord : compter.** Pattern de 8 mesures (128 pas, 8 pages) à
190 BPM, soit 10,1 s par tour. Une phrase de 32 mesures = 4 tours =
40,4 s. Le kick coupé à la fin du 4e tour et remis au début du tour
suivant tombe sur le 1 d'une phrase de 32 : la salle l'attendait. Coupé
au milieu du 3e tour, il tombe nulle part : surprise, mais une surprise
qui ne porte pas, sauf si elle est voulue (doctrine §6, principe 6).
Compter à voix haute les tours de pattern est le premier exercice.

**Pourquoi les phrases de 4 et 8.** L'oreille groupe par 2 : deux mesures
font une unité, deux unités une phrase de 4, deux phrases une de 8. Les
changements sur le 1 d'une phrase de 8 ou 16 sont entendus comme une
**décision**, ceux sur le 1 d'une phrase de 4 comme une **variation**,
ceux ailleurs comme un accident. Butler : la forme de l'EDM est un
processus de couches qui entrent et sortent sur des multiples de 4, et le
DJ compte en 8 et 32 pour mixer.

**Tension par soustraction.** Une boucle de 10 tracks qui tourne 32
mesures a installé une normale. Retirer la 8 (ride) et la 7 (hat ouvert)
au 1 d'une phrase : l'énergie baisse, la salle attend. Retirer la 1 et la
2 : breakdown. Remettre les quatre d'un coup sur le 1 suivant : drop. Le
même contenu, trois états, zéro nouveau son ; la tension était dans la
**privation** puis le **retour** (doctrine §6, principes 4 et 5). C'est le
cœur du jeu aux mutes (fiche [[../mutes]]) : un pattern plein, et un
ordre de retrait et de retour.

**Tension par ajout, à petites doses.** Build : retrigs de plus en plus
rapides (1/8 puis 1/16 puis 1/32 sur la 3, fiche
[[../microtiming-retrigs]]), riser sur la 15 en `LST` (fiche
[[../fill-conditions]]), filtre qui s'ouvre sur 8 mesures (Control All).
Un seul paramètre qui bouge sur une boucle fixe (doctrine §6, principe 2)
vaut mieux que trois : la salle suit une ligne, pas trois.

**Appel et réponse.** Deux tracks qui ne jouent jamais ensemble : la 13
en condition `1:2` (tour impair), la 14 en `2:2` (tour pair) ; ou la 7
sur la première demi-mesure, la 8 sur la seconde. Le motif de 32 pas qui
en résulte est entendu comme une phrase à deux voix ; c'est le tom
interplay de Detroit (KT16) et le dialogue des percs tribe (KT10). Le
repliage de la passe `rhythm_signature` en montre la trace : les creux
du mid et du high tribe ne tombent pas aux mêmes pas.

**Turnaround.** La 4e mesure d'une phrase de 4 porte la variation : un
clap en `4:4`, un retrig, une note tendue de fin de ligne (KT7), ou un
silence d'un temps. Sans turnaround, une boucle de 4 mesures est une
boucle de 1 mesure jouée 4 fois ; avec, c'est une phrase. Le `FILL`
manuel est le turnaround à la demande, la condition `4:4` le turnaround
automatique.

**L'arc.** Un morceau de 6 minutes à 190 BPM = 6 × 60 / 1,263 = 285
mesures, soit 9 phrases de 32. Un plan qui tient : intro 32, plateau 32,
build 16, breakdown 16, drop et plateau 64, respiration 16, plateau final
64, sortie 32 = 272 mesures. Le set (doctrine §6, principe 1) est le
même arc à l'échelle de l'heure : montées avec respirations, un ou deux
sommets, une fin marquante.

**Ce que disent les sources de production.** Les blogs d'arrangement et
les fils Elektronauts ([[../../veille-theorie]] §F) convergent : **16
mesures est l'unité de décision, 32 la section, 8 le fill, jamais 24** ;
un seul changement perceptible par frontière ; et la rupture est
**annoncée** sur la fin du bloc. Les recettes de fin de bloc, données pour
125-140 BPM : ouverture de filtre concentrée sur les mesures 13 à 16 d'un
bloc de 16, résonance à l'inverse du cutoff ; send de reverb de rien à
-6 dB sur les mesures 15 et 16, puis retour sec sur le 1 ; kick baissé de
2 demi-tons sur les deux derniers temps de la mesure 16 ; hats retirés sur
les 4 dernières mesures ; kick coupé 8 mesures avant le pic ; clap coupé
une mesure sur 8 ; profondeur d'un LFO de 10 à 80 % sur 32 mesures
(Myloops, TrackSensei). Règles de terrain : « quelque chose change toutes
les 15 secondes », soit 15 / 1,263 = 12 mesures à 190 BPM ; +1 élément
et -2 toutes les 16 ; construire la boucle principale et le climax
d'abord, puis le reste à rebours ; sortir par soustraction dans l'ordre
inverse de l'entrée ; chasser les **zones mortes** au milieu des blocs de
32 et 64 (Elektronauts 2021, Attack 2020). Côté machine, Wolkenhauer joue
un morceau entier sur **un seul pattern** Digitakt en six sections aux
mutes (intro, transition, break percussif sans kick, core loop, break
mélodique, outro) avec `FILL` pour les breaks courts, `NOT FILL` pour le
motif normal, `3:3` pour un élément un cycle sur trois, `1ST` pour
l'impact d'entrée ; et le fil sur les conditions montre que `1:2` en début
de pattern et `2:2` en fin **allongent la période perçue** : sur un
pattern de 4 mesures, `2:2` fait 8 mesures, `2:3` 12, `2:4` 16. C'est la
version DT1 de ce que la doctrine §2 arbitre pour la DT2 (pattern main
écrit pour 4 tours).

## Compter sans compter : les repères

Compter dans la tête est le dernier recours. La techno pose des repères
audibles à chaque étage de la hiérarchie, et la DT2 a trois compteurs :
la LED `[PAGE]` (la mesure, en GRID REC), les conditions `A:B` (le tour,
jusqu'à 8), `CHANGE` et le song mode (la phrase). Le but est qu'on
*entende* dans quelle phrase on est, et que la salle l'entende aussi.

### Dans la musique : les conventions

| Étage | Repère techno | Mesuré sur les références (hub, passe drums) |
|---|---|---|
| 1 mesure | le kick | — |
| 2 mesures | hat ouvert ou clap qui alterne un tour sur deux (`1:2` / `2:2`) ; l'unité de 2 de l'oreille | Tekotak *L'okapi* : kick doublé sur le « et » du 1 **toutes les 2 mesures** |
| 4 mesures | turnaround sur la 4e mesure ; en tribe, le **kick lui-même compte** : halte de 2 temps en tête de phrase, rebond autour du 1 | Kodaman *Smash*, *Béton* : halte `..X.X.X.` à chaque phrase de 4 ; Tekotak : kick accentué toutes les 4 |
| 8 mesures | halte longue, roulement de fin de phrase avec une croche vide avant le 1 | Tekotak : `X....... \| ..X.X.X.` toutes les 8, roulement `.xXXXXX.` |
| 16 et 32 mesures | crash ou cymbale inversée sur le 1, shout ou stab vocal, note de basse qui change (KT7), sub drop, **kick coupé sur la dernière mesure**, ride qui n'entre qu'à la moitié (phrases 3 et 4), filtre acid qui s'ouvre sur 32 mesures et se referme au 1 (KT11) | sections des sidecars en multiples de 8 et 16 mesures |

Le filtre qui s'ouvre sur 32 mesures est une **horloge analogique** : la
brillance dit où on est dans la phrase, sans rien compter.

### Sur la DT2 : faire compter la machine

1. **Une note toutes les 4 phrases.** Track marqueur de 128 pas (8
   mesures, PER TRACK, car `A:B` compte les tours de la *track*), un trig
   au pas 1 en `1:4` : il joue une fois toutes les 32 mesures. Sur la 15 :
   crash, shout, sub drop. Si le pattern fait 4 mesures (64 pas), `1:8`
   donne aussi 32 mesures (B va jusqu'à 8). Une cymbale inversée doit
   *précéder* le 1 : la poser en fin de page 8 en `4:4`, pas au pas 1 en
   `1:4`.
2. **Le trou qui annonce le 1.** Condition inversée `NOT 4:4` (le trig
   joue sauf au tour 4, fiche [[../fill-conditions]]) sur les kicks de la
   dernière mesure (page 8) : le kick se coupe une mesure toutes les 32,
   le kick cut de la techno sans toucher aux mutes. Même chose en `NOT
   4:4` sur la basse pour une respiration.
3. **Un étage par tour.** Rien de plus au tour 1, ride en `2:4`, hat
   ouvert en `3:4`, roulement sur la dernière page en `4:4` : le numéro
   du tour s'entend. Le drop remet le tour 1 nu, et le cycle repart.
4. **Un LFO comme horloge.** Sur la track porteuse (la 10 pour un filtre
   acid, la 8 pour le volume du ride) : LFO `WAVE` RAMP ou EXP, `MODE`
   TRG, `SPD` 1 × `MULT` 4 = un cycle de 512 pas, soit 32 mesures (règle
   de [[../lfo]] : `SPD` 8 × 16 = 16 pas). `LFO.T` (page TRIG 1) locké à
   OFF sur tous les trigs, sauf un trig au pas 1 en `1:4` avec `LFO.T`
   ON : la rampe repart au 1 de chaque phrase de 32 et nulle part
   ailleurs. Variante sans condition : `MODE` FRE, la rampe part au
   `[PLAY]` et reste calée tant qu'on ne stoppe pas. *Durée du cycle et
   relance par un lock trig à vérifier à la machine*
   ([[../tutos/maison-rumble-dans-le-kick]] pose la même question).
5. **Atterrir sans viser.** `CHANGE` = 128 (PER TRACK, fiche
   [[../page-setup]]) : un pattern mis en file part sur le 1 d'une phrase
   de 8 quel que soit le moment du geste ; 512 pour une phrase de 32 si la
   plage le permet *(maximum à vérifier à la machine)*. En song mode
   ([[../song-mode]]), une ligne = un pattern × 4 tours : le song compte
   les 32 mesures et change tout seul.
6. **Préparer, puis lâcher.** Mutes préparés avec `[FUNC]` maintenu
   pendant la mesure 8, relâchés quand le 1 arrive : on n'a plus à viser
   l'instant, seulement à savoir qu'on est dans la dernière mesure, ce que
   le turnaround dit.

### Dans la tête, quand il faut

Compter les mesures, pas les temps : le numéro de la mesure remplace le
« 1 » (« 1 2 3 4, 2 2 3 4 … 8 2 3 4 »), un doigt levé par phrase de 8 ;
quatre doigts = 32. Deux mains pour deux étages : la droite compte les
mesures de 1 à 8 à voix haute, la gauche garde la phrase de 1 à 4 en
silence. Exercice : compter ainsi sur une référence de la library et
vérifier avec les frontières `structure` et `cues` du sidecar
(`analyze.py`) que les changements tombent sur des multiples de 32.

## Sur la DT2

Arbitré dans la [[../../doctrine]] le 2026-10-26 : un pattern main fait 8
mesures et est écrit pour 4 tours (§2), slots 1-8 par rôle (§2), un mute
par phrase de 8 et une décision par 16 ou 32 (§4), un étage par changement
(§6, principe 3). Grille de la doctrine §1. Gestes : [[../mutes]] (préparer
plusieurs mutes, lâcher sur le 1), [[../fill-conditions]] (`A:B`, `FILL`,
`LST`), [[../patterns-chaines]] (file d'attente, `CHANGE`),
[[../microtiming-retrigs]] (retrigs).

1. **Compter et soustraire (10 min).** Pattern tribe plein de 8 mesures,
   `[FUNC] + [TRK]` (mute global). Compter les tours à voix haute. Au 1
   du tour 5 : retirer 4 et 6. Au 1 du tour 7 : retirer 1, 2, 9 préparées
   avec `[FUNC]` maintenu. Au 1 du tour 9 : tout remettre d'un coup. Puis
   refaire en coupant au milieu du tour 3 pour entendre la différence.
2. **Appel, réponse, turnaround (10 min).** Track 13 en `1:2`, track 14
   en `2:2` (motifs différents, même registre). Clap de la 3 : un trig
   supplémentaire sur le pas 15 en `4:4`, un roll `RATE` 1/32 `LEN` 4 en
   `FILL`. Écouter 16 mesures sans toucher, puis tenir `[PAGE]` sur la
   dernière mesure d'une phrase de 8.
3. **Build en un paramètre (5 min).** Boucle fixe, riser sur la 15 en
   `LST` avant une bascule de pattern (fiche [[../patterns-chaines]]),
   Control All sur le filtre (`[TRK]` maintenu + `FREQ`) ouvert sur 8
   mesures, drop au changement de pattern. Un seul geste, une seule
   ligne.
4. **Marqueurs de phrase (10 min).** Pattern de 8 mesures, track 15 en
   128 pas : crash en `1:4` au pas 1, cymbale inversée en `4:4` en fin de
   page 8. Kicks de la page 8 en `NOT 4:4`. Ride de la 8 en `2:4`, hat
   ouvert de la 7 en `3:4`. Laisser tourner 3 phrases de 32 sans toucher,
   fermer les yeux, et dire le numéro du tour quand le ride entre ; poser
   le mute de la 9 sur le 1 annoncé par le trou de kick.

## Pièges

- `A:B` compte les tours de la **track** : avec une 13 en 12 pas, `1:2`
  ne vaut plus « une mesure sur deux » (fiche [[../fill-conditions]],
  KT2).
- Un marqueur de phrase en `1:4` sur une track de 16 pas joue toutes les 4
  **mesures**, pas toutes les 4 phrases : la track marqueur doit faire la
  longueur du pattern (128 pas).
- Trop de marqueurs tuent le repère : un seul élément par étage (le crash
  pour le 32, le turnaround pour le 4), sinon tout est un signal et plus
  rien ne l'est.
- Un pattern de 8 mesures mis en file d'attente démarre à la fin du tour
  en cours : choisir le suivant tôt, ou régler `CHANGE` sur 16 ou 32 pas
  (fiche [[../patterns-chaines]]).
- Trop de changements en même temps hors drop : un seul par phrase de 8
  ou 16 (doctrine §6, principe 3).
- Un breakdown trop long à 190 BPM (plus de 16 mesures sans kick) fait
  retomber la salle : les références n'en font pas.
- Le riser `LST` ne joue que si le pattern suivant est bien en file
  d'attente ; en chaîne ou en song il tombe juste, à la main il faut
  avoir choisi le pattern avant le dernier tour.

## Ressources

- Butler, *Unlocking the Groove* (Indiana UP, 2006), chapitres sur la
  forme comme processus et le rôle du DJ ; catalogue.
- Attack Magazine, Beat Dissected (index) :
  <https://www.attackmagazine.com/technique/beat-dissected/> `[V]`, dont
  *raw hypnotic techno like Silent Servant* `[R]`.
- Attack Magazine, *The Secrets of Techno Production* (livre) :
  <https://store.attackmagazine.com/products/the-secrets-of-techno-production> `[R]`
- TrackSensei, *How to Arrange a Techno Track (Bar-by-Bar)* :
  <https://tracksensei.com/blog/how-to-arrange-a-techno-track> `[V]`
- Myloops, *Techno Automation: 11 Moves That Keep an 8-Minute Track Alive* :
  <https://www.myloops.net/using-automation-to-keep-techno-interesting> `[V]`
- Attack Magazine, *4 Ways To Break Out Of The Loop* :
  <https://www.attackmagazine.com/technique/tutorials/4-ways-to-break-out-of-the-loop/> `[V]`
- Elektronauts, *Simple Tips in Techno Structure* :
  <https://www.elektronauts.com/t/simple-tips-in-techno-structure/151609> `[V]`
- Elektronauts, Wolkenhauer, *Turning a DAW track into a Digitakt live performance* :
  <https://www.elektronauts.com/t/turning-a-daw-track-into-a-digitakt-live-performance-tutorial-how-to/42056> `[V]`
- Elektronauts, *How do you use conditional triggers?* :
  <https://www.elektronauts.com/t/how-do-you-use-conditional-triggers/42272> `[V]`
- Manuel DT2 OS 1.17, §8.5.3 (mutes), §10.7 (`CHANGE`, `RESET`), §10.8.4
  (FILL), §11.2 (conditions).

## Liens

[[_index]] · [[../mutes]] · [[../fill-conditions]] ·
[[../patterns-chaines]] · [[../microtiming-retrigs]] ·
[[../perform-kit-temp-save]] · [[../lfo]] · [[../page-setup]] ·
[[../song-mode]] · [[../tutos/maison-rumble-dans-le-kick]] ·
[[../../doctrine]] §2, §4, §5, §6 · KT2
[[kt-polymetrie-polyrythmie]] · KT3 [[kt-swing-microtiming]] · KT7
[[kt-tensions-lignes]] · KT10 (tribe), KT15 (hypnotique), à rédiger
