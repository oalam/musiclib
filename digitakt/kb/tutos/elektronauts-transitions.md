---
tags: [digitakt, kb, tutos]
theme: Transitions entre patterns, LAST, note tenue (Elektronauts)
lot: 2
ordre: 10
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
auteur: communauté Elektronauts
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-23
---

# Elektronauts 10 — Transitions entre patterns

**En une phrase** : les conditions `LAST` et `/LAST` ne jouent que quand un
autre pattern est cué, une note tenue traverse le changement de pattern, et
une chaîne de patterns courts avec fills de 8 pas fait une montée ; le
changement de pattern cesse d'être une coupure.

Panorama : [[elektronauts-panorama]]. Fiches du geste :
[[../fill-conditions]], [[../patterns-chaines]], [[../song-mode]],
[[../midi-config]].

## Sur notre grille

Les FX de transition vivent sur la 15 ([[../../doctrine]] §5) ; la note
tenue à travers le changement sert sur l'atmo 11 et la basse 9.

## Astuces

### 1. Les nouvelles conditions

- **Source** : [#78](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/78).
- **Résultat** : un trig qui ne joue qu'à l'annonce du prochain pattern, ou
  qui se tait un tour sur B.
- **Pas à pas** :
  1. Tenir un trig, encodeur de condition : `/A:B` (se tait au tour A tous
     les B), `LAST` (joue seulement quand un autre pattern est cué),
     `/LAST` (l'inverse).
  2. Conditions, probabilité et FILL se cumulent en ET.
  3. La probabilité de track ne fait pas partie du calcul : la locker sur le
     trig si besoin.
- **Chez nous** : riser sur la 15 en `LAST`, downlifter en `/LAST` sur le
  pattern suivant ([[../fill-conditions]]).

### 2. Laisser sonner à travers le changement

- **Source** : [#375](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/375).
- **Résultat** : une nappe ou une basse qui ne se coupe pas au changement
  de pattern.
- **Pas à pas** :
  1. Sur la track : dernier trig du pattern avec `NOTE` tenue, longueur
     maximale, enveloppe **AHD** et non ADSR.
  2. Le son continue dans le nouveau pattern jusqu'au prochain trig de sa
     track.
  3. Werp, Repitch et Stretch adoptent le nouveau tempo ; les paramètres
     touchés sautent à la valeur de la nouvelle track.
  4. Garder des réglages proches d'un pattern à l'autre sur cette track.
  5. Transition simple : `LAST` + un resample de la phrase sur la 16.
- **Chez nous** : atmo 11, basse 9.

### 3. Chaîne de patterns de montée

- **Source** : [#222](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/222).
- **Pas à pas** :
  1. Patterns de 56 pas chaînés, chacun suivi d'un fill de 8 pas.
  2. Pendant la chaîne : CTRL-ALL sur loop, tune, slot, longueur, note,
     probabilité et filtres ([[elektronauts-ctrl-all]]).
- **Chez nous** : montée pas à pas de la doctrine §4 et
  [[../patterns-chaines]].

### 4. Ableton et program changes

- **Source** : [#224](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/224).
- **Pas à pas** :
  1. Clips de program change dans Live, sans quantisation globale.
  2. Quantisation de Live égale à la longueur maître du pattern.
  3. Les scènes partent avec le pattern.
- **Chez nous** : [[../midi-config]] ; hors scope du live one-box.

## Liens

[[elektronauts-panorama]] · [[elektronauts-ctrl-all]] ·
[[../fill-conditions]] · [[../patterns-chaines]] · [[../song-mode]] ·
[[../midi-config]] · [[../../doctrine]] §4, §5
