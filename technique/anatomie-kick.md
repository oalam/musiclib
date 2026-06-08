---
tags: [technique, kick, synthèse, anatomie]
source: "https://www.youtube.com/watch?v=mTGI15msfrE"
source_titre: "Understand the Kick Drum — Explained by a Musicologist"
source_auteur: "Bahadırhan Koçer — sound designer, producer, PhD Music Sciences"
---

# Anatomie du kick

Notes prises sur la vidéo de **Bahadırhan Koçer**. Le découpage suit le sien : trois couches structurelles (sub, thump, click), chacune avec une réponse physiologique distincte, et une recette de construction de A à Z. Le volet politique/philosophique est tiré au clair dans [[../philo/kick-comme-loi]].

> "Erase the idea of a drum. The kick exists as a convergence point — a precise collision where energy, matter, and perception align into a single, powerful event."

## Le kick comme événement

Avant d'être un son, le kick est un **point de convergence** : énergie + matière + perception alignées en un événement bref. Chaque variation dans son spectre **reconfigure la façon dont le corps habite le temps**.

- Sans kick, "time seeps, vanishes like water" — le temps fuit.
- À 70 BPM, c'est le pouls cardiaque : "optimum pulse, a body in sync".
- Le kick "tend un contrat solide : aligne-toi sur le pouls" — le **groove est un pacte**.

## Les trois couches

### 1. Sub — 30 à 60 Hz

À cette plage, "l'oreille cesse d'entendre et commence à sentir". Le système auditif délègue : peau, poitrine, os deviennent **capteurs**. Les mécanorécepteurs cutanés et viscéraux répondent ; la membrane basilaire de la cochlée bouge à peine.

> "The kick is kinetic information. The sub activates the body before the brain decides it's music."

C'est **primal, gravitationnel**. Le sub enracine le temps dans le corps. Pour une free party : précisément ce que le sound system rend disponible — un sub massif sollicite les viscères, pas les oreilles.

### 2. Thump — ~100 à 200 Hz

Là où l'onde **prend forme**. "The ear and the body meet halfway — muscular, tactile, yet audible." Donne au kick son **sentiment d'impact**, sa brève illusion de masse.

Le cortex auditif lit cette plage comme **frontière entre ton et toucher** — la même zone où les consonnes de la parole gagnent en force, où "drums become language".

### 3. Click — au-dessus de 2 kHz

Un pic transitoire de quelques millisecondes. Neuroscientifiquement : **phase locking** — le tronc auditif tire en synchronie avec le transitoire. Cette synchronisation rend le rythme **intelligible**.

> "The click defines the exact moment your nervous system acknowledges 'the beat'. Before the click, the music is shapeless… With the click, time crystallizes into perfect, high resolution."

### Synthèse

| Couche | Fréquence | Action physiologique |
|---|---|---|
| **Sub** | 30–60 Hz | stirs the viscera |
| **Thump** | 100–200 Hz | engages the muscles |
| **Click** | > 2 kHz | aligns the neurons |

"Together they create a full-spectrum signature that feels complete — a miniature model of how we experience sound itself."

## La recette de Koçer (Ableton Operator)

À transposer ensuite en SynthDef SuperCollider (plus bas).

### Oscillateurs

- **OSC A — sub** : sine, fixed **50 Hz**, attaque 0, sustain bas.
- **OSC B — thump** : triangle, **100 Hz** (× 2 du fondamental), attaque 0, release réduit, pas de sustain.
- **OSC C — click** : square, **1 kHz**, decay/release courts, pas de sustain.

> "A sine wave is smooth and contains no harmonics, so it cannot naturally create a sharp transient. A square wave has built-in high-frequency content and discontinuities, which produce a clear click."

Le click se cherche entre sine et square : "finding the sweet spot."

### Pitch envelope

- Initial level **+24 demi-tons** (2 octaves au-dessus)
- Peak level **+24 demi-tons**
- "Slopes matter too" — ajuster les pentes selon le grain voulu.

Sans ce sweep, "the electric pulse" reste raw — c'est ce qui donne le thump perçu.

### Saturation

Triangle = fondamental propre mais disparaît sur petite enceinte. Square = clic dur, peu d'harmoniques.

→ **Saturation Soft Sine, +4 dB**. Triangle gagne en harmoniques supérieures, square s'adoucit.

### Drum Bus

- Drive **10–15 %**
- Boom **30–50 %** (fréquence selon contexte)
- Transient **0.2–0.5**

Garde kick et basse centrés, pleins ; transitoire clarifié ; "full and sharp on every system".

### Utility — mono sous 150 Hz

Les grandes longueurs d'onde créent des problèmes de phase en stéréo, et l'oreille ne détecte pas la direction en bas du spectre. **Toujours mono < 150 Hz**. Strong, stable low end.

### Glue Compressor + Limiter

- Glue léger : attack rapide pour préserver le transitoire, ratio faible — concentre l'énergie au centre.
- Limiter : slight input boost, gain reduction optimale.

## Transposition TidalCycles / SuperCollider

### Variante A — sample sculpté (rapide)

```haskell
d1 $ s "bd*4"
  # speed 0.95            -- pitch légèrement plus bas, creuse le sub
  # shape 0.4             -- saturation soft
  # hpf 30 # lpf 12000
  # gain 1.0
```

Limites : on n'a pas le contrôle indépendant des trois couches. Utile pour démarrer, insuffisant pour vraiment **dessiner** un kick.

### Variante B — SynthDef calquée sur la recette de Koçer

```supercollider
SynthDef(\kickKocer, { |amp=1, decay=0.4|
  // SUB — sine 50 Hz avec pitch env +24 st (×4 en linéaire)
  var subEnv   = EnvGen.kr(Env.perc(0.001, decay), doneAction: 2);
  var subFreq  = XLine.kr(200, 50, 0.05);
  var sub      = SinOsc.ar(subFreq) * subEnv;

  // THUMP — triangle 100 Hz, même type de sweep
  var thumpEnv = EnvGen.kr(Env.perc(0.001, decay * 0.6));
  var thumpFreq = XLine.kr(400, 100, 0.04);
  var thump    = LFTri.ar(thumpFreq) * thumpEnv * 0.7;

  // CLICK — square 1 kHz, très court
  var clickEnv = EnvGen.kr(Env.perc(0.001, 0.015));
  var click    = Pulse.ar(1000) * clickEnv * 0.3;

  // Mix + saturation soft sine (tanh)
  var mix = (sub + thump + click) * amp;
  mix = (mix * 1.3).tanh;

  // .dup = même signal L/R → mono effectif (ce qu'on veut sous 150 Hz)
  Out.ar(0, mix.dup);
}).add;
```

Une fois enregistrée, déclenchable depuis Tidal :

```haskell
d1 $ s "kickKocer*4" # cps (180/60/4)
```

Les facteurs `× 4` pour le pitch envelope correspondent aux +24 st de Koçer (2 octaves = ratio 4).

## À tester

1. Construire le kick **couche par couche** : sub seul → +thump → +click. **Sentir** chaque rôle physiologique sur le sub.
2. Comparer avec un sample stock (`bd:0`) sur le même système.
3. Régler la profondeur et la vitesse du pitch envelope — c'est là que se joue le thump perçu.
4. Tester sur caisson, pas au casque. Le sub ne se vérifie nulle part ailleurs.

## Liens

- [[../philo/kick-comme-loi]] — la lecture politique/poétique du kick chez Koçer
- [[../technique/sound-system-free-party]] — pourquoi le mono sous 150 Hz n'est pas une option
- [[../technique/tidalcycles-bases]]

#kick #synthèse #anatomie #koçer
