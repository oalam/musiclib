---
tags: [technique, patches, drum-and-bass, tidalcycles]
---

# Patches — drum'n'bass

## Anatomie du genre

- **Tempo** : 170–180 BPM (sweet spot 174). Le rythme **se sent en half-time** : kick sur 1, snare sur 3 dans un 4/4 — donc rythme perçu autour de 85 BPM.
- **Drums** : centre de gravité = breakbeats (Amen surtout, aussi Think, Apache). En live coding : programmer un break à la main, OU choper un break sampé (`amencutup`).
- **Basse** : sub dominant + un **reese** (saws détunées à effet phasey) qui occupe les médiums.
- **Hats** : 16ᵉs, accent sur les off-beats.
- **Atmosphère** : pads aériens, vocal stabs, breakdowns longs.

## Patches

### Tempo

```haskell
setcps (174/60/4)
```

### Drums — version 1 : kick + snare half-time

```haskell
d1 $ s "bd ~ ~ ~ sn ~ ~ ~"
  # gain 1.0
  # shape 0.3
```

### Drums — version 2 : Amen choppé

```haskell
-- amencutup contient les chops du break (16 disponibles, n 0..15)
d1 $ s "amencutup*8" # n (irand 16)
  # gain 1.0
```

Ou avec `slice` (plus contrôlable, on choisit la séquence) :

```haskell
d1 $ slice 16 "0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15" $ s "amen"
  # gain 1.0
```

### Hats — 16ᵉs animés

```haskell
d2 $ s "hh*16"
  # gain (range 0.4 0.9 $ slow 4 sine)
  # hpf 6000
  # pan (range (-0.3) 0.3 $ slow 8 rand)
```

### Reese bass — saws détunées + filtre LFO

```haskell
d3 $ n "<0 0 -3 -5 -7 -3 0 0>" # s "supersaw"
  # voice 0.5            -- mixe saw simple → empilement détuné
  # detune 0.3
  # cutoff (range 200 1800 $ slow 8 sine)
  # resonance 0.35
  # gain 0.95
  # release 0.3
```

### Sub — note tenue dessous

```haskell
d4 $ n "<0 -3 -5 -3>/2" # s "sine"
  # release 0.6
  # lpf 90
  # gain 0.9
```

## À tweaker

- **Tempo** : 168 (deep DnB / liquid) → 178 (drum funk / neurofunk)
- **d3 `voice`** : 0.2 (saw simple, deep) → 0.9 (très détuné, neurofunk lourd)
- **d3 LFO cutoff** :
  - `slow 8` (vague lente, marin)
  - `slow 16` (sub aquatique, deep)
  - `fast 2` (wobble rapide — tu glisses vers le dubstep)
- **d1 (amen)** : ajouter `# speed (range 0.95 1.05 $ slow 16 sine)` pour micro-pitch sur le break
- **d1** : ajouter `jux rev` — version inversée à droite, effet drum funk hallucinant
- **d2** : `degrade` pour aérer, ou `every 4 (# crush 4)` pour un bit-crush ponctuel
- **d4 (sub)** : remplacer le `release 0.6` par `release 1.5` pour un sub tenu

## Variations / structures

### Drop (8 mesures sans drums)

```haskell
d1 silence
d2 silence
d3 silence
-- d4 sub continue
-- attendre, puis réévaluer tous les blocs d'un coup pour le retour
```

### Build-up : cutoff montant

```haskell
d3 $ n "<0 0 -3 -5>" # s "supersaw"
  # voice 0.5 # detune 0.3
  # cutoff (range 200 4000 $ slow 16 saw)   -- saw montant = tension
  # gain 0.95
```

## Liens

- [[../tidalcycles-bases]] pour les fonctions de transformation
- [[_index]] pour les conventions

#dnb #patches
