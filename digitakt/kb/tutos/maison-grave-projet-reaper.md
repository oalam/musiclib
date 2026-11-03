---
tags: [digitakt, kb, tutos]
theme: Grave sur Mac, ch. 2, le projet Reaper modèle : construction clic par clic, pistes, durées au tempo, sidechain par canaux 3/4, saturation par bandes (splitter, Trash sur 3/4, joiner), mesure SPAN
lot: 4
ordre: 2
source: "échange de travail du 2026-10-29 (stack retenue) ; chapitre détaché du tuto le 2026-10-31"
auteur: Tom (stack), rédaction à vérifier dans Reaper
modele: DT2
os: "1.17"
stack: [Reaper, Vital, Maschine Drumsynth Kick, Kick 3, iZotope Trash Lite, SPAN, ReaComp, Acid V]
parent: maison-sounddesign-grave-reaper
statut: draft
updated: 2026-10-31
---

# Grave sur Mac, ch. 2 — Le projet Reaper modèle

Chapitre 2 du tuto « sound design préparatoire » (lot 4 de [[_index]]).
Le hub [[maison-sounddesign-grave-reaper]] porte les arbitrages (§0), la stack et
les notions Reaper (§1), les pièges (§8) et les exercices (§9). Les numéros
de section sont ceux du tuto entier : un renvoi « §n » vise le chapitre n,
avec le lien de sa fiche quand ce n'est pas celle-ci.

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
   pas suivant moins un rien ([[maison-grave-kickbass]] §5).
6. **Item de la basse.** Même geste sur BASS, notes aux pas 3, 7, 11, 15
   (le contretemps), longueur deux ou trois pas.
7. **Lire en boucle.** La sélection temporelle couvre la mesure 1 ; touche
   R pour activer la répétition ; Espace. Le projet tourne comme un pattern.
   Muter KICKBASS, BASS et ACID (bouton M) : on entend le kick seul.
8. **Effets de base.** Sur chaque piste, FX > Add : les chaînes du §2.1,
   dans l'ordre du tableau. Les réglages viennent aux [[maison-grave-kick]] §3 à §6.
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
   et le soft clipper de la chaîne de sortie, [[maison-grave-kick]] §3.4). Le son revient entier.
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
rendre le kick sec ([[maison-grave-rendu-dt2]] §7), créer deux pistes enfants d'un dossier KICK (icône
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

## Liens

[[maison-sounddesign-grave-reaper]] · [[maison-grave-kick]]

#digitakt #kb #tutos #sounddesign
