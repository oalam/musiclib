---
tags: [digitakt, kb, tutos]
theme: Grid, wavetables, LFO aléatoire, granulaire (Elektronauts)
lot: 2
ordre: 8
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
auteur: communauté Elektronauts
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-23
---

# Elektronauts 8 — Grid, wavetables, LFO aléatoire

**En une phrase** : la machine Grid découpe un sample en 16 à 64 tranches
et un LFO aléatoire lissé (`RAND` + `SLEW`) sur le numéro de slice en fait
un drone de wavetable, un remix de boucle ou une texture granulaire ; la
DT2 devient un oscillateur à partir d'un sample.

Panorama : [[elektronauts-panorama]]. Fiches du geste : [[../machines-src]],
[[../lfo]], [[../slice-breaks]], [[../euclidien]].

## Sur notre grille

Drones et textures sur l'atmo 11 ; remix de boucle sur l'Id1 5 ; sample
oscillateur sur 13 et 14. Les réglages de slice et de profondeur sont liés :
hors de la table, du bruit ([[elektronauts-panorama]] pièges).

## Astuces

### 1. 128 pas = 64 demi-pas à x2

- **Source** : [#3](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/3).
- **Résultat** : un territoire DnB, trigs serrés et slices aléatoires.
- **Pas à pas** :
  1. Trigs euclidiens convertis en grille ([[elektronauts-seconde-sequence]]
     astuce 2), longueur 128 pas.
  2. Machine Grid 32 ou 64 sur une boucle de break, `LEN 4`.
  3. `[PAGE] + [YES]` : random locks de slice sur la page.
- **Chez nous** : Id1 5 en half-time ([[../theorie/kt-halftime-passerelles]]).

### 2. Drone wavetable

- **Source** : [#111](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/111), [#76](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/76), [#390](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/390), [#473](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/473).
- **Résultat** : une nappe mouvante depuis une wavetable d'usine, sans clic.
- **Pas à pas** :
  1. Sample : Factory > 5-Oscillators > Wavetables.
  2. Machine Grid, `GRID 64`, `SLICE 32`, `PLAY FWD.L`, AMP REL au maximum.
  3. LFO : `WAVE RAND`, `SLEW 127`, mode `FREE`, `DEP 32`,
     `DEST SRC:SLICE`, `MULT BPM 1`, `SPD 8`.
  4. Un trig long, écouter : la table se parcourt sans saut.
- **Attention** : pour balayer toute la table sans sortir, slice **33**,
  `LEN 1`, profondeur **31,99** ; hors plage le LFO donne du bruit. Mettre
  la slice par défaut au milieu pour qu'un LFO sinus ou random lissé couvre
  tout.
- **Chez nous** : atmo 11.

### 3. Grid random comme remix

- **Source** : [#534](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/534).
- **Résultat** : un remix de boucle plus musical que les random locks.
- **Pas à pas** :
  1. Boucle d'une mesure en Grid 16, trigs sur les 16 pas.
  2. Locks de slice linéaires (slice 1 sur le pas 1, 2 sur le 2…) : la
     boucle joue droite.
  3. Euclidien ON, puis randomiser la page euclidienne : la rotation
     réordonne les tranches en gardant la grille.
- **Chez nous** : Id1 5 ([[../slice-breaks]]).

### 4. SRC + YES pour l'inspiration

- **Source** : [#408](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/408).
- **Pas à pas** :
  1. Charger une trentaine de samples au hasard dans le projet.
  2. Sur une track : `[SRC] + [YES]` enchaîné : des slices aléatoires de
     samples aléatoires.
  3. Garder AMP, FLTR, FX et LFO, nouveau `[SRC] + [YES]` jusqu'à ce qu'un
     son accroche ; le sauver en preset.

### 5. Granulaire et sample comme oscillateur

- **Source** : [#410](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/410), [#550](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/550).
- **Résultat** : une note de synthé de quelques secondes devient un
  oscillateur sculpté par les enveloppes et le filtre de la DT2 ; grains
  doux par LFO sur le point de départ.
- **Pas à pas** :
  1. Échantillonner une note de synthé de 3 s, filtre ouvert, plus longue
     que nécessaire (pour monter la note sans atteindre le point de boucle).
  2. Machine one-shot en `FWD.L`, AMP et filtre de la DT2 pour la forme.
  3. LFO libre sur `STRT` : chaque frappe part d'un endroit différent.
  4. LFO triangle sur AMP VOL pour des grains doux.
- **Attention** : depuis l'OS 1.10 les clics de boucle ont presque disparu.
- **Chez nous** : 13 et 14, en complément des presets Substance
  ([[../presets-substance]], [[../oneshots-synthe]]).

### 6. Timestretch sans la machine, et l'inverse

- **Source** : [#179](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/179), [#237](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/237).
- **Pas à pas** :
  1. Sur une machine one-shot, sacrifier un LFO (rampe sur `STRT` au tempo)
     pour recréer un stretch.
  2. À l'inverse : un kick sauvé sous la machine Timestretch puis rejoué en
     one-shot donne un accent lourd.

### 7. Boucle depuis un point de départ

- **Source** : [#72](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/72).
- **Pas à pas** :
  1. Machine en `FWD.L`.
  2. Pour partir de `STRT` et boucler depuis le début du sample : `LOOP` à
     0,02.

## Liens

[[elektronauts-panorama]] · [[elektronauts-seconde-sequence]] ·
[[../machines-src]] · [[../lfo]] · [[../slice-breaks]] · [[../euclidien]]
· [[../oneshots-synthe]] · [[../presets-substance]] ·
[[../theorie/kt-halftime-passerelles]]
