---
tags: [digitakt, doctrine, live, set, elektron]
source: "https://youtu.be/y_YijodbZYI"
updated: 2026-10-06
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
| 2 | **Rumble / sub** | 30-80 Hz | Souvent le kick resamplé + reverb + filtre passe-bas ; joue entre les kicks |
| 3 | **Clap / snare** | 200 Hz-2 kHz | Temps 2 et 4 en four-on-floor, plus libre en tribe |
| 4 | **Hat fermé** | 6-12 kHz | Contretemps, doubles croches |
| 5 | **Hat ouvert** | 5-10 kHz | Un seul bien placé vaut mieux qu'un empilement |
| 6 | **Ride** | 4-10 kHz | Couleur de « plein régime », sort en peak |
| 7 | **Perc A** | variable | Toms, rims… |
| 8 | **Perc B** | variable | Shakers, claves, métalliques… |

### Mélodique et textures — tracks 9 à 16 (seconde rangée)

| Track | Rôle | Bande dominante | Notes |
|---|---|---|---|
| 9 | **Basse** | 50-300 Hz | Sacrée avec le kick ; joue entre les kicks ou sidechainée |
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
  save. [FUNC] + [NO] revient à l'état propre *(combinaison de sauvegarde à
  vérifier)*.

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
## Liens

- [[../SPEC]] — Phase 7 (Digitakt)
- [[../technique/anatomie-kick]] — pourquoi le kick ne bouge jamais

#digitakt #doctrine #live
