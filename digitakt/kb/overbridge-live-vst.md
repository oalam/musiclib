---
tags: [digitakt, kb]
theme: Overbridge en live (multipiste, VST par track)
lot: 5
ordre: 32
manuel: "§6.6, §13.1.1, §14.6.3, §14.6.4, §14.8.1 (p20, 68, 80-83)"
os: "1.17"
statut: draft
---

# Overbridge en live : multipiste et effets VST par track

**En une phrase** : en mode Overbridge, les 16 tracks arrivent séparées
dans le DAW ; on peut y ajouter des VST par track (delay dub, distorsion,
sidechain) et enregistrer le set en multipiste, au prix de la latence et
d'un Mac indispensable sur scène.

## Gestes rapides

| Action | Où |
|---|---|
| Mode Overbridge | `[SETTINGS]` > SYSTEM > USB CONFIG = `OVERBRIDGE` (cf. [[audio-routing-overbridge]]) |
| Plugin Overbridge | instancier « Digitakt II » dans le DAW (VST3 / AU), choisir les sorties à créer |
| Envoyer une track vers un VST | piste audio du DAW sur la sortie Overbridge de la track |
| Échantillonner un son du Mac | `[SAMPLING]` `SRC` = USB (cf. [[sampling-resampling]]) |
| Horloge et transport | le DAW maître, la DT2 suit (cf. [[midi-config]]) |

## Deux usages, deux réglages

| | Enregistrer le set | Jouer avec des VST |
|---|---|---|
| Ce qui sort en façade | la DT2 (sortie main), comme d'habitude | l'interface audio du Mac |
| Rôle du DAW | enregistreur 16 pistes | table de mixage + effets |
| Latence | sans importance | à mesurer, critique pour le kick |
| Risque si le Mac plante | perte de l'enregistrement seulement | silence en façade |

## Pas à pas : enregistrer le set en 16 pistes

1. USB CONFIG = `OVERBRIDGE`, Overbridge installé, DAW ouvert au tempo.
2. Plugin Digitakt II, 16 sorties de track + main, une piste
   d'enregistrement par sortie, nommées comme la grille (1 kick, 2 rumble…).
3. La façade reste branchée sur la sortie main de la DT2.
4. Enregistrer tout le set ; réécouter piste par piste (doctrine §6,
   principe 12).

## En live techno

- Le cas sûr est l'**enregistrement** : la DT2 reste autonome en façade, le
  Mac ne fait qu'écouter.
- Effets VST en jeu seulement sur les tracks **hautes** (10, 11, 12-14 :
  lead, atmo, Id, vocal), jamais sur le kick et le rumble : un retard de
  quelques ms sur le grave casse le groove.
- Un delay dub VST en envoi sur la 14 (vocal) ou la 11 (atmo) avec des coups
  de feedback en jeu : le pont dub du set (doctrine §13).
- La sortie main d'Overbridge reste disponible pour un enregistrement
  stéréo de secours en parallèle des 16 pistes.

## Pièges

- Les sorties de track Overbridge sont **sans les effets internes** (reverb,
  delay, compresseur) : le rumble resamplé passe, la reverb en direct non.
- Les trois modes USB s'excluent : en `OVERBRIDGE`, pas de class compliant.
- *À vérifier* : latence aller-retour avec l'interface du Mac (réglage du
  buffer), et stabilité du plugin Overbridge dans le DAW du projet
  (Renoise : compatibilité VST3 / AU à confirmer).
- Les vidéos DT1 montrent l'ancien Overbridge : l'interface du plugin DT2
  diffère.

## À essayer (5 min)

Enregistrer 4 minutes d'un pattern en 16 pistes, puis comparer dans le DAW
les pistes 1 (kick) et 9 (basse) sur un analyseur de spectre : c'est aussi
l'étalonnage des filtres demandé par la doctrine §9.

Source : manuel DT2 OS 1.17, §6.6, §13.1.1, §14.6, §14.8.1.

## Vidéos

Ajoutées depuis [[../veille-live]] (2026-10-07), non visionnées.

- [Elektron finally dropped Overbridge for Digitakt 2 // Ableton setup tutorial](https://www.youtube.com/watch?v=i_MjSIeomwM) (vidéo entière) · DT2, Ableton
- [Multitrack recording with Elektron Overbridge](https://www.youtube.com/watch?v=VP2HDXqbGj8) (vidéo entière) · machine non précisée
- [Recording Digitakt into Overbridge — how to control your FX](https://www.youtube.com/watch?v=Frpqf3MnPH8) (vidéo entière) · DT1
- [Configuring Overbridge for Digitakt in Logic Pro with FX](https://www.youtube.com/watch?v=EosDRHyf0Ug) (vidéo entière) · DT1, Logic
- [Using automation to control Digitakt via Ableton Live and Overbridge](https://www.youtube.com/watch?v=t7mig0QU0qI) (vidéo entière) · DT1, Ableton
