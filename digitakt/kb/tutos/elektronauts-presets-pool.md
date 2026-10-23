---
tags: [digitakt, kb, tutos]
theme: Presets et preset pool, le rack de fills (Elektronauts)
lot: 2
ordre: 1
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
auteur: communauté Elektronauts
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-23
---

# Elektronauts 1 — Presets et preset pool

**En une phrase** : sur la DT2 un trig p-locké se sauve en preset d'un seul
geste, et le preset pool (les presets chargés dans le pattern, jouables aux
touches de trig) devient un rack de fills et de one-shots que l'on tient le
temps d'un appui à la place du son de la track.

Panorama et vocabulaire : [[elektronauts-panorama]]. Fiches du geste :
[[../preset-pool]], [[../presets-kits-pool]], [[../slice-breaks]].

## Sur notre grille

Le pool vit par pattern. Sur la grille de la [[../../doctrine]] §1, les
presets de fills visent la 15 (risers, impacts), la 12 (cris, voix), la 4
et la 5 (toms, boucle de break). La 1 et la 2 restent hors pool : le kick
ne change pas (§3).

## Astuces

### 1. Un trig devient un preset

- **Source** : [#9](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/9), le post le plus voté du fil (62 likes).
- **Résultat** : chaque trouvaille (un kick retuné sur le pas 9, un hat avec
  son lock de filtre) devient un preset du +Drive, rappelable dans tout
  projet.
- **Pas à pas** :
  1. En GRID RECORDING, tenir le trig qui porte les p-locks.
  2. Sans lâcher, presser `[PRESET/KIT]`.
  3. Choisir « Save new preset » : le preset embarque le sample, la
     machine et tous les p-locks du trig.
  4. Nommer, ranger dans un dossier du +Drive, valider par `[YES]`.
- **Chez nous** : à faire pour chaque kick de banque retenu (doctrine §3) et
  pour les rumbles ([[../rumble-grave]]).

### 2. Le pool comme rack de fills

- **Source** : [#268](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/268).
- **Résultat** : en mode PRESET, tenir une touche mute la track sélectionnée
  et joue le preset à la place ; un break remplacé par un riser à la volée.
  Avec `RETRIG ON` et `LEN` au minimum, chaque touche tenue retrigue à la
  vitesse choisie : des fills de jungle sur une boucle Werp, Repitch ou
  Stretch.
- **Pas à pas** :
  1. Réserver un pattern de travail ; y poser sur 16 tracks les sons de
     fill (risers, impacts, cris, boucles de break).
  2. Sauver le kit de ce pattern (`[PRESET/KIT]`, « Save kit », un nom
     court).
  3. Vider le pool du pattern de destination.
  4. KITS > MANAGE > flèche gauche sur le kit > « Add to preset pool » : la
     première page du pool est maintenant ce kit.
  5. Dans le pattern de live, passer en mode PRESET (`[FUNC] + [PRESET/KIT]`
     selon la fiche [[../preset-pool]]) ; sélectionner la track à remplacer,
     tenir la touche du preset : la track se tait, le preset joue.
  6. Pour un fill roulé : sur la track hôte, page RETRIG `ON`, `LEN` au
     minimum ; tenir la touche de preset et changer le `RATE` (1/8, 1/16,
     1/32).
- **Attention** : le preset tenu continue même si on change de mode de trig.
- **Chez nous** : exercice 3 du panorama ; pool de fills sur 15, 12, 4, 5.

### 3. Nommer d'un coup les 16 presets d'un pattern

- **Source** : [#287](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/287).
- **Résultat** : les 16 presets du pool portent un préfixe commun.
- **Pas à pas** :
  1. Sauver le kit sous le nom voulu (par exemple `TRB`).
  2. KITS > MANAGE > « Add to preset pool ».
  3. Les 16 presets arrivent nommés `TRB …`, dans l'ordre des tracks.

### 4. Chaîne Grid sauvée en preset

- **Source** : [#256](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/256).
- **Résultat** : un preset « progression d'accords » qui rappelle la
  machine Grid, ses slices et son `LEN` ; posé sur une track, trigs
  d'enregistrement et random locks, et le pattern démarre.
- **Pas à pas** :
  1. Sur une track, machine Grid sur une chaîne d'accords ou de notes
     tenues ; régler `GRID`, `SLICE` et `LEN`.
  2. Sauver la track en preset (tenir `[TRK]` + `[PRESET/KIT]` ou depuis un
     trig, astuce 1).
  3. Dans un nouveau pattern, charger le preset sur la 13 ou la 14, poser
     des trigs, `[PAGE] + [YES]` pour des locks aléatoires de slice.
- **Chez nous** : Id2 et Id3 (13, 14, doctrine §12).

### 5. Faux slicing par le pool, et la machine Slice

- **Source** : [#450](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/450), [#491](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/491).
- **Résultat** : plusieurs points de départ d'un même sample sous les
  touches de preset ; depuis l'OS 1.15 la machine Slice fait mieux, et une
  Slice à une seule tranche sert à rogner finement un one-shot.
- **Pas à pas (pool)** :
  1. Sur une track, le sample ; régler `STRT` sur le premier coup, sauver
     en preset ; répéter pour chaque coup (`STRT` différent, même sample).
  2. Ajouter ces presets au pool.
  3. Pour poser le même preset sur toute la track : `[TRK]` tenu + touche
     de trig ; sur une page : `[PAGE]` tenu + touche de trig.
- **Pas à pas (Slice, OS 1.15 et plus)** :
  1. Machine Slice sur la track, une seule tranche.
  2. Ajuster début, fin et point de boucle de la tranche pour rogner le
     one-shot au plus près.
  3. Répéter sur deux ou trois tracks pour empiler des snares rognées.
- **Chez nous** : [[../slice-breaks]] pour les breaks de la 5.

## Liens

[[elektronauts-panorama]] · [[../preset-pool]] · [[../presets-kits-pool]]
· [[../slice-breaks]] · [[../rumble-grave]] · [[../../doctrine]] §3, §12
