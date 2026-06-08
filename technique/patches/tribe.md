---
tags: [technique, patches, tribe, acid-core, tidalcycles]
---

# Patches — tribe / acid core

## Anatomie du genre

- **Tempo** : 175–200 BPM. Tribe FR : 180–190.
- **Drums** : kick **4 on the floor** saturé, hat sur les off-beats, claps occasionnels. Le kick est central — voir [[../anatomie-kick]] et la SynthDef `\kickKocer`.
- **Basse** : sub continu sous le kick + **303 acid** (square + filter sweep + résonance haute) comme signature.
- **Atmosphère** : sombre, hypnotique. Sample stabs, montées, breaks. L'énergie est dans la **continuité saturée** plus que dans les ruptures.

## Patches

### Tempo

```haskell
setcps (185/60/4)
```

### Kick (sample brut)

```haskell
d1 $ s "bd*4"
  # speed 0.95
  # shape 0.65
  # hpf 30 # lpf 9000
  # gain 1.0
```

Ou, une fois la SynthDef de Koçer enregistrée (voir [[../anatomie-kick]]) :

```haskell
d1 $ s "kickKocer*4" # gain 1.0
```

### Hats — off-beats

```haskell
d2 $ s "~ hh ~ hh"
  # gain 0.7 # hpf 8000
```

### Couche 16ᵉs denses (à activer ponctuellement)

```haskell
-- Activer en montée :
d3 $ s "hh*16" # gain 0.55 # hpf 9000
-- Couper :
d3 silence
```

### Acid 303

```haskell
d4 $ n "0 7 0 5 -3 ~ 0 7" # s "supersquare"
  # cutoff (range 200 3500 $ slow 16 sine)
  # resonance 0.4
  # release 0.07
  # shape 0.55
  # gain 0.95
  # accelerate (-0.03)      -- glide acid : chaque note glisse vers le bas
```

### Sub — note tenue sous le kick

```haskell
d5 $ n "0" # s "sine"
  # release 0.25
  # lpf 85 # gain 0.95
```

## À tweaker

- **Tempo** : 175 (acid techno groovy) → 200 (full tribe / acidcore brut)
- **d4 (acid)** :
  - notes : essayer `"0 12 0 7 -3 ~ 0 7"`, `"0 7 -3 5 0 -5 7 ~"`, ou plus chaotique `"0 7 ~ 5 -3 0 12 -5"`
  - `resonance` : 0.3 (doux) → 0.55 (criard — protéger les oreilles)
  - durée LFO `slow 16` : essayer `slow 32` (vague très lente, immersive) ou `slow 8` (plus mouvant)
  - `accelerate` : `0` (pas de glide), `(-0.05)` (glide marqué), `0.05` (pitch up bizarre)
- **d1 (kick) `shape`** : 0.4 (clair) → 0.85 (lourd, frôle la distorsion)
- **d2** : remplacer par `s "~ cp ~ cp"` pour des claps off-beat
- Couche noise tenue pour la tension :

```haskell
d6 $ s "white" # gain 0.3 # lpf 2000 # release 8
```

## Variations / structures

### Mute kick 1 mesure sur 8 (effet montée)

```haskell
d1 $ every 8 (const silence) $ s "bd*4"
  # speed 0.95 # shape 0.65 # gain 1.0
```

### Doubler le tempo de l'acid 1 mesure sur 4

```haskell
d4 $ every 4 (fast 2) $ n "0 7 0 5 -3 ~ 0 7" # s "supersquare"
  # cutoff (range 200 3500 $ slow 16 sine)
  # resonance 0.4 # release 0.07 # shape 0.55
```

### Break sec : couper kick + acid, laisser sub + hat

```haskell
d1 silence
d4 silence
-- 4 mesures, puis réévaluer d1 et d4
```

## Liens

- [[../anatomie-kick]] — la pièce maîtresse du kick tribe
- [[../sound-system-free-party]] — le contexte de jeu
- [[_index]] pour les conventions

#tribe #acid-core #patches
