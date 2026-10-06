# Changelog

Toutes les évolutions notables du vault et des outils `scripts/`.
Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Les slices
renvoient aux phases de [[SPEC]]. Pas de `pyproject.toml` : la version vit ici.

## [Non publié]

## [0.11.0] - 2026-10-06

### Ajouté

- [7.B2] Premier temps de la mesure (`downbeat_offset`) : parmi les 4
  décalages de temps, celui qui aligne les changements d'activité des tracks
  sur les débuts de mesure, plus le clap sur 2 et 4.
- [7.B2] Structure déduite de l'activité des tracks (`detect_sections`,
  `label_sections`) sur une grille de 4 mesures, labels intro / main / peak /
  breakdown / outro.
- [7.B2] Réutilisation de slot pour les sections au contenu proche ;
  `DigitaktBank.sections` et `chain` (ordre de jeu), table « Structure » dans
  la note Obsidian.
- [7.C] Le front affiche la structure de la bank sous l'onde et la chaîne des
  slots ; le curseur de pas suit le passage en cours d'un slot réutilisé.

### Modifié

- [7.B2] Impact FX sur le retour du kick au lieu du saut de RMS du sidecar ;
  `method` passe à `stem_band_fold_v2`.

### Supprimé

- [7.B2] `plan_sections` (segmentation librosa du sidecar) dans
  `analyzer/digitakt.py`.

## [0.10.0] - 2026-10-06

### Ajouté

- [7.C] Zoom à la molette dans le lecteur (bande des sections synchronisée sur
  la fenêtre visible, bouton « Ajuster »).
- [7.C] Bouton « Régénérer la bank » quand une bank existe déjà.

## [0.9.0] - 2026-10-06

### Ajouté

- [7.C] Lecteur : clic sur la forme d'onde = position de lecture (les sections
  passent dans une bande cliquable sous l'onde).
- [7.C] Boucle par glisser sur la forme d'onde, calée sur un nombre entier de
  mesures, redimensionnable, ÷2 / ×2, raccourcis `L` et `Échap`.
- [7.B] `DigitaktBank.bar_times_s` (grille de mesures recalée sur le kick) et
  `bar_times` dans le détail de track de l'API (repli sidecar).

### Modifié

- [7.C] Le curseur de pas de la grille suit la grille de mesures réelle au lieu
  d'un tempo constant (plus de dérive).

## [0.8.0] - 2026-10-06

### Ajouté

- [7.C] API locale `scripts/api.py` (FastAPI, 127.0.0.1) : liste et détail des
  tracks, audio avec Range, lecture et génération des banks Digitakt.
- [7.C] Front POC `web/` (Svelte 5 + Vite + wavesurfer.js) : library filtrable,
  lecteur avec sections cliquables, vue bank 16 tracks x 128 pas avec curseur
  synchronisé à la lecture, tracks mutées grisées, partition de mutes cliquable.
- Tests `tests/test_api.py` (library factice).
- Dépendances `fastapi`, `uvicorn`, `httpx` dans `requirements.txt`.

### Corrigé

- [7.B] Partition de mutes : les phrases repartent à chaque début de section ;
  avant, une phrase pouvait chevaucher deux patterns et afficher le kick muté
  alors qu'il jouait.

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
