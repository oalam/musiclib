---
tags: [digitakt, kb]
theme: Preset Pool (cas d'usage)
lot: 3
ordre: 34
manuel: "§8.5.4, §9.1, §9.3.4, §9.8.2, §10.8.2 (p27, 29-31, 38, 48)"
os: "1.17"
statut: draft
---

# Preset Pool : quatre cas d'usage

**En une phrase** : le pool met **plusieurs sons complets sur une seule
track** (preset locks, trig mode Preset Pool), ce n'est pas un rangement ;
le socle n'en a pas besoin, les tracks Id, FX et one-shots si.

Rappel (cf. [[presets-kits-pool]]) : le pool fait partie du projet, 128
presets maximum, et seuls ses presets peuvent être preset lockés.

## Gestes rapides

| Action | Touches |
|---|---|
| Ajouter au pool | `[PRESET/KIT]` > PRESET `MANAGE`, `[YES]` sur chaque preset, `[LEFT]` > `ADD TO PRESET POOL` |
| Gérer le pool (renommer, supprimer, ranger) | `[PRESET/KIT]` > `POOL`, `[RIGHT]` (PRESET OPERATIONS) |
| Placer un son à un slot précis | `POOL`, slot choisi, `[RIGHT]` > `SAVE TO HERE` (son de la track active) |
| Preset lock | maintenir le trig + tourner LEVEL/DATA, choisir, relâcher |
| Voir le preset d'un trig | maintenir le trig |
| Trig mode Preset Pool | `[FUNC] + [UP]` / `[DOWN]` ; slots 17-32 : `[PAGE] + [RIGHT]` |

**Preset lock ou sample lock ?** Le sample lock ne change que le sample et
garde filtre, enveloppes et envois de la track. Le preset lock remplace
**tout le son** : sample, filtre, enveloppes, envois.

## Cas 1 : une track Id qui change de son à chaque pas

But : un seul motif sur la 12 (Id1) qui enchaîne perc sèche, vocal haché et
stab dans le delay, sans prendre d'autre track (doctrine §1 et §12).

1. Track 12 : régler la perc sèche, PRESET `SAVE` (ex. `ID-PERC-SEC`).
   Même chose pour `ID-VOX-CHOP` et `ID-STAB-DLY` (envoi delay à fond).
2. Ajouter les trois au pool.
3. Poser le motif avec la perc comme son de base.
4. Maintenir le pas 7, tourner LEVEL/DATA, choisir `ID-VOX-CHOP`, relâcher.
   Pas 15 : `ID-STAB-DLY`.
5. Une version d'Id = un preset (doctrine §12) : pour faire évoluer l'Id,
   changer les locks, pas le son de base.

## Cas 2 : les variantes d'un même son

But : trois rumbles (sec, saturé, très filtré) sur la track 2, sans
retoucher les réglages à la main.

1. Sauver `RMB-SEC`, `RMB-SAT`, `RMB-FILT` depuis la track 2, puis les
   ajouter au pool.
2. **Par pas** : preset lock `RMB-SAT` sur les trigs de la dernière mesure
   pour faire monter avant la bascule.
3. **D'un pattern à l'autre** : sur le pattern suivant, `POOL` >
   `RMB-FILT` > `LOAD TO TRACK` ; le pattern garde sa copie (charger =
   copier, doctrine §13).
4. Même logique pour deux basses sur la 9 (cf. [[parameter-preset-locks]]).

## Cas 3 : les touches comme pads de one-shots

But : improviser vocals, impacts et cris sur la 14 ou la 15 par-dessus le
pattern.

1. Ranger les one-shots dans les **slots 1-16** du pool : ce sont eux que
   jouent les touches sans changer de page (`SAVE TO HERE` pour fixer
   l'ordre).
2. Track 14 active, `[FUNC] + [DOWN]` jusqu'au trig mode Preset Pool :
   `[TRIG 1]` = slot 1… `[TRIG 16]` = slot 16.
3. Jouer en lecture ; en LIVE REC, les coups sont enregistrés avec leur
   preset lock (cf. [[enregistrement-quantize]]).

## Cas 4 : la palette du set multi-styles

But : avoir les presets fil rouge (FX de transition, perc signature,
texture commune) dans les trois banks dub / DnB / tribe (doctrine §13),
sans repasser par le +Drive.

1. Ajouter ces presets au pool dès la préparation du projet.
2. Dans n'importe quel pattern du projet : preset lock ou `LOAD TO TRACK`.

**Proposition de rangement (à arbitrer dans la doctrine)** : slots 1-16 =
one-shots joués aux touches (cas 3) ; 17-32 = fil rouge (cas 4) ; 33 et
suivants = variantes et Id (cas 1 et 2).

## En live techno

- **Socle (tracks 1, 3-8) : pas de pool.** Chaque son a sa track et ses
  réglages ; le kick ne change pas dans un acte (doctrine §3).
- Pool : tracks Id (12-13), FX (15), one-shots (14), variantes de rumble
  (2) et de basse (9).
- `OCTAVE` (réglages de la track, `[FUNC] + [FLTR]`, manuel §9.8.2) aligne les octaves de
  plusieurs presets pour qu'ils jouent ensemble sans transposer les trigs.

## Pièges

- Pas de preset lock sans pool : un preset du +Drive doit d'abord y être
  ajouté.
- Le pool est **par projet** : un autre projet a son propre pool.
- Les presets MIDI ne vont pas dans le pool ; les trig modes Slices et
  Preset Pool ne marchent que sur les tracks audio.
- Le preset porte le **niveau d'envoi**, pas les réglages du delay ou de la
  reverb, communs au kit : la stab « noyée de delay » sonne avec le delay
  du pattern.
- En STEP RECORDING, en trig mode Preset Pool : `[FUNC]` + `[TRIG]` pour
  poser un trig.
- **À vérifier sur la machine** : si retoucher un preset dans le pool met à
  jour les preset locks qui le désignent ; si la queue du son précédent
  est coupée par un trig preset locké.

## À essayer (5 min)

Track 12, quatre trigs (pas 1, 5, 9, 13), deux presets dans le pool :
preset lock du second sur les pas 5 et 13. Puis trig mode Preset Pool et
jouer les deux presets aux touches 1 et 2 par-dessus.

Source : manuel DT2 OS 1.17, §8.5.4, §9.1, §9.3.4, §9.8.2, §10.8.2.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [Daddy Long Les — Lessons For Complete Beginners 1 : Samples & Presets](https://youtu.be/NSZabPi5qLA?t=1193) : « THE PRESET POOL » (19:53) · DT2, 2025
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=4257) : « Multiple presets on one track » (1:10:57) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=4544) : « Trig mode - Preset Pool » (1:15:44) · DT2, 2024
