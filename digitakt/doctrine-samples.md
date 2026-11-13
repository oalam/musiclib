---
tags: [digitakt, doctrine, samples, elektron]
source: "https://www.youtube.com/watch?v=aTq7VydK8Bk"
updated: 2026-11-13
status: living document
---

# Doctrine Digitakt II — gestion des samples

Source : Synthackers (James Orvis), « Digitakt II Course: Comprehensive
Guide to Sample Management »
(<https://www.youtube.com/watch?v=aTq7VydK8Bk>). Les principes de la vidéo
sont adaptés à notre export (`samples.py --export` pour la lib, export des
lives) ; arbitrés le 2026-11-10. Les principes valent pour la lib comme
pour les lives : tout ce qui part sur le +Drive passe par la même chaîne.

**Exemple concret** : un kick du pack Hodge arrive dans
`samples/01 KICK/HARD/BD F Hodge driver.wav`, au format 48 kHz / 16 bits, au
niveau des autres kicks. Dans la track 1, remplacer ce kick par un autre ne
change pas le niveau du mix.

## Arbre : dossiers numérotés dans l'ordre de la grille

La DT2 trie par ordre alphabétique : un numéro en tête de dossier impose
l'ordre. On numérote les dossiers **dans l'ordre des tracks de [[doctrine]] §1**. On
cherche alors un son de la track 1 en haut de la liste, un son de la track
15 en bas. Les branches DRUMS / TONAL / LOOPS de 7.J8 disparaissent. Les
**sous-catégories de 7.J8 restent** (`01 KICK/HARD/`) : sans elles, un
dossier dépasse 150 kicks.

Correspondance (dossier, codes, track de [[doctrine]] §1), validée le 2026-11-10 :

| Dossier | Codes | Track |
|---|---|---|
| `01 KICK` | BD | 1 |
| `02 RUMBLE` | RM | 2 |
| `03 CLAP` | CP | 3 |
| `04 SNARE` | SD | 3 |
| `05 TOM` | TM | 4 |
| `06 PERC` | PC | 4 |
| `07 HAT` | HH | 5 |
| `08 OPEN HAT` | OH | 5 |
| `09 CYMBAL` | CY | 6 |
| `10 BREAK` | BR | 7-8 |
| `11 DRUM LOOP` | DL | 7-8 |
| `12 PERC LOOP` | PL | 7-8 |
| `13 BASS` | BS | 9 |
| `14 BASS LOOP` | BL | 9, 13 |
| `15 SYNTH` | ST | 10 |
| `16 PAD` | PD | 11 |
| `17 VOX` | VX | 12 |
| `18 MELO LOOP` | ML | 13-14 |
| `19 FX` | FX | 15 |
| `20 SAMPLE` | samples et resamples maison, rangés par code | 16 |

Les lives gardent leur arbre à plat (`<live>/<BANQUE>/`, kit `0-KIT`) : les
banques y suivent déjà l'ordre du set.

## Nommage : on garde le nôtre

La vidéo nomme `BD_HODGE_driver-Fm` : code, pack, description, tonalité. On
garde notre format `<CODE> [BPM|note] <desc> <pack>` (18 caractères). Le
point commun avec la vidéo est retenu : **le code en tête, même dans le
dossier du code**, parce que la liste des samples d'une track n'affiche que
le nom du fichier.

## Format : 48 kHz / 16 bits, dither à la réduction

L'export écrit chaque fichier en **48 kHz** (fréquence native de la DT2) et
en **16 bits**, avec dither quand la source a plus de 16 bits. La conversion
est maîtrisée à l'export au lieu d'être laissée à Transfer. Le poids et la
RAM d'un fichier deviennent prévisibles. La stéréo est conservée (7.J).

## Niveaux : la ligne inclinée, puis un plafond de crête

**D'où ça vient** (vidéo, 07:25-11:51). On n'égalise pas un niveau en dB
par famille. On mixe chaque son **sur une ligne** :

1. Dans Pro-Q, l'analyseur est incliné de **4,5 dB par octave**. Le spectre
   d'un mix équilibré devient alors à peu près horizontal.
2. On règle le gain de chaque son pour que **le haut de son spectre touche
   une même ligne horizontale**. C'est vrai pour le kick, le clap, la perc,
   la basse.
3. Les sons les plus forts, kicks et basses, lus au fader à 0, montent
   alors vers **-6 dBFS de crête**. C'est le seul chiffre en dB de la
   méthode. Pas de normalisation à -0,2 dB.

**Résultat** : on échange un clap ou une perc contre un autre et le pattern
reste mixé, à quelques dB près. Dans la vidéo, ça donne « 80 à 90 % »
d'un bon équilibre. C'est ce qui permet de construire un pattern en live
sans retoucher les niveaux.

**Chez nous** (arbitré le 2026-11-11) :
- **Même règle partout** : à la main dans Live avec Pro-Q 4 pour les sons
  fabriqués ([[kb/tutos/maison-premaster-samples]]), et automatiquement à
  l'export pour tout ce qui part. L'export calcule le spectre lissé du son,
  l'incline de +4,5 dB/oct et règle le gain pour que son maximum touche la
  ligne. Un son déjà préparé dans Live ressort à un gain proche de 0 dB.
- **Décalage par famille** autour de la ligne : 0 dB par défaut ; HH, OH,
  CY un peu au-dessus (dans la vidéo, les hats dépassent un peu, par goût) ;
  PD en dessous (« faible niveau », [[doctrine]] §1). Valeurs à fixer à
  l'oreille.
- **Plafond de crête à -6 dBFS** : il vaut pour le grave (BD, RM, BS, BL)
  et borne aussi tous les autres sons. Si la ligne demande plus, le gain
  s'arrête au plafond.
- Placement de la ligne : réglé une fois, de sorte que les kicks de
  référence arrivent à -6 dBFS de crête.

## Pré-mastering dans Live (arbitré le 2026-11-11)

**Où** : les projets Live du set, `<MEDIA>/Sets/solaris/<banque>/` (par
exemple `C Groove (A# aeo 143)/kickbass_tribecore_A#_143/`), dans le projet
modèle à deux groupes OB et SD ([[kb/tutos/maison-sounddesign-grave-live]]
§1.3). **Quoi** : chaque sample fabriqué est préparé avant son rendu, selon
sa **nature** (one-shot, boucle, tonal) et sa **track** dans la grille
([[doctrine]] §1). Le but est qu'il se mixe tout seul sur la DT2.

**Pourquoi dans le sample et pas sur la machine** : une track de la DT2 n'a
qu'un filtre, et on le garde pour le jeu (balayages, ouverture d'une
montée), pas pour corriger. Le compresseur master et l'overdrive de la
machine finissent le son ([[doctrine]] §10). Le sample arrive donc **propre,
à sa place dans le spectre, avec de la marge**, jamais fini ni écrasé.

### La chaîne, dans l'ordre

Sur la piste SD du projet modèle, après la source (Vital, Kick 3, sample
de pack, resample de la DT2 par Overbridge) :

1. **Début et fin** : l'attaque tombe sur le premier échantillon (aucun
   silence en tête, sinon le trig de la DT2 est en retard). La queue est
   coupée à la longueur utile au tempo de la banque, avec un fondu de sortie
   de 5 à 20 ms. La RAM du projet DT2 se gagne ici.
2. **EQ correctif** : coupure sous 20 Hz pour tout le monde (kick
   compris : c'est sous l'audible, pas le sub du kick), passe-haut de la
   famille (table ci-dessous), puis
   creux étroits sur les résonances gênantes. Toujours en phase naturelle
   ou à latence nulle : la phase linéaire fait un pré-écho devant les
   attaques des kicks et des percussions.
3. **Image stéréo** : mono sous 120 Hz pour tout le monde, entièrement mono
   pour le grave (BD, RM, BS : le rendu mono divise aussi la RAM par deux).
   La stéréo n'est gardée que là où elle sert (OH, CY, PD, FX, ML).
4. **Dynamique** : légère, et seulement si le son le demande (pic isolé
   d'une boucle, note d'une ligne plus forte que les autres). Jamais de
   limiteur ni de compression sur le kick : la marge sert à l'overdrive de
   la DT2.
5. **Niveau sur la ligne** : analyseur de Pro-Q 4 incliné à 4,5 dB/oct,
   gain de sortie réglé pour que le haut du spectre touche la ligne, avec le
   décalage de la famille ; crête au plus à -6 dBFS (section « Niveaux »).
   L'export ne fait plus alors qu'un ajustement proche de 0 dB.
6. **Écoute dans le pattern** : le sample est jugé joué par la DT2 (groupe
   OB, Overbridge), avec le kick et la basse de la banque, au tempo de la
   banque. Il ne part en rendu qu'une fois validé là ; le +Drive ne reçoit
   pas de brouillons.
7. **Rendu** : 48 kHz, 24 bits, sans normalisation, sans queue ajoutée,
   mono pour le grave ([[kb/tutos/maison-grave-rendu-dt2]] §7.1). L'export
   fait ensuite le passage en 16 bits.

### Par track : points de départ

Valeurs de départ, à corriger à l'oreille. La bande visée est celle de
[[doctrine]] §1, et le partage du grave suit [[doctrine]] §9.

| Track | Codes | Passe-haut | Stéréo | Dynamique, longueur | À surveiller |
|---|---|---|---|---|---|
| 1 | BD | sous 20 Hz seulement ([[doctrine]] §9) | mono | aucune compression ; 150-300 ms avec rumble, jusqu'au kick suivant en kickbass | note de la queue, click au-dessus de 2 kHz |
| 2 | RM | sous le sub du kick (le rumble vit en 60-150 Hz) | mono | boucle au tempo, duck déjà dans le sample | qu'il ne masque pas le thump du kick |
| 3 | SD, CP | 150-200 Hz | légère | queue courte | 2-4 kHz agressifs |
| 4 | TM, PC | 60-80 Hz (toms), 200 Hz et plus (percs) | légère | queue courte | résonances métalliques |
| 5 | HH, OH | 300 Hz-1 kHz | HH mono, OH stéréo | OH assez long pour la variation d'AMP decay | sifflantes 6-10 kHz |
| 6 | CY | 500 Hz-1 kHz | stéréo | longueur réelle, coupée par le choke | même zone que les hats |
| 7-8 | BR, DL, PL | 100-150 Hz (le kick de la boucle ne doit pas doubler celui de la 1) | mono sous 150 Hz | compression douce si un pic dépasse | grave résiduel de la boucle |
| 9 | BS, BL | au-dessus du sub si le kick le porte ([[doctrine]] §9) | BS mono ; BL mono sous 150 Hz (2026-11-13) | contretemps, attaque franche, decay court | collision avec la queue du kick |
| 10 | ST | 150-300 Hz | légère | notes au même niveau | résonance du filtre acid |
| 11 | PD | 200 Hz | stéréo | faible niveau | bas-médium qui s'accumule |
| 12 | VX | 100-150 Hz | centre | compression douce admise | sifflantes |
| 13 | BL, ML graves | au-dessus du sub (vers 100 Hz) | mono sous 150 Hz | | grave de la 9 |
| 14 | ML aigus | 600-800 Hz | stéréo | | zone des hats |
| 15 | FX | 100-150 Hz, sauf impacts à sub voulu | stéréo | | queue de reverb |

### Outils : Live 12 Intro et Pro-Q 4

Live 12 Intro n'a ni EQ Eight ni Spectrum. Ses filtres (EQ Three, Auto
Filter) font des coupures, mais pas de creux étroit ni de traitement
mid / side. SPAN est le seul analyseur.

**FabFilter Pro-Q 4 couvre tout ce qui manque**, en un seul plug-in :
- coupures et creux à toute pente, en phase naturelle ;
- bandes dynamiques pour une résonance qui n'apparaît que sur certaines
  notes ;
- mid / side, donc mono sous 120 Hz par un passe-haut sur le side ;
- analyseur intégré ;
- vue des autres instances du projet, pour voir le kick, le rumble et la
  basse se chevaucher ;
- inclinaison de l'analyseur (4,5 dB/oct), qui sert à mettre chaque son
  sur la ligne (section « Niveaux »).

Recommandé dans cette stack. **Essai** d'abord avec la version d'essai de
FabFilter, et l'achat seulement si les creux dynamiques et le mid / side
servent vraiment. Sans Pro-Q 4 : EQ Three ou Auto Filter pour les coupures,
Utility (Bass Mono) pour le mono, SPAN pour voir (son analyseur a aussi
une inclinaison réglable, *à vérifier*).

## Import dans le pack perso : `premaster.py` (arbitré le 2026-11-13)

**Où** : le pack perso `/Users/tom/Documents/samples/solaris`, arbre
numéroté à plat (`01 KICK` … `20 SAMPLE`). **Quoi** : les sons qui
n'ont pas été préparés à la main dans Live (pack du commerce, enregistrements
de la DT2, boucles déjà rangées) passent sur la ligne automatiquement, par
`scripts/premaster.py` (mode d'emploi dans `scripts/README.md`). Ce que
l'oreille doit trancher (début, fin, creux, découpe des extraits de disques)
reste dans Live (section « Pré-mastering »).

### Le déroulé

1. **Zone de tri** : les sons arrivent dans `solaris/_import/<lot>/`
   (`serum`, `recorded`, `cuts`…), jamais directement dans les dossiers
   numérotés.
2. **Mesure, puis proposition de classement** : durée, part d'énergie sous
   120 Hz, entre 120 Hz et 2 kHz, au-dessus, largeur stéréo. La mesure
   propose un code ; **Tom valide** avant tout traitement, et tranche les cas
   douteux (boucle grave : BL ou DL ; son large : ST, FX ou ML). Repères :
   - plus de la moitié de l'énergie sous 120 Hz → tonal grave (BL, banque E) ;
   - le reste → tonal médium et aigu (ML, banque F) ;
   - un extrait de disque long ou sans début net → découpé dans Live
     d'abord (`_import/cuts`).
3. **Nom** : `<CODE> [BPM] <desc> <pack>`, 18 caractères au plus (section
   « Nommage ») ; `slr` pour le maison, `sr2` pour Serum 2. Le tempo n'est
   écrit que s'il est connu, pas deviné.
4. **Traitement** (`premaster.py import` pour un pack, `premaster.py apply`
   pour des sons déjà nommés) :
   - 48 kHz / 24 bits (le passage en 16 bits reste à l'export) ;
   - coupure sous 20 Hz, passe-haut de la famille en 24 dB/oct, phase
     minimale (valeur basse de la table « Par track ») ;
   - BD, RM, BS en mono intégral ; boucles BR, DL, PL, BL, ML mono sous
     150 Hz ; les autres mono sous 120 Hz ;
   - gain sur la ligne, décalage de la famille à 0 tant qu'il n'est pas
     fixé à l'oreille ;
   - **plafond de -6 dBFS pour tous les sons**, claps compris (gardé le
     2026-11-13 même si un clap posé à la main monte à -4,8) ;
   - ni normalisation ni rognage.
5. **Rangement** : le fichier va dans le dossier de son code. Un changement
   de code renomme le préfixe (`14 BASS LOOP/BL 145 Deep 1 slr` →
   `18 MELO LOOP/ML 145 Deep 1 slr`). L'original part dans
   `solaris/_backup/<date>/<chemin>` et sert de source aux passages suivants :
   relancer ne filtre pas deux fois.
6. **Doublons** : une ancienne copie au contenu identique (même mesure),
   rangée ailleurs, est supprimée une fois la nouvelle en place, après
   accord.
7. **Écoute** : un son qui sort bas (crête vers -11 dBFS pour une basse
   sans sub, ou pour un kick) n'est pas remonté d'office. Il s'écoute
   d'abord dans le pattern ; s'il manque, on règle le décalage de sa famille
   (`FAMILY` dans `scripts/analyzer/line.py`) et on relance.

### L'analyseur et son étalonnage

Spectre aux maxima maintenus (Freeze de Pro-Q), FFT de 8192 points, lissage
au 1/6 d'octave, inclinaison de +4,5 dB/oct autour de 1 kHz. La ligne est
le haut du spectre du kick de référence
(`01 KICK/BD 145 A# longtail 1 slr.wav`, crête
-6,3 dBFS) : -26,5 en interne, contre -26 lu dans Pro-Q. Le poids des bandes
(`BAND_WEIGHT` = 0,75) a été ajusté sur quatre sons posés à la main dans
Live + Pro-Q 4 (`CP 909 1`, `HH 909 2/3/4 slr PRE MASTER`) : écarts de -0,5
à +1,7 dB. À réajuster si un autre son préparé à la main s'en écarte de plus
de 2 dB.

## À l'export : coupure sous 20 Hz, sans EQ ni compression

La vidéo égalise, sature et compresse certains sons avant le transfert.
Chez nous, ce travail se fait **dans Live, son par son**, avant l'entrée
dans la lib (section « Pré-mastering »). L'export n'applique que ce qui ne
demande pas d'écoute :
- la coupure sous 20 Hz ;
- le niveau sur la ligne et le plafond de crête ;
- le format.

Une compression automatique aplatirait les attaques des kicks hard.

**Appliqué depuis le 2026-11-13 (7.J9b)**, pour la lib (`00 curated`) comme
pour les lives : l'export rend chaque son avec les réglages de la section
« Import dans le pack perso » (coupures, mono, ligne du kick de référence,
plafond de -6 dBFS) et l'écrit en 48 kHz / 16 bits avec dither. Les deux
sources, pack perso et lib, sortent ainsi sur la même ligne.

## Sauvegarde datée

- **+Drive** : avant un gros transfert, sauvegarder le +Drive avec Transfer
  dans un dossier daté (`DT2-backup-2026-11-10`), comme dans la vidéo.
- **Export** : l'export rejouable ne supprime plus rien. Un fichier
  remplacé ou retiré part dans `<MEDIA>/Live/_backup/<date>/`, au même
  chemin relatif.

## Pool du projet (arbitré 2026-11-12)

Le pool d'un projet compte 8 banques de 128 slots (8 × 128 = 1024). **La
lettre de la banque suit la position de la track** dans la grille
([[doctrine]] §1) : A à D pour la rangée du haut (tracks 1-8), E et F pour
la rangée du bas, G pour les FX, H pour le travail en cours. Le son d'une
track se cherche toujours dans la même banque.

| Banque | Tracks | Codes | Solaris (2026-11-12) |
|---|---|---|---|
| **A**, le corps | 1-3 | 0-KIT, BD, RM, CP, SD | 16 + 15 + 13 + 4 + 27 = 75 |
| **B**, percussions | 4 | PC, TM | 31 + 1 = 32 |
| **C**, aigus | 5-6 | HH, OH, CY | 18 + 4 + 14 = 36 |
| **D**, Id1 (boucles) | 7-8 | DL, BR, PL | 32 + 14 + 1 = 47 |
| **E**, tonal grave | 9, 13 | BS, BL | 20 + 16 = 36 |
| **F**, tonal médium et aigu | 10-12, 14 | SC (en tête), ST, ML, PD, VX | 0 + 2 + 0 + 1 + 21 = 24 |
| **G**, transitions | 15 | FX | 70 |
| **H**, espace de travail | 16 | resamples, sons enregistrés sur la machine, chargements en cours de session | vidée avant de sauver le projet |

Le 0-KIT reste en A01-A16 (7.L5).

**Dans une banque, des blocs de 16.** Chaque code occupe un bloc qui
commence à un multiple de 16, à la même place dans tous les projets.
Exemple pour A :

| Slots | Contenu |
|---|---|
| 01-16 | 0-KIT |
| 17-48 | BD (32 slots) |
| 49-64 | RM |
| 65-80 | CP |
| 81-112 | SD (32 slots) |
| 113-128 | libre |

Dans un bloc, l'ordre reprend l'arbre de l'export : la sous-catégorie
d'abord (CLEAN, HARD, SUB…), puis le nom. Les variantes voisines se
parcourent en balayant le slot, au p-lock ou au LFO
([[kb/tutos/elektronauts-ctrl-all]] §2).

**Règles** :

- **Une banque, une place.** Un son sans place dans la grille va en H,
  jamais dans le bloc libre d'une autre banque.
- **Des trous, pas de tassement.** Un bloc à moitié vide le reste : BD
  commence toujours en A17.
- **La même grille dans tous les projets**, comme celle des tracks.
- Les blocs des banques B à H se fixent quand on les remplit, sur le
  modèle de A.

**Single-cycles (SC)** : une seule période d'onde, jouée en boucle comme un
oscillateur. Bloc **F01-F16** (F01-F32 s'il en faut plus), avant ST, ML,
PD et VX. Tous au même endroit, quel que soit le registre : la même onde
fait une basse en track 9 ou un lead en track 10, c'est la note qui
décide, pas le fichier. Dans la lib, SC n'est pas un code : ces fichiers
restent en ST (`15 SYNTH`) et portent `SC` dans le nom (`ST SC Saw slr`).

## Sur la machine

- **Auto-preview** au navigateur de samples : on écoute avant de charger
  *(menu à vérifier sur la machine)*.
- Le +Drive est la bibliothèque, la RAM du projet ne contient que ce que le
  live joue (export des lives, jauge de RAM de 7.L). Vider de la RAM du
  projet les slots inutilisés avant de sauver le projet *(manip à vérifier,
  manuel)*.

## Liens

- [[doctrine]] — grille des 16 tracks (§1), qui fixe l'ordre des dossiers
- [[../SPEC]] — 7.J (bibliothèque de samples), 7.L (lives), Phase 8 (sound design)

#digitakt #doctrine #samples
