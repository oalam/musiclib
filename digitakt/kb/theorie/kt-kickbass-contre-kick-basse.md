---
tags: [digitakt, kb, theorie, kt]
theme: Kickbass contre kick + basse en contretemps
lot: 2
ordre: 23
styles: [acidcore, tribe, hard techno, frenchcore]
statut: draft
updated: 2026-10-26
---

# KT23 — Kickbass contre kick + basse : qui tient le sub

**En une phrase** : il n'y a qu'une place sous 60 Hz et trois façons de la
remplir, le kick seul (kickbass), le kick plus un rumble, ou une basse qui
porte le sub pendant qu'un kick court claque au-dessus ; le choix se fait
avant le sound design, il décide de la longueur du kick, de ce que la
track 9 contient, et de la tension disponible en live.

Point laissé vide par toutes les sources écrites
([[../../veille-theorie]] §F) : cette KT ne tient que sur les mesures des
références de la library.

## Signature

Passe `scripts/kt_kick_profile.py <slug> <mesure> <mesure>` sur un plateau de
chaque référence avec stems : kick moyen recalé sur l'attaque, hauteur de la
queue, spectre, et **sub 30-100 Hz entre les kicks par stem** (drums, bass,
other), relatif au sub de l'attaque. Qui tient le sub entre deux kicks se lit
dans la colonne la plus forte.

| Morceau (BPM, temps) | Kick | Sub entre les kicks | Architecture |
|---|---|---|---|
| Neurotribe, *Le côté obscur* (161,5 ; 372 ms), mes. 100-130 | pitch envelope 84 → 57 Hz en 130 ms, corps centré 60-120 Hz, harmoniques 120-300 à -5,5 dB : **saturé** ; -24 dB à 128 ms | drums **+5,5 dB**, bass -2,7, other -37 ; profil sur un temps `0 +1 +1 -3 -7 -9 -8 -8` | **kickbass** : la queue tient le sub jusqu'au kick suivant, 8 à 9 dB sous l'attaque |
| Six ou Sept, *Acid Pirate* (143,6 ; 418 ms), mes. 76-100 | click puis **sinus de sub** : -12 dB à 6 ms, puis queue à 57 → 50 Hz, 60-120 Hz à -12, harmoniques à -17 : propre ; -24 dB à 138 ms | drums **+3,2 dB**, bass -17, other -19 ; profil `0 -1 -1 -2 -6 -18 -15 -6` | **kickbass** sinus, tenu une demi-noire puis trou de 18 dB et remontée avant le kick suivant (pickup ou attaque anticipée, à confirmer à l'oreille) |
| Floxytek, *Micro Tribe*, *Roots* (161,5) | sinus de sub écrêté, sans click ni pitch envelope (*Micro Tribe*) ou avec un snap bref (*Roots*) | nappe à -10 dB sur *Micro Tribe*, bosse plate gatée de 130 ms sur *Roots* ; rumble faible ou absent | **kick-sub** hardtek, variante du kickbass sans saturation ni note tenue |
| Kodaman, *Smash*, *Béton* (156-161) | kick saturé qui descend jusqu'au sub | rumble en bosse (*Smash*) ou basse qui roule (*Béton*) | **kick + rumble** : doctrine §9 |
| Tekotak, *L'okapi* (172,3) | kick de médiums, le « tok » (60-120 Hz et 300 Hz-3 kHz), sub à -13 dB, pitch envelope légère | stem bass à **+17,5 dB** du sub du kick | **kick + basse** : la 9 porte tout le sub |

Détail des cinq kicks tribe dans KT10 [[kt-style-tribe]] ; passe `--harmony`
dans [[_index]]. Signatures de sub de la passe drums (KT5) : kickbass
`X...X...X...X...` sans rien entre les kicks (Nailik, KTC), acid tribe
`X.x.X.x.` quand la basse en contretemps passe sous 200 Hz.

## Vocabulaire

- **Kickbass** : kick long, accordé, dont la queue joue la basse jusqu'au
  kick suivant ; la track 9 est vide (KT5, KT11).
- **Kick-sub** : kickbass sans note tenue, un sinus écrêté qui remplit le
  30-60 Hz à chaque coup (hardtek, Floxytek).
- **Kick + rumble** : kick court ou moyen, et la queue réverbérée resamplée
  sur la 2 qui roule entre les coups (doctrine §9).
- **Kick + basse** : kick court et brillant, la 9 porte le sub en
  contretemps ou en roulement (KT21).
- **Tenue du sub** : niveau du 30-100 Hz entre deux kicks, relatif à
  l'attaque ; -8 dB est une tenue, -18 dB un trou.
- **Durée utile du kick** : temps où la queue reste au-dessus de -24 dB ;
  rapportée au temps, elle dit si le kick peut tenir le sub (plus de la
  moitié du temps) ou doit le laisser (moins d'un quart).
- **Battement** : deux fondamentales proches dans le sub (KT5) ; ce qui
  arrive quand deux architectures cohabitent.

## Pourquoi ça marche

**Concret d'abord : le temps et la queue.** À 161,5 BPM, un temps vaut
60 / 161,5 = 0,372 s. Le kick de Neurotribe est à -24 dB après 128 ms, soit
128 / 372 = 34 % du temps, mais son sub tient à -8 dB sur toute la seconde
moitié du temps : la queue grave dure plus que l'enveloppe globale ne le
dit, parce que les médiums tombent vite et que le sub reste. C'est la
définition mesurable du kickbass : **le stem drums contient plus de sub
entre les kicks qu'à l'attaque** (+5,5 dB), et le stem bass n'apporte
rien (-2,7 dB). Chez Tekotak, l'inverse : le stem bass est à +17,5 dB du
sub du kick, le kick ne tient rien sous 120 Hz et peut donc être court
(le « tok »), doublé, roulé, sans jamais embourber le sub.

**Pourquoi une seule architecture à la fois.** Sous 120 Hz l'oreille ne
sépare plus deux hauteurs (KT5) : un kickbass sur la tonique et une basse 9
sur la même tonique ne s'additionnent pas, ils battent dès qu'ils sont à
quelques hertz, et masquent quand ils sont justes. Un rumble sous un
kickbass est redondant : la queue du kick **est** le rumble. D'où la règle,
qui est celle de la grille §1 : la 9 est vide en kickbass, la 2 est vide en
kick + basse, et le kick est court dans les deux cas où il ne tient pas le
sub.

**Ce que chaque architecture permet.** Le kickbass donne la pression
continue du mental : le grave ne respire jamais, la tension vient du
filtre et de la distorsion de la ligne acid au-dessus (KT11), et du trou
de kick qui est aussi un trou de basse (KT21). Il interdit le double kick
et les roulements de kick (la queue du premier mange le second) et il
contraint le tempo : à 190 BPM le temps fait 316 ms, une queue qui tient
250 ms demande un kick très sinus ou très court, et le mental à 190 tend
vers le kick-sub de Floxytek plutôt que vers le kickbass saturé de
Neurotribe. Le kick + basse donne le rebond tribe : kick court, roulements,
haltes et doublés (KT10, passe drums : `XxX.X.X.`, `..X.X.X.`), et une
basse qui peut jouer un rythme et deux notes (KT21) ; sa tension vient de
la soustraction, couper la 9 en gardant le kick. Le kick + rumble est
l'entre-deux hard techno et tribe posé : la pression du rumble avec un kick
encore assez court pour le double kick (KT13).

**Deux kickbass, deux sons.** Neurotribe sature : harmoniques 120-300 Hz à
-5,5 dB sous le fondamental, pitch envelope de 84 à 57 Hz (E2 → A#1), un
kick qui se fait entendre sur un petit système par ses harmoniques (voir
[[../../../sounddesign/rumble]], fondamentale absente). Six ou Sept reste
sinus : harmoniques à -17 dB, click de 6 ms puis sub pur à 57 → 50 Hz, un
kick qui n'existe que sur un sub. Le premier est le kickbass de free party,
le second celui du club ; sur la DT2, c'est `OVER` et le filtre qui font
la différence, pas le sample (fiche [[../kick-mental-vst]]).

**Passer d'une architecture à l'autre en set.** Jamais dans un pattern, ni
dans une bank : c'est un changement de kit et de banque (doctrine §13), et
il passe par un break où le grave est absent, pour que l'oreille perde la
référence du sub avant d'en recevoir une autre. Un live tribe qui ouvre
vers le mental change d'architecture une fois, au milieu, pas à chaque
morceau.

## Sur la DT2

Grille de la [[../../doctrine]] §1 : kick 1, rumble 2, basse 9. Gestes :
[[../kick-mental-vst]] (kickbass), [[../rumble-grave]] (rumble),
[[../filtres]], [[../amp-overdrive-bitreduction]], [[../send-fx-compresseur]]
(ducking), [[../keyboard-gammes]] (note).

1. **Mesurer la tenue du sub (5 min).** Kick seul sur la 1 en four-on-floor,
   Overbridge et analyseur (fiche [[../audio-routing-overbridge]]) : lire
   le niveau du 30-100 Hz juste avant le kick suivant. Au-dessus de -10 dB
   par rapport à l'attaque, le kick tient le sub : kickbass, la 9 reste
   vide. En dessous de -20 dB, il le laisse : la 2 ou la 9 doit le prendre.
2. **Trois architectures, même tonique (15 min).** Tonique F#. Pattern A,
   kickbass : kick long (`DEC` jusqu'au kick suivant, `OVER` poussé, LOWPASS
   4 pour couper au-dessus de 300 Hz), 2 et 9 vides, acid sur la 10. Pattern
   B, kick + rumble : kick court (AMP 80 ms), rumble 2 sur les mêmes pas,
   ducking `SCS` = TRK1, basse 9 en contretemps dans les médiums (passe-haut
   monté). Pattern C, kick + basse : kick court passe-haut à 60 Hz, 2 vide,
   basse 9 en sinus sur la tonique `..x...x...x...x.` puis en roulement.
   Chaîner A, B, C, 16 mesures chacun : trois graves, une tonalité.
3. **Le mélange interdit (5 min).** Pattern A avec la basse 9 démutée sur la
   tonique : entendre le battement et le masquage ; monter la basse d'une
   octave : ça passe, mais ce n'est plus une basse, c'est une ligne (KT7).
   Remuter la 9 : conclusion à garder dans le kit.
4. **Kickbass à 190 (5 min).** Pattern A à 190 BPM : le temps fait 316 ms,
   la queue déborde sur le kick suivant. Raccourcir `DEC` jusqu'à ce que le
   sub soit propre, écouter ce qu'il reste ; puis remplacer par un sinus
   écrêté (kick-sub Floxytek, `OVER` fort sur un sinus court). C'est le
   kickbass du tempo tribe.

## Pièges

- Kickbass et basse 9 ensemble sur la même tonique : battement et masquage,
  pas un renfort (KT5, KT11).
- Rumble sous un kickbass : redondant, deux fois le même sub ; la 2 reste
  vide (grille §1).
- Juger la tenue du sub sur des enceintes de bureau : on n'entend ni le sub
  tenu ni le trou ; casque fermé ou sub, et l'analyseur pour la mesure.
- Un kickbass saturé à 190 BPM : la queue mange le kick suivant ; c'est le
  tempo qui choisit entre kickbass saturé (jusqu'à 165) et kick-sub.
- Demucs range la queue tonale du kick dans le stem bass sur certains
  passages (KT10, *Micro Tribe*) : lire les trois colonnes du profil
  ensemble, pas la seule colonne bass.
- La note se mesure sur la queue, pas sur l'attaque (KT5) ; sur Six ou
  Sept la f0 saute à 200 Hz à 60 et 130 ms, artefact de l'autocorrélation
  sur un sinus presque pur : les lectures 20-40 et 90 ms font foi.

## Ressources

- Passe `scripts/kt_kick_profile.py` sur `neurotribe_-_le_cote_obscur`
  (mes. 100-130) et `six_ou_sept_-_acid_pirate_vendetta_acidcore_mentalcore`
  (mes. 76-100), banks générées le 2026-10-26 ; profils tribe dans KT10.
- Aucune source écrite ne traite le kickbass contre kick + basse en techno
  rapide ([[../../veille-theorie]] §F) ; la seule phrase trouvée, forum
  Audiofanzine 2019 : « pour une basse en contretemps, decay court ».
- Myloops, *Techno Kick Rumble* (bandes : sub 20-60 Hz au kick seul) :
  <https://www.myloops.net/creating-techno-kick-rumbles> `[V]`
- Manuel DT2 OS 1.17, §11.5-11.8 (filtre, amp, FX), §12.6 (compresseur).

## Liens

[[_index]] · KT5 [[kt-tonalite-du-grave]] · KT10 [[kt-style-tribe]] · KT11
[[kt-style-acidcore]] · KT13 [[kt-style-hard-techno]] · KT21 [[kt-basses]]
· [[../kick-mental-vst]] · [[../rumble-grave]] · [[../filtres]] ·
[[../audio-routing-overbridge]] · [[../../doctrine]] §1, §9, §11, §13 ·
notebook [[../../../sounddesign/rumble]] · [[../../veille-theorie]] §F ·
fabrication des trois architectures sur le Mac
[[../../../technique/sounddesign-grave-reaper]] §3 à §6
