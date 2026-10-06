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
- `RSET` off : l'enveloppe ne repart pas à chaque trig.
- `RESO` élevée sur un son grave = pics de niveau dans le compresseur.

## À essayer (5 min)

Même hat sur MULTI-MODE, `TYPE` de passe-bas à passe-haut en jouant ; puis
COMB+ avec `FDBK` monté, et accorder `FREQ` sur la tonalité du morceau.

Source : manuel DT2 OS 1.17, §11.5, §11.6, annexe A.3.
