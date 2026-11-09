# Changelog — mk-brain

Format [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Chaque slice
de `SPEC.md` § Phases = une entrée balisée `[N]` et une version mineure.

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
