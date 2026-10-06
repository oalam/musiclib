---
tags: [digitakt, kb, index]
manuel: "refs/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf"
os: "1.17"
updated: 2026-10-06
---

# Base de connaissance Digitakt II

Fiches courtes et pratiques, rédigées depuis le manuel (OS 1.17), dans l'ordre
de **préparation d'un set** : du projet vide au set prêt à jouer. Les
conventions (grille des 16 tracks, banks, mutes, FX) restent dans
[[../doctrine]] ; les fiches disent *comment le faire sur la machine*.

Format d'une fiche : frontmatter (`theme`, `lot`, `ordre`, `manuel`, `os`, `statut`),
puis *En une phrase*, *Gestes rapides*, *Pas à pas*, *En live techno*,
*Pièges*, *À essayer (5 min)*. `statut: draft` passe à `vérifié` une fois
testé sur la machine.

Recherche : panneau `/` du front ou `python scripts/kb.py search "..."`.

## Parcours dans l'ordre (Dataview)

Fiches rédigées, triées par lot puis par `ordre` (le numéro des tableaux
ci-dessous). Vue dynamique dans Obsidian (plugin Dataview) ; les tableaux
statiques plus bas restent la liste de référence, thèmes à rédiger compris.

```dataview
TABLE WITHOUT ID ordre AS "#", file.link AS "Fiche", lot AS "Lot", statut AS "Statut"
FROM "digitakt/kb"
WHERE ordre
SORT lot ASC, ordre ASC
```

Pour ne voir que ce qui reste à tester sur la machine : ajouter
`AND statut = "draft"` à la ligne `WHERE`.

## Lot 1 — Poser le cadre du projet

| # | Fiche | Manuel | Statut |
|---|---|---|---|
| 1 | [[projet-sauvegarde]] | §6.9, §14.1, §14.3 | draft |
| 2 | [[presets-kits-pool]] | §5, §9 | draft |
| 3 | [[copier-coller]] | §6.4, §10.1, §17 | draft |
| 4 | [[page-setup]] | §10.7 | draft |
| 5 | [[tempo-metronome]] | §7.3 | draft |

## Lot 2 — Remplir les patterns depuis les banks générées

| # | Fiche | Manuel | Statut |
|---|---|---|---|
| 6 | [[enregistrement-quantize]] | §10.2, §10.6 | draft |
| 7 | [[midi-config]] | §14.4 | draft (import multi-canal à vérifier) |
| 8 | [[parameter-preset-locks]] | §10.8 | draft |
| 9 | [[microtiming-retrigs]] | §10.4, §10.5, §11.3 | draft |
| 10 | [[euclidien]] | §10.3 | draft |

## Lot 3 — Sons et transitions

| # | Thème | Manuel | Statut |
|---|---|---|---|
| 11 | Sampling et resampling interne | §13 | à rédiger |
| 12 | Machines SRC | annexe A.2 | à rédiger |
| 13 | Amp, overdrive, bit reduction | §11.7, §11.8 | à rédiger |
| 14 | Filtres (machines FLTR, enveloppes) | §11.5, §11.6, A.3 | à rédiger |
| 15 | LFO (dont riser one-shot track 15) | §11.9-11.11, annexe C | à rédiger |
| 16 | Send FX et compresseur master | §12 | à rédiger |
| 17 | FILL et conditions de trig | §10.8 | à rédiger |

## Lot 4 — Structurer le set, puis le jouer

| # | Thème | Manuel | Statut |
|---|---|---|---|
| 18 | Song mode (rejouer la chaîne d'une bank) | §10.9 | à rédiger |
| 19 | Changer de pattern en live, chaînes | §10.1 | à rédiger |
| 20 | Mutes (globaux / de pattern) | §8.5 | à rédiger |
| 21 | Perform kit mode | §10.10 | à rédiger |

## Lot 5 — MIDI et intégration

| # | Thème | Manuel | Statut |
|---|---|---|---|
| 22 | CC et NRPN (prérequis Phase 7.E) | annexe B | à rédiger |
| 23 | Tracks MIDI pour piloter un synthé | §5.3.2, §16.3 | à rédiger |
| 24 | Audio routing et Overbridge | §6.6, §14.6 | à rédiger |
