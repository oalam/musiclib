---
tags: [digitakt, kb, tutos]
theme: Une seconde séquence cachée dans chaque pattern (Elektronauts)
lot: 2
ordre: 2
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
auteur: communauté Elektronauts
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-23
---

# Elektronauts 2 — Une seconde séquence cachée dans chaque pattern

**En une phrase** : chaque couche du séquenceur a un interrupteur
(euclidien, retrig, page loop au-delà de la longueur maître, perform kit,
condition sur toute la track), et un pattern fini garde deux ou trois
variations en réserve sans pattern supplémentaire.

Panorama : [[elektronauts-panorama]]. Fiches du geste : [[../euclidien]],
[[../microtiming-retrigs]], [[../page-setup]], [[../perform-kit-temp-save]],
[[../parameter-preset-locks]], [[../keyboard-gammes]].

## Sur notre grille

Les variations se préparent sur les tracks qui ont le droit de bouger :
percs 4 et 5, hats 6 et 7, ride 8, Id 13 et 14. Kick 1, rumble 2 et MIDI
16 restent hors CONTROL ALL CONFIG ([[../../doctrine]] §4).

## Astuces

### 1. Euclidien éteint = séquence B

- **Source** : [#81](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/81), [#286](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/286), [#204](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/204), [#522](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/522).
- **Résultat** : un fill de toms sur 4 et 5 pendant que kick et hats
  tiennent, déclenché et rangé d'un geste.
- **Pas à pas** :
  1. Sur la perc 4, page euclidienne : régler les générateurs A et B
     (par exemple E(5, 16) et E(7, 16)), laisser le mode **OFF**.
  2. Même chose sur la 5 avec d'autres valeurs. Sur les tracks qui ne
     doivent pas bouger, laisser A et B à zéro.
  3. `[FUNC] + [FLTR]` : CONTROL ALL CONFIG, cocher 4 et 5 seulement.
  4. En jeu : `[TRK]` tenu + basculer « Euclidean ON » : les tracks dont les
     générateurs sont réglés passent sur la séquence euclidienne, les
     autres ne bougent pas.
  5. `[NO]` avant de lâcher `[TRK]` pour revenir.
- **Attention** : les p-locks posés sur les trigs euclidiens suivent la
  rotation et se retrouvent aux mêmes pas sur la grille rouge. Le `LEN`
  euclidien agit même mode éteint, donc un CTRL-ALL dessus décale tout le
  pattern ([#522](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/522)).

### 2. Euclidien → grille

- **Source** : [#75](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/75).
- **Résultat** : une recherche euclidienne concluante figée en trigs rouges
  éditables.
- **Pas à pas** :
  1. Page euclidienne de la track, mode ON, écouter.
  2. Tenir `[FUNC]` et tourner l'encodeur du mode sur OFF : les trigs bleus
     deviennent des trigs rouges.
  3. Éditer, p-locker, poser des conditions comme sur toute grille.

### 3. Page de retrig = fill verrouillable

- **Source** : [#97](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/97).
- **Résultat** : le hat fermé passe de croches en doubles croches par un
  interrupteur, indépendant de FILL et de l'euclidien ; trois couches de
  variation dans un pattern.
- **Pas à pas** :
  1. Hat 6 en croches sur la grille.
  2. Page RETRIG de la track : `LEN 2`, `RATE 1/16`, interrupteur **OFF**.
  3. Sur les tracks qui ne doivent pas rouler : `LEN` et `RATE` au minimum,
     ou les sortir de CONTROL ALL CONFIG.
  4. En jeu : `[TRK]` tenu + retrig ON ; le hat roule ; OFF, il revient.
- **Chez nous** : exercice 1 du panorama ; profils de [[../theorie/kt-hats]].

### 4. Pages au-delà de la longueur maître

- **Source** : [#304](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/304).
- **Résultat** : un fill de batterie sur les pages 5 à 8 qui ne touche pas
  la seconde rangée.
- **Pas à pas** :
  1. `[FUNC] + [PAGE]` : longueur par track, longueur maître 64 pas.
  2. Kick 1, rumble 2, clap 3, percs 4 et 5 : longueur 128 (pages 5 à 8
     écrites avec le fill).
  3. Les autres tracks restent à 64 ou moins.
  4. En jeu : `[PAGE]` tenu + touches 9 à 16 pour boucler les pages 5 à 8 :
     seules les tracks écrites sur 128 changent, les autres continuent.
- **Attention** : la page loop a eu des bugs en lecture live sous l'OS 1.01 ;
  à revérifier en 1.17 avant de compter dessus.

### 5. Punch-in de variation par perform kit

- **Source** : [#250](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/250), [#523](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/523).
- **Résultat** : une variation complète du kit (samples, FX) rappelée par
  deux touches, et le retour au kit du pattern par une seule.
- **Pas à pas (préparation)** :
  1. Pattern fini, perform kit **ON**.
  2. Construire la variation : samples, filtres, FX.
  3. `[FUNC] + [YES]` : temp save.
  4. Perform kit **OFF** : le pattern revient à son kit.
- **Pas à pas (live)** :
  1. Perform kit ON.
  2. `[FUNC] + [NO]` : la variation sauvée se charge.
  3. Perform kit OFF : retour au kit du pattern.
- **Attention** : selon l'auteur l'état perform est sauvé avec le projet, à
  vérifier ([[../perform-kit-temp-save]]).

### 6. Locks conditionnels sur toute la track

- **Source** : [#402](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/402), [#391](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/391), [#433](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/433).
- **Résultat** : une condition, une note ou un recalage de gamme posé sur
  tous les trigs d'une track en un geste (OS 1.10 et plus).
- **Pas à pas (condition)** :
  1. Tenir un trig de la track, puis `[TRK]`.
  2. Régler la condition (`2:2`) : toute la ligne attend le second tour.
- **Pas à pas (doubler le kick par la mélodie)** :
  1. Tenir un trig + `[TRK]`, régler `NOTE` pour coller les notes sur le
     kick 1.
  2. Même geste, ramener `NOTE` à C5 d'un coup : le kick double la ligne
     sans sauter de hauteur.
- **Pas à pas (recaler sur une gamme)** :
  1. KEYBOARD : changer la gamme ou la tonique, option « notes sur la
     gamme » active ([[../keyboard-gammes]]).
  2. Tenir un trig + `[TRK]`, `NOTE` +1 puis -1 : toutes les notes se
     recalent sur la nouvelle gamme.
- **Chez nous** : tonalité par banque ([[../../doctrine]] §11), 13 et 14 en
  `1:2` / `2:2` ([[../theorie/kt-phrasage-tension]]).

## Liens

[[elektronauts-panorama]] · [[elektronauts-ctrl-all]] · [[../euclidien]]
· [[../microtiming-retrigs]] · [[../page-setup]] ·
[[../perform-kit-temp-save]] · [[../parameter-preset-locks]] ·
[[../keyboard-gammes]] · [[../../doctrine]] §4, §11
