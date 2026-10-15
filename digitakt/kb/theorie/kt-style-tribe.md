---
tags: [digitakt, kb, theorie, kt]
theme: Tribe / hardtek
lot: 3
ordre: 10
styles: [tribe, hardtek, tekno]
statut: draft
updated: 2026-10-15
---

# KT10 — Tribe / hardtek

**En une phrase** : le tribe est un four-on-floor à 160-190 BPM dont le
kick a une enveloppe de hauteur audible, dont le groove vient des toms et
percs en appel-réponse qui anticipent le temps, et dont la forme est une
suite de plateaux de 8 à 16 mesures ponctués de samples en points
d'orgue ; tout le socle KT1 à KT9 s'y retrouve, c'est le style de
référence du live.

## Signature

Références : 7 morceaux tribe du hub ([[_index]], passe du 2026-10-15 :
Floxytek, Kodaman, Area 23, Apre, Liberté Naturel, Tekotak).

| Élément | Théorique | Mesuré | Lecture |
|---|---|---|---|
| Tempo | 160-180, hardtek jusqu'à 190 | 161,5 (× 4), 166,7, 172,9, 181 | le gros de la library tribe est à 160-165, pas à 190 |
| Kick (sub) | `X...X...X...X...` | 4 morceaux nets ; Floxytek `XXx.XXx.XXXxXXXx`, Kodaman `XxX.xXx.XXXxXXXX` | chez Floxytek et Kodaman le sub est plein entre les kicks : rumble ou basse sous 200 Hz (KT5) |
| Toms, percs (mid) | `...x..x.....x.x.` en réponse au kick | moyenne `Xxxxx.xxXx.xXxxx` ; Tekotak `X..XX.xXX.xXX.Xx`, Area 23 `X.xXX.xXX..XX.xX` | le motif `X..X` par temps (kick et pickup sur le « a ») domine : anticipation (KT3) |
| Hats (high) | `x.x.x.x.x.x.x.x.` croches, shuffle 50-56 % | moyenne `Xx.Xx.xxXx.xX.xx` | croches avec un « a » marqué ; `swing` 0,70-0,88 sur 4 morceaux sur 7 |
| Rebond du kick | `X...X...X...X.X.` une mesure sur 2 ou 3 | trace : `x` sur les pas 2-3 d'un temps (Kodaman `XxX.xXx.`, Tekotak `X...X...X.x.X.x.`) | le repliage moyenne les mesures : le doublé apparaît en coup faible, sa périodicité (2 ou 3 mesures) est invisible, à écouter |
| Tonalité | pentatonique mineure sur la tonique du kick | Kodaman D pentatonique mineure (0,81), Apre F pentatonique mineure, Floxytek F phrygien | peu de notes, accords D5 / Dsus2 seuls (KT8) |
| Structure | plateaux de 8-16 mesures, breakdowns de 4-8 | Kodaman : sections de 4 à 28 mesures, 13 tracks actives en main, 4 à 5 en breakdown | la bank générée ([[../../../library/digitakt/kodaman_-_beton]]) donne l'ordre d'entrée des tracks |

## Vocabulaire

- **Tribe kick** : kick avec **pitch envelope** audible, descente rapide
  de la hauteur vers la fondamentale, peu distordu comparé au gabber ;
  son « bouncy » vient de cette descente.
- **Pitch envelope** : variation de hauteur sur les premières
  millisecondes du kick ; longue = « boing », courte = « tak ».
- **Offbeat** : basse ou hat sur le « et » (`..x.`) ; la basse tribe est
  en contretemps, rebondissante (doctrine §13).
- **Call and response** : toms et percs qui se répondent sur deux
  demi-mesures ou deux tours (KT9).
- **Plateau** : 8 à 16 mesures sans changement, où un seul élément entre
  ou sort (KT9).
- **Point d'orgue** : sample vocal ou filmique posé une fois par phrase
  de 8 ou 16, qui suspend la boucle.
- **Sample hook** : le sample qui identifie le morceau ; vit sur la 12
  ou une Id.
- **Drop-out** : retrait brutal d'un élément (souvent le kick) pour une
  mesure, puis retour.
- **Rebond** (doublé martial) : un kick supplémentaire une croche avant
  le 1 (`X.X.` sur le temps 4), une mesure sur deux ou sur trois ; le
  roulement de marche du tribe.
- **Hardtek** : tribe plus rapide (180-190) et plus saturé, kick plus
  dur, percs moins nombreuses ; le pont vers le mental (KT11).

## Pourquoi ça marche

**Concret d'abord : une boucle tribe en six tracks.** À 165 BPM, kick 1
`X...X...X...X...`, rumble 2 sur les mêmes pas, basse 9 `..x...x...x...x.`
sur la tonique, hat fermé 5 en croches, toms 7 `...x..x.....x.x.`, perc
B 8 en E(5, 16) `x..x..x..x..x...` tournée de 2 pas. C'est tout : les
morceaux de référence n'ont pas plus de matière rythmique. Ce qui fait
tribe est dans le détail de chaque couche.

**Le kick et son enveloppe.** La passe harmonique du hub (KT5) ne trouve
que des quintes nues et des sus2 : le grave est une tonique tenue par un
kick qui a une note. Le tribe kick n'est pas le kickbass mental : il est
plus court, sa queue retombe avant la basse en contretemps, et sa
descente de hauteur est audible (« bouncy »). Sur la DT2, le pitch
envelope est un p-lock ou un LFO court sur `TUNE` relancé à chaque trig
(fiche [[../lfo]]) ; sur un sample déjà enveloppé, c'est le choix du kick
(fiche [[../kick-mental-vst]] pour la fabrication).

**Les toms en appel-réponse et le « a ».** La signature mesurée du mid,
`X..XX.xXX.xXX.Xx` chez Tekotak, dit deux choses : un coup sur chaque
temps (le kick lui-même, replié dans le mid), et un coup sur le pas qui
précède le temps suivant. C'est l'anticipation de KT1 et KT3 : les toms
tribe ne sont pas en retard, ils **tirent** vers le temps. Le tresillo
`x..x..x.` sur les toms (KT1) la contient naturellement ; l'appel-réponse
entre 7 et 8 (KT9) répartit ces anticipations sur deux voix pour que
l'oreille suive un dialogue plutôt qu'un roulement.

**Le rebond du kick : le doublé martial.** Le kick tribe ne bouge pas
(doctrine §3), sauf une fois toutes les deux ou trois mesures : un coup
supplémentaire sur le « et » du temps 4, une croche avant le 1
(`X...X...X...X.X.`), le temps d'un bégaiement, puis la mesure suivante
repart droite. Trois choses font l'effet « martial » :

1. **le doublé lui-même** : deux kicks à une croche d'écart, soit à
   170 BPM 60 / 170 / 2 = 176 ms, à 190 BPM 158 ms ; c'est la vitesse
   d'un « ra » de tambour militaire, le double stroke d'une marche ;
2. **la rareté** : à chaque mesure ce serait un pattern différent ; une
   mesure sur deux ou trois, la salle l'attend sans pouvoir le prévoir et
   chaque retour « remet au pas » ; c'est un turnaround (KT9) joué par le
   kick lui-même, ce qu'aucun autre style cœur ne se permet ;
3. **le cycle** : sur 2 mesures, le rebond tombe toujours au même endroit
   d'une phrase de 4 ou 8, carré ; sur 3 mesures, il glisse par rapport à
   la phrase (polymétrie de KT2, ppcm(3, 4) = 12 mesures, ppcm(3, 8) =
   24) et se réaligne de loin en loin : la « marche forcée ».

Le rebond tire **vers** le 1 : c'est une anticipation (KT1, KT3) à
l'échelle de la mesure, comme le « a » l'est à l'échelle du temps. La
passe du hub n'en montre que la trace (un `x` faible sur les pas 2-3,
puisque le repliage moyenne les mesures) ; la périodicité s'écoute sur les
références. Sur la DT2, il ne touche pas au kick sacré : un trig de plus
sur le pas 15 de la track 1 en condition `2:2` ou `3:3`, ou un retrig
`RATE` 1/8 `LEN` 1 sur le kick du pas 13 sous la même condition ; variante
sur les toms (7) pour le doublé sans toucher à la 1.

**Les hats en léger shuffle.** La veille donne 50-56 % ; KT3 montre
qu'à 165-190 BPM, 56 % vaut 7 à 10 ms, à peine audible mais présent. Ce
qui s'entend davantage, c'est la vélocité : pas 1, 5, 9, 13 pleins, le
reste à 60-70 %, et le « a » (pas 4, 8, 12, 16) relevé. Ce profil
reproduit la signature `Xx.Xx.xxXx.xX.xx` sans aucun swing machine.

**Basse en contretemps, rumble entre les kicks.** Chez Floxytek et
Kodaman, le sub est plein (`XXx.XXx.`) : le rumble et la basse occupent
les pas entre les kicks, exactement le partage du temps de KT5. La
doctrine §9 arbitre : rumble sur les mêmes pas que le kick avec ducking,
basse en contretemps ; la variante « rumble qui roule entre les kicks »
remplace la basse, pas l'inverse.

**Tonalité : trois notes, une couleur.** Kodaman tourne sur D5 pendant
tout le morceau, avec un Dsus2 ou un Csus2 de temps en temps : la
tonalité est une tonique (KT5), la ligne une pentatonique de deux ou
trois notes (KT6, KT7). La b2 phrygienne apparaît chez Floxytek : c'est
le moment où le tribe penche vers le mental (doctrine §13, KT11).

**Forme : plateaux et points d'orgue.** La bank de Kodaman montre des
sections de 4 à 28 mesures, 13 tracks actives en main, 4 ou 5 en
breakdown ; les breakdowns durent 4 à 8 mesures, jamais plus de 16 (KT9).
Le sample vocal est posé une fois par phrase (`1:8`, `1:16`) : un point
d'orgue qui suspend la boucle sans la couper. Un live tribe de 20 min =
4 à 6 plateaux, un élément qui entre ou sort par phrase, deux breakdowns.

## Sur la DT2

Grille de la [[../../doctrine]] §1. Gestes : [[../euclidien]],
[[../polymetrie]], [[../fill-conditions]], [[../lfo]], [[../mutes]].
Patch Tidal équivalent : [[../../../technique/patches/tribe]].

1. **La boucle de référence (10 min).** 165 BPM, les six tracks du
   paragraphe « concret d'abord ». Vélocités des hats : 100 / 65 / 65 /
   80 par temps (pas 1, 2, 3, 4), swing à 50. Toms 7 en tresillo sur 8 pas
   (`PL1` = 3, `LEN` = 8), `RO1` à l'oreille pour placer un coup sur le
   « a » du temps 2. Perc 8 en E(5, 16) tournée de 2. Écouter 16 mesures
   sans toucher : c'est la signature mesurée.
2. **Pitch envelope (5 min).** Kick 1 : LFO sur `TUNE`, forme
   exponentielle descendante, `TRIG` relancé, vitesse rapide, profondeur
   +12 puis +24 (fiche [[../lfo]]). Comparer avec un kick sec. Le
   « bouncy » apparaît entre les deux ; garder le réglage en preset.
3. **Rebond (5 min).** Kick 1 en four-on-floor, un trig de plus sur le
   pas 15, `COND` = `2:2` (fiche [[../fill-conditions]]) : 8 mesures.
   Puis `3:3` : 12 mesures, le temps que le rebond retombe sur le 1 d'une
   phrase de 4. Puis le trig sur le pas 14 (deux croches avant) : plus
   « roulé », moins martial. Garder `3:3` sur le pas 15.
4. **Plateaux et point d'orgue (10 min).** Pattern complet, vocal sur
   12 en `1:8`. Jouer 6 phrases de 8 mesures aux mutes : phrase 1 kick,
   rumble, hats ; 2 + basse ; 3 + toms ; 4 + perc B ; 5 drop-out du kick
   sur la dernière mesure (mute et démute à la main) ; 6 tout. Compter.
   C'est un live tribe de 50 s à l'échelle 1/20.

## Pièges

- Trop de percs polymétriques à la fois (KT2) : une ou deux suffisent ;
  les références n'ont pas plus de trois couches percussives.
- Hats swingués à 60 % et plus à 165-190 BPM : flou, pas groove (KT3).
- Rebond à chaque mesure : ce n'est plus un rebond, c'est un pattern à
  cinq kicks, et l'effet martial disparaît ; `2:2` au plus serré.
- Rebond par micro timing ou en déplaçant un kick : le kick sacré bouge ;
  toujours un trig **ajouté** sous condition, le four-on-floor intact.
- Un kick trop long sous une basse en contretemps : les deux se masquent
  dans le sub (KT5) ; raccourcir l'AMP du kick ou retirer la basse.
- Un breakdown de plus de 16 mesures à ce tempo fait retomber la salle
  (KT9) ; les références font 4 à 8.
- Le repliage de la passe cale le maximum : un `X` au pas 1 n'est pas
  forcément le kick ; lire les motifs, pas les positions.
- Tag `genre` de la library : « breakbeat » sur des tribe (Floxytek,
  Kodaman) ; les listes du hub font foi, pas le tag.

## Ressources

- Wikipedia, *Free tekno* : <https://en.wikipedia.org/wiki/Free_tekno> `[V]`
- Wikipedia, *Spiral Tribe* : <https://en.wikipedia.org/wiki/Spiral_Tribe> `[V]`
- Maelstrom, *10 best teknival anthems* :
  <https://dmy.co/news/the-10-best-teknival-anthems-according-to-maelstrom/> `[R]`
- Forum Renoise, kicks en couches :
  <https://forum.renoise.com/t/making-gabber-kicks-and-making-them-not-take-over-your-mix/44325> `[V]`
- Vault : [[../../../refs/free-tek-sources]], [[../../../inspirations/sets]]
  (rien d'écrit sur Heretik, Keja, Tekno Mental : à l'oreille).

## Liens

[[_index]] · [[../../doctrine]] §1, §9, §13 · [[../euclidien]] ·
[[../polymetrie]] · [[../lfo]] · [[../fill-conditions]] · [[../mutes]] ·
[[../kick-mental-vst]] · [[../../../technique/patches/tribe]] ·
[[../../../library/digitakt/kodaman_-_beton]] · KT1
[[kt-cellules-rythmiques]] · KT3 [[kt-swing-microtiming]] · KT5
[[kt-tonalite-du-grave]] · KT9 [[kt-phrasage-tension]] · KT11
[[kt-style-acidcore]]
