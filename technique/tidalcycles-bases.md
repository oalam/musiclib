---
tags: [technique, tidalcycles, bases]
---

# TidalCycles — bases

Tidal pense la musique comme **patterns** (motifs cycliques) qu'on transforme par fonctions. Un cycle = une mesure (durée modifiable via `cps`).

## Mini-langue de patterns

```haskell
-- Séquence simple (4 pas dans un cycle)
d1 $ s "bd cp sn cp"

-- Répétition
d1 $ s "bd*4"           -- 4 bd dans le cycle
d1 $ s "bd/2"           -- bd toutes les 2 mesures

-- Euclidien : 3 frappes réparties sur 8 pulsations (tribe-friendly)
d1 $ s "bd(3,8)"

-- Alternance lente
d1 $ s "<bd cp sn>"     -- un son par cycle, en rotation
```

## Canaux et silence

```haskell
d1 $ s "bd*4"
d2 $ s "~ cp ~ cp"      -- ~ = silence
hush                    -- tout couper
solo 1                  -- isoler d1
unsolo 1
```

## Transformations

```haskell
every 4 (fast 2) $ s "bd cp sn cp"   -- toutes les 4 mesures, double la vitesse
slow 2 $ s "bd cp"
fast 2 $ s "bd cp"
jux rev $ s "bd cp sn cp"            -- canal stéréo : version inversée à droite
degrade $ s "hh*16"                  -- supprime aléatoirement la moitié
sometimes (# crush 4) $ s "bd*4"
```

## Effets (chaîne SuperDirt)

```haskell
d1 $ s "bd*4"
  # gain 1.1
  # lpf 800 # resonance 0.4
  # room 0.3 # sz 0.6
  # delay 0.3 # delaytime (1/3) # delayfb 0.4
  # crush 6
  # shape 0.4
```

## Tempo

```haskell
setcps (170/60/4)        -- 170 bpm en 4/4
```

Tribe / acid core : viser 175–195 BPM.

## Acid 303-like

```haskell
d3 $ n "0 7 0 5 3 ~ 0 7" # s "supersquare"
  # cutoff (range 200 3000 $ slow 8 sine)
  # resonance 0.35
  # gain 0.95
  # shape 0.5
  # release 0.08
```

## Pour aller plus loin

- Doc officielle : https://tidalcycles.org/docs/
- *Getting started* : https://tidalcycles.org/docs/getting-started/
- Voir aussi `refs/` pour livres et papers.

#tidalcycles #patterns
