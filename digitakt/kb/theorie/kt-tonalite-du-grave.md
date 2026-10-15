---
tags: [digitakt, kb, theorie, kt]
theme: Tonalité du grave
lot: 2
ordre: 5
styles: [tribe, acidcore, hard techno, frenchcore]
statut: draft
updated: 2026-10-15
---

# KT5 — Tonalité du grave

**En une phrase** : sous 120 Hz il n'y a de place que pour une note à la
fois, donc kick, rumble et basse doivent partager la même tonique ou sa
quinte, se répartir les bandes et se relayer dans le temps ; c'est le
grave qui fixe la tonalité du morceau, pas la mélodie.

## Signature

| Élément | Théorique | Mesuré | Lecture |
|---|---|---|---|
| Kick accordé | fondamentale 40-65 Hz, une note sur la queue | passe harmonique du hub : accords `5` et `sus2` dominants (berio C#5, kodaman D5, luche G#5) | le détecteur n'entend qu'une fondamentale et sa quinte : la tierce est absente du grave |
| Rumble | même note que le kick, 30-80 Hz, entre les coups | tribe sub `Xxx.X.x.Xx..Xxxx` (KT1) | de l'énergie sub sur les pas 2-3 : la queue du rumble après chaque kick |
| Basse en contretemps | tonique ou quinte, 80-250 Hz, `..x...x...x...x.` | acid sub `X.xxX.x.X.x.X.x.` | le `x` du pas 3 est la basse qui descend sous 200 Hz |
| Kickbass mental | kick long qui joue la note, pas de basse | nailik, ktc : sub `X...X...X...X...` net, mid `X..XX..x` | rien entre les kicks dans le sub : le kick tient tout le grave |

Passe harmonique : `scripts/kt_signatures.py --harmony`, table dans
[[_index]]. Sur 32 morceaux analysés, 17 ont une gamme « incertaine » (marge
inférieure à 0,05) : en techno la tonalité est une **tonique**, rarement
une gamme complète, et c'est le grave qui la porte.

## Vocabulaire

- **Tonique** : la note de repos du morceau, celle que tient le grave.
- **Fondamentale** : fréquence la plus basse d'un son périodique ; pour un
  kick, la note de sa queue, pas de son attaque.
- **Quinte** : 7 demi-tons au-dessus de la tonique (A → E) ; rapport de
  fréquences 3:2, la seule autre note stable dans le grave.
- **Kickbass** : kick long et accordé dont la queue joue la basse (mental,
  frenchcore) ; la track 9 reste vide.
- **Rumble** : queue réverbérée et saturée du kick, resamplée, accordée
  sur la même note (doctrine §9).
- **Bande** : zone du spectre tenue par un élément ; sub 30-80 Hz, grave
  80-120, bas-médium 120-250.
- **Masquage** : deux sons dans la même bande au même moment, dont le plus
  fort cache l'autre ; le mal du grave.
- **Repitch** : transposition qui change aussi la durée ; sur un kick, plus
  de deux ou trois demi-tons le dénature.
- **Battement** : oscillation lente entre deux fondamentales proches
  (50 et 52 Hz battent à 2 Hz) ; signe d'un grave désaccordé.

## Pourquoi ça marche

**Concret d'abord : les notes du grave en hertz.** La fondamentale d'un
kick techno tombe entre 40 et 65 Hz. Les notes de cette zone (La 440 Hz
comme référence, une octave = division par 2) :

| Note | Hz | Note | Hz |
|---|---|---|---|
| E1 | 41,2 | A1 | 55,0 |
| F1 | 43,7 | A#1 | 58,3 |
| F#1 | 46,2 | B1 | 61,7 |
| G1 | 49,0 | C2 | 65,4 |
| G#1 | 51,9 | C#2 | 69,3 |

Exemple de calcul : A1 = 440 / 2³ = 440 / 8 = 55 Hz ; F#1 = 55 ×
2^(−3/12) = 55 × 0,841 = 46,2 Hz. Un demi-ton dans cette zone vaut 2,5 à
4 Hz : un kick « un peu haut » de 3 Hz est **une note à côté**, et il bat
contre la basse.

**Pourquoi une seule note.** Sous 120 Hz, l'oreille ne sépare plus bien
deux hauteurs proches ; les enceintes et les subs de free party encore
moins. Deux fondamentales différentes dans le sub ne font pas un accord,
elles font une bouillie qui bat. D'où la règle de la doctrine §11 : la
tonique est fixée par le kick, rumble et basse s'y accordent, et la seule
autre note admise dans le grave est la **quinte**, dont la fréquence (3:2)
partage ses harmoniques avec la tonique. La tierce, qui dit majeur ou
mineur, vit une ou deux octaves plus haut, sur la track 10 ou 13 (KT6).

**Qui tient quelle bande, à quel moment.** Le partage se fait sur deux axes
(doctrine §9) :

| Élément | Bande | Moment | Track |
|---|---|---|---|
| Kick | 40-120 Hz + click 2-5 kHz | les temps | 1 |
| Rumble | 30-80 Hz | entre les kicks, ducké | 2 |
| Basse | 80-250 Hz + harmoniques | contretemps | 9 |
| Kickbass | 40-250 Hz | tout le temps | 1 (la 9 vide) |

Le chevauchement est normal, le conflit est la **même bande au même
moment**. La basse en contretemps n'est pas qu'un choix rythmique (KT1,
KT2) : c'est le partage du temps qui évite le partage impossible de la
bande.

**Kickbass : le cas où le kick est la basse.** En mental et en frenchcore,
le kick dure jusqu'au kick suivant et sa queue saturée joue la note. À
190 BPM, une noire = 60 / 190 = 0,316 s ; le kick doit retomber ou être
coupé juste avant. Le kick devient un instrument de hauteur : les
progressions se jouent par p-lock de `TUNE` sur la track 1 (tonique sur 4
mesures, quinte sur 4), ce que fait le frenchcore avec son pitched kick
(KT12). Plus de basse, plus de rumble : la track 1 tient le grave seule.

**Ce que disent les morceaux.** La passe harmonique ne trouve presque que
des accords `5` (tonique + quinte) et `sus2` : Kodaman *Beton* reste sur
D5 toute la section principale, Luche alterne G#5 et G#sus2, Berio tourne
sur C#5, F#sus2, G#5 (tonique, quarte, quinte en quintes nues). La tierce
est absente, et la gamme « incertaine » dans 17 cas sur 32 : la tonalité
techno, c'est une fondamentale tenue par le grave et une couleur modale
posée au-dessus, de façon assez discrète pour que le détecteur hésite.

## Sur la DT2

Grille de la [[../../doctrine]] §1 : kick 1, rumble 2, basse 9, lead 10.
Gestes : [[../rumble-grave]] (recette du rumble), [[../kick-mental-vst]]
(kickbass), [[../keyboard-gammes]] (tonique de la track).

1. **Mesurer la note du kick (5 min).** Kick seul sur la 1, accordeur ou
   analyseur via Overbridge (fiche [[../audio-routing-overbridge]]), lire
   la note sur la **queue**. L'écrire dans le nom du preset
   (`kick_tribe_F#`). Sans analyseur : basse 9 en sinus, chercher la note
   où le battement contre le kick disparaît.
2. **Tonique, quinte, tierce (10 min).** Kick F#, rumble 2 à `TUNE` 0,
   basse 9 sur F# en contretemps : propre. Basse sur C# (quinte) : encore
   propre, plus ouvert. Basse sur A (tierce mineure) : le grave se
   brouille ; monter la basse d'une octave : la tierce redevient lisible.
   Conclusion à entendre : la tierce vit au-dessus de 120 Hz.
3. **Kickbass contre kick + basse (5 min).** Même tonique F#. Pattern A :
   kick court, rumble, basse `..x.`. Pattern B : kickbass long sur la 1
   (fiche [[../kick-mental-vst]]), 2 et 9 mutées, p-lock `TUNE` +7 sur les
   kicks des mesures 3 et 4. Chaîner A et B : même tonalité, deux
   écritures du grave.

## Pièges

- Mesurer la note sur l'attaque du kick donne une note fausse (le click
  et le pitch envelope descendent) : toujours la queue.
- Tordre un kick de plus de deux ou trois demi-tons au `TUNE` le dénature
  (mou vers le bas, cartoon vers le haut, durée modifiée) : une famille de
  kicks par tonalité (doctrine §11, fiche [[../kick-mental-vst]]).
- Un kick court et sec n'a pas de note perceptible : c'est la basse qui
  fixe la tonique, et le rumble se cale sur elle.
- Rumble et basse mal accordés s'annulent par battement : vérifier la
  note avant de toucher aux niveaux (fiche [[../rumble-grave]]).
- Les filtres de la DT2 se règlent en valeurs, pas en hertz : étalonner
  une fois avec un analyseur (doctrine §9, fiche [[../filtres]]).
- Le rumble se juge au casque ou sur un sub ; sur des enceintes de bureau
  on le pousse toujours trop.

## Ressources

- Forum Renoise, *Making gabber kicks and making them not take over your
  mix* : <https://forum.renoise.com/t/making-gabber-kicks-and-making-them-not-take-over-your-mix/44325> `[V]`
  (click, corps, sub 50 Hz, filtrage de la queue).
- Attack Magazine, Beat Dissected *Dark techno rumble* :
  <https://www.attackmagazine.com/technique/beat-dissected/dark-techno-rumble/> `[V]`
- Ableton, *Sara Landry high-end hard techno* :
  <https://www.ableton.com/en/blog/sara-landry-high-end-hard-techno/> `[V]`
  (kick construit en premier, distorsion multi-étages).
- Elektronauts, *psytrance kick bass parameters* :
  <https://www.elektronauts.com/t/psytrance-kick-bass-parameters/253875> `[R]`
- Manuel DT2 OS 1.17, §11.5-11.8 (filtre, amp), §12.3 (sampling), §13
  (machines SRC, `TUNE`).

## Liens

[[_index]] · [[../rumble-grave]] · [[../kick-mental-vst]] ·
[[../keyboard-gammes]] · [[../filtres]] · [[../audio-routing-overbridge]]
· [[../../doctrine]] §3, §9, §11 · notebook
[[../../../sounddesign/rumble]] · KT6 [[kt-modes-techno]] · KT8
[[kt-accords-voicings]] · KT12 (frenchcore, à rédiger)
