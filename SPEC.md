---
tags: [spec, projet, library, dj, mir]
updated: 2026-05-31
status: living document
---

# SPEC — Music library & analyzer

Source of truth du projet : ce que la stack fait aujourd'hui, ce qu'on
va faire maintenant, ce qu'on a décidé de ne pas faire, et les pistes
futures cataloguées.

## Vision

Outils Python pour construire et préparer la **library musicale** qui
alimente deux usages :

1. **Sets free party** sur sound system — tribe / acid core 180-200 BPM,
   ouvertures DnB / dubstep / break / ralentis
2. **Patches TidalCycles** en live coding — stems et samples extraits
   des tracks

Tout est en `music/library/` (vault Obsidian). Voir [[README]] pour les
détails opérationnels et [[etude-cas-build-vers-moliy|étude de cas]]
pour un exemple pédagogique de set.

---

## État implémenté (mai 2026)

### Architecture des scripts

```
music/scripts/
├── grab.py                       # acquisition multi-plateforme
├── analyze.py                    # analyse qualité + structure
├── setbuilder.py                 # préparation de set
├── visualize.py                  # rendu PNG signatures
├── library_md.py                 # parse / write library.md
└── analyzer/
    ├── audio_loader.py           # soundfile + fallback librosa
    ├── metadata.py               # ffprobe
    ├── signal.py                 # peak / true peak / clipping / RMS
    ├── loudness.py               # pyloudnorm LUFS + LRA
    ├── dynamic.py                # crest factor
    ├── spectral.py               # bandwidth + fake-lossless
    ├── scoring.py                # score audiophile pondéré
    ├── report.py                 # rendu terminal + sidecar JSON
    ├── beat_tracking.py          # 3 détecteurs + consensus + override
    ├── structure.py              # segmentation beat-sync
    ├── cue_detection.py          # cues depuis structure
    ├── pipeline.py               # analyze_file unifié
    ├── types.py                  # Pydantic models
    ├── keys.py                   # Camelot Wheel
    ├── compatibility.py          # score BPM + key + énergie
    ├── duplicates.py             # détection fuzzy
    ├── playlist.py               # builder greedy forward + backward
    ├── infer.py                  # auto-fill champs sémantiques
    ├── describe.py               # MusicBrainz lookup
    └── visualize.py              # render_track + write_index_md
```

### Schéma de la library

```
music/library/
├── library.md                    # source de vérité : table markdown unique
├── library.md.backup-*           # backups pre-migration
├── audio/<slug>.{opus,m4a,mp3,flac}
├── quality/<slug>.json           # sidecars Phase 1+2+6A+6C (Pydantic)
├── visuals/<slug>.png            # PNG signatures Phase 5
├── visuals/_index.md             # index Obsidian auto-généré
├── stems/<slug>/{drums,bass,other,vocals}.wav  # Phase 6.B Demucs
└── artists/<slug>.json           # cache MusicBrainz
```

#### Format de library.md (depuis 2026-05-31)

**Table markdown unique** — une ligne par morceau, une colonne par champ.
Échappement : `|` → `\|`, `\n` → `<br>` (rendu Obsidian propre).

Colonnes dans l'ordre canonique (`FIELD_ORDER`) :

| Champ | Source | Régénéré ? |
|---|---|---|
| `artist` | grab.py | oui |
| `title` | grab.py | oui |
| `bpm` | librosa initial, **édition manuelle prioritaire** | non si édité |
| `key` | librosa | non si édité |
| `duration` | grab.py | oui |
| `year` | yt-dlp metadata | oui |
| `genre` | infer (BPM-derived) + yt-dlp | oui |
| `about` | MusicBrainz API | oui si vide |
| `quality` | grab.py (codec + bitrate) | oui |
| `quality_score` | analyzer Phase 1 (0-100) | oui |
| `band_profile` | **Phase 6.A** : `sub:N bass:N lowmid:N mid:N pres:N high:N air:N \| tonal-profile` | oui |
| `groove_cluster` | **Phase 6.D** : index de famille de groove (`setbuilder groove-clusters --write`) | oui |
| `source` | grab.py | oui |
| `url` | grab.py | oui |
| `buy_url` | description scan + Bandcamp search API | oui si vide |
| `file` | grab.py | oui |
| `has_stems` | **Phase 6.B** stems.py (`yes` quand stems générés) | oui |
| `added` | grab.py (1re fois) | non |
| `energy` | infer (LUFS+BPM+crest) | **PRESERVED** |
| `mood` | infer (mode+tempo+LUFS, suffixe `?`) | **PRESERVED** |
| `tags` | infer (lo-fi, half-time-suspect) | **PRESERVED** |
| `notes` | manuel | **PRESERVED** |

**Convention `?` final** : suffixe ajouté aux champs auto-inférés
incertains (mood, parfois tags). Sans `?` = mesurable ou édité humain.

**PRESERVED_FIELDS** : `energy`, `mood`, `tags`, `notes` ne sont jamais
écrasés par les outils (même sous `--force`). Les autres champs sont
régénérables.

---

### Phase 1 — Analyse qualité audio

Pipeline `metadata → signal → loudness → dynamic → spectral → scoring`.

**Métriques** :
- Metadata via ffprobe : codec, bitrate, sample rate, bit depth, container
- Signal : sample peak, true peak (oversampling 4× via scipy resample_poly), RMS, clipping ratio
- Loudness : LUFS intégré + LRA (pyloudnorm, ITU-R BS.1770-4)
- Dynamic : crest factor + catégorisation (very_dynamic/good/modern/compressed/overcompressed)
- Spectral : bandwidth cutoff (Welch PSD), high-freq energy ratio, fake-lossless probability (uniquement si conteneur lossless)

**Score audiophile** (0-100) pondéré :
- Dynamic 25 / Spectral 25 / Clipping 20 / Codec 15

**Flags émis** : `overcompressed`, `clipping_detected`,
`intersample_clipping_risk`, `crushed_master`, `fake_lossless_suspected`,
`low_bitrate`, `low_sample_rate`.

### Phase 2 — Structure et cue points

**Beat tracking** : 3 détecteurs structurellement indépendants
1. `librosa.beat.beat_track` (dynamic programming)
2. `librosa.feature.tempo` (autocorrelation tempogramme)
3. IOI comb-filter custom (scoring harmonique k=1..4 sur intervalles
   inter-onsets)

Consensus par clustering ±5% + équivalence harmonique (×2/0.5×). Expose
`tempo_bpm`, `confidence`, `candidates_bpm`, `manual_override`. Si
library.md a un `bpm` édité, prime ; les 3 algos sont quand même lancés
et listés comme candidats (conf=0.70 si désaccord = drapeau d'alerte).

**Structure** : segmentation 4-15 segments via clustering agglomératif
sur features MFCC + chroma beat-synchrones. Labels par énergie relative
+ position : `intro`/`build`/`peak`/`main`/`breakdown`/`outro`. Fusion
des adjacents de même label.

**Cues** : extraction depuis structure (`intro_start`, `beat_entry`,
`drop`, `breakdown`, `outro`) alignés sur le beat le plus proche
(±0.5s).

### Phase 4 — Préparation de set (`setbuilder.py`)

**Commandes** :
- `keys` : inventaire Camelot de la library
- `duplicates` : groupes fuzzy (titres normalisés, drop "Original Mix" / "feat." / labels)
- `compatible <slug> -n N` : top N tracks mixables (BPM + key + énergie)
- `playlist --start <slug>` : build forward depuis le slug
- `playlist --peak <slug>` : build backward vers le slug (climax final)
- `infer [--field X] [--force]` : auto-fill genre/energy/mood/tags depuis sidecars
- `describe [--force]` : lookup MusicBrainz pour remplir `about`

**Compatibilité harmonique** : Camelot Wheel 24 codes (1A..12B). Score :
même code 1.0 / même chiffre lettre opposée 0.9 / ±1 même lettre 0.85 /
±2 même lettre 0.55.

**Compatibilité BPM** : ratio 0.97-1.03 = direct 1.0 / 0.94-1.06 = nudge
0.85 / 2× ou 0.5× = half/double-time 0.7 / 0.90-1.10 = pitch shift 0.5.

**Score transition** : `0.5 × bpm + 0.3 × key + 0.2 × energy`. Veto hard
sur energy si direction `rising`/`falling` et chute/montée trop violente.

**Playlist builder** : greedy local, pas d'optimisation globale (TSP
inutile sous 2h). Flag `--max-track` (défaut 15 min) exclut les mix long
du pool. Plancher d'énergie auto à `peak - 2 crans` en mode `--peak`.

**Export** : `--export-m3u8 <path>` pour import Mixxx.

### Phase 5 — Visualisation PNG (`visualize.py`)

PNG 1200×320 par track : header texte + waveform RMS + mel-spectrogram
magma log-freq + bande structure colorée + cues overlay. Stockée dans
`library/visuals/<slug>.png`. Index Markdown auto `_index.md` pour
browser dans Obsidian en vue d'avion.

Couleurs segments : intro=gris clair / build=orange / peak=rouge /
main=bleu / breakdown=violet / outro=gris foncé.

### Pipeline `grab.py --analyze-quality` bout-en-bout

```
recherche YT/SC + sélection meilleure qualité (codec*multiplicateur*match)
└─ download (codec natif, FLAC seulement si source lossless)
   └─ tags audio (mutagen, multi-conteneur)
      └─ analyse BPM/key (librosa)
         └─ library.md upsert (champs préservés)
            └─ Phase 1+2 sidecar JSON + quality_score
               └─ infer (genre/energy/mood/tags)
                  └─ describe MusicBrainz (about)
                     └─ visualize PNG + maj index
```

Une seule commande, tout est rempli.

---

## État Phase 6 (livrée le 2026-05-31)

Les trois axes A/B/C ont été implémentés. Format library.md migré en
table markdown unique le même jour (64 entrées migrées, 0 perte).

### 6.A — Analyse fréquentielle par bandes ✓

**But** : savoir en 1 seconde si un track va péter sur le sub, ou s'il
manque de basses pour un peak free party.

**Bandes implémentées (7 au total)** :
- sub      (20-60 Hz)    → critical pour sound system
- bass     (60-200 Hz)
- low-mid  (200-500 Hz)  → zone de mud
- mid      (500-2 kHz)   → corps des leads
- presence (2-5 kHz)     → clarté / intelligibilité
- high     (5-10 kHz)    → cymbales / harmonies aigues
- air      (10 kHz+)     → harmoniques

**Métrique** : % d'énergie dans chaque bande (Welch PSD intégrée).
Total normalisé à 100%.

**Tonal profile heuristique** : `bass-heavy` / `warm full` / `balanced`
/ `mid-heavy` / `bright` / `thin` selon distribution.

**Sortie** :
- Sidecar JSON : champ `frequency_bands` (FrequencyBandsReport Pydantic)
- library.md : champ `band_profile` compact, ex :
  `sub:12 bass:70 lowmid:8 mid:3 pres:2 high:5 air:0 | bass-heavy`
- PNG visualize : `tonal_profile` ajouté au header texte (pas de
  barchart visuel, reporté)

**Modules** : `analyzer/frequency_bands.py`, types Pydantic, intégration
dans `analyzer/pipeline.py`, propagation library.md depuis grab.py +
analyze.py.

### 6.B — Stems separation via Demucs

**But** : extraire `drums.wav`, `bass.wav`, `other.wav`, `vocals.wav`
de chaque track pour les **sampler dans TidalCycles**. Change
qualitativement ce qu'on peut faire en live coding.

**Outil** : Demucs (Meta, MIT, ~1 Go modèle htdemucs). Auto-détection
device : **MPS sur Apple Silicon** (~15-25s/track), CUDA si dispo,
fallback CPU (~30-60s/track). Dépendance transitive : `torchcodec`.

**Sortie** :
```
library/stems/<slug>/
├── drums.wav
├── bass.wav
├── other.wav
└── vocals.wav
```

Demucs écrit toujours dans `<out>/<model>/<audio_stem>/` malgré le
flag `--filename`, on **aplatit par move post-traitement** vers
`library/stems/<slug>/`.

**Intégration** :
- Script `scripts/stems.py` CLI standalone (pas dans pipeline `grab`
  par défaut, opt-in pour ne pas alourdir chaque download)
- Champ `has_stems: yes` dans library.md (mis à jour quand stems
  générés)
- Flags : `--model`, `--device auto|cpu|cuda|mps`, `--force`, `--all`

**Cleanup techno-aware** (`--cleanup`) : module `analyzer/stems_cleanup.py`
qui applique 3 règles domain après Demucs :
1. Highpass `bass.wav` à 60 Hz (retire le sub-kick résiduel)
2. Lowpass `bass.wav` à 500 Hz (retire fuites de leads)
3. Merge `vocals.wav` dans `other.wav` si RMS < -40 dBFS (track instrumental)

Marqueur `has_stems: cleaned` dans library.md. Overwrite des stems
(pas de version raw préservée). Règles techno-aware uniquement —
empirent pop/rock.

**Résultats sur la library (62 tracks traités, 2026-05-31)** :
- 62/64 nettoyés (2 misses = audio absent)
- 10/62 ont eu le merge vocals déclenché (tracks instrumentaux :
  Floxytek, Hertz, Kangding Ray, Kontinum, Ororr...)
- Tous les tracks à voix réelle ont gardé `vocals.wav` intact

Doc pédagogique détaillée : [[technique/cleanup-stems-techno]].

**Pas implémenté** : index Obsidian `library/stems/_index.md` (skip,
les stems sont organisés en dossiers parlants par slug) et export
`samples.tidal` (à voir si besoin réel — la convention `~dirt.loadSoundFiles`
dans le startup.scd SuperCollider suffit en pratique). Fine-tune Demucs
sur techno : reporté pour absence de dataset paired public.

### 6.C — Rythmique enrichie ✓

**Champs ajoutés à `BeatReport`** :
- `onset_density_per_s` (events/sec) : "complexité rythmique" — 4-6/s
  pour DnB/tribe, 2-3/s pour downtempo
- `beat_strength` : amplitude moyenne de l'onset envelope aux positions
  de beats — proxy de "punch" / poids du kick
- `time_signature` (str) : `4/4` / `3/4` / `6/8` / `5/4` / `7/8` / `17/8`
- `time_signature_confidence` (0-1) : 0.3 = défaut 4/4 / >0.5 = signal fort

**Méthode time signature** : autocorrelation des beat strengths sur lag K
pour chaque candidat. Bias 4/4 (×1.3 + 0.05). **Floor 0.15** : si la
confiance du gagnant non-4/4 est trop faible, on retombe sur 4/4 par
défaut. Detection 17/8 sur Noisia "The Hole Pt. 1" possible mais
confidence basse (0.09) — limite de la méthode librosa-only.

**Affichage terminal** : `signature: 4/4 (conf=0.30) | onsets: 4.35/s | beat strength: 1.35`

**Modules** : ajouts dans `analyzer/beat_tracking.py::_enrich_rhythm`.
Intégration automatique dans le pipeline (Phase 2 toujours).

### 6.D — Signature de groove + export MIDI/Tidal ✓

**But** : décrire la *forme* du pattern rythmique (groove), tempo-invariante,
pour trouver des tracks au groove proche et regrouper la library en familles.
Axe orthogonal à Camelot + BPM + energy : deux tracks à 180 BPM peuvent être un
tribe roulant syncopé ou un acid four-on-floor martelé — même BPM/key/energy,
groove radicalement différent.

**`RhythmSignatureReport`** (dans `BeatReport`/sidecar, calculé en Phase 2) :
- `bar_pattern` / `sub_pattern` / `mid_pattern` / `high_pattern` (16 pas,
  normalisés min-max) : pattern global + par bande (sub=kick, mid=snare,
  high=hats), replié sur la mesure via `beat_times`
- `syncopation` (0-1) : énergie hors-temps pondérée (martelé ↔ roulant)
- `pulse_clarity` (0-1) : régularité du pulse (autocorrélation onset env)
- `swing` (0-1) : microtiming des contretemps (0.5 = droit)

**Anti-redondance** : la signature **n'encode ni BPM, ni key, ni energy** (déjà
couverts par `compatibility.py`). C'est ce qui la rend orthogonale et lève
l'objection de la décision arbitrée sur le clustering générique (cf. infra).

**Similarité** : `rhythm_distance` ∈ [0,1] compare les patterns par
cross-corrélation sur les 16 rotations (invariance à la phase du downbeat) +
scalaires. Repliage en 4/4 par défaut sauf signature impaire confiante
(`time_signature_confidence ≥ 0.5`).

**Consommation** (`setbuilder.py`) :
- `similar <slug>` : voisins de groove (nearest-neighbor, indépendant du BPM)
- `groove-clusters [--k 6] [--write]` : familles via clustering agglomératif
  (sklearn, métrique = `rhythm_distance`) ; `--write` écrit `groove_cluster`
  dans library.md. Indicatif sur une petite library.

**Export groove jouable** (`groove.py`, opt-in) : transcrit le pattern en hits
discrets depuis le **stem drums Demucs** (`library/stems/<slug>/drums.wav`,
fallback mix avec warning), seuillés sur le pattern replié+étiré, calés sur le
kick le plus fort. Sorties `library/grooves/<slug>.{mid,tidal}` :
- `.mid` : clip batterie GM (kick=36, snare=38, hat=42) → Renoise / DAW
- `.tidal` : `d1 $ stack [s "bd ~ ...", ...]` collable en live

**Modules** : `analyzer/rhythm_signature.py` (extraction + distance +
clustering), `groove.py` (export). Dép. ajoutée : `mido` (MIDI, pur python).
Tests : `tests/test_rhythm_signature.py`.

---

## Décisions arbitrées (à NE PAS refaire)

- **Phase 3 (export DJ XML Rekordbox/Traktor)** : skipée intentionnellement.
  Pas de DJ software dans la chaîne TidalCycles. Si besoin futur de mixer
  hors Tidal, ressortir Phase 3.
- **Plots matplotlib génériques** (waveform standalone, spectrogramme
  isolé) : couverts par Phase 5 visualize. Pas besoin de plots séparés.
- **Clustering algorithmique GÉNÉRIQUE librosa-only** : peu de valeur vs vue
  d'œil sur les PNG. Sans embeddings deep (CLAP/OpenL3), un clustering global
  redonde avec Camelot+BPM+energy. **Nuance (Phase 6.D)** : le clustering/
  voisinage par **signature de groove** est lui retenu, car il décrit la
  *forme* rythmique (pattern/syncope/microtiming) — un axe orthogonal que
  BPM+key+energy n'encodent pas. La signature exclut volontairement ces
  champs pour rester non redondante. Cf. section 6.D.
- **ML genre / mood classification** : modèles deep trop lourds
  (CLAP/OpenL3 ~500 Mo), ROI marginal sur tribe/acid core (hors dataset
  d'entraînement). À reconsidérer si on bascule sur DnB plus mainstream.
- **aubio, madmom** : ne s'installent pas sur Python 3.14.4. Pas la
  peine de retenter sans changement upstream.
- **`infer --force` écrasant par vide** : précédemment effacait les
  édits manuels. Corrigé : `--force` n'écrase non-vide que par non-vide,
  jamais par vide.

---

## Tier 2 — Possibilités futures cataloguées

À activer à la demande, classés par valeur descendante.

### Tier 2 (bon ROI, prêt à coder)

- **Spotify-like features sans ML** : danceability (tempo stability ×
  beat strength × regularity), instrumentalness (HPSS), acousticness
  (flatness spectrale), speechiness (zone vocale soutenue).
- **Mix-in / mix-out points auto** : zones de faible densité spectrale
  exposées comme cues additionnels (cf. `mix_in_window` / `mix_out_window`).
- **Compression / brickwall detection** + **LUFS short-term curve** en
  overlay sur waveform de la PNG.
- **Downbeat detection** : où est le "1" de chaque mesure. Aligne les
  cues sur les phrases pour mixes propres.

### Tier 3 (moins prioritaire)

- **Chord progression** via Chordino / Crema — couvert essentiellement
  par Camelot
- **Stereo width / mono compat** — marginal en sound system mono
- **Loop point detection** — Demucs + oreille fait mieux
- **Tonnetz** (réseau harmonique) — visualisation plus que action

### Tier 4 (lourd, ROI incertain)

- **Genre / mood classification via CNN** (Essentia models, OpenL3
  embeddings) : besoin de gros modèles, résultats parfois faux sur
  tribe/acid core
- **Auto-tune detection** : intéressant mais hors scope
- **Vocal isolation deep** : Spleeter (vieux), Demucs déjà top
- **Embeddings deep pour similarité** (CLAP, OpenL3) : ~500 Mo, ouvre
  recommandation contextuelle riche mais usage marginal

---

## Sources d'inspiration

État de l'art consulté en mai 2026 :

- **Rekordbox 7** : phrase analysis (intro/build/drop/breakdown/outro),
  key detection, color-coded waveform par bandes de fréquence (rouge=low,
  vert=mid, bleu=high), energy level. Standard de l'industrie DJ.
- **Mixed In Key 11** : energy level 1-10, cue points auto Intros/Outros/
  Breakdowns/Drops/Bridges, key Camelot, sort par energy/tempo/key/genre.
- **Spotify Audio Features API** : danceability, energy, valence,
  acousticness, instrumentalness, speechiness, loudness, tempo, key,
  mode, time signature, duration. Toutes mesurables depuis librosa +
  spectrogramme + HPSS sans ML.
- **Essentia** (Pompeu Fabra MTG) : tonnetz, chroma, spectral contrast,
  MFCC, onset density, HPSS. C++ avec wrapper Python (lourd à compiler).
- **MIRFLEX paper (2024)** : librairie MIR open-source qui unifie
  beaucoup d'extracteurs en un.
- **Demucs** (Meta) : SOTA stems separation, CPU OK pour batch.

## Liens internes

- [[scripts/README]] — manuel opérationnel des outils
- [[scripts/quality-analyzer|scripts/quality-analyzer.md]] — spec
  initiale brain-dump (historique, gardée pour mémoire)
- [[sets/etude-cas-build-vers-moliy]] — étude de cas pédagogique théorie
  mix
- [[journal]] — entrées chronologiques

#projet #spec
