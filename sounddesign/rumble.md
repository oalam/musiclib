---
tags: [sounddesign, rumble, kick, techno, tribe]
traitement: rumble
presets: [deep, gritty, kick_rumble]
---

# Rumble

## En une phrase

Le rumble est le **grondement grave qui roule entre les coups de kick** :
on l'entend sous le kick de la hard techno, de la tribe et de beaucoup de
sets de free party, comme une nappe de sub qui respire au tempo. Ici, on
le fabrique à partir d'un kick de la library : le kick est séquencé au
tempo, noyé dans une reverb, filtré pour ne garder que le grave, saturé,
puis creusé à chaque coup pour laisser passer le kick.

Exemple concret : `KIK DB 160 (1).wav` (pack Drumbrute) avec le preset
`deep` à 150 BPM donne une boucle d'une mesure de 4 × 60 / 150 = 1,6 s,
dont 85 % de l'énergie est sous 200 Hz, et qui baisse d'environ 16 dB à
chaque coup de kick (RMS 0,067 sur le coup contre 0,445 entre deux coups).

## Pourquoi ça marche

- **La reverb prolonge l'énergie du kick.** Un kick est une impulsion :
  quelques dizaines de millisecondes de sub qui chute de 150 à 50 Hz (voir
  [[../technique/anatomie-kick|anatomie du kick]]). Une grande reverb à
  100 % wet transforme chaque impulsion en une queue de plusieurs secondes.
  Au tempo, les queues se chevauchent : on obtient un bourdon grave continu
  dont la couleur dépend du kick d'origine.
- **Le filtrage garde le grave.** Une reverb sur un kick contient aussi le
  claquement de l'attaque, diffusé en souffle. Un passe-bas entre 150 et
  350 Hz ne laisse que le corps : c'est ce qui distingue un rumble d'une
  simple reverb de kick.
- **La saturation rend le grave audible.** Un sub pur (40-60 Hz) est
  inaudible sur un petit système et se perd dans le mix. La distorsion
  ajoute des harmoniques (80, 120, 160 Hz…) que l'oreille entend et qui
  reconstituent la fondamentale (phénomène de la fondamentale absente). Le
  second passe-bas, après la distorsion, retire les harmoniques aiguës
  qu'elle a créées.
- **Le sidechain sépare kick et rumble.** Kick et rumble occupent les mêmes
  fréquences : s'ils sonnent en même temps, ils s'additionnent en boue et
  mangent la marge du sound system. Le rumble est donc creusé à chaque coup
  (device `duck`) et remonte entre les coups : c'est ce mouvement de pompe
  qui le fait « rouler ».
- **Le grave se garde mono.** Sous 150 Hz, l'oreille ne localise plus ;
  une différence entre gauche et droite ne fait que créer des annulations
  sur un système mono, ce qui est le cas de beaucoup de sound systems de
  free party (voir [[../technique/sound-system-free-party|sound system]]).
- **Le rumble a une note.** La queue de reverb sonne à la hauteur du kick :
  un kick accordé (BD avec note, cf. la roue des notes de la vue Samples)
  donne un rumble accordé. Choisir un kick dans la tonalité du morceau
  évite que le grondement frotte contre la basse.

## La chaîne, device par device

Ordre du preset `deep` (chaîne « Rumble »). Chaque potard du rack porte la
même aide en infobulle.

### Réglages du traitement

| Réglage | Rôle | Repères |
|---|---|---|
| Tempo | tempo de la boucle et de la séquence du kick | 140-150 hard techno, 180-195 tribe |
| Mesures | longueur de la boucle (1 à 8) | 1 suffit pour un rumble régulier ; 2 ou 4 si `Coups / mesure` crée un motif |
| Coups / mesure | nombre de kicks par mesure | 4 = four on the floor ; 2 = demi-temps (rumble plus ample) ; 8 = croches (grondement serré) |
| Mode | **Boucle** ou **Un coup** | Un coup : un seul kick et sa queue complète (coupée à -60 dB sous la crête, puis fondu de 50 ms), sans tempo dans le nom ; tempo, mesures et coups sont ignorés |

Durée de la boucle : mesures × 4 × 60 / tempo. Exemple : 2 mesures à
185 BPM = 2 × 4 × 60 / 185 = 2,595 s.

### Reverb

Reverb algorithmique Freeverb (Schroeder-Moorer : peignes parallèles puis
passe-tout en série).

| Paramètre | Effet | Pour un rumble |
|---|---|---|
| Taille | longueur de la queue | 0,8 à 0,9 : les queues se chevauchent entre les coups ; au-delà, la queue déborde sur plusieurs mesures |
| Amortissement | absorption des aigus dans la queue | 0,5-0,6 = sombre et rond ; 0,3 = plus de grain, utile avant une saturation forte |
| Wet | niveau de la reverb | 1 |
| Dry | niveau du kick sec | 0 : le kick sec vit dans sa propre chaîne |
| Largeur | stéréo de la queue | 0 : mono dès la source |

### Passe-bas (avant la distorsion)

Filtre du 1er ordre (6 dB/oct). **Coupure** 200-350 Hz : plus bas, le
rumble est sourd et propre ; plus haut, la distorsion qui suit trouve plus
de matière et le son devient agressif.

### Distorsion

Saturation tanh. **Drive** en dB : 10-16 dB arrondit et densifie, 20-30 dB
écrase (preset `gritty`), au-delà le grondement devient un bruit. C'est le
réglage qui décide si le rumble passe sur un petit système.

### Passe-bas (après la distorsion)

Même filtre, plus bas que le premier (150-200 Hz) : retire les harmoniques
aiguës créées par la saturation. Pour un rumble plus « parlant », remplacer
ce device par un **Filtre** LP24 avec de la résonance (0,3-0,5) : la
coupure se met à chanter, et le nœud de la courbe se glisse en temps réel.

### Passe-haut

**Coupure** 30-40 Hz : retire l'infra-grave qui consomme de la puissance
sans être entendu et que beaucoup de systèmes ne reproduisent pas. À
monter (50-60 Hz) si le kick a déjà beaucoup de sub.

### Duck (sidechain)

Baisse le volume à chaque coup de la séquence, comme un compresseur en
sidechain déclenché par le kick, mais calé exactement sur la grille.
L'attaque **anticipe** le coup : le creux est complet quand le kick frappe.
La boucle commence et finit donc dans le creux (à -30 dB, environ 0,02
d'amplitude au lieu de 0,5) : jouée une seule fois, elle ne claque ni au
départ ni à l'arrêt.

| Paramètre | Effet | Repères |
|---|---|---|
| Profondeur | creux en dB à chaque coup | 24-30 dB : le kick sort seul ; 10-12 dB : le rumble reste présent sous le kick |
| Attaque | durée de la descente | 1-2 ms (au-delà, le début du coup bave) |
| Tenue | durée du creux complet | 20-40 ms, la longueur du « punch » du kick |
| Retour | durée de la remontée | 140-220 ms. À 185 BPM un temps dure 60 / 185 = 324 ms : un retour de 220 ms laisse peu de plateau ; 140 ms fait pomper davantage |

### Largeur stéréo

**Largeur** 0 = mono. Garder 0 pour un rumble destiné à un sound system.

### Master

**Limiteur** à -1 dB puis normalisation de crête (case « norm. » de la
tranche Master, -1 dBFS) : chaque rendu arrive au même niveau crête, ce qui
facilite la comparaison A/B et le gain sur la DT2.

### Chaîne « Kick »

Le kick sec, avec un passe-haut à 25 Hz. **Mutée** dans `deep` et
`gritty` (le rumble seul, à poser sous le kick d'origine), **active** dans
`kick_rumble` (kick et rumble dans la même boucle, gain du rumble à
-4 dB). Le bouton **S** (solo) permet d'écouter une chaîne seule sans
modifier le preset.

## Presets

| Preset | Tempo | Différences | Usage |
|---|---|---|---|
| `deep` | 150 | reverb sombre (amortissement 0,6), drive 14 dB, retour 220 ms | rumble rond sous un kick de hard techno |
| `gritty` | 185 | reverb plus claire (0,3), drive 26 dB, bande +4 dB à 120 Hz, ladder LP24 résonant, retour 140 ms | tribe : grondement qui pousse |
| `kick_rumble` | 150 | chaîne Kick active, rumble à -4 dB | écouter le couple, régler la profondeur du duck, ou jouer tel quel |

## Sur la Digitakt II

1. Dans la vue **Samples**, se placer sur un kick (`DRUMS/BD/...`) : c'est
   la source du rumble. Bouton « Changer dans Samples » pour y revenir ;
   « ▶ source » pour l'écouter en A/B.
2. Régler, puis **Rendre sur disque** : le wav part dans
   `SoundDesign/rumble/` (48 kHz, la fréquence native de la DT2) sous le
   **nom DT2** proposé à partir du kick, modifiable avant le rendu :
   `BD C Punch 01 dbr` à 150 BPM donne `RM 150 C Punch dbr` (le numéro de
   variante part d'abord pour tenir dans les 18 caractères).
3. **Verser** le rendu depuis la liste : il est copié dans le pack
   `Samples/SoundDesign/rumble/` et rangé, après la réanalyse de la
   bibliothèque, en `DRUMS/RM/<sous-dossier du kick>` (un kick de
   `DRUMS/BD/CLEAN` donne `DRUMS/RM/CLEAN`). Il suit ensuite le circuit
   habituel : écoute garder / écarter, puis export vers Transfer.
4. Sur la machine : **track 2**, juste après le kick (cf.
   [[../digitakt/doctrine|doctrine]] § 1 et 9). Rendu **Boucle** : sample
   en lecture **loop**, un trig au premier pas de chaque mesure. Rendu
   **Un coup** : un trig sur chaque pas du kick, comme le préconise la
   doctrine (§ 9) ; le rumble suit alors le motif du kick, fills compris.
   Le kick d'origine reste sur la track 1.
5. En live : muter la track du rumble dans un break (ou la passer en
   NOT FILL), la rouvrir sur le drop ; jouer le filtre de la track pour
   l'ouvrir progressivement.

## Pièges

- **Tempo différent** de celui du set : le duck tombe à côté des kicks.
  Rendre une version par tempo plutôt que de time-stretcher sur la machine.
- **Rumble trop fort** : il masque le kick. Régler d'abord la profondeur du
  duck, puis le niveau de la track.
- **Note qui frotte** : changer de kick plutôt que de filtrer davantage.
- **Queue trop longue** (taille > 0,9) : le rumble ne respire plus, et la
  jointure de la boucle peut cliquer (le pré-roll de 4 s ne suffit plus).

## Ressources

- Attack Magazine, [Adding reverb to a techno kick](https://www.attackmagazine.com/technique/tutorials/adding-reverb-techno-kick/) :
  la reverb en parallèle, sidechainée par le kick.
- Bonedo, [Bass Drum Rumble & Rattle for Techno](https://www.bonedo.de/artikel/bass-drum-rumble-rattle-for-techno) :
  rumble par effets de pièce sur le kick, passe-bas, variantes.
- Production Music Live, [6 steps to create that rumbling techno kick](https://productionmusiclive.com/blogs/news/6-steps-to-create-that-rumbling-techno-kick-you-love-with-johannes-menzel)
  (Johannes Menzel) : la recette pas à pas dans Ableton Live.
- Julius O. Smith (CCRMA, Stanford), [Freeverb](https://ccrma.stanford.edu/~jos/pasp/Freeverb.html)
  et [Schroeder Reverberators](https://www.dsprelated.com/freebooks/pasp/Schroeder_Reverberators.html) :
  ce que fait la reverb du device, à l'intérieur.
- Spotify, [pedalboard](https://spotify.github.io/pedalboard/) : la
  bibliothèque des plugins du moteur (paramètres exacts de chaque device).

#sounddesign #rumble
