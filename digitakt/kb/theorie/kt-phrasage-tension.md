---
tags: [digitakt, kb, theorie, kt]
theme: Phrasage et tension
lot: 2
ordre: 9
styles: [tribe, acidcore, hypnotique, dnb]
statut: draft
updated: 2026-10-15
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

## Sur la DT2

Grille de la [[../../doctrine]] §1. Gestes : [[../mutes]] (préparer
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

## Pièges

- `A:B` compte les tours de la **track** : avec une 13 en 12 pas, `1:2`
  ne vaut plus « une mesure sur deux » (fiche [[../fill-conditions]],
  KT2).
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
- Manuel DT2 OS 1.17, §8.5.3 (mutes), §10.7 (`CHANGE`, `RESET`), §10.8.4
  (FILL), §11.2 (conditions).

## Liens

[[_index]] · [[../mutes]] · [[../fill-conditions]] ·
[[../patterns-chaines]] · [[../microtiming-retrigs]] ·
[[../perform-kit-temp-save]] · [[../../doctrine]] §2, §4, §5, §6 · KT2
[[kt-polymetrie-polyrythmie]] · KT3 [[kt-swing-microtiming]] · KT7
[[kt-tensions-lignes]] · KT10 (tribe), KT15 (hypnotique), à rédiger
