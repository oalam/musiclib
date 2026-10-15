---
tags: [digitakt, kb, theorie, kt]
theme: Tensions et lignes
lot: 2
ordre: 7
styles: [acidcore, tribe, industrial, hard techno]
statut: draft
updated: 2026-10-15
---

# KT7 — Tensions et lignes

**En une phrase** : une ligne techno vit sur trois à cinq notes sûres
(la pentatonique) et tire sa tension d'une ou deux notes dangereuses
placées exprès, blue note, seconde mineure, triton, chromatisme ; la
compétence n'est pas de connaître les gammes mais de doser la note qui
frotte et le moment où elle revient à la tonique.

## Signature

| Élément | Théorique | Mesuré | Lecture |
|---|---|---|---|
| Ligne tribe | 1, b3, 4, 5, b7 (pentatonique mineure), 2 à 3 notes jouées | 11 morceaux sur 32 en pentatonique mineure, 7 en blues | le détecteur voit la pentatonique, parfois la blue note (blues = pentatonique + b5) |
| Ligne acid | 1, b2, 5, octave ; slides sur b2 et b5 | neurotribe `Esus2 F5`, six ou sept B blues, ktc C# blues | la b2 en mouvement de basse, la b5 dans le « blues » détecté |
| Industrial | clusters, triton, atonalité contrôlée | beauz `E5 G#dim E Fdim` (hard techno) | des accords diminués (triton inclus) entre les quintes nues |
| Blue note | b5 de passage entre 4 et 5 | 7 morceaux « blues » : six ou sept, ktc, beauz, maureen, tim reaper, 2hot2play, floxytek roots | la b5 est assez présente pour faire basculer la détection |

Passe harmonique : `scripts/kt_signatures.py --harmony`, table dans
[[_index]]. Les étiquettes « blues » de la passe sont la trace des blue
notes et des slides acid ; les « dim » de Beauz, la trace des tritons.

## Vocabulaire

- **Pentatonique mineure** : 1 b3 4 5 b7 (A C D E G) ; cinq notes sans
  demi-ton, aucune n'est fausse contre la tonique.
- **Blue note** : la b5 (Eb sur A) glissée entre 4 et 5 ; la
  pentatonique plus la blue note = gamme blues.
- **Seconde mineure** (b2) : un demi-ton au-dessus de la tonique (Bb sur
  A) ; la tension phrygienne (KT6).
- **Triton** : six demi-tons (A-Eb), l'intervalle le plus instable ; il
  coupe l'octave en deux et ne « penche » d'aucun côté.
- **Chromatisme** : note hors gamme utilisée de passage entre deux notes
  de la gamme (A → Bb → B).
- **Note de passage, broderie** : note brève qui relie (passage) ou
  entoure (broderie) une note de la gamme.
- **Résolution** : retour d'une note tendue vers une note stable
  (b2 → 1, b5 → 5 ou 4, 7 → 1).
- **Cluster** : trois notes ou plus à un demi-ton ou un ton d'écart,
  jouées ensemble ; une texture, plus un accord.
- **Atonalité contrôlée** : pas de tonique affirmée dans la ligne, mais le
  grave (KT5) en tient une ; l'industrial vit là.
- **Contour** : forme de la ligne (monte, descend, zigzague) indépendante
  des notes exactes ; à trois notes, c'est le contour qu'on retient.

## Pourquoi ça marche

**Concret d'abord : une ligne de huit pas, quatre tensions.** Tonique A,
ligne sur la track 10 en pentatonique : `A . C . D . E .` sur les pas 1,
3, 5, 7. Quatre variantes en changeant **une** note :

| Variante | Ligne | Note changée | Effet |
|---|---|---|---|
| Pentatonique | A C D E | aucune | sûre, tourne sans fatiguer |
| Blue note | A C Eb E | D → Eb | « blues », la b5 glisse vers la quinte |
| Phrygien | A Bb D E | C → Bb | oppressant, la b2 veut retomber sur A |
| Triton | A C Eb D | E → Eb en fin de ligne | instable : la ligne ne se pose pas |
| Sensible | A C E G# | D → G# | tire vers l'octave, « dramatique » |

Le tableau est l'exercice 1. Ce qu'on entend : la tension n'est pas dans
la gamme, elle est dans **une note et sa place** (début, fin, note
tenue, note de passage).

**Pourquoi la pentatonique est sûre.** Ses cinq notes n'ont aucun
demi-ton entre elles ; aucune ne frotte avec la tonique tenue au grave
(KT5) ni avec la quinte. On peut y jouer n'importe quel ordre, à
n'importe quel rythme (KT1, KT2) sans fausse note : c'est la raison pour
laquelle la passe harmonique la détecte dans 18 morceaux sur 32 (mineure
ou blues). Avec `KB FOLD` ON et `KB SCALE` = PENTATONIC MINOR, les 16
touches de la DT2 sont toutes bonnes (fiche [[../keyboard-gammes]]).

**Les intervalles qui frottent, et contre quoi.** Une note est tendue
par rapport à ce qui sonne en même temps : la tonique du grave, et la
note précédente de la ligne.

| Intervalle contre la tonique | Demi-tons | Rapport approché | Perception |
|---|---|---|---|
| Octave | 12 | 2:1 | fusion |
| Quinte | 7 | 3:2 | stable |
| Quarte | 5 | 4:3 | stable, suspendue |
| Tierce mineure | 3 | 6:5 | couleur, sombre |
| Seconde majeure | 2 | 9:8 | frotte peu |
| Seconde mineure | 1 | 16:15 | frotte fort, veut résoudre |
| Triton | 6 | 45:32 | instable, ne résout nulle part |

Plus les nombres du rapport sont petits, plus les harmoniques des deux
notes coïncident et plus l'intervalle est stable. La b2 (16:15) et le
triton (45:32) sont tendus parce que presque rien ne coïncide. En acid,
le **slide** fait entendre le passage d'une note stable à une note tendue
sans paliers : c'est le glissement lui-même qui porte la tension (KT11).

**Doser : la règle du retour.** Une tension n'existe que si elle est
résolue ; une b2 tenue 32 mesures devient la nouvelle normale. Trois
dosages qui marchent :

1. **note de passage** : la tension dure un pas et retombe sur la tonique
   ou la quinte ;
2. **note de fin de phrase** : la tension clôt la ligne de 8 ou 16 pas,
   le pas 1 suivant la résout (lien avec le phrasage, KT9) ;
3. **note tenue par le drone** (track 11) : une b2 ou un triton tenus 8
   mesures sous une ligne pentatonique, puis retour à la tonique :
   modulation de tension sans bouger la ligne.

Le générateur acid 9.A fait exactement cela : marche aléatoire sur les
degrés de la gamme choisie (`--scale PHRYGIAN`), `type` bas pour des pas
conjoints autour de la tonique, haut pour des sauts.

**Atonalité contrôlée.** L'industrial et le hard techno de Beauz jouent
des accords diminués et des clusters au-dessus d'un grave fixe : la ligne
ne dit pas de tonique, le grave la dit pour elle. L'oreille accepte à
peu près n'importe quoi au-dessus de 1 kHz tant que le sub reste
accordé : les Id bruitées, les samples métalliques pitchés hors gamme
(track 13) sont de la tension gratuite, à condition que la 1, la 2 et la
9 restent justes (KT5).

## Sur la DT2

Grille de la [[../../doctrine]] §1 : basse 9, lead 10, drone 11, Id1 13.
Gestes : [[../keyboard-gammes]], [[../parameter-preset-locks]] (p-locks
de `NOTE`).

1. **Quatre tensions, une note (10 min).** Tonique du kick, track 10,
   ligne `A . C . D . E .` (degrés 1, b3, 4, 5) sur 8 pas. Quatre copies
   du pattern (fiche [[../copier-coller]]) : remplacer une seule note par
   la b5, la b2, le triton en fin de ligne, la 7 majeure, par p-lock de
   `NOTE` avec `NOTE PARAM` = CHRO. Chaîner, 8 mesures chacune, noter la
   variante qui tient le plus longtemps sans lasser.
2. **Passage, fin, drone (10 min).** Même ligne pentatonique. A : Bb en
   note de passage (pas 2, vélocité 60). B : Bb sur le pas 15, résolue
   par le A du pas 1. C : ligne intacte, Bb tenue sur la track 11 pendant
   8 mesures puis A. Trois placements de la même note.
3. **Tirages acid (5 min).** Générateur 9.A (vue « Acid · MIDI »), `--root`
   sur la tonique du kick, `--scale PENTATONIC MINOR` puis `PHRYGIAN`,
   `type` 3 puis 12. Envoyer sur la 10, garder le tirage dont les notes
   tendues tombent en fin de phrase.

## Pièges

- Deux tensions à la fois (b2 et triton dans la même ligne de 8 pas) ne
  font pas deux fois plus de tension, elles effacent la tonique.
- Une tension dans le grave (basse 9 sur la b2 sous un kick sur la
  tonique) bat et brouille (KT5) : les tensions vivent au-dessus de
  200 Hz, sur la 10, 11, 13.
- `NOTE PARAM` = SCALE empêche de poser une note hors gamme au bouton :
  passer en CHRO pour la note tendue, ou choisir une gamme qui la
  contient (BLUES, PHRYGIAN).
- Un slide acid vers une note tendue sans retour à la tonique dans les
  deux pas suivants sonne faux, pas tendu.
- Le détecteur de gamme des sidecars est instable sur ces lignes (marge
  faible, « blues » et « pentatonique majeure » relative) : ne pas lui
  demander la tonalité d'un morceau, lire la tonique du grave.

## Ressources

- Attack Magazine, *How to make an acid house bassline* :
  <https://www.attackmagazine.com/technique/tutorials/how-to-make-an-acid-house-bassline/> `[V]`
- MusicTech, *Chicago-style acid bassline* :
  <https://musictech.com/guides/essential-guide/how-to-create-a-chicago-style-acid-house-bassline> `[V]`
  (slides et accents d'abord, 13 / 15 pas).
- Attack Magazine, Passing Notes *5 Tips To Improve Your Synth
  Basslines* (index) : <https://www.attackmagazine.com/technique/passing-notes/> `[V]`
- musictheory.net, intervalles : <https://www.musictheory.net/lessons> `[V]`
- Attack Magazine, Beat Dissected *Industrial techno* :
  <https://www.attackmagazine.com/technique/beat-dissected/industrial-techno/> `[V]`
- Générateur acid 9.A : `scripts/analyzer/acid.py` (`--scale`, `--type`,
  `--density`, `tie_mode`).

## Liens

[[_index]] · [[../keyboard-gammes]] · [[../parameter-preset-locks]] ·
[[../copier-coller]] · [[../../doctrine]] §11, §12 · KT5
[[kt-tonalite-du-grave]] · KT6 [[kt-modes-techno]] · KT9
[[kt-phrasage-tension]] · KT11 (acid core), KT16 (industrial), à rédiger
