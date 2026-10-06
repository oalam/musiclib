---
tags: [digitakt, kb]
theme: Changer de pattern en live, chaînes
lot: 4
ordre: 20
manuel: "§10.1, §10.7 (CHANGE / RESET), §14.4.1 (p40-41, 46-47)"
os: "1.17"
statut: draft
---

# Changer de pattern en live, chaînes

**En une phrase** : un pattern choisi pendant la lecture se met en file
d'attente et démarre à la fin du pattern en cours ; une chaîne aligne
jusqu'à 64 patterns qui s'enchaînent seuls, mais elle n'est jamais
sauvegardée.

## Gestes rapides

| Action | Touches |
|---|---|
| Pattern de la bank courante | `[PTN] + [TRIG 1-16]` |
| Pattern d'une autre bank | `[PTN]`, `[LEFT]/[RIGHT]` pour la bank, `[TRIG 1-16]` |
| Variante façon anciens Elektron | `[FUNC] + [PTN]`, `[TRIG 9-16]` = bank A-H, puis `[TRIG 1-16]` |
| Ouvrir le créateur de chaîne | `[PTN]` puis `[FUNC] + [YES]` |
| Retirer le dernier pattern de la chaîne | `[FUNC] + [LEFT]` (dans le créateur) |
| Chaîne rapide (méthode legacy) | maintenir `[PTN]` + 1er `[TRIG]`, puis les suivants en gardant le précédent enfoncé |
| Arrêt avec coupure des queues de FX | `[STOP]` `[STOP]` |

Lecture des touches en `[PTN]` : blanche = pattern rempli, rouge = pattern
actif, éteinte = vide. Le pattern en attente clignote en haut à gauche de
l'écran.

## Pas à pas : enchaîner intro → main → break

1. Pendant la lecture de l'intro (slot 01) : `[PTN]`, puis `[FUNC] + [YES]`.
2. Taper `[TRIG 1]`, `[TRIG 2]`, `[TRIG 3]`, `[TRIG 2]` : intro, main, break,
   main.
3. `[YES]` : la chaîne part à la fin du pattern en cours, puis boucle.
4. Pour en sortir : choisir un pattern seul (`[PTN] + [TRIG]`).
5. Pour garder l'ordre : le transformer en song (`CREATE ROWS FROM CHAIN`,
   cf. [[song-mode]]).

## En live techno

- Les patterns de 8 mesures font des bascules lentes : choisir le suivant
  **tôt**, il attend la fin. Pour basculer plus vite sans raccourcir le
  pattern, régler `CHANGE` sur 16 ou 32 pas (cf. [[page-setup]]).
- La file d'attente laisse le temps de préparer le pattern suivant pendant
  que le riser `LST` de la track 15 marque le dernier tour (cf.
  [[fill-conditions]]).
- Peu de bascules par morceau : la doctrine fait vivre un pattern plein par
  les mutes (cf. [[mutes]]) et garde les changements de pattern pour les
  grosses ruptures.
- Changer de pattern recharge son kit : pour garder les réglages tournés en
  live d'un pattern à l'autre, passer en perform kit (cf.
  [[perform-kit-temp-save]]).
- Un séquenceur externe peut changer de pattern par program change (cf.
  [[midi-config]]).

## Pièges

- La chaîne est perdue en créant une autre chaîne, en choisissant un pattern
  ou un song, et à l'extinction.
- `RESET` sur `INF` avec `CHANGE` sur `OFF` : le pattern en attente ne part
  jamais.
- `[FUNC] + [YES]` hors écran `[PTN]` fait un temp save, pas une chaîne.
- `[STOP]` laisse sonner les delays et reverbs ; `[STOP]` `[STOP]` les coupe
  presque net.

## À essayer (5 min)

Chaîne 01-02-03-02 en lecture ; pendant le break, choisir 01 à la main et
vérifier qu'on sort de la chaîne à la fin du break.

Source : manuel DT2 OS 1.17, §10.1, §10.7.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [XNB — DIGITAKT II Song Mode & Chain](https://youtu.be/55fCA4d2vNw?t=40) : « Chain » (0:40) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=3831) : « Queue up pattern change » (1:03:51) · DT2, 2024
- [Synthackers — Optimise Your Workflow with Sequencer Page Setup](https://youtu.be/5zCFR5911zY?t=291) : « Pattern Change » (4:51) · DT2, 2024
- [Hexwave — New Conditional Trigs For Easy Hands-Free Transitions](https://youtu.be/DLi1B6ia-_M) (vidéo entière) · DT2, 2024
