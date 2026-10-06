# scripts/ — alimentation, analyse et préparation de set

Cinq outils :

- **`grab.py`** : télécharge la meilleure source audio (YT/SC/Bandcamp)
- **`analyze.py`** : analyse audiophile (Phase 1+2+6A+6C+6D : qualité +
  structure + bandes fréquence + rythmique enrichie + signature de groove)
- **`setbuilder.py`** : préparation de set (Phase 4 : doublons,
  compatibilité harmonique Camelot, génération de playlist, inférence
  des champs vides, lookup MusicBrainz, voisinage et clustering par groove)
- **`groove.py`** : Phase 6.D, extrait un groove jouable (`.mid` + pattern
  TidalCycles) depuis le stem drums Demucs
- **`visualize.py`** : Phase 5, génère une PNG signature par track
  (waveform + mel-spectrogram + structure + cues overlay + tonal profile)
- **`stems.py`** : Phase 6.B, sépare en 4 stems via Demucs
  (drums/bass/other/vocals) pour sampling TidalCycles
- **`samples.py`** : catalogue de banques de samples wav (Maschine, Battery,
  Blastwave...) : dédoublonnage par contenu audio + copie sélective

Format library.md : **table markdown unique** (migration de 2026-05-31).
Voir `../SPEC.md` (source of truth) pour l'état détaillé.

---

# samples.py — catalogue de banques de samples

Scanne des dossiers de samples wav/aiff, dédoublonne **sur le PCM décodé**
(Maschine et Maschine 2 livrent les mêmes sons avec des en-têtes différents,
un hash de fichier ne les voit pas) et écrit un catalogue CSV. On copie
ensuite ce qu'on veut garder, par filtre ou par marquage.

```bash
S=/Volumes/tanathos/Samples
# l'ordre fixe la priorité : en cas de doublon, l'exemplaire du 1er dossier gagne
python samples.py scan "$S/Maschine 2 Library" "$S/Maschine Library" \
    "$S/Battery 3 Library" "$S/Blastwave FX - Haunted FX Sound Effects Library"
# -> library/samples/catalog.csv (+ catalog.duplicates.csv pour l'audit)

# Copie par filtres (globs insensibles à la casse), toujours tester en --dry-run
python samples.py copy --dest ~/Samples/keep --category 'drums/kick' --dry-run
python samples.py copy --dest ~/Samples/keep --source 'maschine 2' --name '*909*'
python samples.py copy --dest ~/Samples/keep --category 'one shots/*' --max-duration 2

# Copie par marquage : mettre x (ou 1/oui) dans la colonne keep du CSV
python samples.py copy --dest ~/Samples/keep --marked
```

Destination : `<dest>/<source>/<arborescence d'origine sans le préfixe Samples>`. La copie est rejouable
(les fichiers déjà présents à la même taille sont sautés). Les banques
Kontakt `.nkx` protégées ne sont pas couvertes.

---

# grab.py — alimentation de la library

Télécharge un morceau depuis **YouTube / SoundCloud / Bandcamp** en
choisissant automatiquement la **meilleure qualité disponible**, sans
recompression. FLAC est réservé aux sources lossless ; un Opus 160 reste
en `.opus`, un AAC 160 en `.m4a`, un MP3 en `.mp3`. La library est un
fichier unique `library/library.md` avec une section par morceau.

## Prérequis système

- `yt-dlp` et `ffmpeg` dans le `PATH` (Homebrew sur macOS)
- Python 3.10+

## Installation

Depuis ce dossier (`music/scripts/`) :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> librosa pèse ~200 Mo. Si tu veux alléger, lance avec `--no-analyze` et
> renseigne `--bpm` / `--key` à la main.

## Usage

```bash
source .venv/bin/activate

# Par URL (un ou plusieurs)
python grab.py "https://perctrax.bandcamp.com/track/90s-hammer-original-mix"
python grab.py URL1 URL2 URL3

# Playlist / album / track Spotify : developpe en N requetes 'artiste titre'
# (Spotify n'autorise pas le DL audio ; chaque titre est cherche sur YT/SC)
python grab.py "https://open.spotify.com/playlist/69CWyZkHWDzKXc8u6f1POR"

# Backfill : remplit buy_url pour les entrees existantes de library.md
python grab.py --refresh-buy-urls

# Par requete texte libre — le moteur cherche sur YT + SC et compare
python grab.py "RVDE 90s Hammer Original Mix"
python grab.py "90s Hammer (Original Mix) de l'album 90s Hammer (TPTX003) par RVDE"

# Liste multi-lignes (une query par ligne, label/annee final retire automatiquement)
python grab.py "Noisia - The Hole Pt. 1 [VISION]
Ivy Lab x Two Fingers - Orange [2020]
Two Fingers - 296 Rhythm [NOMARK]"

# Voir le candidat retenu sans telecharger
python grab.py --dry-run "RVDE 90s Hammer"

# Ecraser un fichier deja present (pour upgrader la qualite)
python grab.py --replace URL

# Hint BPM librosa pour tribe / acid core (defaut 140)
python grab.py --start-bpm 180 URL

# Override BPM / key / genre
python grab.py --no-analyze --bpm 175 --key "A minor" --genre "hardtek, tribe" URL

# Ranger dans un sous-dossier de style explicite
python grab.py --folder swing "Glenn Miller In the Mood"

# Authentifier yt-dlp avec les cookies du navigateur (playlists privees,
# videos en 403, formats Premium type AAC 256k)
python grab.py --cookies-from-browser chrome URL
```

## Choix de la source

Pour une requête texte libre, le moteur :

1. Nettoie la requête (drop "de l'album X", déplace "par X" en tête)
2. Cherche sur YouTube + SoundCloud (top 3 par défaut, `--search-n N`)
3. Sonde le meilleur format audio de chaque candidat
4. Score qualité = **bitrate × multiplicateur perceptuel** (Opus ×1.6, Vorbis
   ×1.3, AAC ×1.2, MP3 ×1.0, lossless = score absolu)
5. Score match = fraction des tokens de la query trouvés dans `title + artist + uploader` du candidat ; match <50% pénalise ×10
6. Score final = `qualité × match`. Sélectionne le max et affiche le tableau

Bandcamp n'est **pas** dans la recherche libre (son stream public plafonne à MP3
128 kbps, perdu d'avance). Reste accessible en mode URL.

## Stockage

- `library/audio/<style>/<artist>_-_<title>.<ext>` — audio sans recompression,
  rangé par style : `--folder` si fourni, sinon premier genre connu (slugifié),
  sinon racine de `library/audio/` (comportement historique)
  - `.flac` pour sources lossless (FLAC/ALAC/WAV → recodé en FLAC)
  - `.opus`, `.m4a`, `.mp3`, `.ogg` pour le reste, codec natif préservé
- `library/library.md` — catalogue unique, une section par morceau ; le champ
  `file` porte le chemin relatif complet (`[[audio/swing/....opus]]`)
- Un morceau déjà présent (racine ou sous-dossier) est détecté récursivement
  et n'est pas re-téléchargé sans `--replace`

## Tags audio

Écrits dans le conteneur natif via mutagen :
- FLAC / Opus / OGG → Vorbis comments (`TITLE`, `ARTIST`, `BPM`, `KEY`, ...)
- M4A → atoms iTunes (`\xa9nam`, `\xa9ART`, `tmpo`, `initialkey` freeform)
- MP3 → ID3v2 via EasyID3 (`title`, `artist`, `bpm`, `initialkey` → TKEY)

Lisibles par Rekordbox, Mixxx, Serato.

## Library — édition manuelle

Le fichier `library/library.md` contient un bloc par morceau :

```markdown
## RVDE — 90s Hammer (Original Mix)

- **artist**: RVDE
- **title**: 90s Hammer (Original Mix)
- **bpm**: 175
- **key**: A minor
- **genre**: Techno
- **quality**: mp4a.40.2 160kbps
- **file**: [[audio/rvde_-_90s_hammer_original_mix.m4a]]
- **energy**: high              ← edite-les a la main
- **mood**: dark, peak time     ← preserves lors des re-runs
- **tags**: tribe, kick puissant
- **notes**: bon en sortie d'intro, attention break vers 3:20
```

Les champs **`energy`, `mood`, `tags`, `notes`** sont préservés lors des
ré-exécutions du script. Tout autre champ est régénéré.

## Idempotence

- Si un fichier audio avec le slug existe déjà (toute extension), pas de
  re-download. Utiliser `--replace` pour forcer (utile pour upgrader la
  qualité quand on découvre une meilleure source).
- L'entrée dans `library.md` est mise à jour (préserve les champs
  manuels) ; l'ordre dans le fichier est alphabétique par artist + title.

## Détection du lien d'achat (`buy_url`)

À chaque téléchargement, le pipeline cherche un lien d'achat dans cet ordre :

1. **URL source** : si elle est sur un site marchand (`bandcamp.com`,
   `beatport.com`, etc.), on la garde directement.
2. **Description du upload YT/SC** : on extrait les URL et on garde la
   première qui pointe vers un domaine marchand direct.
3. **Recherche Bandcamp** via leur API publique `bcsearch_public_api` :
   retourne le track le mieux matché (au moins 50% des tokens de
   `artist + title` en commun).
4. **Smart link** dans la description (`fanlink.to`, `linktr.ee`,
   `ffm.to`, `ditto.fm`, etc.) en dernier recours.

Le résultat est écrit dans le champ `buy_url` de library.md. Si rien
n'est trouvé, le champ reste vide (à éditer manuellement).

## Heuristique BPM

librosa détecte souvent en half-time sur le tribe rapide (180 BPM → 90).
Le script double automatiquement si <90 BPM. Pour les BPM intermédiaires
(ex. 175 détecté comme 136), pas de magie : vérifier à l'oreille et
corriger avec `--bpm`, ou éditer le frontmatter de la section. Utiliser
`--start-bpm 180` comme hint à librosa peut aider sur du tribe.

---

# analyze.py — analyse audiophile (Phase 1)

Mesure la qualité technique et perceptuelle d'un fichier audio, produit
un score 0-100 et écrit le résultat dans `library.md` + un sidecar JSON
dans `library/quality/<slug>.json`.

## Pipeline

1. **Metadata** (ffprobe) : codec, bitrate, sample rate, bit depth
2. **Signal** : sample peak, true peak (oversampling 4×), RMS, clipping
3. **Loudness** : LUFS intégré + LRA (pyloudnorm, BS.1770)
4. **Dynamique** : crest factor + catégorisation (very_dynamic / good /
   modern / compressed / overcompressed)
5. **Spectral** : bandwidth via Welch PSD, ratio HF >16 kHz, probabilité
   fake-lossless (cutoff suspect dans un conteneur lossless)
6. **Score audiophile** pondéré (dynamique 25 / spectral 25 / clipping 20
   / codec 15) → rating reference / excellent / good / average / poor /
   severely_degraded + flags (clipping_detected, crushed_master,
   fake_lossless_suspected, low_bitrate, etc.)

## Usage

```bash
source .venv/bin/activate

# Un fichier (chemin absolu, relatif, ou nom dans library/audio/)
python analyze.py rvde_-_90s_hammer_original_mix.m4a

# Toute la library
python analyze.py --all

# JSON sur stdout (pour piper vers jq, etc.)
python analyze.py --json track.opus

# Ne pas mettre à jour library.md
python analyze.py --no-update-library track.opus
```

## Intégration avec grab.py

```bash
# Télécharger + analyser en une commande
python grab.py --analyze-quality "RVDE 90s Hammer Original Mix"
```

Le `quality_score` apparaît directement dans la section library.md du
morceau, et un sidecar JSON détaillé est créé.

## Interprétation des flags

| Flag | Signification |
|---|---|
| `overcompressed` | crest factor < 6 dB, brickwall master |
| `clipping_detected` | >0.1% des samples dépassent -0.026 dBFS |
| `intersample_clipping_risk` | true peak >-0.1 dBFS (clipping post-DAC) |
| `crushed_master` | LUFS intégré >-7 (loudness war) |
| `fake_lossless_suspected` | FLAC/ALAC avec spectre tronqué (transcodé) |
| `low_bitrate` | <128 kbps en lossy |
| `low_sample_rate` | <44.1 kHz |

## Phase 2 — beats / structure / cue points / signature de groove

Activée par défaut. Ajoute quatre sections au rapport :

- **Beats** : tempo + confiance + candidats alternatifs (voir détail
  ci-dessous) + positions des beats
- **Structure** : segmentation en 4-15 segments contigus via clustering
  agglomératif sur features MFCC + chroma beat-synchrones, labellisés
  `intro` / `build` / `peak` / `main` / `breakdown` / `outro` par
  énergie relative + position. Les segments adjacents de même label
  sont fusionnés.
- **Cues** : extraction depuis la structure (`intro_start`,
  `beat_entry`, `drop`, `breakdown`, `outro`) alignés sur le beat le
  plus proche (±0.5 s). Triés par temps.
- **Rhythm signature** (Phase 6.D) : empreinte de groove tempo-invariante
  (patterns 16 pas par bande + syncope/pulse/swing). Détail dans la
  section dédiée plus bas.

Skip Phase 2 avec `--quick` (Phase 1 seule, ~3× plus rapide sur les
tracks longs).

### Détection BPM blindée (3 algos + consensus)

Pour blinder le tempo (librosa peut se tromper d'un facteur 2 sur le
tribe/breakbeat), l'analyzer lance **trois détecteurs structurellement
indépendants** :

1. **`librosa.beat.beat_track`** : dynamic programming sur l'onset
   envelope
2. **`librosa.feature.tempo`** : autocorrelation du tempogramme
3. **IOI comb-filter** (custom) : détection d'onsets en pics discrets +
   scoring d'un comb-filter sur la distribution des intervalles
   inter-onsets (harmoniques k=1..4). Algo *radicalement* différent des
   deux librosa (regarde les pics, pas l'envelope continu).

**Consensus** : clustering ±5% des candidats avec équivalence harmonique
(x2 et /2 sont considérés équivalents pour le cluster). Vote majoritaire.
Confidence = `votes_du_cluster / nb_detecteurs_valides`.

**Override library.md** : si tu corriges un `bpm` à la main dans
library.md, l'analyzer utilise cette valeur comme tempo primaire MAIS
relance les 3 détecteurs auto et les liste comme candidats. Conf=1.00 si
ton override matche un cluster auto, conf=0.70 sinon (signal d'alerte
"vérifie à l'oreille").

Affichage terminal :
```
[Beats] tempo 175.0 BPM — 995 beats  (manual override; conf=0.70, candidates=[132.5, 137.0])
```

Lecture : tu as forcé 175, mais les 3 algos auto donnent 132-137. Soit
ton oreille a raison (tribe rapide piège librosa), soit l'edit manuel
est faux. À vérifier.

## Limites connues

- **Opus en float dépasse ±1.0** : le `sample_peak_dbfs` peut afficher
  +2 dBFS après décodage. C'est attendu (Opus n'est pas normalisé en
  amplitude), c'est un indicateur de master très chaud.
- **m4a/opus passent par audioread** (libsndfile ne les lit pas
  nativement) : warning supprimé mais chargement plus lent.
- **Calibration des seuils** : volontairement permissive pour la musique
  électronique moderne (mastering club 8-10 dB crest = "good"). Ajustable
  dans `analyzer/scoring.py`.
- **Détection BPM librosa** : imparfaite sur tribe/acid core, le tempo
  affiché dans `[Beats]` peut différer du `bpm` de `library.md` (qui peut
  avoir été corrigé à la main).
- **Détection structure** : fonctionne bien sur DnB / techno bien
  structurés, plus bruité sur tribe / ambient / live coding peu cadré.
  Les segments restent une heuristique : à confronter à l'écoute.
- **Pas encore implémenté** : export DJ (Rekordbox/Traktor XML) et plots
  matplotlib (Phase 3 skipée), ML perceptual quality / similarité
  structurelle (Phase 4 partielle) — voir `quality-analyzer.md`.

---

# setbuilder.py — préparation de set (Phase 4)

Exploite `library.md` et les sidecars JSON pour préparer un set :
détecter les doublons, trouver les tracks compatibles harmoniquement,
générer une playlist greedy avec progression d'énergie, et
auto-remplir les champs vides.

## Commandes

```bash
source .venv/bin/activate

# Inventaire des keys + Camelot
python setbuilder.py keys

# Doublons (artist+title normalisés : drop "Original Mix", "feat.", labels)
python setbuilder.py duplicates

# Top N tracks compatibles avec un slug (BPM + key + energie)
python setbuilder.py compatible <slug> -n 10 \
    --energy maintain --min-score 0.4

# Génération de playlist greedy à partir d'un slug de départ
python setbuilder.py playlist --start <slug> \
    --duration 60 --energy rising --max-track 15

# Génération backward depuis un peak final (build vers le climax)
python setbuilder.py playlist --peak <slug> \
    --duration 60 --max-track 15

# Export Mixxx (M3U8 importable via File -> Import Playlist)
python setbuilder.py playlist --peak <slug> --duration 60 \
    --export-m3u8 ../sets/build-vers-x.m3u8

# Auto-fill genre / energy / mood / tags depuis les sidecars
python setbuilder.py infer [--field genre|energy|mood|tags|all] [--force]

# Lookup MusicBrainz pour remplir `about` (pays + tags genres)
python setbuilder.py describe [--force]

# Voisins par groove (signature rythmique, indépendant du BPM/key)
python setbuilder.py similar <slug> -n 8

# Familles de groove (clustering ; --write pour écrire groove_cluster)
python setbuilder.py groove-clusters --k 6 [--write]
```

`--start` et `--peak` sont mutuellement exclusifs :
- `--start` construit forward (le slug ouvre le set, progression selon `--energy`)
- `--peak` construit backward (le slug ferme le set en climax, progression rising forcée). Plancher d'énergie automatique à `peak - 2 crans` pour éviter que le greedy ne dégringole.

## Compatibilité harmonique (Camelot Wheel)

Les keys sont mappées en notation Camelot (1A..12B, A=minor / B=major).
Score de compatibilité :

| Cas | Score |
|---|---|
| Même code (8A → 8A) | 1.0 |
| Même chiffre, lettre opposée (8A → 8B, relatif maj/min) | 0.9 |
| ±1 sur la roue, même lettre (8A → 7A ou 9A, quinte/quarte) | 0.85 |
| ±2 sur la roue, même lettre (boost énergétique) | 0.55 |
| Autre | 0.0 |

## Compatibilité BPM

| Ratio B/A | Score | Type de mix |
|---|---|---|
| 0.97 - 1.03 | 1.0 | direct |
| 0.94 - 1.06 | 0.85 | tempo nudge |
| 0.5 ou 2.0 (±4%) | 0.7 | half-time / double-time |
| 0.90 - 1.10 | 0.5 | pitch shift |
| autre | 0.0 | incompatible |

## Score de transition

```
total = 0.5 × bpm_score + 0.3 × key_score + 0.2 × energy_score
```

L'energy_score dépend de `--energy` : `rising` favorise B > A,
`falling` favorise B < A, `maintain` favorise B ≈ A.

## Inférence des champs vides

`infer` lit les sidecars de `library/quality/` et remplit :

| Champ | Méthode | Marqueur |
|---|---|---|
| `genre` | BPM range + genre yt-dlp existant (downtempo / hip-hop / house / techno / dubstep / breakbeat / dnb / tribe / hardcore) | sans `?` |
| `energy` | 0.5 × BPM + 0.3 × LUFS + 0.2 × crest factor → very_low / low / medium / high / very_high | sans `?` |
| `mood` | mode (major/minor) × tempo × LUFS → dark / uplifting / driving / chill / peak time / intimate | **avec `?`** (à valider à l'oreille) |
| `tags` | bandwidth → `lo-fi`, half-time correction → `half-time-suspect` | sans `?` |

**Important** : `infer` ne touche **jamais aux champs non vides** sauf
si tu passes `--force`. Et même sous `--force`, on n'écrase jamais par
une valeur vide (tes éditions manuelles sont protégées). Pour clearer
un champ, édite `library.md` à la main.

L'inférence préfère le `bpm` de library.md (corrigible à la main) au
tempo détecté par librosa. Donc si tu corriges un BPM dans library.md
et relances `infer`, le genre/energy/mood s'actualisent en cohérence.

## Description d'artiste (`about`)

`setbuilder.py describe` interroge **MusicBrainz** (API publique, free)
pour chaque artiste unique de la library. Format de sortie : `<pays> |
<tag1>, <tag2>, <tag3>`.

- Cache local dans `library/artists/<slug>.json` pour éviter le rate
  limit (1 req/sec)
- Skip les artistes ayant déjà un `about` non vide (sauf `--force`)
- Regroupe par `primary_artist` (split sur `feat.` / `&` / `,` / ` x `)
  pour ne pas faire de requête redondante
- Filtre les tags pourris (`seen live`, `favourite`, etc.)

Exemples obtenus sur la library :
- Polar Inertia → `ambient, techno, minimal techno`
- Quantic → `downtempo, jazz, funk`
- Zero 7 → `UK | trip hop, electronic, downtempo`
- BAD BUNNY → `PR | hip hop, latin, reggaeton`

Couverture typique : 60-70% (MusicBrainz n'a pas les artistes free
party / acid core / labels indé). Édite à la main pour le reste.

---

# signature de groove + groove.py (Phase 6.D)

Décrit la **forme** du pattern rythmique, repliée sur une mesure de 16 pas,
**indépendamment du tempo**. Sert à trouver des tracks au groove proche et à
regrouper la library en familles — un axe que BPM + key + energy ne capturent
pas (un tribe roulant syncopé et un acid four-on-floor martelé peuvent partager
BPM/key/energy mais avoir un groove opposé).

## Ce qui est extrait (`RhythmSignatureReport`, sidecar)

Calculé en Phase 2 par `analyze.py` (donc `analyze.py --all` repeuple les
sidecars). Affiché dans le bloc `[Rhythm signature]` du rapport terminal :

```
[Rhythm signature] 16 pas/mesure  —  164 mesures repliees
  bar : █▃▁▃▅▅▃▄█▄▂▃▇▅▂▄
  sub : ▇▇▃▃▅▇▄▂██▄▁▆█▂▁     ← kick (20-200 Hz)
  mid : █▄▂▁▅▅▅▄█▅▄▁▇▅▆▄     ← snare/clap/corps (200-2k)
  high: ▇▁▂▆▅▃▃▆▆▁▁█▇▂▃▇     ← hats/texture (2k+)
  syncope: 0.49  |  pulse: 0.93  |  swing: 0.45
```

- patterns normalisés min-max (relief des hits) ; `syncopation` (hors-temps),
  `pulse_clarity` (régularité), `swing` (microtiming des contretemps).
- **N'encode ni BPM, ni key, ni energy** : volontairement orthogonal à la
  compatibilité Camelot (cf. SPEC 6.D et décisions arbitrées).

## Similarité et clustering (`setbuilder.py`)

```bash
# Voisins de groove (cross-corrélation invariante à la phase du downbeat)
python setbuilder.py similar <slug> -n 8

# Familles de groove (clustering agglomératif, métrique = rhythm_distance)
python setbuilder.py groove-clusters --k 6          # dry-run
python setbuilder.py groove-clusters --k 6 --write  # écrit groove_cluster
```

Le clustering est **indicatif** : sur une petite library, viser ~5-8 familles.

## Export groove jouable (`groove.py`)

Transcrit le pattern en hits discrets kick/snare/hat et l'exporte en `.mid`
**et** `.tidal`. Source préférée : le **stem drums Demucs** (lance `stems.py`
avant pour un rendu propre ; fallback sur le mix avec warning).

```bash
# Exporte library/grooves/<slug>.{mid,tidal}
python groove.py <slug>

# Réglages : finesse de grille, longueur, format, sensibilité
python groove.py <slug> --steps 32 --bars 2 --format tidal --threshold 0.5
python groove.py <slug> --no-align   # ne pas caler sur le kick le plus fort
```

Sortie `.tidal` (collable en live) :

```
-- groove extrait de 2HOT2PLAY — Keep The Balance
-- 152 BPM, 16 pas/mesure, 1 mesure(s)
-- setcps (152/60/4)
d1 $ stack [
  s "bd ~ ~ ~ bd bd ~ ~ ~ ~ ~ ~ bd ~ ~ ~",
  s "sn ~ ~ sn ~ ~ sn ~ sn ~ sn sn ~ ~ sn sn",
  s "~ ~ hh hh ~ ~ hh hh ~ ~ hh hh ~ ~ hh hh"
  ]
```

Le `.mid` (kick=36, snare=38, hat=42, canal GM batterie) s'ouvre dans Renoise
(cf. `to_xrns.py`) ou n'importe quel DAW.

## Méthode

Une mel-spectrogram → onset strength par bande → repliage sur la grille via les
`beat_times` (4/4 par défaut sauf signature impaire confiante). `groove.py`
seuille le pattern replié+étiré (robuste au jitter, là où la détection d'onsets
discrets se disperse entre pas adjacents). Modules :
`analyzer/rhythm_signature.py`, `groove.py`. Tests :
`tests/test_rhythm_signature.py` (`python -m pytest tests/`).

---

# digitakt.py — draft de bank Digitakt II (Phase 7.B)

1 morceau = 1 bank. La structure est **déduite de l'activité des tracks**
(16 sections au plus) ; chaque section est jouée par un pattern (128 pas =
8 mesures au plus), deux sections au contenu proche partageant le même slot
(ordre de jeu = chaîne, ex. `01 02 01 03`). Les patterns sont répartis sur la **grille fixe des 16
tracks** de [[../digitakt/doctrine|la doctrine]] (1 kick, 2 rumble, 3 clap,
4-6 hats/ride, 7-8 percs, 9 basse, 10 lead, 11 atmo, 12-13 Id1/Id2 laissées
vides, 14 vocal, 15 FX, 16 réserve). Prérequis : sidecar (`analyze.py`) et de
préférence les stems (`stems.py <slug> --cleanup`) ; fallback mix avec warning.

```bash
# library/digitakt/<slug>.{json,md} + library/digitakt/<slug>/pNN.mid
python digitakt.py <slug>

# Partition de mutes par phrases de 16 mesures, trigs plus sensibles, sans MIDI
python digitakt.py <slug> --phrase-bars 16 --threshold 0.4 --no-midi

# Toute la library (tracks avec sidecar)
python digitakt.py --all
```

Exemple réel (`2hot2play_-_keep_the_balance`, un pattern, 1re page, génération 7.B) :

```
01 Kick          x...x...x...x...
02 Rumble        .x...x...x...x..
05 Hat ouvert    .x...x...x...x..
09 Basse         .x...x...x...x..
```

**Méthode** :
- Beats **re-suivis sur la bande kick (30-120 Hz) du stem drums** : la grille
  du sidecar est parfois un tempo constant légèrement faux (152 BPM au lieu de
  kicks à 0,406 s soit 147,8 BPM) ; sur 128 pas la dérive rend le repliage
  illisible.
- Une STFT par stem ; chaque track lit sa bande dans son stem (kick 30-120 Hz,
  clap 300-3000 Hz, hats 3-16 kHz…), agrégée par double-croche.
- Calage de phase sur le kick (dans le temps), puis **premier temps de la
  mesure** : parmi les 4 décalages de temps, celui qui aligne le mieux les
  changements d'activité des tracks (fenêtre de 2 mesures, maxima locaux) sur
  les débuts de mesure, plus un bonus si le clap tombe sur 2 et 4.
- Activité par mesure (actif si à moins de 12 dB du max de la track).
- **Structure** : grille de 4 mesures (phase choisie là où les tracks
  basculent le plus, pour gérer une anacrouse), tracks actives à la majorité
  par bloc, blocs identiques fusionnés, bloc isolé à une track près absorbé
  (c'est un mute, pas une section), fusion des voisines les plus proches
  au-delà de 16. Labels déduits du contenu : sans kick = `breakdown` (`intro` /
  `outro` en bord), le plus de tracks = `peak`, sinon `intro` / `main` /
  `outro`. La segmentation librosa du sidecar n'est plus utilisée ici.
- **Réutilisation de slot** : une section reprend le slot d'une précédente si
  mêmes tracks actives et grilles proches (Jaccard moyen des pas ≥ 0,3 sur
  l'union des tracks ; seuil bas car les trigs détectés sont bruités).
- **Partition de mutes** par phrase (repart à chaque section).
- Par section : repliage des mesures actives modulo 1/2/4/8 mesures,
  normalisation robuste (médiane → 95e percentile), seuil → trigs. Hats
  ventilés ouvert / fermé / ride par décroissance et rapport de bandes.
  Notes basse / lead estimées par chroma.
- Track 15 : impact au pas 0 d'un drop (retour du kick après une section sans
  kick), riser figuré sur la dernière mesure d'avant. Un slot réutilisé porte
  ses FX à chaque passage, comme sur la DT.

**Sorties** : JSON `DigitaktBank` (Pydantic, consommé par le front :
`patterns`, `sections`, `chain`, `mutes`), note Obsidian (tableau des
patterns, structure et chaîne, partition de mutes, grilles `x...`),
un `.mid` par pattern avec **canal MIDI = track** (drums sur la note 60 =
pitch d'origine du sample) à enregistrer en live recording sur la DT2.

**Limites** : draft, pas transcription. Les percs et le lead sont bruités, les
hats ouverts sur-détectés quand la reverb tient. Id1 / Id2 sont à choisir à
l'oreille. Les mutes à l'intérieur d'une section diluent le repliage (trous
dans le kick).

# harmony.py — gamme et accords (Phase 7.H)

Gamme du morceau sous son nom **KB SCALE** de la DT2 (7 modes, mineurs
harmonique / mélodique, pentatoniques, blues) et accords par mesure (triades,
sus2 / sus4, dim, quinte à vide), progression par section.

```bash
# Une track (stems conseillés : stems.py <slug> --cleanup)
python harmony.py 2hot2play_-_keep_the_balance
# Toute la library (tracks avec sidecar)
python harmony.py --all
```

Exemple : `F blues (score 0.731, marge 0.264, stems)`, `DT2 : KB SCALE = BLUES,
ROOT NOTE = F`, puis la progression par section (`main  Fm - F5 - Fm`).

- **Source** : stem `other` (composante harmonique HPSS, 3 notes dominantes par
  trame) + stem `bass` (note tenue, départage la fondamentale) ; repli sur le
  mix. Grille de mesures de la bank si elle existe.
- **Marge** : écart avec la meilleure autre fondamentale. Sous 0,05 la gamme est
  marquée *incertaine* (modes relatifs, ex. F majeur / A# lydien) ; les gammes
  voisines sur la même fondamentale sont listées comme alternatives.
- **Sorties** : bloc `harmony` du sidecar (conservé quand `analyze.py` réécrit
  le sidecar), section Harmonie + `scale` dans la note de bank, front (gamme
  dans l'entête du lecteur, bande d'accords, mode KEYBOARD de la DT2).
- **Limites** : sur les musiques peu mélodiques (dubstep, tek), beaucoup de
  quintes à vide et de sus2 ; un draft à valider à l'oreille.

# kb.py — base de connaissance Digitakt II (Phase 7.D, 7.F)

Corpus : `digitakt/kb/*.md` + `digitakt/doctrine.md`, découpés en sections
(`##` / `###`). Recherche plein texte **sans index ni RAG** : le corpus est
relu à chaque requête (une note éditée dans Obsidian est vue tout de suite).
Tous les termes doivent être présents dans la section, sans tenir compte des
accents ni de la casse ; score = occurrences, ×5 dans le titre.

```bash
python kb.py search "pattern modele"
python kb.py toc                         # fiches par lot (noms tirés de _index.md)
```

**Lien avec le manuel (7.F)** : le sommaire du PDF
`refs/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf` (lu par `pypdf`, mis en
cache par version du fichier) donne la page de chaque `§x.y` ; le numéro de
page imprimé est celui du PDF. Les références du frontmatter `manuel` et
celles du texte sont résolues (bornes des plages `§12.6-12.9` comprises).
`doctrine §3`, `[[../doctrine]] §3` et, dans la doctrine, un `§3` à un seul
niveau visent la doctrine, pas le manuel. Le PDF est ignoré par git : à
déposer dans `refs/` pour activer les liens.

Dans le front : bouton **Base de connaissance** du bandeau (ou touche `/`,
`Échap` pour fermer). Le panneau s'ouvre sur le **sommaire par lot** (statut
draft visible), la recherche surligne les extraits. Une fiche affiche ses
**pages du manuel** en tête (`§11.7 amp page p56`), les `§` du texte et les
wikilinks deviennent cliquables (manuel, section de la doctrine, autre
fiche). Le manuel s'ouvre dans le panneau élargi à la bonne page
(`#page=N`, visionneuse PDF du navigateur) ou dans un nouvel onglet.

# api.py + web/ — front de la library (Phase 7.C)

POC web local : parcourir la library, écouter un morceau et naviguer dedans,
voir sa bank Digitakt comme sur la machine. Backend FastAPI (`scripts/api.py`),
front Svelte 5 + Vite + wavesurfer.js (`web/`). Le passage en app native Mac
se fera via Tauri en reprenant `web/` tel quel.

```bash
# Une fois : dépendances
pip install -r requirements.txt          # fastapi, uvicorn, httpx
cd ../web && npm install && npm run build && cd ../scripts

# Lancer : API + front buildé sur http://127.0.0.1:8765
python api.py

# Dev du front (hot reload sur http://localhost:5173, proxy /api → 8765)
python api.py &   puis   cd ../web && npm run dev
```

**Ce que fait le front** :
- **Library** : 386 tracks, filtre texte (artiste, titre, genre, key, mood),
  tri BPM / key / energy, filtres « a des stems » / « a une bank ».
- **Lecteur** : forme d'onde, **clic = position de lecture**, bande des
  sections de structure sous l'onde (mêmes couleurs que `visualize.py`, clic =
  début de section), boutons de cues. Espace = lecture / pause, flèches = ±10 s.
  **Molette = zoom** (jusqu'à 600 px/s, la bande des sections suit), geste
  horizontal du trackpad = défilement, bouton « Ajuster » pour revenir.
- **Boucle** : **glisser sur la forme d'onde** crée une boucle calée sur un
  nombre entier de mesures (grille de la bank, recalée sur le kick ; sinon
  grille du sidecar). Poignées redimensionnables (recalage à chaque fois),
  ÷2 / ×2, `L` = on/off, `Échap` = retirer.
- **Structure** : quand une bank existe, la bande sous l'onde affiche les
  sections déduites des tracks (au lieu de celles du sidecar).
- **Bank Digitakt, façade DT2** : écran à bandeau (`A01 INTRO ♩161.5`),
  **16 trig keys en 2 rangées de 8** pour la track sélectionnée (contour
  rouge = trig, intensité = vélocité, note sur les tracks 9-16, pas joué
  éclairci, clic = saut au pas), LEDs de page 2 × 4 + PAGE / FOLLOW, touches
  **TRK** (choisir la track), `[FUNC]` + TRK = **MUTE** (vert = track active
  dans la phrase en cours), **PTN** (slots de la bank, lettre A-P mémorisée
  par morceau dans le navigateur, flèches gauche / droite = bank). Patterns
  nommés A01-P16.
- **Mise en page** : en large (≥ 1150 px), DT2 et légende à gauche, figées et
  calées sur la hauteur de l'écran, lecteur + chaîne + vue d'ensemble + mutes à
  droite ; en étroit, tout est empilé et centré. Bouton **Morceaux** pour
  masquer la liste et gagner la largeur.
- **Façade complète (7.G)** : les 23 contrôles du §3.1 du manuel, placés à
  l'échelle sur le dessin de la façade, fonctions
  secondaires en orange ; **PLAY / STOP** pilotent le lecteur, **FUNC** est
  une bascule, les touches **TRIG / SRC / FLTR / AMP / FX / MOD** changent la
  page des knobs A-H (noms du §11, NOTE / VEL du pas courant). Clic = légende épinglée
  (fonction, CC / NRPN, fiche, § du manuel), survol = simple aperçu ; **AIDE ?** = un clic ouvre la
  fiche. Données dans `web/src/lib/dt2.ts`. Dessous : **chaîne** (ordre de jeu,
  clic = saut à la section, double-clic = boucle sur la section), **vue d'ensemble** (onglet, avec mesures et répétitions du pattern) 16 tracks × tous les pas
  (curseur synchronisé, tracks mutées grisées `M`), partition de mutes
  cliquable (second onglet).
- **Harmonie (7.H)**, si `harmony.py` a tourné : gamme dans l'entête du
  lecteur (soulignée en pointillé si *incertaine* ; survol = notes, marge,
  réglage DT2, alternatives) suivie de l'accord en cours ; **bande d'accords**
  par mesure sous les sections (opacité = confiance, hachures = « N », clic =
  début de mesure, suit le zoom). Sur la façade, **[KEYBOARD]** (ou `[FUNC]` +
  KEYBOARD) passe l'écran en **KB SETUP** (SCALE / ROOT à reporter sur la
  machine, accord en cours, progression de la section) et les trig keys en
  clavier chromatique (rangée basse = blanches, haute = noires) : notes de la
  gamme éclairées, fondamentale en rouge, notes de l'accord en vert.
- **Générer / Régénérer la bank** depuis le front (appelle `digitakt.py` puis
  `harmony.py` sur la nouvelle grille, une vingtaine de secondes) : utile après
  `stems.py` ou une mise à jour de l'analyzer. Un échec de l'harmonie n'empêche
  pas la bank (l'ancien bloc `harmony` reste en place).

**API** (127.0.0.1 uniquement ; un fichier n'est servi que pour un slug présent
dans library.md) :

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/api/tracks` | liste (`TrackSummary`) |
| GET | `/api/tracks/{slug}` | détail + segments + cues + `harmony` / `keyboard_setup` (7.H) |
| GET | `/api/tracks/{slug}/audio` | fichier audio (requêtes Range pour le seek) |
| GET | `/api/tracks/{slug}/bank` | `DigitaktBank` (404 si absente) |
| POST | `/api/tracks/{slug}/bank` | génère la bank |
| GET | `/api/kb/search?q=` | recherche plein texte KB + doctrine (`KbHit`) |
| GET | `/api/kb/note?path=` | note du corpus KB (404 hors corpus) + références au manuel |
| GET | `/api/kb/toc` | fiches par lot (`KbLot`) |
| GET | `/api/manual/outline` | sommaire du manuel, § → page (`ManualRef`) ; `{}` sans PDF |
| GET | `/api/manual` | manuel PDF (chemin fixe, 404 s'il manque) |

**Limites** : la forme d'onde est décodée dans le navigateur (quelques secondes
sur un morceau long). Le rebouclage se fait sur l'événement `timeupdate` du
navigateur : quelques millisecondes de flottement possibles au saut, suffisant
pour écouter, pas pour un enregistrement. Sans bank, la boucle se cale sur la
grille du sidecar, qui peut dériver (cf. SPEC Phase 7).

# stems.py — séparation Demucs (Phase 6.B)

Sépare chaque track en 4 stems via Demucs (Meta, modèle htdemucs) :
- `drums.wav` (kicks, snares, hats)
- `bass.wav` (basses sub + bass synth)
- `other.wav` (mélodies, harmonies, FX)
- `vocals.wav` (voix si présentes)

Stockés dans `library/stems/<slug>/`. Champ `has_stems: yes` dans
library.md. **Apple Silicon GPU (MPS) détecté en auto** → ~15-25s/track
(contre ~30-60s en CPU). 1er run = +250 Mo de modèle à télécharger.

## Usage

```bash
source .venv/bin/activate

# Track spécifique
python stems.py kodaman_-_beton

# Toute la library (long : ~60min pour 60 tracks)
python stems.py --all

# Forcer re-génération
python stems.py --force <slug>

# Autre modèle
python stems.py --model htdemucs_ft <slug>     # fine-tuned, plus précis
python stems.py --model mdx_extra <slug>        # alternative

# Forcer un device particulier
python stems.py --device cpu <slug>     # force CPU
python stems.py --device mps <slug>     # force Apple Silicon GPU

# Post-processing techno (cleanup des fuites Demucs)
python stems.py --cleanup <slug>        # cleanup seul (stems déjà existants)
python stems.py --cleanup --all         # applique le cleanup à toute la library
```

## Cleanup techno-aware (`--cleanup`)

Demucs `htdemucs` est entraîné majoritairement sur pop/rock (MUSDB18).
Sur tribe/techno/hardtek il a 3 fuites typiques qu'on peut corriger
avec des règles domain :

1. **Sub-kick → drums** : highpass `bass.wav` à 60 Hz (le sub 20-60 Hz
   appartient au kick territory, pas à la bassline)
2. **Pas de mélodie aigüe dans bass** : lowpass `bass.wav` à 500 Hz
   (au-dessus = fuite de lead/synth)
3. **Vocals quasi-silencieux** : si RMS < -40 dBFS, on merge dans
   `other.wav` (track instrumental, le contenu de `vocals.wav` est du
   leak)

Quand le cleanup est appliqué, `has_stems: cleaned` (au lieu de `yes`)
dans library.md. Les stems sont **overwrités** (pas de version raw
préservée). Si tu veux revenir au brut, relance `stems.py --force <slug>`
sans `--cleanup`.

**Caveat** : ces règles sont techno-aware. Sur de la pop/rock (bass
guitar qui monte à 1 kHz, voix réelle dans vocals), elles empirent le
résultat. À activer track par track ou batch si toute la library est
électronique.

Théorie audio détaillée derrière ces règles (filtres Butterworth, RMS
vs peak, où vit une bassline techno) : voir
`../technique/cleanup-stems-techno.md`.

## Cas d'usage TidalCycles

```haskell
-- Charger les stems d'un track dans SuperDirt
-- (à mettre dans ~/.config/SuperCollider/startup.scd ou en run-time)
~dirt.loadSoundFiles("/Users/tom/.../library/stems/kodaman_-_beton/*.wav");

-- Puis dans Tidal :
d1 $ s "drums:0"     -- drums du Kodaman
d2 $ s "bass:0" # gain 1.2
```

## Limites

- **Modèle bias** : Demucs est entraîné majoritairement sur pop/rock.
  Sur tribe/acid core très dense, "other" et "drums" peuvent fuiter
  l'un dans l'autre. Vérifier à l'oreille avant de sampler.
- **Vocals vide** = OK : si pas de voix dans le track, `vocals.wav`
  contient juste du quasi-silence.

---

# visualize.py — PNG signatures (Phase 5)

Une PNG par track dans `library/visuals/<slug>.png` au format **1200×320 px**.
Permet de **browser visuellement la library** : tu reconnais une signature
spectrale en moins d'1 seconde, plus rapide qu'écouter.

## Layout d'une PNG

```
┌─────────────────────────────────────────────────────────────┐
│ Artist — Title | BPM | key (Camelot) | energy | LUFS | dur  │  header
├─────────────────────────────────────────────────────────────┤
│ ▁▄▆█▆▄▂▄▆█▆▄▂▁▂▄▆█▆▄▂                            waveform  │  RMS
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  mel-spectrogram (palette magma, log frequency)             │  spectro
│  cue points : lignes blanches verticales avec labels         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ intro │ build │ peak │ break │ main │ outro                 │  structure
└─────────────────────────────────────────────────────────────┘
```

## Usage

```bash
source .venv/bin/activate

# Toute la library + génère library/visuals/_index.md
python visualize.py

# Tracks spécifiques par slug
python visualize.py rvde_-_90s_hammer_original_mix noisia_-_the_hole_pt_1

# Force la régénération (sinon skip si PNG existe)
python visualize.py --force
```

## Couleurs des segments de structure

| Label | Couleur |
|---|---|
| intro | gris clair |
| build | orange |
| peak | rouge |
| main | bleu |
| breakdown | violet |
| outro | gris foncé |

## Browse dans Obsidian

`library/visuals/_index.md` est auto-généré et embarque toutes les PNG via
wikilinks. Ouvre-le dans Obsidian et scroll pour scanner toute ta library
en mode visuel.

## Cas d'usage typiques

- **Comparer deux tracks pour valider une transition** : ouvre les 2 PNG
  côte à côte, regarde si les structures s'enchaînent
- **Trouver tous les tracks avec un gros breakdown** : scan visuel, repère
  les bandes violettes longues
- **Identifier les tracks lo-fi** (bandwidth coupée) : le mel-spectrogram
  est noir au-dessus d'une certaine fréquence
- **Repérer les masters compressés** : la waveform RMS est saturée
  uniformément (pas de creux)

---

# Import dans Mixxx

`--export-m3u8 <chemin>` génère un fichier M3U8 standard avec :
- `#EXTINF:durée,Artist - Title` par track
- Chemin absolu vers le fichier audio

Dans Mixxx : **File → Import Playlist** ou drag-and-drop. Les tags
audio (BPM, KEY, Comment) écrits par `grab.py` sont lus
automatiquement par Mixxx — pas besoin d'une autre étape.

Pour des exports plus riches (cue points, beat grids dans XML
Rekordbox lisible par Mixxx), voir Phase 3 dans `quality-analyzer.md`
(non implémentée à date).

## Limites

- **`mood` et `tags` suggérés peuvent être faux** si la détection
  librosa s'est trompée sur le BPM ou le mode (major/minor). Le suffixe
  `?` sur `mood` te rappelle que c'est à valider.
- **Pas d'optimisation globale de playlist** : algorithme greedy, prend
  le meilleur voisin à chaque étape. Pour une optimisation globale (TSP)
  il faudrait un algo plus coûteux ; pas justifié sous 2h de set.
- **`duplicates` ne fait pas de fuzzy match d'audio** : juste sur le
  texte normalisé. Deux mêmes morceaux nommés différemment ne seront
  pas détectés.
