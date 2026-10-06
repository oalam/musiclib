---
tags: [digitakt, kb]
theme: +Drive, pool, presets et kits
lot: 1
ordre: 2
manuel: "§5, §9.1-9.8 (p16-17, 29-37)"
os: "1.17"
statut: draft
---

# +Drive, pool, presets et kits

**En une phrase** : un **preset** = un sample + les réglages d'une track, un
**kit** = les 16 presets + niveaux, compresseur et send FX ; sauvegarder le
kit modèle permet de l'appliquer d'un coup à tous les patterns vides du set.

## Gestes rapides

| Action | Touches |
|---|---|
| Navigateur de presets | `[FUNC]` + tourner LEVEL/DATA |
| Écouter avant de charger | `[FUNC] + [YES]` (ou `[TRIG]` de la track active) |
| Menu presets / kits | `[PRESET/KIT]` |
| Copier / coller le preset d'une track | `[TRK] + [TRIG] + [RECORD]` puis `[TRK] + [TRIG] + [STOP]` |
| Choisir le sample d'une track | `[SRC]`, tourner DATA ENTRY D |
| Menu SETUP (control all, compresseur, swap) | `[FUNC] + [FLTR]` |

## Pas à pas : le kit modèle du set

1. Sur le pattern modèle, charger un preset par track selon la grille de
   [[../doctrine]] §1 (`[TRK] + [TRIG n]`, puis navigateur, `[YES]`).
2. Régler niveaux, envois, compresseur, LFO de riser sur la track 15.
3. `[PRESET/KIT]` > KIT `SAVE` : slot, nom (ex. `KIT-TRIBE-190`), `[YES]`.
4. Pour tout le set : KIT `MANAGE` > le kit > `[RIGHT]` > **`LOAD TO EMPTY`**
   charge ce kit dans **tous les patterns vides** du projet.
5. Un son retouché à garder : `[PRESET/KIT]` > PRESET `SAVE`, avec tags.

## En live techno

- Kit et pattern ne sont **pas liés** : un kit chargé est une copie dans le
  pattern. Modifier le kick d'un pattern ne touche pas les autres. Pour
  garder le même kick partout (doctrine §3), régler une fois dans le kit
  modèle *avant* `LOAD TO EMPTY`, ou recopier le preset track 1
  (`[TRK] + [TRIG 1] + [RECORD]` / `[STOP]`).
- Le **pool** (128 presets max par projet) sert aux *preset locks* : y
  ajouter les variantes de kick / basse à échanger pas à pas (PRESET
  `MANAGE` > sélection > `[LEFT]` > `ADD TO PRESET POOL`).
- `TRACK SWAP` (`[FUNC] + [FLTR]` > KIT) remet un son sur la bonne track
  sans perdre ses trigs : pratique pour ranger un pattern importé selon la
  grille des 16 tracks.

## Pièges

- `LOAD TO EMPTY` n'agit que sur les patterns **vides** : le faire avant de
  remplir les patterns.
- Un kit ne contient pas les trigs : les trigs FILL / NOT FILL préparés du
  pattern modèle se recopient par copie de pattern (cf. [[copier-coller]]).
- Les presets MIDI ne vont pas dans le pool.
- Samples : 16 bits / 48 kHz, 400 Mo par projet ; supprimer un sample du
  +Drive le retire partout.

## À essayer (5 min)

Sauvegarder le kit du pattern modèle, créer deux patterns vides, `LOAD TO
EMPTY`, puis changer le kick dans un seul des deux : vérifier que l'autre
garde l'original.

Source : manuel DT2 OS 1.17, §5, §9.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=930) : « Presets » (15:30) · DT2, 2024
- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=1442) : « Kits » (24:02) · DT2, 2024
- [Daddy Long Les — Lessons For Complete Beginners 1 : Samples & Presets](https://youtu.be/NSZabPi5qLA?t=1193) : « THE PRESET POOL » (19:53) · DT2, 2025
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=4169) : « Saving presets to the Preset Pool » (1:09:29) · DT2, 2024
- [Synthackers — Comprehensive Guide to Sample Management](https://youtu.be/aTq7VydK8Bk?t=820) : « Transfer - Managing Samples » (13:40) · DT2, 2024
