---
tags: [digitakt, kb]
theme: CC et NRPN
lot: 5
ordre: 23
manuel: "annexe B, §14.4.2, §14.4.3, §14.5 (p77-79, 109-113)"
os: "1.17"
statut: draft
---

# CC et NRPN

**En une phrase** : chaque paramètre de la DT2 a un numéro CC (7 bits) et
un numéro NRPN (plus fin) : la machine les envoie quand on tourne un knob
et les reçoit pour être pilotée ou automatisée depuis le Mac.

## Gestes rapides

| Réglage | Chemin |
|---|---|
| Recevoir CC / NRPN | `[SETTINGS]` > MIDI CONFIG > PORT CONFIG > `RECEIVE CC/NRPN` |
| Type envoyé par les knobs | PORT CONFIG > `PARAM OUTPUT` = `CC` ou `NRPN` |
| Les knobs envoient-ils du MIDI | PORT CONFIG > `ENCODER DEST` = `INT` / `INT + EXT` |
| Les mutes envoient-ils du MIDI | PORT CONFIG > `MUTE DEST` |
| Canal de chaque track (paramètres) | MIDI CONFIG > CHANNELS > `TRACK 1-16 CHANNEL` |
| Canal des FX send, compresseur, overdrive master | CHANNELS > `FX CONTROL CH` |

## Numéros utiles en live (annexe B)

Paramètres de track, sur le canal de la track. NRPN noté MSB:LSB.

| Paramètre | CC | NRPN |
|---|---|---|
| Mute de track | 94 | 1:101 |
| Niveau de track | 95 | 1:100 |
| Fréquence du filtre | 74 | 1:20 |
| Résonance (knob F du filtre, selon le type) | 75 | 1:21 |
| Profondeur d'enveloppe du filtre | 77 | 1:23 |
| Decay d'amp | 81 | 1:32 |
| Volume d'amp | 89 | 1:39 |
| Pan | 90 | 1:38 |
| Send delay / reverb / chorus | 84 / 85 / 12 | 1:36 / 1:37 / 1:35 |
| Profondeur LFO 1 (CC haute résolution, LSB 59) | 109 | 1:49 |
| Note / vélocité / longueur de trig (valeur par défaut) | 3 / 4 / 5 | 3:0 / 3:1 / 3:2 |
| Mute de pattern | 110 | 1:104 |

Sur `FX CONTROL CH` : overdrive master CC 17 (NRPN 2:37), délai (CC
21-28, NRPN 2:0-2:7), reverb (CC 29-31, 89-92, NRPN 2:8-2:15).

## Pas à pas : piloter le filtre du kick depuis le Mac

1. PORT CONFIG : `INPUT FROM` = USB, `RECEIVE CC/NRPN` = on.
2. CHANNELS : `TRACK 1 CHANNEL` = 1 (garder track n = canal n, cohérent avec
   les `.mid` de bank, cf. [[midi-config]]).
3. Côté Mac (mido) : `control_change` canal 1, CC 74, valeur 0 à 127.
4. Pour plus de finesse : NRPN = CC 99 (MSB) = 1, CC 98 (LSB) = 20, puis
   CC 6 / CC 38 pour la valeur.

## Phase 7.E : ce que les NRPN permettent ou non

- **Aucun NRPN ne pose un trig sur un pas** : les NRPN 3:0 à 3:2 changent la
  note, la vélocité et la longueur **par défaut** de la track, comme les
  knobs de la page TRIG.
- Remplir un pattern depuis le Mac passe donc par l'enregistrement en live
  de notes MIDI (une track à la fois, cf. [[midi-config]]).
- Les CC / NRPN servent à **préparer les sons** (niveaux, filtres, sends,
  mutes) et à **automatiser** depuis un script.
- Piste non explorée : le SYSEX DUMP (§14.5) envoie et reçoit des patterns
  entiers, mais le format n'est pas documenté dans le manuel.

## En live techno

- `MUTE DEST` = `INT + EXT` : les mutes joués sur la DT2 sortent en MIDI, de
  quoi les enregistrer côté Mac et relire sa propre partition de mutes.
- Un contrôleur à faders en CC 95 sur les canaux 1-16 = une table de mixage
  des 16 tracks.

## Pièges

- `ENCODER DEST` = `INT` par défaut : les knobs n'envoient rien.
- Une track sur `OFF` dans CHANNELS n'envoie ni ne reçoit de paramètres.
- `OUTPUT TO` = `MIDI+USB` ralentit l'USB : rester sur `USB` pour les gros
  envois.
- Texte de l'annexe B extrait du PDF : certaines lignes ont des colonnes
  vides ou des doublons (Env. Delay et Env. Depth tous deux en 1:23). Tester
  chaque numéro avant de l'utiliser dans un script.
- CC 17 = Play Mode sur le canal d'une track, overdrive master sur
  `FX CONTROL CH` : ne pas mettre les deux sur le même canal.

## À essayer (5 min)

`ENCODER DEST` = `INT + EXT`, `PARAM OUTPUT` = `NRPN`, ouvrir un moniteur
MIDI sur le Mac (ou `mido` en écoute) et tourner le filtre du kick : relever
les messages et les comparer au tableau.

Source : manuel DT2 OS 1.17, annexe B, §14.4.2, §14.4.3, §14.5.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [Optoproductions — Digitakt 2 MIDI Setup](https://youtu.be/noEAqTsXL8M?t=355) : « Naming Parameters » (5:55) · DT2, 2024
- [Optoproductions — Digitakt 2 MIDI Setup](https://youtu.be/noEAqTsXL8M?t=542) : « CC Issue » (9:02) · DT2, 2024
- [loopop — DIGITAKT II vs OG Digitakt, detailed tutorial](https://youtu.be/nepWmWsq84g?t=1390) : « Name CCs » (23:10) · DT2, 2024
- [Synthackers — Digitakt II Now Has Overbridge!](https://youtu.be/ghWoEDlLwKA?t=2155) : « DAW Automation for Digitakt II » (35:55) · DT2, 2024
- [XNB — Elektron DIGITAKT MIDI Tracks deep dive](https://youtu.be/ZTFFs89y5gg?t=650) : « CC's » (10:50) · DT1 : 8 tracks MIDI dédiées, sur DT2 toute track peut l'être, 2023
