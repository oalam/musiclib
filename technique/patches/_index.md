---
tags: [technique, patches, tidalcycles, index]
---

# Patches par genre

Patches Tidal classés par genre — copiables-collables dans un fichier `.tidal`, faits pour être **tweakés en live**. Chaque genre a son anatomie (BPM, feel, instrumentation) et ses points de variation.

## Index

- [[dnb]] — drum'n'bass / drum funk (170–180 BPM, half-time, amen + reese)
- [[tribe]] — tribe / acid core (175–200 BPM, kick saturé 4-on-the-floor + 303)
- [[dubstep]] — dubstep (140 BPM half-time, wobble bass + sub massif)

## Conventions communes

- **Canaux** par défaut : `d1` drums principaux, `d2` hats, `d3` basse, `d4` lead/acid, `d5` sub ou pad, `d6+` ornements. À ajuster.
- **Tempo** : `setcps (BPM/60/4)`. Toujours **avant** de lancer les patterns.
- **Couper une couche** : `d3 silence`.
- **Tout couper** : `hush`.
- **Solo / unsolo** : `solo 3`, `unsolo 3`.

## Astuces transversales

- **Modulation lente = vie**. Mettre `range x y $ slow 8 sine` sur n'importe quel paramètre (cutoff, gain, room, pan) donne un mouvement organique sans effort.
- **Tester sur sub avant set**. Un patch qui marche au casque peut s'effondrer sur sound system. L'inverse aussi. Voir [[../sound-system-free-party]].
- **Sub mono < 150 Hz** non négociable. Soit on filtre, soit on utilise `# pan 0.5`.
- **Transformations rapides** dans la trousse :
  - `every 4 (fast 2)` — doubler le tempo 1 mesure sur 4
  - `every 8 rev` — inverser le pattern 1 mesure sur 8
  - `sometimes (# crush 6)` — bit-crush aléatoire
  - `jux rev` — version inversée à droite (canal stéréo)
  - `degrade` — supprime aléatoirement la moitié des frappes

## À développer

- `transitions.md` — passer d'un genre à l'autre dans un set hybride
- `breaks.md` — patterns de break / drop / montée
- `texture.md` — pads, drones, ambiances pour reposer les oreilles

#patches #tidalcycles
