---
tags: [technique, patches, dubstep, tidalcycles]
---

# Patches — dubstep

## Anatomie du genre

- **Tempo** : 140 BPM, **perçu en half-time** (~70 BPM). Kick sur 1, snare sur 3.
- **Drums** : sparse. Kick et snare lourds, hi-hat discret, parfois une percu syncopée.
- **Basse** : **wobble** = LFO sur le cutoff d'une basse saw, qui fait osciller le timbre rythmiquement, + **sub massif** dessous qui dialogue avec le wobble.
- **Atmosphère** : espace, reverb généreuse, sentiment de vide entre les frappes. Le silence fait partie de l'instrumentation.

## Patches

### Tempo

```haskell
setcps (140/60/4)
```

### Drums — half-time

```haskell
d1 $ s "bd ~ ~ ~ sn ~ ~ ~"
  # gain 1.0
  # shape 0.4
```

### Hat — sparse

```haskell
d2 $ s "~ ~ hh ~ ~ ~ hh ~"
  # gain 0.55 # hpf 7000
```

### Wobble bass — pièce maîtresse

```haskell
d3 $ n "<0 0 -3 -5 -3 0>" # s "supersaw"
  # voice 0.4
  # cutoff (range 150 1600 $ fast 4 sine)   -- LFO 4× par mesure → wobble
  # resonance 0.4
  # release 0.5
  # gain 0.95
  # shape 0.35
```

### Sub — gros, long, dominant

```haskell
d4 $ n "<0 0 -3 -5>/2" # s "sine"
  # release 0.7
  # lpf 100
  # gain 1.0
```

### Pad / atmosphère

```haskell
d5 $ n "<0 -3 -5 -3>/4" # s "supersaw"
  # voice 0.7
  # release 1.5
  # cutoff 1000
  # gain 0.45
  # room 0.6 # sz 0.8
```

## À tweaker

- **Tempo** : 138 (deep dub) → 142 (skip up). Au-delà → drum'n'bass.
- **d3 vitesse du wobble** :
  - `fast 2` : lent, sourd, profond
  - `fast 4` : commun, 4 wobbles par mesure
  - `fast 8` : frénétique, brostep
- **d3 forme du LFO** : `sine` (doux) → `saw` (montant) → `square` (gate dur) → `tri` (linéaire)
- **d3 `voice`** : 0.2 (clean) → 0.85 (gros et large)
- **d1** : ajouter `# speed 0.9` sur le kick pour creuser le sub
- **d2** : remplacer par `s "~ ~ cp ~ ~ ~ cp ~"` pour des claps
- **Reverb agressive sur le snare** (couche dédiée) :

```haskell
d6 $ s "~ ~ ~ ~ sn ~ ~ ~" # room 0.9 # sz 0.95 # gain 0.7
```

## Variations / structures

### Drop : laisser sub + pad seuls 4 mesures

```haskell
d1 silence
d2 silence
d3 silence
-- d4 et d5 continuent
-- attendre 4 mesures, puis réévaluer
```

### Build-up : wobble qui accélère sur 16 mesures

```haskell
d3 $ n "<0 0 -3 -5>" # s "supersaw"
  # voice 0.4
  # cutoff (range 150 1600 $ fast (range 2 16 $ slow 16 saw) sine)
  # gain 0.95
```

Le LFO passe de 2× à 16× par mesure sur 16 mesures. Tension max.

### Variation de la forme du LFO en alternance

```haskell
d3 $ n "<0 0 -3 -5>" # s "supersaw"
  # voice 0.4
  # cutoff (range 150 1600 $ fast 4 "<sine tri square saw>")
  # gain 0.95
```

Une forme d'onde différente toutes les 4 mesures.

## Liens

- [[../sound-system-free-party]] — sub mono < 150 Hz
- [[_index]] pour les conventions

#dubstep #patches
