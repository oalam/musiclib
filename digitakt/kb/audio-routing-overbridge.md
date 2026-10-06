---
tags: [digitakt, kb]
theme: Audio routing et Overbridge
lot: 5
ordre: 25
manuel: "§6.6, §6.8, §14.6, §14.8.1 (p20, 80-83)"
os: "1.17"
statut: draft
---

# Audio routing et Overbridge

**En une phrase** : choisir quelles tracks sortent sur le main et passent
par les FX, et quoi envoyer au Mac par USB : le mix stéréo, une ou deux
tracks isolées, ou toutes les tracks séparées avec Overbridge.

## Gestes rapides

| Réglage | Chemin |
|---|---|
| Mode USB (un seul à la fois) | `[SETTINGS]` > SYSTEM > USB CONFIG : `OVERBRIDGE` / `USB MIDI` / `USB AUDIO/MIDI` |
| Tracks et FX envoyés au main | AUDIO ROUTING > `TO MAIN` (`[YES]`, touches vertes = envoi) |
| Tracks envoyées aux FX | AUDIO ROUTING > `TO FX` |
| Ce qui part vers le Mac (class compliant) | AUDIO ROUTING > `USB OUT` : `MAIN`, `L:T / R:T`, `EXT`, `OFF` |
| Ce qui arrive du Mac | AUDIO ROUTING > `USB IN` : `MAIN` / `OFF` |
| Son interne coupé pendant le streaming | AUDIO ROUTING > `INT TO MAIN` : `OFF` / `ON` / `AUTO` |
| Gain du retour USB / pré ou post fader | `USB TO MAIN` (0 à +18 dB), `PRE/POST FADER` |

`USB OUT` par track : appuyer deux fois sur une touche `[TRIG]` = cette
track seule en stéréo (blanche) ; une touche puis une autre = deux tracks
en mono, gauche (bleue) et droite (rouge).

## Pas à pas : s'enregistrer pour réécouter (doctrine §6, conseil 12)

1. Mix seul, sans logiciel Elektron : USB CONFIG = `USB AUDIO/MIDI`,
   `USB OUT` = `MAIN`, `INT TO MAIN` = `ON` pour garder le son au casque.
2. Sur le Mac, enregistrer l'entrée « Digitakt II » dans n'importe quel
   enregistreur ou DAW.
3. Tracks séparées : USB CONFIG = `OVERBRIDGE`, installer Overbridge
   (site Elektron), enregistrer les 16 tracks sur 16 pistes du DAW.
4. Réécouter : parties trop longues, transitions ratées, sons qui se
   marchent dessus.

## En live techno

- Overbridge multipiste = vérifier piste par piste la place de chaque
  rôle de la grille (kick et basse qui se marchent dessus, cf. doctrine
  §1).
- `USB OUT` en `L:T1 / R:T9` : kick à gauche, basse à droite, pour
  analyser leur conflit dans un outil du Mac.
- `TO FX` : retirer kick, rumble et basse des FX garde le bas du spectre
  sec, même si un send est monté par erreur (cf. [[send-fx-compresseur]]).
- `USB IN` = `MAIN` : un son du Mac (synthé logiciel piloté par une track
  MIDI, cf. [[tracks-midi]]) sort par la DT2.

## Pièges

- Les trois modes USB s'excluent : en `OVERBRIDGE`, pas de class compliant,
  et inversement.
- `USB IN`, `USB OUT` et `INT TO MAIN` n'existent qu'en `USB AUDIO/MIDI`.
- `INT TO MAIN` = `AUTO` coupe le main **pendant** le streaming : silence en
  façade si un enregistrement tourne pendant le set.
- Les sorties de track USB / Overbridge sont **sans effets**.
- Une track retirée de `TO MAIN` sort quand même dans Overbridge.

## À essayer (5 min)

`USB AUDIO/MIDI`, `USB OUT` = `MAIN`, `INT TO MAIN` = `ON` : enregistrer 2
minutes d'un pattern sur le Mac, puis repasser en `L:T1 / R:T9` et
comparer kick et basse.

Source : manuel DT2 OS 1.17, §6.6, §6.8, §14.6, §14.8.1.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [Synthackers — Digitakt II Now Has Overbridge!](https://youtu.be/ghWoEDlLwKA) (vidéo entière) · DT2, 2024
- [Synthackers — Digitakt II Now Has Overbridge!](https://youtu.be/ghWoEDlLwKA?t=1441) : « DAW: Multitracking Seperate Tracks » (24:01) · DT2, 2024
- [Synthackers — Digitakt II Now Has Overbridge!](https://youtu.be/ghWoEDlLwKA?t=2072) : « Routing Audio From DAW Into Digitakt II » (34:32) · DT2, 2024
- [Zonal Audio — The Big Elektron Overbridge Tutorial, multitrack](https://youtu.be/NYLRBTIsoDo) (vidéo entière) · DT2, 2026
- [XNB — DIGITAKT II Sampling](https://youtu.be/tDBeHZV-qnU?t=659) : « External Mixer » (10:59) · DT2, 2024
