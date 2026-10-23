---
tags: [digitakt, kb, tutos]
theme: Compresseur, sidechain, kick fantôme et saturation (Elektronauts)
lot: 2
ordre: 6
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
auteur: communauté Elektronauts
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-23
---

# Elektronauts 6 — Compresseur, sidechain, saturation

**En une phrase** : le compresseur master de la DT2 se route par track et
par FX, se déclenche sur une track silencieuse qui sert de « kick fantôme »,
et son make-up pousse l'overdrive master pour salir ; les valeurs du fil
sont des points de départ.

Panorama : [[elektronauts-panorama]]. Fiches du geste :
[[../send-fx-compresseur]], [[../audio-routing-overbridge]],
[[../amp-overdrive-bitreduction]], [[../lfo]].

## Sur notre grille

Le kick fantôme est prévu par la [[../../doctrine]] §10 ; il vit sur la 16
retirée du main, ou sur la 2 si le rumble est produit autrement. Le
compresseur reçoit la basse 9, les Id 13-14, la ride 8 et les FX, jamais le
kick 1.

## Astuces

### 1. Routing et source du compresseur

- **Source** : [#30](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/30), [#141](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/141), [#195](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/195).
- **Résultat** : un pompage propre sur les tracks choisies, déclenché par le
  kick.
- **Pas à pas** :
  1. `[FUNC] + [FLTR]` sur la page du compresseur : les touches de trig
     cochent les tracks envoyées.
  2. Source du sidechain : une track (la 1), « /COMP » (tout ce qui n'est
     pas routé) ou l'entrée audio.
  3. Filtre de sidechain en **passe-bas** pour que ce soit le kick qui
     déclenche.
  4. Point de départ d'un utilisateur : seuil 35, attaque 0, release 43,
     make-up 4,3 dB, ratio 1:20, source /COMP, SC filter -50, mix 127.
- **Attention** : valeurs d'un utilisateur et d'un sample, à régler à
  l'oreille.

### 2. Kick fantôme sur une track silencieuse

- **Source** : [#252](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/252).
- **Résultat** : le pompage continue quand le vrai kick se tait, se place où
  l'on veut (four-on-floor sous un break half-time), se p-locke par trig
  et se mute pendant une montée.
- **Pas à pas** :
  1. Sur la 16 : un signal propre (onde carrée courte ou le kick lui-même),
     trigs sur 1, 5, 9, 13.
  2. AUDIO ROUTING > TO MAIN : décocher la 16, elle ne sort plus.
  3. Compresseur : source = track 16.
  4. Régler decay et release de la 16 : c'est maintenant l'enveloppe du
     pompage ; p-locker attaque ou release sur certains trigs.
  5. Muter la 16 pendant une montée pour arrêter le pompage sans toucher au
     kick.
- **Chez nous** : [[../send-fx-compresseur]], doctrine §10.

### 3. Compresseur avant l'overdrive master

- **Source** : [#124](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/124), [#570](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/570), [#571](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/571).
- **Résultat** : les 24 dB de make-up poussent l'overdrive du master ;
  attaque et release au minimum ajoutent une distorsion ; resampler le
  résultat pour en faire un sample.
- **Pas à pas** :
  1. Compresseur : make-up haut, attaque et release au minimum.
  2. Overdrive master : monter jusqu'à la saturation voulue.
  3. Resampler MAIN L/R la mesure salie, la poser sur la 5 ou la 15.
- **Attention** : sous un sub avec du contenu aigu « ça casse tout en
  morceaux » ; en techno Synthackers ne l'accepte qu'en dry/wet
  ([[synthackers-techno-acid]] trick 14).

### 4. Patterns du DT1 qui sonnent faux

- **Source** : [#388](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/388).
- **Résultat** : comprendre pourquoi un pattern importé pompe moins.
- **Pas à pas** :
  1. Sur le DT1 la reverb pouvait passer dans le compresseur ; sur le DT2 le
     routage des FX vers le compresseur est séparé et **éteint par défaut**.
  2. Seconde page du routage compresseur : cocher delay et reverb pour
     retrouver le comportement.
- **Chez nous** : même geste que [[synthackers-techno-acid]] trick 5.

### 5. Faux clipper pour grossir la basse

- **Source** : [#543](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/543).
- **Résultat** : les autres tracks s'effacent en rythme autour de la basse,
  qui ne change pas.
- **Pas à pas** :
  1. Sur chaque track à « écraser » : LFO1 sinus rapide → **AMP VOL** (le
     flutter).
  2. LFO2 rampe exponentielle → **profondeur de LFO1**.
  3. Mode LFO.T sur les deux, déclenchés par les trigs posés en rythme
     avec la basse.
  4. Doser la profondeur de LFO2 jusqu'à ce que la basse ressorte.

## Liens

[[elektronauts-panorama]] · [[../send-fx-compresseur]] ·
[[../audio-routing-overbridge]] · [[../amp-overdrive-bitreduction]] ·
[[../lfo]] · [[../sampling-resampling]] · [[../../doctrine]] §10
