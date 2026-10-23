---
tags: [digitakt, kb, tutos]
theme: Projet modèle, kits, banques par famille (Elektronauts)
lot: 2
ordre: 7
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
auteur: communauté Elektronauts
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-23
---

# Elektronauts 7 — Projet modèle, kits, banques

**En une phrase** : tout nouveau pattern charge les slots 1 à 16, les kits
sont des copies et non des liens, et des banques rangées par famille
rendent le CTRL-ALL sur les slots musical ; un projet modèle plein, « save
as » à chaque live, et l'on ne repart plus de zéro.

Panorama : [[elektronauts-panorama]]. Fiches du geste :
[[../projet-sauvegarde]], [[../presets-kits-pool]], [[../machines-src]].

## Sur notre grille

C'est le 0-KIT A01-A16 et les banques par couleur de la [[../../doctrine]]
§2 et §13 ; les colonnes de l'auteur du fil (1 et 9, 2-3 et 10-11…) sont
remplacées chez nous par les rangées corps / tête (§1), le principe reste.

## Astuces

### 1. Slots 1 à 16 = kit par défaut

- **Source** : [#24](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/24), [#65](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/65), [#577](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/577).
- **Résultat** : chaque pattern vierge démarre avec ses 16 one-shots
  favoris ; un kit entier se charge en deux gestes.
- **Pas à pas** :
  1. PROJECT RAM : poser ses 16 one-shots dans les slots 1 à 16, dans
     l'ordre des tracks.
  2. Sauver le projet sous « DEFAULT » (ou le nom du 0-KIT) et le
     verrouiller.
  3. Pour un kit en deux gestes : vider les 16 slots, sélectionner dans le
     +Drive un dossier de 16 samples, « load to project » : ils tombent
     dans l'ordre sur les slots vides.
- **Chez nous** : 0-KIT A01-A16 ([[../projet-sauvegarde]], doctrine §2) ;
  l'export des lives (SPEC 7.L5) produit ces dossiers de 16.

### 2. Banques par famille, colonnes de tracks

- **Source** : [#101](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/101), [#425](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/425).
- **Résultat** : le slot n de chaque banque joue le même rôle, donc un
  CTRL-ALL sur les slots change tout le kit d'un cran sans casser la grille.
- **Pas à pas** :
  1. Ranger les banques par famille (l'auteur : A kicks et basses, B-C hats
     et claps, D percs, E synthés, F-H FX).
  2. Dans chaque banque, le même rôle au même numéro de slot.
  3. Projet modèle plein, « save as » à chaque nouveau live.
  4. En jeu : `[TRK]` tenu + encodeur de slot ([[elektronauts-ctrl-all]]).
- **Chez nous** : banques par couleur (doctrine §13), tracks en rangées.

### 3. Chaînes courtes ou slots pleins

- **Source** : [#24](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/24), [#218](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/218), [#219](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/219).
- **Résultat** : avec 1024 slots, un sample par slot et un LFO sur le slot
  remplacent la chaîne, sans silence perdu ; la chaîne reste utile pour le
  round-robin d'un même son.
- **Pas à pas** :
  1. Un son par slot ; variation par LFO ou lock sur le numéro de slot.
  2. Chaîne seulement pour quatre kicks presque identiques : Grid 4, locks
     de slice linéaires (« linear locks »), un round-robin.
- **Attention** : chaînes longues lentes à charger et pleines de silence,
  16 éléments au plus.

### 4. Kits et presets sont des copies

- **Source** : [#35](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/35).
- **Résultat** : comprendre que modifier le kit dans A02 ne touche pas A01 ;
  les kits sont des modèles à rappeler, pas des réglages partagés.
- **Pas à pas** :
  1. Charger un kit copie ses réglages dans le pattern ; le lien avec le
     +Drive est perdu.
  2. Pour propager une correction (un kick) : la refaire par pattern, ou
     passer par un preset ([[elektronauts-presets-pool]] astuce 1).
  3. Garder des kits modèles nommés par couleur (kit tribe, kit dub, kit
     dnb).
- **Chez nous** : « même kick dans tout le set » (doctrine §3) tenu par
  discipline ou par preset.

### 5. Transporter un pattern vers un autre projet

- **Source** : [#263](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/263).
- **Pas à pas** :
  1. Dans le projet source : sauver le kit du pattern sous « temp ».
  2. Copier le pattern (`[FUNC] + [REC]`).
  3. Ouvrir le projet cible, charger le kit « temp » sur le pattern de
     destination.
  4. Coller le pattern (`[FUNC] + [STOP]`).
- **Attention** : les locks de slot de sample ne suivent pas.

### 6. Multi-sample dynamique

- **Source** : [#464](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/464).
- **Résultat** : un fût acoustique vivant sur une track : 16 frappes
  classées, vélocité qui choisit la frappe, round-robin et variations
  minuscules.
- **Pas à pas** :
  1. Chaîne de 16 frappes d'un même fût en Grid 16 : les 10 premières
     fortes, les 6 suivantes de plus en plus douces.
  2. VEL → VOL OFF ; VEL MOD : slice en négatif (la vélocité baisse le
     numéro de slice) et profondeur d'un LFO S&H sur la slice en positif
     (round-robin plus large quand on frappe fort).
  3. Second LFO S&H minuscule sur TUNE et PAN.
  4. MW → bascule de banque vers des versions saturées du même fût.
- **Chez nous** : percs 4 et 5 ; [[elektronauts-velocite-macros]].

## Liens

[[elektronauts-panorama]] · [[elektronauts-ctrl-all]] ·
[[elektronauts-presets-pool]] · [[elektronauts-velocite-macros]] ·
[[../projet-sauvegarde]] · [[../presets-kits-pool]] · [[../machines-src]]
· [[../../doctrine]] §1, §2, §3, §13
