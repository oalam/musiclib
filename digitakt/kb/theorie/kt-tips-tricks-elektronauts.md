---
tags: [digitakt, kb, theorie, kt]
theme: Tips & tricks de la communauté Elektronauts (fil Digitakt II)
lot: 5
ordre: 22
styles: [tous]
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
os: "1.17"
statut: draft
updated: 2026-10-22
---

# KT22 — Tips & tricks Elektronauts (fil Digitakt II)

**En une phrase** : le fil *Digitakt II Tips & Tricks* d'Elektronauts
(564 posts, d'avril 2024 à mai 2026) tourne autour de six idées qui comptent
pour un live sur notre grille : une **seconde séquence cachée dans chaque
pattern** (euclidien éteint, page de retrig, page loop hors longueur
maître, perform kit), le **CTRL-ALL ciblé** comme geste de fill, le
**preset pool** comme rack de fills et de one-shots, le **resampling
stéréo** comme fader d'Octatrack, la **vélocité et le key tracking** comme
macros, et un **projet modèle** (16 slots par défaut, kits, banques par
famille) pour ne plus repartir de zéro.

Source : fil
[Digitakt II Tips & Tricks](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556)
ouvert et tenu par LyingDalai ; lecture du 2026-10-22 via l'API du forum,
tri par nombre de likes. Chaque astuce renvoie au post d'origine (`#n`) ;
les gestes ne sont pas encore rejoués sur la machine (statut `draft`). Les
premières pages datent de l'OS 1.01, plusieurs astuces supposent l'OS
1.10 et plus (locks sur toute la track ou la page, gammes au bouton NOTE,
key tracking) ou 1.15 (machine Slice, track swap) ; tout est valable en
OS 1.17.

## Panorama du fil

Les 121 posts à 6 likes et plus, regroupés par famille ; les fiches de la
KB disent le geste, cette KT dit ce que la communauté en fait.

| Famille | Posts les plus votés | Ce que ça apporte au live | Fiche KB |
|---|---|---|---|
| Sauver un trig en preset, pool | #9 (62), #268 (38), #450 (21), #256 (15) | un son p-locké devient un preset ; le pool devient un rack de fills | [[../preset-pool]], [[../presets-kits-pool]] |
| Seconde séquence cachée | #97 (24), #286 (16), #304 (17), #81 (25), #250 (12) | deux ou trois variations par pattern sans changer de pattern | [[../euclidien]], [[../microtiming-retrigs]], [[../perform-kit-temp-save]] |
| CTRL-ALL ciblé | #36 (12), #425 (20), #295 (6), #522 (11) | fills d'un seul geste, retour par NO | [[../parameter-preset-locks]] |
| Resampling stéréo, crossfade | #76 (26), #88 (19), #208 (12), #93 (37), #149 (10) | une boucle du main comme track de secours, fondu LFO3 | [[../sampling-resampling]], [[../live-looping]] |
| Vélocité, macros, key tracking | #28 (28), #135 (22), #81 (25), #392 (21) | 4 paramètres sous un bouton, dynamique sans toucher au volume | [[../parameter-preset-locks]], [[../lfo]] |
| Compresseur et sidechain | #30 (17), #252 (35), #195 (9), #124 (7) | pompage propre, kick fantôme, make-up dans l'overdrive | [[../send-fx-compresseur]] |
| Projet modèle, kits, banques | #24 (28), #65 (23), #101 (42), #425 (20), #35 (22), #577 (4) | 16 slots par défaut, kit par couleur, banques par famille | [[../projet-sauvegarde]], [[../presets-kits-pool]] |
| Grid, wavetables, LFO random | #3 (37), #111 (24), #180 (28), #390 (8), #410 (21) | drones et textures depuis une chaîne 64 slices | [[../machines-src]], [[../lfo]] |
| Comb filter, delay accordé | #17 (9), #116 (13), #181 (24), #290 (9) | flanger de hats, résonateur accordé au C | [[../filtres]] |
| Transitions entre patterns | #375 (8), #78 (10), #222 (15), #540 (8) | LAST, note tenue à travers le changement, machines synchro | [[../fill-conditions]], [[../patterns-chaines]] |
| Raccourcis d'écran | #7 (8), #31, #32, #33, #114, #449, #553 | moins de menus pendant le live | [[../page-setup]], [[../mutes]] |

## Vocabulaire

- **CTRL-ALL / CTRL-SEL** : `[TRK]` tenu + un encodeur agit sur toutes les
  tracks cochées dans CONTROL ALL CONFIG (`[FUNC] + [FLTR]`) ; `[NO]`
  tant que `[TRK]` est tenu annule tout. Le fil dit « CTRL-SEL » pour
  rappeler que, contrairement au DT1, la sélection se règle.
- **Seconde séquence** : tout ce qu'un pattern garde en réserve sans
  pattern supplémentaire : trigs euclidiens préparés mais éteints, page
  de retrig éteinte, pages au-delà de la longueur maître, état perform.
- **Preset pool** : les presets chargés dans le pattern et jouables par les
  touches de trig (mode PRESET) ; tenir une touche remplace le son de la
  track sélectionnée le temps de l'appui.
- **Kick fantôme** : duplicata du kick sur une track retirée du main,
  seule source du sidechain ; le vrai kick peut se taire sans arrêter le
  pompage.
- **Sound macros** : PB, AT, MW, BC dans le SETUP de la track, 4
  destinations chacune, pilotées par un contrôleur ou un loopback MIDI.
- **Vélocité macro** : VEL → VOL coupé dans le SETUP, puis 4 destinations
  sur la page VEL MOD ; le bouton de vélocité devient une macro.
- **Key tracking** : page 2 du filtre, la hauteur de la note module
  jusqu'à 4 destinations (SRR, volume, pan, sends).
- **Slew** : avec `WAVE = RAND`, l'encodeur F lisse les sauts entre deux
  valeurs aléatoires ; sur `SRC:SLICE` d'une wavetable, un morphing.
- **Preroll** : nombre de mesures (jusqu'à 16) avant le début d'un
  enregistrement armé ; permet d'enregistrer une boucle externe avec ses
  queues de FX.

## Les astuces, famille par famille

Numéro de post entre parenthèses, lien vers le post ; les tracks sont
celles de la grille de la [[../../doctrine]] §1.

### 1. Presets et preset pool

- **Un trig devient un preset** ([#9](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/9)) :
  tenir le trig, presser `[PRESET/KIT]` : « Save new preset » avec tous ses
  p-locks. C'est le geste le plus voté du fil ; il transforme chaque
  trouvaille (un kick retuné sur le pas 9, un hat lock) en preset du +Drive.
- **Le pool comme rack de fills** ([#268](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/268)) :
  réserver un pattern à des presets de fills (risers, impacts, breaks),
  sauver son kit, vider le pool, puis KITS > MANAGE > flèche gauche >
  « Add to preset pool ». La première page du pool devient ce kit. Tenir
  une touche de preset mute la track sélectionnée et joue le preset à la
  place : un break remplacé par un riser, à la volée. Avec `RETRIG ON` et
  `LEN` au minimum, chaque touche tenue retrigue à la vitesse choisie :
  fills de jungle sur une boucle Werp / Repitch / Stretch. Le preset tenu
  continue même si on change de mode de trig.
- **Nommer d'un coup les 16 presets d'un pattern** ([#287](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/287)) :
  sauver le kit sous un nom, puis « Add to preset pool » : les 16 presets
  prennent ce préfixe.
- **Chaîne Grid sauvée en preset** ([#256](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/256)) :
  la machine Grid, ses slices et son `LEN` restent dans le preset. Un
  preset « progression d'accords » rappelé, trigs d'enregistrement, random
  locks, et le pattern démarre.
- **Faux slicing par le pool** ([#450](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/450)) :
  plusieurs presets du même sample avec des `STRT` différents, ajoutés au
  pool ; avec `[TRK]` + trig (lock sur toute la track) et `[PAGE]` + trig
  (sur une page). Depuis l'OS 1.15, la machine Slice rend ce détour moins
  nécessaire ([#491](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/491) :
  une Slice à une seule tranche sert aussi à rogner finement début, fin et
  boucle d'un one-shot, pour empiler deux ou trois snares).

### 2. Une seconde séquence cachée dans chaque pattern

- **Euclidien éteint = séquence B** ([#81](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/81),
  [#286](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/286),
  [#204](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/204)) :
  régler les paramètres euclidiens de certaines tracks (A et B non nuls)
  en laissant le mode éteint ; CTRL-ALL sur « Euclidean ON » bascule ces
  tracks sur la séquence euclidienne, les autres (à zéro) ne bougent pas.
  Un fill de toms sur les percs 4 et 5 pendant que kick et hats tiennent.
  Les p-locks posés sur les trigs euclidiens suivent la rotation (et se
  retrouvent aux mêmes pas sur la grille rouge).
  [#522](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/522) :
  `LEN` euclidien agit même mode éteint, donc CTRL-ALL dessus décale tout
  le pattern.
- **Euclidien → grille** ([#75](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/75)) :
  `[FUNC]` tenu en tournant `ENC` sur OFF convertit les trigs bleus en
  trigs rouges. Pratique après une recherche euclidienne concluante.
- **Page de retrig = fill verrouillable** ([#97](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/97)) :
  hat fermé 6 en croches, page RETRIG `LEN 2`, `RATE 1/16`, interrupteur
  OFF ; ON et le hat passe en doubles croches, OFF il revient. Indépendant
  de FILL et de l'euclidien : trois couches de variation dans un seul
  pattern. Sur les tracks qu'on ne veut pas voir rouler, `LEN` et `RATE` au
  minimum ou hors CONTROL ALL CONFIG.
- **Pages au-delà de la longueur maître** ([#304](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/304)) :
  longueur maître 64 pas, mais kick, rumble, clap et perc 1 à 4 écrits sur
  128 ; un page loop sur les pages 5 à 8 (`[PAGE]` tenu, trigs 9 à 16) ne
  change que ces tracks, les autres continuent. Un fill de batterie qui ne
  touche pas la seconde rangée.
- **Punch-in de variation par perform kit** ([#250](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/250),
  [#523](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/523)) :
  pattern fini, perform kit ON, variation (samples, FX), `[FUNC] + [YES]`
  temp save, perform OFF. En live : perform ON, `[FUNC] + [NO]` charge la
  variation, perform OFF revient au kit du pattern. Selon l'auteur, l'état
  perform est sauvé avec le projet (à vérifier, cf. [[../perform-kit-temp-save]]).
- **Locks conditionnels sur toute la track** ([#402](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/402),
  [#391](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/391)) :
  tenir un trig + `[TRK]` et régler `2:2` : toute la ligne attend le second
  tour. Même geste pour coller les notes d'une mélodie sur le kick 1 puis
  ramener `NOTE` à C5 d'un coup : le kick double la ligne sans sauter de
  hauteur.
  [#433](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/433) :
  changer la gamme ou la tonique dans KEYBOARD, tenir un trig + `[TRK]`,
  `NOTE` +1 puis -1 : toutes les notes se recalent sur la nouvelle gamme
  (OS 1.10 et plus, option « notes sur la gamme » activée, cf.
  [[../keyboard-gammes]]).

### 3. CTRL-ALL comme geste de fill

- **Casser puis revenir** ([#36](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/36)) :
  `[TRK]` tenu + `TUNE` casse tout ; `[NO]` avant de lâcher `[TRK]`
  restaure. Lâcher `[TRK]` sans `[NO]` rend le changement définitif :
  sauver avant.
- **Slots de samples en CTRL-ALL** ([#295](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/295),
  [#425](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/425)) :
  `[TRK]` tenu + encodeur de slot change le sample de toutes les tracks
  d'un cran, le groove inchangé. Les flèches haut / bas ne changent que la
  track sélectionnée. `[PAGE] + [YES]` randomise la page, et avec `[TRK]`
  tenu toutes les tracks. Sur notre grille ça n'a de sens que si les
  banques sont rangées par famille (slot n de chaque banque = même rôle),
  cf. §7.
- **Euclidien, retrig, LFO3 en CTRL-ALL** : les trois familles ci-dessus
  se déclenchent d'un seul geste si les tracks concernées sont cochées
  dans CONTROL ALL CONFIG. Hors config : les tracks qui ne doivent jamais
  bouger (kick 1, rumble 2, track MIDI 16).

### 4. Resampling stéréo et fondu entre original et resample

- **Resample du main en une touche** ([#76](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/76)) :
  source MAIN L/R, longueur du pattern, REC START sur le 1 ; le sample va
  sur une track mutée (16 chez l'auteur, réserve chez nous) en Grid avec
  les trigs déjà posés. Prep mutes pour basculer vers cette seule track et
  revenir, ou en fill : une version mangée de tout le pattern.
- **LFO3 comme crossfader** ([#88](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/88)) :
  sur la track resample, LFO3 → AMP VOL profondeur -0.01, sur toutes les
  autres +0.01, LFO arrêté ; CTRL-ALL sur la profondeur de LFO3 fond entre
  pattern et resample. Variante filtre
  ([#208](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/208)) :
  resample en passe-haut fermé, les autres en passe-bas ; CTRL-ALL sur la
  fréquence croise les deux. La boucle en lecture infinie survit à un
  changement de pattern tant qu'aucun trig ne retombe sur sa track.
- **Enregistrer une boucle externe avec ses queues** ([#93](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/93)) :
  DT2 maître, PREROLL = longueur du pattern externe, métronome, REC START
  = PLAY, longueur, ARM, `[REC] + [PLAY]` : l'enregistrement part à la fin
  du preroll, queues de FX comprises. Même logique en interne avec un page
  loop ([#149](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/149)) :
  doubler le pattern, boucler les pages vides, enregistrer les queues.
- **Boucle de nappe sans clic** ([#540](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/540)) :
  même sample sur deux tracks, trig de longueur 128 sur chacune, `1:2` et
  `2:2`, release ajusté pour couvrir la jonction ; resample de deux
  cycles, et le milieu du resample boucle proprement.
  [#551](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/551) :
  en ping-pong (LFO carré sur PLAY MODE, profondeur ~1.8) on inverse le
  sens au lieu de sauter, moins d'artefacts.

### 5. Vélocité, macros et key tracking

- **Vélocité macro** ([#28](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/28)) :
  VEL → VOL sur OFF dans le SETUP, puis 4 destinations (filtre, decay
  d'AMP, send delay, profondeur LFO) ; jouable en mode VELOCITY, lockable
  au bouton VEL, et en CTRL-ALL. Avec une chaîne de 16 hats classés par
  force, la vélocité choisit la slice : dynamique par multi-sample.
- **Overdrive comme volume** ([#135](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/135)) :
  VEL → VOL coupé, vélocité → OVERDRIVE : plus fort = plus sale, naturel
  sur les percs.
- **Sound macros par loopback** ([#81](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/81),
  [#62](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/62),
  [#516](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/516)) :
  MW (CC1), BC (CC2), AT, PB, 4 destinations chacune par track ; un
  contrôleur ou la track 16 en MIDI vers l'entrée de la DT2. Toutes les
  tracks sur le même canal MIDI reçoivent le même mouvement.
- **Key tracking** ([#392](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/392)) :
  vers SRR en négatif, les notes graves perdent du taux d'échantillonnage
  comme un sampler qui ralentit son horloge ; vers VOL en positif pour
  compenser ; vers PAN ou vers les sends (moins de reverb en bas).
  [#446](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/446) :
  key tracking +8 sur TUNE joue les slices d'une Grid chromatiquement
  depuis le clavier (valeur empirique).
  [#578](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/578) :
  OCTAVE à -1 dans le SETUP décale les slices d'une octave et libère les
  notes qui déclenchent les tracks sur un clavier externe.

### 6. Compresseur, sidechain, saturation

- **Routing et source** ([#30](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/30)) :
  cibles par `[FUNC] + [FLTR]` puis touches de trig ; source = une track,
  « /COMP » (les non routées) ou l'entrée. Le filtre de sidechain doit
  être en passe-bas pour que le kick déclenche
  ([#141](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/141)).
  Point de départ d'un utilisateur ([#195](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/195)) :
  seuil 35, attaque 0, release 43, make-up 4,3 dB, ratio 1:20, source
  /COMP, SC filter -50, mix 127.
- **Kick fantôme sur une track silencieuse** ([#252](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/252)) :
  source = track 16, retirée du main dans AUDIO ROUTING > TO MAIN. Avantages
  : enveloppe complète (decay, sustain), trigs de sidechain où on veut
  (four-on-floor sous un break half-time), p-locks d'attaque ou de release
  par trig, mute du pompage pendant une montée, signal propre (une onde
  carrée plutôt qu'un kick bizarre). C'est le « kick fantôme » de la
  doctrine §10 et de [[../send-fx-compresseur]].
- **Compresseur avant l'overdrive master** ([#124](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/124),
  [#570](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/570),
  [#571](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/571)) :
  les 24 dB de make-up poussent l'overdrive ; attaque et release minimum
  ajoutent une distorsion ; resampler ensuite le sample sali. Sous un sub
  avec du contenu aigu, « ça casse tout en morceaux ».
- **Patterns du DT1 qui sonnent faux** ([#388](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/388)) :
  sur le DT1 la reverb pouvait passer dans le compresseur ; sur le DT2 le
  routage des FX vers le compresseur est séparé et éteint par défaut.
- **Faux clipper pour grossir la basse** ([#543](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/543)) :
  sur chaque track à « écraser », LFO1 sinus rapide → AMP VOL (le flutter),
  LFO2 rampe exponentielle → profondeur de LFO1, déclenchés par LFO.T en
  rythme avec la basse. La basse ne change pas, les autres s'effacent
  autour d'elle.

### 7. Projet modèle, kits, banques

- **Slots 1 à 16 = kit par défaut** ([#24](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/24),
  [#65](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/65)) :
  tout nouveau pattern charge les slots 1 à 16 ; y mettre ses 16 one-shots
  favoris, sauver le projet sous « DEFAULT » et le verrouiller. C'est notre
  0-KIT A01-A16 ([[../../doctrine]] §2, [[../projet-sauvegarde]] dans la KB).
  [#577](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/577) :
  vider les 16 slots dans PROJECT RAM, sélectionner un dossier de 16
  samples du +Drive, « load to project » : ils tombent dans l'ordre sur les
  slots vides, un kit chargé en deux gestes.
- **Banques par famille, colonnes de tracks** ([#101](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/101),
  [#425](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/425)) :
  l'auteur range ses samples par banque (A kicks et basses, B-C hats et
  claps, D percs, E synthés, F-H FX) et pense ses 16 tracks en colonnes
  (1 et 9 kick et basse, 2-3 et 10-11 aigu, 4 et 12 percs...). Notre grille
  fait le choix inverse (rangée 1-8 corps, 9-16 tête, §1) mais le principe
  tient : un projet modèle plein, « save as » à chaque nouveau live, et le
  CTRL-ALL sur les slots devient musical.
- **Chaînes courtes ou slots pleins** ([#24](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/24),
  [#218](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/218),
  [#219](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/219)) :
  avec 1024 slots, un sample par slot et un LFO sur le slot remplacent la
  chaîne, sans silence perdu. Les chaînes gardent un intérêt pour des
  variations d'un même son (quatre kicks presque identiques, linear
  locks) : c'est le round-robin.
- **Kits et presets sont des copies** ([#35](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/35)) :
  charger un kit copie ses réglages dans le pattern, le lien avec le +Drive
  est perdu ; modifier le kit dans A02 ne touche pas A01. Les kits servent
  donc de modèles à rappeler (kit chords, kit dub, kit dnb), pas de
  réglages partagés comme sur A4 / AR.
- **Transporter un pattern vers un autre projet** ([#263](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/263)) :
  sauver le kit sous « temp », copier le pattern, ouvrir le projet cible,
  charger « temp », coller. Les locks de slot de sample ne suivent pas.
- **Multi-sample dynamique** ([#464](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/464)) :
  16 frappes d'un même fût en Grid, les 10 premières fortes, les 6
  suivantes de plus en plus douces ; la vélocité baisse le numéro de slice
  et augmente la profondeur d'un S&H sur la slice (round-robin), un second
  S&H minuscule sur TUNE et PAN ; MW bascule la banque vers des versions
  saturées. Un kit acoustique vivant sur 16 tracks.

### 8. Grid, wavetables, LFO aléatoire

- **128 pas = 64 demi-pas à x2** ([#3](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/3)) :
  trigs euclidiens convertis en grille, SRC Grid 32 ou 64, `LEN 4`,
  `[YES]` random locks : territoire DnB.
- **Drone wavetable** ([#111](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/111),
  [#76](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/76)) :
  Factory > 5-Oscillators > Wavetables, machine Grid, `GRID 64`, `SLICE
  32`, `PLAY FWD.L`, AMP REL au max ; LFO `RAND`, `SLEW 127`, `FREE`, `DEP
  32`, `DEST SRC:SLICE`, `MULT BPM 1`, `SPD 8`. Les wavetables d'usine
  passent sans clic en Grid 64.
  [#390](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/390) :
  pour balayer toute la table, slice 33, `LEN 1`, profondeur 31,99, sinon
  le LFO sort de la table et donne du bruit.
  [#473](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/473) :
  slice par défaut au milieu de la série pour qu'un LFO sinus ou random
  lissé couvre tout.
- **Grid random comme remix** ([#534](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/534)) :
  boucle d'une mesure en Grid 16, trigs sur les 16 pas, « linear locks »,
  puis euclidien ON et randomiser la page euclidienne : un remix plus
  musical que les random locks. Comme pour notre Id1 (track 5), cf.
  [[../slice-breaks]].
- **SRC + YES pour l'inspiration** ([#408](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/408)) :
  trente samples au hasard dans le projet, `[SRC] + [YES]` enchaîné : des
  slices aléatoires de samples aléatoires, puis mêmes AMP / FLTR / FX / LFO
  et nouveau `[SRC] + [YES]`.
- **Granulaire et sample comme oscillateur** ([#410](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/410),
  [#550](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/550)) :
  depuis l'OS 1.10 les clics ont presque disparu ; une note de synthé de
  3 s filtre ouvert, sculptée par les enveloppes et le filtre de la DT2,
  LFO libre sur `STRT` pour varier chaque frappe, triangle sur AMP VOL pour
  des grains doux. Échantillonner plus long que nécessaire pour monter la
  note sans atteindre le point de boucle.
- **Timestretch sans la machine** ([#179](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/179),
  [#237](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/237)) :
  un LFO sacrifié recrée le stretch sur une machine one-shot ; à l'inverse,
  un kick sauvé sous la machine Timestretch puis rejoué en one-shot fait un
  accent lourd.
- **Boucle depuis un point de départ** ([#72](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/72)) :
  en `FWD.L`, pour partir de `STRT` et boucler depuis zéro, `LOOP` à 0,02.

### 9. Comb filter et delay accordé

- **Comb sur tout, resample** ([#17](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/17)) ;
  **flanger de hats** ([#116](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/116)) :
  comb très lent, beaucoup de feedback, l'autre filtre en passe-haut, delay
  et reverb : hats flangés des années 90.
- **Accorder le comb** ([#181](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/181),
  [#392](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/392)) :
  `[FUNC]` tenu en tournant FREQ arrête sur 0, 48, 60, 72, 84, 127, des C
  à l'octave ; avec le key tracking du filtre page 2, un résonateur
  jouable. Utile pour accorder le comb sur la tonique du kick
  ([[kt-tonalite-du-grave]]).
- **Delay en résonateur** ([#290](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/290)) :
  onde à cycle unique ou transitoire, delay au temps minimum, feedback
  monté très lentement (103-110 selon la largeur de bande du delay),
  enveloppe de filtre positive : percussions à main, basses, plucks, puis
  resample pour jouer chromatiquement. Monter le BPM raccourcit encore le
  delay. Limiteur conseillé.

### 10. Transitions entre patterns

- **Nouvelles conditions** ([#78](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/78)) :
  `/A:B` (se tait au tour A tous les B), `LAST` et `/LAST` (ne joue que
  quand un autre pattern est cué). Conditions, probabilité et FILL se
  cumulent en ET ; la probabilité de track ne fait pas partie du calcul,
  la locker sur le trig si besoin ([[../fill-conditions]]).
- **Laisser sonner à travers le changement** ([#375](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/375)) :
  un dernier trig par track avec `NOTE` tenue (longueur max, enveloppe AHD
  et non ADSR) continue dans le nouveau pattern jusqu'au prochain trig de
  sa track ; Werp, Repitch et Stretch adoptent le nouveau tempo ; les
  paramètres touchés sautent à la valeur de la nouvelle track, donc garder
  des réglages proches d'un pattern à l'autre. `LAST` + un resample de la
  phrase font une transition simple.
- **Chaîne de patterns de montée** ([#222](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/222)) :
  patterns de 56 pas chaînés avec des fills de 8 pas, CTRL-ALL sur loop,
  tune, slot, longueur, note, probabilité et filtres.
- **Ableton et program changes** ([#224](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/224)) :
  clips de program change sans quantisation globale, quantisation Live
  égale à la longueur maître : les scènes partent avec le pattern.

### 11. Raccourcis d'écran et réglages

- **Page loop et page mute** ([#7](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/7)) :
  en grid recording, `[PAGE]` tenu : trigs 1 à 8 sautent à la page, 9 à 16
  mutent une page.
- **Mutes depuis le grid recording** ([#449](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/449),
  [#545](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/545)) :
  `[TRK]` puis `[FUNC]` (dans cet ordre) affiche le mode mute le temps de
  l'appui ; `[FUNC]` puis `[TRK]` sort du grid recording.
- **Menus secondaires** ([#31](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/31),
  [#32](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/32)) :
  flèches haut / bas pour passer d'un sous-menu à l'autre ; `[FUNC] +
  [SRC]` depuis FLTR ouvre le choix du type de filtre, depuis SRC le choix
  de machine ; flèches gauche / droite entre eux.
- **PTN sans tenir** ([#33](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/33)) :
  appui court sur `[PTN]`, flèches pour la banque ; copier-coller rapide
  de pattern (tenir un trig, copy, lâcher, tenir un autre, paste).
- **Remember subpage** ([#114](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/114)) :
  SETTINGS > PERSONALIZE, la machine retient la sous-page de chaque menu.
- **Micro timing à tout encodeur** ([#417](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/417)).
- **Reset de LFO par pas** ([#553](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/553)) :
  plutôt que locker LFO.T, locker le mode (TRIG / HOLD / ONE / HALF) sur
  le pas qui doit recaler et FREE sur les autres : la phase se conserve en
  passant d'un mode à FREE.
- **Changer de machine déplace les p-locks** ([#351](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/351)) :
  les locks restent à la même position d'écran et tombent sur le paramètre
  de la nouvelle machine, MIDI compris.
- **Quatre volumes** ([#279](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/279)) :
  niveau du sample, AMP, mixer par track, volume de pattern (page du
  compresseur) ; LFO sur l'AMP pour le tremolo, mixer pour le mix, les
  deux autres pour le gain staging.
- **Clics** ([#215](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/215)) :
  attaque, decay ou release au-dessus de 0 et notes de la longueur exacte
  du trig moins un peu.
- **Portamento legato** ([#480](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/480)) :
  LEGATO ON, seules les notes qui se chevauchent glissent.
- **Renommer et ranger dans Transfer** ([#242](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/242)) :
  renommage et dossiers directement sur le +Drive.

## Pourquoi ça marche

Concret d'abord : un pattern tribe à 170 sur notre grille, kick 1, rumble
2, perc 4-5, hats 6-7. Sans rien ajouter, il contient déjà un fill de
toms (euclidien éteint sur 4 et 5), un roulement de hats (page de retrig
sur 6), un break de batterie (pages 5 à 8 sur la rangée 1-8), une version
mangée de tout (resample sur 16, LFO3 en fader) et un kit saturé (perform
kit). Cinq variations, un pattern, zéro changement de pattern.

La raison est structurelle : sur la DT2, presque chaque couche du
séquenceur a un **interrupteur** (euclidien ON / OFF, retrig ON / OFF,
perform ON / OFF, page loop, mute) et le CTRL-ALL applique l'interrupteur à
un sous-ensemble choisi de tracks. Un interrupteur se joue d'une main sans
regarder, un changement de pattern non. La doctrine §4 dit que les mutes
sont le vrai séquenceur du live ; le fil ajoute que les interrupteurs de
couche en sont la seconde moitié.

Deuxième idée : la machine confond volontiers **son et réglage**. Un trig
p-locké est un preset, un kit est une copie, un sample resamplé est un
nouveau son, une vélocité est une macro. La communauté en tire une règle :
dès qu'un réglage plaît, le figer (preset, kit, resample) pour le
retrouver, puis continuer à casser l'original sans risque.

Troisième idée : le **projet modèle**. Les 16 slots par défaut, les kits
par couleur et les banques rangées par famille rendent le CTRL-ALL sur les
slots musical (le slot n de chaque banque joue le même rôle) et évitent de
reconstruire la grille à chaque live. Notre 0-KIT et nos banques par
couleur ([[../../doctrine]] §2, §13) sont la même réponse.

## Sur la DT2

Grille de la [[../../doctrine]] §1. Gestes : [[../euclidien]],
[[../microtiming-retrigs]], [[../perform-kit-temp-save]],
[[../sampling-resampling]], [[../preset-pool]], [[../send-fx-compresseur]],
[[../parameter-preset-locks]].

1. **Trois interrupteurs, un pattern (10 min).** Pattern tribe fini. Percs
   4 et 5 : E(5, 16) et E(7, 16) réglés, euclidien OFF. Hat 6 : page RETRIG
   `LEN 2`, `RATE 1/16`, OFF. CONTROL ALL CONFIG : 4, 5, 6 seulement.
   Jouer 8 mesures, `[TRK]` + euclidien ON pour 1 mesure, `[TRK]` + retrig
   ON pour 2 temps, `[NO]` pour revenir. Noter ce qui sert de fill et ce
   qui sert de break.
2. **Fader de resample (10 min).** Resample MAIN L/R d'une mesure, posé sur
   la 16 en Grid 16 avec 16 trigs. LFO3 → AMP VOL -0.01 sur la 16, +0.01
   sur 1 à 14, LFO arrêté. CTRL-ALL sur la profondeur de LFO3 : fondre vers
   le resample, filtrer le resample, revenir. Puis la variante filtre
   (passe-haut contre passe-bas).
3. **Pool de fills (10 min).** Pattern réservé : track 15 riser, 12 un cri,
   4 un impact, 5 une boucle de break en Repitch (1 mesure). Kit sauvé,
   « Add to preset pool ». Retour au pattern tribe, mode PRESET, `RETRIG
   ON` et `LEN` au minimum sur la 5 : tenir le break aux rates 1/8, 1/16,
   1/32 sur le dernier temps de la phrase ([[kt-phrasage-tension]]).
4. **Vélocité macro sur le hat (5 min).** Track 6, VEL → VOL OFF, VEL MOD :
   filtre +, decay +, send delay +, profondeur LFO -. Profils de vélocité
   de [[kt-hats]] : la même grille de vélocité ouvre maintenant le timbre
   au lieu du seul volume.

## Pièges

- CTRL-ALL sans CONTROL ALL CONFIG : le kick 1, le rumble 2 et la track
  MIDI 16 bougent aussi. Configurer avant, et sauver le pattern avant de
  casser (le retour par `[NO]` ne marche que `[TRK]` tenu).
- La page loop a eu des bugs en lecture live (OS 1.01, [#7](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/7)) :
  à revérifier en 1.17 avant de compter dessus en set.
- Les kits ne sont pas partagés entre patterns : modifier le kick dans A02
  ne corrige pas A01. Le « même kick dans tout le set » (doctrine §3) se
  tient par discipline ou par preset, pas par le kit.
- Chaînes de samples longues : lentes à charger et pleines de silence ;
  un sample par slot, 16 max par chaîne et seulement pour des variations
  d'un même son.
- Les « alt tracks » 1-6 / 9-14 de [#527](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/527)
  (chaque track du haut doublée par une variante en bas) contredisent la
  grille invariante : chez nous la variante vit dans les interrupteurs du
  même pattern, pas dans une autre track.
- Wavetable en Grid : hors de la plage (slice + profondeur du LFO) la table
  donne du bruit ; slice 33, profondeur 31,99.
- Le perform kit ne sauve rien : tout ce qui plaît se fige par temp save
  ou preset ([[../perform-kit-temp-save]]).
- Les réglages chiffrés du fil (seuil 35, release 43, feedback 103-110,
  key tracking +8) sont ceux d'un utilisateur, d'un sample et d'un OS :
  des points de départ, pas des valeurs.

## Ressources

- Fil source : <https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556>
  `[V]` (564 posts, lu le 2026-10-22 ; les numéros `#n` renvoient aux posts).
- Fil jumeau Digitone II Tips & Tricks, cité pour le remix Grid + euclidien
  ([#534](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/534)) `[R]`.
- Manuel DT2 OS 1.17 : §9 (presets, kits, pool), §10.4 (micro timing),
  §10.7 (longueur par track), §11.2 (TRIG, VEL MOD), §11.5 (filtre, key
  tracking), §13 (compresseur), §14 (sampling, preroll) ; p. 47 pour les
  locks sur toute la track ([#402](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/402)).
- Vidéos citées dans le fil (non reprises ici, cf. [[../tutos/_index]]
  pour les sessions décortiquées) : Eak (wavetables, song mode, sidechain),
  Speldosa (page loop hors longueur maître), GyZa (faux slicing par le
  pool), Chroma_Surge (granulaire), djst (sample comme oscillateur).

## Liens

[[_index]] · [[../../doctrine]] §1, §2, §4, §10, §13 · [[../preset-pool]] ·
[[../presets-kits-pool]] · [[../euclidien]] · [[../microtiming-retrigs]] ·
[[../perform-kit-temp-save]] · [[../sampling-resampling]] ·
[[../live-looping]] · [[../send-fx-compresseur]] ·
[[../parameter-preset-locks]] · [[../fill-conditions]] ·
[[../patterns-chaines]] · [[../filtres]] · [[../lfo]] · [[../machines-src]]
· [[../slice-breaks]] · [[../keyboard-gammes]] · [[../projet-sauvegarde]]
· [[../mutes]] · KT5 [[kt-tonalite-du-grave]] · KT9
[[kt-phrasage-tension]] · KT20 [[kt-hats]]
