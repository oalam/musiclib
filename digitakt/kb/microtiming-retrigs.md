---
tags: [digitakt, kb]
theme: Micro timing et retrigs
lot: 2
ordre: 9
manuel: "§10.4, §10.5, §11.3, §7.3 (p23, 45, 54)"
os: "1.17"
statut: draft
---

# Micro timing et retrigs

**En une phrase** : le micro timing décale un trig avant ou après le pas
(groove), les retrigs répètent un trig à vitesse réglable (rolls, roulements)
avec une montée ou une chute de vélocité.

## Gestes rapides

| Action | Touches |
|---|---|
| Micro timing d'un trig | maintenir `[TRIG]` + `[LEFT]/[RIGHT]` (GRID) |
| Micro timing de tous les trigs | maintenir `[TRIG] + [FUNC]` + `[LEFT]/[RIGHT]` |
| Page RETRIG | `[TRIG PARAMETERS]` deux fois (GRID) |
| Retrig sur un trig | maintenir `[TRIG]`, `RTRG` on (knob A) |
| Swing du pattern | `[TEMPO]`, DATA ENTRY D (50-80 %) |

Paramètres retrig : `RATE` (1/16 = un coup par pas, 1/32 = deux, 1/12 ou
1/24 = triolets), `LEN` (durée du roll, en pas), `VFAD` (-64 = s'éteint,
+64 = monte jusqu'à la vélocité pleine).

## Pas à pas : roulement de caisse avant un drop

1. `[RECORD]`, track 3 (clap / snare), dernière page du pattern d'avant le
   drop.
2. Poser un trig sur le pas 13, le maintenir, `[TRIG PARAMETERS]` deux fois.
3. `RTRG` on, `RATE` 1/32, `LEN` 4 (jusqu'à la fin de la mesure), `VFAD`
   +64 : le roll monte en puissance.
4. Variante tribe : `RATE` 1/12 pour un roulement en triolets.

## En live techno

- Le roulement de caisse ci-dessus double le riser de la track 15 (doctrine
  §5) : préparé dans le dernier pattern avant chaque drop de la chaîne.
- Hats en léger retard (micro timing positif sur les contretemps) : le
  groove « tire » sans toucher au swing global. À 190 BPM, rester subtil.
- Kick et rumble : jamais de micro timing, ils tiennent la grille.
- Combiner avec une condition `FILL` (lot 3) : le roll ne joue que quand on
  tient `[PAGE]`.

## Pièges

- Les retrigs n'existent pas sur les tracks MIDI.
- `VFAD` dépend du `VEL` de la page TRIG 1 : un `VEL` bas étouffe le roll.
- La quantize (cf. [[enregistrement-quantize]]) recale aussi le micro timing.
- `LEN` du retrig ≠ `LEN` de la note : le premier borne la courbe de
  vélocité du roll.

## À essayer (5 min)

Même trig de snare, comparer `RATE` 1/16, 1/32, 1/12 avec `VFAD` +64, puis
-64 : choisir un roulement « montée » et un « retombée » à garder comme
presets (`[TRIG] + [PRESET/KIT]`).

Source : manuel DT2 OS 1.17, §7.3, §10.4, §10.5, §11.3.
