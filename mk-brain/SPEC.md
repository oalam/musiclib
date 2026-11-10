---
tags: [projet, spec, maschine, digitakt]
statut: draft
cree: 2026-11-09
---

# SPEC — mk-brain : la Maschine MK2 comme cerveau de jeu devant la Digitakt II

## En une phrase

Un Raspberry Pi, sans Mac ni logiciel Native Instruments, lit la Maschine MK2
en HID brut (pads, boutons, encodeurs) et pilote ses LED et ses deux écrans.
Il se cale sur l'horloge MIDI de la Digitakt II et lui envoie des notes
quantizées, du note repeat et des CC. Il affiche aussi BPM, paramètres et
position dans la phrase de 32/64 mesures.

```
Maschine MK2 --USB HID--> Raspberry Pi (mk-brain) --USB MIDI--> Digitakt II
   pads, boutons,          horloge suivie (PLL),       notes, CC, Program Change
   encodeurs               quantize, note repeat,  <--  clock 24 ppqn, Start/Stop,
   <-- LED, 2 écrans       phrases, rendu écrans        Program Change
                                  ^
                                  | git (à la maison, au démarrage)
                           mk-brain/projects/*.yaml, convertis depuis la doctrine du set
```

Un seul mode depuis la slice 8 (2026-11-09) : les pads jouent un kit en
tranches façon **MPC** ou un **clavier** calé sur la banque, bascule à
PAD MODE ; le contexte suit la DT2, et on enregistre mélodies et
mouvements de paramètres en LIVE REC sur la DT2 (live et design
fusionnés, cf. Mode unique et pads MPC). Aucun écran, clavier, front web ni
Wi-Fi sur scène : la MK2 est la seule interface, projet choisi à
l'encodeur maître.

Prototypage d'abord sur le Mac, avec le même code et le même câblage logique.
Le portage sur le Pi vient en fin de MVP.

## D'où on part

- **7.D (vault music)** : la MK2 joue déjà la DT2 via le Mac, en mode MIDI
  par Controller Editor, avec le template `digitakt/maschine/DT2 Pads.ncm2`
  et un routeur mido. Fiche : `digitakt/kb/controleur-maschine.md`.
  Limites : il faut le Mac et Controller Editor, sans horloge, sans
  quantize, sans écrans.
- **7.E (vault music)** : `scripts/dt2_midi.py` suit déjà l'horloge de la
  DT2 (24 ppqn, 6 clocks par double-croche, Start/Stop) pour rejouer une
  track en LIVE REC. Pièges déjà constatés et repris ici (fiche
  `digitakt/kb/midi-config.md`) :
  - Elektron Transfer ouvert fait perdre la moitié des clocks USB ;
  - la DT2 envoie ses clocks en continu, même à l'arrêt ;
  - la gigue USB est d'environ ±1 ms.
- **Chat de cadrage du 2026-11-09** : clock + quantize + note repeat,
  écrans, compteur de phrases. Le présent document l'arbitre.

## Périmètre

### Dans le MVP (choisi le 2026-11-09)

1. **Pads → notes DT2 + LED** : reprise des 8 dispositions du template
   `DT2 Pads` (groupe A rythmique notes 0-15 = tracks, groupes B-H
   chromatique et modes), même code couleur, vélocité depuis la pression.
2. **Horloge + quantize + note repeat** : suivi de la clock DT2 avec
   verrouillage de phase, quantize « nearest » réglable à la volée, note
   repeat sur pad maintenu, swing.
3. **Écrans** : écran gauche = contexte (BPM, pattern, quantize, position) ;
   écran droit = 8 encodeurs → 8 paramètres DT2 en CC, avec soft-takeover.
4. **Compteur de phrases 32/64** : mesure et phrase depuis le Start, remise à
   zéro manuelle et automatique sur Program Change, LED Group A-H, compte à
   rebours avant le cap.
5. **Deux modes, live et design** (ajouté le 2026-11-09), nettement
   distincts à l'écran et dans le comportement des contrôles.
   **Fusionnés le 2026-11-09** (slice 8) : un seul mode, pads MPC ou
   clavier à PAD MODE (cf. Mode unique et pads MPC).
6. **Projets** (ajouté le 2026-11-09) : conversion de la doctrine d'un set
   (front matter + `solaris.json`) en fichier projet, commit dans
   `mk-brain/projects/`, récupération par git au démarrage du Pi, choix du
   projet à l'encodeur maître.

### Hors périmètre (pas de pré-construction)

- **Front web, mobile ou non** : écarté le 2026-11-09, la MK2 suffit à
  choisir le projet et à régler la session.
- **Wi-Fi sur scène, point d'accès** : le réseau ne sert qu'à la
  synchronisation git, à la maison.
- Édition de la config depuis le Pi : on modifie la doctrine sur le Mac,
  on reconvertit, on commite. Les réglages de session (quantize, swing,
  longueur de phrase) se font à la MK2 et ne sont pas réécrits dans le
  projet.

- Tout ce qui demande un état renvoyé par la DT2 au-delà de la clock, du
  transport, des Program Change et des notes : noms de samples, valeurs
  réelles des paramètres, pattern en cours de lecture.
- Microcontrôleur (Teensy, ESP32) : écarté pour le MVP, le HID des écrans y
  serait trop coûteux à porter.
- Audio, sampling, navigateur de samples, séquenceur propre.
- Maschine MK3, Mikro, Maschine+ : MK2 seulement.

## Décisions arbitrées

| Sujet | Décision | Pourquoi |
|---|---|---|
| Matériel | Raspberry Pi 3 Model B (Linux), prototypage sur Mac | HID et écrans en Python ; MK2 + DT2 disponibles ; Pi 3B déjà en main, retenu le 2026-11-10 (question 5) |
| Langage | Python 3.12, paquet autonome `mk-brain` | même outillage que le vault (ruff, mypy strict, pytest, Pydantic) |
| Indépendance | aucun import depuis `music/scripts/` | le Pi ne déploie que `mk-brain/` ; les constantes utiles (6 clocks par pas, message sysex Transfer) sont recopiées et citées |
| Maître d'horloge | la DT2 mène (Clock Send + Transport Send) ; le Pi ne fait que suivre | les notes restent alignées sur les trigs de la DT2 |
| MIDI | `mido` + `python-rtmidi` (CoreMIDI sur Mac, ALSA sur Pi) | déjà éprouvé en 7.E |
| HID | `hidapi` (bindings Python `hid`) | le même code sur Mac et sur Linux (hidraw) |
| Rendu écrans | Pillow, image 1 bit, thread dédié | la boucle MIDI ne doit jamais attendre le rendu |
| Configuration | `config/default.yaml` (matériel, dispositions, page d'encodeurs) + un `projects/<set>.yaml` par set, validés par Pydantic | modifiable sans toucher au code |
| Canal de jeu | AUTO CHANNEL de la DT2 sur le **canal 16** (décidé le 2026-11-09 ; c'était 10 en 7.D) | sur un canal partagé l'AUTO CHANNEL l'emporte : seule la track 16, jouée depuis la DT2, perd son canal propre |
| Source d'un projet | la doctrine du set (front matter `mkbrain:`) + le `library/lives/<set>.json` qu'elle référence ; convertis sur le Mac | un seul hub par donnée, pas de recopie des tonalités et tempos à la main |
| Transport des projets | git : le Pi clone `oalam/musiclib` en partiel (`--filter=blob:none --sparse`, dossier `mk-brain/` seul), `git pull` au démarrage si le réseau répond, sinon dernière copie locale | le dépôt fait 677 Mo, le Pi n'en prend que `mk-brain/` ; le même mécanisme met à jour le code |
| Accès GitHub du Pi | clé de déploiement en lecture seule | moindre privilège, le Pi ne pousse jamais |
| Interface | la MK2 seule, aucun front web | décidé le 2026-11-09 |
| Modes | un seul mode ; pads MPC (kit en tranches, table `mpc`) ou clavier, bascule PAD MODE | décidé le 2026-11-09 (slice 8) : live et design ne se distinguaient plus, la disposition Drums ne servait pas |

## Architecture

### Fils d'exécution

| Fil | Rôle | Contrainte |
|---|---|---|
| HID in | lit les rapports MK2 (pads, boutons, encodeurs), pousse des évènements typés dans une file | poll serré, aucun traitement lourd |
| MIDI in | callback rtmidi : clock, Start/Stop/Continue, Program Change | horodate chaque tick avec `time.perf_counter_ns()`, rien d'autre |
| Moteur | consomme évènements et ticks ; quantize, repeat, phrases ; planifie les envois | seul propriétaire de l'état, pas de verrous éparpillés |
| Ordonnanceur | envoie les messages MIDI planifiés à l'instant cible | boucle à haute priorité, attente active sur les dernières centaines de µs |
| Rendu | dessine les écrans et les LED à partir d'instantanés de l'état | au plus 30 fps, seulement sur changement |

### Cœur pur et testable

Le moteur ne connaît ni HID ni MIDI. Il reçoit des évènements horodatés
(`PadPressed`, `ClockTick`, `Start`, `ProgramChange`…) et rend des
messages datés. On le teste avec une horloge simulée, sans matériel.

```
mk-brain/
├── SPEC.md, CHANGELOG.md, pyproject.toml, README.md
├── config/default.yaml           # matériel, dispositions, page d'encodeurs
├── projects/solaris.yaml         # généré par convert, commité, lu par le Pi
├── src/mk_brain/
│   ├── convert.py                # doctrine (front matter) + lives JSON → projet (Mac)
│   ├── project.py                # modèle Pydantic du projet, chargement
│   ├── selection.py              # liste des projets, dernier joué (6.C)
│   ├── session.py                # derniers réglages par projet (state/)
│   ├── modes.py                  # bascule live / design
│   ├── hid_mk2.py                # rapports HID MK2 : parse entrée, LED, écrans
│   ├── display.py                # Pillow 1 bit → octets écran
│   ├── midi_io.py                # ports DT2, callback clock
│   ├── clock.py                  # suivi d'horloge + PLL, BPM, position
│   ├── quantize.py               # nearest / grille / off, swing
│   ├── repeat.py                 # note repeat
│   ├── phrase.py                 # mesure / phrase / reset
│   ├── layouts.py                # dispositions A-H (portées de DT2 Pads)
│   ├── engine.py                 # assemble le tout, état unique
│   ├── render.py                 # pages d'écran et LED
│   └── main.py                   # CLI, fils, arrêt propre
└── tests/                        # miroir de src/
```

## Démarrage et choix du projet

1. Le Pi démarre et le service `mk-brain` se lance. Pendant ce temps,
   l'écran gauche affiche `mk-brain · démarrage`.
2. Synchronisation : si le réseau répond (Wi-Fi ou Ethernet de la maison),
   `git pull` du dossier `mk-brain/` (projets et code), avec un délai
   maximum de 10 s. Sinon, on garde la copie locale. L'écran affiche
   `sync ok · a1b2c3d` ou `hors ligne · copie du 2026-11-08`.
3. Écran de **sélection de projet** :
   - l'encodeur maître fait défiler la liste de `projects/*.yaml`, avec le
     nom, la date du commit et le nombre de banques ;
   - un appui sur l'encodeur charge le projet ;
   - le dernier projet joué est présélectionné : un seul appui suffit sur
     scène.
4. Le Pi entre en mode **live**, prêt dès que la DT2 envoie sa clock.

Changer de projet en cours de route : SHIFT + BROWSE ramène à la sélection.
Refusé en mode live tant que le transport tourne.

Le code n'est mis à jour qu'au démarrage, jamais pendant le jeu. Un code qui
ne démarre pas après un pull revient au commit précédent : **à préciser à
la slice 7**.

## Mode unique et pads MPC (slice 8, décidé le 2026-11-09)

**Fait foi sur les sections « Modes : live et design », « Pads en live » et
« Affectation des contrôles »**, qui décrivent l'état jusqu'à la slice 6 et
restent comme historique. Ordre : la slice 8 passe **avant** le portage Pi
(slice 7).

### Pourquoi

- La disposition rythmique « Drums » (groupe A, pad n = track n) ne sert
  pas au jeu : elle frappe chaque track à sa hauteur d'origine, une voix
  par track. Le **mode MPC** la remplace : un kit joué en tranches, sur les
  tracks de la grille (doctrine §1), sans rien changer aux canaux.
- Les deux modes ne se distinguent presque plus : le design suit déjà les
  PC d'une autre banque, la MK2 suit la track active de la DT2 (v0.20.0),
  et la bascule MPC ↔ clavier rend inutile de réserver une disposition au
  live. **Live et design fusionnent** : la seule bascule est celle des
  pads, à PAD MODE.

### Pads : deux dispositions, PAD MODE bascule

| | **MPC** (au chargement) | **Clavier** |
|---|---|---|
| Pad | joue l'entrée de la table `mpc` : canal de sa track + note de sa tranche | joue la disposition de la banque (chromatique, gammes B-H) sur la **track sélectionnée** |
| Couleurs | celle de l'entrée, × `dim` au repos, pleine à la frappe | rôles de la note (tonique, tierce, quinte, hors gamme éteint), comme le design |
| Flèches de transport | sans effet | octave ±4 |
| Écran gauche | vue « live » : pattern, track, mutes, compteur | vue « design » : disposition, note jouée et degré, cadre |

- **PAD MODE** bascule MPC ↔ clavier, LED pleine en clavier. Le cycle des
  dispositions passe par le menu GAMME seulement.
- La disposition du clavier reste calée sur le mode de la banque (5.D) ;
  GAMME la surcharge jusqu'au prochain changement de banque.
- Une note tenue au moment de la bascule s'éteint sur le canal et la note
  où elle est partie (pas de note bloquée).
- Un PC ne remplace la banque courante que si la DT2 change de banque et
  pas vers celle déjà choisie : GROUP A pendant que la DT2 joue E, puis
  E02, garde A (règle de la 5.D, précisée au code le 2026-11-09).
- Au chargement d'un projet : MPC. La session retient la dernière
  disposition du clavier, pas la bascule.

**Table `mpc` de `config/default.yaml`** (routage minimal, choisi le
2026-11-09) : 16 entrées `{pad, track, note, label, color}`. Le canal
est celui de la track (`TRACK n CHANNEL` = n) ; la track 16 (AUTO
CHANNEL) y est refusée à la validation. Kit retenu, lecture MPC (rangée
du bas = pads 1-4) :

```
 CR  T6/60   RD  T6/61   CH2 T5/63   OH2 T5/64     cymbales / variantes
 LT  T4/61   MT  T4/62   HT  T4/63   OH  T5/62     toms, open hat
 RS  T4/60   CP  T3/62   SD2 T3/61   CH  T5/61     rim, clap, snare 2, hat
 BD  T1/60   BD2 T1/61   SD  T3/60   CH1 T5/60     kick, kick long, snare, hat
```

- Couleurs : BD rouge ; SD, SD2, CP, RS orange ; CH jaune ; OH blanc ;
  toms bleu ; cymbales violet.
- Chaque track joue un **sample découpé en tranches** (machine SLICE,
  `SLICE` = `NOTE`) ; la note choisit la tranche. La note 60 joue la
  tranche 1 (vérifié le 2026-11-10, question 17). Au-delà de la dernière
  tranche, la note reboucle (grille de 6 : 66 rejoue la tranche 1) : la
  grille d'un sample doit compter au moins autant de tranches que ses
  pads dans la table.
- **Choke gratuit** : une track ne joue qu'une voix, OH coupe CH (T5),
  le clap coupe la snare (T3), un tom coupe le précédent (T4). Assumé.
- Vélocité depuis la pression, quantize et note repeat **globaux**, comme
  aujourd'hui ; chaque coup répété part sur le canal de son pad.
- À la frappe, l'écran gauche affiche le label et la cible (`CH1 T05 60`).

**Hors périmètre de la slice 8** (notés, pas pré-construits) :
- options par pad (quantize, repeat automatique, sans retrig : question 3) ;
- round-robin sur deux tracks, un pad vers plusieurs cibles (stack), layer
  ou CC par la pression (question 4) ;
- plusieurs tables `mpc` ou une table par projet ; rechargement à chaud de
  la config.

### Modifieurs, banque, encodeurs : un seul comportement

- **SELECT + pad n** : track n pour les encodeurs et le clavier, quelle
  que soit la disposition. **SELECT + pad 16** = l'AUTO CHANNEL, donc la
  track active de la DT2 (comme le design). Un bouton tourné sur la DT2
  sélectionne sa track (v0.20.0, inchangé).
- **MUTE + pad n** : mute de la track n (pad 16 refusé, inchangé).
- **PATTERN + pad n** : pattern n de la banque courante (PC), toujours
  permis.
- Pendant SELECT, MUTE ou PATTERN tenus, les pads montrent la grille des
  tracks (`track_colors`), pas la table `mpc` : pad n = track n. Sous
  PATTERN (pad n = pattern n de la banque courante), seul le pad du
  pattern en cours est allumé, les autres éteints (demandé le 2026-11-10) ;
  tout éteint si le pattern en cours n'est pas dans la banque courante.
- **Banque courante, une seule** : suivie par PC (la DT2 la donne), ou
  choisie par **GROUP seul** (sans envoi). Elle règle la tonique, le mode,
  la disposition du clavier, la phrase et la banque de PATTERN + pad.
  PATTERN + GROUP disparaît (doublon). GROUP ne touche que l'état du Pi :
  un appui par erreur ne change aucun son.
- **LED GROUP** : transport lancé, le compteur de phrases ; arrêté, les
  banques du projet (choisie en blanc), comme le design.
- **Encodeurs** : CC sur le canal de la track sélectionnée (ou l'AUTO
  CHANNEL pour la 16). En LIVE REC, les CC reçus sur le canal de la track
  active s'enregistrent en p-locks (vérifié) ; sur une track non active,
  à vérifier (question 16, reste ouverte pour les CC).
- **Clavier** : notes sur le canal de la track sélectionnée, l'AUTO
  CHANNEL pour la 16. Les notes reçues sur le canal d'une track non
  active s'enregistrent sur cette track en LIVE REC (vérifié le
  2026-11-10, question 16).

### Ce qui disparaît

- La bascule SHIFT + CONTROL 1 s, la confirmation à l'encodeur maître,
  `modes.py`, la clé `play.mode`, le verrou « live locked ». Le bouton
  CONTROL redevient non affecté.
- La quantize propre à chaque mode : **une seule quantize**, au réglage
  `play.quantize` (1/16) au chargement, GRID la fait défiler. À couper
  (GRID → off) avant un LIVE REC, la DT2 quantize l'enregistrement
  (décision de la slice 3 inchangée). L'indicateur `Qoff` / `Q16` reste
  dans le bandeau des deux vues.
- Le rappel `DT2 en LIVE REC ?` du design.
- La disposition rythmique « Drums » (groupe A) : `layouts` ne garde que
  B-H, la table `mpc` prend sa place.

Restent refusés transport lancé : SHIFT + BROWSE (sélection de projet).
Le menu (boutons d'écran 1-4 : GAMME, TRACK, QUANT, PHRASE) est
accessible dans les deux vues ; NOTE REPEAT garde la priorité.

**Compatibilité** : les sessions écrites avant la slice 8 se relisent
(`extra = "ignore"`, champs en trop ignorés) ; `design_bank` et `bank`
convergent sur la banque courante, le premier présent l'emporte.

### Préalable : sonde LIVE REC (passée le 2026-11-10, notes validées)

`scripts/dt2_mpc_probe.py` (vault, hors `mk-brain/`), DT2 en LIVE REC :

1. `channels` : notes 60 sur les canaux 1, 3 et 5, track 9 active. Les
   trigs s'écrivent-ils sur T1, T3 et T5 ? (question 16)
2. `slices --channel 5 --base 60` (puis `--base 0`) : quelle note joue la
   tranche 1, et la relecture rejoue-t-elle la même tranche ? (question 17)

Si 1 échoue : le MPC reste jouable, l'enregistrement d'un kit en un geste
passe par une capture côté Pi puis une réinjection track par track sur
l'AUTO CHANNEL (slice à part). Si la tranche ne s'enregistre pas : CC du
paramètre `SLICE` envoyé juste avant la note (p-lock), CC à chercher dans
l'annexe B.

### Critère de fin

Sur la DT2, kit de tranches chargé sur T1, T3, T4, T5, T6 : les 16 pads
jouent leur tranche, OH coupe CH ; PAD MODE passe au clavier sur la track
sélectionnée et revient sans note bloquée ; GROUP et PC changent la
banque dans les deux dispositions ; plus aucune trace des modes à l'écran.

## Modes : live et design

> **Remplacé par « Mode unique et pads MPC » (slice 8, 2026-11-09).**
> Historique de la séparation live / design, slices 5.B à 6.

| | **Live** | **Design** |
|---|---|---|
| Objectif | jouer le set, lire d'un coup d'œil, zéro fausse manœuvre | préparer les patterns sur la DT2 : enregistrer des mélodies et des mouvements de paramètres en LIVE REC |
| Contexte (banque, gamme, phrase) | suit la DT2 : Program Change reçu → banque et pattern → réglages de la banque dans le projet | choisi à la main (GROUP) ; un Program Change d'une autre banque la choisit aussi (2026-11-09) |
| Quantize du Pi | active, au réglage par défaut du projet | coupée par défaut (la DT2 quantize déjà en LIVE REC), activable |
| Pads | rythmique : pad n = track n ; SELECT / MUTE / PATTERN + pad | toute disposition, au choix par le menu ; sélection de track et de canal |
| Encodeurs | les 8 faders de la track sélectionnée (SELECT + pad), sur son canal, soft-takeover | pages de paramètres de la track ; les mouvements partent en CC sur l'AUTO CHANNEL et s'enregistrent comme p-locks de la track active si la DT2 est en LIVE REC (vérifié le 2026-11-09) |
| Compteur de phrases | affiché en grand | affiché en petit (repère pour enregistrer sur 1, 2, 4 mesures) |
| Écrans | grosses polices, peu d'infos | détail : messages MIDI envoyés, valeurs, notes jouées |
| Menus | inaccessibles | navigués par les 8 boutons au-dessus des écrans et l'encodeur maître |
| Distinction visuelle | fond normal, bandeau `LIVE` absent | écran gauche bordé, bandeau `DESIGN` permanent, pads en couleurs atténuées hors notes de la gamme |

- **Changer de mode** : SHIFT + CONTROL maintenu 1 s. L'écran droit affiche
  une confirmation (`→ DESIGN ? encodeur maître`). Désactivé en live tant
  que le transport tourne.
- **Mode au chargement** : `play.mode` de `config/default.yaml`,
  **design** depuis le 2026-11-09 (période de préparation, demande
  utilisateur) ; repasser à `live` pour la scène. Remplace l'idée d'un
  `demarrage: design` par projet. La clé `mode` d'une banque reste le mode
  musical.
- Le Pi ne sait pas si la DT2 est en LIVE REC (rien n'est transmis). Le mode
  design le rappelle à l'écran (`DT2 en LIVE REC ?`) au premier mouvement
  d'encodeur.
- **Précisé le 2026-11-09 (slice 5.B, provisoire jusqu'à l'essai sur la
  MK2)** :
  - la proposition (`-> DESIGN ?` sur l'écran droit, LED CONTROL pleine)
    attend 5 s l'appui sur l'encodeur maître ; tout autre bouton l'annule.
    En live, un Start pendant l'attente l'annule et la confirmation revérifie
    le transport ;
  - quantize propre à chaque mode : on retrouve celle du live en revenant ;
  - live : GROUP seul sans effet, LED GROUP éteintes transport arrêté
    (compteur transport lancé) ; PAD MODE éteint ;
  - design : GROUP seul ou PAD MODE choisit la disposition (B chromatique au
    départ ; GROUP en design = banque depuis la 5.D), LED CONTROL pleine ;
    SELECT + pad 16 permis (la track active est visée par l'AUTO CHANNEL),
    valeurs des encodeurs tenues sous la track sélectionnée ; rappel
    `DT2 en LIVE REC ?` au premier mouvement de chaque passage en design ;
  - Program Change reçu en design : banque de PATTERN + pad, faders hors
    prise et mesure 1 comme en live (faits de la DT2) ; depuis le
    2026-11-09, un PC d'une **autre banque** choisit aussi la banque du
    design (comme GROUP : octave à 0, phrase de la banque à la barre) ; un
    autre pattern de la même banque laisse le choix fait à la main ;
  - bandeau `DESIGN` et cadre de l'écran gauche dès 5.B ; couleurs des pads
    hors gamme et pages complètes : 5.C et 5.D ; `demarrage: design` avec
    les projets (slice 6).
- **Cadrage de la 5.D (décidé le 2026-11-09)** :
  - en design, **GROUP A-H seul = banque** : la tonique, le mode et la
    phrase de la banque colorent les pads par degré et calent la
    chromatique sur la tonique ; PAD MODE seul fait défiler les
    dispositions ; LED GROUP = banque choisie ;
  - **banques initialisées avec solaris** sans attendre la slice 6 (tonique,
    mode, tempo, phrase des banques A-G depuis la doctrine solaris et
    `library/lives/solaris.json`) ; à trancher en début de 5.D : fichier
    provisoire tenu à la main (doublon assumé jusqu'à `convert`) ou avance
    du modèle de projet et de `projects/solaris.yaml` ;
  - menu design : entrées de la maquette, BANK et GAMME alimentées par
    solaris.
- **Fait le 2026-11-09 (slice 5.D)** :
  - tranché en début de 5.D : **modèle de projet avancé** (`project.py`,
    `Project` / `Bank` au schéma du front matter, `ProjectError`) et
    `projects/solaris.yaml` écrit à la main, marqué provisoire, jusqu'à
    `convert` (slice 6) ; `tests/test_project.py` le recoupe avec les
    `keys` et `tempos` de `solaris.json`. Banques A-F ; **G-JOKER absent** (ajouté à la 6.A, cf. Projets)
    (ni tonalité ni tempo dans le JSON : kick + sub en fa, la# et do), à
    trancher avec le front matter. Phrase de 32 partout (`defaults`), la
    doctrine ne fixe pas de longueur par banque ;
  - le mode d'une banque désigne la disposition qui porte ses intervalles
    (clé `mode` des dispositions B-H, `config/default.yaml`, un seul hub) ;
  - GROUP A-H = banque : départ des dispositions sur la tonique dans
    l'octave de C5 (la# → A#5, note 70), chromatique avec la gamme de la
    banque (hors gamme en blanc, avant les rôles : la tierce majeure d'un
    mode mineur est blanche), phrase de la banque au compteur (en live, la
    config jusqu'à la slice 6) ; GROUP d'une banque absente : `pas de
    banque G`, sans changement ; LED GROUP en design = banques du projet à
    la couleur de la famille de leur mode × `dim`, la choisie en **blanc
    plein** (`leds.bank`, revu le 2026-11-09 : la choisie en couleur pleine
    se distinguait mal), quel que soit le transport (le compteur reste à
    l'écran) ;
  - **disposition calée sur le mode de la banque** (demandé le
    2026-11-09) : chaque changement de banque du design (GROUP, PC d'une
    autre banque, premier passage) choisit la disposition de son mode
    (éolien → Aeolian, chromatique → Chroma) ; PAD MODE ou le menu GAMME la
    surchargent jusqu'au prochain changement de banque ; un PC de la banque
    déjà choisie garde la surcharge ;
  - premier passage en design : banque du dernier PC reçu si le projet
    l'a, sinon la première ; gardée ensuite d'un passage à l'autre ;
  - **menu réduit** (décidé le 2026-11-09) : boutons d'écran 1-4 =
    GAMME (disposition), TRACK, QUANT, PHRASE ; BANK retirée à l'essai
    des écrans (GROUP la choisit, l'écran droit l'affiche) ; SLOTS, CANAL
    et MON reportés tant que leur rôle n'est pas précisé. **Réglage
    direct** (demandé le 2026-11-10, à l'essai de la slice 8) : une entrée
    a toujours le focus, GAMME au départ ; l'encodeur maître règle sa
    valeur, appliquée à chaque cran, en boucle ; son appui
    passe le focus à l'entrée suivante (GAMME → TRACK → QUANT → PHRASE,
    en boucle) ; un bouton d'écran 1-4 donne le focus à son entrée, 5-8
    sans effet ; NOTE REPEAT garde la priorité sur les boutons d'écran ;
  - **gammes exotiques** (ajoutées le 2026-11-10) : après les 7
    dispositions B-H, GAMME propose Locrian, Hung. min, Dbl harm., Blues,
    Hirajoshi, In-sen, Pelog, Whole tone ; sans groupe ni mode de banque
    (aucune banque ne les choisit), calées sur la tonique de la banque
    courante ; la session garde la disposition par son nom (les sessions
    d'avant, par sa lettre de groupe, restent relues) ;
  - provisoire jusqu'à l'essai sur la MK2 : disposition des écrans (cf.
    Écrans, design).

## Projets : de la doctrine au fichier projet

### Où vit chaque donnée (un hub par donnée)

| Donnée | Hub | Exemple |
|---|---|---|
| Samples par banque et track | `library/lives/<set>.json` | `items[].bank`, `items[].track`, `items[].name` |
| Fiche de chaque banque : titre, description, tempo, tonique, mode ; et ce que mk-brain ajoute pour jouer : longueur de phrase, paliers de tempo, longueur des patterns | front matter `mkbrain:` de la doctrine du set (`digitakt/doctrine-dt2-<set>.md`) | `E-TRIBE: {title: Tribe, tempo: 162, tonique: A#, mode: phrygien, phrase: 64}` |
| Matériel, dispositions de pads, page d'encodeurs (CC) | `mk-brain/config/default.yaml` | `encodeurs: [{nom: CUT, cc: 74}, …]` |
| Projet résolu, prêt à jouer | `mk-brain/projects/<set>.yaml` (généré par `convert` depuis la slice 6.A, jamais édité à la main) | tout ce qui précède, aplati par banque |

### Formalisme du front matter (validé ; posé dans la doctrine solaris à la 6.A)

```yaml
---
mkbrain:
  live: library/lives/solaris.json   # samples par banque et track
  auto_channel: 16
  defaults: {phrase: 32, quantize: "1/16", swing: 50}
  banks:
    A-HALF:
      title: Half-time
      desc: Ouverture lourde et lente, drone puis beat half-time
      tempo: 160
      tonique: F
      mode: eolien
      intro: 16
    C-GROOVE:
      title: Groove tribe
      desc: Kick glissant la#, stab à la tierce, charley
      tempo: 143
      tonique: A#
      mode: eolien
      quantize: "1/8"
      paliers: {de: 143, a: 152, pas: 2, toutes: 32}
    E-TRIBE:
      title: Tribe
      desc: Cœur du set, rumble, couleur phrygienne
      tempo: 162
      tonique: A#
      mode: phrygien
      phrase: 64
    # … B-DNB, D-ACID, F-MENTAL, G-JOKER sur le même modèle
  patterns:                          # facultatif, longueur si ≠ 64 pas
    E-TRIBE: {13: 32, 14: 16}
---
```

- **Fiche de banque obligatoire** : `title`, `desc`, `tempo`, `tonique`,
  `mode`. `title` et `desc` s'affichent au premier Program Change de la
  banque (écran droit, 2 s) et dans le menu design.
- **Modes acceptés** : `eolien`, `phrygien`, `dorien`, `mineur-harmonique`,
  `phrygien-dominant`, `penta-mineure`, `chromatique` (les 7 gammes des
  groupes B-H de `DT2 Pads`).
- **Recoupement avec le JSON** : `solaris.json` porte aussi `keys` et
  `tempos`. Pour mk-brain, le front matter fait foi ; `convert` lève
  `ProjectError` si les deux divergent, pour que les deux sources ne
  dérivent pas en silence (décidé le 2026-11-09).
- **Déduit, jamais saisi** : notes de la gamme, rôle de chaque note
  (tonique, tierce, quinte, autre degré, hors gamme), couleurs des pads.
- **Paliers de tempo** (groove et acid) : rappel à l'écran
  `palier 147 dans 3 mes`. Le Pi ne change pas le tempo, la DT2 mène.
- `mk-brain convert digitakt/doctrine-dt2-solaris.md` lit le front matter
  et le JSON, valide (banque inconnue, tonalité illisible, clé inconnue →
  exception typée `ProjectError` avec la ligne fautive), écrit
  `projects/solaris.yaml`. Le commit est fait à la main, avec le reste.

**Découpage de la slice 6 (décidé le 2026-11-09)** :
- **6.A** front matter `mkbrain:` dans la doctrine solaris, `convert`,
  `projects/solaris.yaml` généré ;
- **6.B** contexte live suivi par Program Change : banque du projet, donc
  gamme, tonique et phrase ; titre et description 2 s ; tonique et vraie
  note sur l'écran play ;
- **6.C** écran de sélection de projet (encodeur maître, dernier joué
  présélectionné, SHIFT + BROWSE), noms de samples à la frappe depuis le
  JSON.

**Fait le 2026-11-09 (slice 6.A, `convert.py`)** :
- front matter posé en tête de `digitakt/doctrine-dt2-solaris.md`, banques
  A-G ; seules les clés que mk-brain emploie déjà y figurent (`live`,
  `defaults.phrase`, fiche de banque, `phrase` par banque) ; `auto_channel`,
  `quantize`, `swing`, `intro`, `paliers` et `patterns` viendront avec
  leur usage (pas de pré-construction), une clé inconnue est refusée ;
- **G-JOKER** (tranché le 2026-11-09) : `chromatique` sur A#, 165 BPM
  (milieu de la plage 160-168, celui du `0-KIT`). Le JSON n'a ni tonalité
  ni tempo pour G : rien à recouper ;
- `live` est relatif à la racine du vault (parent de `digitakt/`) ; le nom
  du projet est le `name` du JSON ;
- recoupement : chaque banque du front matter existe dans `banks` du JSON ;
  chaque `keys` du JSON a sa fiche, même tonique (bémols normalisés,
  `Bb` = `A#`) et même mode (`m` = `eolien`, `phrg` = `phrygien`, une
  autre abréviation est refusée) ; chaque `tempos` d'une banque du projet
  est égal (le `0-KIT` est ignoré). Erreur = `ProjectError` avec
  `doctrine:ligne` de la banque ;
- sortie rejouable (même texte à source égale), en-tête « GÉNÉRÉ » ;
  `tests/test_convert.py` échoue si `projects/solaris.yaml` est périmé
  (sauté sans le vault, sur le Pi).

**Fait le 2026-11-09 (slice 6.B)**, provisoire jusqu'à l'essai sur la MK2 :
- en live, la banque du **dernier PC reçu** règle le contexte (`Engine.context`) ;
  PATTERN + GROUP choisit seulement la banque de PATTERN + pad. Banque
  absente du projet (H) : phrase de la config, pas de tonique ;
- sa longueur de phrase s'applique **avec la remise à 1**, à la barre
  suivante (transport arrêté : tout de suite) ; le mode design garde la
  sienne (banque choisie par GROUP, menu PHRASE) et ignore le PC ;
- **annonce** au changement de banque (premier PC d'une autre banque, pas
  d'un autre pattern de la même) : clé et titre en gras, description sur
  deux lignes, 2 s à la place du bandeau droit ; le compte à rebours
  garde la priorité. Accents retirés (`Cœur` → `Coeur`, police sans
  accents) ;
- **tonique et mode** en haut à droite du bandeau droit live
  (`Bb Phrygian`), phrase et cap dessous (`ph 2  -6 to 32`) ;
- console de `mk-brain play` : banque, tonique et mode devant chaque note
  (`E-TRIBE A# Phrygian : pad 3 -> b2 (B5, 71)`) ; en design, la
  disposition part de la tonique (5.D), le nom MIDI est donc la vraie
  note ; en live (rythmique), la track.

**Fait le 2026-11-09 (slice 6.C, `selection.py`)**, provisoire jusqu'à
l'essai sur la MK2 :
- `mk-brain play` sans `--project` ouvre la sélection au démarrage ;
  `--project <fichier>` charge directement (essais) ;
- liste de `projects/*.yaml` par nom : nom, date du dernier commit (`git
  log`, sinon date de modification), nombre de banques ; un fichier
  invalide reste listé, marqué `!`, son erreur à droite, et ne se charge
  pas ;
- dernier projet chargé retenu dans `mk-brain/state/last_project` (local,
  ignoré par git) et présélectionné ;
- écrans : liste à gauche (choisi en gros, inversé, 3 lignes visibles),
  projet choisi et gestes à droite ; les deux écrans entiers ;
- SHIFT + BROWSE (l'une ou l'autre flèche) ouvre ou referme sans charger ;
  ouverture refusée en live transport lancé, permise en design ; un Start
  en live referme la sélection sur le projet en cours. Les pads restent
  jouables pendant la sélection ;
- chargement : banque du design à rechoisir (la DT2 d'abord, cf. 5.D),
  contexte live repris du dernier PC reçu, mode inchangé ;
- **noms de samples à la frappe reportés** (décidé le 2026-11-09) : le
  lives JSON ne dit pas quel sample est sur quelle track hors `0-KIT`, et
  le sample d'une track change d'un pattern à l'autre (cf. Questions
  ouvertes) ; le mode de démarrage est réglé par la config (`play.mode`),
  pas par projet.

**Session : derniers réglages (demandé et fait le 2026-11-09)** :
- par projet, dans `mk-brain/state/session-<projet>.json` (local, ignoré
  par git) : banque du design, disposition, octave, banque de PATTERN +
  pad, dernier PC reçu (pattern et banque live), track sélectionnée, page
  et valeurs des faders, mutes ;
- sauvée au plus toutes les 2 s si elle a changé, et à l'arrêt (Ctrl-C) :
  une coupure du Pi perd au plus 2 s ; écriture atomique ;
- reprise au chargement du projet (`--project` ou sélection), **sans rien
  envoyer à la DT2** : faders hors prise (pointillé), mutes à l'affichage
  seulement (décidé le 2026-11-09 : la DT2 a pu changer entre-temps) ; un
  PC déjà reçu de la DT2 l'emporte sur le pattern sauvé ; une banque
  absente du projet ou une octave hors bornes est ignorée ; pitch bend non
  sauvé (ressort) ;
- fichier illisible ou hors bornes : session neuve, sans erreur.

## Comportements

### Horloge et PLL

- 24 ticks par noire, 6 par double-croche, 96 par mesure en 4/4.
- Durée de tick = pente de la régression linéaire sur les 24 derniers
  ticks (affiné le 2026-11-09 à la slice 2 : la moyenne glissante des
  intervalles ne dépend que des deux ticks extrêmes, donc de leur gigue).
  BPM affiché = 60 / (24 × durée de tick), arrondi à 0,1.
- Un envoi prévu au pas k part à l'instant que la droite de régression
  donne pour ce tick, pas au tick reçu : la gigue USB (±1 ms) n'est pas
  recopiée. Cible : erreur sous 0,3 ms. Mesuré sur Mac le 2026-11-09 :
  0,17 ms rms, p99 0,72 ms (cf. Constats horloge).
- Clocks sans Start (la DT2 en envoie à l'arrêt) : BPM affiché, aucune note
  planifiée, compteur de phrases figé.
- Trafic sysex Elektron détecté : avertissement à l'écran (Transfer ouvert).

### Quantize

- Modes : `off`, `1/16`, `1/8`, globaux, réglables à la volée par un bouton.
  Quantize par pad : **à arbitrer** (question ouverte 3).
- « Nearest » : pression dans les 3 premiers ticks après un pas → envoi
  immédiat ; sinon → au pas suivant. En 1/8 : 6 ticks (la moitié du pas).
  L'instant pris en compte est celui de la frappe, pas la fin de la fenêtre
  de vélocité. Retard maximum d'un 16ᵉ = 105 ms à
  143 BPM (60 / 143 / 4 = 0,105 s), d'un demi-16ᵉ en moyenne.
- Swing : décalage des 16ᵉ impairs d'un pourcentage réglable (50-75 %),
  à caler à la main sur celui de la DT2, qui ne le transmet pas.
- En LIVE REC sur la DT2 : couper la quantize du Pi (bouton), pour ne pas
  quantizer deux fois. Indicateur visible à l'écran. **Décidé le
  2026-11-09** : l'enregistrement se quantize par la DT2 ; la quantize du
  Pi sert au jeu live. Pas de mode « strict » (toute frappe au pas
  suivant) : jusqu'à 105 ms de retard au jeu.

### Note repeat

- Pad maintenu + bouton repeat (NOTE REPEAT de la MK2) : répétition à 1/8,
  1/16, 1/32, triolets (1/8T, 1/16T), calée sur la grille d'horloge. Premier
  coup sur la division la plus proche (règle « nearest »), puis un coup par
  division ; durée de chaque coup = moitié de la division. Transport
  arrêté : pas de repeat, le pad joue une fois.
- Vélocité de chaque coup = pression courante du pad (aftertouch MK2).
  Pression vers un CC (filtre) : **à arbitrer** (question ouverte 4).
- Division courante en gros caractères sur l'écran gauche pendant le maintien.

### Pads, dispositions, LED

- Reprise des groupes A-H de `DT2 Pads.ncm2` (table dans
  `digitakt/kb/controleur-maschine.md`) en données YAML :
  - A : notes 0-15 sur l'AUTO CHANNEL = tracks 1-16, pad n = track n (les
    doublons 9-16 du template 7.D sont abandonnés, cf. Pads en live) ;
  - B : chromatique ;
  - C-H : modes à partir de 60.
- Couleurs reprises : tonique rouge, tierce jaune, quinte verte, groupe A
  rouge/bleu ; pad vif à la frappe, atténué au repos. Les LED sont pilotées
  par le Pi, plus besoin de retour MIDI.
- Vélocité : courbe réglable dans la config. Les frappes légères donnaient
  5 à 26 en 7.D.

**Pads en live** (décidé le 2026-11-09 ; remplacé par le mode MPC, slice 8) :

- **Pad seul = jouer**, disposition rythmique : pad n = note n − 1 sur
  l'AUTO CHANNEL = track n, à sa hauteur d'origine, quelle que soit la
  track active (16 pads = 16 tracks). Quantize et note repeat s'appliquent.
- **SELECT + pad = sélectionner la track n** pour les 8 encodeurs (cf.
  Encodeurs). Rien ne sonne. La track sélectionnée est celle du Pi, pas la
  track active de la DT2, que le MIDI ne peut ni lire ni changer.
- **MUTE + pad = mute / démute de la track n** (CC 94 sur son canal).
- **PATTERN + pad = pattern n de la banque courante** : Program Change
  `banque × 16 + (n − 1)` envoyé à la DT2, qui le met en file comme ses
  propres changements.
- LED : pad de la track sélectionnée allumé en permanence (à mi-intensité,
  `leds.selected`, pour que la frappe reste visible en plein), tracks mutées
  éteintes, couleurs par rôle de la grille (doctrine §1).
- **Track 16 et Preset Pool** : le pool se joue depuis les touches `[TRIG]`
  de la DT2, en trig mode Preset Pool. La MK2 ne peut pas choisir un preset
  du pool (vérifié le 2026-11-09, fiche `digitakt/kb/preset-pool.md`).

**Couleurs des pads en mode design** (décidé le 2026-11-09), calculées
depuis la tonique et le mode de la banque :

| Rôle de la note | Chromatique (B) | Gamme (C-H) |
|---|---|---|
| Tonique | rouge | rouge |
| Tierce (mineure ou majeure) | blanc | jaune |
| Quinte | blanc | vert |
| Autres degrés de la gamme | blanc | bleu (une seule famille `gamme`) |
| Hors gamme | éteint au repos, blanc à la frappe | — (absent) |

- **Révisé le 2026-11-09 (après la 5.D)** : en chromatique, seule la
  tonique est en couleur ; la gamme se lit par les pads allumés, le hors
  gamme éteint reste jouable. Distinction mineur / majeur supprimée : elle
  ne disait que la tierce du phrygien dominant, la disposition gamme est
  la même pour tous les modes, seules les notes changent. Piste écartée
  pour l'instant : marquer la note caractéristique du mode (♭2 phrygien,
  6 dorien…).
- Disposition par défaut en design : **chromatique** (16 demi-tons à partir
  de la tonique), pour que les notes hors gamme restent jouables.
  Les dispositions « gamme seule » restent dans le menu.
- Pad frappé : couleur vive ; au repos : atténuée.

**Mode accords (design, piste à explorer)** : un pad = un degré de la gamme
de la banque, qui joue l'accord diatonique (triade, puis 7e en option) bâti
sur ce degré. Couleurs : celle du degré fondamental. **À vérifier
d'abord** : combien de voix une track audio de la DT2 joue à la fois. Si
c'est une seule, il faut répartir l'accord sur plusieurs tracks (Id1 à Id3)
ou passer par une track MIDI. Hors MVP tant que ce point n'est pas tranché.

### Écrans (256 × 64, monochromes) — maquettes à valider

Grille de travail : police 6 × 8, soit 42 colonnes × 8 lignes ; police
double 12 × 16 pour les chiffres clés. **Constaté sur la MK2 le
2026-11-09** : la police bitmap 6 × 8 se lit mal (6 pris pour 8) ; texte
courant en police vectorielle de Pillow, taille 13, 5 lignes de 12,8 px,
gras d'1 px pour les libellés. Les maquettes ci-dessous sont en
caractères, une ligne = 8 pixels.

**Sélection de projet** (au démarrage)
```
mk-brain                   sync ok a1b2c3d
                                          
 > SOLARIS        7 banques   2026-11-08  <- police double sur la ligne active
   DEMO-TRIBE     2 banques   2026-10-30
                                          
 encodeur : choisir · appui : charger     
```

**Live, écran gauche : contexte et phrase**
```
E·TRIBE  A# phrg        162.0 ▶  Q16 SW54
                                          
  27 / 64              PAT E04  2/4       <- chiffres doubles
                                          
[████████|████████|████████|██▒░░░░░░░░░] <- 8 blocs de 8 mesures
 ● ○ ○ ○                     cap 32 : -6  <- temps, mesures avant le cap
```
- 4 dernières mesures d'une phrase : la barre passe en vidéo inverse.
- BPM lu sur la clock, arrondi à 0,1 ; `■` à l'arrêt, `▶` en lecture.

**Live, écran droit : les 8 faders de la track sélectionnée**
```
T07 PERC A  ch7            palier 147 -3
 CUT   RES   ENV   DEC   LVL   PAN   DLY  REV
  87    40    12    64   100    0     0   20
 ▮▮▮▯  ▮▯▯▯  ▯▯▯▯  ▮▮▯▯  ▮▮▮▮  ·▮·   ▯▯▯▯ ▮▯▯▯
```
- Colonne touchée en vidéo inverse ; `~` devant la valeur tant que le
  soft-takeover n'a pas rattrapé la DT2.

**Note jouée et tonique** (demandé le 2026-11-09) : l'écran affiche le
mode, la note jouée avec son degré et son nom (`pad 3 -> b3 (D#5, 63)`,
convention Elektron 60 = C5). Fait à la slice 2, sur l'écran gauche de
`mk-brain play`. Tant qu'aucun projet n'est chargé, le nom suppose la DT2
sans `TUNE` ; avec le projet (slice 6), la tonique s'affiche à côté du
mode et le nom devient la vraie note (tonique + degré) : fait à la 6.B.

**Superpositions temporaires sur l'écran droit**, par ordre de priorité :
1. Note repeat : la division en très gros (`1/16T`) tant que le pad est
   tenu.
2. Compte à rebours `-2`, `-1` en très gros dans les 2 dernières mesures
   avant un cap.
3. Frappe d'un pad : nom du sample, slot, track, pendant 1 s. Les noms
   viennent du projet (samples par banque et track du JSON), la DT2 ne les
   renvoie pas. **Reporté le 2026-11-09** (6.C) : le JSON n'a pas de track
   par banque.

**Fait le 2026-11-09 (slice 5.C, `render.py`), revu à l'essai le même
jour** : chaque valeur s'affiche juste au-dessus de son encodeur. Les deux
écrans ont la même structure, qui remplace les maquettes live ci-dessus :

```
écran gauche                              écran droit
E04 > E06 (gros)       SD/CP T03 (gros)  25 / 32 (gros)       phrase 1
                                                               cap 32 : -8
■ ■ □ ■ ■ ■ ■ ■ ■ ■ □ ■ ■ ■ ■ ·           [████████|████████|████████|██░░]
----------------------------------------  ---------------------------------
CUT [███░] RES [██░░] ENV [██░░] DEC [██░] LVL [██░] PAN [─|─] DLY [██░] REV [██░]
```

- deux tiers supérieurs (40 px) = bandeau ; dessous, 4 colonnes de 64 px
  par écran, encodeurs 1-4 à gauche, 5-8 à droite : nom et jauge sur une
  ligne, sans valeur numérique (inutile, décidé à l'essai) ; jauge en
  pointillé tant qu'elle est hors prise (remplace le `~`) ; le pan depuis le centre
  (`bipolar` dans la page d'encodeurs) ; colonne touchée inversée 1 s ;
- bandeau gauche (revu à l'essai) : en gros, le pattern en cours, suivi
  du prochain (`> E06`) annoncé par la DT2 ou demandé par PATTERN + pad,
  et la track sélectionnée avec son code de la grille (doctrine §1,
  `T03` + `SD/CP` ; `track_names` de `config/default.yaml`, deux codes au
  plus, à remplacer par le projet à la slice 6) ; dessous, 16 cases de mutes (pleine =
  ouverte, vide = mutée, point = track de l'AUTO CHANNEL, track
  sélectionnée soulignée), remplacées 1,5 s par le dernier geste ou par
  une alerte (`pas de clock`, `TRANSFER OUVERT ?`). Ni tempo, ni quantize,
  ni swing : la DT2 affiche le tempo, les LED GRID et SWING disent si
  quantize et swing du Pi sont actifs. Frappe de pad : rien en live (les
  LED suffisent), `pad n vel v` en design ;
- bandeau droit : `mesure / longueur`, phrase, cap ; barre d'une case par
  mesure, séparée tous les 8, inversée dans les 4 dernières mesures ;
  dans les 2 dernières avant un cap, bandeau inversé avec `-2` / `-1` ;
- NOTE REPEAT (tenu, ou pad qui répète) : les 8 divisions remplacent les
  bandeaux, chacune sous son bouton d'écran, la choisie inversée ;
- bascule de mode proposée : écran droit entier ;
- design : cadre autour de l'écran gauche, menu dans les bandeaux depuis
  la 5.D (cf. ci-dessous) ;
- tonique et mode de la banque en live, titre et description 2 s au
  changement de banque : slice 6.B (cf. Projets) ;
- rafraîchi au plus toutes les 50 ms dans la boucle principale, envoyé
  seulement si l'image change ; moins d'1 ms la paire d'écrans sur le
  Mac. Si le Pi est trop lent, passer au fil de rendu dédié (slice 7).

**Fait le 2026-11-09 (slice 5.D), remplace les deux maquettes design
ci-dessous** : les entrées du menu sous leurs boutons d'écran, comme les
divisions du repeat ; faders inchangés.

```
écran gauche (bordé)                          écran droit
[D] Chroma   T03 SD/CP   Q off   32 mes       E-TRIBE 162 (gras)
[██Db6 tierce mineure██████░░░░░░░░░░░]       Bb phrygien · Tribe
                                              6 / 32  cap 16 : -11  [██░░░░]
```

- **textes d'écran en anglais, sans accent** (décidé le 2026-11-09 : la
  police de Pillow n'a pas les accents) : degrés (`minor 3rd`, `2nd, out of
  scale`), gestes (`T03 selected`, `switch cancelled`), alertes (`no
  clock`, `TRANSFER OPEN?`), noms des dispositions (Drums, Chroma, Aeolian,
  Phrygian, Dorian, Harm. min, Phryg. dom, Min. penta), cap noté `-8 to
  32` ; la console et le code restent en français ;
- revu le 2026-11-09 : valeurs seules, sans libellé (`Q` et `bars` gardés,
  `off` et `32` seuls seraient muets) ; plus de `DESIGN` écrit, une icône
  `D` inversée au coin haut gauche (le cadre reste) ;
- entrée ouverte en vidéo inverse, avec la valeur en cours de choix ;
- sous le menu, 1 s après une frappe : la note en bémols, comme la
  doctrine (`Db6`, convention Elektron 60 = C5), et sa place depuis la
  tonique de la banque (`tierce mineure`, `seconde, hors gamme`), sur une
  barre de vélocité, texte inversé sur la partie pleine ; en rythmique,
  la track et son code ; sinon le dernier geste (1,5 s), une alerte ou les
  mutes ;
- écran droit : fiche de la banque (clé, tempo, tonique en bémols, mode,
  titre), `pas de projet` sans projet ; **pattern en cours en gros en haut
  à droite** (`E04`, demandé le 2026-11-09), la fiche rétrécit sa police
  pour lui laisser la place ; phrase en petit, sans compte à rebours en
  gros ;
- noms courts des dispositions pour tenir sous un bouton (Chroma, Min.
  harm., Penta min.).

**Design, écran gauche : ce qui part vers la DT2** (maquette d'origine)
```
╔DESIGN═ E-TRIBE ═ T10 acid ═ ch11 ═══════╗
║ pad 6 -> A#3 (70) vel 96   Grp H penta  ║
║ MIDI > CC74=87 ch11                     ║
║ clock 162.0 ■   Q off   mes 3 / 4       ║
╚═════════════════════════════════════════╝
```
- Le cadre et le bandeau `DESIGN` ne disparaissent jamais : un coup d'œil
  suffit à savoir dans quel mode on est.

**Design, écran droit : menu ou page de paramètres** (maquette d'origine)
```
 BANK  TRACK GAMME SLOTS QUANT PHRASE CANAL MON
  E     10   penta 33-48  off   32    11    ·
 [sous-page de l'entrée choisie, ou les 8 paramètres de la track]
```
- Les 8 boutons au-dessus des écrans choisissent l'entrée, l'encodeur
  maître règle la valeur, un appui valide.

- Format supposé (chat de cadrage) : 8 pages de 256 octets par écran, un
  octet = 8 pixels verticaux, environ 2 ko par écran envoyés en rapports HID
  d'environ 250 octets avec en-tête. **À vérifier contre cabl / maschine.rs
  en phase 0.**

### Encodeurs → DT2

**Deux pages, les mêmes pour toutes les tracks** (décidé le 2026-11-09,
remplace la page unique CUT RES ENV DEC LVL PAN DLY REV), définies dans
`config/default.yaml`, choisies par les flèches à côté des écrans, en
live comme en design. Numéros de l'annexe B du manuel DT2
(`refs/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf`, B.1-B.7). **Ordre
revu le 2026-11-09** (demande utilisateur), TYPE retiré :

| Page | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| p1 | LVL 95 (niveau de track) | CUT 74 | RES 75 | ENV 77 | OVER 57 (overdrive) | DEL 84 (envoi delay) | REV 85 | SRR 55 |
| p2 | LVL 95 | MW 1 (mod wheel) | BC 2 (breath) | PB (pitch bend) | BR 54 (bit reduction) | CHO 12 (chorus) | TUNE 16 | PAN 90 |

- **Flèches** (2026-11-09) : `BROWSE_RIGHT` = page suivante,
  `BROWSE_LEFT` = précédente, **en boucle** ; LED des
  deux flèches atténuées, pleine pendant l'appui ; `page 2/2` dans le
  bandeau.
- Page des niveaux des 16 tracks : faite puis retirée le 2026-11-09 (pas retenue).

- TYPE (CC 76, knob G du filtre) retiré des pages le 2026-11-09 : le type
  sur la machine MULTI-MODE seulement, un autre paramètre ailleurs.
- MW, BC et PB n'agissent que si le preset leur assigne jusqu'à 4
  paramètres (menus MODULATION WHEEL, BREATH CTRL, PITCH BEND du preset,
  manuel p. 39). PB part en message pitch bend (0-127 → -8192..8191,
  64 = centre). **PB seulement avec SHIFT tenu** (décidé le 2026-11-09) :
  sans SHIFT, l'encodeur ne fait rien (`PB: hold SHIFT`) ; au relâché de
  SHIFT, pitch bend remis au centre sur le canal où il est parti, comme
  une molette à ressort.
- Jauge depuis le centre : PB, ENV, PAN, TUNE (`bipolar`). Valeurs gardées
  par track et par paramètre, quelle que soit la page ; un CC reçu de la
  DT2 est appris même si sa page n'est pas affichée.

- **Live** : CC sur le canal de la track sélectionnée (SELECT + pad),
  `TRACK n CHANNEL` = n. Une track répond sur son canal (vérifié le
  2026-11-09).
- **Design** : CC sur l'AUTO CHANNEL, donc vers la track active de la DT2 ;
  enregistrés en p-locks en LIVE REC (vérifié le 2026-11-09).
- **Valeurs connues, pas de vrai soft-takeover** (décidé le 2026-11-09,
  slice 5.A) : les encodeurs de la MK2 sont relatifs et la DT2 ne dit rien
  au changement de pattern, un rattrapage n'a donc rien à rattraper. Le Pi
  part de la dernière valeur connue, par track et par paramètre (64 si
  jamais vue). Il **écoute la DT2** : `ENCODER DEST` et `MUTE DEST` =
  `INT + EXT`, les boutons et mutes joués sur la machine mettent à jour
  ses valeurs. Une rotation de la MK2 = un CC, sans attente.
- **Constaté le 2026-11-09** : la DT2 envoie ses boutons sur l'AUTO
  CHANNEL (16), pas sur le canal de la track, et ne dit pas quelle track
  est active. Un CC reçu sur l'AUTO CHANNEL met donc à jour la track
  sélectionnée sur la MK2 (décidé : on tourne sur la DT2 la track
  sélectionnée sur la MK2). Un mute reçu sur ce canal est ignoré.
  **Remplacé le 2026-11-09** : c'était le réglage `OUTPUT CH` = AUTO CH
  de la DT2 (PORT CONFIG, manuel §14.4.2). Avec `OUTPUT CH` = TRACK CH,
  ses boutons sortent sur le canal de la track active (vérifié à l'écoute
  MIDI brute : tracks 4, 5, 6 sur leurs canaux, la 16 sur le canal 16) ;
  le Pi **sélectionne cette track sur la MK2** au premier bouton tourné
  (`T04 selected (DT2)`). [TRK] + trig seul n'envoie rien : la synchro
  attend un bouton. Vérifié aussi avec `TRIG KEY DEST` = `INT + EXT` :
  ni [TRK] + trig ni un trig seul n'envoient de message (écoute MIDI
  brute, 2026-11-09) ; pas d'autre moyen de connaître la track active. Un CC sur l'AUTO CHANNEL vient alors de la track 16 :
  suivie en design, valeur seulement apprise en live (la track 16 n'y est
  pas joignable). Les mutes ne changent pas la sélection.
  `midi.knobs_on_track_channel: false` rend l'ancien comportement.
- Mutes : la DT2 ne donne pas leur état, elle n'envoie que leurs
  changements. Au lancement, toutes les tracks sont supposées ouvertes
  jusqu'au premier mute joué (limite assumée, 2026-11-09).
- **Constaté le 2026-11-09** (écoute MIDI brute, mutes joués sur la DT2,
  `MUTE DEST` = `INT + EXT`) : la DT2 envoie un CC 94 **sur le canal de la
  track**, valeur **1 = muté, 0 = ouvert** (pas 127). Le Pi lisait
  « muté » à partir de 64 et ne voyait donc aucun mute : il lit désormais
  toute valeur non nulle comme muté. MUTE + pad envoie 127 pour muter et 0
  pour ouvrir (vérifié). Une première lecture inversée (0 = muté, erreur
  de manip) a été corrigée le même jour, après l'essai.
- PATTERN + pad : banque choisie par PATTERN + GROUP A-H (sans envoi,
  décidé le 2026-11-09) ou apprise du dernier PC reçu ; avant, `banque ?`.
  Le PC au Stop relevé en 7.E ne s'est pas reproduit : sur une quinzaine
  de Stop, aucun PC sans changement de pattern (à confirmer).
- Un changement de pattern (PC d'un autre pattern) recharge le kit de la
  DT2 : toutes les valeurs passent « hors prise », jauge en pointillé
  (c'était un `~` devant la valeur avant la 5.C). La première rotation
  repart de la dernière valeur connue (saut possible, assumé) et rend la
  jauge pleine.
- Rotation : 4 unités brutes de la MK2 par cran de CC
  (`encoders.raw_per_step`), restes cumulés.

### Affectation des contrôles

> **Jusqu'à la slice 6.** Depuis la slice 8 : une seule colonne, cf.
> « Mode unique et pads MPC » (PAD MODE = MPC ↔ clavier, GROUP = banque,
> PATTERN + pad partout, CONTROL non affecté).

Noms de la face avant MK2, tous décodés en HID le 2026-11-09 (slice 0, cf. Constats HID).

| Contrôle | Live | Design |
|---|---|---|
| Pad | joue la track n (rythmique) | joue la disposition choisie (chromatique par défaut) |
| SELECT + pad | sélectionne la track n pour les encodeurs | sélectionne la track n (canal) |
| MUTE + pad | mute / démute la track n | idem |
| PATTERN + pad | pattern n de la banque courante (PC) | sans effet, le pad joue (décidé le 2026-11-09) |
| PATTERN + GROUP n | banque n pour PATTERN + pad (sans envoi) ; GROUP tenus = banque | sans effet (GROUP seul = banque du design) |
| 8 encodeurs | les 8 faders de la track sélectionnée | les 8 faders de la track active (p-locks en LIVE REC) |
| Flèches à côté des écrans (BROWSE ◀ ▶) | page d'encodeurs précédente / suivante, en boucle | idem |
| Flèches de transport (◀ ▶, à côté de RESTART) | sans effet, LED éteintes | octave des pads −1 / +1, ±4 au plus, notes bornées à 0-127, remise à 0 par GROUP ; sans effet en rythmique ; LED pleine du côté décalé, `oct +1` sur l'écran droit (décidé le 2026-11-09) |
| NOTE REPEAT tenu + pad | répétition ; les 8 boutons au-dessus des écrans choisissent la division (1/4, 1/8, 1/8T, 1/16, 1/16T, 1/32, 1/32T, 1/64) | idem |
| SHIFT + NOTE REPEAT | verrouillage du repeat | idem |
| GRID | quantize off → 1/16 → 1/8 | idem (off par défaut) |
| SWING + encodeur maître | swing 50-75 % | idem |
| SHIFT + PLAY | phrase remise à 1 à la prochaine mesure | idem |
| SHIFT + GROUP n | recale le compteur au début du bloc n | idem |
| GROUP A-H | LED du compteur 8 × 8 mesures | banque n : sa tonique, son mode et sa phrase colorent et calent les pads (décidé le 2026-11-09) |
| PAD MODE | — | cycle des dispositions |
| 8 boutons au-dessus des écrans | divisions du repeat (pendant NOTE REPEAT) | 1-4 : GAMME, TRACK, QUANT, PHRASE (5.D) ; divisions pendant NOTE REPEAT |
| Encodeur maître | sans effet (sauf avec SWING) | valeur de l'entrée de menu ; appui = valider |
| SHIFT + CONTROL (1 s) | changer de mode (refusé transport lancé) | changer de mode |
| SHIFT + BROWSE | sélection de projet (refusé transport lancé) | idem |
| Autres (PLAY, REC, ERASE, RESTART, STEP, SAMPLING, ALL, AUTO WRITE, SCENE, NAVIGATE, DUPLICATE, SOLO, TEMPO, VOLUME, flèches du maître) | non affectés, LED éteintes | idem |

- **La DT2 reste maître du transport** : PLAY et REC de la MK2 n'envoient
  ni Start ni Stop.
- **En live, tout geste à risque passe par SHIFT.**
- **Un bouton non affecté a sa LED éteinte.**

### Compteur de phrases

- Mesure courante depuis le Start (96 ticks par mesure), longueur de phrase
  32 ou 64, réglable à l'encodeur ; intro de 16 possible.
- Les 4 dernières mesures d'une phrase en vidéo inverse ; compte à rebours
  `-2`, `-1` sur l'écran droit dans les 2 dernières.
- LED Group A-H : 8 × 8 = 64 mesures, un bouton de plus allumé toutes les
  8 mesures ; la dernière mesure avant un cap (16, 32, 64) clignote au temps.
- Un pad ou un bouton pulse sur le 1 de chaque mesure.
- Remise à zéro :
  - manuelle : SHIFT + PLAY → mesure 1 à la prochaine barre ;
  - automatique : Program Change reçu (DT2 `PRG CH SEND` = on) → mesure 1
    à la frontière suivante. En live, le même PC change aussi la banque
    courante et ses réglages (cf. Modes). Changement de pattern dans la
    même banque (E03 → E04) : remise à zéro aussi (décidé le 2026-11-09).
- Longueur de phrase par banque, lue dans le projet. `intro: 16` = première
  phrase de 16 mesures après le premier PC de la banque.
- Patterns de longueur non puissance de 2 : le compteur dérive, c'est
  assumé ; le bouton manuel corrige.
- **Précisé le 2026-11-09 (slice 4)** :
  - toute remise à zéro (SHIFT + PLAY, SHIFT + GROUP n, PC) s'applique à
    la barre suivante ; SHIFT + GROUP n donne à cette barre le numéro
    (n − 1) × 8 + 1, ignoré au-delà de la longueur de phrase ;
  - mesures avant le cap comptées avec la mesure en cours : `-1` pendant la
    dernière, donc `cap 32 : -6` à la mesure 27 (32 − 27 + 1 = 6) ;
  - PC reçu transport arrêté : ignoré (le Start remet à 1) ; Stop reçu
    avant la barre : la remise en attente est oubliée ;
  - le 1 de chaque mesure pulse sur la LED PLAY (première croche) ;
  - transport lancé, les LED GROUP montrent le compteur ; arrêté, la
    disposition en design, rien en live, où GROUP seul est sans effet
    (slice 5.B, cf. Modes). Longueur de phrase dans `config/default.yaml`
    (`play.phrase`), par banque avec les projets (slice 6), comme `intro`.

## Réglages DT2 requis

Repris de `digitakt/kb/midi-config.md` :

- `USB CONFIG` = USB MIDI. En `USB AUDIO/MIDI`, `INT TO MAIN` = `AUTO`
  coupe la sortie principale et le casque dès que l'hôte ouvre le flux
  audio USB (constaté le 2026-11-09, cf.
  `digitakt/kb/audio-routing-overbridge.md`) ;
- `INPUT FROM` et `OUTPUT TO` = USB ;
- `RECEIVE NOTES` et `RECEIVE CC/NRPN` = on ;
- `CLOCK SEND` et `TRANSPORT SEND` = on ;
- `PRG CH SEND` = on (suivi de contexte, reset du compteur) et
  `PRG CH RECEIVE` = on (PATTERN + pad), avec `PROGRAM CHG OUT CH` **et**
  `PROGRAM CHG IN CH` = `midi.program_channel` de `config/default.yaml`
  (10). Le canal d'entrée est réglé à part : resté sur `AUTO` (16), la DT2
  ignorait les PC du Pi (constaté le 2026-11-09) ;
- `OUTPUT CH` = TRACK CH : la MK2 suit la track active de la DT2 (2026-11-09) ;
- `ENCODER DEST` et `MUTE DEST` = `INT + EXT` : le Pi apprend les valeurs
  des boutons et les mutes joués sur la DT2 (décidé le 2026-11-09) ;
- `TRACK n CHANNEL` = n pour les 16 tracks (faders et mutes par track) ;
- `AUTO CHANNEL` = 16 (valeur `auto_channel` du projet). La track 16 n'est
  plus joignable par son canal : SELECT + pad 16 et MUTE + pad 16 sont
  désactivés (LED éteinte) ; le pad 16 la joue toujours (note 15) ;
- Transfer fermé.

## Phases

**Spec UX (2026-11-09)** : maquettes des écrans retenues en l'état, à
ajuster à l'usage ; formalisme du front matter validé avec la fiche de
banque (titre, description, tempo, tonique, mode).

Slices 0 à 6 faites le 2026-11-09 ; 8 (mode MPC, mode unique) codée, à essayer, avant la 7 (Pi). L'ordre suit le risque : le HID (phase 0)
conditionne tout le reste.

| Slice | Contenu | Critère de fin | Statut |
|---|---|---|---|
| 0 | **Spike HID sur Mac** : ouvrir la MK2 sans NI, lire pads, boutons, encodeurs ; allumer une LED ; afficher une mire sur chaque écran | une mire nette sur les deux écrans, tous les contrôles décodés et listés | fait 2026-11-09 : mire nette, 48 boutons, 16 pads, 9 encodeurs |
| 1 | **Relais pads → DT2** : dispositions A-H, couleurs, vélocité, sans horloge | la page A joue les tracks 1-16, les groupes changent de gamme, LED justes | fait 2026-11-09 : tracks 1-16 en A, gamme du groupe C jouée sur la track active (9) |
| 2 | **Horloge** : suivi, PLL, BPM, transport, détection Transfer ; banc de mesure de gigue | BPM juste à 0,1 près, gigue d'envoi mesurée et notée | fait 2026-11-09 : BPM à 0,1 près (145, 151), envoi 0,17 ms rms, pas de flam à l'oreille |
| 3 | **Quantize + note repeat + swing** | à 143 BPM, des frappes volontairement décalées tombent sur la grille de la DT2, à l'oreille et à l'enregistrement LIVE | fait 2026-11-09 : frappes avant le pas posées sur la grille ; frappes après le pas envoyées tout de suite (règle « nearest »), donc à quantizer par la DT2 en LIVE REC (critère précisé le 2026-11-09) |
| 4 | **Compteur de phrases** : mesure, phrase, LED Group, resets manuel et PC | compteur juste sur un set de 64 mesures avec deux changements de pattern | fait 2026-11-09 : PC C02 et C16 remettent à 1 sur la mesure du nouveau pattern, recalages manuels justes, LED GROUP et PLAY conformes |
| 5 | **Écrans, encodeurs, modes** : pages live et design, superpositions, CC, soft-takeover, bascule de mode verrouillée | lisible dans le noir d'un coup d'œil ; aucun saut de valeur à la reprise ; impossible de quitter le live par erreur transport lancé | en cours, découpée le 2026-11-09 : 5.A encodeurs, SELECT / MUTE / PATTERN + pad, faite et essayée sur la DT2 le 2026-11-09 ; 5.B modes et bascule, faite et essayée sur la MK2 le 2026-11-09 ; 5.C écrans live et superpositions, faite le 2026-11-09 et revue à l'essai ; 5.D design (banques solaris, GROUP = banque, menu à 4 entrées), faite et essayée sur la MK2 le 2026-11-09, octave aux flèches de transport (±4) essayée |
| 6 | **Projets** : front matter `mkbrain:` dans la doctrine solaris, `convert`, `projects/solaris.yaml`, écran de sélection, contexte suivi par Program Change | changer de pattern sur la DT2 change banque, gamme et phrase sur la MK2 | **faite, close le 2026-11-09** : 6.A front matter et `convert` ; 6.B contexte suivi par PC ; 6.C sélection de projet ; en plus, à l'essai : session par projet, mutes DT2 (1 = muté), design qui suit la banque de la DT2 et cale la disposition sur son mode, pattern en gros, GROUP choisi en blanc, pages d'encodeurs réordonnées et flèches en boucle. Noms de samples reportés (question 15). Reste à essayer : sélection de projet et reprise de session |
| 7 | **Portage Pi** (Pi 3 Model B, question 5) : image Bookworm Lite 64 bits, udev (hidraw), clone partiel + clé de déploiement, `git pull` au démarrage, service systemd, alimentation, arrêt propre, retour au commit précédent si échec | débrancher le Mac, allumer le Pi : projet présélectionné, jouable en moins de 30 s, sans réseau | à venir, après la 8 |
| 8 | **Mode MPC et mode unique** : table `mpc` (kit en tranches sur T1, T3-T6), PAD MODE = MPC ↔ clavier, fusion live / design, une quantize, banque courante unique | cf. « Mode unique et pads MPC », critère de fin ; préalable : sonde LIVE REC (`scripts/dt2_mpc_probe.py`) | codée le 2026-11-09 (v0.21.0), à essayer sur la MK2 ; sonde LIVE REC à passer sur la DT2 |

Chaque slice livrée produit une entrée de `CHANGELOG.md` balisée `[N]` et
une version mineure dans `pyproject.toml`. Les deux fichiers sont créés à
la slice 0.

## Questions ouvertes

1. ~~Pilotes NI sur le Mac~~ : **tranché le 2026-11-09** (slice 0). hidapi
   ouvre la MK2 alors que NIHardwareAgent et NIHostIntegrationAgent
   tournent ; aucune autorisation macOS demandée. Seul prérequis constaté :
   la brancher en direct sur le Mac, pas sur un hub USB 2.0 non alimenté
   (elle n'y apparaît même pas en USB).
2. ~~« CC slot + note »~~ : **tranché le 2026-11-09**. L'annexe B donne
   CC 19 (slot) et CC 24 (banque de samples), mais le Preset Pool ne se
   pilote pas en MIDI (vérifié) et la track 16 garde son pool joué depuis
   la DT2. Pas de changement de sample par la MK2 dans le MVP.
3. **Quantize par pad** ou seulement globale ?
4. **Pression en note repeat** : vélocité seule, ou aussi un CC (filtre) ?
5. ~~**Modèle de Pi**~~ : **Raspberry Pi 3 Model B Rev 1.2**, retenu le
   2026-11-10 (déjà en main ; Pi 4 ou 5 envisagés avant). Trouvé sur le
   réseau en `pi@10.20.20.56` (clé SSH du Mac acceptée), sous Raspbian 8
   Jessie (Python 3.4) : à reflasher en Raspberry Pi OS Bookworm Lite
   64 bits à l'ouverture de la slice 7. Restent à vérifier sur ce Pi : la
   MK2 sur l'alimentation par bus (USB 2.0 partagé avec l'Ethernet, sinon
   hub alimenté), le rendu des deux écrans et la gigue d'horloge
   (`mk-brain clock --bench-note`).
6. **Latence de bout en bout** pad → son : budget visé sous 5 ms hors
   quantize. À mesurer en phase 2.
7. ~~Numérotation des Program Change~~ : **vérifiée le 2026-11-09**
   (fiche `digitakt/kb/midi-config.md`). PC = banque × 16 + (pattern − 1),
   sur un seul canal. Transport lancé, le PC arrive 10 clocks avant la
   mesure du nouveau pattern : le Pi bascule le contexte et remet la phrase
   à 1 sur la mesure suivante, pas à la réception. Le PC qui accompagne un
   Stop ne change pas le contexte.
8. ~~CC reçus en LIVE REC~~ : **vérifié le 2026-11-09** (fiche
   `digitakt/kb/cc-nrpn.md`). La DT2 les enregistre en p-locks, un par pas,
   qu'ils arrivent sur l'AUTO CHANNEL ou sur le canal de la track. En mode
   design, les encodeurs envoient donc sur l'AUTO CHANNEL, et la track
   active est visée sans régler de canal. Reste à préciser : un pas sans
   trig reçoit-il un p-lock ?
9. ~~SHIFT + CONTROL~~ : **tranché le 2026-11-09** (slice 0). En HID brut,
   la combinaison remonte au Pi (SHIFT on, CONTROL on/off, SHIFT off) et la
   MK2 ne bascule pas en mode MIDI : la bascule de mode est conservée.
10. **Polyphonie d'une track audio DT2** : conditionne le mode accords.
11. ~~AUTO CHANNEL et canaux de track~~ : **vérifié le 2026-11-09** (fiche
    `digitakt/kb/midi-config.md`). Sur un canal partagé, l'AUTO CHANNEL
    l'emporte : notes et CC vont à la track active, la track de ce canal
    n'est plus joignable. AUTO CHANNEL = 16 (décidé le 2026-11-09) : seule
    la track 16, jouée depuis la DT2, perd ses faders et son mute en live.
13. **Notes 0-15 hors AUTO CHANNEL** : à l'essai de la slice 1, AUTO
    CHANNEL resté à 10, le groupe A (notes 0-15 sur le canal 16) a semblé
    jouer les tracks 1-16, alors que les notes 60+ allaient à la track 16.
    Les notes 0-15 déclenchent-elles les tracks sur n'importe quel canal de
    track ? À réécouter, sans enjeu tant que l'AUTO CHANNEL est à 16.
12. ~~Canal 16 au test du pool~~ : la track 16 répond bien sur le canal 16
    (vérifié le 2026-11-09).
14. **Luminosité des écrans** : la commande n'est pas connue (cabl :
    `//!\todo set backlight`). Écarté le 2026-11-09 : octets libres des
    rapports LED (`0x82`[31], `0x81`[56]) sans effet ; aucun feature report
    ne change quand on règle Display dans Maschine 2 ; le réglage n'est pas
    gardé par la MK2 à la réouverture. Pas de capture USB sur Mac Apple
    Silicon (SIP), et Maschine ne tourne pas sur le Pi : piste restante,
    capturer sur un PC Windows (Wireshark + USBPcap) en bougeant le
    curseur Display de Maschine 2. Ne pas sonder au hasard les rapports de
    sortie (`0xd0`-`0xdf` ressemblent à la flash : calibration, série).
15. **Noms de samples à la frappe** (reporté le 2026-11-09, 6.C) : le
    lives JSON range les samples par banque sans track (288 sur 304), seuls
    les 16 du `0-KIT` ont une track, et le sample d'une track change d'un
    pattern à l'autre. Il faudrait une table banque × pattern × track →
    sample, tenue dans le JSON ou la doctrine, avant de l'afficher.
16. **Notes et CC sur le canal d'une track non active, en LIVE REC**
    (slice 8) : pour les notes, oui (vérifié le 2026-11-10, sonde
    `dt2_mpc_probe.py channels`, track 9 active : trigs sur T1, T3 et T5,
    rien sur la 9). Pour les CC, reste à vérifier.
17. ~~**Note → tranche** avec `SLICE` = `NOTE`~~ (slice 8) : vérifié le
    2026-11-10 (sonde `dt2_mpc_probe.py slices --channel 5 --base 60`,
    grille de 6 tranches) : 60 joue la tranche 1, 61 la 2… ; au-delà, la
    note reboucle (66 et 67 rejouent les tranches 1 et 2). Le trig
    enregistré porte une NOTE (pas un lock SLICE) et rejoue sa tranche.

## Constats HID (slice 0, 2026-11-09)

Formats de cabl confirmés sur la MK2 (`src/mk_brain/hid_mk2.py` en garde
le détail) :

- **USB** : `17cc:1140`, interface HID 2, page d'usage vendeur `0xff01`.
- **Écrans** : 256 × 64, octets horizontaux, bit fort à gauche, 8 tranches
  `E0|écran` de 256 octets ; pas de séquence d'init, image nette.
- **LED** : rapports 0x80 (pads RGB), 0x81 (groupes RGB + transport),
  0x82 (boutons) ; valeur 255 = pleine luminosité, couleurs justes ;
  balayage une à une : chaque LED de bouton, de groupe et de pad à sa place.
- **Pads** : rapport 0x20 en continu (environ 755 par seconde au repos :
  2266 en 3 s, 2266 / 3 ≈ 755), 16 pressions sur 12 bits, deux relevés
  par rapport. Index 0 = pad 13 (en haut à gauche), index 12 = pad 1.
  Frappe légère vers 240, appuis francs 1000-2500 sur 4095 ; seuil 200.
- **Boutons** : rapport 0x01 envoyé seulement sur changement, 48 boutons
  nommés comme dans cabl, sauf `Main` = appui sur l'encodeur maître, renommé
  `MASTER_PUSH`.
- **Encodeurs** : 8 compteurs absolus sur 10 bits qui bouclent à 1024,
  pas minimal remonté de 4 (zone morte du matériel), jusqu'à 70 par rapport
  en rotation rapide ; maître sur 4 bits, 1 par cran.

## Constat DT2 (slice 1, 2026-11-09)

- L'AUTO CHANNEL de la DT2 était resté à 10 (réglage 7.D) : les notes du
  Pi sur le canal 16 jouaient la track 16 au lieu de la track active.
  Réglé à 16, la gamme joue sur la track active. Premier point à vérifier
  si les pads visent la mauvaise track.

## Constats horloge (slice 2, 2026-11-09, Mac)

`mk-brain clock --bench-note 3` : note de la track 4 envoyée à chaque
noire sur la droite de régression, DT2 à 151 BPM, 2 minutes.

| Mesure | Résultat |
|---|---|
| BPM lu | 145,0 / 145,1 puis 151,0 / 151,1 ; recalé en une seconde après un changement |
| Arrivée des ticks vs prévision | 0,22 à 0,38 ms rms, p99 0,44 ms ; rares pics isolés (max 12,8 ms, un tick) |
| Envoi vs cible | moyenne +0,13 ms, 0,17 ms rms, p99 0,72 ms, max 1,47 ms, 464 envois, aucun abandon |
| Durée de `send()` vers la DT2 | 0,06 ms en moyenne, p99 0,22 ms |
| Oreille | perc du Pi pile avec le kick de la DT2, pas de flam |

- Premier banc à 1,8 ms rms et +1,3 ms de retard : macOS réveille tard les
  longues attentes (jusqu'à 3,6 ms). Corrigé par des attentes découpées en
  tranches de 2 ms et 2 ms d'attente active avant la cible.
- L'attente active doit céder le GIL (`time.sleep(0)`) : sinon le callback
  MIDI horodate en retard et la gigue d'arrivée triple (0,63 ms rms).
- Cible SPEC (0,3 ms) tenue en rms, pas au p99 (0,72 ms) : sans effet
  audible ; à remesurer sur le Pi (slice 7).

## Constats quantize (slice 3, 2026-11-09)

`mk-brain play` affiche pour chaque frappe sa position et la décision
(`frappe 287.2 -> pas 288 (-15 ms) retardé`).

- Frappes avant le pas (−15 à −44 ms) : retardées, enregistrées sur la
  grille par la DT2.
- Frappes visées « juste avant le temps », écoute au casque de la DT2 :
  mesurées de +12 à +38 ms après le pas, et enregistrées après le temps
  par la DT2 aussi. Le Pi et la DT2 concordent ; le retard est celui du
  jeu, pas de la chaîne.

## Constats compteur de phrases (slice 4, 2026-11-09)

`mk-brain play`, DT2 avec `PRG CH SEND` activé :

| Évènement (position à la réception) | Effet |
|---|---|
| `PC C02` à 8.4.3 | mesure 1 à la barre 9 |
| `PC C16` à 24.4.3 | mesure 1 à la barre 25 |
| SHIFT + GROUP C à 14.1.3 | mesure 17 à la barre 15 |

- Le PC arrive à 8.4.3, soit 756 ticks (7 × 96 + 3 × 24 + 2 × 6) ; la
  barre 9 commence à 768, soit 12 ticks plus tard. La position affichée
  est arrondie au pas : le PC arrive bien autour de 10 clocks avant la
  mesure, comme constaté en 7.E.
- SHIFT + PLAY ne recale que la MK2 : la DT2 reste maître du transport,
  c'est voulu.
- Appuis de recalage souvent frappés sur le 1 (12.1.1, 9.1.3, 6.1.2,
  23.1.1) : appliqués une mesure plus tard. Tolérance sur le premier
  temps proposée, **à trancher**.

## Références

- `cabl` (shaduzlabs, C++) : pilotage HID des contrôleurs NI, Canvas pour
  les écrans MK2.
- `maschine.rs` (Rust) : implémentation HID de la MK2 sous Linux.
- Le format des rapports HID se vérifie sur ces deux sources en phase 0,
  sans se fier au chat de cadrage.
- Manuel Digitakt II OS 1.17 : §10.2.3, §10.2.4, §14.4, §14.8.1, annexe MIDI
  (CC).
- Vault music : `digitakt/kb/controleur-maschine.md`,
  `digitakt/kb/midi-config.md`, `scripts/dt2_midi.py`, `SPEC.md` 7.D et 7.E.
