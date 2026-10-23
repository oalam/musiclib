---
tags: [digitakt, kb, tutos]
theme: CTRL-ALL ciblé comme geste de fill (Elektronauts)
lot: 2
ordre: 3
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
auteur: communauté Elektronauts
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-23
---

# Elektronauts 3 — CTRL-ALL comme geste de fill

**En une phrase** : `[TRK]` tenu + un encodeur agit sur toutes les tracks
cochées dans CONTROL ALL CONFIG, `[NO]` avant de lâcher annule tout ; un
fill d'un seul geste, et le retour par une touche.

Panorama : [[elektronauts-panorama]]. Fiche du geste :
[[../parameter-preset-locks]].

## Sur notre grille

CONTROL ALL CONFIG (`[FUNC] + [FLTR]`) exclut toujours le kick 1, le rumble
2 et la MIDI 16. Le reste se coche selon le geste voulu : 4-5-6 pour les
fills rythmiques, 9 à 14 pour un geste tonal ([[../../doctrine]] §4).

## Astuces

### 1. Casser puis revenir

- **Source** : [#36](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/36).
- **Résultat** : un chaos contrôlé de deux temps, puis le pattern intact.
- **Pas à pas** :
  1. Sauver le pattern (`[FUNC] + [YES]` temp save au minimum).
  2. Tenir `[TRK]`, tourner `TUNE` (ou tout autre encodeur) : toutes les
     tracks cochées bougent.
  3. Toujours `[TRK]` tenu, presser `[NO]` : tout revient.
  4. Lâcher `[TRK]` seulement après `[NO]`.
- **Attention** : lâcher `[TRK]` sans `[NO]` rend le changement définitif.

### 2. Slots de samples en CTRL-ALL

- **Source** : [#295](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/295), [#425](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/425).
- **Résultat** : le sample de toutes les tracks change d'un cran, le groove
  inchangé ; un kit complet qui bascule.
- **Pas à pas** :
  1. Prérequis : banques rangées par famille, le slot n de chaque banque
     joue le même rôle ([[elektronauts-projet-modele]]).
  2. Tenir `[TRK]`, tourner l'encodeur de slot de la page SRC : chaque
     track passe au slot suivant.
  3. Les flèches haut / bas ne changent que la track sélectionnée.
  4. Variante aléatoire : `[PAGE] + [YES]` randomise la page de la track ;
     avec `[TRK]` tenu, toutes les tracks cochées.
- **Chez nous** : n'a de sens qu'avec le 0-KIT et des banques par couleur
  ([[../../doctrine]] §2, §13).

### 3. Euclidien, retrig, LFO3 en CTRL-ALL

- **Source** : synthèse du fil ([[elektronauts-seconde-sequence]],
  [[elektronauts-resampling]]).
- **Résultat** : les trois interrupteurs se déclenchent d'un seul geste si
  les tracks concernées sont cochées.
- **Pas à pas** :
  1. Préparer les tracks (générateurs euclidiens réglés mode OFF, page
     RETRIG réglée OFF, LFO3 → AMP VOL profondeur ±0.01 arrêté).
  2. CONTROL ALL CONFIG : cocher ces tracks seulement.
  3. `[TRK]` tenu + le paramètre visé (mode euclidien, retrig ON,
     profondeur de LFO3) ; `[NO]` pour revenir.

## Liens

[[elektronauts-panorama]] · [[elektronauts-seconde-sequence]] ·
[[elektronauts-resampling]] · [[elektronauts-projet-modele]] ·
[[../parameter-preset-locks]] · [[../../doctrine]] §2, §4, §13
