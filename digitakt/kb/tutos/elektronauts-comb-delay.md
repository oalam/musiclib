---
tags: [digitakt, kb, tutos]
theme: Comb filter et delay accordé (Elektronauts)
lot: 2
ordre: 9
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
auteur: communauté Elektronauts
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-23
---

# Elektronauts 9 — Comb filter et delay accordé

**En une phrase** : le comb filter s'accorde sur des do à l'octave en tenant
`[FUNC]`, devient un résonateur jouable avec le key tracking, et un delay au
temps minimum avec beaucoup de feedback fait un résonateur de Karplus-Strong
à resampler.

Panorama : [[elektronauts-panorama]]. Fiches du geste : [[../filtres]],
[[../send-fx-compresseur]], [[../sampling-resampling]].

## Sur notre grille

Le comb se cale sur la tonique de la banque ([[../../doctrine]] §11,
[[../theorie/kt-tonalite-du-grave]]) ; flanger sur les hats 6-7 ; résonateur
sur 13-14, puis resample.

## Astuces

### 1. Comb sur tout, et flanger de hats

- **Source** : [#17](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/17), [#116](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/116).
- **Résultat** : hats flangés des années 90 ; ou un pattern entier passé au
  comb puis resamplé.
- **Pas à pas (hats)** :
  1. Hat 6 : filtre 1 en **comb**, fréquence très lente à moduler (LFO
     lent sur FREQ), feedback élevé.
  2. Filtre 2 en passe-haut pour nettoyer le grave.
  3. Un peu de delay et de reverb.
- **Pas à pas (tout)** :
  1. Comb sur chaque track du pattern (ou CTRL-ALL sur le type de filtre).
  2. Resampler MAIN L/R, garder le résultat comme sample de texture.

### 2. Accorder le comb

- **Source** : [#181](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/181), [#392](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/392).
- **Résultat** : un comb sur la tonique, puis un résonateur jouable au
  clavier.
- **Pas à pas** :
  1. Filtre en comb ; tenir `[FUNC]` en tournant `FREQ` : l'encodeur
     s'arrête sur 0, 48, 60, 72, 84, 127, des do à l'octave.
  2. Pour une autre tonique, partir du do le plus proche et compter les
     demi-tons.
  3. Page 2 du filtre : key tracking vers la fréquence du comb pour que la
     note jouée l'accorde.
- **Chez nous** : accorder le comb sur la tonique du kick
  ([[../theorie/kt-tonalite-du-grave]]).

### 3. Delay en résonateur

- **Source** : [#290](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/290).
- **Résultat** : percussions à main, basses et plucks tirés d'un transitoire
  ou d'une onde à cycle unique ; resample pour jouer chromatiquement.
- **Pas à pas** :
  1. Source : onde à cycle unique ou transitoire court sur une track.
  2. Delay au **temps minimum**, send à fond sur la track.
  3. Monter le feedback très lentement, jusqu'à 103-110 selon la largeur
     de bande du delay (au-delà ça part en larsen).
  4. Enveloppe de filtre positive sur la track pour l'attaque.
  5. Resampler la note, la poser en one-shot et la jouer au clavier.
- **Attention** : monter le BPM raccourcit encore le delay et monte la
  hauteur ; limiteur conseillé sur le master.

## Liens

[[elektronauts-panorama]] · [[../filtres]] · [[../send-fx-compresseur]] ·
[[../sampling-resampling]] · [[../theorie/kt-tonalite-du-grave]] ·
[[../../doctrine]] §11
