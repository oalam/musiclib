---
tags: [digitakt, kb]
theme: Filtres (machines FLTR, base-width, enveloppe)
lot: 3
ordre: 14
manuel: "§11.5, §11.6, annexe A.3 (p55-56, 104-108)"
os: "1.17"
statut: draft
---

# Filtres : machines FLTR, base-width, enveloppe

**En une phrase** : chaque track a un filtre au choix (multimode, passe-bas
24 dB, EQ, comb, legacy DT1) avec sa propre enveloppe ADSR, plus un filtre
base-width (passe-haut + passe-bas en série) pour nettoyer.

## Gestes rapides

| Action | Touches |
|---|---|
| Page FLTR 1 (machine) | `[FLTR]` |
| Page FLTR 2 (base-width, délai d'enveloppe) | `[FLTR]` de nouveau |
| Changer de machine filtre | `[FUNC] + [SRC]`, catégorie FLTR |
| Délai d'enveloppe depuis la page 1 | `[FUNC]` + knob A |

| Machine | Son | Paramètres propres |
|---|---|---|
| MULTI-MODE | passe-bas → passe-bande → passe-haut | `FREQ`, `RESO`, `TYPE` |
| LOWPASS 4 | passe-bas 24 dB/oct | `FREQ`, `RESO` |
| EQ | bande paramétrique | `FREQ`, `GAIN`, `Q` |
| COMB- / COMB+ | résonances métalliques accordées | `FREQ`, `FDBK`, `LPF` |
| LEGACY | filtre de la DT1, LP ou HP | `FREQ`, `RESO`, `TYPE` |

Communs : `ATK`, `DEC`, `SUS`, `REL`, `ENV` (profondeur, bipolaire).
Page 2 : `BASE`, `WIDTH`, `BW.RT` (avant / après la machine), `KEY.T`,
`DEL`, `RSET`.

## Pas à pas : basse acid

1. Track 9, machine LOWPASS 4, `FREQ` bas, `RESO` haut.
2. `ENV` positif, `DEC` court, `SUS` 0 : chaque note « couine ».
3. Locker `ENV` ou `FREQ` sur quelques trigs (accents acid).
4. Page 2 : `BASE` un peu monté pour retirer le sub qui gêne le kick.

## En live techno

- Nettoyage systématique : `BASE` (passe-haut) sur tout ce qui n'est pas
  kick / rumble / basse, pour laisser le bas au kick.
- Rumble : LOWPASS 4 `FREQ` bas ; `WIDTH` pour borner le haut.
- COMB+ sur un hat ou une perc = tonalité métallique accordée, typée tribe.
- Le filtre est la cible n°1 des LFO de transition (cf. [[lfo]]).

## Pièges

- `BASE` 0 + `WIDTH` 127 = base-width neutre ; `BASE` 0 seul = passe-bas.
- Le manuel ne donne aucune correspondance en Hz pour `FREQ`, `BASE` ou
  `WIDTH`. *À vérifier sur la machine* : si l'EQ affiche sa fréquence
  centrale en Hz. Sinon, étalonner une fois via Overbridge + analyseur de
  spectre (SPAN) et noter ici les repères kick / rumble / basse (doctrine §9).
- `RSET` off : l'enveloppe ne repart pas à chaque trig.
- `RESO` élevée sur un son grave = pics de niveau dans le compresseur.

## À essayer (5 min)

Même hat sur MULTI-MODE, `TYPE` de passe-bas à passe-haut en jouant ; puis
COMB+ avec `FDBK` monté, et accorder `FREQ` sur la tonalité du morceau.

Source : manuel DT2 OS 1.17, §11.5, §11.6, annexe A.3.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=4916) : « Filter » (1:21:56) · DT2, 2024
- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=5227) : « New filter modes » (1:27:07) · DT2, 2024
- [loopop — DIGITAKT II vs OG Digitakt, detailed tutorial](https://youtu.be/nepWmWsq84g?t=595) : « Filter machines » (9:55) · DT2, 2024
- [loopop — DIGITAKT II vs OG Digitakt, detailed tutorial](https://youtu.be/nepWmWsq84g?t=700) : « Comb filter » (11:40) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=2849) : « Exploring the other filters » (47:29) · DT2, 2024
