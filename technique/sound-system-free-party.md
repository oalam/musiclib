---
tags: [technique, sound-system, free-party]
---

# Live coder pour un sound system de free party

Le sound system free party n'est pas un casque, ni un club. C'est un mur de basses dans un champ ou une grange, avec sub qui descend très bas, public en endurance, énergie continue.

## Implications pour le code

- **Le sub n'est pas négociable.** Tester sur un caisson — pas seulement au casque. Beaucoup de patterns qui pétaient en studio se vident dans 8000 W.
- **Headroom.** Le système est saturé en sortie ; il faut laisser du gras. Un kick à `gain 1.5` + sub libre sera mangé par les amplis. Mieux : kick mid-tight + sub propre via couche dédiée.
- **Continuité.** Pas de blanc imprévu. `hush` au mauvais moment = malaise. Toujours préparer la sortie d'un pattern avec une couche de continuité (drone, hihat, sub tenu).
- **Ruptures lisibles.** Le public free aime les chocs de structure : drop, montée, breakdown. Mais lisibles — un break trop subtil dans un système à 8000 W passe inaperçu.

## Chaîne sonore type

Laptop → carte son (USB) → DI box ou jack symétrique → console du sound system → ampli → caissons.

Penser : **niveau de sortie cohérent** avec ce que le système attend. Un peu en dessous de 0 dBFS, pas de clipping numérique. Le système se charge déjà bien tout seul de saturer.

## Patterns spécifiques

### Kick tribe à 180 BPM

```haskell
setcps (180/60/4)
d1 $ s "bd*4"
  # gain 1.0
  # shape 0.6
  # speed 0.95         -- pitcher légèrement plus bas pour creuser le sub
```

### Sub indépendant du kick

```haskell
d2 $ n "0 ~ 0 ~ 0 ~ 0 ~" # s "sine"
  # gain 0.9
  # release 0.18
  # lpf 90             -- coupe net au-dessus de 90Hz
```

### Mute du kick à intervalles (effet montée)

```haskell
d1 $ every 8 (const silence) $ s "bd*4"
```

## À tester en condition

- Latence laptop → système (cable + DI). Mesurer avant le set.
- Comportement de SuperDirt sur 1h+ de tourne (CPU, RAM, drift).
- **Plan B** : avoir un set audio pré-enregistré sur clé USB en cas de plantage. C'est pas tricher, c'est prévoir.

#sound-system #free-party #live
