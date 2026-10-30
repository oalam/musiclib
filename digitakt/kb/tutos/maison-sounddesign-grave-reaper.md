---
tags: [digitakt, kb, tutos]
theme: Sound design du grave sur Mac (kick, rumble, kickbass, basse) avec Reaper, Vital, Drumsynth, Kick 3, Trash Lite, SPAN, ReaComp, Acid V
lot: 3
ordre: 3
source: "échange de travail du 2026-10-29 (stack retenue) ; vérifications web Kick 3, Trash Lite, Drumsynth"
auteur: Tom (stack), rédaction à vérifier dans Reaper
modele: DT2
os: "1.17"
stack: [Reaper, Vital, Maschine Drumsynth Kick, Kick 3, iZotope Trash Lite, SPAN, ReaComp, Acid V]
statut: draft
updated: 2026-10-29
---

# Maison 3 — Sound design du grave sur Mac : kick, rumble, kickbass, basse

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
sont pas rediscutées ici. Format : recette maison du lot 3 ([[_index]]).

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
| **Trash** (iZotope) | distorsion lourde : kick saturé, rumble, basse | la version gratuite est **Trash Lite** : module Trash (plus de 60 styles, pad XY entre quatre algorithmes), Randomize, Autogain / limiteur ; **sans Convolve ni multibande**. Le multibande se fait dans Reaper (§2.4) |
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
| **Pin connector** | la matrice « 2 in 2 out » en haut de chaque effet : quels canaux de la piste entrent dans le plug-in et où ses sorties reviennent. Par défaut 1/2 → 1/2 ; brancher un effet sur 3/4 le fait travailler sur une autre « voie » de la même piste, c'est la base du multibande du §2.4 | bouton « 2 in 2 out » dans la fenêtre FX ; les JS 3-Band Splitter et Joiner créent et résorbent ces voies |
| **Dossier** (folder) | une piste parent dont les enfants sont sommés dedans ; les effets du parent s'appliquent au mélange, le fader du parent dose le tout ; les enfants gardent leur fader et leurs effets | icône de dossier en bas du TCP de la piste parent ; les pistes qui suivent deviennent enfants (indentées) jusqu'à la dernière, marquée par un clic sur la même icône |
| **Render** (rendu) | écrire un WAV sur disque : tout le master, ou une piste seule (« stem »), sur la sélection temporelle. C'est le resampling de la DT2, en mieux : on choisit la fréquence, le format, le nombre de canaux, et le projet garde tout | Cmd+Opt+R ; détail champ par champ au §7 |
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

## 2. Le projet Reaper modèle

Un projet `grave_<tonique>_<bpm>.rpp`, à copier pour chaque bank. Il est
au tempo du set, en 48 kHz (la fréquence native de la DT2), avec un item
MIDI d'une mesure et quatre kicks sur la piste KICK.

### 2.0 Construire le projet, clic par clic (20 min, une fois)

1. **Projet neuf et réglages.** Cmd+N. Opt+Enter ouvre Project Settings :
   onglet Project Settings, case « Project sample rate » cochée, 48000 ;
   le tempo se tape
   directement dans le champ BPM de la barre de transport (165,00). Cmd+S,
   nom `grave_F#_165.rpp`, dans un dossier à lui (Reaper y met les rendus
   et les enregistrements).
2. **Grille.** Opt+L ouvre les réglages de grille : 1/16 ; Opt+S active
   l'aimantation. Dans la règle, la mesure 1 est maintenant découpée en
   16 cases, comme la DT2.
3. **Pistes.** Cmd+T six fois, nommer KICK, RUMBLE, KICKBASS, BASS, ACID et
   laisser MASTER tel quel (il existe toujours). L'ordre compte peu, sauf
   pour la variante en dossier (§2.4).
4. **Instruments.** Sur KICK, bouton FX > Add > taper le nom (Kick 3, Vital,
   ou Maschine 2 pour le Drumsynth) ; Reaper demande si la piste doit
   recevoir le MIDI : oui. Même chose sur KICKBASS et BASS (Vital) et ACID
   (Acid V).
5. **Item MIDI du kick.** Cliquer-glisser dans la règle de la mesure 1 à la
   mesure 2 (la sélection s'aimante aux mesures), sélectionner la piste
   KICK, Insert > New MIDI item. Double-clic sur l'item : dans l'éditeur,
   grille 1/16 (menu Grid en bas), poser quatre notes sur la ligne F#1
   (note 30) aux pas 1, 5, 9, 13, longueur un pas. Fermer l'éditeur.
   Copier l'item sur KICKBASS (Cmd+C, sélectionner la piste, Cmd+V au même
   endroit) ; sur KICKBASS, rallonger chaque note dans l'éditeur jusqu'au
   pas suivant moins un rien (§5).
6. **Item de la basse.** Même geste sur BASS, notes aux pas 3, 7, 11, 15
   (le contretemps), longueur deux ou trois pas.
7. **Lire en boucle.** La sélection temporelle couvre la mesure 1 ; touche
   R pour activer la répétition ; Espace. Le projet tourne comme un pattern.
   Muter KICKBASS, BASS et ACID (bouton M) : on entend le kick seul.
8. **Effets de base.** Sur chaque piste, FX > Add : les chaînes du §2.1,
   dans l'ordre du tableau. Les réglages viennent aux §3 à §6.
9. **Sends et sidechain.** §2.3, pour RUMBLE et BASS.
10. **SPAN sur le master.** Cliquer sur le bouton FX du master, Add > SPAN,
    en dernière position.
11. **Sauver comme modèle.** File > Project templates > Save project as
    template, `grave_modele`. Chaque bank repart de là : File > New project
    from template.

### 2.1 Pistes

| Piste | Contenu | Chaîne de départ | Sortie |
|---|---|---|---|
| KICK | Drumsynth, Kick 3 ou Vital ; item MIDI `X...X...X...X...` ; 6 canaux | JS 3-Band Splitter → Trash sur 3/4 → JS 3-Band Joiner (§2.4) → ReaEQ (passe-haut 25-30 Hz) | master **et** send vers canaux 3-4 des pistes duckées |
| RUMBLE | reçoit KICK en send pré-fader | ReaEQ (passe-haut avant reverb) → ReaVerbate 100 % wet → ReaEQ (passe-bas 24 dB/oct) → Trash → ReaComp (sidechain) → largeur 0 | master |
| KICKBASS | Vital ou Kick 3, même item MIDI que KICK, piste **mutée** quand KICK joue | Vital (distorsion interne) → Trash → ReaEQ (passe-bas 300 Hz) | master |
| BASS | Vital, item MIDI en contretemps `..x...x...x...x.` | Vital → ReaEQ (passe-haut 60-80 Hz) → JS Saturation → ReaComp (sidechain) | master |
| ACID | Acid V, même item que BASS ou ligne de 16 pas | Acid V (drive interne) → ReaEQ (passe-haut 120-200 Hz) | master |
| MASTER | | SPAN en dernier ; bouton **Mono** du master pour juger le grave | |

Règle de muting : KICK + RUMBLE, ou KICK + BASS, ou KICKBASS seul (KT23).
Les trois combinaisons se comparent en solo-muting, jamais superposées.

### 2.2 Durées au tempo

Un temps vaut 60 / BPM, la croche la moitié, la double-croche le quart.

| BPM | temps | croche | double-croche | usage |
|---|---|---|---|---|
| 150 | 60 / 150 = 0,400 s | 200 ms | 100 ms | hard techno, preset `deep` |
| 160 | 60 / 160 = 0,375 s | 187 ms | 94 ms | bas du set ; kickbass saturé (Neurotribe 161,5) |
| 165 | 60 / 165 = 0,364 s | 182 ms | 91 ms | **tempo de travail de la fiche** |
| 170 | 60 / 170 = 0,353 s | 176 ms | 88 ms | haut du set |

Le set vit entre 160 et 170 BPM, jamais au-delà : les repères des sources
(donnés pour 125-140) se recalent ici sur 165, et la différence entre 160
et 170 (22 ms par temps) se règle à l'oreille, pas en refaisant le rendu.
Le preset `gritty` de la chaîne Python est écrit pour 185 : le relancer au
tempo de la bank (`sounddesign.py` prend le tempo de la banque).

Ces durées servent partout : longueur du kick (une fraction du temps),
decay de la reverb (1,5 à 2 s à 160-170 BPM), release du ducking (une
croche), longueur d'un rendu « un coup » (un temps).

### 2.3 Sidechain dans Reaper, pas à pas

**Le principe d'abord.** Un compresseur baisse le volume quand *ce qu'il
écoute* dépasse un seuil. Par défaut il écoute le signal qu'il traite. En
sidechain, on lui fait écouter **autre chose** : le kick. Reaper n'a pas de
bouton « sidechain » ; il a quelque chose de plus général, les canaux. Une
piste a deux canaux audibles (1 et 2, gauche et droite). On lui en donne
quatre : les canaux 3 et 4 ne sortent nulle part, mais un plug-in posé sur
la piste peut les lire. On envoie le kick dans ces canaux 3/4, et on dit à
ReaComp d'écouter son « entrée auxiliaire », c'est-à-dire 3/4. Le rumble
passe par 1/2, le kick par 3/4, ReaComp traite 1/2 en écoutant 3/4.

1. Sur la piste duckée (RUMBLE ou BASS) : bouton **Route** du TCP. En haut
   de la fenêtre, « Track channels » : passer de 2 à **4**. Rien ne change
   à l'écoute, la piste a juste deux canaux muets en plus.
2. Sur la piste KICK : bouton **Route**, section Sends, « Add new send »,
   choisir RUMBLE. Sur la ligne du send qui apparaît : le menu de mode sur
   **Pre-Fader (Post-FX)** (pour que le kick baissé ou muté au fader
   continue de déclencher, l'équivalent du kick fantôme de la doctrine
   §10) ; canaux laissés en **1/2 => 1/2** ; volume à 0 dB. Ce send-là
   **nourrit la reverb** : c'est lui qui fabrique le rumble. Pour la piste
   BASS, qui a son propre instrument, ce premier send n'existe pas.
3. Sur KICK encore, « Add new send » **une seconde fois** vers RUMBLE
   (Reaper accepte plusieurs sends vers la même piste). Même mode
   pré-fader, mais le petit menu des canaux passé à **1/2 => 3/4**. Ce
   send-là **pilote le ducking** et n'est jamais entendu : le send parent
   de RUMBLE n'envoie que 1/2 au master. Pour BASS, c'est le seul send.
   Dans le mixer, les deux sends apparaissent sous la piste KICK ; la
   fenêtre View > Routing Matrix (Opt+R) montre toute la toile d'un coup,
   utile pour vérifier qu'on n'a pas visé la mauvaise piste ou le mauvais
   couple de canaux.
4. ReaComp sur RUMBLE, en dernier dans la chaîne (après Trash) : le menu
   « Detector input » sur **Auxiliary input L+R** (c'est 3/4), « Pre-comp »
   à **0 ms**, « Auto make-up » **décoché**. Lecture : le vumètre vertical
   de ReaComp doit plonger à chaque kick ; s'il ne bouge pas, le second
   send vise 1/2 ou le détecteur écoute « Main input ».
5. Réglages de départ (repères de [[../rumble-grave]] recalés
   au tempo) : ratio 4:1 à 8:1, attaque 0,1 à 1 ms, release = une croche
   (180 ms à 165 BPM), seuil descendu jusqu'à 6-12 dB de réduction à chaque
   kick (lire le vumètre de ReaComp).
6. Mêmes réglages sur BASS : la basse est duckée **avec la même forme** que
   le rumble (Myloops, via rumble-grave).

**Pourquoi deux sends.** Le rumble n'est pas un son à lui : c'est le kick
qui traverse la reverb. ReaVerbate, comme tout effet, lit 1/2. Un seul send
vers 3/4 et la reverb ne reçoit plus rien : la piste se tait, alors que le
kick est bien là sur 3/4, écouté par le seul détecteur. Un seul send vers
1/2 et le rumble sonne, mais ReaComp n'entend rien sur son entrée
auxiliaire : plus de ducking.

**Variante à un seul send, par le pin connector.** Send unique 1/2 => 3/4.
Sur RUMBLE, le ReaEQ passe-haut et ReaVerbate sont rebranchés par leur
bouton « 2 in 2 out » : entrées sur 3/4 pour les deux, et pour ReaVerbate
sorties sur 1/2. La reverb lit le kick sec sur 3/4 et écrit la queue sur
1/2 ; 3/4 garde le kick sec pour ReaComp, puisqu'un plug-in ne vide pas les
canaux où il n'écrit pas. Le reste de la chaîne reste en 1/2. Même idée
qu'au §2.4 ; à adopter quand le pin connector est devenu un réflexe, les
deux sends restant plus lisibles dans la Routing Matrix.

### 2.4 Saturation lourde sans multibande : séparer les bandes dans Reaper

Trash Lite est monobande : saturé en une pièce, un kick perd son sub (les
harmoniques créées mangent la fondamentale et le passe-bas qui suit ne
rend rien). Le découpage se fait dans Reaper, avec deux effets JS livrés
avec lui et le **pin connector**, sur une seule piste.

**Le principe.** « JS: 3-Band Splitter » découpe le signal en trois
bandes et les pose sur trois paires de canaux de la piste : graves sur
1/2, médiums sur 3/4, aigus sur 5/6. Chaque effet de la chaîne a, en haut
de sa fenêtre, un bouton « 2 in 2 out » : c'est le pin connector, une
matrice qui dit quels canaux de la piste entrent dans le plug-in et où
ressortent ses sorties. Brancher Trash sur 3/4 seulement, c'est le faire
travailler sur le corps du kick sans qu'il voie le sub ni le click.
« JS: 3-Band Joiner » resomme ensuite les six canaux en stéréo. Les
filtres de croisement du splitter sont faits pour se resommer à plat, ce
que deux ReaEQ indépendants ne garantissent pas à la fréquence de coupure.

1. Piste KICK, bouton **Route**, « Track channels » = **6**. Rien ne change
   à l'écoute : quatre canaux muets de plus.
2. FX > Add > **JS: 3-Band Splitter**, placé juste après l'instrument.
   Coupures : basse à **90-100 Hz** (sub / corps), haute à **2-3 kHz**
   (corps / click). Son entrée est mono (« left input », canal 1) : sans
   conséquence sur un kick, qui est mono. Ouvrir son pin connector et
   cliquer **Reset** une fois la piste à 6 canaux : la matrice doit
   montrer six lignes et une diagonale low → 1/2, mid → 3/4, high → 5/6 ;
   si les lignes 5 et 6 manquent, le click part dans le vide. Pour
   l'instant tout ressort tel quel : le joiner n'est pas encore là et
   seuls 1/2 sont audibles, donc on n'entend que le sub ; c'est normal.
3. FX > Add > **Trash** après le splitter. Cliquer son bouton « 2 in 2 out » :
   dans la matrice, **décocher** les entrées 1 et 2 et cocher les canaux
   **3 et 4** sur les entrées 1 et 2 du plug-in ; même chose côté sorties
   (sorties 1 et 2 du plug-in vers les canaux 3 et 4). La matrice doit
   montrer deux diagonales sur les lignes 3 et 4, côté entrées **et** côté
   sorties, rien d'autre. Des sorties laissées sur 1/2 écrasent le sub
   avec le corps saturé pendant que 3/4 garde le corps sec : plus de sub,
   corps en double, l'inverse du but (erreur faite et corrigée le
   2026-10-30).
4. FX > Add > **JS: 3-Band Joiner** en dernier (avant le passe-haut 25-30 Hz
   et le soft clipper de la chaîne de sortie, §3.4). Le son revient entier.
5. Régler Trash : bypasser le joiner un instant pour écouter 1/2 seuls (le
   sub, qui doit rester un sinus propre), puis remettre le joiner et doser
   style, drive et mix sur le corps. Les potards du joiner servent de
   faders de bandes : baisser 5/6 si le click ressort trop après la
   saturation.
6. Un second Trash, ou JS Saturation, branché sur **5/6** traite le click à
   part (léger) ; un troisième étage sur 1/2 reste interdit : le sub ne se
   sature pas, il se garde.
7. Sauvegarder la chaîne en **preset de chaîne** (menu FX > Save chain) ou,
   depuis Reaper 7, mettre splitter, Trash et joiner dans un **conteneur
   FX** (FX > Add > Container, puis glisser les trois dedans) : un seul
   bloc « Trash 3 bandes » réutilisable sur BASS et RUMBLE.

Même découpage pour la basse mid, et pour le rumble si le drive de Trash
dépasse 20 dB. C'est le « multi-étages » de Sara Landry (doctrine §3) avec
des outils gratuits.

**Variante en dossier, SUB / BODY.** Avant de connaître le splitter, ou
quand on veut deux chaînes vraiment différentes sur le sub et le corps :
rendre le kick sec (§7), créer deux pistes enfants d'un dossier KICK (icône
de dossier en bas du TCP du parent, puis sur le dernier enfant pour fermer
le dossier ; le parent somme ses enfants et son fader dose le tout), poser
le WAV sur les deux, ReaEQ **Low Pass** 90-100 Hz sur SUB (une bande fait
12 dB/oct, deux bandes identiques pour 24), ReaEQ **High Pass** 90-100 Hz
puis Trash sur BODY, solo de BODY pour régler Trash, puis doser aux faders
en mono. Plus lourd (trois pistes, un WAV à rendre d'abord) et pas de
garantie de resommation plate au croisement : le splitter est le défaut.

**Hors Reaper.** Des hôtes multibandes qui chargent un VST tiers par bande
existent (Blue Cat's MB-7 Mixer, DDMF Metaplugin), tous payants et
inutiles ici ; Kilohearts Multipass n'accepte que ses propres snapins. La
version payante de Trash est elle-même multibande (trois bandes, un
réglage par bande) : c'est l'argument d'achat si Trash Lite ne suffit
plus un jour.

### 2.5 Mesurer

- **SPAN** : taille de bloc 8192 (résolution dans le grave), pente 4,5
  dB/oct, moyenne 1 à 2 s, maintien de crête activé. Le pic lu dans la
  queue du kick donne la **note** ; la lecture entre deux kicks, le niveau
  du 30-100 Hz par rapport à l'attaque, donne la **tenue du sub** (KT23 :
  au-dessus de -10 dB le kick tient le sub, en dessous de -20 dB il le
  laisse).
- **SPAN, trois lectures qui servent à chaque séance.** La note : curseur
  sur le sommet de la bosse grave, SPAN affiche fréquence et note. Un
  creux dans le spectre à la fréquence du crossover (100 Hz) peut être le
  kick lui-même ou une annulation de phase entre le sub sur 1/2 et le
  corps saturé sur 3/4 : bouton **Underlay** pour garder le spectre
  courant en fond, bypasser Trash, rejouer ; si le creux disparaît, c'est
  Trash qui creuse le corps (style « scoopé », filtres du module, ou
  mélange dry / wet déphasé ; constaté le 2026-10-30 sur un kick Kick 3).
  Deux leviers : changer de style ou baisser le mix vers 30-40 % ; ou
  monter le crossover 1 du splitter de 100 à 140-150 Hz, pour que le thump
  (100-150 Hz) reste dans la bande propre avec le sub, Trash ne travaillant
  que le haut du corps. Le second est le plus simple quand le thump compte,
  ce qui est le cas d'un kick tribe. Les statistiques (Peak, Clippings) s'accumulent depuis
  l'ouverture : bouton **Reset** avant chaque lecture, puis Peak entre -6
  et -3 dBFS et Clippings à 0 sur un kick à exporter. Le **Correlation
  Meter** doit se tenir à +1,0 sur un kick en lecture (il affiche 0,0 à
  l'arrêt) ; en dessous de 0,9, quelque chose est stéréo dans la chaîne.
- **ReaTune** sur la piste KICK, boucle réduite à la queue (20-90 ms après
  l'attaque, pas l'attaque elle-même) : la note s'affiche. Sur un sinus
  presque pur la détection peut sauter à l'octave ou à 200 Hz, croiser avec
  SPAN.
- **Mono** : bouton Mono du master. Si le rumble disparaît, le grave est
  stéréo quelque part (reverb, unisson de Vital).
- **Où écouter** : casque fermé ou sub ; sur des enceintes de bureau le
  rumble est toujours poussé trop fort et la tenue du sub ne s'entend pas.
  Vérifier aussi sur le téléphone : ce qui y reste du kick est l'effet de la
  saturation, pas du sub.

## 3. Tuto kick : trois recettes, une chaîne

Objectif commun : un kick **accordé** (note lue sur la queue), de
**longueur choisie au tempo**, exporté sec avec de la marge (crête -3 à
-6 dBFS, la DT2 a son propre overdrive). Trois longueurs selon
l'architecture :

| Architecture | Longueur de la queue (à -24 dB) | Exemple à 165 BPM (temps = 364 ms) |
|---|---|---|
| kick + basse (tribe, le « tok ») | moins d'un quart du temps | 60-80 ms, sub à -13 dB, médiums 300 Hz-3 kHz (Tekotak, KT23) |
| kick + rumble | 150-300 ms, sub de la queue coupé avant la reverb | 130-200 ms (40-60 % du temps) |
| kickbass | plus de la moitié du temps, jusqu'au kick suivant | §4 |

### 3.1 Recette A, Drumsynth Kick (le kick tribe en cinq minutes)

1. Reaper : piste KICK, insérer le plug-in Maschine 2, groupe A, pad 1 en
   **Drumsynth > Kick**, moteur **Sub** (sinus, les paramètres de base sont
   Tune, Decay et Bend) ; item MIDI quatre noires sur la note du pad.
2. **Tune** jusqu'à lire la tonique sur SPAN dans la queue (F#1 = 46,2 Hz,
   G1 = 49 Hz, A1 = 55 Hz, table complète dans KT5).
3. **Decay** à la longueur visée (lire la forme d'onde dans Reaper après un
   rendu, ou SPAN en maintien de crête).
4. **Bend** (l'enveloppe de pitch) : faible pour un kick-sub, fort pour un
   thump ; c'est le réglage qui décide si on entend une note ou un coup.
5. Moteur **Tronic** pour une version avec gain et tone intégrés (kick déjà
   sale, bon départ pour la hard techno), **Dusty** pour un kick rauque avec
   bruit et filtre haut (le « tok » tribe) ; les autres moteurs à écouter
   (noms et pages de paramètres à vérifier dans le manuel Maschine, section
   Drum Synths > Kick).
6. Rendu (§6). Un Drumsynth sonne rapidement mais ne dessine pas la courbe
   de pitch : quand le kick doit tenir une note (kickbass), passer à B ou C.

### 3.2 Recette B, Kick 3 (le kick de référence de la bank)

0. **Savoir ce qu'un preset d'usine apporte.** Les presets livrés
   arrivent avec leur EQ (entailles étroites dans le corps, par exemple
   179 Hz à -6 dB avec Q 4 sur `tom1`), leur section Effects (trois drives
   empilés) et leur **limiteur actif**, qui plafonne à 0 dBFS en interne.
   Le limiteur est une couleur comme une autre, à garder si elle plaît
   (c'est le cas sur `tom1`, 2026-10-30) ; la seule règle est la marge :
   le fader OUT de Kick 3 est **après** le limiteur, le baisser jusqu'à une
   crête de -6 dBFS dans SPAN garde la couleur et laisse la place à
   l'overdrive de la DT2. Pour régler l'étage Trash du §2.4, couper Effects
   le temps du réglage, afin de juger une saturation à la fois, puis les
   réintroduire. Le champ KEY du panneau Export est une transposition, pas
   la note de la queue : la note juste reste celle lue dans SPAN.
1. Piste KICK, Kick 3, preset init. Première couche en **sub synthétisé** :
   dessiner l'enveloppe de pitch avec deux ou trois points : départ une à
   deux octaves au-dessus (+24 à +36 demi-tons, la recette Koçer dans
   [[../../../technique/anatomie-kick]]), chute en 10-20 ms pour un click intégré, 40-60 ms
   pour un thump, point d'arrivée **sur la tonique**, affichée par le
   plug-in sur le dernier point.
2. Enveloppe de volume de la même couche : plateau court puis descente ;
   lire la longueur en ms et la caler sur la table du §3 (à 165 BPM,
   150-250 ms pour un kick à rumble).
3. Deuxième couche, un **click** parmi les 500 (ou un sample de la banque
   `/Volumes/xtreme/Samples`, branche DRUMS, [[../../kt-banque-samples]]) :
   enveloppe raccourcie « assez » pour qu'il se fonde au sub, pas de queue.
   Une troisième couche optionnelle en bruit filtré pour l'air (tribe).
4. Harmoniques du sub (le sub « étendu ») : un peu, pour que le kick passe
   sur le téléphone ; le reste de la saturation se fait dans Reaper (§2.4)
   pour rester comparable entre kicks.
5. EQ intégré avec analyseur : couper au-dessous de 25-30 Hz ; en
   architecture kick + basse, cloche de **-4,5 dB** à la fondamentale de la
   basse (Attack Magazine, via KT5) pour que les deux coexistent.
6. Famille : enregistrer trois presets du même kick qui ne diffèrent que
   par la note d'arrivée (F#, G, A) et trois par la longueur (court, à
   rumble, kickbass). Un kick par bank, choisi dans la famille, jamais
   repitché de plus de deux ou trois demi-tons sur la DT2 (doctrine §11).
7. Phase : vérifier que le kick part toujours au même point de phase (pas
   de randomisation) ; deux kicks exportés d'un même preset doivent se
   superposer sans annulation.

### 3.3 Recette C, Vital (le kick dessiné de A à Z)

1. Piste KICK, Vital, preset init. **Voices** = 1, **OSC 1** en sinus,
   unisson 1 voix, **randomisation de phase à 0** (petit potard à côté de
   Phase), sinon chaque kick part d'une phase différente et le sub change
   de poids d'un coup à l'autre.
2. **ENV 1** (ampli) : attaque 0, hold 0, decay à la longueur visée,
   sustain 0, release 10 ms.
3. **ENV 2** glissée sur le **Transpose** de l'OSC 1, profondeur +24 à +36
   demi-tons ; ENV 2 : attaque 0, decay 10-60 ms (click intégré à thump),
   sustain 0. La note MIDI jouée est la tonique (F#1 = note MIDI 30, G1 =
   31, A1 = 33) ; vérifier sur SPAN que la queue retombe bien dessus.
4. Click séparé : **OSC 2** en carré ou en bruit (section Sampler avec un
   bruit blanc), ENV 3 sur son niveau, decay 5-15 ms, niveau bas. C'est la
   couche « click » de Koçer, à chercher entre sinus et carré.
5. **Filtre 1** sur OSC 1 seulement, modèle Analog ladder 24 dB, cutoff
   250-400 Hz, **Drive** du filtre modéré : premier étage de saturation,
   qui reste sous le passe-bas.
6. Effet **Distortion** de Vital (Soft Clip, puis Hard Clip pour le mental)
   en second étage, mix 30-50 % ; refermer avec l'EQ de Vital si le haut
   devient criard. Le troisième étage, Trash, se fait dans Reaper sur la
   bande 3/4 du splitter (§2.4).
7. Enregistrer le preset Vital avec la note dans le nom, puis rendu (§6).

### 3.4 Chaîne de sortie commune

Après le joiner (ou le dossier SUB + BODY) : ReaEQ passe-haut, puis JS
Soft Clipper à -1 dB pour rattraper une crête, jamais pour « grossir »,
puis rendu. Pas de compresseur sur le kick seul ; la colle se fait sur la
DT2 (doctrine §10).

**La ReaEQ de sortie, réglage.** Une seule bande : Type High Pass,
Frequency 28 Hz, Bandwidth 1,7 (courbe sans bosse) ; les autres bandes
retirées ; preset `kick HPF 28`, le même pour toutes les banks. Elle reste
branchée en 1/2, ce qui est juste : après le joiner seuls 1/2 vont au
master. Rien d'autre : l'équilibre sub / corps se règle sur le mix de
Trash et les potards de bande du joiner, et un creux du spectre (souvent
vers 100 Hz sur un kick à sub sinus, entre la fondamentale et le départ de
l'enveloppe de pitch) ne se rebouche pas à l'EQ, on remonterait du bruit.
Seule exception, en architecture kick + basse : une cloche de -4,5 dB à
la fondamentale de la basse (92 Hz pour une basse en F#2), bandwidth 1 oct
(Attack Magazine, via KT5). Pas de cloche en kick + rumble ni en kickbass.
Ensuite, Reset des statistiques de SPAN et lecture du Peak : entre -6 et
-3 dBFS, prêt à rendre ; au-dessus, baisser le fader de KICK plutôt que
d'ajouter un limiteur.

### 3.5 Valider un kick

- Note sur la queue = tonique du projet (SPAN + ReaTune).
- Longueur lue en ms, conforme à l'architecture (table §3).
- Tenue du sub entre deux kicks (SPAN, 30-100 Hz) : sous -20 dB pour un
  kick court, au-dessus de -10 dB pour un kickbass.
- En mono, puis au téléphone : le kick doit rester reconnaissable au
  téléphone par ses harmoniques, et ne pas gagner ni perdre en mono.
- Export avec de la marge, nom `kick_<style>_<note>_<bpm>.wav` (ex.
  `kick_tribe_F#_165.wav`).

## 4. Tuto rumble : la reverb saturée, duckée par le kick

Même recette que la chaîne `Rumble` de [[../../../sounddesign/rumble]] (Freeverb,
passe-bas, tanh, passe-bas, passe-haut, duck) et que la doctrine §9, avec
les plug-ins de Reaper. Deux départs possibles pour le passe-haut avant la
reverb (désaccord des sources, [[../rumble-grave]]) : les deux
se rendent et se comparent.

### 4.1 Chaîne sur la piste RUMBLE

| Étape | Plug-in | Réglage de départ | Pourquoi |
|---|---|---|---|
| 1. Entrée | send KICK → RUMBLE, pré-fader, canaux 1/2 | 0 dB | le kick sec reste sur KICK, la reverb n'entend que lui |
| 2. Passe-haut avant reverb | ReaEQ, **une seule bande** de type High Pass, posée sur le kick qui arrive par le send, **avant** qu'il n'entre dans la reverb ; la piste KICK n'est pas touchée | **départ A** : fréquence 30 Hz ; **départ B** : fréquence 120 Hz. Même bande, deux valeurs, jamais les deux à la fois ; détail sous le tableau | ce filtre décide de ce que la reverb étale. A ne retire que l'infra : le sub du kick entre dans la queue, le rumble tient lui-même le 40-60 Hz entre les coups (Futureproof, hard techno 140-150). B retient le sub : la queue ne contient que le corps, le rumble vit en 100-250 Hz avec le passe-bas de l'étape 4, le 20-60 Hz reste au kick seul (Myloops, doctrine §9, KT5). Les sources se contredisent et aucune n'est écrite pour 160-170 BPM : rendre les deux (exercice 2) ; à nos tempos B est le défaut, A demande plus de ducking et accumule du sub entre les coups sur un gros système |
| 3. Reverb | ReaVerbate | wet 100 %, dry 0, room size grand, **dampening** 0,5-0,6 (sombre), pre-delay 0, **width 0** | queue de 1,5 à 2 s à 160-170 BPM (la croche vaut 176-187 ms, le temps 353-375 ms : les queues doivent se chevaucher d'un temps à l'autre sans s'accumuler sur la mesure) ; jamais au-delà de 3-4 s ; aucune modulation dans la queue (ReaVerbate n'en a pas) |
| 4. Passe-bas après reverb | ReaEQ, low-pass 24 dB/oct | 200-250 Hz (rumble qui pousse, `gritty`) ou 130-170 Hz (rond, `deep`) | ce qui distingue un rumble d'une reverb de kick |
| 5. Saturation | Trash Lite | style doux (tube, tape), drive 10-16 dB (`deep`) à 20-26 dB (`gritty`), **mix 30-50 %** | harmoniques 80-160 Hz audibles sur petit système ; après la reverb (Futureproof), le fizz se juge au téléphone |
| 6. Second passe-bas | ReaEQ, low-pass 24 dB/oct, résonance légère | 150-200 Hz | retire les harmoniques aiguës créées en 5 ; avec de la résonance, le rumble « parle » |
| 7. Passe-haut | ReaEQ, high-pass | 30-40 Hz (50-60 si le kick a déjà beaucoup de sub) | l'infra-grave consomme de la puissance sans être entendu |
| 8. Ducking | ReaComp, sidechain (§2.3) | 24-30 dB de creux pour que le kick sorte seul (10-12 dB si le rumble reste présent sous le kick), attaque 1-2 ms, release une croche | la pompe qui fait « rouler » |
| 9. Mono | ReaVerbate « Stereo width » à 0 ; pour un item audio, clic droit > Item properties > Channel mode = Mono (downmix) ; pour un instrument, unisson 1 à la source | | mono sous 120 Hz |
| 10. Niveau | fader | le rumble **sous** le kick ; sur la DT2 la 2 se règle sous la 1 après coup | une prise normalisée ment sur le niveau |

**Régler le passe-haut dans ReaEQ (étape 2), à l'écran.** ReaEQ s'ouvre
avec plusieurs bandes par défaut ; il n'en faut qu'une.

1. Onglet **1** : Type = **High Pass** ; Frequency = **30** (départ A) ou
   **120** (départ B). Le champ Gain ne compte pas pour un passe-haut.
2. Toujours sur la bande 1, régler **Bandwidth** pour que la courbe
   descende sans remonter au-dessus de 0 dB (1,7 oct convient, vérifié à
   l'écran le 2026-10-30) : une valeur plus grande fait résonner le
   filtre, avec une bosse de plusieurs dB juste au-dessus de la coupure,
   qui gonfle le sub du kick avant la reverb, l'inverse du but.
3. Onglets **2**, 3, 4 s'il y en a : **Remove band**. Une cloche à 0 dB ne
   fait rien, et un shelf par défaut fausse la comparaison.
4. Bouton **+** à côté de « No preset » : enregistrer `rumble HPF A 30`,
   passer la fréquence à 120, enregistrer `rumble HPF B 120`. Les deux se
   rappellent dans le menu déroulant ; rendre la boucle avec chacun
   (exercice 2) et écouter au même niveau sous le kick.
5. Le passe-bas de l'étape 4 va dans la **seconde** ReaEQ, après
   ReaVerbate, pas dans celle-ci.

Le preset `deep` de la chaîne Python (dampening 0,6, drive 14 dB, retour
220 ms, 150 BPM) et `gritty` (dampening 0,3, drive 26 dB, bande +4 dB à
120 Hz, retour 140 ms, écrit pour 185 BPM) donnent deux cibles A/B, à
relancer au tempo de la bank : rendre le même
kick avec les deux (`sounddesign.py`) et avec Reaper, comparer au même
niveau.

### 4.2 Variante par sample (poids constant)

Un drone, un bruit filtré ou un field recording de la branche TONAL de la
banque, sur une piste RUMBLE-S : passe-haut 30 Hz, passe-bas 200-250 Hz,
Trash doux, même ReaComp que le rumble, mixé 3 à 6 dB sous le niveau où on
l'entend seul. Combinaison cible (Myloops, via rumble-grave) : le rumble par
reverb pour le mouvement, la couche sample pour le poids.

### 4.3 Couche sinus

Vital sur une piste SUB-R : sinus **une octave sous** la fondamentale du
kick (F#0 = 23,1 Hz pour un kick en F#1 ; à 46,2 / 2), attaque 200 ms,
mixé 10-12 dB sous le rumble, ducké pareil. Uniquement sur un vrai sub ;
à retirer si le système ne descend pas (passe-haut du rig à 35-40 Hz,
[[../../../technique/sound-system-free-party]]).

### 4.4 Rendu du rumble pour la DT2

Deux formats, comme dans [[../../../sounddesign/rumble]] :

- **Boucle** : sélection temporelle d'exactement 1 ou 2 mesures (à 165 BPM,
  2 mesures = 2 × 4 × 60 / 165 = 2,909 s), kick muté dans le master,
  rendu de la piste RUMBLE ; la boucle part et finit dans le creux du
  ducking. Sur la DT2 : track 2 en lecture loop, un trig par mesure.
- **Un coup** : un seul kick, rendu d'un temps (0,364 s à 165) plus un
  fondu de 20 ms. Sur la DT2 : un trig sur chaque pas du kick, fills
  compris (doctrine §9).

Nom `rumble_<preset>_<note>_<bpm>.wav` ; rendre une version par tempo,
jamais de time-stretch sur la machine. Après versement dans la library, le
rendu prend un nom DT2 en miroir du kick (`RM 165 ... `, circuit 8.L2 dans
[[../../../sounddesign/rumble]]).

### 4.5 Valider un rumble

Sous le kick, au casque : le kick garde son attaque (sinon ducking plus
profond ou plus rapide, rumble baissé de 2-3 dB) ; entre deux kicks, le
30-100 Hz remonte sans dépasser l'attaque ; en mono, rien ne disparaît ;
au téléphone, le grondement s'entend encore par ses harmoniques. La table
de dépannage est dans [[../rumble-grave]].

## 5. Tuto kickbass : le kick qui est la basse

Référence mesurée (KT23) : Neurotribe à 161,5 BPM, pitch envelope 84 →
57 Hz en 130 ms, harmoniques 120-300 Hz à -5,5 dB (saturé), sub tenu à -8
dB sur toute la seconde moitié du temps ; Six ou Sept à 143,6, click puis
sinus pur 57 → 50 Hz, harmoniques à -17 dB. Deux kickbass, deux chaînes.

### 5.1 Vital

1. Piste KICKBASS, Vital : OSC 1 sinus, voices 1, phase fixe (§3.3).
2. ENV 1 (ampli) : decay long, **release 5-10 ms**, et la **longueur de la
   note MIDI** égale au temps moins 10-20 ms (à 165 BPM, 364 - 15 = 349 ms) :
   la note s'arrête juste avant le kick suivant, la queue ne mange pas
   l'attaque suivante. Sur la DT2 ce sera l'AMP de la track 1 qui coupe.
3. ENV 2 sur Transpose, +24 à +30 demi-tons, decay 100-130 ms (Neurotribe)
   ou 20-40 ms puis sinus pur (Six ou Sept).
4. **Version saturée** (free party) : filtre ladder, drive haut, puis
   distorsion Vital Soft Clip, puis Trash sur la bande 3/4 (§2.4, coupure
   basse du splitter à 90 Hz pour que le sinus reste intact), passe-bas final 300 Hz
   (LOWPASS 4 sur la DT2). Cible : harmoniques 120-300 Hz à -5 ou -6 dB du
   fondamental sur SPAN.
5. **Version sinus** (club) : pas de Trash, un seul étage de Soft Clip très
   léger pour les harmoniques à -15 dB ; le click vient d'OSC 2 (§3.3).
6. Hauteur : la note MIDI jouée est la tonique ; les progressions se feront
   par p-lock de `TUNE` sur la DT2 (tonique 4 mesures, quinte 4 mesures,
   KT5), donc **un seul export par note**, pas de glissando.

### 5.2 Kick 3

Même chose en dessinant : enveloppe de volume de la couche sub avec un
plateau qui dure jusqu'au temps suivant (lire les ms), enveloppe de pitch
courte, note d'arrivée = tonique, harmoniques du sub poussées pour la
version saturée ; Trash en aval sur la bande 3/4 (§2.4). L'option de suivre la hauteur de
la seule queue (pitch tracking des sub tails) sert ici : la queue suit la
note MIDI, le click reste fixe.

### 5.3 Tempo et limite

Entre 160 et 170 BPM le temps fait 353 à 375 ms : c'est exactement la
zone du kickbass saturé de référence (Neurotribe, 161,5), et c'est aussi
sa limite haute. À 170, une queue qui tient encore -8 dB à 300 ms laisse
53 ms avant le kick suivant : assez si la note MIDI s'arrête à 340 ms,
trop peu si la saturation allonge la queue. L'autre option à ce tempo est
le **kick-sub** (sinus écrêté court, sans note tenue, Floxytek, KT23) :
Vital, sinus, decay 150-200 ms, Hard Clip fort, pas de Trash. Rendre les
deux à 170 et comparer ; en dessous de 165 le kickbass saturé gagne
presque toujours.

### 5.4 Valider un kickbass

Tenue du sub entre deux kicks (SPAN, 30-100 Hz) **au-dessus de -10 dB** de
l'attaque, sans trou ni battement ; rien sur la piste BASS ni RUMBLE (une
seule architecture) ; sur la DT2, la 9 et la 2 restent vides. Export
`kickbass_<sat|sin>_<note>_<bpm>.wav`.

## 6. Tuto basse : la 9 en contretemps, et la ligne acid

En architecture kick + basse, la basse porte le sub entre les kicks (le
stem bass de Tekotak est à +17,5 dB du sub du kick, KT23) ; en kick +
rumble, elle vit au-dessus (80-250 Hz, KT5), passe-haut monté. Dans les
deux cas : attaque franche, decay court, retombée avant le kick suivant,
**la double-croche du kick vide** (Attack Magazine : c'est un placement de
trigs, pas un compresseur).

### 6.1 Basse Vital en contretemps (track 9, one-shot BS)

1. Piste BASS, Vital, **voices 1**, legato, portamento 0 (ou court pour un
   slide ponctuel), OSC 1 sinus ou triangle, OSC 2 en dent de scie à -12 dB
   pour les harmoniques, phase fixe, unisson 1.
2. ENV 1 : attaque 2-5 ms (franche, sans clic), decay 120-200 ms à 165 BPM (le temps fait 364 ms)
   (moins qu'un temps : 324 ms), sustain 0 ; **pas de release** longue.
3. Filtre ladder ou diode, cutoff 150-400 Hz, enveloppe de filtre (ENV 3)
   rapide pour le claquement, résonance modérée ; drive du filtre pour le
   mordant (doctrine §9 : la rondeur est une variation, pas la base).
4. ReaEQ en aval : **passe-haut 60-80 Hz** si un rumble ou un kick long tient
   le sub, 30 Hz si la basse porte le sub (kick court) ; passe-bas 350 Hz
   sur la couche mid (Attack : synthé HPF 65 / LPF 350).
5. JS Saturation léger, puis ReaComp sidechainé par KICK avec les mêmes
   réglages que le rumble (§2.3). Sur la DT2 : `SCS` = TRK1 pour la 9 aussi.
6. Item MIDI `..x...x...x...x.` sur la tonique, puis variante tonique /
   quinte (`..x...x...x...y.`). Comparer avec le kick : propre sur la
   tonique et la quinte, brouillé sur la tierce (KT5, exercice 2).
7. Export **one-shot par note** : une note de 200 ms rendue seule, nommée
   `bass_sub_F#.wav`, `bass_sub_C#.wav` (quinte) ; sur la DT2, machine
   ONESHOT, `TUNE` 0, trigs en contretemps. Variante boucle (BL) : rendre
   une mesure complète avec le ducking, pour une 9 qui « roule ».

### 6.2 Trois couches (Attack Magazine)

Quand une seule basse ne tient pas : **sub** = la queue du kick elle-même,
passe-bas 80 Hz (c'est le kickbass en version douce) ; **synthé** Vital
HPF 65 / LPF 350 ; **percussive** = le kick envoyé dans un delay à la
double-croche (ReaDelay, 1/16, feedback bas, passe-bas 200 Hz), le « rumble
en contretemps » de [[maison-rumble-dans-le-kick]].
Sur la DT2 ces trois couches ne tiennent pas sur une track : choisir
laquelle est la 9, figer les autres dans le kick ou le rumble.

### 6.3 Ligne acid, Acid V (track 10, et basse acid)

1. Piste ACID, Acid V ; séquence interne ou item MIDI de 16 pas sur le mode
   de la bank (phrygien sur la tonique, [[../keyboard-gammes]]).
   Dent de scie pour l'acid tribe, carré pour un son plus rond.
2. Cutoff bas, résonance haute, env mod fort, decay court ; accents sur
   deux ou trois pas, un slide par mesure au plus. Le drive interne d'Acid V
   pour le grain ; Trash en parallèle (§2.4) pour l'acid core.
3. **Passe-haut** ReaEQ à 120-200 Hz dès que le grave est tenu par un
   kickbass ou un rumble : la ligne acid est une ligne, pas une basse (KT7,
   KT11). En **acid tribe** sans kickbass, Acid V peut être la basse en
   contretemps elle-même (`X.x.X.x.` du sub quand la basse descend sous
   200 Hz, KT5) : alors passe-haut à 40-60 Hz et ReaComp sidechainé.
4. Pour la DT2, deux voies : rendre des one-shots par note (track 10 en
   audio, un sample par degré), ou garder Acid V live sur le Mac séquencé
   par une track MIDI ([[../midi-vst]]).

### 6.4 Valider une basse

Avec le kick, au casque : aucun battement (sinon la note est fausse de
quelques hertz, KT5) ; la double-croche du kick reste vide ; le kick garde
son attaque ; sur SPAN, la basse n'ajoute rien sous 60 Hz quand un rumble
ou un kickbass y est déjà.

## 7. Rendu et transfert vers la DT2

### 7.1 La fenêtre de rendu, champ par champ

Cmd+Opt+R (File > Render). La fenêtre fait peur la première fois ; cinq
champs comptent, le reste garde sa valeur par défaut.

| Champ | Valeur ici | Pourquoi |
|---|---|---|
| **Source** | « Master mix » quand les autres pistes sont mutées ; « Stems (selected tracks) » pour rendre la piste sélectionnée seule, avec ses effets mais **sans** les effets du master (SPAN n'y change rien) | un stem ignore les mutes des autres pistes : pas besoin de muter |
| **Bounds** | « Time selection » | le fichier fait exactement la longueur de la sélection : une note, un temps ou deux mesures (§2.2) |
| **Output > Directory, File name** | le dossier `rendus/` du projet ; nom tapé à la main (`kick_tribe_F#_165`) ; les jokers `$track` et `$project` existent pour les séries | le nom porte la note mesurée (§3.5), pas la note MIDI |
| **Sample rate, Channels** | **48000**, **Mono** | fréquence native de la DT2 ; le grave est mono (si la source est stéréo, Reaper somme gauche + droite) |
| **Format** | WAV, **24 bit PCM** ; « Normalize/limit » **décoché** pour le kick et le kickbass (garder la marge, la DT2 sature encore à l'overdrive) ; sur le rumble, normalisation de crête à -1 dB acceptée, à condition de baisser la 2 après coup | Transfer convertit en 16 bits à l'envoi |
| **Tail** | « Add tail » **décoché** (ou 0 ms) | sinon le fichier dépasse la sélection et la boucle ne tombe plus juste |
| Bouton | « Render 1 file » ; « Add to render queue » pour empiler plusieurs rendus (trois longueurs de kick) et les lancer d'un coup | |

Deux raccourcis pour les cas simples : sélectionner un item, clic droit >
**Glue items** le rend sur place avec ses fondus (sans les effets de la
piste) ; clic droit > **Apply track FX to items as new take** rend l'item
**avec** la chaîne d'effets de la piste, en gardant l'original comme prise
précédente (Cmd+Z ou le menu des prises pour y revenir). Le second est
pratique pour figer un kick traité, ou pour la variante en dossier du §2.4.

### 7.2 Du rendu à la machine

1. **Sélection temporelle** exacte (une note, un temps, une ou deux
   mesures) : glisser dans la règle avec l'aimantation active (Opt+S) ; pour
   une note seule, sélectionner l'item puis la sélection temporelle se cale
   dessus par double-clic dans la règle au-dessus de l'item (ou Time
   selection > Set time selection to items).
2. Rendu selon le tableau §7.1. Écouter le fichier rendu dans le Media
   Explorer (View > Media Explorer) : il lit au tempo du projet, ce qui
   permet de vérifier une boucle de rumble avant de l'envoyer.
3. Nommer avec le style, la note et le tempo : `kick_tribe_F#_165.wav`,
   `rumble_gritty_F#_165.wav`, `kickbass_sat_F#_160.wav`, `bass_sub_F#.wav`.
   La note vient de la mesure sur la queue, pas de la note MIDI.
4. Ranger les WAV dans la banque de samples (`/Volumes/xtreme/Samples`,
   [[../../kt-banque-samples]]) dans un pack `SoundDesign/` à côté de
   `SoundDesign/rumble/` (sous-dossier par rôle, `kick/`, `kickbass/`,
   `bass/` ; nom du pack à arbitrer avant le premier versement), puis
   réanalyse : le circuit habituel, écoute garder / écarter, export
   Transfer, conversion 16 bits.
5. Sur la machine : kick sur la 1 (ONESHOT, `TUNE` 0), rumble sur la 2 sur
   les mêmes pas que le kick, basse sur la 9 en contretemps ; preset nommé
   avec la note (`kick_tribe_F#`, `rumble_F#`, `bass_F#`), puis le kit
   (doctrine §8, §13). Garder le projet Reaper et les presets Vital / Kick 3
   dans le vault : le sample est figé, le projet est la source.

## 8. Pièges propres à la stack

- **Trash Lite est monobande** : saturer un kick entier mange le sub ;
  toujours derrière un JS 3-Band Splitter, branché sur 3/4 par le pin
  connector (§2.4). Convolve et le multibande sont dans la version
  payante, non nécessaire ici.
- **Send du kick déplacé de 1/2 vers 3/4** : le rumble se tait, parce que
  la reverb ne reçoit plus rien ; il faut les deux sends (§2.3), ou la
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
  dans Vital (§3.3) et transposer plus tard.
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

0. **Échauffement Reaper (15 min).** Construire le projet modèle du §2.0
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
   preset `gritty` et dans Reaper avec les valeurs du §4.1 ; au même niveau,
   écouter ce que Trash et ReaVerbate font de différent du tanh et de
   Freeverb, et noter dans [[../../../sounddesign/rumble]] ce qui vaut d'être
   porté dans un preset.

## Ressources

- Recettes et repères chiffrés des sources (Myloops, Futureproof, Attack
  Magazine, Gearnews, Bonedo, Elektronauts) : rassemblés dans
  [[../rumble-grave]] et [[../../veille-theorie]] §F ;
  valeurs données pour 125-140 BPM, recalées ici avec la table du §2.2.
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
