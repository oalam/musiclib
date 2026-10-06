---
tags: [digitakt, kb]
theme: Configuration MIDI (canaux, sync, import des .mid)
lot: 2
ordre: 7
manuel: "§10.2.3, §14.4 (p43, 77-79)"
os: "1.17"
statut: draft
---

# Configuration MIDI : canaux, sync, import des `.mid`

**En une phrase** : régler d'où la DT2 écoute (USB / DIN), sur quels canaux,
et qui mène l'horloge, pour rejouer les `.mid` des banks générées depuis le
Mac et les enregistrer dans les patterns.

## Gestes rapides

| Réglage | Chemin |
|---|---|
| Horloge et transport | `[SETTINGS]` > MIDI CONFIG > SYNC |
| Entrée / sortie (USB, DIN) | MIDI CONFIG > PORT CONFIG > `INPUT FROM` / `OUTPUT TO` |
| Jouer la DT2 depuis l'extérieur | PORT CONFIG > `RECEIVE NOTES` |
| Canal de chaque track | MIDI CONFIG > CHANNELS > `TRACK 1-16 CHANNEL` |
| Canal qui pilote la track active | CHANNELS > `AUTO CHANNEL` |

## Pas à pas : enregistrer un `.mid` de bank

1. USB entre Mac et DT2. PORT CONFIG : `INPUT FROM` = USB (ou MIDI+USB),
   `RECEIVE NOTES` = on.
2. SYNC : `CLOCK RECEIVE` et `TRANSPORT RECEIVE` = on si le Mac mène le
   tempo (lecteur MIDI ou DAW réglé au BPM de la bank).
3. Méthode sûre, **une track à la fois** : sélectionner la track
   (`[TRK] + [TRIG n]`), router la piste `n` du `.mid` sur l'**AUTO
   CHANNEL**, `[RECORD] + [PLAY]`, lancer la lecture côté Mac.
4. Vérifier en GRID, recaler si besoin (cf. [[enregistrement-quantize]]),
   sauver.

## En live techno

- Les `.mid` générés mettent la track `n` sur le canal `n` (doctrine §7) et
  les drums sur la note 60. Le manuel ne dit pas que la DT2 **enregistre**
  les notes reçues sur les canaux de track : il décrit l'enregistrement
  externe via l'AUTO CHANNEL vers la track active. *À vérifier* : envoyer le
  `.mid` complet en LIVE RECORDING et voir si les 16 tracks s'écrivent.
- *À vérifier* aussi : quelle note joue un sample à sa hauteur d'origine
  sur une track audio (60 supposé par `digitakt.py`).
- `PRG CH RECEIVE` permet de changer de pattern depuis l'extérieur (program
  change), utile plus tard pour piloter la chaîne d'une bank.

## Pièges

- `OUTPUT TO` = MIDI+USB bride la vitesse USB : USB seul pour les gros
  transferts.
- Les canaux de track (CHANNELS) servent aux **paramètres** ; les notes d'une
  track MIDI partent sur le `CHAN` de sa page SRC.
- Horloge reçue + horloge envoyée sur le même câble = boucle : n'activer
  qu'un sens.

## À essayer (5 min)

Exporter `p01.mid` d'une bank, router la piste du kick sur l'AUTO CHANNEL,
enregistrer en LIVE sur la track 1. Puis tester l'envoi des 16 canaux d'un
coup et noter le résultat ici (passer `statut` à `vérifié`).

Source : manuel DT2 OS 1.17, §10.2.3, §14.4.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [Optoproductions — Digitakt 2 MIDI Setup](https://youtu.be/noEAqTsXL8M) (vidéo entière) · DT2, 2024
- [EZBOT — The Elektron MIDI Syncing Guide](https://youtu.be/i69tj48vfxM?t=173) : « What is Auto Channel? » (2:53) · Elektron, générique, 2023
- [Synthackers — Mastering Recording Modes](https://youtu.be/VOXnpUoH_nQ?t=1070) : « Using an External Keyboard » (17:50) · DT2, 2024
- [loopop — DIGITAKT II vs OG Digitakt, detailed tutorial](https://youtu.be/nepWmWsq84g?t=1330) : « MIDI learn » (22:10) · DT2, 2024
