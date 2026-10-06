---
tags: [digitakt, kb]
theme: Amp, overdrive, bit reduction
lot: 3
ordre: 13
manuel: "§11.7, §11.8 (p56-58)"
os: "1.17"
statut: draft
---

# Amp, overdrive, bit reduction

**En une phrase** : la page AMP donne la forme du son dans le temps
(enveloppe, panoramique, volume lockable), la page FX le salit (overdrive,
bit reduction, sample rate reduction) et règle les envois.

## Gestes rapides

| Page | Accès | Paramètres |
|---|---|---|
| AMP | `[AMP]` | `ATK`, `HOLD`, `DEC`, `SUS`, `REL`, `RSET`, `MODE` (AHD / ADSR), `PAN`, `VOL` |
| FX | `[FX]` | `BR` (16 à 1 bit), `OVER`, `SRR`, `ROUT`, `DEL`, `REV`, `CHR`, `OD.RT` |
| Voir toutes les valeurs | maintenir la touche de page |
| Hasard sur la page | touche de page + `[YES]` (`+ [NO]` pour revenir) |

## Pas à pas : kick court et sale

1. Track 1, `[AMP]` : `MODE` AHD, `ATK` 0, `HOLD` court, `DEC` réglé pour
   que la queue s'arrête avant le kick suivant (à 190 BPM, un temps ≈ 0,32 s).
2. `[FX]` : `OVER` monté jusqu'à l'attaque voulue ; `OD.RT` = PRE pour que
   le filtre arrondisse la saturation, POST pour la garder crue.
3. Rumble (track 2) : `HOLD` = NOTE pour que le `LEN` du trig décide de la
   durée, plus facile à caler entre les kicks.

## En live techno

- Acid / hardcore : `BR` à 8-6 bits et `SRR` sur un hat ou un lead pour le
  grain ; `ROUT` choisit avant / après filtre.
- `VOL` (page AMP) se locke par trig, contrairement au LEVEL de la track :
  accents et ghost notes sans toucher au mixer.
- Envois `DEL` / `REV` par track : la base des transitions (cf.
  [[send-fx-compresseur]]).
- Doctrine §3 : même réglage de kick dans tout le set ; le figer dans le kit
  modèle (cf. [[presets-kits-pool]]).

## Pièges

- `SUS` et `REL` n'existent qu'en ADSR, `HOLD` qu'en AHD.
- `HOLD` fixe (0-126) ignore la fin de note : un `LEN` de trig court ne
  raccourcit pas le son.
- `RSET` off : l'enveloppe ne repart pas à chaque trig (utile pour des
  roulements liés, piège pour un kick).
- La page FX est vide sur les tracks MIDI.

## À essayer (5 min)

Sur le kick, comparer `OD.RT` PRE et POST avec le même `OVER`, puis tester
`BR` à 4 bits sur un hat ouvert et revenir avec `[FX] + [NO]`.

Source : manuel DT2 OS 1.17, §11.7, §11.8, §11.1.
