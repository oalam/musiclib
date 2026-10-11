---
tags: [sounddesign, variations, kick, slices, digitakt]
traitement: variations
presets: [drive_tints, rumble_tints]
---

# Variations

## En une phrase

Un **jeu de variantes subtiles d'un même one-shot** (un kick de kit, par
exemple), rangées en tranches égales dans un seul fichier : sur la DT2, la
machine GRID les découpe et un tirage au sort par trig fait que deux coups
de suite ne sont jamais tout à fait identiques.

Exemple concret : le preset `drive_tints` sur un kick, à 150 BPM, 8 tranches
d'un temps : un fichier de 8 × 60 / 150 = 3,2 s. La tranche 1 est presque
propre (drive 2 dB), la tranche 8 franchement saturée (12 dB). Mesuré sur un
kick synthétique, la part d'harmoniques au-dessus de 300 Hz passe de 0,3 % à
1,1 % et le corps du kick (RMS après le premier quart) de 0,269 à 0,326,
alors que l'attaque a le même niveau dans les 8 tranches.

## Pourquoi ça marche

- **Le « machine gun »** : un sample identique répété des centaines de fois
  finit par s'entendre comme une boucle figée. Une batterie jouée change
  un peu de timbre à chaque coup ; quelques teintes suffisent à l'imiter.
- **Varier la couleur, pas le volume.** Chaque tranche est ramenée au même
  niveau (RMS des 150 premières ms, l'attaque et le corps) : le tirage au
  sort change le grain sans créer d'accents involontaires. Les accents se
  posent à part, par la vélocité ou le volume des trigs.
- **Subtil d'abord** : les écarts doivent rester sous le seuil où l'on
  entend « un autre kick ». Sur un kick, quelques dB de drive ou un rumble
  plus ou moins présent suffisent.

## La chaîne, device par device

Le bouton ↗ sous un potard ne trace plus une évolution dans le temps : il
donne la valeur de la **dernière tranche** (potard « tranche N »). La
tranche 1 prend la valeur du potard, les autres s'étagent entre les deux,
de façon géométrique pour une fréquence.

### Réglages du traitement

| Réglage | Rôle |
|---|---|
| Tempo | Avec la longueur : durée d'une tranche. |
| Longueur | Durée d'une tranche en temps (1 = l'écart entre deux kicks en 4/4). La queue est coupée, fondu de 20 ms ; la track DT2 étant monophonique, le kick suivant la coupe de toute façon. |
| Tranches | 4, 8, 16 ou 32 : la grille GRID à régler sur la DT2. |
| Aléa | 0 = pas régulier de la tranche 1 (la plus sobre) à la dernière (la plus marquée) ; 1 = jusqu'à un pas d'écart en plus ou en moins. Le tirage est fixe : même preset, même fichier. |

### Distorsion

La teinte d'overdrive. De 2 à 12 dB, le kick passe de rond à granuleux ;
au-delà de 15 dB, ce n'est plus une variante mais un autre kick.

### Overdrive

Émulation de l'Overdrive de Live : un **passe-bande** choisit la bande
saturée (fréquence, largeur en octaves), puis une saturation asymétrique de
pédale (0 % de drive distord déjà), la **tonalité** (passe-bas après la
saturation, 800 Hz à 20 kHz), la **dynamique** (0 % : la saturation
compresse et rattrape le niveau, son dense ; 100 % : l'enveloppe de
l'entrée revient, l'attaque du kick reste) et le **dry/wet**. Sur un kick,
le passe-bande retire le sub : bande large (8 à 9 octaves) ou dry/wet
autour de 30 à 60 % pour garder le corps. Automatiser le dry/wet ou le
drive d'une tranche à l'autre donne des teintes plus « pédale » que la
Distorsion.

### Dynamic Tube

Émulation du Dynamic Tube de Live : une lampe dont le **bias** (point de
repos dans la courbe) donne le grain asymétrique, et dont l'**enveloppe**
module ce bias selon le niveau : positive, l'attaque est plus sale que la
queue ; négative, les forts restent propres (expansion). Modèles : **A**
propre tant que le signal reste sous un seuil, **B** saturation douce,
**C** « mauvais ampli » qui distord tout le temps. **Tone** au-dessus de
0,5 porte la distorsion sur les aigus (le clic grésille), en dessous sur le
grave. Pas de mode Hi-Quality (pas de suréchantillonnage) : rester sobre
sur le drive des aigus pour éviter le repliement.

### Bande (peak)

Une cloche vers 3,5 kHz qui monte un peu le clic de l'attaque sur les
dernières tranches : le kick « parle » plus dans le mix, sans changer de
corps.

### Passe-haut

Retire le très grave inutile (sous 25 Hz) que la saturation peut ajouter.

### Chaîne « Rumble »

Celle du traitement rumble (reverb, passe-bas, distorsion, duck, mono, cf.
[[sounddesign/rumble]]), terminée par un **Gain** qui varie : dans
`rumble_tints`, de −30 dB (à peine audible) à −12 dB (bien présent). Le
kick garde son attaque, la queue grave change d'une tranche à l'autre.

## Presets

| Preset | Variantes | Usage |
|---|---|---|
| `drive_tints` | Drive 2 → 12 dB, clic −1 → +3 dB, 8 tranches | Kick de kit qui respire, sur la track 1 |
| `rumble_tints` | Rumble −30 → −12 dB, drive 2 → 8 dB, 8 tranches | Kick et rumble d'un seul sample, la queue qui bouge |
| `tube_tints` | Bias du tube 0,1 → 0,5, overdrive dry/wet 30 → 60 %, 8 tranches | Grain de lampe qui monte, attaque plus sale, sub gardé |
| `layer_blend` | Couche C1 −24 → −6 dB au-dessus de 1 kHz, 8 tranches | Kick + clic ou top d'un autre sample, dosé tranche par tranche |

## Layering

Concrètement : la source (le kick de la vue Samples) tient le corps, une
**couche** (clic de 909, top d'un autre kick, bruit court) apporte
l'attaque, et le dosage de la couche change d'une tranche à l'autre.

- **Ajouter une couche** : « + couche » à côté de la source, choisir le
  sample dans la vue Samples, « Ajouter comme couche ». Jusqu'à trois
  couches (C1 à C3) ; la source ne change pas pendant le choix.
- **Attribuer** : boîte « Source » en tête des devices de la chaîne,
  sélecteur Source / C1… Le preset retient le numéro de couche, pas le
  fichier : le même preset sert à n'importe quelle paire.
- **Calage des attaques** : automatique, l'attaque de la couche (premier
  passage à −30 dB de sa crête) est posée sur celle de la source, son
  silence initial est coupé. Le potard **Décalage** (±50 ms) ajuste à la
  main : +2 à +5 ms laissent passer le clic du kick avant celui de la
  couche ; un décalage négatif qui entamerait la couche retarde tout le son.
- **Mélange variable** : ↗ gain sur la boîte Source, le gain de la chaîne
  va de son fader (tranche 1) à la valeur de fin (dernière tranche), avec
  l'aléa du traitement. Le niveau des tranches reste égalisé : la couche
  change la couleur, pas le volume.
- **Pièges** : filtrer la couche (passe-haut) pour ne pas doubler le grave,
  sinon les deux fondamentales se battent (phase) ; écouter la couche seule
  (solo) pour vérifier son calage.

## Sur la Digitakt II

1. Verser le rendu : il est rangé **avec la source** (même code, même
   dossier, ex. `DRUMS/BD/CLEAN`), nommé `BD V8 …`, tagué `slices`.
2. Track 1 (kick), machine **GRID** (`[FUNC] + [SRC]`), `GRID` = nombre de
   tranches du rendu (8).
3. Poser les trigs du kick, puis **CREATE RANDOM LOCKS** sur `SLICE` : chaque
   trig tire une tranche (cf. [[digitakt/kb/slice-breaks]]).
4. Variante dirigée : locker `SLICE` à la main, tranches basses dans le
   break, hautes au drop. Ou p-locks de `SLICE` sous condition `FILL`.
5. Sauvegarder le preset de la track : la grille de tranches est sauvée
   avec lui.

## Pièges

- **Grille fausse** : `GRID` doit valoir exactement le nombre de tranches du
  rendu, sinon les tranches tombent au milieu des coups.
- **Variantes trop éloignées** : si l'on reconnaît « deux kicks », réduire
  la plage (valeur de fin plus proche) plutôt que le nombre de tranches.
- **Queue coupée trop tôt** : une longueur de 0,5 temps tronque le rumble ;
  garder 1 temps pour un kick en 4/4.
- La réanalyse des samples ne juge pas un fichier tagué `slices` « long » :
  ne pas retirer ce tag.

## Ressources

- [[digitakt/kb/slice-breaks]] : machines SLICE / GRID, CREATE RANDOM LOCKS.
- [[sounddesign/rumble]] : la chaîne rumble device par device.
- [[digitakt/doctrine]] § 1 : grille des tracks (kick sur la 1).

#sounddesign #variations
