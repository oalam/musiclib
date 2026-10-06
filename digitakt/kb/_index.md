---
tags: [digitakt, kb, index]
manuel: "refs/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf"
os: "1.17"
updated: 2026-10-06
---
ok
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

| # | Fiche | Manuel | Statut |
|---|---|---|---|
| 11 | [[sampling-resampling]] | §13 | draft |
| 12 | [[machines-src]] | annexe A.2 | draft |
| 13 | [[amp-overdrive-bitreduction]] | §11.7, §11.8 | draft |
| 14 | [[filtres]] | §11.5, §11.6, A.3 | draft |
| 15 | [[lfo]] | §11.9-11.11, annexe C | draft |
| 16 | [[send-fx-compresseur]] | §12 | draft |
| 17 | [[mixer-setup]] | §6.2.2, §9.8, §12.6-12.9 | draft |
| 18 | [[fill-conditions]] | §10.7.3, §10.8.4 | draft |

## Lot 4 — Structurer le set, puis le jouer

| # | Fiche | Manuel | Statut |
|---|---|---|---|
| 19 | [[song-mode]] | §10.9 | draft |
| 20 | [[patterns-chaines]] | §10.1, §10.7 | draft |
| 21 | [[mutes]] | §8.5.3 | draft |
| 22 | [[perform-kit-temp-save]] | §10.10, §10.8.6 | draft |

## Lot 5 — MIDI et intégration

| # | Thème | Manuel | Statut |
|---|---|---|---|
| 23 | CC et NRPN (prérequis Phase 7.E) | annexe B | à rédiger |
| 24 | Tracks MIDI pour piloter un synthé | §5.3.2, §16.3 | à rédiger |
| 25 | Audio routing et Overbridge | §6.6, §14.6 | à rédiger |
