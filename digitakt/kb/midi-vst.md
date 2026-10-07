---
tags: [digitakt, kb]
theme: Tracks MIDI vers des synthés VST (acid, accords)
lot: 5
ordre: 33
manuel: "§16.3, A.2.7, §14.4, §14.6.3 (p79-80, 87, 101-103)"
os: "1.17"
statut: draft
---

# Tracks MIDI vers des synthés VST : ligne acid et accords

**En une phrase** : une track MIDI de la DT2 séquence un synthé logiciel
sur le Mac par USB ; c'est la voie pour une vraie ligne acid (émulation
303) sur la track 10 et pour les accords polyphoniques du §11, que les
tracks audio (monophoniques) ne jouent pas.

## Gestes rapides

| Action | Où |
|---|---|
| Track en machine MIDI, canal | `[FUNC] + [SRC]` > MIDI ; `[SRC]` `CHAN` (cf. [[tracks-midi]]) |
| MIDI vers le Mac | PORT CONFIG : `OUTPUT TO` = USB (ou MIDI+USB) |
| Côté DAW | entrée MIDI « Digitakt II », piste du synthé VST sur le même canal |
| Accord jusqu'à 4 notes | page TRIG 1, `NOT2`-`NOT4` |
| Cutoff, résonance, accent | `[FLTR]` VAL1-8 sur les CC du VST (MIDI learn côté DAW) |
| Retour du son | interface audio du Mac, ou `USB IN` = MAIN en mode `USB AUDIO/MIDI` (cf. [[audio-routing-overbridge]]) |

## Pas à pas : ligne acid sur la track 10

1. Track 10 en machine MIDI, `CHAN` = 10 ; dans le DAW, une émulation 303
   en écoute sur le canal 10.
2. `[FLTR]` : VAL1 = CC du cutoff, VAL2 = CC de la résonance (activer avec
   `[FUNC]` + knob) ; MIDI learn côté VST.
3. KEYBOARD SETUP de la track en PHRYGIAN sur la note du kick (cf.
   [[keyboard-gammes]]), puis notes en GRID ou en LIVE REC.
4. Accents : `VEL` haute sur quelques trigs (si le VST mappe la vélocité sur
   l'accent). Slides : `LEN` qui chevauche la note suivante (legato,
   *à vérifier selon le VST*).
5. LFO lent sur VAL1, p-locks de VAL1 sur les trigs clés : la ligne
   « s'ouvre » sur 16 ou 32 mesures (doctrine §6, principe 2).

## Pas à pas : nappe d'accords sur la track 11

1. Track 11 en MIDI vers un synthé polyphonique VST (pad, reverb longue).
2. Accord mineur 7 : `NOT2` = +3, `NOT3` = +7, `NOT4` = +10.
3. Un trig long toutes les 2 ou 4 mesures, note lockée par trig :
   progression i7 → IV7 du §11 (dorien).

## En live techno

- La track MIDI **garde son rôle** dans la grille (10 = lead, 11 = atmo) :
  mutes et fills restent les mêmes réflexes (cf. [[tracks-midi]]).
- Le son VST revient par le Mac : il ne passe ni par les effets ni par le
  compresseur de la DT2, donc pas de ducking par le kick ; le sidechain se
  fait dans le DAW.
- Préparer les presets VST par morceau et les rappeler par program change
  (`PROG` locké sur le premier trig).

## Pièges

- Le réglage `USB IN` n'est proposé qu'en `USB AUDIO/MIDI`, mais le manuel
  prévoit le sampling `SRC` = USB « using Overbridge » : l'audio du Mac
  atteint donc la DT2 dans les deux modes. *À vérifier* : si, en mode
  `OVERBRIDGE`, ce retour sort aussi au main de la DT2 (sinon, faire sortir
  le VST par l'interface du Mac ; cf. [[overbridge-live-vst]]).
- Pas de page FX ni de troisième LFO sur une track MIDI.
- La latence du VST décale la ligne acid par rapport au kick : compenser
  dans le DAW ou par le microtiming de la track (cf.
  [[microtiming-retrigs]]).
- Plugins payants (Acid V) ou gratuits (comparatif ci-dessous) : à choisir
  avant de figer le kit.

## À essayer (5 min)

Track 10 vers une 303 VST, 16 trigs en PHRYGIAN, VAL1 sur le cutoff avec un
LFO triangle sur 4 mesures ; muter et démuter la 10 sur le 1 de chaque
phrase pour vérifier la latence à l'oreille.

Source : manuel DT2 OS 1.17, §16.3, A.2.7, §14.4, §14.6.3.

## Vidéos

Ajoutées depuis [[../veille-live]] (2026-10-07), non visionnées.

- [Digitakt — the MIDI tracks](https://www.youtube.com/watch?v=ZyFY0o44DK8) (vidéo entière) · DT1
- [Sequencing MIDI on the Digitakt? As good as a software DAW?](https://www.youtube.com/watch?v=6qn-KMwLjj8) (vidéo entière) · DT1
- [The best free TB-303 / acid plugin? 5 of the best, reviewed](https://www.youtube.com/watch?v=sptDyCMqq8o) (vidéo entière) · VST
- [Découverte du plugin Acid V — Arturia (émulation TB-303)](https://www.youtube.com/watch?v=zseHGJg1ugI) (vidéo entière) · VST payant, FR
- [How to make a TB-303 acid line in Ableton Live (stock plugin)](https://www.youtube.com/watch?v=P_gpsUKY3ng) (vidéo entière) · Ableton
