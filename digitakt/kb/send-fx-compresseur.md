---
tags: [digitakt, kb]
theme: Send FX et compresseur master
lot: 3
ordre: 16
manuel: "§9.8.1, §12.1-12.7 (p37, 61-65)"
os: "1.17"
statut: draft
---

# Send FX (delay, reverb, chorus) et compresseur master

**En une phrase** : un delay, une reverb et un chorus partagés par tout le
pattern (chaque track dose son envoi), plus un compresseur sur la sortie
avec sidechain : la colle et le pompage du set.

## Gestes rapides

| Action | Touches |
|---|---|
| Pages SEND FX (delay, reverb, chorus) | `[FUNC] + [FX]`, `[UP]/[DOWN]` |
| Pages MIXER (compresseur, niveaux de tracks) | `[FUNC] + [MOD]`, `[UP]/[DOWN]` |
| Envois par track | `[FX]` : `DEL`, `REV`, `CHR` |
| Tracks routées au compresseur | `[FUNC] + [FLTR]` > KIT > COMPRESSOR ROUTING |

Delay : `TIME` en 128e de mesure (16 = croche, 12 = double-croche pointée,
32 = noire), `X` ping-pong, `WID`, `FDBK`, `HPF`, `LPF`, `REV` (vers la
reverb). Reverb : `PRE`, `DEC`, `FREQ` / `GAIN` (amorti des aigus), `HPF`,
`LPF`. Compresseur : `THR`, `ATK`, `REL`, `MUP`, `RAT` (1,5 à 20), `SCS`
(source sidechain), `SCF` (filtre sidechain), DRY/WET.

## Pas à pas : pompage sur le kick

1. COMPRESSOR ROUTING : toutes les tracks **sauf** 1 (kick) et 2 (rumble).
2. Page compresseur : `SCS` = TRK1, `SCF` négatif (réagit au grave),
   `RAT` 4, `ATK` rapide, `REL` réglé pour que le niveau remonte juste avant
   le kick suivant.
3. Descendre `THR` jusqu'au pompage voulu, compenser avec `MUP`.
4. DRY/WET sous 127 si le pompage écrase trop (compression parallèle).

## En live techno

- Delay en croche pointée (`TIME` 24) sur le clap, `HPF` haut pour ne pas
  salir le bas : l'espace tribe classique.
- Transition : monter `FDBK` du delay à fond sur la fin d'un pattern, puis
  couper les tracks (cf. lot 4, mutes) : la queue fait le pont.
- Reverb : `HPF` haut pour ne jamais réverbérer le sub (kick, basse).
- Le niveau d'ensemble du pattern (`VOL` du mixer) est sauvé avec le kit :
  équilibrer les patterns entre eux avant le set.

## Pièges

- Les effets sont **par pattern** : changer de pattern peut changer la
  reverb. Garder les mêmes réglages via le kit modèle
  (cf. [[presets-kits-pool]]).
- `FDBK` élevé = signal qui s'emballe et devient très fort.
- Delay et reverb continuent après `[STOP]` ; `[STOP]` deux fois coupe
  presque net.

## À essayer (5 min)

Pompage ci-dessus sur un pattern kick + basse + hats, puis comparer `SCF`
négatif et positif, et noter le `REL` qui sonne le mieux à 190 BPM.

Source : manuel DT2 OS 1.17, §9.8.1, §10.1.2, §12.
