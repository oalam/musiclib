---
tags: [digitakt, kb, tutos, samples, mixage]
theme: Pré-mastering d'un sample dans Live 12 Intro avant la DT2 — début et fin, EQ correctif, mono, son sur la ligne inclinée de Pro-Q 4, rendu 48 kHz
lot: 4
ordre: 8
source: "Synthackers (James Orvis), Digitakt II Course: Comprehensive Guide to Sample Management, https://www.youtube.com/watch?v=aTq7VydK8Bk (07:25-13:16) ; échange de travail du 2026-11-11"
auteur: Tom (méthode), rédaction à vérifier dans Live
modele: DT2
stack: [Ableton Live 12 Intro, FabFilter Pro-Q 4, Utility, Compressor, SPAN, Overbridge]
parent: maison-sounddesign-grave-live
statut: draft
updated: 2026-11-13
---

# Pré-mastering d'un sample pour la DT2 (Live 12 Intro + Pro-Q 4)

La règle est dans [[../../doctrine-samples]] (sections « Niveaux » et
« Pré-mastering »). Cette fiche est le pas à pas dans Live : un son entre
brut, il sort en WAV prêt pour la lib, **propre, à sa place dans le
spectre, sur la ligne, avec sa marge**.

**Exemple qui sert de fil** : le kick de
`<MEDIA>/Sets/solaris/C Groove (A# aeo 143)/kickbass_tribecore_A#_143/`,
puis un clap pris dans un pack. Les deux sortent sur la même ligne : dans
le pattern de la banque C, ils se mixent sans toucher aux niveaux de la
DT2.

## 0. Avant de commencer

| Quoi | Où | Pourquoi |
|---|---|---|
| Pro-Q 4 (version d'essai de FabFilter) | AU ou VST3 dans Live | seul EQ à creux étroits, mid / side, bandes dynamiques et analyseur incliné de la stack ; Live Intro n'a ni EQ Eight ni Spectrum |
| Projet modèle, groupes OB et SD | [[maison-sounddesign-grave-live]] §1.3 | le son se juge avec la DT2 qui joue le pattern de la banque |
| Live en 48 kHz | Preferences > Audio > Sample Rate = 48000 | fréquence native de la DT2 ; pas de conversion au rendu |
| Tempo de la banque | celui du dossier (`C Groove (A# aeo 143)` → 143) | longueurs de queue et boucles au bon tempo |
| Table par track | [[../../doctrine-samples]], « Par track : points de départ » | passe-haut, stéréo et dynamique de chaque famille ; cette fiche n'en recopie pas les valeurs |

## 1. La piste PREMASTER (une fois, dans le template)

Dans le groupe SD, une piste audio `PREMASTER`, avec cette chaîne, dans
l'ordre :

1. **Pro-Q 4 « CORRECTIF »** : coupures, creux, mid / side. Mode de phase
   **Zero Latency** ou **Natural Phase**, jamais Linear Phase (pré-écho
   devant les attaques).
2. **Compressor** (désactivé par défaut) : seulement pour les sons qui le
   demandent (étape 3.4).
3. **Utility** : le **gain** qui met le son sur la ligne. **Bass Mono**
   reste disponible si on ne fait pas le mono dans Pro-Q.
4. **Pro-Q 4 « LIGNE »** : aucune bande, il ne sert que d'analyseur, après
   le gain. C'est lui qu'on regarde pour la ligne.

Enregistrer le projet comme template (Save Live Set as Template) : la piste
revient à chaque nouveau projet de banque.

## 2. Étalonner la ligne (une fois)

La vidéo règle tout « sur la ligne ». Il faut donc d'abord choisir cette
ligne.

1. Sur Pro-Q 4 « LIGNE », dans les réglages de l'analyseur (survol du
   bouton Analyzer, en bas) : **Tilt = 4,5 dB/oct, à régler à la main** (le
   preset par défaut de Pro-Q 4 peut être à 0 dB/oct), **Range = 90 dB**,
   **Resolution = High**, affichage **Post**. Le spectre d'un mix équilibré
   devient à peu près horizontal. Ces réglages fixent la hauteur du spectre
   affiché : s'ils changent, la ligne change.
2. Activer **Freeze** (bouton du même panneau) : le spectre ne retombe plus
   et garde son maximum. Un one-shot ne dure que quelques centaines de ms, et
   il faut voir le haut de son spectre, pas une image au vol. Couper puis
   remettre Freeze entre deux sons, sinon l'ancien maximum reste affiché.
3. Poser sur PREMASTER un **kick de référence** (le meilleur kick validé
   de la banque). Fader à 0 dB, régler Utility pour que sa **crête monte à
   -6 dBFS** (mètre de la piste).
4. Rejouer le kick : relever, sur l'**échelle grise de l'analyseur** (à
   droite, de 0 à -90 dB ; pas l'échelle jaune du gain des bandes), la
   hauteur du haut de son spectre. **C'est la ligne.** Relevée le
   2026-11-12 sur le kick de référence à -6 dBFS de crête (mètre de Pro-Q :
   -5,9) :
   `ligne = -26 dB (échelle analyseur Pro-Q 4, Range 90 dB, Resolution High, tilt 4,5 ; lecture à ±1 dB)`.
   Repère visuel : juste sous le **+3 jaune** quand la plage d'affichage est
   à 12 dB. Le chiffre en haut du mètre de Pro-Q est un maximum mémorisé :
   cliquer dessus pour le remettre à zéro avant de lire la crête.
5. Enregistrer le réglage de Pro-Q 4 « LIGNE » comme preset `LIGNE DT2`.

Cette ligne est la même que celle de l'export : un son préparé ici ressort
de l'export à un gain proche de 0 dB.

## 3. Pas à pas pour un son

### 3.1 Début et fin

- Dans le clip, poser le **marqueur de début sur l'attaque** : aucun
  silence en tête, sinon le trig de la DT2 joue en retard.
- Couper la queue à la **longueur utile** au tempo de la banque (un kick
  avant rumble : 150-300 ms ; un clap : sa queue utile, pas sa reverb
  entière).
- **Fondu de sortie** de 5 à 20 ms (poignées de fondu du clip). Un fondu
  d'entrée seulement si l'attaque claque, et alors 1 ms au plus.

### 3.2 EQ correctif (Pro-Q 4 « CORRECTIF »)

1. **Coupure sous 20 Hz** pour tout le monde, kick compris : c'est sous
   l'audible, ce n'est pas le sub du kick ([[../../doctrine]] §9).
2. **Passe-haut de la famille**, d'après la table de la doctrine. Exemple :
   le clap coupé vers 150-200 Hz ; le kick, rien de plus que sous 20 Hz.
3. **Résonances** : une bande étroite, montée de 10 dB, promenée lentement
   sur le spectre pendant la lecture ; là où ça siffle ou sonne en boîte, la
   **baisser** de 3 à 6 dB, avec une bande assez étroite. Si la résonance
   n'apparaît que sur certaines notes, passer cette bande en **dynamique**.
4. Pour le kick, regarder aussi la vue des autres instances de Pro-Q
   (rumble, basse) : la queue du kick ne doit pas se superposer au rumble ou
   à la basse.

### 3.3 Mono

- **Grave (BD, RM, BS)** : entièrement mono. Au rendu, « Convert to Mono »
  (3.6) ; le fichier mono pèse aussi deux fois moins en RAM sur la DT2.
- **Les autres** : mono sous 120 Hz. Dans Pro-Q 4, une bande passe-haut à
  120 Hz réglée sur **Side** seulement ; ou Utility, Bass Mono à 120 Hz.
- La stéréo n'est gardée qu'où elle sert : OH, CY, PD, FX, boucles
  mélodiques.

### 3.4 Dynamique (si besoin seulement)

- **Jamais sur le kick** : sa marge sert à l'overdrive et au compresseur
  master de la DT2 ([[../../doctrine]] §10).
- Une boucle avec un pic isolé, une voix, une ligne dont une note dépasse :
  Compressor, ratio 2:1 à 3:1, attaque lente (10-30 ms) pour laisser passer
  l'attaque, 2-3 dB de réduction au plus.

### 3.5 Sur la ligne

1. Lire le son en boucle et regarder Pro-Q 4 « LIGNE » (tilt 4,5, maxima
   maintenus).
2. Régler le **gain d'Utility** jusqu'à ce que le haut du spectre **touche
   la ligne**, avec le décalage de la famille :
   - 0 dB pour la plupart ;
   - hats et cymbales un peu au-dessus ;
   - nappes un peu en dessous.

   Les valeurs exactes se fixent à l'oreille (doctrine, « Niveaux »).
3. Vérifier la **crête** au mètre de la piste : -6 dBFS au plus. Si la ligne
   demande plus, s'arrêter à -6 : c'est le plafond.
4. Ne pas normaliser.

Fil : le kick de C Groove touche la ligne à -6 dBFS de crête. Le clap,
coupé sous 200 Hz, touche la ligne par son médium (1-2 kHz) et sa crête
tombe autour de -12 à -10 dBFS. Il n'a pas besoin d'être plus fort.

### 3.6 Écouter dans le pattern, puis rendre

1. **Écoute** : la DT2 joue le pattern de la banque (groupe OB, Overbridge)
   et le son joue en même temps dans Live, ou il est envoyé à la machine par
   `SRC` = USB ([[maison-grave-rendu-dt2]] §7). Il ne part en rendu qu'une
   fois validé là.
2. **Rendu** (File > Export Audio/Video, Cmd+Shift+R), *noms de champs à
   vérifier dans Live 12* :

| Champ | Valeur | Pourquoi |
|---|---|---|
| Rendered Track | PREMASTER | la piste seule, avec sa chaîne |
| Render Start / Length | la sélection (une note, un temps, une mesure) | le fichier fait exactement la longueur voulue |
| Convert to Mono | **on** pour BD, RM, BS ; off sinon | grave mono, RAM divisée par deux |
| Normalize | **off** | garde la ligne et le plafond |
| Sample Rate | 48000 | fréquence native de la DT2 |
| Bit Depth | 24 | le passage en 16 bits avec dither est fait par l'export |
| Dither | aucun | pas de réduction de profondeur ici |

3. **Nom et place** : le nom porte la note et le tempo
   (`kickbass_tribecore_A#_143_kick.wav`), et le fichier reste dans le
   dossier de son projet sous `<MEDIA>/Sets/solaris/<banque>/`.

## 4. Pièges

| Piège | Ce qu'on entend ou voit | Parade |
|---|---|---|
| Linear Phase sur une percussion | un « souffle » avant l'attaque | Zero Latency ou Natural Phase |
| Analyseur sans maxima maintenus | le kick ne touche jamais la ligne, on le pousse trop | maintien des maxima, ou lire le son en boucle |
| Normalize au rendu | tout part à 0 dBFS, la ligne est perdue | Normalize off |
| Bass Mono sur une boucle de breaks | le kick de la boucle devient mono et plus présent | normal, la boucle doit perdre son grave (passe-haut 100-150 Hz) |
| Plafond oublié | une basse à -2 dBFS sature l'overdrive de la DT2 | crête à -6 dBFS au plus |
| Projet à 44,1 kHz | conversion au rendu, accordage faussé d'un cheveu | Preferences > Audio = 48000 avant de commencer |

## Liens

- [[../../doctrine-samples]] — la règle : ligne inclinée, plafond, table par track
- [[maison-sounddesign-grave-live]] — hub du lot 4, projet modèle, Live 12 Intro
- [[maison-grave-rendu-dt2]] — rendu et transfert, voie directe `SRC` = USB
- [[maison-etalonnage-presets-overbridge]] — la même ligne pour les presets de la DT2, lue par Overbridge
- [[../../doctrine]] — grille des tracks (§1), grave (§9), compresseur master (§10)

#digitakt #kb #tutos #samples #mixage
