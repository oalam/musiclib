---
tags: [digitakt, doctrine, live, set, elektron]
source: "https://youtu.be/y_YijodbZYI"
updated: 2026-10-07
status: living document
---

# Doctrine Digitakt II — live techno

Règles **arbitrées** pour préparer et jouer un live sur Digitakt II. Elles
servent aussi de contrat à l'analyzer [[../scripts/README|digitakt.py]]
(qui range chaque morceau de référence selon cette même grille de tracks).
Les points marqués *(à vérifier)* sont des manipulations machine à confirmer dans
le manuel, ils alimenteront la base de connaissance `digitakt/kb/`.

Terrain : voir [[../README]] — tribe / acid core 180-200 BPM, ouvertures DnB,
dubstep, ralentis.

---

## 1. Grille des 16 tracks (invariante)

**Chaque track garde le même rôle dans tous les patterns de tous les sets.** En
live, les doigts doivent savoir sans regarder que le 1 coupe le kick et que le 9
coupe la basse. Les mutes et les réflexes en dépendent.

### Rythmique — tracks 1 à 8 (première rangée de touches)

| Track | Rôle | Bande dominante | Notes |
|---|---|---|---|
| 1 | **Kick** | 40-120 Hz + click 2-5 kHz | Même sample, même réglage dans tout le set (cf. §3) |
| 2 | **Rumble / sub** | 30-80 Hz | Kick resamplé + reverb + saturation + passe-bas ; même pas que le kick + ducking (cf. §9) |
| 3 | **Clap / snare** | 200 Hz-2 kHz | Temps 2 et 4 en four-on-floor, plus libre en tribe |
| 4 | **Hat fermé** | 6-12 kHz | Contretemps, doubles croches |
| 5 | **Hat ouvert** | 5-10 kHz | Un seul bien placé vaut mieux qu'un empilement |
| 6 | **Ride** | 4-10 kHz | Couleur de « plein régime », sort en peak |
| 7 | **Perc A** | variable | Toms, rims… |
| 8 | **Perc B** | variable | Shakers, claves, métalliques… |

### Mélodique et textures — tracks 9 à 16 (seconde rangée)

| Track | Rôle | Bande dominante | Notes |
|---|---|---|---|
| 9 | **Basse** | 80-250 Hz + harmoniques | Sacrée avec le kick ; contretemps, attaque franche, decay court (cf. §9) |
| 10 | **Séquence / lead** | 300 Hz-4 kHz | Acid line, stabs, arpèges |
| 11 | **Atmo / drone** | large, faible niveau | Nappe, drone, room tone ; souvent sample Stretch |
| 12 | **Id1** | variable | Identité du pattern : rythmique, ambiance ou mélodie |
| 13 | **Id2** | variable | Seconde identité, en dialogue ou en remplacement de Id1 |
| 14 | **Vocal / one-shots** | 300 Hz-4 kHz | Voix, samples parlés, cris, hooks |
| 15 | **FX de transition** | large | Risers, noise, impacts, downlifters, reverses (cf. §5) |
| 16 | **Réserve / MIDI** | — | Track MIDI vers une machine externe, ou joker |

**Règles dérivées** :

- Une track vide reste vide, **jamais réaffectée à un autre rôle** pour « gagner
  une place ». Un pattern qui n'a pas besoin de ride laisse la 6 vide.
- Id1 / Id2 (12-13) sont les seules tracks dont le *contenu* change franchement
  d'un pattern à l'autre. C'est là qu'on reconnaît « le morceau ».
- Les 8 premières touches = le corps, les 8 suivantes = la tête. Muter toute la
  seconde rangée = break percussif ; muter la première = break mélodique.

## 2. Pattern modèle, banks et rangement

**Pattern modèle** : un pattern de référence avec la grille ci-dessus déjà en
place (samples kick / rumble / clap / hats chargés, niveaux, envois, compresseur
master réglé). **Chaque nouveau pattern démarre par une copie du modèle.** Sans
ça, chaque pattern a sa propre logique et le set ne sonne pas cohérent.

**Banks** : une bank = un morceau, ou une bank = un « acte » du set. Les patterns
sont rangés **dans l'ordre où on compte les jouer**.

Convention de slots proposée (16 patterns par bank) :

| Slots | Usage |
|---|---|
| 1-8 | Progression du morceau dans l'ordre de jeu (intro → peak → sortie) |
| 9-12 | Variations pour les grosses bascules (drop, break total, double-time) |
| 13-15 | Patterns **réservoir** : à sortir si l'énergie retombe ou si la salle en redemande |
| 16 | Copie du pattern modèle (point de départ propre, jamais joué tel quel) |

**Longueur de pattern** : jusqu'à 128 pas = 8 pages de 16 pas = 8 mesures en
doubles croches. À 190 BPM : 1 mesure = 4 × 60 / 190 = 1,263 s, donc 8 mesures
= 10,1 s et une phrase de 32 mesures = 4 tours de pattern = 40,4 s. Caler les
longueurs sur les phrases de 8 / 16 / 32 mesures (cf. §6, principe 6).

## 3. Conseils qui changent tout en live

- **Le kick ne bouge jamais** d'un pattern à l'autre : même sample, même réglage.
  Le groove reste stable pendant que le reste change.
- **Une track dédiée aux transitions** (la 15), sinon rien pour faire monter la
  tension entre deux patterns. Avec les conditions FILL, les roulements partent
  avec le bouton fill sans changer de pattern.
- **Marge sur kick et basse** : ne pas pousser les volumes à fond. Le compresseur
  master sert de colle, pas de limiteur de secours.
- **Contrôle global** : maintenir [TRK] en tournant un bouton agit sur toutes les
  tracks à la fois. Idéal pour un filtre ou une décroissance sur tout le kit
  pendant un break.
- **Mutes plutôt que changements de pattern** : en techno, un même pattern dure
  longtemps. Construire des patterns « pleins » et faire vivre le morceau en
  mutant / démutant. Garder quelques patterns de variation pour les grosses
  bascules.
- **Temp save et reload** : avant de triturer un pattern en live, faire un temp
  save ([FUNC] + [YES]) ; [FUNC] + [NO] revient à l'état propre (cf.
  [[kb/perform-kit-temp-save]]).

## 4. Mutes : le vrai séquenceur du live

Un pattern plein + un ordre de mutes = un morceau. Ordre type pour une montée
(une entrée à la fois, toutes les 8 / 16 / 32 mesures) :

```
kick seul (1) → +rumble (2) → +hat fermé (4) → +basse (9) → +clap (3)
→ +percs (7-8) → +Id1 (12) → +lead (10) → +hat ouvert (5) → +ride (6) = peak
```

Et pour un break : muter 1 + 2 + 9 (kick, rumble, basse) en début de phrase,
laisser tourner atmo / Id1, riser sur la 15, démuter les trois **ensemble** sur le
1 de la phrase suivante.

C'est exactement ce que l'analyzer extrait d'un morceau de référence : pour chaque
section, quelles tracks sont actives. On lit la « partition de mutes » d'un
morceau qu'on aime pour s'en inspirer.

## 5. Fabriquer les FX de transition (track 15)

### Riser

- **Son de base** : bruit blanc, nappe ou son tenu qui dure longtemps. La machine
  **Stretch**, ou un sample en boucle, fait durer le son toute la montée.
- **La montée** :
  - un LFO lent en **rampe montante** sur le cutoff ou la hauteur, vitesse réglée
    pour qu'un cycle dure toute la montée, mode **one-shot** (ONE) pour qu'il ne
    reparte pas à zéro ;
  - ou des **p-locks progressifs** : cutoff et volume augmentent un peu à chaque
    trig.
  - Augmenter aussi progressivement l'**envoi reverb et delay** : ça épaissit.
- **L'arrêt** : couper net sur le temps où tout revient. Un trig à volume zéro,
  ou la fin de la condition FILL. Le contraste montée / silence fait tout l'effet.

### Riser + fill

Trigs du riser en condition **FILL**, kick en **NOT FILL**. On maintient fill :
le kick disparaît et le riser monte. On relâche : le kick retombe sur le temps.

### Variantes

- **Downlifter** : même principe en descente, pour retomber après un drop.
- **Impact** : gros coup grave avec beaucoup de reverb sur le premier temps.
- **Reverse** : crash ou reverb jouée à l'envers qui aspire vers le temps.

## 6. Principes de construction du set

1. **Penser en arc, pas en morceaux.** Une histoire sur une heure ou plus :
   montée d'énergie avec respirations, un ou deux sommets, puis descente ou fin
   marquante. Esquisser la courbe avant de jouer et y placer les patterns.
2. **La tension vient de la répétition, pas de la nouveauté.** Une boucle peut
   tourner longtemps si quelque chose évolue lentement (filtre, perc qui
   apparaît, note qui change). Erreur classique : trop changer, trop vite.
3. **Un changement à la fois**, idéalement toutes les 8, 16 ou 32 mesures.
   Plusieurs changements simultanés = moments forts seulement (drop, bascule).
4. **Le kick et la basse sont sacrés.** Couper le kick est l'outil le plus
   puissant, à utiliser rarement et au bon moment : un break sans kick marche
   d'autant mieux que le kick a tourné longtemps. Kick et basse doivent
   s'entendre en fréquences (sidechain, ou basse entre les kicks).
5. **Retrancher crée autant d'énergie qu'ajouter.** Le retour d'un élément après
   une absence fait plus d'effet que son ajout initial.
6. **Respecter les phrases de 8, 16, 32 mesures.** Une transition en début de
   phrase paraît naturelle, décalée elle paraît maladroite (sauf si voulu).
7. **Cohérence sonore** : mêmes familles de sons, tonalités proches (cf. Camelot
   dans [[../SPEC]]), tempo stable ou qui évolue doucement. Un set « pro »
   ressemble à un seul long morceau.
8. **Varier les textures autant que le rythme** : distorsion, reverb, filtrage,
   timbre des percs. Souvent plus efficace qu'un nouveau rythme.
9. **Préparer, mais garder de la marge pour improviser** : patterns rangés,
   transitions répétées, patterns réservoir (slots 13-15).
10. **Le silence et l'espace sont des instruments.** Laisser respirer
    fréquences et temps.
11. **Soigner le début et la fin.** Les deux premières minutes installent la
    crédibilité, les deux dernières sont ce dont on se souvient.
12. **S'enregistrer et réécouter**, par exemple via Overbridge sur le Mac : on
    entend les parties trop longues, les transitions ratées, les sons qui se
    marchent dessus.

## 7. Workflow : d'un morceau de référence à une bank

1. Grabber le morceau ([[../scripts/README|grab.py]]) puis générer ses stems
   (`stems.py --cleanup`).
2. `digitakt.py <slug>` : draft de bank, 1 section = 1 pattern, réparti sur la
   grille §1. Sorties : `library/digitakt/<slug>.json`, une note
   `library/digitakt/<slug>.md` (grilles + partition de mutes) et un `.mid` par
   pattern (16 canaux = 16 tracks) à enregistrer en live recording.
3. Lire la partition de mutes, repérer les Id1 / Id2 du morceau.
4. Reconstruire sur la DT2 à partir du **pattern modèle** : les grilles sont un
   point de départ, pas une transcription.


## 8. Pattern "Modèle"

Il n'y a pas de pattern « modèle » officiel dans la Digitakt : aucune fonction ne désigne un pattern comme template. C'est une convention que tu te fixes toi-même.

**1. Choisis un emplacement fixe**  
Prends un slot que tu n'utiliseras jamais pour jouer, toujours le même dans tous tes projets. Par exemple **H16**, le tout dernier pattern de la dernière bank. Il est facile à retrouver et ne gêne pas tes banks de set, qui commencent en A. Certains préfèrent **A01** et commencent leurs morceaux en A02. Le choix n'a aucune importance, seule compte la constance.

**2. Construis le modèle**  
Dans ce pattern, mets ta répartition des tracks : le kick sur la 1, le rumble sur la 2, les hats, la basse sur la 9, la track de transitions, etc. Charge des sons de base, règle les volumes, les envois d'effets, les LFO de riser, et pose quelques trigs FILL et NOT FILL déjà préparés. Laisse la séquence presque vide, ou juste un kick en 4/4.

**3. Copie-le pour chaque nouveau pattern**  
Hors GRID RECORDING, sélectionne le pattern modèle et fais [FUNC] + [RECORD] (copier). Va sur le pattern de destination, puis fais [FUNC] + [STOP] (coller). Tu repars de ton modèle à chaque fois. Variante sans quitter le modèle : [PTN], puis [TRIG] du modèle + [RECORD], et [TRIG] de chaque destination + [STOP] (manuel §10.1.1, §17 ; détail dans [[kb/copier-coller]]).

**4. Bonus : sauvegarde aussi les sons en kit**  
La Digitakt II peut sauvegarder l'ensemble des sons des 16 tracks en **kit**, via le menu PRESET/KIT. Sauvegarde ton modèle en kit : tu pourras recharger ces sons dans n'importe quel pattern, même dans un autre projet, sans écraser la séquence. Le pattern modèle donne la structure complète, le kit seulement la palette de sons.

**Astuce** : pour réutiliser ce modèle dans tous tes projets, garde un projet « TEMPLATE » sur le +Drive. Pour chaque nouveau set, charge-le et sauvegarde-le aussitôt sous un nouveau nom.

## 9. Le grave : kick, rumble, basse

### Fabriquer le rumble (track 2)

1. **Source** : le même sample que le kick (track 1), trigs sur chaque temps.
   Envoi reverb à fond (decay long, un peu de pre-delay, aigus coupés),
   overdrive poussé, enveloppe d'amplitude très courte pour ne garder que la
   queue.
2. **Resampler** : la reverb est un envoi partagé, donc on fige le rumble en
   sample. Muter tout sauf la 2, `[SAMPLING]` : `SRC` = MAIN (sortie main,
   reverb comprise), `R.LEN` = 16 pour une mesure (cf.
   [[kb/sampling-resampling]]).
3. **Sculpter** le sample : passe-bas (Lowpass 4) bas avec un peu de résonance,
   overdrive, accordé sur la tonique (cf. §11).
4. **Le faire respirer** : sidechain du compresseur (cf. §10), attaque lente sur
   l'AMP, ou LFO de volume calé sur la noire et relancé à chaque trig.
5. **Équilibrer** : moins fort que le kick, pan centré, jugé au casque ou sur un
   vrai sub. Sauvegarder en **preset**.

### Placement en tribe

- **Défaut** : rumble **sur le même pas que le kick**, avec ducking (il gonfle
  derrière l'attaque) et release courte. Basse en **contretemps**.
- À 180-200 BPM, une double-croche ≈ 80 ms : un rumble sur le pas suivant crée
  un galop qui empiète sur la basse en contretemps. À éviter, sauf variante
  **sans basse** : le rumble roule sur les doubles-croches entre les kicks et
  joue lui-même le rôle de basse.
- Rumble en **NOT FILL** : il disparaît avec le kick pendant les breaks.

### Basse en contretemps

- **Attaque franche** (quelques ms pour éviter les clics), **decay court**,
  retombée avant le kick suivant.
- **Overdrive** pour le mordant, enveloppe de filtre rapide pour le claquement.
- La rondeur est une **variation**, pas la base : filtre plus fermé en intro qui
  s'ouvre avec un LFO lent ou des p-locks.

### Partage des fréquences

Séparation **dans le temps** (contretemps) **et** en fréquences. Ordres de
grandeur, à ajuster à l'oreille :

| Élément | Zone | Outil DT2 (filtre base-width) |
|---|---|---|
| Kick | sub et grave, patron du sub | léger passe-haut contre l'infra |
| Rumble | sub, entre les coups de kick (ducking) | passe-bas fermé, ne monte pas dans les médiums |
| Basse | bas-médium + harmoniques de saturation | passe-haut un peu monté, laisse le sub au kick |

- Le chevauchement est normal : éviter seulement la **même zone au même moment**.
- Kick, rumble et basse **accordés ensemble** se renforcent au lieu de s'annuler.
- Les filtres de la DT2 se règlent sur une échelle de valeurs, **pas en Hz**.
  Étalonner une fois via Overbridge + analyseur de spectre (SPAN) et noter
  les repères dans `kb/` ; la machine **Equalizer** est plus adaptée au réglage
  de bandes *(à vérifier sur la machine : affichage en Hz, le manuel ne le
  dit pas ; cf. [[kb/filtres]])*.

## 10. Compresseur master : routing et sidechain

Deux réglages distincts :

- **Routing** (qui est compressé) : [FUNC] + [FLTR] → COMPRESSOR ROUTING, on
  ajoute / retire les tracks avec les touches de trig. Page 2 : entrée externe
  L / R.
- **Source** (qui déclenche) : sur la page du compresseur, une track, l'ensemble
  des tracks non routées (« /COMP ») ou l'entrée externe.

**Réglage sidechain du set** : kick (1) **hors** du routing et en **source** ;
rumble, basse, atmo (et éventuellement percs) dans le routing.

| Paramètre | Départ |
|---|---|
| Ratio | ≥ 4:1 |
| Attaque | la plus rapide |
| Release | courte à moyenne, remonte juste avant le kick suivant |
| Seuil | descendre jusqu'au creux audible, puis remonter un peu |
| Make-up | compenser sans exagérer |
| Mix | 100 % pour un ducking franc, moins pour adoucir |

**Kick fantôme** : dupliquer le kick sur une track libre (16 si non utilisée en
MIDI), la retirer du main dans l'AUDIO ROUTING, la mettre en source. Le vrai
kick peut alors être muté / NOT FILL pendant les breaks sans arrêter le
pompage (cf. [[kb/send-fx-compresseur]]) *(à vérifier sur la machine : une
track hors main déclenche-t-elle encore le sidechain ? le manuel ne le dit
pas)*.

**Arbitrage** : avec ce routing, le compresseur est un ducker, plus une colle
globale. Si on veut les deux : pompage par **LFO de volume** sur les tracks, et
compresseur en colle légère (ratio 1,5-2:1, 1-3 dB, attaque lente).

Bonnes pratiques générales : sidechainer d'abord ce qui est grave, ne pas
écraser les transitoires du kick, comparer à volume égal, garder ~-6 dB de marge
avant le master si on finit dans le DAW (multipiste Overbridge).

## 11. Tonalité et harmonie

### Le kick donne la tonalité

1. Choisir le kick pour son **son et son impact**.
2. **Mesurer sa note** sur la queue (pas l'attaque) : accordeur ou analyseur via
   Overbridge (~55 Hz ≈ La, ~65 Hz ≈ Do), ou à l'oreille contre une sinus.
3. Fixer la **tonique du morceau** sur cette note : KEYBOARD SETUP de la track →
   gamme + tonique (cf. [[kb/keyboard-gammes]]).
4. Accorder rumble (même TUNE que le kick au départ), basse (tonique ou quinte),
   puis lead et Id dans la gamme.

- Ne pas tordre un kick de plus de quelques demi-tons (mou vers le bas, cartoon
  vers le haut, durée modifiée en Repitch) : **choisir des kicks proches** de la
  tonalité visée.
- **Nommer les samples avec leur note** : `kick_tribe_F#.wav`.
- Un kick court et sec n'a pas de note perceptible : c'est alors la basse qui
  fixe la tonalité.

### Modes et changements de tonalité

- Harmonie **statique** par défaut : une tonique qui tourne longtemps = transe.
- **Dans un morceau** : pas de changement de tonalité. Changer de **mode sur la
  même tonique** pour colorer (dorien → phrygien assombrit : la sixte majeure
  éclaire, la seconde mineure oppresse), ou faire bouger la basse sur un ou
  deux degrés quelques mesures.
- **Entre les parties** : tonalités voisines (quinte, quarte, relatif — Camelot,
  cf. [[../SPEC]]) ; montée d'un demi-ton / ton pour un coup d'énergie (une ou
  deux fois max) ; pattern pont sans tonalité marquée ; ou **note pivot**
  commune tenue par un drone ou un Id.
- Changer de tonalité = réaccorder le grave : **presets par tonalité**
  (`rumble_D`, `rumble_F`) ou TUNE dans les patterns concernés.

### Progressions d'accords

- **Pédale** : kick et rumble sur la tonique, les accords bougent au-dessus.
- Progressions types : dorien i7 → IV7 (Dm7 → G7) ; mineur i → ♭VI → ♭VII ;
  phrygien i → ♭II (tension, vers le mental). Couleurs min7 / min9 / min11 /
  sus, noyées de reverb et delay (dub techno).
- **Changer d'accord lentement** (toutes les 2 à 4 mesures), notes en p-locks,
  conditions de trig pour alterner sur plusieurs cycles.
- Track audio = **monophonique**. Accords via : samples d'accords transposés
  (méthode dub techno), une voix par track, ou track MIDI (4 notes / pas) vers
  un synthé externe.
- **Mélodies aléatoires dans le mode** : gamme fixée dans KEYBOARD SETUP, NOTE
  PARAM (menu PERSONALIZE) réglé pour que le bouton NOTE suive la gamme, puis
  p-locks de notes + trig chance / conditions + longueur polymétrique. Éviter
  un LFO random sur le pitch (non quantifié sur la gamme).

## 12. Tracks identité (Id1 / Id2)

Le socle (grille §1) garantit la **stabilité**, les Id portent le
**caractère** : c'est par elles qu'on reconnaît un pattern et qu'on tient les
arcs du set.

- **Écrire les Id d'abord** (deux ou trois par partie), le socle vient ensuite
  les servir.
- **Introduire → développer → rappeler** : un Id apparaît discrètement,
  s'impose, disparaît, revient plus tard comme rappel.
- **Faire voyager un motif** entre les parties : le même Id transformé (lent,
  filtré, noyé de delay en dub → haché sur la grille en DnB → saturé, martelé
  en tribe → ligne acid vers le mental).
- **Ponts** : garder l'Id de la partie précédente pendant que le nouveau socle
  s'installe, puis faire apparaître le nouvel Id.
- Outils : **preset locks** (variantes de son par pas via le Preset Pool),
  **conditions de trig** (1:2, 3:4, FILL), **longueur polymétrique** (12 ou
  14 pas contre 16), **une version d'Id = un preset**.

## 13. Set multi-styles : kits, banks, presets

### Hiérarchie

| Élément | Contient | Vit où |
|---|---|---|
| **Projet** | patterns, songs, slots de samples, Preset Pool, réglages | +Drive (1 set = 1 projet) |
| **Bank de patterns** | 16 patterns | Dans le projet |
| **Pattern** | séquence 16 tracks **+ sa copie des sons** | Dans une bank |
| **Song** | lignes : pattern, répétitions, longueur, mutes, tempo | Dans le projet (patterns du même projet uniquement) |
| **Kit** | les sons des 16 tracks (photo à un instant donné) | Bibliothèque +Drive |
| **Preset** | le son d'une track (sample + réglages) | Banks de presets, bibliothèque +Drive |
| **Preset Pool** | sélection de presets sous la main | Dans le projet |

- Banks de presets et banks de patterns n'ont **aucun rapport** : les premières
  rangent la bibliothèque de sons, les secondes les séquences du projet.
- **Charger = copier** : un preset ou kit chargé perd le lien avec l'original.
  Pour mettre à jour l'original, le réenregistrer.

### Workflow

1. Construire les sons sur les tracks → sauvegarder les réussis en **presets**.
2. Les 16 tracks validées → sauvegarder en **kit**.
3. Pattern modèle (§8) = kit + routing compresseur + FILL / NOT FILL préparés.
4. Copier le modèle dans la bank → développer les patterns.
5. **Song** pour l'enchaînement. Sauvegarder le projet ([FUNC] + [SETTINGS]) à
   chaque étape.

### Un kit et une bank par couleur

Exemple : bank A dub → bank B DnB → bank C tribe, chacune avec son kit et son
pattern modèle.

- **Arbitrage avec §3** : le kick ne bouge pas *à l'intérieur d'un acte* ; il
  change avec le kit d'un acte à l'autre.
- La **grille §1 reste identique** dans les trois kits : les réflexes de mutes
  et de fills restent valables tout le set.
- **Presets fil rouge** partagés entre kits : une texture retravaillée, les FX
  de transition (15), une perc signature ou un vocal (14), mêmes réglages de
  reverb et delay.
- **Jonctions** : derniers patterns d'une bank et premiers de la suivante pensés
  comme ponts, en mélangeant des presets des deux kits.

### Transitions de tempo

- **Demi-temps** : une DnB à 172 se sent à 86 ; finir la partie lente en
  demi-temps, puis doubler l'énergie.
- **Pattern pont** sans kick (nappe, reverb, riser) pendant lequel on change de
  tempo.
- **Rupture assumée** : silence ou impact, puis nouvelle partie franche.
- Tempo global au projet ou par pattern : `[TEMPO]`, puis `[FUNC]` + DATA
  ENTRY E pour changer de mode. En song, `ROW TEMPO` fixe le BPM par ligne ;
  un tempo de song écrase tous les autres (cf. [[kb/tempo-metronome]],
  [[kb/song-mode]]).

### Tribe vs mental (tendances, frontières floues)

| | Tribe | Mental |
|---|---|---|
| Groove | percussif, toms, motifs tribaux | linéaire, martelé |
| Kick | dur | encore plus saturé, agressif |
| Basse | contretemps rebondissante | souvent remplacée par le rumble / acid |
| Mélodie | motifs tribaux | lignes acid (type 303), sombre, hypnotique |

Le rumble n'est pas le critère distinctif : tempo, traitement du kick, place des
percs et nature des sons mélodiques le sont. Passage tribe → mental : l'Id
mélodique devient acid, l'Id rythmique perd ses percs, mode vers le phrygien.

## 14. Aide-mémoire machine

| Action | Manip | Statut |
|---|---|---|
| Mode keyboard, gamme, tonique | [KEYBOARD] ; [FUNC] + [KEYBOARD] = KEYBOARD SETUP (cf. [[kb/keyboard-gammes]]) | manuel §8.5.2 |
| Trig mode (Tracks / Velocity / Retrigs / Slice / Preset Pool) | [FUNC] + [HAUT] / [BAS] | manuel §8.5.4 |
| Preset Pool en trig mode | pool vide = toutes les touches jouent le même son ; remplir via PRESET/KIT | forum |
| Step recording | [RECORD] + [STOP] ; choisir le pas ([TRIG] ou [LEFT] / [RIGHT]), [FUNC] + [TRIG n] pose un trig sur la track n, ou [KEYBOARD] maintenu + [TRIG] pour une note ; le pas avance ; [NO] = silence ou effacement ; [RECORD] + double [STOP] = mode JUMP | manuel §10.2.4 |
| Grid / live recording | [RECORD] / [RECORD] + [PLAY] | |
| Fill | [PAGE] maintenu hors grid recording ; [YES] + [PAGE] = un tour de pattern ; [PAGE] + [YES] en lâchant [PAGE] d'abord = verrouillé, [PAGE] libère | manuel §10.8.4 |
| Effacer un paramètre locké sur toute la track | LIVE REC : maintenir [NO] + maintenir le bouton du paramètre (efface au fil de la lecture) ; sur un seul trig : [TRIG] + appui sur le bouton | manuel §10.8.1 |
| Effacer les p-locks de toutes les tracks | Pas de commande dédiée : [FUNC] + [NO] = reload temporaire du pattern (retour au dernier temp save). Un trig effacé puis reposé perd ses locks | manuel §10.8.1, §17 |
| Effacer trig + locks | GRID REC : [TRIG] + [PLAY] (cf. [[kb/copier-coller]]) | manuel §17 |
| Factory reset | [FUNC] maintenu à l'allumage → FACTORY RESET ; écrase le slot projet 1, samples d'usine et persos conservés. **Jamais** FORMAT +DRIVE | Elektron |
| Écouter la DT2 sur le Mac | mode USB Overbridge + Overbridge Engine ; monitoring via DAW, GarageBand ou LadioCast. BlackHole inutile pour ça | |
| Injecter les `.mid` du §7 | sortie MIDI du DAW → Digitakt II, canal = track (ou auto = track active), horloge + transport depuis le DAW, LIVE REC ([RECORD] + [PLAY]) ; quantize auto : [RECORD] + double [PLAY] ; après coup : [FUNC] + [TRIG PARAMETERS] | manuel §10.2.3, §10.6 ; import multi-canal *(à vérifier, cf. [[kb/midi-config]])* |

**P-locks** : maintenir un trig + tourner un bouton = valeur pour ce pas
seulement. **Trig-less lock** : lock sans note, pour modifier un son en cours.
**Preset lock** : un preset du pool assigné à un pas.

## Liens

- [[../SPEC]] — Phase 7 (Digitakt)
- [[../technique/anatomie-kick]] — pourquoi le kick ne bouge jamais

#digitakt #doctrine #live
