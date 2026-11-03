---
tags: [digitakt, kb, tutos]
theme: Vélocité, sound macros et key tracking comme macros (Elektronauts)
lot: 2
ordre: 5
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
auteur: communauté Elektronauts
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-23
---

# Elektronauts 5 — Vélocité, macros et key tracking

**En une phrase** : la vélocité découplée du volume, les quatre sound
macros (PB, AT, MW, BC) et le key tracking du filtre mettent chacun quatre
paramètres sous un seul geste ; de la dynamique et du timbre sans toucher
au volume.

Panorama : [[elektronauts-panorama]]. Fiches du geste :
[[../parameter-preset-locks]], [[../lfo]], [[../filtres]], [[../cc-nrpn]],
[[../tracks-midi]].

## Sur notre grille

Vélocité macro sur les hats 6-7 et les percs 4-5 ; sound macros sur les
tracks tonales 9 à 14, pilotées par la 16 en MIDI ou un contrôleur
([[../controleur-maschine]]) ; key tracking sur la basse 9 et la séquence 10.

## Astuces

### 1. Vélocité macro

- **Source** : [#28](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/28).
- **Résultat** : le bouton de vélocité ouvre le filtre, allonge le decay,
  envoie au delay et module un LFO, au lieu de ne faire que le volume ;
  jouable au clavier, lockable, et en CTRL-ALL.
- **Pas à pas** :
  1. SETUP de la track : **VEL → VOL** sur OFF.
  2. Page TRIG, VEL MOD : quatre destinations, par exemple fréquence du
     filtre +, decay d'AMP +, send delay +, profondeur de LFO -.
  3. Jouer en mode VELOCITY, ou locker `VEL` par pas au bouton.
  4. Variante multi-sample : chaîne de 16 hats classés par force, VEL MOD →
     slice ; la vélocité choisit la frappe. Même recette pour le kick,
     rendu depuis Reaper : [[maison-grave-rendu-dt2]] §7.3.
- **Chez nous** : exercice 4 du panorama ; profils de [[../theorie/kt-hats]].

### 2. Overdrive comme volume

- **Source** : [#135](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/135).
- **Résultat** : plus fort = plus sale, naturel sur les percs.
- **Pas à pas** :
  1. SETUP : VEL → VOL sur OFF.
  2. VEL MOD : destination **OVERDRIVE** en positif.
  3. Doser pour que la vélocité basse reste propre.

### 3. Sound macros par loopback MIDI

- **Source** : [#81](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/81), [#62](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/62), [#516](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/516).
- **Résultat** : mod wheel, breath controller, aftertouch et pitch bend
  modulent chacun quatre destinations par track, sans contrôleur externe
  si la 16 renvoie du MIDI dans la machine.
- **Pas à pas** :
  1. SETUP de chaque track tonale : destinations de MW (CC1), BC (CC2), AT
     et PB, quatre chacune.
  2. Toutes ces tracks sur le **même canal MIDI** d'entrée pour recevoir le
     même mouvement.
  3. Source : un contrôleur, ou la track 16 en MIDI (CC1 / CC2 lockés ou
     en LFO) câblée de MIDI OUT vers MIDI IN de la DT2.
- **Chez nous** : c'est la mécanique des presets Substance
  ([[../presets-substance]]) et des builds de
  [[synthackers-techno-acid]] trick 16 ; [[../cc-nrpn]] pour les numéros.

### 4. Key tracking

- **Source** : [#392](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/392), [#446](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/446), [#578](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/578).
- **Résultat** : la hauteur de la note module SRR, volume, pan ou sends ;
  les notes graves perdent du taux d'échantillonnage, les notes hautes
  moins de reverb ; une Grid jouée chromatiquement au clavier.
- **Pas à pas (timbre)** :
  1. Page 2 du filtre : key tracking vers **SRR** en négatif (le grave
     ralentit son horloge comme un vieux sampler).
  2. Vers **VOL** en positif pour compenser le niveau.
  3. Vers PAN ou vers les sends (moins de reverb en bas).
- **Pas à pas (slices chromatiques)** :
  1. Machine Grid sur la track, key tracking **+8 sur TUNE** (valeur
     empirique, à ajuster à l'oreille).
  2. Les notes du clavier parcourent les slices.
  3. OCTAVE à **-1** dans le SETUP décale les slices d'une octave et libère
     les notes qui déclenchent les tracks depuis un clavier externe.
- **Chez nous** : basse 9 et séquence 10 ; [[synthackers-techno-acid]]
  trick 3 pour un exemple en preset.

## Liens

[[elektronauts-panorama]] · [[../parameter-preset-locks]] · [[../lfo]] ·
[[../filtres]] · [[../cc-nrpn]] · [[../tracks-midi]] ·
[[../controleur-maschine]] · [[../presets-substance]] ·
[[../theorie/kt-hats]]
