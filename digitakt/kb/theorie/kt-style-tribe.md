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
| Rebond du kick | `X...X...X...X.X.` une mesure sur 2 ou 3 | trace : `x` sur les pas 2-3 d'un temps (Kodaman `XxX.xXx.`, Tekotak `X...X...X.x.X.x.`) ; par mesure (`kt_kick_bars.py`, grille de la bank) sur *Smash* : 64 mesures sur les temps, 10 de roulement, 19 avec rebond, 18 vides, halte de deux temps à chaque phrase de 4 | le repliage moyenne les mesures : le doublé apparaît en coup faible ; la passe par mesure montre le rebond, le halte et les roulements |
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
puisque le repliage moyenne les mesures) ; la périodicité se lit mesure
par mesure avec `scripts/kt_kick_bars.py` (stem drums, 8 croches par
mesure), ou s'écoute.

**Le martial par excellence : Kodaman x Mosmoz x Adharaa, *Smash*.** La
passe par mesure (`scripts/kt_kick_bars.py`, stem drums, grille re-suivie
par la bank à 156,6 BPM, 111 mesures) donne 64 mesures de kick sur les
temps, 10 de roulement de croches, 19 mixtes (rebonds), 18 vides, et
**aucune** mesure décalée d'une croche (une première passe sur la grille
fixe du sidecar à 152 BPM en avait montré 21 : c'était la dérive de la
grille, 3 % d'écart font glisser d'une croche en 4 mesures ; le script lit
maintenant la grille de la bank). Ce que le morceau fait vraiment :

```
mesures  1 à 4 d'une phrase (kick, 8 croches par mesure)
  ..X.X.X.  X.X.X.X.  X.X.X.X.  X.X.X...     le « halte » : deux temps sans kick à la jointure
  X.X.X.XX  XxX.X.X.  X.X.X.X.  X.X.X...     le rebond : 4, « et », 1, « et » = roulement de 4 croches autour du 1
  ..XXXxXx  XxXxX.Xx  X.XxX.X.  X.X.X.XX     le roulement long (peak, mesures 81 à 94)
```

Trois gestes, donc. Le **halte** : le kick se tait sur le temps 4 de la
dernière mesure et sur le temps 1 de la première, à chaque phrase de 4 ;
deux temps de silence du grave qui font « stop… marche ». Le **rebond**
avant le 1, comme décrit plus haut, mais sous forme de roulement de quatre
croches à cheval sur la barre (`X.X.X.XX | XxX.`), une phrase sur deux
dans les plateaux. Le **roulement long** en croches continues sur 6 à 8
mesures au peak, qui est le même geste étiré. Le martial vient de
l'alternance stricte halte / roulement / pas cadencé, à l'échelle de la
phrase de 4. Kodaman *Béton* (bank à 161,5, 137 mesures : 53 sur les temps,
0 décalée, 22 de roulement, 28 rebonds) fait exactement la même chose,
avec deux roulements longs de 6 à 8 mesures au peak : c'est une signature
d'écriture de Kodaman. Chez Floxytek (banks générées pour l'occasion,
grille re-suivie) : *Roots* est un four-on-floor droit, 81 mesures sur les
temps, 0 roulement, 17 rebonds ; *Micro Tribe* roule à l'intro
(`XxXxXxXx`, croches à accents alternés, 9 mesures) et fait 35 mesures
mixtes. Le halte et le roulement autour du 1 ne sont donc pas « le »
tribe, ils sont le martial de Kodaman ; le rebond simple, lui, est
partout.

**Tekotak, *L'okapi* : le doublé à période fixe.** Stems et bank générés
le 2026-10-15 (172,3 BPM, 243 mesures : 168 sur les temps, 0 décalée, 7
de roulement, 31 mixtes, 37 vides). Les plateaux sont écrits sur un cycle
de 4 mesures d'une régularité de métronome :

```
  X.X.X.X.  XxX.X.X.  X.X.X.X.  XXX.X.X.     le doublé sur le « et » du 1, faible une mesure sur deux, plein une sur quatre
  X.......  ..X.X.X.                          le halte long : le 1, puis rien jusqu'au temps 2 de la mesure suivante (3 temps et demi)
  X.X.X.XX  XXX.X.X.                          le rebond Kodaman, en tête des phrases du second plateau (mesures 113 à 125)
  X.X.X...  .xXXXXX.  X.X.X.X.                le roulement de fin de phrase : 6 croches, puis une croche vide avant le 1
```

C'est le **doublé martial** décrit plus haut, mesuré : un coup
supplémentaire d'une demi-croche tous les 2 mesures (80 mesures sur 243
ont un kick sur le « et » du 1, 52 fois à 2 mesures d'écart, 17 fois à 4),
accentué toutes les 4 pour marquer la phrase. Ici il tombe **après** le
1 (`XxX.`), pas avant : le « et » du 4 n'a aucune périodicité (22 mesures,
écarts quelconques). La position avant le 1 décrite plus haut reste
celle du rebond de Kodaman (`.XX | XxX.`) ; Tekotak place le même geste
de l'autre côté de la barre, ce qui donne un pas moins « tiré » et plus
« tamponné ». Son halte est plus long que celui de Kodaman (3 temps et
demi contre 2, toutes les 8 mesures dans le second plateau : mesures 37,
149, 157, 173) et son roulement de fin de phrase laisse une croche vide
avant le 1 (`.xXXXXX. | X.`), le trou avant la reprise. Trois écritures
martiales, donc : Kodaman alterne halte, rebond et roulement à l'échelle
de la phrase ; Tekotak tient un doublé à période 2 et ponctue la phrase ;
Floxytek ne fait ni l'un ni l'autre et roule à l'intro.

**Partition rythmique de *Smash*, mesure type du plateau** (pattern 04 de
la bank, 8 mesures ; draft `digitakt.py` sur les stems, seuil 0,5 ; grille
de la doctrine §1, rôles actuels) :

| Pas | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 Kick | X | | | | X | | | | X | | | | X | | | |
| 2 Rumble | | x | | | | x | | | | x | | | | x | | |
| 3 Clap | | | | | | | | | | | | | | | x | |
| 5 Hat fermé | | | | | | | | | | | | | x | | | |
| 6 Hat ouvert | | | | | | | | | x | | x | | | | x | |
| 8 Perc B | | | | | x | | | | x | | | | | | | |
| 9 Basse | | | x | | | | x | | | | x | | | | x | |

Lecture : le **rumble** est détecté sur le pas qui suit chaque kick (il
gonfle après l'attaque, ducké pendant, doctrine §9) ; la **basse** est en
contretemps strict (pas 3, 7, 11, 15, KT21) ; le clap tombe sur le pas 15,
une **anticipation** du 1 plutôt qu'un backbeat ; le hat ouvert vit sur la
seconde moitié de mesure (pas 9, 11, 15) ; la perc B double les temps 2 et
3. Au peak (pattern 07) : clap sur 3 et 15, hat ouvert en `..x.......x.x.x.`,
perc B en `....x...x.x.x...`, basse qui ajoute le pas 16 ; la dernière
mesure de chaque phrase de 4 retire le kick du pas 13 et la première celui
du pas 1 (le halte). Rebond : kick ajouté sur le pas 15 de la mesure 4 et
le pas 3 de la mesure 1. Sur la DT2 : halte par `NOT` condition ou lock
trig (deux trigs de kick en `4:4` et `1:4` retirés), rebond par deux trigs
ajoutés sous la même condition, roulement par retrig `RATE` 1/8 sur une
mesure (fiche [[../microtiming-retrigs]]).

**Le kick et le rumble de Kodaman, mesurés** (`scripts/kt_kick_profile.py`,
kick moyen sur 45 à 54 coups d'un plateau, stems Demucs) :

| | *Smash* (156,6, 54 kicks) | *Béton* (161,5, 45 kicks) |
|---|---|---|
| Enveloppe | pic, −12 dB à 4 ms, −24 dB à 72 ms : un click très fort puis un corps de 70 ms | −12 dB à 2 ms, −24 dB à 28 ms : kick très court, 30 ms |
| Hauteur de la queue | 91 Hz à 20 ms → 79 → 67 → 63 → 56 Hz (A1) à 130 ms : pitch envelope d'une octave sur 100 ms | 92 → 62 → 57 Hz (A#1) à 40-60 ms, puis plus rien : la descente est faite en 40 ms |
| Spectre du corps | 60-120 Hz dominant, sub 30-60 à −4 dB, 120-300 à −8, 300-1k à −13, 1-3k à −16 : riche jusqu'à 3 kHz | 60-120 dominant, 120-300 à −3 dB, 300-1k à −10 : encore plus d'harmoniques graves |
| Saturation | facteur de crête 5,6 dB, 9 % des échantillons à plus de 85 % du pic : crêtes **aplaties**, clipping ou saturation dure | facteur de crête 13,8 dB, 2 % : harmoniques riches mais crêtes intactes, saturation douce ou distorsion avant un transitoire préservé |
| La pointe d'aigus | centroïde des 8 premières ms à 2,6 kHz, 3-8 kHz à +9 dB sur l'attaque par rapport au corps : un click 1-3 kHz collé devant | centroïde à 670 Hz, 60-300 Hz à +7 dB sur l'attaque : un « knock » bas-médium plutôt qu'un click |
| Rumble entre les kicks | stem drums à **+7 dB** du sub de l'attaque, bass à −1 dB : le rumble est dans les drums, plus fort que le kick lui-même | drums à −13 dB, **bass à +12 dB** : le sub entre les kicks est tenu par la basse, le kick n'a pas de queue |
| Profil du sub sur un temps | 0, +3, +3, −8, −27, −33, −46, −16 dB par huitième de temps : gonfle 140 ms puis coupé net | 0, −6, −19, −24… : le sub du kick meurt en 100 ms |

Lecture pour la DT2. *Smash* est un **kick en deux étages** : un click
1-3 kHz de quelques millisecondes (c'est lui qui donne la « pointe
d'aigus »), puis un corps saturé à crêtes aplaties avec un pitch envelope
d'une octave, 90 vers 56 Hz, sur 100 ms (le « bouncy »), accordé sur A1.
Le rumble n'est pas une longue queue : c'est une **bosse de sub** qui
gonfle pendant 140 ms après chaque kick, 7 dB au-dessus du sub du kick,
puis **gate** net à la moitié du temps (chute de 30 à 45 dB) pour laisser
la basse en contretemps ; la bank le voit sur le pas qui suit le kick
(partition ci-dessus). *Béton* fait l'inverse : kick très court et
« knock » dans les bas-médiums, sans click, et un **rumble porté par la
basse** (stem bass à +12 dB) qui roule entre les kicks, la variante
« sans basse » de la doctrine §9. Recette *Smash* sur la machine :
click sur une track à part ou sample en couches (fiche
[[../kick-mental-vst]], trois couches de KT12), overdrive en deux étages
puis bitreduction légère (fiche [[../amp-overdrive-bitreduction]]), LFO
exponentiel sur `TUNE` relancé au trig (+12 demi-tons, 100 ms, fiche
[[../lfo]]) ; rumble 2 avec AMP attaque 20 ms / decay 120 ms et ducking
(fiche [[../rumble-grave]]), donc une bosse, pas une nappe. Réserve :
Demucs range le rumble tonal dans `bass` ou `drums` selon le morceau, d'où
les deux colonnes lues ensemble.

**Les kicks de Floxytek et de Tekotak, même passe** (plateaux : *Micro
Tribe* mesures 65 à 90, *Roots* 113 à 125, *L'okapi* 89 à 108) :

| | *Micro Tribe* (161,5, 88 kicks) | *Roots* (161,5, 51 kicks) | Tekotak *L'okapi* (172,3, 79 kicks) |
|---|---|---|---|
| Enveloppe | −12 dB à 4 ms, −24 dB à 94 ms : corps de 90 ms | large bande morte en 14 ms, mais le sub tient 130 ms (profil ci-dessous) | −12 dB à 8 ms, −24 dB à 58 ms : corps de 60 ms |
| Hauteur de la queue | 59 Hz à 5 ms puis 50 Hz (G1) stable de 20 à 90 ms : **pas** de pitch envelope | 57 Hz (A#1) à 5-20 ms, 44 Hz (F1) à 40 ms, puis 49-55 Hz : instable, posée sur F1, la tonique du morceau (F mineur) | 90 Hz à 5 ms → 85 → 76 → 66 Hz (C2) à 60 ms : pitch envelope de 5 demi-tons sur 60 ms, puis plus rien |
| Spectre du corps | sub 30-60 dominant, 60-120 à −12, 120-300 à −16, 300-1k à −24 : un **sub pur** | sub dominant, 60-120 à −6, 120-300 à −16, 300-1k à −31 : sub pur, encore plus propre | 60-120 dominant, **sub 30-60 à −13**, 120-300 à −11, 300-1k à −12, 1-3k à −15, 3-8k à −16 : spectre plat, kick de médiums sans sub |
| Saturation | facteur de crête 4,9 dB, **15 %** des échantillons au pic : le plus aplati des cinq, un sinus écrêté presque carré | facteur de crête 5,0 dB, 8 % : écrêté aussi | facteur de crête 12,1 dB, 1 % : crêtes intactes, harmoniques riches (−11 dB) et énergie jusqu'à 8 kHz : distorsion douce large bande, comme *Béton* |
| La pointe d'aigus | centroïde à 330 Hz, 3-8 kHz à +5 dB sur l'attaque : pas de click | centroïde à 320 Hz mais 3-8 kHz à **+12 dB** sur l'attaque : un snap bref et clair, 14 ms | centroïde à 2,2 kHz, 3-8 kHz à +3 dB seulement : un click présent mais peu contrasté, le corps est déjà brillant |
| Rumble entre les kicks | drums −10 dB, bass −11 dB : pas de rumble, le kick **est** le sub | drums **−6 dB**, bass −13 : rumble dans les drums, modéré | drums −9 dB, **bass +17,5 dB** : tout le sub est dans la basse |
| Profil du sub sur un temps | 0, −1, −8, −11, −10, −9, −11, −9 : le kick puis une nappe plate à −10 dB | 0, −1, −1, −9, −20, −24, −24, −18 : sub tenu 130 ms puis coupé de 20 dB, bosse plate gatée | 0, −7, −14, −19, −13… : le sub du kick meurt en 100 ms |

Lecture. Cinq kicks, trois architectures du grave. **Floxytek** : le kick
est un sinus de sub écrêté, sans click ni pitch envelope (*Micro Tribe*),
ou avec un snap bref devant (*Roots*) ; le rumble est faible ou absent,
le kick remplit lui-même le 30-60 Hz, et le sub reste tenu entre les
coups (nappe à −10 dB sur *Micro Tribe*, bosse plate de 130 ms gatée sur
*Roots*). C'est le « kick-sub » hardtek, et Demucs le confirme à sa
manière : sur toute la seconde moitié de *Micro Tribe* (mesures 97 à 136)
et le long break de *Roots* (30 à 98), le kick passe dans le stem bass
(35-130 Hz : drums à −37 dB, bass à −19 sur *Micro Tribe*), la passe par
mesure y lit des mesures vides et ces zones ne sont pas analysables.
**Tekotak** : l'inverse, un kick de médiums (le « tok », 60-120 Hz et
300 Hz-3 kHz, sub à −13 dB) avec une petite pitch envelope et une
distorsion douce, et **tout le sub dans la basse** (stem bass à +17,5 dB
du sub du kick) : l'architecture acid tribe, où le kick laisse le grave à
la ligne de basse (KT21) et peut donc être court, brillant et doublé sans
embourber le sub. **Kodaman** est entre les deux : kick saturé qui descend
jusqu'au sub, plus un rumble en bosse (*Smash*) ou une basse qui roule
(*Béton*). Sur la DT2, le choix se fait avant le sound design : qui tient
le 30-60 Hz, le kick (Floxytek : kick sinus long, `OVERDRIVE` fort,
pas de rumble, basse en contretemps dans les médiums), le rumble (Kodaman,
recette ci-dessus) ou la basse (Tekotak : kick court filtré passe-haut à
60 Hz, basse 9 qui porte le sub, doctrine §9) ; les trois ne tiennent pas
ensemble.

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
