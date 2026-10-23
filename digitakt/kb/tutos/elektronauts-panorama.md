---
tags: [digitakt, kb, tutos]
theme: Tips & tricks Elektronauts (fil Digitakt II), panorama et pièges
lot: 2
ordre: 0
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
auteur: communauté Elektronauts (fil tenu par LyingDalai)
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-23
---

# Elektronauts — Tips & tricks Digitakt II, panorama

**En une phrase** : le fil *Digitakt II Tips & Tricks* d'Elektronauts
(564 posts, d'avril 2024 à mai 2026) tourne autour de six idées qui comptent
pour un live sur notre grille : une **seconde séquence cachée dans chaque
pattern** (euclidien éteint, page de retrig, page loop hors longueur
maître, perform kit), le **CTRL-ALL ciblé** comme geste de fill, le
**preset pool** comme rack de fills et de one-shots, le **resampling
stéréo** comme fader d'Octatrack, la **vélocité et le key tracking** comme
macros, et un **projet modèle** (16 slots par défaut, kits, banques par
famille) pour ne plus repartir de zéro.

Source : fil [Digitakt II Tips & Tricks](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556)
ouvert et tenu par LyingDalai ; lecture du 2026-10-22 via l'API du forum,
tri par nombre de likes. Les 121 posts à 6 likes et plus sont répartis en
**onze fiches, une par famille**, chaque astuce y est déroulée pas à pas et
renvoie au post d'origine (`#n`). Les gestes ne sont pas encore rejoués
sur la machine (statut `draft`). Les premières pages datent de l'OS 1.01,
plusieurs astuces supposent l'OS 1.10 et plus (locks sur toute la track ou
la page, gammes au bouton NOTE, key tracking) ou 1.15 (machine Slice, track
swap) ; tout est valable en OS 1.17.

## Les onze familles

| # | Fiche | Posts les plus votés | Ce que ça apporte au live |
|---|---|---|---|
| 1 | [[elektronauts-presets-pool]] | #9 (62), #268 (38), #450 (21), #256 (15) | un son p-locké devient un preset ; le pool devient un rack de fills |
| 2 | [[elektronauts-seconde-sequence]] | #97 (24), #286 (16), #304 (17), #81 (25), #250 (12) | deux ou trois variations par pattern sans changer de pattern |
| 3 | [[elektronauts-ctrl-all]] | #36 (12), #425 (20), #295 (6), #522 (11) | fills d'un seul geste, retour par NO |
| 4 | [[elektronauts-resampling]] | #76 (26), #88 (19), #208 (12), #93 (37), #149 (10) | une boucle du main comme track de secours, fondu LFO3 |
| 5 | [[elektronauts-velocite-macros]] | #28 (28), #135 (22), #81 (25), #392 (21) | 4 paramètres sous un bouton, dynamique sans toucher au volume |
| 6 | [[elektronauts-compresseur]] | #30 (17), #252 (35), #195 (9), #124 (7) | pompage propre, kick fantôme, make-up dans l'overdrive |
| 7 | [[elektronauts-projet-modele]] | #24 (28), #65 (23), #101 (42), #425 (20), #35 (22), #577 (4) | 16 slots par défaut, kit par couleur, banques par famille |
| 8 | [[elektronauts-grid-wavetables]] | #3 (37), #111 (24), #180 (28), #390 (8), #410 (21) | drones et textures depuis une chaîne 64 slices |
| 9 | [[elektronauts-comb-delay]] | #17 (9), #116 (13), #181 (24), #290 (9) | flanger de hats, résonateur accordé au C |
| 10 | [[elektronauts-transitions]] | #375 (8), #78 (10), #222 (15), #540 (8) | LAST, note tenue à travers le changement, machines synchro |
| 11 | [[elektronauts-raccourcis]] | #7 (8), #31, #32, #33, #114, #449, #553 | moins de menus pendant le live |

## Vocabulaire

- **CTRL-ALL / CTRL-SEL** : `[TRK]` tenu + un encodeur agit sur toutes les
  tracks cochées dans CONTROL ALL CONFIG (`[FUNC] + [FLTR]`) ; `[NO]`
  tant que `[TRK]` est tenu annule tout. Le fil dit « CTRL-SEL » pour
  rappeler que, contrairement au DT1, la sélection se règle.
- **Seconde séquence** : tout ce qu'un pattern garde en réserve sans
  pattern supplémentaire : trigs euclidiens préparés mais éteints, page
  de retrig éteinte, pages au-delà de la longueur maître, état perform.
- **Preset pool** : les presets chargés dans le pattern et jouables par les
  touches de trig (mode PRESET) ; tenir une touche remplace le son de la
  track sélectionnée le temps de l'appui.
- **Kick fantôme** : duplicata du kick sur une track retirée du main,
  seule source du sidechain ; le vrai kick peut se taire sans arrêter le
  pompage.
- **Sound macros** : PB, AT, MW, BC dans le SETUP de la track, 4
  destinations chacune, pilotées par un contrôleur ou un loopback MIDI.
- **Vélocité macro** : VEL → VOL coupé dans le SETUP, puis 4 destinations
  sur la page VEL MOD ; le bouton de vélocité devient une macro.
- **Key tracking** : page 2 du filtre, la hauteur de la note module
  jusqu'à 4 destinations (SRR, volume, pan, sends).
- **Slew** : avec `WAVE = RAND`, l'encodeur F lisse les sauts entre deux
  valeurs aléatoires ; sur `SRC:SLICE` d'une wavetable, un morphing.
- **Preroll** : nombre de mesures (jusqu'à 16) avant le début d'un
  enregistrement armé ; permet d'enregistrer une boucle externe avec ses
  queues de FX.

## Pourquoi ça marche

Concret d'abord : un pattern tribe à 170 sur notre grille, kick 1, rumble
2, perc 4-5, hats 6-7. Sans rien ajouter, il contient déjà un fill de
toms (euclidien éteint sur 4 et 5), un roulement de hats (page de retrig
sur 6), un break de batterie (pages 5 à 8 sur la rangée 1-8), une version
mangée de tout (resample sur 16, LFO3 en fader) et un kit saturé (perform
kit). Cinq variations, un pattern, zéro changement de pattern.

La raison est structurelle : sur la DT2, presque chaque couche du
séquenceur a un **interrupteur** (euclidien ON / OFF, retrig ON / OFF,
perform ON / OFF, page loop, mute) et le CTRL-ALL applique l'interrupteur à
un sous-ensemble choisi de tracks. Un interrupteur se joue d'une main sans
regarder, un changement de pattern non. La doctrine §4 dit que les mutes
sont le vrai séquenceur du live ; le fil ajoute que les interrupteurs de
couche en sont la seconde moitié.

Deuxième idée : la machine confond volontiers **son et réglage**. Un trig
p-locké est un preset, un kit est une copie, un sample resamplé est un
nouveau son, une vélocité est une macro. La communauté en tire une règle :
dès qu'un réglage plaît, le figer (preset, kit, resample) pour le
retrouver, puis continuer à casser l'original sans risque.

Troisième idée : le **projet modèle**. Les 16 slots par défaut, les kits
par couleur et les banques rangées par famille rendent le CTRL-ALL sur les
slots musical (le slot n de chaque banque joue le même rôle) et évitent de
reconstruire la grille à chaque live. Notre 0-KIT et nos banques par
couleur ([[../../doctrine]] §2, §13) sont la même réponse.

## Pièges

- CTRL-ALL sans CONTROL ALL CONFIG : le kick 1, le rumble 2 et la track
  MIDI 16 bougent aussi. Configurer avant, et sauver le pattern avant de
  casser (le retour par `[NO]` ne marche que `[TRK]` tenu).
- La page loop a eu des bugs en lecture live (OS 1.01, [#7](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/7)) :
  à revérifier en 1.17 avant de compter dessus en set.
- Les kits ne sont pas partagés entre patterns : modifier le kick dans A02
  ne corrige pas A01. Le « même kick dans tout le set » (doctrine §3) se
  tient par discipline ou par preset, pas par le kit.
- Chaînes de samples longues : lentes à charger et pleines de silence ;
  un sample par slot, 16 max par chaîne et seulement pour des variations
  d'un même son.
- Les « alt tracks » 1-6 / 9-14 de [#527](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/527)
  (chaque track du haut doublée par une variante en bas) contredisent la
  grille invariante : chez nous la variante vit dans les interrupteurs du
  même pattern, pas dans une autre track.
- Wavetable en Grid : hors de la plage (slice + profondeur du LFO) la table
  donne du bruit ; slice 33, profondeur 31,99.
- Le perform kit ne sauve rien : tout ce qui plaît se fige par temp save
  ou preset ([[../perform-kit-temp-save]]).
- Les réglages chiffrés du fil (seuil 35, release 43, feedback 103-110,
  key tracking +8) sont ceux d'un utilisateur, d'un sample et d'un OS :
  des points de départ, pas des valeurs.

## À essayer (une séance)

Grille de la [[../../doctrine]] §1.

1. **Trois interrupteurs, un pattern (10 min).** Pattern tribe fini. Percs
   4 et 5 : E(5, 16) et E(7, 16) réglés, euclidien OFF. Hat 6 : page RETRIG
   `LEN 2`, `RATE 1/16`, OFF. CONTROL ALL CONFIG : 4, 5, 6 seulement.
   Jouer 8 mesures, `[TRK]` + euclidien ON pour 1 mesure, `[TRK]` + retrig
   ON pour 2 temps, `[NO]` pour revenir. Noter ce qui sert de fill et ce
   qui sert de break ([[elektronauts-seconde-sequence]]).
2. **Fader de resample (10 min).** Resample MAIN L/R d'une mesure, posé sur
   la 16 en Grid 16 avec 16 trigs. LFO3 → AMP VOL -0.01 sur la 16, +0.01
   sur 1 à 14, LFO arrêté. CTRL-ALL sur la profondeur de LFO3 : fondre vers
   le resample, filtrer le resample, revenir. Puis la variante filtre
   (passe-haut contre passe-bas) ([[elektronauts-resampling]]).
3. **Pool de fills (10 min).** Pattern réservé : track 15 riser, 12 un cri,
   4 un impact, 5 une boucle de break en Repitch (1 mesure). Kit sauvé,
   « Add to preset pool ». Retour au pattern tribe, mode PRESET, `RETRIG
   ON` et `LEN` au minimum sur la 5 : tenir le break aux rates 1/8, 1/16,
   1/32 sur le dernier temps de la phrase ([[../theorie/kt-phrasage-tension]],
   [[elektronauts-presets-pool]]).
4. **Vélocité macro sur le hat (5 min).** Track 6, VEL → VOL OFF, VEL MOD :
   filtre +, decay +, send delay +, profondeur LFO -. Profils de vélocité
   de [[../theorie/kt-hats]] : la même grille de vélocité ouvre maintenant le
   timbre au lieu du seul volume ([[elektronauts-velocite-macros]]).

## Ressources

- Fil source : <https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556>
  `[V]` (564 posts, lu le 2026-10-22 ; les numéros `#n` renvoient aux posts).
- Fil jumeau Digitone II Tips & Tricks, cité pour le remix Grid + euclidien
  ([#534](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/534)) `[R]`.
- Manuel DT2 OS 1.17 : §9 (presets, kits, pool), §10.4 (micro timing),
  §10.7 (longueur par track), §11.2 (TRIG, VEL MOD), §11.5 (filtre, key
  tracking), §13 (compresseur), §14 (sampling, preroll) ; p. 47 pour les
  locks sur toute la track ([#402](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/402)).
- Vidéos citées dans le fil (non reprises ici, cf. [[_index]] pour les
  sessions décortiquées) : Eak (wavetables, song mode, sidechain),
  Speldosa (page loop hors longueur maître), GyZa (faux slicing par le
  pool), Chroma_Surge (granulaire), djst (sample comme oscillateur).

## Liens

[[_index]] · [[../../doctrine]] §1, §2, §4, §10, §13 · [[../preset-pool]] ·
[[../presets-kits-pool]] · [[../euclidien]] · [[../microtiming-retrigs]] ·
[[../perform-kit-temp-save]] · [[../sampling-resampling]] ·
[[../live-looping]] · [[../send-fx-compresseur]] ·
[[../parameter-preset-locks]] · [[../fill-conditions]] ·
[[../patterns-chaines]] · [[../filtres]] · [[../lfo]] · [[../machines-src]]
· [[../slice-breaks]] · [[../keyboard-gammes]] · [[../projet-sauvegarde]]
· [[../mutes]] · KT5 [[../theorie/kt-tonalite-du-grave]] · KT9
[[../theorie/kt-phrasage-tension]] · KT20 [[../theorie/kt-hats]]
