# Changelog

Toutes les évolutions notables du vault et des outils `scripts/`.
Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Les slices
renvoient aux phases de [[SPEC]]. Pas de `pyproject.toml` : la version vit ici.

## [Non publié]

## [0.7.0] - 2026-10-06

### Ajouté

- [7.A] Doctrine Digitakt II `digitakt/doctrine.md` : grille invariante des 16
  tracks, pattern modèle, convention de slots par bank, partition de mutes,
  fabrication des FX de transition (riser, FILL / NOT FILL), 12 principes de
  construction de set.
- [7.B] `scripts/digitakt.py` + `analyzer/digitakt.py` : draft de bank Digitakt
  depuis une track (1 section = 1 pattern, <= 128 pas, grille 16 tracks),
  partition de mutes par phrase, notes basse / lead par chroma, FX sur les
  drops. Sorties `library/digitakt/<slug>.{json,md}` et un `.mid` par pattern
  (canal = track). Modèles Pydantic `Digitakt*` dans `analyzer/types.py`.
- Tests `tests/test_digitakt.py` (15 tests, features synthétiques).

### Corrigé

- [7.B] Beats re-suivis sur la bande kick du stem drums : la grille du sidecar
  (tempo constant) dérive d'un temps en ~36 beats sur certaines tracks.
