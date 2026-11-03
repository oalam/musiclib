---
tags: [digitakt, kb, tutos]
theme: Grave sur Mac, ch. 3, tuto kick : Drumsynth, Kick 3 par couches, Vital de A à Z, chaîne de sortie commune, validation
lot: 4
ordre: 3
source: "échange de travail du 2026-10-29 (stack retenue) ; chapitre détaché du tuto le 2026-10-31"
auteur: Tom (stack), rédaction à vérifier dans Reaper
modele: DT2
os: "1.17"
stack: [Reaper, Vital, Maschine Drumsynth Kick, Kick 3, iZotope Trash Lite, SPAN, ReaComp, Acid V]
parent: maison-sounddesign-grave-reaper
statut: draft
updated: 2026-10-31
---

# Grave sur Mac, ch. 3 — Le kick, trois recettes et une chaîne

Chapitre 3 du tuto « sound design préparatoire » (lot 4 de [[_index]]).
Le hub [[maison-sounddesign-grave-reaper]] porte les arbitrages (§0), la stack et
les notions Reaper (§1), les pièges (§8) et les exercices (§9). Les numéros
de section sont ceux du tuto entier : un renvoi « §n » vise le chapitre n,
avec le lien de sa fiche quand ce n'est pas celle-ci.

## 3. Tuto kick : trois recettes, une chaîne

Objectif commun : un kick **accordé** (note lue sur la queue), de
**longueur choisie au tempo**, exporté sec avec de la marge (crête -3 à
-6 dBFS, la DT2 a son propre overdrive). Trois longueurs selon
l'architecture :

| Architecture | Longueur de la queue (à -24 dB) | Exemple à 165 BPM (temps = 364 ms) |
|---|---|---|
| kick + basse (tribe, le « tok ») | moins d'un quart du temps | 60-80 ms, sub à -13 dB, médiums 300 Hz-3 kHz (Tekotak, KT23) |
| kick + rumble | 150-300 ms, sub de la queue coupé avant la reverb | 130-200 ms (40-60 % du temps) |
| kickbass | plus de la moitié du temps, jusqu'au kick suivant | [[maison-grave-rumble]] §4 |

### 3.1 Recette A, Drumsynth Kick (le kick tribe en cinq minutes)

1. Reaper : piste KICK, insérer le plug-in Maschine 2, groupe A, pad 1 en
   **Drumsynth > Kick**, moteur **Sub** (sinus, les paramètres de base sont
   Tune, Decay et Bend) ; item MIDI quatre noires sur la note du pad.
2. **Tune** jusqu'à lire la tonique sur SPAN dans la queue (F#1 = 46,2 Hz,
   G1 = 49 Hz, A1 = 55 Hz, table complète dans KT5).
3. **Decay** à la longueur visée (lire la forme d'onde dans Reaper après un
   rendu, ou SPAN en maintien de crête).
4. **Bend** (l'enveloppe de pitch) : faible pour un kick-sub, fort pour un
   thump ; c'est le réglage qui décide si on entend une note ou un coup.
5. Moteur **Tronic** pour une version avec gain et tone intégrés (kick déjà
   sale, bon départ pour la hard techno), **Dusty** pour un kick rauque avec
   bruit et filtre haut (le « tok » tribe) ; les autres moteurs à écouter
   (noms et pages de paramètres à vérifier dans le manuel Maschine, section
   Drum Synths > Kick).
6. Rendu ([[maison-grave-rendu-dt2]] §7). Un Drumsynth sonne rapidement mais ne dessine pas la courbe
   de pitch : quand le kick doit tenir une note (kickbass), passer à B ou C.

### 3.2 Recette B, Kick 3 (le kick de référence de la bank)

0. **Savoir ce qu'un preset d'usine apporte.** Les presets livrés
   arrivent avec leur EQ (entailles étroites dans le corps, par exemple
   179 Hz à -6 dB avec Q 4 sur `tom1`), leur section Effects (trois drives
   empilés) et leur **limiteur actif**, qui plafonne à 0 dBFS en interne.
   Le limiteur est une couleur comme une autre, à garder si elle plaît
   (c'est le cas sur `tom1`, 2026-10-30) ; la seule règle est la marge :
   le fader OUT de Kick 3 est **après** le limiteur, le baisser jusqu'à une
   crête de -6 dBFS dans SPAN garde la couleur et laisse la place à
   l'overdrive de la DT2. Pour régler l'étage Trash du [[maison-grave-projet-reaper]] §2.4, couper Effects
   le temps du réglage, afin de juger une saturation à la fois, puis les
   réintroduire. Le champ KEY du panneau Export est une transposition, pas
   la note de la queue : la note juste reste celle lue dans SPAN.
1. Piste KICK, Kick 3, preset init. Première couche en **sub synthétisé** :
   dessiner l'enveloppe de pitch avec deux ou trois points : départ une à
   deux octaves au-dessus (+24 à +36 demi-tons, la recette Koçer dans
   [[../../../technique/anatomie-kick]]), chute en 10-20 ms pour un click intégré, 40-60 ms
   pour un thump, point d'arrivée **sur la tonique**, affichée par le
   plug-in sur le dernier point.
2. Enveloppe de volume de la même couche : plateau court puis descente ;
   lire la longueur en ms et la caler sur la table du §3 (à 165 BPM,
   150-250 ms pour un kick à rumble).
3. Deuxième couche, un **click** parmi les 500 (ou un sample de la banque
   `/Volumes/xtreme/Samples`, branche DRUMS, [[../../kt-banque-samples]]) :
   enveloppe raccourcie « assez » pour qu'il se fonde au sub, pas de queue.
   Une troisième couche optionnelle en bruit filtré pour l'air (tribe).
4. Harmoniques du sub (le sub « étendu ») : un peu, pour que le kick passe
   sur le téléphone ; le reste de la saturation se fait dans Reaper ([[maison-grave-projet-reaper]] §2.4)
   pour rester comparable entre kicks.
5. EQ intégré avec analyseur : couper au-dessous de 25-30 Hz ; en
   architecture kick + basse, cloche de **-4,5 dB** à la fondamentale de la
   basse (Attack Magazine, via KT5) pour que les deux coexistent.
6. Famille : enregistrer trois presets du même kick qui ne diffèrent que
   par la note d'arrivée (F#, G, A) et trois par la longueur (court, à
   rumble, kickbass). Un kick par bank, choisi dans la famille, jamais
   repitché de plus de deux ou trois demi-tons sur la DT2 (doctrine §11).
7. Phase : vérifier que le kick part toujours au même point de phase (pas
   de randomisation) ; deux kicks exportés d'un même preset doivent se
   superposer sans annulation.

### 3.3 Recette C, Vital (le kick dessiné de A à Z)

1. Piste KICK, Vital, preset init. **Voices** = 1, **OSC 1** en sinus,
   unisson 1 voix, **randomisation de phase à 0** (petit potard à côté de
   Phase), sinon chaque kick part d'une phase différente et le sub change
   de poids d'un coup à l'autre.
2. **ENV 1** (ampli) : attaque 0, hold 0, decay à la longueur visée,
   sustain 0, release 10 ms.
3. **ENV 2** glissée sur le **Transpose** de l'OSC 1, profondeur +24 à +36
   demi-tons ; ENV 2 : attaque 0, decay 10-60 ms (click intégré à thump),
   sustain 0. La note MIDI jouée est la tonique (F#1 = note MIDI 30, G1 =
   31, A1 = 33) ; vérifier sur SPAN que la queue retombe bien dessus.
4. Click séparé : **OSC 2** en carré ou en bruit (section Sampler avec un
   bruit blanc), ENV 3 sur son niveau, decay 5-15 ms, niveau bas. C'est la
   couche « click » de Koçer, à chercher entre sinus et carré.
5. **Filtre 1** sur OSC 1 seulement, modèle Analog ladder 24 dB, cutoff
   250-400 Hz, **Drive** du filtre modéré : premier étage de saturation,
   qui reste sous le passe-bas.
6. Effet **Distortion** de Vital (Soft Clip, puis Hard Clip pour le mental)
   en second étage, mix 30-50 % ; refermer avec l'EQ de Vital si le haut
   devient criard. Le troisième étage, Trash, se fait dans Reaper sur la
   bande 3/4 du splitter ([[maison-grave-projet-reaper]] §2.4).
7. Enregistrer le preset Vital avec la note dans le nom, puis rendu ([[maison-grave-rendu-dt2]] §7).

### 3.4 Chaîne de sortie commune

Après le joiner (ou le dossier SUB + BODY) : ReaEQ passe-haut, puis JS
Soft Clipper à -1 dB pour rattraper une crête, jamais pour « grossir »,
puis rendu. Pas de compresseur sur le kick seul ; la colle se fait sur la
DT2 (doctrine §10).

**La ReaEQ de sortie, réglage.** Une seule bande : Type High Pass,
Frequency 28 Hz, Bandwidth 1,7 (courbe sans bosse) ; les autres bandes
retirées ; preset `kick HPF 28`, le même pour toutes les banks. Elle reste
branchée en 1/2, ce qui est juste : après le joiner seuls 1/2 vont au
master. Rien d'autre : l'équilibre sub / corps se règle sur le mix de
Trash et les potards de bande du joiner, et un creux du spectre (souvent
vers 100 Hz sur un kick à sub sinus, entre la fondamentale et le départ de
l'enveloppe de pitch) ne se rebouche pas à l'EQ, on remonterait du bruit.
Seule exception, en architecture kick + basse : une cloche de -4,5 dB à
la fondamentale de la basse (92 Hz pour une basse en F#2), bandwidth 1 oct
(Attack Magazine, via KT5). Pas de cloche en kick + rumble ni en kickbass.
Ensuite, Reset des statistiques de SPAN et lecture du Peak : entre -6 et
-3 dBFS, prêt à rendre ; au-dessus, baisser le fader de KICK plutôt que
d'ajouter un limiteur.

### 3.5 Valider un kick

- Note sur la queue = tonique du projet (SPAN + ReaTune).
- Longueur lue en ms, conforme à l'architecture (table §3).
- Tenue du sub entre deux kicks (SPAN, 30-100 Hz) : sous -20 dB pour un
  kick court, au-dessus de -10 dB pour un kickbass.
- En mono, puis au téléphone : le kick doit rester reconnaissable au
  téléphone par ses harmoniques, et ne pas gagner ni perdre en mono.
- Export avec de la marge, nom `kick_<style>_<note>_<bpm>.wav` (ex.
  `kick_tribe_F#_165.wav`).

## Liens

[[maison-sounddesign-grave-reaper]] · [[maison-grave-projet-reaper]] · [[maison-grave-rumble]]

#digitakt #kb #tutos #sounddesign
