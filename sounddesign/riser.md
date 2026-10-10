---
tags: [sounddesign, riser, transition, fx]
traitement: riser
presets: [white_sweep, pink_thin, pad_lift]
---

# Riser

## En une phrase

Le riser est la **montée qui annonce un retour** : un bruit ou un son tenu
dont le filtre s'ouvre, le volume monte et l'espace s'épaissit pendant
quelques mesures, puis qui **s'arrête net** sur le temps où le kick revient.
C'est la track 15 de la doctrine (FX de transition, [[digitakt/doctrine]] § 5).

Exemple concret : le preset `white_sweep` à 150 BPM sur 4 mesures donne un
rendu de 4 × 4 × 60 / 150 = 6,4 s. Mesuré par quarts de durée, son niveau
RMS passe de 0,003 à 0,006, 0,022 puis 0,152 : à peu près × 50 entre le
premier et le dernier quart. Sa dernière valeur est 0 (fondu de 5 ms), mais
5 ms plus tôt le bruit est encore plein : la coupure s'entend comme une coupure.

## Pourquoi ça marche

- **L'oreille anticipe une montée.** Un son dont la hauteur ou la brillance
  augmente régulièrement crée une attente : on sait qu'« il va se passer
  quelque chose » et on sent à peu près quand.
- **La brillance compte plus que le volume.** Ouvrir un passe-bas sur du
  bruit blanc fait entrer de plus en plus d'aigus : le son paraît monter
  même à hauteur fixe (le bruit n'a pas de hauteur).
- **La courbe lente puis rapide** (courbe 2) garde l'essentiel de la
  montée pour la fin : la tension croît le plus fort juste avant le retour.
- **Le silence fait l'impact.** Couper net sur le temps, sans queue de
  reverb, laisse un trou d'une fraction de seconde que le kick vient combler.
  Une queue qui déborde sur le drop le salit.

## La chaîne, device par device

L'automation (bouton ↗ sous un potard) donne à un paramètre une valeur de
**fin** : il part de la valeur du potard et l'atteint à la fin du rendu,
selon la courbe du traitement. Les fréquences montent de façon
géométrique : de 200 Hz à 14 kHz, la moitié du temps (en courbe 1) mène à
200 × √(14000 / 200) ≈ 1,7 kHz, ce qui s'entend comme un balayage régulier.

### Réglages du traitement

| Réglage | Rôle |
|---|---|
| Tempo | Pour que la montée dure un nombre exact de mesures. |
| Mesures | Durée de la montée (1 à 16) ; 4 ou 8 sont les plus courants. |
| Source | Bruit blanc, bruit rose (plus doux, plus de grave) ou le sample en cours de la vue Samples, joué en boucle. |
| Hauteur | Montée de hauteur en demi-tons (varispeed : le son accélère). Sans effet audible sur un bruit blanc, très net sur une nappe. |
| Courbe | 1 = linéaire, 2 = lente puis rapide (défaut), < 1 = rapide puis plateau. Elle pilote aussi la hauteur. |

### Filtre

Le cœur du riser. En **LP** (passe-bas), la coupure s'ouvre du grave vers
l'aigu : le son s'éclaircit. En **HP** (passe-haut), la coupure monte et
vide le grave : le son s'amincit et laisse la place au kick qui revient. La
résonance accentue la zone de la coupure : un sifflement qui suit le
balayage, à automatiser elle aussi pour un effet plus agressif.

### Gain

Le volume qui monte. Partir bas (−24 à −40 dB) : l'entrée du riser doit
passer presque inaperçue.

### Reverb

Épaissit et éloigne. En fin de montée, plus de wet (ou moins de dry) donne
l'impression que le son remplit la salle. Sur la chaîne « Air » de
`white_sweep`, une reverb 100 % wet, filtrée au-dessus de 3 kHz, ajoute un
souffle large.

### Delay

Une réinjection (feedback) qui monte fait s'empiler les échos : la densité
augmente. À garder sous 0,7 pour que les échos ne s'emballent pas.

### Limiteur

En master : tient la crête pendant que tout monte. Le rendu est ensuite
normalisé à −1 dBFS.

## Presets

| Preset | Son | Usage |
|---|---|---|
| `white_sweep` | Bruit blanc, LP 200 Hz → 14 kHz, souffle de reverb qui monte | Le riser classique, avant un drop |
| `pink_thin` | Bruit rose, HP 40 Hz → 5 kHz, delay qui s'empile, 8 mesures | Montée longue qui vide le grave avant le retour du kick |
| `pad_lift` | Le sample en cours monte d'une octave, filtre et reverb qui s'ouvrent | Montée mélodique, à partir d'une nappe ou d'un drone |

## Sur la Digitakt II

- **Track 15** (FX de transition). Le rendu est rangé en `FX/RISE` une fois
  versé.
- **Riser + fill** (doctrine § 5) : trig du riser en condition **FILL** sur
  le premier pas de la montée, kick en **NOT FILL**. On maintient fill, le
  kick disparaît et le riser monte ; on relâche sur le temps, le kick revient.
- **Longueur** : rendre au tempo du set et à la durée de la montée voulue.
  Un riser de 4 mesures à 150 BPM se déclenche 4 mesures avant le retour.
- La DT2 sait aussi faire un riser à la volée (LFO en rampe, mode ONE, sur
  la coupure) : le rendu d'ici sert quand on veut une montée travaillée
  (plusieurs chaînes, hauteur, reverb) prête à jouer.

## Pièges

- **Queue après la coupure** : il n'y en a pas, c'est voulu. Pour un
  retour plus doux, réduire le nombre de mesures plutôt que d'ajouter une
  queue.
- **Sample bouclé qui claque** : la jointure de la boucle n'est pas fondue.
  Choisir un son tenu sans attaque (nappe, drone, bruit du pack).
- **Trop de grave** : un bruit rose ou une nappe à pleine bande sous le
  kick qui revient bave. Un HP qui monte (`pink_thin`) règle le problème.
- **Résonance haute + coupure en fin de course** : sifflement strident vers
  14 kHz ; baisser la résonance de fin ou arrêter la coupure plus bas.

## Ressources

- [[digitakt/doctrine]] § 5 « Fabriquer les FX de transition » : riser,
  riser + fill, downlifter, impact, reverse.
- [[digitakt/kb/_index]] : fiches LFO (riser one-shot) et FILL / conditions
  de trig.
- [[sounddesign/rumble]] : le notebook du premier traitement (même rack).
- pedalboard (Spotify), plugins utilisés : https://spotify.github.io/pedalboard/

#sounddesign #riser
