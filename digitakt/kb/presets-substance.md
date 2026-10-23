---
tags: [digitakt, kb]
theme: Presets Substance (Synthackers) pour les tracks 9 et 10
lot: 3
ordre: 37
manuel: "§9 (presets, pool), §14.4 (MIDI, macros)"
os: "1.17"
statut: draft
updated: 2026-10-23
---

# Presets Substance (Synthackers)

**En une phrase** : 64 presets de synthèse pour Digitakt II (32 basses,
32 synthés) qui n'utilisent que les ondes simples et wavetables d'usine,
donc zéro slot de sample par banque, avec deux macros (mod wheel, breath
controller) : la matière des tracks 9 et 10 sans passer par l'enregistrement
d'un synthé (cf. [[oneshots-synthe]]).

Achat du 2026-10-20 (James Orvis, Synthackers, 17 £). Fichiers dans
`digitakt/presets/` (hors git : contenu sous licence, non redistribuable),
zip d'origine dans les téléchargements. Démo d'usage : la fiche tuto
[[tutos/synthackers-techno-session]] (basse « moogy » en fa à 3:26, macros à
30:00 et 36:00) et [[tutos/synthackers-techno-acid]] (preset acid square,
bit reduction et key tracking à 2:58, LFO du preset à 17:41, macros à 28:55).

## Ce que contient un fichier

Un `.dt2pst` est un zip : `manifest.json` (type `Sound`, firmware `1.10`,
tag `BASS` ou `SYNTH`) et un payload binaire de 298 octets au nom du
preset (`JO_SB_…`). Les noms sont tronqués à 12 caractères par la machine
(`MANCHESTE`, `AFTERPART`). Pas de tonalité dans le nom : un preset se joue
dans la gamme par le mode keyboard ou se décline par tonalité (doctrine §9).

## Installation (Transfer)

1. DT2 et Transfer à jour ; le dossier `Factory` du +Drive doit être présent
   (les presets pointent sur ses ondes).
2. Transfer, panneau de gauche : le dossier `Substance Presets` ; panneau de
   droite : la DT2, destination presets du +Drive. Glisser le dossier entier
   (64 d'un coup) ou des presets un par un.
3. Dans un projet : charger les presets voulus dans le Preset Pool
   ([[preset-pool]]), puis sur la track 9 ou 10 ; sauvegarder le kit de la
   banque ([[presets-kits-pool]]).

## Macros

- **Mod wheel** (CC 1) : filtre et timbre, le geste de la basse en live.
- **Breath controller** (CC 2) : tension, risers, montées.

Depuis la machine : page des macros de la track. Depuis le Maschine ou un
autre contrôleur : CC 1 et CC 2 sur le canal de la track
([[cc-nrpn]], [[controleur-maschine]]). Sans contrôleur, revenir à l'état
initial après un geste est lent (constat du tuto, 49:20) : prévoir le
mapping avant de jouer un preset en live.

## Dans la grille

| Tag | Track | Rôle doctrine |
|---|---|---|
| BASS | 9 | basse en contretemps, possède le grave avec le kick et le rumble (§9) ; un preset accordé sur la tonique de la banque |
| SYNTH | 10 | séquence, stabs, lead ; passe-haut au-dessus du sub (§9) ; les plus graves peuvent servir en Id2 (13), les plus brillants en Id3 (14) |

Un preset ne coûte rien en RAM : une banque peut avoir sa basse et son lead
sans toucher au plafond de 127 fichiers (doctrine solaris).

## Catalogue

Colonnes à remplir à l'écoute : caractère, tenue à 170-190 BPM, tonalités
où ça marche, et la croix « retenu » pour le set.

### Basses (32)

| # | Nom | Track | Écoute (à remplir) | Retenu |
|---|---|---|---|---|
| B001 | `REZZ` | 9 | | |
| B002 | `RUBBER` | 9 | | |
| B003 | `FLATULENT` | 9 | | |
| B004 | `SIZZLER` | 9 | | |
| B005 | `TARRED` | 9 | | |
| B006 | `CANNED` | 9 | | |
| B007 | `BITTEN` | 9 | | |
| B008 | `DUALITY` | 9 | | |
| B009 | `BRICKED` | 9 | | |
| B010 | `ORGANDUB` | 9 | | |
| B011 | `RATTLE` | 9 | | |
| B012 | `MOOGY` | 9 | | |
| B013 | `CRACK` | 9 | | |
| B014 | `PULSE` | 9 | | |
| B015 | `BUBBLER` | 9 | | |
| B016 | `RIZZLER` | 9 | | |
| B017 | `BODZINGER` | 9 | | |
| B018 | `SIMPLESUB` | 9 | | |
| B019 | `MOOGSUB` | 9 | | |
| B020 | `FMSUB` | 9 | | |
| B021 | `PWMSQUELC` | 9 | | |
| B022 | `HOODLUM` | 9 | | |
| B023 | `AFTERPART` | 9 | | |
| B024 | `BOOTY` | 9 | | |
| B025 | `COMB` | 9 | | |
| B026 | `PHATTY` | 9 | | |
| B027 | `CHEWY` | 9 | | |
| B028 | `DAZE` | 9 | | |
| B029 | `FLUBBER` | 9 | | |
| B030 | `HOLLOW` | 9 | | |
| B031 | `TRIHARD` | 9 | | |
| B032 | `DUST` | 9 | | |

### Synthés (32)

| # | Nom | Track | Écoute (à remplir) | Retenu |
|---|---|---|---|---|
| B033 | `TRICEP` | 10 | | |
| B034 | `QUADRICEP` | 10 | | |
| B035 | `BUZZED` | 10 | | |
| B036 | `TAPEKEYS` | 10 | | |
| B037 | `SITARI` | 10 | | |
| B038 | `FELINE` | 10 | | |
| B039 | `KUNTALINI` | 10 | | |
| B040 | `FMPLUK` | 10 | | |
| B041 | `BUZZY` | 10 | | |
| B042 | `TRANCEFIZ` | 10 | | |
| B043 | `XFILES` | 10 | | |
| B044 | `PLINK` | 10 | | |
| B045 | `GRISTLE` | 10 | | |
| B046 | `DUTTY` | 10 | | |
| B047 | `KALE` | 10 | | |
| B048 | `CHIMED` | 10 | | |
| B049 | `SPACKEYS` | 10 | | |
| B050 | `POPKORN` | 10 | | |
| B051 | `RACKET` | 10 | | |
| B052 | `LOBSTEP` | 10 | | |
| B053 | `MANCHESTE` | 10 | | |
| B054 | `LIVERPOOL` | 10 | | |
| B055 | `TWANGER` | 10 | | |
| B056 | `GLASSED` | 10 | | |
| B057 | `RASPY` | 10 | | |
| B058 | `DRIFTER` | 10 | | |
| B059 | `FLOCKED` | 10 | | |
| B060 | `BLOCKS` | 10 | | |
| B061 | `EFFEM` | 10 | | |
| B062 | `BROKEN` | 10 | | |
| B063 | `REDUX` | 10 | | |
| B064 | `KOMBAT` | 10 | | |

## Pièges

- Les presets visent la techno à 130-140 : à 180, raccourcir decay et release
  d'abord, sinon la basse bave sur le kick suivant (release au minimum sur
  1, 5, 9, 13, trick 14 de la fiche tuto).
- Pas de 303 dedans : l'acid reste au générateur et aux BL accordées.
- Licence : usage dans ses morceaux et lives, pas de partage des fichiers,
  pas de réemploi dans un autre pack.

## À essayer (5 min)

1. Charger `MOOGY` sur la 9 d'un pattern techno, keyboard en fa, notes
   entre les kicks ; mod wheel pendant 8 mesures.
2. Même pattern à 180 : release à zéro sur 1, 5, 9, 13, comparer avec le
   sidechain du compresseur ([[send-fx-compresseur]]).
3. Passer les 32 synthés en auto-preview sur la 10 et cocher dix
   candidats dans le catalogue, pas plus.
