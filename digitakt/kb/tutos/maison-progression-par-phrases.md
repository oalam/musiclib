---
tags: [digitakt, kb, tutos]
theme: Progression par phrases aux seules conditions et mutes de la DT2, exemple travaillé
lot: 3
ordre: 2
source: "arbitrage doctrine du 2026-10-26 (§2, §4, §6) et veille §F"
auteur: Tom (doctrine), rédaction à vérifier à la machine
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-26
---

# Maison 2 — Progression par phrases : un pattern main et sa partition

**En une phrase** : un pattern main de 8 mesures **écrit pour 4 tours**
(le cycle de variations en conditions), une **partition de mutes** sur
trois cycles de 32 mesures (un mute par phrase de 8, une décision par 16
ou 32), puis **un changement de pattern** qui ne change qu'une chose : les
trois étages de la doctrine §6 principe 3, déroulés sur un morceau.

Le *pourquoi* : KT9 [[../theorie/kt-phrasage-tension]], tables des hats
(KT20 [[../theorie/kt-hats]]) et de la basse (KT21 [[../theorie/kt-basses]]).
Gestes : [[../fill-conditions]], [[../mutes]], [[../page-setup]],
[[../patterns-chaines]], [[../parameter-preset-locks]]. Session de
référence : [[elektronauts-un-pattern-six-sections]]. Rien n'a encore été
rejoué à la machine : statut `draft`.

## Sur notre grille

Tribe ou mental à 190 BPM, grille de la [[../../doctrine]] §1 : 1 kick,
2 rumble, 3 clap, 4 perc, 5 Id1, 6 hat fermé, 7 hat ouvert, 8 ride,
9 basse (ou vide si kickbass, KT11), 10 lead, 13 Id2, 15 FX. Pattern de
128 pas en PER TRACK (`[FUNC] + [PAGE]`) pour que `A:B` compte les tours du
pattern. Un tour = 8 mesures = 10,1 s ; un cycle de 4 tours = 32 mesures =
40,4 s (KT9).

## Le piège physique, avant de câbler

Une condition est **une par trig**, et un pas ne porte qu'un trig. Un
élément qui doit jouer aux tours 3 et 4 ne peut pas porter `3:4` et `4:4`
sur le même pas. Trois issues : la condition inversée (`NOT 1:4` joue aux
tours 2, 3, 4), le **pas voisin micro-timé** (deux trigs sur les pas 3 et
4, le second ramené de 23 ticks vers la gauche, l'un en `3:4`, l'autre en
`4:4`, astuce du fil Elektronauts, [[../../veille-theorie]] §F), ou le
mute, qui est de toute façon l'outil de l'étage au-dessus : une entrée qui
dure deux tours ou plus est une **décision**, pas une variation, et se
joue aux mutes (KT20). Les conditions ne portent que ce qui est court :
annonces, turnarounds, trous.

## Recettes

### 1. Le pattern main A, écrit pour 4 tours

- **Résultat** : laissé tourner sans toucher, le pattern annonce lui-même
  l'arrivée du 1 de chaque phrase de 32, et le tour 4 s'entend.
- **Pas à pas** (tout en `[RECORD]`, GRID) :
  1. Pattern copié du modèle (doctrine §8), 128 pas PER TRACK, `CHANGE`
     = 128 pour que toute bascule atterrisse sur un tour
     ([[../page-setup]]).
  2. **Moteur**, sans condition : kick 1 sur les temps ; rumble 2 sur les
     mêmes pas ; hat fermé 6 en 16es avec profil de vélocité (KT20) ;
     basse 9 en contretemps `..x...x...x...x.` sur la tonique (KT21).
  3. **Couche rythmique** : clap 3 sur 5 et 13 ; perc 4 sur un motif tribe
     avec `PROB` 70 % sur les ghosts ; Id1 5 en `1:2` et Id2 13 en `2:2`,
     motifs différents, même registre : appel et réponse sur deux tours
     (KT9).
  4. **Couches hautes**, écrites pleines, elles entreront aux mutes : hat
     ouvert 7 en contretemps, ride 8 sur les temps.
  5. **Annonce automatique** (`NOT 4:4`) : les trigs de la 6 et de la 7 de
     la **page 8** en `NOT 4:4`. Hats et ouvert se taisent sur la dernière
     mesure de chaque cycle de 32. Variante plus large : pages 7 et 8.
  6. **Turnaround** (`4:4`) : clap 3, trig supplémentaire au pas 15 de la
     page 8 en `4:4`, roll `RATE` 1/32 `LEN` 4 ; basse 9, trig
     supplémentaire au pas 16 de la page 8 en `4:4`, `NOTE` +1 (la b2
     phrygienne, KT6, KT21), un pickup avant le 1 ; le pas 16 est libre
     puisque la basse joue en contretemps.
  7. **Marqueur de phrase** sur la 15 : crash au pas 1 de la page 1 en
     `1:4` (une fois par cycle de 32) ; cymbale inversée au pas 13 de la
     page 8 en `4:4`, micro-timée pour finir sur le 1.
  8. **Trou de kick**, en option : kick 1, trig du pas 13 de la page 8 en
     `NOT 4:4` ; un temps de silence avant le 1, une fois toutes les 32
     mesures. Fort : réservé au pattern de drop (recette 3).
  9. Sauver le pattern ; `[FUNC] + [YES]` temp save avant de jouer.
- **Attention** : les conditions `A:B` comptent les tours de la **track** ;
  toute track qui porte une condition doit faire 128 pas (fiche
  [[../fill-conditions]]). La 5 et la 13 en `1:2` / `2:2` peuvent rester à
  128 pas, leur cycle de 2 tours divise le cycle de 4.
- **Chez nous** : rien de ce qui précède ne se joue à la main. C'est la
  **variation** de l'étage tour (doctrine §6 principe 3), et elle est
  identique dans chaque pattern main copié d'A.

### 2. La partition de mutes sur trois cycles

- **Résultat** : 96 mesures sur le seul pattern A, une entrée par phrase de
  8, une décision par 16 ou 32, la salle entend une progression sans qu'un
  seul son nouveau apparaisse.
- **Pas à pas** : mute global `[FUNC] + [TRK]` (fiche [[../mutes]]) ;
  préparer chaque mute avec `[FUNC]` maintenu pendant la mesure 8 du tour,
  lâcher sur le 1 (KT9, « Préparer, puis lâcher »). « + » = démuter,
  « – » = muter.

| Cycle | Tour | Mesures | Geste | Étage |
|---|---|---|---|---|
| 1 | 1 | 1-8 | 1 kick, 2 rumble, 6 hat fermé, 9 basse | départ, moteur |
| 1 | 2 | 9-16 | + 3 clap | variation |
| 1 | 3 | 17-24 | + 4 perc | variation |
| 1 | 4 | 25-32 | rien : l'annonce (`NOT 4:4`), le turnaround et la cymbale inversée jouent seuls | automatique |
| 2 | 5 | 33-40 | + 10 lead | **décision** (1 de 32) |
| 2 | 6 | 41-48 | + 5 Id1 (sa `1:2` le fait répondre à la 13 qui viendra) | variation |
| 2 | 7 | 49-56 | + 7 hat ouvert | variation |
| 2 | 8 | 57-64 | + 13 Id2 ; annonce automatique | variation |
| 3 | 9 | 65-72 | + 8 ride : **peak**, tout joue | **décision** (1 de 32) |
| 3 | 10 | 73-80 | rien : plateau | — |
| 3 | 11 | 81-88 | – 8 ride, un tour : respiration | variation (KT20) |
| 3 | 12 | 89-96 | + 8 ride ; mettre le pattern B en file d'attente | retour |

- **Attention** : jamais deux mutes sur la même frontière hors drop ; la
  basse ne bouge pas de toute la partition (KT21) ; la 6 non plus.
- **Chez nous** : c'est le scénario par défaut au sens de la doctrine §4,
  celui que la bank générée produit sur 8 mesures ; en live on garde
  l'ordre et on étire ou raccourcit les cycles selon la salle. Le
  compte se lit sur le crash `1:4` et la cymbale `4:4`, pas dans la tête.

### 3. Le changement de pattern : une seule chose change

- **Résultat** : à la mesure 97, le 1 d'un cycle, la matière change une
  fois, et le reste de la partition est inchangé.
- **Pas à pas** :
  1. Pattern B = copie d'A (`[FUNC] + [RECORD]` sur le pattern, fiche
     [[../copier-coller]]) avec **une** différence : la basse 9 sur la
     quinte (`NOTE` +7) ou une seconde note sur les pas 7 et 15 ; ou le
     lead 10 avec une b2 en slide (KT11). Mutes identiques à la fin d'A.
  2. Mis en file pendant le tour 12 ; `CHANGE` = 128 le fait partir sur le
     1 du tour 13.
  3. Pattern break (slot 6, doctrine §2) : copie d'A sans trigs sur 1, 2
     et 9, riser sur la 15 en `LST` ; chaîné pour 8 à 16 mesures (1 ou 2
     tours), jamais plus à 190 BPM (KT9).
  4. Pattern drop (slot 7) : A ou B tel quel, impact sur la 15 en `1ST` au
     pas 1 ; **tout démuté** à l'arrivée, le seul moment où trois tracks
     reviennent ensemble (kick, rumble, basse). *À vérifier* : `1ST` se
     réinitialise-t-il au changement de pattern sur la DT2 ? Sur la DT1 de
     2017, non ([[elektronauts-un-pattern-six-sections]], trick 3).
- **Chez nous** : la forme complète intro, A, B, break, drop, sortie tient
  en six slots (doctrine §2, table des slots), et chaque slot porte le même
  cycle de 4 tours écrit une fois dans A.

## À essayer (5 min)

Pattern A seul, recette 1 faite. Laisser tourner **deux cycles** sans
toucher, les yeux fermés, et dire « quatre » quand les hats se taisent ;
puis jouer le cycle 1 de la partition en préparant chaque mute avec
`[FUNC]` et en lâchant sur le crash. Si le crash arrive avant qu'on ait
lâché, le compte était faux, pas la machine.

## Liens

[[_index]] · [[elektronauts-un-pattern-six-sections]] ·
[[maison-rumble-dans-le-kick]] · [[../fill-conditions]] · [[../mutes]] ·
[[../page-setup]] · [[../patterns-chaines]] · [[../copier-coller]] ·
[[../parameter-preset-locks]] · [[../theorie/kt-phrasage-tension]] ·
[[../theorie/kt-hats]] · [[../theorie/kt-basses]] ·
[[../theorie/kt-style-acidcore]] · [[../../doctrine]] §2, §4, §6, §8 ·
[[../../veille-theorie]] §F
