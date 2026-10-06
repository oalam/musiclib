---
tags: [digitakt, kb]
theme: Mutes (globaux / de pattern)
lot: 4
ordre: 21
manuel: "§8.5.3 (p26-27)"
os: "1.17"
statut: draft
---

# Mutes (globaux / de pattern)

**En une phrase** : en mode MUTE, les 16 touches `[TRIG]` coupent ou
rétablissent les 16 tracks ; en mute global la coupure vaut pour tous les
patterns, en mute de pattern pour le seul pattern actif.

## Gestes rapides

| Action | Touches |
|---|---|
| Entrer / sortir du mute global (touches vertes) | `[FUNC] + [TRK]` |
| Entrer dans le mute de pattern (touches magenta) | `[FUNC]` + double appui `[TRK]` |
| Couper / rétablir une track | `[TRIG 1-16]` (allumée = joue, éteinte = coupée) |
| Préparer plusieurs mutes d'un coup | en mode MUTE, maintenir `[FUNC]` + `[TRIG]`, lâcher `[FUNC]` pour appliquer |
| Quick mute (sans entrer dans le mode) | maintenir `[FUNC]` + touches de track *(touches exactes à vérifier)* |

Écran en préparation : carré = joue, trait = coupée, `+` = va revenir,
`X` = va être coupée. `[FUNC] + [TRK]` rouvre le dernier mode utilisé
(global ou pattern), quick mute compris.

## Pas à pas : break puis retour du kick

1. `[FUNC] + [TRK]` : mute global (vert).
2. En fin de phrase, maintenir `[FUNC]` et taper `[TRIG 1]`, `[TRIG 2]`,
   `[TRIG 9]` (kick, rumble, basse) : trois `X` à l'écran.
3. Lâcher `[FUNC]` sur le 1 de la phrase : les trois tombent ensemble.
4. Laisser tourner atmo et Id1, riser sur la 15.
5. Maintenir `[FUNC]`, retaper 1, 2, 9 (`+`), lâcher sur le 1 suivant : le
   kick revient avec la basse.

## En live techno

- C'est le cœur du jeu selon la doctrine (§4) : un pattern plein + un ordre
  de mutes = un morceau. La partition de mutes de chaque note de bank
  (`library/digitakt/<slug>.md`) donne l'ordre d'entrée des tracks.
- La grille invariante rend les gestes réflexes : rangée du haut (1-8) =
  corps rythmique, rangée du bas (9-16) = tête. Couper une rangée entière =
  break percussif ou mélodique.
- Mute **global** pour le jeu : il suit d'un pattern à l'autre, le kick reste
  coupé si on bascule pendant un break.
- Mute **de pattern** pour la préparation : il est enregistré avec le
  pattern, donc chaque pattern démarre avec ses tracks d'entrée déjà
  coupées (ex. intro = kick seul).
- La préparation `[FUNC]` maintenu est la seule façon de faire tomber 3
  tracks pile ensemble.

## Pièges

- Mutes globaux sauvés avec le **projet**, mutes de pattern avec le
  **pattern** : un mute global oublié coupe la track partout au prochain
  chargement.
- Une track coupée dans les deux modes clignote en magenta dans les deux.
- Une track coupée qui a des trigs clignote : repère utile pour savoir ce
  qui attend d'entrer.
- En SONG mode, les mutes de ligne reprennent les mutes du pattern (cf.
  [[song-mode]]).

## À essayer (5 min)

Pattern plein, mute de pattern sur tout sauf le kick, sauvegarder ; puis en
mute global, dérouler la montée de la doctrine §4 en préparant chaque
entrée avec `[FUNC]` maintenu et en lâchant sur le 1.

Source : manuel DT2 OS 1.17, §8.5.3.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [Synthackers — How to Use Mute Modes on Digitakt II for Live Performance](https://youtu.be/-JVdETENNyo) (vidéo entière) · DT2, 2025
- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=3359) : « Mute mode » (55:59) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=3866) : « The two mute modes » (1:04:26) · DT2, 2024
- [loopop — DIGITAKT II vs OG Digitakt, detailed tutorial](https://youtu.be/nepWmWsq84g?t=1030) : « Prepare mutes » (17:10) · DT2, 2024
