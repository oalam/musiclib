---
tags: [digitakt, kb, tutos]
theme: Resampling stéréo et fondu entre original et resample (Elektronauts)
lot: 2
ordre: 4
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
auteur: communauté Elektronauts
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-24
---

# Elektronauts 4 — Resampling stéréo et fondu

**En une phrase** : un resample du main posé sur une track mutée donne une
version « mangée » de tout le pattern, et un LFO3 arrêté sur le volume de
toutes les tracks, piloté en CTRL-ALL, fait office de crossfader d'Octatrack
entre le pattern et son resample.

Panorama : [[elektronauts-panorama]]. Fiches du geste :
[[../sampling-resampling]], [[../live-looping]], [[../lfo]], [[../filtres]].

## Sur notre grille

Le resample vit sur la 16 (réserve, [[../../doctrine]] §1), track mutée par
défaut. Le fondu exclut le kick 1 et le rumble 2 si l'on veut garder le
grave stable, ou les inclut pour un vrai break.

## Astuces

### 1. Resample du main en une touche

- **Source** : [#76](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/76).
- **Résultat** : une boucle d'une mesure de tout le pattern, prête sur une
  track mutée, à ramener en prep mute ou en fill.
- **Pas à pas** :
  1. Page SAMPLING : source **MAIN L/R**, longueur = celle du pattern,
     REC START sur le 1 du pattern.
  2. Armer, lancer : la mesure s'enregistre avec les FX.
  3. Assigner le sample à la 16 (mutée), machine Grid, trigs déjà posés
     sur les 16 pas (ou un seul trig de longueur maximale).
  4. En jeu : prep mutes pour basculer vers la seule 16 et revenir, ou la
     démuter en fill sur la dernière mesure.
- **Chez nous** : la 16 est la réserve ; exercice 2 du panorama.

### 2. LFO3 comme crossfader

- **Source** : [#88](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/88), variante filtre [#208](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/208).
- **Résultat** : un seul encodeur fond entre le pattern et son resample.
- **Pas à pas (volume)**, corrigé et **vérifié à la machine le 2026-10-24**
  (OS 1.17, la 16 monte pendant que les 1 à 14 descendent) :
  1. Un LFO immobile sort une valeur constante : sur chaque track, LFO3 →
     **AMP VOL**, vitesse nulle, onde carrée, phase de départ sur le haut
     de l'onde (sortie +1). La profondeur devient un décalage de volume.
  2. Sur la 16 (resample) : même LFO3 mais **phase décalée d'une
     demi-période** (`SPH` 64 sur une échelle 0-127), sortie -1. Contrôle :
     profondeur +20 provisoire, la 16 doit **baisser** ; remettre près de
     zéro. AMP VOL de la 16 assez bas pour qu'elle soit muette au repos.
  3. Profondeur de repos **0.01** sur toutes les tracks concernées (une
     track à zéro ne suit pas le geste ; le signe n'a aucun rôle).
  4. CONTROL ALL CONFIG : cocher 1 à 14 et la 16 (décocher 1 et 2 pour
     garder le grave).
  5. `[TRK]` tenu + profondeur de LFO3 vers le **négatif** : les 1 à 14
     descendent, la 16 monte. Repos = zéro. L'autre sens ne fait rien
     d'utile (les 1 à 14 sont au plafond, la 16 déjà muette).
- **Attention** : le post [#88](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/88)
  propose des profondeurs de signes opposés (-0.01 sur la 16, +0.01
  ailleurs) avec la même onde. À la machine (OS 1.17) le CTRL-ALL est
  additif et pousse toutes les profondeurs dans le même sens : d'un côté
  les deux sons, de l'autre aucun. L'inversion doit venir de la **phase**
  du LFO de la 16, pas du signe de sa profondeur. Vérifié : avec la phase
  décalée, la 16 monte bien pendant que les autres descendent.
- **Pas à pas (filtre)** :
  1. Resample en passe-haut fermé (fréquence basse), les autres tracks en
     passe-bas ouvert.
  2. `[TRK]` tenu + `FREQ` : les deux filtres se croisent, le resample
     s'ouvre quand le pattern se ferme.
- **Attention** : une boucle en lecture infinie survit à un changement de
  pattern tant qu'aucun trig ne retombe sur sa track.

### 3. Enregistrer une boucle externe avec ses queues

- **Source** : [#93](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/93), variante interne [#149](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/149).
- **Résultat** : une phrase externe (ou interne) capturée avec ses queues de
  reverb et de delay, sans couper la fin.
- **Pas à pas (externe)** :
  1. DT2 maître de l'horloge.
  2. Page SAMPLING : **PREROLL** = longueur du pattern externe, métronome
     actif, REC START = PLAY, longueur voulue.
  3. ARM, puis `[REC] + [PLAY]` : la machine externe tourne pendant le
     preroll, l'enregistrement part à la fin et prend les queues.
- **Pas à pas (interne)** :
  1. Doubler la longueur du pattern, laisser les pages ajoutées vides.
  2. Page loop sur les pages vides (`[PAGE]` tenu + touches 9 à 16).
  3. Enregistrer : seules les queues de FX sonnent dans la boucle.

### 4. Boucle de nappe sans clic

- **Source** : [#540](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/540), variante ping-pong [#551](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/551).
- **Résultat** : une nappe qui boucle proprement, resamplée depuis deux
  tracks qui se relaient.
- **Pas à pas** :
  1. Même sample sur deux tracks (13 et 14 par exemple), un trig de
     longueur 128 sur chacune.
  2. Condition `1:2` sur la première, `2:2` sur la seconde.
  3. Régler le release de l'AMP pour que la fin de l'une couvre le départ
     de l'autre.
  4. Resampler deux cycles ; couper le resample au milieu : la jonction
     tombe dans le recouvrement.
- **Variante** : LFO carré sur PLAY MODE, profondeur autour de 1.8 : la
  lecture inverse son sens au lieu de sauter, moins d'artefacts.
- **Chez nous** : atmo 11 ([[../../doctrine]] §1).

## Liens

[[elektronauts-panorama]] · [[elektronauts-ctrl-all]] ·
[[../sampling-resampling]] · [[../live-looping]] · [[../lfo]] ·
[[../filtres]] · [[../mutes]] · [[../../doctrine]] §1, §4
