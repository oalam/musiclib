---
tags: [digitakt, kb, theorie, kt]
theme: Acid core / mental
lot: 3
ordre: 11
styles: [acidcore, mental, hardtek]
statut: draft
updated: 2026-10-26
---

# KT11 — Acid core / mental

**En une phrase** : le mental remplace les percs du tribe par un kickbass
accordé qui tient tout le grave et par une ligne acid 303 dans le médium,
linéaire et martelée, dont la narration passe par le filtre, les accents
et les slides plutôt que par les notes ; une voix, trois à cinq notes en
phrygien ou pentatonique, 13 ou 15 pas pour que le motif glisse.

## Signature

Références : 8 morceaux acid core / mental du hub ([[_index]] : Six ou
Sept, Nailik, Diuko303, Captain 303, Luche, Teksa, KTC, Berio).

| Élément | Théorique | Mesuré | Lecture |
|---|---|---|---|
| Tempo | 170-200 | 144, 152 (× 2), 161,5 (× 4), 166,7 | la library mentale est à 150-165 ; le 180-200 reste à grabber |
| Kickbass (sub) | `X...X...X...X...`, rien entre | Nailik, KTC, Berio `X...X...X...X...` nets ; Six ou Sept, Captain 303 `X.x.X.x.` | moitié des morceaux : rien entre les kicks, le kick tient le grave ; l'autre moitié a une basse offbeat sous 200 Hz |
| Acid (mid) | `X.xx.xx.X.xx.xx.`, accents sur 1 et 9 | moyenne `X.xXx.xxX.xxX.xx` ; Nailik `X..XX..xX.xxX.xx` | motif `X..X` par temps, le « a » avant chaque temps : l'acid anticipe (KT3) |
| Hats (high) | sobres, `..x...x.` | Nailik `...X...X...xx.xx`, KTC `Xx.X...Xx.xXX.xX` | high clairsemé chez les plus « mentaux » : moins de percs que le tribe (doctrine §13) |
| Tonalité | phrygien ou mineur sur la tonique du kickbass | Neurotribe (tekno rapide) `Esus2 F5` (b2), Luche G# mineur harmonique, 5 pentatoniques / blues | la b2 en mouvement de basse ; gammes incertaines (KT6) |
| Swing | droit, accents | `swing` 0,76-0,95 sur 6 morceaux sur 8 | le plus anticipé de tous les styles : l'acid line pousse |

## Vocabulaire

- **Acid line** : séquence monophonique de type TB-303 : carré ou dent de
  scie, filtre passe-bas résonant, enveloppe de filtre.
- **Accent** : pas joué plus fort **et** avec plus d'ouverture de filtre
  ; sur la 303 c'est un seul bouton, sur la DT2 vélocité + lock de
  `FREQ`.
- **Slide** : glissement de hauteur jusqu'à la note suivante, sans
  nouvelle attaque (portamento) ; en 9.A, un pas long lié au suivant.
- **Env mod** : profondeur de l'enveloppe sur le cutoff ; la
  « morsure » de l'acid.
- **Résonance** : pic du filtre à la coupure ; haute = « wow », trop
  haute = sifflement.
- **Kickbass** : kick long, accordé, saturé, qui joue la basse (KT5) ; la
  track 9 reste vide (fiche [[../kick-mental-vst]]).
- **Longueur impaire** : track acid en 13 ou 15 pas contre le kick en 16,
  pour que le motif glisse (KT2).
- **Narration au filtre** : la forme du morceau est une courbe de cutoff
  et de résonance sur 16-32 mesures, pas une suite de notes.
- **Distorsion en série** : plusieurs étages de saturation douce plutôt
  qu'un seul fort ; gain staging entre les étages.
- **Mental** : le versant linéaire et martelé du hardtek (doctrine §13) ;
  l'Id mélodique devient acid, l'Id rythmique perd ses percs.

## Pourquoi ça marche

**Concret d'abord : une acid line de 16 pas.** Tonique F# au kickbass.
Track 10, 16 pas, trois notes : F# (1), G (b2), C# (5), une octave
au-dessus du kick. `X.xx.xx.X.xx.xx.` : accents (`VEL` 120, `FREQ` +20)
sur les pas 1 et 9, ghosts (`VEL` 70) ailleurs, slide de G vers F# sur
les pas 7-8 et 15-16. Cutoff bas, résonance moyenne. Puis la track en 15
pas : le motif recule d'un pas par mesure et revient en phase au bout de
15 mesures (ppcm(15, 16) = 240 pas, KT2). C'est la recette de MusicTech
et de la veille §B2 : slides et accents d'abord, notes ensuite.

**Pourquoi trois à cinq notes suffisent.** La 303 a été conçue pour
accompagner, pas pour jouer des mélodies ; ce qui s'entend d'une acid
line, c'est le **timbre qui bouge** (cutoff, résonance, env mod), les
accents et les slides. Avec une tonique, sa b2 et sa quinte, on a la
stabilité (1, 5), la tension (b2, KT7) et le mouvement (slide 1 → b2 →
1). Le générateur 9.A fait la même chose avec `--type` bas (pas
conjoints autour de la tonique) et `--density` 12-14 : beaucoup de pas
joués, peu de notes distinctes.

**Le kickbass tient le grave.** Dans la moitié des références, le sub
mesuré est `X...X...X...X...` sans rien entre les kicks : le kick long et
saturé joue la note (KT5), il n'y a ni basse ni rumble. La ligne acid
vit une à deux octaves au-dessus, dans le médium (500 Hz-2 kHz), et le
filtre la fait descendre vers le grave ou monter vers l'aigu sans jamais
toucher au sub. C'est la **séparation en fréquences** de KT5 poussée à
l'extrême : une track pour tout le grave, une track pour tout le
médium. L'autre moitié (Six ou Sept, Captain 303) garde une basse offbeat
`X.x.X.x.` : c'est l'acid tribe, à la frontière.
Mesuré le 2026-10-26 au profil du kick (KT23
[[kt-kickbass-contre-kick-basse]]) : sur Neurotribe et Six ou Sept, le sub
entre les kicks est dans le stem drums (+5,5 et +3,2 dB), le stem bass ne
porte rien (-2,7 et -17 dB), l'un saturé, l'autre sinus.

**Phrygien et b2.** Neurotribe fait bouger sa fondamentale de E à F : un
demi-ton, la b2 phrygienne (KT6) en mouvement de basse, le geste
« mental » le plus simple. Sur l'acid line, la b2 arrive en slide depuis
la tonique : le glissement d'un demi-ton est la tension la plus
économique de la gamme (KT7, rapport 16:15). Luche en G# mineur
harmonique ajoute la sensible : le même mécanisme, par en dessous (7 → 1).

**Narration au filtre.** Un morceau mental tourne 4 minutes sur la même
ligne ; ce qui change est le cutoff (de fermé à ouvert sur 32 mesures),
la résonance (montée avant le break), l'env mod, la distorsion. Un seul
paramètre à la fois (doctrine §6, KT9) : le filtre est le build, le
break est l'acid seule avec cutoff montant, le drop est le retour du
kickbass. Sur la DT2 : LFO lent sur `FREQ` (fiche [[../lfo]]), ou le
knob en perform kit (fiche [[../perform-kit-temp-save]]) ; Control All
sur `FREQ` pendant le break.

**Ce que disent les sources hypnotiques.** The Acid Mind
([[../../veille-theorie]] §F) donne un plan de 64 mesures qui est la
narration au filtre mise en forme : 16 mesures kick, basse et une phrase
de perc ; 16 avec une seconde voix et un petit changement tonal ; 16 où
un élément grave est retiré et la texture s'élargit ; 16 de retour de
l'élément manquant, accentué ou avec un jet de delay. Les breakdowns y
font **2 ou 4 mesures seulement**, le centre retiré et le rythme sec
exposé, graves rétablis à la fin du cycle. Les modulations durent 4 ou 8
mesures et **pas toutes sur la même division** ; on coupe un coup attendu
juste avant le retour de boucle ; des boucles de 3 ou 5 pas font le
déphasage (KT2, fiche [[../page-setup]]). Myloops ajoute que l'ouverture
du filtre se concentre sur les 3 ou 4 dernières mesures du bloc, pas en
rampe linéaire : sur la DT2, un LFO `WAVE` EXP plutôt que RAMP (fiche
[[../lfo]]).

**Anticipation maximale.** Le `swing` mesuré (énergie sur le « a »,
KT3) est le plus haut de tous les styles : 0,76 à 0,95 sur 6 morceaux
sur 8. L'acid line place ses accents sur les pas 4, 8, 12, 16, le pas qui
précède le temps, et le kickbass tombe sur le temps : la ligne **pousse**
le kick. Sur la DT2, c'est un placement de trigs, pas un swing.

**Distorsion en série.** Le kickbass et l'acid passent par deux ou trois
étages (overdrive de l'AMP, saturation du filtre, bitreduction légère,
fiche [[../amp-overdrive-bitreduction]]) plutôt qu'un seul étage à fond
: chaque étage ajoute des harmoniques sans écraser l'attaque. Le gain
staging entre étages est ce qui distingue un mental propre d'une bouillie.

## Sur la DT2

Grille de la [[../../doctrine]] §1 : kickbass 1, lead 10, Id2 13.
Gestes : [[../kick-mental-vst]], [[../keyboard-gammes]],
[[../parameter-preset-locks]], [[../lfo]], [[../page-setup]] (15 pas).
Tirages : générateur 9.A (vue « Acid · MIDI »).

1. **Slides et accents d'abord (10 min).** Track 10, 16 pas, une seule
   note (la tonique du kickbass, une octave au-dessus), gate court.
   Accents sur 1 et 9 (`VEL` 120 + lock `FREQ`), slides sur 7-8 et 15-16
   (note longue + note suivante). Écouter : ça groove déjà sans mélodie.
   Puis ajouter la b2 sur le pas 8 (arrivée du slide) et la quinte sur
   le pas 12.
2. **15 contre 16 (5 min).** Même ligne, `[FUNC] + [PAGE]`, PER TRACK,
   track 10 à 15 pas. Écouter 16 mesures : le motif tourne. Revenir à 16
   pas pour comparer ; garder 15 pour les plateaux longs.
3. **Narration au filtre (10 min).** Kickbass 1 sur F#, acid 10, hats
   5 sobres. 32 mesures : LFO lent (une période = 32 mesures) sur `FREQ`
   de la 10, de fermé à ouvert. Break de 8 mesures : kickbass muté,
   résonance montée à la main. Drop : kick remis, LFO relancé. Un seul
   paramètre, trois états.

## Pièges

- Kickbass et basse 9 ensemble : deux fondamentales dans le sub, elles
  battent (KT5) ; en mental, la 9 reste vide (grille §1 : une track vide
  reste vide).
- Résonance trop haute à 190 BPM : sifflement qui masque les hats ; la
  résonance se monte pour un break, pas pour un plateau.
- Trop de notes : au-delà de cinq notes distinctes, ce n'est plus une
  acid line, c'est une mélodie, et le filtre ne raconte plus rien.
- Slide sans retour à la tonique dans les deux pas suivants : faux, pas
  tendu (KT7).
- `A:B` compte les tours de la track : à 15 pas, `1:4` ne vaut plus « une
  mesure sur quatre » (KT2).
- Un seul étage de distorsion à fond écrase l'attaque du kickbass : deux
  ou trois étages doux (fiche [[../amp-overdrive-bitreduction]]).

## Ressources

- Attack Magazine, *How to make an acid house bassline* :
  <https://www.attackmagazine.com/technique/tutorials/how-to-make-an-acid-house-bassline/> `[V]`
- MusicTech, *Chicago-style acid bassline* (slides et accents d'abord,
  13 / 15 pas) :
  <https://musictech.com/guides/essential-guide/how-to-create-a-chicago-style-acid-house-bassline> `[V]`
- Attack Magazine, *30 years of acid* :
  <https://www.attackmagazine.com/features/long-read/you-just-have-move-your-feet-30-years-acid/> `[V]`
- Wikipedia, *Acid techno* : <https://en.wikipedia.org/wiki/Acid_techno> `[V]`
- Attack Magazine, Beat Dissected *Armando acid house* :
  <https://www.attackmagazine.com/technique/beat-dissected/armando-acid-house/> `[R]`
- The Acid Mind, *Hypnotic Techno: How Repetition, Space and Subtle Motion Build the Groove* :
  <https://www.theacidmind.com/2026/08/hypnotic-techno-repetition-space-production/> `[V]`
- Myloops, *Techno Automation: 11 Moves* :
  <https://www.myloops.net/using-automation-to-keep-techno-interesting> `[V]`
- SPEC Phase 9.A, règles de tirage (`scripts/analyzer/acid.py`).
- Rien d'écrit sur Teksa, Crystal Distortion, 69db : à l'oreille, sur les
  références du hub.

## Liens

[[_index]] · [[../../doctrine]] §9, §11, §13 · [[../kick-mental-vst]] ·
[[../keyboard-gammes]] · [[../parameter-preset-locks]] · [[../lfo]] ·
[[../page-setup]] · [[../amp-overdrive-bitreduction]] ·
[[../perform-kit-temp-save]] · [[../../../SPEC]] Phase 9.A · KT2
[[kt-polymetrie-polyrythmie]] · KT3 [[kt-swing-microtiming]] · KT5
[[kt-tonalite-du-grave]] · KT6 [[kt-modes-techno]] · KT7
[[kt-tensions-lignes]] · KT10 [[kt-style-tribe]] · KT19 (trance / psy, à
rédiger)
