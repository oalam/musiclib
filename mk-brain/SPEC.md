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

Deux modes : **live** (jouer le set, contexte suivi automatiquement) et
**design** (préparer les patterns : mélodies et mouvements de paramètres
enregistrés en LIVE REC sur la DT2). Aucun écran, clavier, front web ni
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
| Matériel | Raspberry Pi (Linux), prototypage sur Mac | HID et écrans en Python ; MK2 + DT2 disponibles, pas encore de Pi |
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
│   ├── project.py                # modèle Pydantic du projet, chargement, liste
│   ├── modes.py                  # live / design / sélection de projet
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

## Modes : live et design

| | **Live** | **Design** |
|---|---|---|
| Objectif | jouer le set, lire d'un coup d'œil, zéro fausse manœuvre | préparer les patterns sur la DT2 : enregistrer des mélodies et des mouvements de paramètres en LIVE REC |
| Contexte (banque, gamme, phrase) | suit la DT2 : Program Change reçu → banque et pattern → réglages de la banque dans le projet | choisi à la main dans le menu ; Program Change reçu affiché mais sans effet |
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
- **Mode au chargement** : live. Un projet peut en imposer un autre
  (`demarrage: design`, au niveau du projet) pour les séances de
  préparation. La clé `mode` est réservée au mode musical d'une banque.
- Le Pi ne sait pas si la DT2 est en LIVE REC (rien n'est transmis). Le mode
  design le rappelle à l'écran (`DT2 en LIVE REC ?`) au premier mouvement
  d'encodeur.

## Projets : de la doctrine au fichier projet

### Où vit chaque donnée (un hub par donnée)

| Donnée | Hub | Exemple |
|---|---|---|
| Samples par banque et track | `library/lives/<set>.json` | `items[].bank`, `items[].track`, `items[].name` |
| Fiche de chaque banque : titre, description, tempo, tonique, mode ; et ce que mk-brain ajoute pour jouer : longueur de phrase, paliers de tempo, longueur des patterns | front matter `mkbrain:` de la doctrine du set (`digitakt/doctrine-dt2-<set>.md`) | `E-TRIBE: {title: Tribe, tempo: 162, tonique: A#, mode: phrygien, phrase: 64}` |
| Matériel, dispositions de pads, page d'encodeurs (CC) | `mk-brain/config/default.yaml` | `encodeurs: [{nom: CUT, cc: 74}, …]` |
| Projet résolu, prêt à jouer | `mk-brain/projects/<set>.yaml` (généré, jamais édité à la main) | tout ce qui précède, aplati par banque |

### Formalisme du front matter (proposition, à valider)

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

## Comportements

### Horloge et PLL

- 24 ticks par noire, 6 par double-croche, 96 par mesure en 4/4.
- Durée de tick = moyenne glissante des 24 derniers intervalles. BPM
  affiché = 60 / (24 × durée de tick), arrondi à 0,1.
- Un envoi prévu au pas k part à `dernier_tick + n × durée_moyenne` (n =
  ticks restants), pas au tick reçu : la gigue USB (±1 ms) n'est pas
  recopiée. Cible : erreur sous 0,3 ms. **À mesurer.**
- Clocks sans Start (la DT2 en envoie à l'arrêt) : BPM affiché, aucune note
  planifiée, compteur de phrases figé.
- Trafic sysex Elektron détecté : avertissement à l'écran (Transfer ouvert).

### Quantize

- Modes : `off`, `1/16`, `1/8`, globaux, réglables à la volée par un bouton.
  Quantize par pad : **à arbitrer** (question ouverte 3).
- « Nearest » : pression dans les 3 premiers ticks après un pas → envoi
  immédiat ; sinon → au pas suivant. Retard maximum d'un 16ᵉ = 105 ms à
  143 BPM (60 / 143 / 4 = 0,105 s), d'un demi-16ᵉ en moyenne.
- Swing : décalage des 16ᵉ impairs d'un pourcentage réglable (50-75 %),
  à caler à la main sur celui de la DT2, qui ne le transmet pas.
- En LIVE REC sur la DT2 : couper la quantize du Pi (bouton), pour ne pas
  quantizer deux fois. Indicateur visible à l'écran.

### Note repeat

- Pad maintenu + bouton repeat (NOTE REPEAT de la MK2) : répétition à 1/8,
  1/16, 1/32, triolets (1/8T, 1/16T), calée sur la grille d'horloge.
- Vélocité de chaque coup = pression courante du pad (aftertouch MK2).
  Pression vers un CC (filtre) : **à arbitrer** (question ouverte 4).
- Division courante en gros caractères sur l'écran gauche pendant le maintien.

### Pads, dispositions, LED

- Reprise des groupes A-H de `DT2 Pads.ncm2` (table dans
  `digitakt/kb/controleur-maschine.md`) en données YAML :
  - A : notes 0-15 sur l'AUTO CHANNEL = tracks 1-16, pads 9-16 en doublon ;
  - B : chromatique ;
  - C-H : modes à partir de 60.
- Couleurs reprises : tonique rouge, tierce jaune, quinte verte, groupe A
  rouge/bleu ; pad vif à la frappe, atténué au repos. Les LED sont pilotées
  par le Pi, plus besoin de retour MIDI.
- Vélocité : courbe réglable dans la config. Les frappes légères donnaient
  5 à 26 en 7.D.

**Pads en live** (décidé le 2026-11-09) :

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
- LED : pad de la track sélectionnée allumé en permanence, tracks mutées
  éteintes, couleurs par rôle de la grille (doctrine §1).
- **Track 16 et Preset Pool** : le pool se joue depuis les touches `[TRIG]`
  de la DT2, en trig mode Preset Pool. La MK2 ne peut pas choisir un preset
  du pool (vérifié le 2026-11-09, fiche `digitakt/kb/preset-pool.md`).

**Couleurs des pads en mode design** (décidé le 2026-11-09), calculées
depuis la tonique et le mode de la banque :

| Rôle de la note | Couleur |
|---|---|
| Tonique | rouge |
| Tierce (mineure ou majeure) | jaune |
| Quinte | vert |
| Autres degrés de la gamme | couleur de la famille du mode (bleu pour les modes mineurs, violet pour le phrygien dominant) |
| Hors gamme (« interdite ») | blanc |

- Disposition par défaut en design : **chromatique** (16 demi-tons à partir
  de la tonique), pour que les notes hors gamme restent jouables mais
  visibles en blanc. Les dispositions « gamme seule » restent dans le menu.
- Pad frappé : couleur vive ; au repos : atténuée.

**Mode accords (design, piste à explorer)** : un pad = un degré de la gamme
de la banque, qui joue l'accord diatonique (triade, puis 7e en option) bâti
sur ce degré. Couleurs : celle du degré fondamental. **À vérifier
d'abord** : combien de voix une track audio de la DT2 joue à la fois. Si
c'est une seule, il faut répartir l'accord sur plusieurs tracks (Id1 à Id3)
ou passer par une track MIDI. Hors MVP tant que ce point n'est pas tranché.

### Écrans (256 × 64, monochromes) — maquettes à valider

Grille de travail : police 6 × 8, soit 42 colonnes × 8 lignes ; police
double 12 × 16 pour les chiffres clés. Les maquettes ci-dessous sont en
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
 ● ○ ○ ○                     cap 32 : -5  <- temps, mesures avant le cap
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

**Superpositions temporaires sur l'écran droit**, par ordre de priorité :
1. Note repeat : la division en très gros (`1/16T`) tant que le pad est
   tenu.
2. Compte à rebours `-2`, `-1` en très gros dans les 2 dernières mesures
   avant un cap.
3. Frappe d'un pad : nom du sample, slot, track, pendant 1 s. Les noms
   viennent du projet (samples par banque et track du JSON), la DT2 ne les
   renvoie pas.

**Design, écran gauche : ce qui part vers la DT2**
```
╔DESIGN═ E-TRIBE ═ T10 acid ═ ch11 ═══════╗
║ pad 6 -> A#3 (70) vel 96   Grp H penta  ║
║ MIDI > CC74=87 ch11                     ║
║ clock 162.0 ■   Q off   mes 3 / 4       ║
╚═════════════════════════════════════════╝
```
- Le cadre et le bandeau `DESIGN` ne disparaissent jamais : un coup d'œil
  suffit à savoir dans quel mode on est.

**Design, écran droit : menu ou page de paramètres**
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

**Une seule page, la même pour toutes les tracks** (décidé le 2026-11-09),
définie dans `config/default.yaml`. Proposition, à ajuster à l'usage ;
numéros de l'annexe B (fiche `digitakt/kb/cc-nrpn.md`) :

| Encodeur | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Paramètre | fréquence du filtre | résonance | profondeur d'env. filtre | decay d'amp | niveau de track | pan | envoi delay | envoi reverb |
| Abrégé | CUT | RES | ENV | DEC | LVL | PAN | DLY | REV |
| CC | 74 | 75 | 77 | 81 | 95 | 90 | 84 | 85 |

- **Live** : CC sur le canal de la track sélectionnée (SELECT + pad),
  `TRACK n CHANNEL` = n. Une track répond sur son canal (vérifié le
  2026-11-09).
- **Design** : CC sur l'AUTO CHANNEL, donc vers la track active de la DT2 ;
  enregistrés en p-locks en LIVE REC (vérifié le 2026-11-09).
- **Soft-takeover**, par track et par paramètre : la valeur du Pi n'est
  envoyée qu'une fois rattrapée depuis la dernière valeur connue, puisque
  la DT2 ne renvoie rien si on tourne son bouton. `~` devant la valeur tant
  que ce n'est pas rattrapé. Au chargement du projet, aucune valeur n'est
  connue : la première rotation envoie, sans rattrapage.
- Un changement de pattern recharge les réglages de la DT2 : les valeurs
  connues du Pi sont alors marquées « hors prise » pour toutes les tracks.

### Affectation des contrôles

Noms de la face avant MK2, à confirmer au décodage HID (slice 0).

| Contrôle | Live | Design |
|---|---|---|
| Pad | joue la track n (rythmique) | joue la disposition choisie (chromatique par défaut) |
| SELECT + pad | sélectionne la track n pour les encodeurs | sélectionne la track n (canal) |
| MUTE + pad | mute / démute la track n | idem |
| PATTERN + pad | pattern n de la banque courante (PC) | idem |
| 8 encodeurs | les 8 faders de la track sélectionnée | les 8 faders de la track active (p-locks en LIVE REC) |
| NOTE REPEAT tenu + pad | répétition ; les 8 boutons au-dessus des écrans choisissent la division (1/4, 1/8, 1/8T, 1/16, 1/16T, 1/32, 1/32T, 1/64) | idem |
| SHIFT + NOTE REPEAT | verrouillage du repeat | idem |
| GRID | quantize off → 1/16 → 1/8 | idem (off par défaut) |
| SWING + encodeur maître | swing 50-75 % | idem |
| SHIFT + PLAY | phrase remise à 1 à la prochaine mesure | idem |
| SHIFT + GROUP n | recale le compteur au début du bloc n | **à trancher** (GROUP en design : banque ou disposition) |
| GROUP A-H | LED du compteur 8 × 8 mesures | **à trancher** |
| PAD MODE | — | cycle des dispositions |
| 8 boutons au-dessus des écrans | divisions du repeat (pendant NOTE REPEAT) | entrées du menu |
| Encodeur maître | sans effet (sauf avec SWING) | valeur de l'entrée de menu ; appui = valider |
| SHIFT + CONTROL (1 s) | changer de mode (refusé transport lancé) | changer de mode |
| SHIFT + BROWSE | sélection de projet (refusé transport lancé) | idem |
| Autres (PLAY, REC, ERASE, RESTART, STEP, SAMPLING, ALL, AUTO WRITE, SCENE, NAVIGATE, DUPLICATE, SOLO, TEMPO, VOLUME, flèches) | non affectés, LED éteintes | idem |

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
  `PRG CH RECEIVE` = on (PATTERN + pad) ;
- `TRACK n CHANNEL` = n pour les 16 tracks (faders et mutes par track) ;
- `AUTO CHANNEL` = 16 (valeur `auto_channel` du projet). La track 16 n'est
  plus joignable par son canal : SELECT + pad 16 et MUTE + pad 16 sont
  désactivés (LED éteinte) ; le pad 16 la joue toujours (note 15) ;
- Transfer fermé.

## Phases

**Spec UX (2026-11-09)** : maquettes des écrans retenues en l'état, à
ajuster à l'usage ; formalisme du front matter validé avec la fiche de
banque (titre, description, tempo, tonique, mode).

Toutes les slices sont à venir. L'ordre suit le risque : le HID (phase 0)
conditionne tout le reste.

| Slice | Contenu | Critère de fin | Statut |
|---|---|---|---|
| 0 | **Spike HID sur Mac** : ouvrir la MK2 sans NI, lire pads, boutons, encodeurs ; allumer une LED ; afficher une mire sur chaque écran | une mire nette sur les deux écrans, tous les contrôles décodés et listés | à venir |
| 1 | **Relais pads → DT2** : dispositions A-H, couleurs, vélocité, sans horloge | la page A joue les tracks 1-8, les groupes changent de gamme, LED justes | à venir |
| 2 | **Horloge** : suivi, PLL, BPM, transport, détection Transfer ; banc de mesure de gigue | BPM juste à 0,1 près, gigue d'envoi mesurée et notée | à venir |
| 3 | **Quantize + note repeat + swing** | à 143 BPM, des frappes volontairement décalées tombent sur la grille de la DT2, à l'oreille et à l'enregistrement LIVE | à venir |
| 4 | **Compteur de phrases** : mesure, phrase, LED Group, resets manuel et PC | compteur juste sur un set de 64 mesures avec deux changements de pattern | à venir |
| 5 | **Écrans, encodeurs, modes** : pages live et design, superpositions, CC, soft-takeover, bascule de mode verrouillée | lisible dans le noir d'un coup d'œil ; aucun saut de valeur à la reprise ; impossible de quitter le live par erreur transport lancé | à venir |
| 6 | **Projets** : front matter `mkbrain:` dans la doctrine solaris, `convert`, `projects/solaris.yaml`, écran de sélection, contexte suivi par Program Change | changer de pattern sur la DT2 change banque, gamme et phrase sur la MK2 | à venir |
| 7 | **Portage Pi** : image, udev (hidraw), clone partiel + clé de déploiement, `git pull` au démarrage, service systemd, alimentation, arrêt propre, retour au commit précédent si échec | débrancher le Mac, allumer le Pi : projet présélectionné, jouable en moins de 30 s, sans réseau | à venir |

Chaque slice livrée produit une entrée de `CHANGELOG.md` balisée `[N]` et
une version mineure dans `pyproject.toml`. Les deux fichiers sont créés à
la slice 0.

## Questions ouvertes

1. **Pilotes NI sur le Mac** : NIHardwareAgent garde-t-il la MK2 ouverte
   et empêche-t-il hidapi de l'ouvrir ? Faut-il l'arrêter pendant le
   prototypage, et l'autorisation « Surveillance de l'entrée » de macOS
   est-elle requise ? À trancher en phase 0.
2. ~~« CC slot + note »~~ : **tranché le 2026-11-09**. L'annexe B donne
   CC 19 (slot) et CC 24 (banque de samples), mais le Preset Pool ne se
   pilote pas en MIDI (vérifié) et la track 16 garde son pool joué depuis
   la DT2. Pas de changement de sample par la MK2 dans le MVP.
3. **Quantize par pad** ou seulement globale ?
4. **Pression en note repeat** : vélocité seule, ou aussi un CC (filtre) ?
5. **Modèle de Pi** : Pi 4 ou Pi 5. Le Pi Zero 2 W, avec un seul port OTG
   et un hub obligatoire, est déconseillé. Il faut vérifier que la MK2
   tient sur l'alimentation par bus du Pi, sinon prévoir un hub alimenté.
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
9. **SHIFT + CONTROL** : en HID brut, la MK2 remonte-t-elle cette
   combinaison au Pi, ou la garde-t-elle pour sa propre bascule en mode
   MIDI (7.D) ? Sinon, choisir une autre combinaison. À voir en phase 0.
10. **Polyphonie d'une track audio DT2** : conditionne le mode accords.
11. ~~AUTO CHANNEL et canaux de track~~ : **vérifié le 2026-11-09** (fiche
    `digitakt/kb/midi-config.md`). Sur un canal partagé, l'AUTO CHANNEL
    l'emporte : notes et CC vont à la track active, la track de ce canal
    n'est plus joignable. AUTO CHANNEL = 16 (décidé le 2026-11-09) : seule
    la track 16, jouée depuis la DT2, perd ses faders et son mute en live.
12. ~~Canal 16 au test du pool~~ : la track 16 répond bien sur le canal 16
    (vérifié le 2026-11-09).

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
