# Changelog — mk-brain

Format [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Chaque slice
de `SPEC.md` § Phases = une entrée balisée `[N]` et une version mineure.

## [0.35.0] - 2026-11-11

### Ajouté

- [13] Presets de l'arpège : `arp.presets` dans `config/default.yaml`,
  un nom pour cinq réglages (ordre, octaves, gate, division, motif), 8 au
  départ (`ACD1`, `GAL2`, `TRIB`, `CTPS`, `RUSH`, `NAPP`, `HASD`, `TRIO`).
  Rappel par l'encodeur 5 `PRE`, PATTERN tenu : le preset s'applique dès
  qu'il est affiché. Un réglage retouché ensuite affiche `----` ;
  l'encodeur repart du dernier preset rappelé, gardé dans la session.
  Un preset mal écrit est refusé au chargement de la config.

### Modifié

- [13] Écran droit, PATTERN tenu : `PRE` au-dessus de l'encodeur 5, le
  motif resserré sur les trois colonnes suivantes (12 px par pas).
- Guide : encodeur `PRE`, capture `13-arpege.png` refaite.

## [0.34.0] - 2026-11-11

### Ajouté

- [12] Motifs de l'arpège : 16 pas par motif (`x` note, `X` note
  accentuée, `.` silence, `-` liée), bibliothèque de 8 motifs dans
  `arp.motifs` de `config/default.yaml` (`GALO`, `OFFB`, `TRES`, `A332`,
  `SYNC`, `ROLL`, `LONG`, `ACID`). Choix par l'encodeur 4 `MOT`, PATTERN
  tenu, `OFF` en premier ; le motif s'affiche en 16 cases sur l'écran
  droit. Le motif est calé sur la mesure (position sur la grille de la
  division, modulo 16) ; sur un silence la note attend ; un pas `x` part
  à `arp.unaccented` % (70) de la vélocité du pad, un pas `X` à la
  pression ; une note suivie de liées dure ces pas en plus de son gate.
- [12] `arp.motif` (motif de départ) et `arp.unaccented` dans la config ;
  motif gardé dans la session par son nom. Un motif mal écrit est refusé
  au chargement (`MotifError`).
- Guide : encodeur `MOT` et lecture du motif à l'écran, capture
  `13-arpege.png` refaite.

## [0.33.0] - 2026-11-11

### Modifié

- [11] Config de l'arpège sur **PATTERN tenu** : divisions, `ORD`, `OCT`
  et `GATE` ne s'affichent, et les encodeurs 1-3 ne les règlent, que
  pendant l'appui ; relâché, les écrans principaux et les encodeurs de la
  track reviennent. Un appui bref (moins de 300 ms, sans réglage) sort du
  mode. La page `ARP` en tête des pages de son disparaît, BROWSE ne change
  que les pages de son. Les boutons d'écran restent les divisions tant
  que le mode est actif.

## [0.32.1] - 2026-11-11

### Corrigé

- [11] Page ARP : course des encodeurs allongée, il était très difficile
  de viser une valeur. 24 unités brutes par valeur de `ORD` et `OCT`, 12
  par pas de 5 % de `GATE` (un CC : 4 par cran), réglables dans `arp:`
  (`raw_per_choice`, `raw_per_gate_step`).

## [0.32.0] - 2026-11-11

### Ajouté

- [11] Arpégiateur : mode `ARPG` sur le bouton PATTERN. Les pads tenus du
  clavier sont joués un par un, une note par division, sur l'horloge de
  la DT2 ; vélocité par la pression de chaque pad. Boutons d'écran =
  division ; page `ARP` des encodeurs en tête des pages de son (`ORD`
  up, down, updown, played, random ; `OCT` 1 à 3 ; `GATE` 10 à 100 %) ;
  NOTE REPEAT = maintien ; PATTERN sort vers le clavier, PAD MODE vers le
  MPC. Transport arrêté : pas d'arpège.
- [11] `arp:` dans `config/default.yaml` (valeurs de départ) ; ordre,
  octaves, gate et division gardés dans la session.
- Guide : section « L'arpégiateur », capture `13-arpege.png`.

### Modifié

- [9] LED PATTERN : atténuée hors `ARPG`, pleine en `ARPG` (elle était
  éteinte, le bouton n'avait pas de rôle).

## [0.31.0] - 2026-11-11

### Modifié

- [9] Bande des mutes : un fin pointillé vertical sépare les temps, entre
  les cases 4/5, 8/9 et 12/13 ; les 4 groupes de cases s'écartent de 1 px
  pour lui faire place. Les cases plus grosses sur les temps (v0.30.5,
  v0.30.6) sont retirées : elles ne se voyaient pas sur l'écran de la MK2.
- Captures du guide (`docs/img/`) régénérées.

## [0.30.6] - 2026-11-11

### Corrigé

- [7] Session perdue à l'arrêt du service : le signal d'arrêt levait une
  exception qui pouvait tomber pendant la sauvegarde (vu sur le Pi à la
  relance de 12:34). Ctrl-C et `SIGTERM` lèvent maintenant un drapeau lu
  par la boucle de jeu ; une lecture HID coupée par le signal sort de la
  boucle au lieu de planter.

### Modifié

- [9] Bande des mutes : les cases des temps (1, 5, 9, 13) sont plus
  grosses en permanence (13 × 12 px au lieu de 11 × 10), pour se repérer
  dans la rangée ; en v0.30.5 seule la case en train de jouer grossissait.
- Captures du guide (`docs/img/`) régénérées.

## [0.30.5] - 2026-11-11

### Corrigé

- [9] Bande des mutes : le temps ne se voyait pas. Le carré de 9 × 8 px
  ne laissait qu'un liseré de 1 px autour de lui, et la case ouverte
  ressemblait à une case mutée. Sur les temps (cases 1, 5, 9, 13) c'est
  maintenant la case qui grossit (11 × 10 → 13 × 12 px) ; le carré
  intérieur reste à 7 × 6 px partout.

## [0.30.4] - 2026-11-11

### Modifié

- [9] Bande des mutes : le carré de la double croche en cours est plus
  gros sur les temps (9 × 8 px en cases 1, 5, 9, 13 ; 7 × 6 ailleurs).
- [1] Vélocité : `velocity.full_scale` 2000 → 3000. Les frappes d'un jeu
  normal mesurées sur la MK2 vont de 2553 à 3203 et donnaient toutes 127.
- Captures du guide (`docs/img/`) régénérées.

## [0.30.3] - 2026-11-11

### Modifié

- [10] Aftertouch réglé sur une mesure de la MK2 (capture guidée sur le
  Pi) : `delay_ms` 80 → 120 (frappes de 54 à 80 ms), `threshold`
  900 → 2350 (pad tenu sans forcer : 1340 à 2263, pointe 2334),
  `full_scale` 3600 → 3000 (pad enfoncé : 2882 à 3171, pointe 3213).
- [9] Bande des mutes : carré de la double croche en cours agrandi
  (5 × 4 px → 7 × 6 px).

## [0.30.2] - 2026-11-11

### Corrigé

- [7] Pads en retard sur le Pi : le rendu des deux écrans prenait environ
  80 ms (35,8 + 43,5, mesuré sur le Pi 3B) et repassait toutes les 50 ms
  dans la boucle qui lit les pads. Les polices et leurs tracés de texte
  sont gardés en cache (`render._CachedFont`) : 4 ms par paire d'écrans
  (1,8 + 2,2), pixels identiques.

## [0.30.1] - 2026-11-11

### Corrigé

- [7] Retour arrière : MK2 ou DT2 absente au lancement ne compte plus
  comme un échec du code tiré. `mk-brain` sort avec le code 3
  (`boot.EXIT_NO_HARDWARE`, `Mk2NotFoundError` ou `MidiPortNotFoundError`),
  ignoré par `deploy/stopped.sh` ; le service relance et attend le
  branchement sans revenir à `state/last_good`.

## [0.30.0] - 2026-11-11

### Ajouté

- [10] Aftertouch : la pression d'un pad tenu part en aftertouch de canal
  sur sa track, en MPC et au clavier (le pad le plus appuyé), toujours
  actif ; pas à la frappe (`aftertouch.delay_ms`, `threshold`), un message
  par canal toutes les `interval_ms` au plus, 0 au relâché. Seuils à
  régler à l'essai.

## [0.29.0] - 2026-11-11

### Ajouté

- [9] Bande des mutes : un carré intérieur marque la double croche en
  cours dans la mesure (rien à l'arrêt).
- [9] Tempo de la clock sur l'écran droit, sous le mode, lissé sur une
  mesure (`ClockTracker.bpm_smooth`, régression sur 96 ticks).
- [9] Barre de la phrase : pointillé à chaque tour de pattern (4 mesures).

### Modifié

- [9] Écran gauche : colonne « écran de la DT2 » (pattern en noir sur
  blanc, `TR 12` dessous), puis la banque et sa tonalité ; alertes,
  dernier geste et frappe remplacent cette ligne, les mutes restent
  visibles.
- [9] Écran droit : phrase en noir sur blanc dans le coin gauche
  (`PHR 01`), mesure / longueur, mesures avant le cap, pattern suivant ;
  étiquette du mode en haut à droite (avant : en bas à gauche de l'écran
  gauche).

### Retiré

- [9] Code de la grille à côté de la track (`BD T01`) ; `track_names`
  reste dans la config pour le menu.

## [0.28.0] - 2026-11-11

### Ajouté

- [9] SHIFT + encodeur : réglage temporaire sur tous les paramètres,
  rendu à sa valeur d'avant au relâché de SHIFT (cumulable, aussi sur le
  groupe SOLO) ; le PB garde son retour au centre.
- [9] Étiquette de mode : `MUTE` ou `SELECT` tant que le bouton est tenu.

### Modifié

- [9] LED GROUP transport lancé : le bloc en cours clignote au temps, en
  vert puis en orange (`leds.phrase_warn`) la dernière mesure avant un
  cap ; les blocs passés restent fixes.
- [9] LED PLAY : clignote au tempo (avant : pulse sur le 1 de la mesure).
- [9] SELECT tenu : seul le pad de la track sélectionnée reste allumé.

### Retiré

- [9] Messages `MPC`, `SOLO`, `SOLO off` qui doublaient l'étiquette de
  mode ; le passage en clavier n'affiche plus que la gamme.

## [0.27.0] - 2026-11-11

### Ajouté

- [7] Extinction propre du Pi depuis la MK2 : SHIFT + ERASE tenus 2 s
  (sous le service seulement, relâcher avant annule). Session sauvée, LED
  éteintes, `POWER OFF` / `unplug in 15 s` laissé à l'écran, puis
  `systemctl poweroff`.
- [7] `deploy/mk-brain-pull.service` et `deploy/pull.sh` : `git pull` à
  l'arrivée du réseau, relance du service si `mk-brain/` a changé.

### Modifié

- [7] Le service ne dépend plus du réseau : le jeu démarre avec la copie
  locale sans attendre (boot mesuré à 65,6 s avec l'attente). `sync.sh`
  ne fait plus que le retour arrière, décidé sur le contenu de
  `mk-brain/` et plus sur le commit du dépôt.

## [0.26.2] - 2026-11-11

### Corrigé

- [7] Boutons et encodeurs muets sur le Pi : la MK2 n'y émet jamais le
  rapport 0x01 par interruption (pads et écrans seuls fonctionnaient).
  L'état est demandé par GET_REPORT après chaque lecture et rendu comme
  un rapport 0x01 quand il change ; sous Linux, hidapi passe par le
  backend hidraw (module `hidraw`), plus par libusb. Rien ne change sur
  le Mac.

## [0.26.1] - 2026-11-10

### Corrigé

- [9] Anti-rebond aussi sur MUTE + pad et SELECT + pad (un mute
  rebondissait en démute au relâché du doigt).

## [0.26.0] - 2026-11-10

### Ajouté

- [9] Mode courant toujours affiché : `MPC`, `KEYS` ou `SOLO` en vidéo
  inverse en bas à gauche de l'écran gauche, même NOTE REPEAT tenu.

### Modifié

- [9] PAD MODE sort de SOLO (sans changer la disposition).
- [9] PB revenu sur SHIFT (`PB: hold SHIFT`), aussi en SOLO.

### Retiré

- [9] Perform par SHIFT + pad tenu : SHIFT + pad joue le pad ; le
  perform passe par SOLO seul.

## [0.25.0] - 2026-11-10

### Modifié

- [9] SOLO : pad n = track n en MPC comme en clavier (la table `mpc` ne
  sert plus sous SOLO).
- [9] PB tenu par MUTE au lieu de SHIFT (`PB: hold MUTE`), aussi en
  perform ; au relâché de MUTE, retour au centre sur chaque track bendée.

## [0.24.2] - 2026-11-10

### Corrigé

- [9] SOLO : rebonds du pad au relâché (un tap basculait plusieurs fois) ;
  un appui moins de `play.tap_debounce_ms` (150 ms) après le relâché du
  même pad est ignoré.

## [0.24.1] - 2026-11-10

### Modifié

- [9] Pads sous SOLO : bleu très faible au repos, vert vif dans le groupe,
  à la place des couleurs du MPC et du clavier (`leds.perform_idle`,
  `leds.perform_on`).

## [0.24.0] - 2026-11-10

### Ajouté

- [9] Perform verrouillé par SOLO (LED pleine) : les pads ne jouent plus,
  un tap ajoute ou retire la track du pad au groupe des encodeurs ; SOLO à
  nouveau vide le groupe. Écran `PERF x2` pour plusieurs tracks.

## [0.23.2] - 2026-11-10

### Corrigé

- [9] Perform : plus de retour de valeur au relâché du pad ; la valeur
  réglée reste, seuls les encodeurs reviennent à la track sélectionnée.
  `Faders.snapshot` / `put_back` retirés.

## [0.23.1] - 2026-11-10

### Modifié

- [9] Pages d'encodeurs réordonnées : page 1 LVL BR OVER SRR / DEL REV CHO
  TUNE, page 2 LVL CUT RES ENV / MW BC PB PAN.

## [0.23.0] - 2026-11-10

### Ajouté

- [9] Perform : SHIFT + pad tenu ne joue pas ; les encodeurs règlent la
  track du pad (entrée `mpc` en MPC, pad n = track n en clavier) tant qu'il
  est tenu, puis chaque paramètre touché reprend sa valeur d'avant,
  renvoyée à la DT2. Écran : `PERF` et la track du pad, ses faders.
  `Faders.steps` / `nudge` / `snapshot` / `put_back`.

### Modifié

- [9] LED GROUP transport arrêté : la banque courante seule, les autres
  éteintes.
- [9] Écrans du clavier = ceux du MPC (pattern, track, mutes, phrase) ;
  restent le cadre, la frappe en note + degré et `oct +1`. Menu et fiche
  de banque retirés de l'écran. Maquette `12-perform` au lieu de
  `12-clavier-menu`.

### Retiré

- [9] PATTERN + pad (Program Change) : la DT2 seule change de pattern ;
  PATTERN n'est plus affecté.

## [0.22.1] - 2026-11-10

### Corrigé

- [7] Service : `PYTHONUNBUFFERED=1`, la sortie de `play` arrive tout de
  suite dans `journalctl` (elle restait en tampon).

## [0.22.0] - 2026-11-10

### Ajouté

- [7] Portage Pi, partie logicielle : `deploy/mk-brain.service` (systemd,
  relances sans fin toutes les 3 s), `deploy/sync.sh` (`git pull` limité à
  10 s une fois par démarrage, `pip install` si `pyproject.toml` change,
  retour à `state/last_good` après 2 échecs d'un nouveau commit),
  `deploy/run.sh`, `deploy/stopped.sh`, règle udev `deploy/99-mk-brain.rules`
  pour la MK2. `boot.py` : la boucle de `play` qui tourne écrit le commit
  dans `state/last_good`.
- [7] Statut de synchro (`sync`, `offline`, `back` + commit ou date) en haut
  à droite de l'écran de sélection.

### Modifié

- [7] `SIGTERM` traité comme Ctrl-C : session sauvegardée, LED et écrans
  éteints à l'arrêt du service.
- [7] Raspberry Pi OS Trixie Lite au lieu de Bookworm (Python 3.12 requis).

## [0.21.0] - 2026-11-09

### Ajouté

- [8] Mode MPC : table `mpc` de `config/default.yaml`, 16 pads
  `{pad, track, note, label, color}`, une tranche (machine SLICE, `SLICE`
  = `NOTE`) sur le canal de sa track ; kit BD/BD2 (T1), SD/SD2/CP (T3),
  RS et toms (T4), hats (T5), CR/RD (T6). Pads au chargement, label et
  cible à l'écran à la frappe. Sonde `scripts/dt2_mpc_probe.py` passée
  (SPEC questions 16-17) : les notes sur le canal d'une track non active
  s'enregistrent sur elle en LIVE REC, la note 60 joue la tranche 1 et
  le trig enregistré porte une NOTE.
- [8] PAD MODE bascule MPC ↔ clavier ; une note tenue s'éteint sur le
  canal et la note où elle est partie.
- [8] `docs/screens.py` : captures des écrans et des LED rendues par le
  vrai code, sans matériel (`docs/img/`).

### Modifié

- [8] Live et design fusionnés en un seul mode : une banque courante (PC
  reçu ou GROUP seul, sans envoi), une quantize, menu et PATTERN + pad
  partout, LED GROUP = compteur transport lancé, banques à l'arrêt.
- [8] Le clavier et les encodeurs visent la track sélectionnée ; SELECT +
  pad 16 = AUTO CHANNEL (track active de la DT2), suivie aussi depuis la
  DT2. Pendant SELECT, MUTE ou PATTERN tenus, les pads montrent la grille
  des tracks ; sous PATTERN, seul le pad du pattern en cours reste allumé.
- [8] Menu en réglage direct : une entrée a toujours le focus (GAMME au
  départ), l'encodeur maître règle sa valeur à chaque cran sans
  validation, en boucle aux extrémités ; son appui passe le focus à
  l'entrée suivante (GAMME, TRACK, QUANT, PHRASE, en boucle) ; les boutons
  d'écran 1-4 y donnent le focus.
- [8] Huit gammes exotiques au menu GAMME, après les sept dispositions
  B-H : Locrian, Hung. min, Dbl harm., Blues, Hirajoshi, In-sen, Pelog,
  Whole tone (sans groupe ni mode de banque). La session garde la
  disposition par son nom ; les sessions d'avant, par sa lettre, restent
  relues.
- [8] Sessions d'avant la 0.21.0 relues : `design_bank` reprise comme
  banque courante ; disposition du clavier gardée par son groupe (`layout`).

### Retiré

- [8] `modes.py`, bascule SHIFT + CONTROL, `play.mode`, rappel `DT2 in
  LIVE REC?`, PATTERN + GROUP, disposition Drums (groupe A).

## [0.20.0] - 2026-11-09

### Ajouté

- [6] La MK2 suit la track active de la DT2 : avec `OUTPUT CH` = TRACK CH
  sur la DT2 (vérifié à l'écoute MIDI brute), un bouton tourné sur la
  machine arrive sur le canal de sa track et la sélectionne sur la MK2
  (`midi.knobs_on_track_channel`, vrai par défaut). Mutes exclus ; track
  16 (AUTO CHANNEL) suivie en design seulement.

## [0.19.0] - 2026-11-09

### Retiré

- [6] Page 3 des niveaux des 16 tracks (0.18.0) : pas retenue. Les flèches
  cyclent sur les deux pages de paramètres.

### Modifié

- [6] Slice 6 close : projets, contexte suivi par Program Change, sélection
  de projet, session, réglages issus des essais. Noms de samples reportés
  (SPEC, question 15).

## [0.18.0] - 2026-11-09

### Ajouté

- [6] Page 3 des encodeurs : niveau (LVL) des 16 tracks, affichage seul
  (`Faders.levels_view`, `render._levels`) ; 1-8 à gauche, 9-16 à droite.

### Modifié

- [6] Ordre des pages : p1 LVL CUT RES ENV / OVER DEL REV SRR ; p2 LVL MW
  BC PB / BR CHO TUNE PAN ; TYPE retiré.
- [6] Flèches BROWSE : page précédente / suivante en boucle (avant :
  gauche = p1, droite = p2) ; LED atténuées, pleines pendant l'appui.

## [0.17.0] - 2026-11-09

### Modifié

- [6] Design : chaque changement de banque (GROUP, PC d'une autre banque,
  premier passage) cale la disposition sur le mode de la banque ; PAD MODE
  ou le menu GAMME la surchargent jusqu'au prochain changement de banque.
- [6] Design : LED GROUP de la banque choisie en blanc plein
  (`leds.bank`), les autres en couleur de leur mode × `dim` ; avant, la
  choisie en couleur pleine se distinguait mal.

## [0.16.0] - 2026-11-09

### Ajouté

- [6] Design : pattern en cours en gros en haut à droite de l'écran droit.

### Modifié

- [6] Design : un Program Change d'une autre banque choisit la banque du
  design comme GROUP (octave à 0, phrase de la banque à la barre) ; un
  autre pattern de la même banque garde le choix fait à la main. Avant,
  le PC était sans effet en design.

## [0.15.3] - 2026-11-09

### Corrigé

- [6] Sens des mutes rétabli après l'essai : la DT2 envoie 1 = muté et
  0 = ouvert ; MUTE + pad renvoie 127 pour muter, 0 pour ouvrir (comme
  avant la 0.15.2). Réception : toute valeur non nulle = muté. Les 0.15.1
  et 0.15.2 reposaient sur une lecture inversée de l'essai.

## [0.15.2] - 2026-11-09

### Corrigé

- [6] MUTE + pad inversé sur la DT2 : envoi de 0 pour muter et 1 pour
  ouvrir, le même sens que ce qu'elle envoie (constaté à l'essai).

## [0.15.1] - 2026-11-09

### Corrigé

- [6] Mutes joués sur la DT2 ignorés : elle envoie le CC 94 avec 0 = muté
  et 1 = ouvert (constaté à l'écoute MIDI brute), le Pi attendait 127 pour
  muté (`Faders.received`).

## [0.15.0] - 2026-11-09

### Ajouté

- [6] Session par projet (`session.py`, `state/session-<projet>.json`) :
  banque du design, disposition, octave, banque, dernier pattern reçu,
  track sélectionnée, page et valeurs des faders, mutes. Sauvée au plus
  toutes les 2 s si elle change et à l'arrêt, reprise au chargement du
  projet sans rien envoyer à la DT2 (faders hors prise, mutes affichés
  seulement, un PC déjà reçu l'emporte). `Engine.snapshot` / `restore`,
  `Faders.values` / `restore`.

## [0.14.1] - 2026-11-09

### Modifié

- [6] Mode au démarrage réglable (`play.mode` de `config/default.yaml`),
  **design** par défaut pendant la préparation ; `live` pour la scène.
  Remplace le `demarrage: design` par projet prévu par la SPEC.

## [0.14.0] - 2026-11-09

### Ajouté

- [6] 6.C : sélection de projet (`selection.py`) au démarrage de
  `mk-brain play` : liste de `projects/*.yaml` (nom, date du dernier
  commit, nombre de banques, fichier invalide marqué et non chargeable),
  encodeur maître pour choisir, appui pour charger, dernier projet joué
  présélectionné (`state/last_project`, ignoré par git). SHIFT + BROWSE
  l'ouvre ou la referme, refusée en live transport lancé ; un Start en live
  la referme. `Engine.set_project` change de projet en cours de séance.

### Modifié

- [6] `mk-brain play --project` charge un projet sans sélection ; il n'a
  plus de défaut (solaris passait d'office).
- [6] Noms de samples à la frappe reportés : le lives JSON n'associe pas
  les samples aux tracks hors `0-KIT` (SPEC, question 15).

## [0.13.0] - 2026-11-09

### Ajouté

- [6] 6.B : en live, la banque du dernier Program Change reçu règle le
  contexte (`Engine.context`, `live_sheet`) : sa longueur de phrase
  s'applique avec la remise à 1 (`PhraseCounter.reset_next_bar(length=)`,
  tout de suite transport arrêté), sa tonique et son mode s'affichent en
  haut à droite du bandeau droit. Le design garde sa banque et ignore le PC.
- [6] Annonce d'une nouvelle banque : clé, titre et description 2 s sur
  l'écran droit en live (le compte à rebours garde la priorité), accents
  retirés (`render.ascii_text`).
- [6] Console de `mk-brain play` : banque, tonique et mode devant chaque note.

### Modifié

- [6] La phrase du live n'est plus seulement celle de la config :
  `play.phrase` ne sert que sans banque du projet.

## [0.12.0] - 2026-11-09

### Ajouté

- [6] 6.A : `mk-brain convert <doctrine>` (`convert.py`) lit le front matter
  `mkbrain:` de la doctrine du set et le lives JSON qu'il référence, recoupe
  banques, tonalités (`Bb` = `A#`, `m` / `phrg`) et tempos, et écrit
  `projects/<set>.yaml` (rejouable, en-tête « GÉNÉRÉ »). Divergence, clé
  inconnue ou front matter absent : `ProjectError` avec `doctrine:ligne`.
- [6] Front matter `mkbrain:` en tête de `digitakt/doctrine-dt2-solaris.md`,
  banques A-G ; **G-JOKER** en chromatique sur A#, 165 BPM.
- [6] `project.note_name` (normalisation des toniques, partagée par le
  modèle et `convert`).

### Modifié

- [6] `projects/solaris.yaml` est généré, plus écrit à la main ; le test
  provisoire de recoupement (5.D) devient `tests/test_convert.py`, qui
  échoue aussi si le projet commité est périmé. GROUP G en design choisit
  désormais G-JOKER.

## [0.11.0] - 2026-11-09

### Ajouté

- [5] Octave des pads en design aux flèches de transport (◀ ▶ à côté de
  RESTART) : ±1 octave par appui, ±4 au plus (essayé), refusé si une note sortait
  de 0-127 (`octave limit`), sans effet en rythmique ni en live ; remise
  à 0 au changement de banque (GROUP) ; LED pleine du côté décalé,
  `oct +1` sur l'écran droit. `layouts.shift_octave` et `layouts.fits`.
- [5] 5.D essayée sur la MK2 : banques, menu, pages d'encodeurs et pitch
  bend validés.

## [0.10.1] - 2026-11-09

### Modifié

- [5] Pitch bend (encodeur 4, page 1) seulement avec SHIFT tenu ; au
  relâché de SHIFT, remis au centre sur le canal où il est parti.

## [0.10.0] - 2026-11-09

### Ajouté

- [5] Deux pages d'encodeurs, flèches à côté des écrans (BROWSE ◀ ▶) :
  p1 LVL, MW (CC 1), BC (CC 2), PB (pitch bend), CUT, RES, TYPE (76),
  ENV ; p2 BR (54), OVER (57), SRR (55), DEL, REV, CHO (12), PAN, TUNE
  (16), numéros de l'annexe B du manuel. Message `PitchBend` vers la DT2.

### Modifié

- [5] Textes d'écran en anglais, sans accent (la police n'en a pas) :
  degrés, gestes, alertes, bascule de mode, noms des dispositions.
- [5] PATTERN sans effet en design : PATTERN + pad y joue la note,
  PATTERN + GROUP = GROUP, LED éteinte.
- [5] Page d'encodeurs : CUT RES ENV DEC LVL PAN DLY REV remplacée par
  les deux pages (DEC retiré).

## [0.9.2] - 2026-11-09

### Modifié

- [5] 5.D Écran gauche du design revu : valeurs du menu sans libellé sur
  une ligne, BANK retirée du menu (GROUP la choisit, l'écran droit
  l'affiche), menu sur les boutons 1-4 ; `DESIGN` remplacé par une icône
  `D` au coin haut gauche ; frappe affichée en note bémolisée et degré
  depuis la tonique (`Db6 tierce mineure`) sur une barre de vélocité.
  Fiche de la banque avec tonique en bémols et titre. Noms courts des
  dispositions (Chroma, Min. harm., Penta min.).

## [0.9.1] - 2026-11-09

### Modifié

- [5] 5.D Couleurs du design : en chromatique, seule la tonique est en
  couleur (rouge), les notes de la gamme en blanc, le hors gamme éteint au
  repos et blanc à la frappe ; familles `mineur` / `majeur` fusionnées en
  `gamme` (bleu), rôle `hors_gamme` retiré de la config.

## [0.9.0] - 2026-11-09

### Ajouté

- [5] 5.D Modèle de projet (`project.py`, `Project` / `Bank`,
  `ProjectError`) au schéma de la SPEC, avancé de la slice 6 ;
  `projects/solaris.yaml` écrit à la main (provisoire jusqu'à `convert`),
  banques A-F, G-JOKER en attente de sa tonalité ; un test vérifie qu'il
  reste aligné sur les tonalités et tempos de `library/lives/solaris.json`.
- [5] 5.D Design : GROUP A-H = banque du projet (LED GROUP = banques, à la
  couleur de leur mode, la choisie pleine) ; tonique de la banque = départ
  des dispositions, gamme de la banque = hors gamme en blanc dans la
  chromatique ; phrase de la banque au compteur. Premier passage en design
  sur la banque de la DT2 si le projet l'a.
- [5] 5.D Menu design : boutons d'écran 1-5 = BANK, GAMME, TRACK, QUANT,
  PHRASE ; encodeur maître = choix, appui = valider, même bouton = fermer.
  Écrans : entrées sous leurs boutons (ouverte inversée), `DESIGN` et
  mutes dessous, fiche de la banque et phrase en petit à droite.
- `mk-brain play --project` (défaut `projects/solaris.yaml`).

### Modifié

- [5] 5.D Clé `mode` sur les dispositions B-H de `config/default.yaml`
  (hub des intervalles des modes) ; en design, GROUP ne choisit plus la
  disposition (PAD MODE ou menu GAMME).

## [0.8.1] - 2026-11-09

### Modifié

- [5] 5.C Écrans revus à l'essai : chaque valeur au-dessus de son
  encodeur (faders 1-4 à gauche, 5-8 à droite, valeurs en gros), tiers
  supérieur des deux écrans en bandeau (contexte et track à gauche,
  phrase et progression à droite, compte à rebours en bandeau inversé) ;
  divisions du repeat sous leurs boutons d'écran ; même structure en
  design, écran gauche bordé.
- [5] 5.C Proportions inversées : bandeau sur les deux tiers (mesure,
  track et compte à rebours en gros), faders sur le tiers bas, nom et
  jauge alignés ; plus de valeur numérique, jauge en pointillé tant
  qu'elle est hors prise (remplace le `~`).
- [5] 5.C Bandeau gauche : pattern en cours et prochain (annoncé par la
  DT2 ou demandé par PATTERN + pad) et track sélectionnée en gros, bande
  des 16 mutes ; tempo, quantize et swing retirés. PC reçu transport
  arrêté = pattern en cours aussitôt.
- [5] 5.C Code de la track à côté de son numéro (`SD/CP T03`), repris de
  la grille de la doctrine §1 dans `track_names` de `config/default.yaml`.

## [0.8.0] - 2026-11-09

### Ajouté

- [5] 5.C `render.py` : écran gauche live (pattern, BPM, transport,
  quantize, swing, mesure / longueur en gros, phrase, cap, barre de
  mesures par blocs de 8 inversée dans les 4 dernières, temps, alerte).
- [5] 5.C Écran droit : 8 faders de la track sélectionnée (nom, valeur,
  `~` hors prise, jauge, pan depuis le centre), colonne touchée inversée
  1 s, dernier geste de contrôle en tête 1,5 s ; superpositions par
  priorité : bascule de mode, division du repeat, compte à rebours,
  frappe d'un pad (track et vélocité, 1 s).
- [5] 5.C `play` : écrans redessinés au plus toutes les 50 ms, envoyés
  seulement s'ils changent ; config `encoders.page[].bipolar`.

## [0.7.1] - 2026-11-09

### Corrigé

- [5] 5.B En live, la track sélectionnée (SELECT + pad) n'était repérée
  que SELECT tenu : son pad reste allumé à mi-intensité (`leds.selected`,
  0.5), plein à la frappe.

## [0.7.0] - 2026-11-09

### Ajouté

- [5] 5.B `modes.py` : modes live / design ; SHIFT + CONTROL tenus 1 s
  proposent l'autre mode, appui sur l'encodeur maître = confirmer (5 s,
  tout autre bouton annule) ; refusé en live transport lancé, à la
  proposition comme à la confirmation.
- [5] 5.B Moteur : live = pads en rythmique, GROUP seul sans effet ;
  design = disposition par GROUP ou PAD MODE (B chromatique au départ),
  encodeurs sur l'AUTO CHANNEL avec rappel `DT2 en LIVE REC ?`, SELECT +
  pad 16 permis ; quantize propre à chaque mode (off en design).
- [5] 5.B LED : CONTROL pleine en design ou proposition en attente,
  atténuée en live ; PAD MODE en design ; GROUP éteints en live arrêté.
- [5] 5.B `play` : écran gauche bordé avec bandeau `DESIGN`, proposition
  de bascule sur l'écran droit (`display.text_image(..., framed=)`).

## [0.6.2] - 2026-11-09

### Ajouté

- [5] 5.A Banque inconnue au lancement : PATTERN + GROUP A-H la choisit
  sans rien envoyer (LED GROUP = banque tant que PATTERN est tenu) ; la
  banque apprise d'un PC est journalisée.

## [0.6.1] - 2026-11-09

### Corrigé

- [5] 5.A Saut de valeur après un bouton tourné sur la DT2 : elle envoie
  ses boutons sur l'AUTO CHANNEL, pas sur le canal de la track ; ces CC
  vont désormais à la track sélectionnée sur la MK2 (mute ignoré).

## [0.6.0] - 2026-11-09

### Ajouté

- [5] 5.A `faders.py` : valeurs des 8 paramètres par track (64 si jamais
  vues), apprises des CC reçus de la DT2 (`ENCODER DEST` / `MUTE DEST` =
  `INT + EXT`), « hors prise » après un changement de pattern, restes de
  rotation cumulés (4 unités brutes par cran), mutes.
- [5] 5.A Moteur : 8 encodeurs → CC sur le canal de la track
  sélectionnée ; SELECT + pad = track des encodeurs, MUTE + pad = CC 94,
  PATTERN + pad = Program Change dans la banque du dernier PC reçu
  (refusé, « banque ? », tant qu'aucun n'est arrivé) ; un pad frappé avec
  un modificateur ne joue pas de note ; track de l'AUTO CHANNEL refusée.
- [5] 5.A LED : SELECT, MUTE, PATTERN atténués, pleins tenus ; MUTE tenu =
  tracks ouvertes allumées, mutées éteintes ; SELECT tenu = track choisie.
- [5] 5.A MIDI : envoi de CC et Program Change, réception des CC ;
  config `encoders` (page, `mute_cc`, `raw_per_step`) et
  `midi.program_channel` ; `play` affiche la track et le dernier geste.

## [0.5.1] - 2026-11-09

### Corrigé

- [4] Écrans peu lisibles (6 lu comme 8) : texte en police vectorielle
  intégrée à Pillow (présente aussi sur le Pi), taille 13, toujours
  5 lignes, au lieu de la police bitmap fine ; gras (1 px) réservé aux
  libellés (`text_image(..., bold=)`) : disposition et alerte dans `play`.

## [0.5.0] - 2026-11-09

### Ajouté

- [4] `phrase.py` : compteur de phrases pur (mesure 1-32/64, numéro de
  phrase, temps, cap 16/32/64, 4 dernières mesures, compte à rebours
  `-2` / `-1`, blocs de 8 mesures), remise à zéro différée à la barre
  suivante, nom de pattern depuis le Program Change (`36` → `C05`).
- [4] Moteur : Start, Stop et Program Change reçus de la DT2
  (`midi_io.feed_engine`) ; PC transport lancé = mesure 1 à la barre
  suivante, ignoré à l'arrêt, oublié si un Stop suit ; SHIFT + PLAY =
  mesure 1, SHIFT + GROUP n = début du bloc n, à la barre suivante.
- [4] LED : transport lancé, GROUP A-H = un bloc de 8 mesures allumé de
  plus toutes les 8 mesures, le bloc clignote au temps pendant la dernière
  mesure avant un cap ; PLAY pulse sur le 1.
- [4] `play` : écran droit `mesure/longueur` et pattern en gros, `*` dans
  les 4 dernières mesures, `-2` / `-1` avant un cap ; recalages, Start et
  Stop journalisés avec la position.
- [4] Config : `play.phrase` (32 ou 64), `leds.phrase` (couleur).

## [0.4.0] - 2026-11-09

### Ajouté

- [3] `quantize.py` : quantize « nearest » 1/16 et 1/8 (moitié du pas =
  immédiat), swing 50-75 % sur les 16ᵉ impairs.
- [3] `repeat.py` : 8 divisions du note repeat (1/4 à 1/64, triolets).
- [3] Moteur : messages datés confiés à l'ordonnanceur ; GRID fait défiler
  off / 1/16 / 1/8 ; SWING + encodeur maître règle le swing ; NOTE REPEAT
  tenu + pad = repeat, vélocité = pression courante, boutons d'écran 1-8 =
  division, SHIFT + NOTE REPEAT verrouille ; note off jamais avant sa note
  on quantizée ; LED GRID, SWING, NOTE REPEAT et division.
- [3] `play` : état `Q16 SW50 R1/16` à l'écran gauche, division en très
  gros pendant NOTE REPEAT ; section `play:` de la config (réglages de
  départ).
- [3] `ClockTracker.ticks_at` : position fractionnaire d'un instant.
- [3] Diagnostic par frappe dans `play` : position, pas visé, écart en
  ms, décision (immédiat ou retardé).
- [3] Essai sur la DT2 : frappes avant le pas posées sur la grille ; la
  quantize de l'enregistrement reste à la DT2 (décidé, cf. `SPEC.md`).

## [0.3.1] - 2026-11-09

### Modifié

- [1] Courbe de vélocité : `gamma` 0,6 → 0,4 et `full_scale` 2500 → 2000,
  les frappes légères sortaient à 2-14.

## [0.3.0] - 2026-11-09

### Ajouté

- [2] `clock.py` : suivi de la clock DT2 par régression linéaire sur 24
  ticks (période, phase, BPM à 0,1), Start / Continue / Stop, position
  mesure.temps.pas, détection du sysex Elektron (Transfer ouvert), écart
  d'arrivée des ticks à la prévision.
- [2] `scheduler.py` : envoi à l'instant cible (sommeil puis attente active
  sur 0,5 ms), écart d'envoi mesuré, abandon au-delà de 20 ms de retard.
- [2] `midi_io.py` : entrée DT2 horodatée dans le callback, `feed_clock`.
- [2] `mk-brain clock [--bench-note N --every T]` : BPM, transport,
  bilan de gigue ; banc d'envoi d'une note sur la grille.
- [2] `mk-brain play` : BPM, transport et position à l'écran gauche, note
  jouée avec degré et nom (`pad 3 -> b3 (D#5, 63)`), alerte Transfer ou
  clock absente.
- [2] Banc sur la DT2 : BPM à 0,1 près, envoi à 0,17 ms rms (p99
  0,72 ms), sans flam à l'oreille (constats dans `SPEC.md`).

### Corrigé

- [2] Ordonnanceur en retard de 1,3 ms en moyenne : attentes découpées
  (2 ms), attente active de 2 ms qui cède le GIL, bascule de fil à 0,2 ms.

## [0.2.0] - 2026-11-09

### Ajouté

- [1] `config/default.yaml` et `config.py` (Pydantic, `ConfigError`) :
  AUTO CHANNEL, courbe de vélocité, couleurs des rôles, des familles et
  des 16 tracks, dispositions A-H du template DT2 Pads.
- [1] `layouts.py` : note et couleur de chaque pad (rythmique pad n =
  track n, chromatique, gammes), courbe pression → vélocité.
- [1] `engine.py` : moteur pur, vélocité = pression maximale sur une
  fenêtre de 2 ms après l'attaque, note off sur la note réellement jouée,
  LED vives à la frappe et atténuées au repos ; GROUP A-H choisit la
  disposition (provisoire, à revoir à la slice 5).
- [1] `midi_io.py` (mido + python-rtmidi, `MidiError`) et
  `mk-brain play [--dry-run]`.
- [1] Essai sur la DT2 : tracks 1-16 en disposition A, gamme sur la track
  active une fois l'AUTO CHANNEL de la DT2 passé de 10 à 16.

### Modifié

- [1] Disposition A : pad n = track n sur les 16 pads (décision « Pads en
  live »), au lieu des tracks 1-8 doublées du template 7.D.

## [0.1.0] - 2026-11-09

### Ajouté

- [0] Paquet `mk-brain` (Python 3.12, hidapi, Pillow ; ruff, mypy strict,
  pytest) et CLI `mk-brain`.
- [0] `hid_mk2.py` : décodage des rapports MK2 repris de cabl (boutons et
  encodeurs 0x01, pads 0x20), rapports LED 0x80/0x81/0x82, accès hidapi,
  exceptions typées `Mk2NotFoundError`, `Mk2OpenError`, `Mk2ReportError`.
- [0] `display.py` : image Pillow 1 bit → 8 rapports `0xE0|écran` de 256
  octets, mire de test.
- [0] `mk-brain list` et `mk-brain spike` : mire sur les deux écrans,
  balayage des LED, écho des contrôles (LED et écran droit), bilan des
  contrôles jamais vus.
- [0] Essai sur la MK2 : mire nette sur les deux écrans, LED justes,
  48 boutons, 16 pads et 9 encodeurs décodés (constats dans `SPEC.md`).

### Modifié

- [0] Bouton `MAIN` de cabl renommé `MASTER_PUSH` (appui sur l'encodeur
  maître, vérifié).
