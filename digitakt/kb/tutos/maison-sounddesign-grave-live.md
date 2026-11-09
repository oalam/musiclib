---
tags: [digitakt, kb, tutos]
theme: Grave sur Mac, hub, arbitrages, stack, notions Reaper, pièges et exercices du tuto en six chapitres
lot: 4
ordre: 0
source: "échange de travail du 2026-10-29 (stack retenue) ; vérifications web Kick 3, Trash Lite, Drumsynth"
auteur: Tom (stack), rédaction à vérifier dans Reaper
modele: DT2
os: "1.17"
stack: [Reaper, Vital, Maschine Drumsynth Kick, Kick 3, iZotope Trash Lite, SPAN, ReaComp, Acid V]
statut: draft
updated: 2026-10-31
---

# Grave sur Mac — hub : arbitrages, stack, pièges, exercices

**En une phrase** : les quatre sons du grave se fabriquent dans un seul
projet Reaper au tempo du set, chacun sur sa piste avec sa chaîne, se
mesurent sur SPAN (note sur la queue, tenue du sub, mono), puis s'exportent
en WAV mono 48 kHz nommés avec leur note pour devenir, sur la DT2, le kick
de la track 1, le rumble de la 2 et la basse de la 9.

Cette fiche est la version « stack concrète » de deux fiches KB qui restent
la référence des gestes machine : [[../kick-mental-vst]] (kick
fabriqué en VST, joué sur la 1) et [[../rumble-grave]] (gestes
DT2 du §9, repères chiffrés des sources, dépannage). Les décisions sur le
grave sont prises dans la [[../../doctrine]] et dans les KT, elles ne
sont pas rediscutées ici. Format : lot 4 « Sound design préparatoire » de
[[_index]], un hub (cette fiche) et six chapitres détachés le 2026-10-31
de l'ex-recette maison 3, devenue trop longue.

## Les chapitres

| Ch. | Fiche | Contenu |
|---|---|---|
| 2 | [[maison-grave-projet-reaper]] | le projet Reaper modèle : construction clic par clic, pistes, durées au tempo, sidechain par canaux 3/4, saturation par bandes (splitter, Trash sur 3/4, joiner), mesure SPAN |
| 3 | [[maison-grave-kick]] | tuto kick : Drumsynth, Kick 3 par couches, Vital de A à Z, chaîne de sortie commune, validation |
| 4 | [[maison-grave-rumble]] | tuto rumble : chaîne plug-in par plug-in sur la piste RUMBLE, deux départs de passe-haut, variante sample, couche sinus, rendu boucle ou un coup |
| 5 | [[maison-grave-kickbass]] | tuto kickbass : Vital saturé ou sinus, Kick 3, limite de tempo vers le kick-sub, validation |
| 6 | [[maison-grave-basse]] | tuto basse : Vital en contretemps (one-shot par note), trois couches Attack Magazine, ligne Acid V, validation |
| 7 | [[maison-grave-rendu-dt2]] | rendu 48 kHz mono champ par champ, du rendu à la machine, chaîne de 16 kicks choisis à la vélocité (Grid 16) |

Les sections 0 et 1 ci-dessous, puis 8 et 9, restent dans le hub ; les
renvois « §n » des chapitres suivent cette numérotation.

## 0. Ce qui est arbitré avant d'ouvrir Reaper

| Décision | Où | Conséquence dans le projet |
|---|---|---|
| Une seule architecture du grave à la fois : kickbass, kick + rumble, ou kick + basse | KT23 [[../theorie/kt-kickbass-contre-kick-basse]] | choisir l'architecture **avant** de dessiner le kick : elle fixe sa longueur et ce qu'on exporte (rumble ou basse, jamais les deux sous un kickbass) |
| Une seule note sous 120 Hz, mesurée sur la queue du kick ; rumble et basse sur la tonique ou la quinte | KT5 [[../theorie/kt-tonalite-du-grave]], doctrine §11 | le projet Reaper a une tonique ; tout s'accorde dessus ; la note va dans le nom du fichier |
| Le kick possède le sub (20-60 Hz), le rumble vit en 60-150 Hz, la basse au-dessus ou duckée ; mono sous 120 Hz | doctrine §9, [[../rumble-grave]] | passe-haut sur le rumble et la basse, pas sur le kick ; master en mono pour juger |
| Le grave d'abord, fini et validé seul, une passe puis on fige | doctrine §7 | une séance = une tonique, une architecture, un tempo ; réécoute à froid le lendemain, une correction, export |
| Un kick par bank, invariant dans la bank | doctrine §3 | une famille de kicks par tonalité (F#, G, A) plutôt qu'un kick repitché |
| Kick de 150-300 ms pour un rumble, kickbass qui tient jusqu'au kick suivant | [[../rumble-grave]], KT23 | la longueur se règle en ms au tempo du set, pas à l'oreille sur le clavier |

Les trois couches du kick (sub 30-60 Hz, thump 100-200 Hz, click au-dessus
de 2 kHz) sont décrites dans [[../../../technique/anatomie-kick]] ; c'est le vocabulaire
utilisé ci-dessous.

## 1. La stack et le rôle de chacun

| Outil | Rôle ici | À savoir |
|---|---|---|
| **Reaper** | hôte, routing, sidechain, mesure, rendu | tout se fait dans un projet modèle ; les plug-ins Rea* et JS sont inclus |
| **Vital** | kickbass, basse sub et mid, kick synthétisé de A à Z, lignes | gratuit ; 3 oscillateurs, 2 filtres (dont ladder et diode), 6 enveloppes, distorsion intégrée ; monophonique à régler |
| **Maschine Drumsynth Kick** | kicks rapides, surtout tribe (moteurs Sub, Tronic, Dusty…) | pas un VST à part : se charge dans le plug-in **Maschine 2** inséré dans Reaper, sur un pad d'un groupe (voir [[../controleur-maschine]]) |
| **Kick 3** (Sonic Academy, démo puis achat) | le kick de référence par bank : enveloppes de pitch et de volume dessinées, click, note lue | cinq couches, chacune sub synthétisé ou sample, avec sa propre enveloppe de pitch et de volume ; 500 clicks ; EQ avec analyseur ; import d'un kick depuis un morceau entier (à vérifier sur la démo : limites d'export) |
| **Trash** (iZotope) | distorsion lourde : kick saturé, rumble, basse | la version gratuite est **Trash Lite** : module Trash (plus de 60 styles, pad XY entre quatre algorithmes), Randomize, Autogain / limiteur ; **sans Convolve ni multibande**. Le multibande se fait dans Reaper ([[maison-grave-projet-reaper]] §2.4) |
| **SPAN** (Voxengo) | analyseur : note de la queue, tenue du sub, bandes, corrélation | sur le master et sur chaque piste pendant la mesure |
| **ReaComp** | ducking du rumble et de la basse par le kick (sidechain) | « Detector input » sur l'entrée auxiliaire, **pre-comp à 0** (lookahead off, sinon le creux arrive avant l'attaque) |
| **ReaEQ, ReaVerbate, ReaTune, JS** | filtres passe-haut / passe-bas, reverb du rumble, accordeur, saturations d'appoint (JS Saturation, JS Soft Clipper) | tous inclus dans Reaper |
| **Acid V** (Arturia) | ligne acid (track 10 sur la DT2) et basse acid en contretemps | filtre diode, accent et slide ; passe-haut au-dessus du sub quand un kickbass tient le grave |

### 1.1 Reaper, les notions dont ce projet a besoin

Reaper ne fait rien d'exotique : il a juste des noms à lui. Les dix notions
ci-dessous couvrent tout ce que la fiche demande ; chacune est reprise au
moment où on s'en sert. Raccourcis macOS (Cmd remplace Ctrl, Opt remplace
Alt).

| Notion | Ce que c'est | Où / comment |
|---|---|---|
| **Track** (piste) | une tranche qui porte des items, une chaîne d'effets, un fader et un routing ; audio ou MIDI, Reaper ne fait pas la différence : une piste avec un synthé VST **est** une piste d'instrument | Cmd+T, ou double-clic dans la zone vide sous les pistes ; nom par double-clic sur le nom |
| **TCP et MCP** | les deux vues de la même piste : le *Track Control Panel* à gauche de l'arrangement (nom, M, S, FX, Route, fader) et le *Mixer* (Cmd+M) où les sends apparaissent en potards | tout ce qui se règle dans l'un se voit dans l'autre |
| **Item** | un bloc posé sur une piste : un fichier audio (WAV glissé depuis le Finder ou le Media Explorer) ou un **item MIDI** (des notes). C'est l'équivalent d'un pattern de la DT2 pour une seule track | item MIDI : faire une sélection temporelle, Insert > New MIDI item ; double-clic pour ouvrir l'éditeur MIDI |
| **Éditeur MIDI** | la grille où l'on dessine les notes ; grille à 1/16 = les 16 pas d'une mesure DT2 ; clic-glisser pose une note, la barre du bas règle la vélocité | la note jouée est celle de la ligne du piano à gauche ; F#1 est la note 30, A1 la note 33 |
| **FX chain** | la chaîne d'effets de la piste, dans l'ordre haut → bas = ordre du signal ; un VST d'instrument se met en premier, les filtres et compresseurs après. Même logique que les pages SRC → FLTR → AMP → FX de la DT2, mais l'ordre est libre | bouton **FX** du TCP ; « Add » ouvre le navigateur, taper le nom (ReaEQ, Vital…) ; glisser pour réordonner ; la case à cocher devant chaque effet le bypass |
| **Sélection temporelle** et **boucle** | la zone en surbrillance dans la règle : Reaper boucle dessus quand **R** (repeat) est actif, et le rendu peut s'y limiter. Cliquer-glisser dans la règle la crée ; **Esc** l'efface ; Opt+S active l'aimantation à la grille pour qu'elle tombe pile sur une mesure | Espace = lecture / stop ; Cmd+R = enregistrer (rien à enregistrer ici) |
| **Send** et **canaux** | un send copie le signal d'une piste vers une autre, avec son propre volume ; chaque piste a par défaut 2 canaux (gauche, droite) mais peut en avoir 4, 6… ; un send peut viser les canaux **3/4** d'une piste, qui n'arrivent pas dans ses haut-parleurs mais restent lisibles par un plug-in (c'est le principe du sidechain) | bouton **Route** du TCP (ou l'icône I/O) : « Track channels », « Add new send », et sur chaque send le mode pré / post-fader et les canaux source → destination |
| **Pin connector** | la matrice « 2 in 2 out » en haut de chaque effet : quels canaux de la piste entrent dans le plug-in et où ses sorties reviennent. Par défaut 1/2 → 1/2 ; brancher un effet sur 3/4 le fait travailler sur une autre « voie » de la même piste, c'est la base du multibande du [[maison-grave-projet-reaper]] §2.4 | bouton « 2 in 2 out » dans la fenêtre FX ; les JS 3-Band Splitter et Joiner créent et résorbent ces voies |
| **Dossier** (folder) | une piste parent dont les enfants sont sommés dedans ; les effets du parent s'appliquent au mélange, le fader du parent dose le tout ; les enfants gardent leur fader et leurs effets | icône de dossier en bas du TCP de la piste parent ; les pistes qui suivent deviennent enfants (indentées) jusqu'à la dernière, marquée par un clic sur la même icône |
| **Render** (rendu) | écrire un WAV sur disque : tout le master, ou une piste seule (« stem »), sur la sélection temporelle. C'est le resampling de la DT2, en mieux : on choisit la fréquence, le format, le nombre de canaux, et le projet garde tout | Cmd+Opt+R ; détail champ par champ au [[maison-grave-rendu-dt2]] §7 |
| **Modèles** | un *track template* sauvegarde une piste avec sa chaîne, son routing et son item ; un *project template* sauvegarde tout le projet comme point de départ. C'est le preset et le kit de la DT2 (doctrine §8) | clic droit sur une piste > « Save tracks as track template » ; File > Project templates > « Save project as template » |

Deux réflexes à prendre tout de suite : **Cmd+Z annule tout, y compris un
réglage de plug-in**, donc essayer sans peur ; et le bouton **Mono** du
master dans le mixer (en bas de la tranche master) est le juge de paix du
grave, à activer à chaque écoute.

### 1.2 Glossaire Reaper → Digitakt

| Reaper | Digitakt II | Différence utile |
|---|---|---|
| track | track | une piste Reaper est polyphonique et sans limite de nombre ; on en met une par **rôle** (KICK, RUMBLE, BASS), pas par son |
| item MIDI d'une mesure, grille 1/16 | pattern, 16 pas | pas de conditions ni de p-locks : les variations se font en dupliquant l'item |
| FX chain | pages FLTR, AMP, FX + machine SRC | l'ordre est libre et un effet peut apparaître deux fois (deux ReaEQ autour d'une distorsion) |
| send vers la piste RUMBLE | envoi reverb (FX send) | un send Reaper peut aller vers **n'importe quelle piste**, et la reverb n'est plus partagée : chaque piste peut avoir la sienne |
| send vers les canaux 3/4 + ReaComp | COMPRESSOR ROUTING + `SCS` = TRK1 | sur la DT2 un seul compresseur pour tout ; dans Reaper, un ReaComp par piste duckée, chacun avec ses réglages |
| splitter de bandes + pin connector (ou dossier SUB + BODY) | (aucun équivalent, une track = une voix, un overdrive large bande) | c'est précisément ce que la DT2 ne sait pas faire et qui justifie de fabriquer le kick sur le Mac |
| render de la sélection temporelle | `[SAMPLING]` `SRC` = MAIN, `R.LEN` = 16 | le rendu est reproductible ; on peut refaire le même sample après avoir changé un réglage |
| track template, project template | preset, kit, pattern modèle | mêmes rôles |
| bouton Mono du master | (écoute sur un sub mono) | la DT2 n'a pas de bouton mono : le contrôle se fait ici |

## 8. Pièges propres à la stack

- **Trash Lite est monobande** : saturer un kick entier mange le sub ;
  toujours derrière un JS 3-Band Splitter, branché sur 3/4 par le pin
  connector ([[maison-grave-projet-reaper]] §2.4). Convolve et le multibande sont dans la version
  payante, non nécessaire ici.
- **Send du kick déplacé de 1/2 vers 3/4** : le rumble se tait, parce que
  la reverb ne reçoit plus rien ; il faut les deux sends ([[maison-grave-projet-reaper]] §2.3), ou la
  variante à un send avec ReaVerbate repiqué sur 3/4.
- **Pin connector oublié ou à moitié fait** : Trash posé après le splitter
  sans toucher au « 2 in 2 out » ne traite que 1/2, donc le sub ; entrées
  sur 3/4 mais sorties laissées sur 1/2, le sub est écrasé par le corps
  saturé et le corps sec reste sur 3/4 (corps en double). Contrôle : au
  bypass du joiner, on ne doit entendre que le sub, propre. Un joiner
  oublié ne laisse entendre que les graves.
- **Vital** : randomisation de phase à 0 sur chaque oscillateur, voices 1,
  unisson 1 sur tout ce qui descend sous 120 Hz ; une basse en unisson
  stéréo disparaît en mono.
- **ReaComp** : « Pre-comp » est un lookahead ; à 0, sinon le creux arrive
  avant l'attaque du kick et le kick perd son punch. « Auto make-up »
  décoché, sinon le niveau du rumble change à chaque réglage du seuil.
- **Sends** : vers canaux 1/2 pour nourrir la reverb, vers 3/4 pour le
  détecteur ; les deux depuis KICK, pré-fader.
- **Drumsynth** : les paramètres changent de nom d'un moteur à l'autre ;
  rendre et mesurer plutôt que de se fier aux noms. Le plug-in Maschine 2
  demande le logiciel Maschine installé, pas seulement le contrôleur.
- **Kick 3 en démo** : vérifier ce que la démo autorise (export, sauvegarde
  de presets) avant de construire la famille de kicks ; sinon construire
  dans Vital ([[maison-grave-kick]] §3.3) et transposer plus tard.
- **Repitch** : plus de deux ou trois demi-tons dénature un kick ; une
  famille par tonalité, exportée depuis le projet.
- **Deux architectures à la fois** dans le projet : KICKBASS démuté avec
  BASS sur la même tonique bat et masque (KT23, exercice 3). Le projet
  modèle n'a jamais plus d'une des trois combinaisons audible.
- **44,1 kHz** : Transfer convertit, sans conséquence audible, mais le
  projet en 48 kHz évite une conversion et un doute.
- **Enceintes de bureau** : tout ce qui est écrit ici se juge au casque
  fermé, sur un sub, puis en mono et au téléphone.

## 9. Exercices

0. **Échauffement Reaper (15 min).** Construire le projet modèle du [[maison-grave-projet-reaper]] §2.0
   avec un seul kick (Vital, sinus, recette C) et une seule piste RUMBLE :
   send vers 1/2, send vers 3/4, ReaComp qui plonge à chaque kick ; puis
   sur KICK, splitter, Trash sur 3/4, joiner, et vérifier au bypass du
   joiner que 1/2 est un sinus propre. Puis
   rendre une mesure en mono 48 kHz et la rouvrir dans le Media Explorer.
   Tant que le vumètre de ReaComp ne bouge pas ou que le fichier n'a pas
   la bonne longueur, le reste de la fiche attendra.
1. **Trois longueurs, un kick (10 min).** Recette B ou C, tonique F#,
   165 BPM : queue 70, 180 et 300 ms. Avec la basse Vital en contretemps
   démutée : garder celle qui la laisse respirer ; noter la tenue du sub
   des trois sur SPAN.
2. **Deux départs de rumble (10 min).** Même kick, passe-haut avant reverb
   à 30 Hz puis à 120 Hz, tout le reste identique ; rendre les deux
   boucles, comparer au même niveau sous le kick, au casque puis en mono.
   Garder celle qui laisse le sub au kick.
3. **Kickbass saturé contre kick-sub (10 min).** Vital, F#, à 160 puis à
   170 BPM : à 160 le kickbass saturé tient ; à 170 raccourcir la note et
   le decay jusqu'à ce que le kick suivant sorte propre, puis essayer le
   kick-sub. Mesurer la
   tenue du sub des deux à chaque tempo.
4. **Tonique, quinte, tierce (5 min).** Basse Vital en contretemps sur F#,
   C# puis A sous le kick F# : entendre le battement sur la tierce, la
   remonter d'une octave, conclure (KT5).
5. **A/B avec la chaîne Python (5 min).** Même kick dans `sounddesign.py`
   preset `gritty` et dans Reaper avec les valeurs du [[maison-grave-rumble]] §4.1 ; au même niveau,
   écouter ce que Trash et ReaVerbate font de différent du tanh et de
   Freeverb, et noter dans [[../../../sounddesign/rumble]] ce qui vaut d'être
   porté dans un preset.

## Ressources

- Recettes et repères chiffrés des sources (Myloops, Futureproof, Attack
  Magazine, Gearnews, Bonedo, Elektronauts) : rassemblés dans
  [[../rumble-grave]] et [[../../veille-theorie]] §F ;
  valeurs données pour 125-140 BPM, recalées ici avec la table du [[maison-grave-projet-reaper]] §2.2.
- MusicTech, *Sonic Academy Kick 3 review* :
  <https://musictech.com/reviews/plug-ins/sonic-academy-kick-3-review/>
  (cinq couches sub ou sample, enveloppes par couche, pitch tracking des
  queues, EQ avec analyseur, import depuis un morceau).
- Sound On Sound, *iZotope Trash (2024)* :
  <https://www.soundonsound.com/reviews/izotope-trash-2024> (modules Trash
  et Convolve, bandes, et ce que **Trash Lite** gratuit contient : Trash,
  Randomize, Autogain / limiteur).
- Native Instruments, communiqué Trash :
  <https://www.native-instruments.com/en/press-area/music-production/trash/>
- Elephorm, *Guide complet sur le Drumsynth Kick* (FR, moteurs Sub, Tronic,
  Dusty, Rasper) :
  <https://www.elephorm.com/formation/apprendre-maschine-2x-tutoriel-video-en-ligne/guide-complet-sur-le-drumsynth-kick>
  ; manuel Maschine, section Drum Synths > Kick, pour les paramètres exacts.
- Reaper, multibande avec n'importe quel plug-in : Cockos, *How to set
  up multi-band effects* :
  <https://www.cockos.com/wiki/index.php/How_to_set_up_multi-band_effects>
  `[V]` ; Sound On Sound, *Reaper: creating multi-band processors* :
  <https://www.soundonsound.com/techniques/reaper-creating-multi-band-processors>
  `[V]` ; The REAPER Blog, splitter
  <https://reaper.blog/2016/04/js-band-splitter-fx/> et joiner
  <https://reaper.blog/2016/05/js-band-joiner-fx-multi-band-processing-with-any-plugin/>.
- Reaper, pour monter en compétence dans l'ordre de cette fiche : le
  *REAPER User Guide* de Geoffrey Francis (PDF gratuit sur reaper.fm,
  chapitres Routing et Sidechaining, Rendering, Track templates) ; les
  vidéos courtes de Kenny Gioia, *REAPER Mania* (YouTube, une notion par
  vidéo : sends, folders, sidechain avec ReaComp, render) ; The REAPER Blog
  (articles sur ReaComp, ReaEQ, le Media Explorer). Voxengo SPAN : manuel
  (block size, slope).
- Tutos vidéo DAW non visionnés (kick mental en Serum 2 / Ableton) listés
  dans [[../kick-mental-vst]].

## Liens

[[../../../technique/anatomie-kick]] · [[../../../technique/sound-system-free-party]] ·
[[../../../sounddesign/rumble]] · [[../kick-mental-vst]] ·
[[../rumble-grave]] · [[maison-rumble-dans-le-kick]]
· [[../midi-vst]] · [[../controleur-maschine]] ·
KT5 [[../theorie/kt-tonalite-du-grave]] · KT21
[[../theorie/kt-basses]] · KT23
[[../theorie/kt-kickbass-contre-kick-basse]] ·
[[../../doctrine]] §3, §7, §9, §10, §11

#digitakt #kb #tutos #sounddesign #kick #rumble #kickbass #basse
