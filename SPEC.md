---
tags: [spec, projet, library, dj, mir]
updated: 2026-10-06
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
├── digitakt.py                   # draft de bank Digitakt II (Phase 7.B)
├── kb.py                         # base de connaissance Digitakt (Phase 7.D)
├── sounddesign.py                # traitements par chaînes de plugins (Phase 8)
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
    ├── visualize.py              # render_track + write_index_md
    ├── digitakt.py               # grille 16 tracks, patterns, mutes, MIDI
    └── sounddesign.py            # devices, traitements, presets, rendu en boucle
```

### Schéma de la library

Deux racines, centralisées dans `scripts/paths.py` (hub unique) : les
**métadonnées** restent dans le vault (versionnées, disponibles sans le
disque), le **média** vit sur le SSD externe `xtreme` (`MUSIC_MEDIA_ROOT`,
défaut `/Volumes/xtreme`), dédié au son.

```
music/library/                    # vault (git)
├── library.md                    # source de vérité : table markdown unique
├── library.md.backup-*           # backups pre-migration
├── quality/<slug>.json           # sidecars Phase 1+2+6A+6C (Pydantic)
├── artists/<slug>.json           # cache MusicBrainz
├── digitakt/<slug>.{json,md}     # banks Phase 7
├── audio   -> <MEDIA>/Mix/audio      # symlinks : wikilinks et embeds Obsidian
└── visuals -> <MEDIA>/Mix/visuals

<MEDIA>/                          # /Volumes/xtreme
├── .music-media                  # marqueur (require_media)
├── Mix/                          # tracks pour le mix (Rekordbox)
│   ├── audio/<style>/<slug>.{flac,m4a,mp3}
│   ├── stems/<slug>/{drums,bass,other,vocals}.wav  # Phase 6.B Demucs
│   └── visuals/<slug>.png + _index.md              # Phase 5
├── Live/                         # matériel de set live
│   ├── renoise/*.xrns
│   ├── grooves/<slug>.{mid,tidal}
│   └── digitakt/<slug>/pNN.mid
└── Samples/, Sounds/             # banque de samples (hors pipeline)
```

La colonne `file` (`[[audio/<slug>.flac]]`) et le `file_path` des sidecars
sont relatifs à `<MEDIA>/Mix/`. **Formats audio : uniquement ceux que lit
Rekordbox** (`.flac`, `.m4a`, `.mp3`) ; `grab.py` transcode opus/vorbis en
FLAC (décodage sans nouvelle perte). Les commandes media (`grab`, `stems`,
`visualize`, `groove`, `to_xrns`, `digitakt`, `analyze --all`) sortent en
code 2 si le disque est absent ; `setbuilder`, `kb`, l'API restent
utilisables sans lui. Migration one-shot : `scripts/migrate_media.py`.

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
`<MEDIA>/Mix/visuals/<slug>.png`. Index Markdown auto `_index.md` pour
browser dans Obsidian en vue d'avion.

Couleurs segments : intro=gris clair / build=orange / peak=rouge /
main=bleu / breakdown=violet / outro=gris foncé.

### Pipeline `grab.py --analyze-quality` bout-en-bout

```
recherche YT/SC + sélection meilleure qualité (codec*multiplicateur*match)
└─ download dans <MEDIA>/Mix/audio/<style>/ (FLAC si lossless ou opus/vorbis, m4a/mp3 natifs)
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
<MEDIA>/Mix/stems/<slug>/
├── drums.wav
├── bass.wav
├── other.wav
└── vocals.wav
```

Demucs écrit toujours dans `<out>/<model>/<audio_stem>/` malgré le
flag `--filename`, on **aplatit par move post-traitement** vers
`<MEDIA>/Mix/stems/<slug>/`.

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

**Pas implémenté** : index Obsidian `<MEDIA>/Mix/stems/_index.md` (skip,
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
discrets depuis le **stem drums Demucs** (`<MEDIA>/Mix/stems/<slug>/drums.wav`,
fallback mix avec warning), seuillés sur le pattern replié+étiré, calés sur le
kick le plus fort. Sorties `<MEDIA>/Live/grooves/<slug>.{mid,tidal}` :
- `.mid` : clip batterie GM (kick=36, snare=38, hat=42) → Renoise / DAW
- `.tidal` : `d1 $ stack [s "bd ~ ...", ...]` collable en live

**Modules** : `analyzer/rhythm_signature.py` (extraction + distance +
clustering), `groove.py` (export). Dép. ajoutée : `mido` (MIDI, pur python).
Tests : `tests/test_rhythm_signature.py`.

---

## Phase 7 — Digitakt II (en cours, démarrée le 2026-10-06)

**But** : analyser des morceaux de référence sous l'angle patterns / tracks du
workflow Elektron, et aider à produire des sets live sur Digitakt II. Source
of truth des conventions : [[digitakt/doctrine]] (grille des 16 tracks, banks,
mutes, FX de transition, principes d'arc).

| Sous-phase | Contenu | Statut |
|---|---|---|
| 7.A | Doctrine `digitakt/doctrine.md` | fait |
| 7.B | `digitakt.py` : draft de bank (JSON + note + MIDI par pattern) | fait |
| 7.C | Front POC : FastAPI (`scripts/api.py`) + Svelte/Vite + wavesurfer.js (`web/`) : lib, lecteur, vue bank synchronisée ; natif Mac ensuite via Tauri | fait (POC web) |
| 7.B2 | Premier temps de la mesure + structure déduite des patterns + réutilisation de slots (cf. plan ci-dessous) | fait (premier temps à valider à l'oreille) |
| 7.D | Base de connaissance `digitakt/kb/*.md` + recherche plein texte dans le front | fait : recherche + panneau, 25 fiches en 5 lots (statut draft, à tester sur la machine) |
| 7.E | Enregistrement assisté (requalifié) : script mido qui rejoue les `.mid` de bank track par track sur l'AUTO CHANNEL pendant un `[RECORD]`, plus pré-réglage des sons par CC / NRPN (cf. [[digitakt/kb/cc-nrpn]]) | en cours : envoi d'une track depuis le front fait (`dt2_midi.py`, à valider sur la machine) ; sortie du lecteur vers la DT2 pour l'échantillonner faite (à valider sur la machine) ; pré-réglage CC / NRPN à venir |
| 7.F | KB intégrée au front : bandeau d'accès, sommaire par lot, liens vers le manuel PDF (table § → page tirée du sommaire du PDF, `/api/manual#page=N`) | fait |
| 7.G | Façade DT2 complète et interactive (potards, touches de page, transport…) reliée aux fiches et au manuel ; base du pilotage MIDI | fait (ordre des knobs à vérifier sur la machine) |
| 7.H | Analyse harmonique : gamme (noms du KEYBOARD SETUP de la DT2) et accords par mesure, `harmony.py`, sidecar + note de bank + front | fait |
| 7.I | Ajout d'un morceau depuis le front : recherche → choix du candidat → job d'acquisition + analyse | fait |
| 7.J | Bibliothèque de samples DT2 : classement famille / code des packs de `<MEDIA>/Samples` (7.J1, `samples.py`), pré-filtre qualité et écoute garder / écarter dans le front (7.J2), export renommé vers `<MEDIA>/Live/samples/` pour Transfer (7.J3), vue par kit (7.J5), recherche multi-facettes et tags inférés (7.J6), tonalité des one-shots tonals (7.J7), arbre du +Drive par type / code / sous-catégorie et plafond par dossier (7.J8) | fait (7.J1 à 7.J8) ; reste l'écoute elle-même, l'export se rejoue après |
| 7.K | Coquille du front : barre générale avec télécommande (morceau ou sample : précédent, lecture / pause, boucle, suivant), panneau latéral minimisable à icônes (Morceaux, Samples, Knowledge), filtre des morceaux par tags multiples, tri date / alpha, historique et recherche en ligne dans les propositions | fait (à valider à l'usage) |

**Décisions 7.I** (arbitrées le 2026-10-07) :
- Parcours **recherche puis choix** : la requête (ex. « Limitlezz x Maureen -
  Shatta Mad ») liste les candidats YT/SC (source, codec, débit, pertinence),
  le meilleur présélectionné ; l'utilisateur valide ou en choisit un autre.
- `grab_one` découpé en `search(query)` (candidats structurés) et
  `ingest(url, options)` ; la CLI `grab.py` les réutilise.
- API : `POST /api/grab/search` (synchrone), `POST /api/grab` (job en
  arrière-plan, **un à la fois** pour sérialiser les écritures de
  library.md), `GET /api/jobs/{id}` (étapes + statut, polling). Lève le
  principe « API en lecture seule » pour cette seule route, comme la bank.
- Job : téléchargement + analyse complète (`--analyze-quality` + visuel)
  par défaut ; **stems Demucs** et **bank Digitakt** (+ harmony) en cases à
  cocher. Exige le disque média (`require_media`).

**Décisions 7.B** :
- 1 morceau = 1 bank ; 1 section de structure = 1 pattern (<= 16, fusion des
  plus courtes) ; longueur 1/2/4/8 mesures (<= 128 pas).
- Patterns = sections (grossières), mais **partition de mutes par phrase**
  (8 mesures par défaut) : c'est elle qui raconte le morceau.
- Beats re-suivis sur le kick du stem drums (cf. [[scripts/README]]).
- Id1 / Id2 jamais remplies automatiquement.
- Sortie MIDI : canal = track, à enregistrer en live recording (la DT2
  n'importe pas de fichier de pattern).
- Partition de mutes : les phrases repartent à chaque début de section (une
  phrase ne chevauche jamais deux patterns).

**Plan 7.B2 (arbitré le 2026-10-06)** :
1. **Premier temps de la mesure** : `kick_shift` ne corrige que la phase à
   l'intérieur d'un temps, donc la mesure peut démarrer sur le temps 2, 3 ou 4
   (constaté sur les boucles du front). Tester les 4 décalages de beat, garder
   celui qui maximise l'alignement des changements d'activité des tracks sur
   les débuts de mesure / phrase et le clap sur les temps 2 et 4.
2. **Structure déduite des patterns** : remplacer la segmentation librosa
   (grossière) par un découpage là où l'ensemble des tracks actives change,
   sur une grille de 4/8 mesures alignée sur le premier temps. Labels déduits
   du contenu (sans kick = breakdown, tout actif = peak, peu de tracks au
   début = intro). Le front affiche cette structure à la place de celle du
   sidecar.
3. **Réutilisation de slots** : deux sections au contenu identique (même
   activité + grilles proches) partagent le même pattern ; la bank expose un
   ordre de jeu (ex. 1-2-1-3), comme une chaîne de patterns sur la DT2.

**Décisions 7.B2 (implémentation)** :
- Grille de structure fixée à 4 mesures (pas 8) : les bascules réelles
  tombent souvent sur 4.
- Réutilisation : mêmes tracks actives (activité par mesure, fiable) **et**
  Jaccard moyen des grilles ≥ 0,3 (les trigs sont trop bruités pour un seuil
  plus haut : des sections identiques à l'oreille plafonnent vers 0,3-0,45).
- Drop (impact FX) = retour du kick après une section sans kick, au lieu du
  saut de RMS du sidecar.
- **À vérifier sur la machine** (fiche `kb/midi-config`) : le manuel ne
  garantit pas l'enregistrement simultané des 16 canaux d'un `.mid` ; la
  voie documentée est l'AUTO CHANNEL vers la track active (une track à la
  fois). Si confirmé, `write_pattern_midi` pourrait sortir un `.mid` par
  track.
- Exemple `2hot2play_-_keep_the_balance` : 15 sections, 13 patterns, chaîne
  `01 … 11 06 05 12 13`, mesure décalée de 2 temps.

**Décisions 7.D (arbitrées le 2026-10-06)** :
- Contenu = **fiches pédagogiques courtes rédigées** depuis le manuel
  (`refs/Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf`), pas un découpage
  automatique (révisé le 2026-10-06 : remplace l'import par signets).
- 25 thèmes en 5 lots, dans l'ordre de **préparation d'un set** ; liste et
  statuts dans le hub [[digitakt/kb/_index]]. Un lot par session.
- Format arbitré : frontmatter (`theme`, `lot`, `ordre`, `manuel`, `os`, `statut`),
  *En une phrase*, *Gestes rapides*, *Pas à pas*, *En live techno*,
  *Pièges*, *À essayer (5 min)* ; 40-70 lignes ; `statut: draft` jusqu'au
  test sur la machine.
- Recherche sur KB + doctrine, résultats par section avec extrait surligné.
- Affichage en panneau latéral (`/`), accessible pendant la lecture.

**Décision 7.E (requalifiée le 2026-10-06)** : l'annexe B du manuel ne donne
aucun NRPN pour poser un trig sur un pas (les NRPN 3:0-3:2 règlent la note, la
vélocité et la longueur par défaut de la track). Le push direct des trigs est
abandonné ; 7.E devient un enregistrement assisté (le script rejoue chaque
piste du `.mid` sur l'AUTO CHANNEL pendant que la DT2 enregistre, une track à
la fois) et un pré-réglage des sons par CC / NRPN. Piste non retenue : le
SYSEX DUMP de pattern (§14.5), format non documenté.

**Décisions 7.E, envoi d'une track (arbitrées le 2026-10-07)** :
- **La DT2 mène** : l'utilisateur lance `[RECORD] + [PLAY]`, le script attend
  le Start MIDI et cale les notes sur l'horloge reçue (`CLOCK SEND` +
  `TRANSPORT SEND` en USB). Pas d'horloge envoyée par le Mac.
- Notes sur l'**AUTO CHANNEL**, saisi dans le front (mémorisé par le
  navigateur), pas sur le canal de la track.
- **Un seul passage** du pattern ; un Stop reçu avant la fin annule.
- Périmètre : la track sélectionnée du pattern affiché, un envoi à la fois.
  Enchaînement guidé des 16 tracks et pré-réglage CC / NRPN hors slice.
- Notes, vélocités et gate identiques au `.mid` de bank (helper partagé
  `track_note_events`). L'envoi n'écrit rien sur disque.

**Décisions 7.E, sortie du lecteur vers la DT2 (arbitrées le 2026-10-08)** :
- Le lecteur choisit sa sortie audio (`setSinkId`) : la DT2 en USB CONFIG =
  `USB AUDIO/MIDI` apparaît comme périphérique ; on l'échantillonne en
  `[SAMPLING]` `SRC` = USB (écoute : `USB IN` = `MAIN`).
- Choix mémorisé par le navigateur, par libellé (l'identifiant varie selon
  les permissions), réappliqué à chaque morceau et à chaque changement de
  périphérique ; sortie absente = sortie système, signalée.
- Chrome masque les sorties sans autorisation micro : demande unique, flux
  coupé aussitôt. Sélecteur masqué si `setSinkId` n'est pas supporté
  (à vérifier sous Tauri / WKWebView).

**Décisions 7.G (arbitrées le 2026-10-06)** :
- Les 23 contrôles du §3.1 sont dessinés à l'échelle et aux emplacements du
  dessin du manuel (panneau 834 × 682), sérigraphie des fonctions secondaires
  en orange ; AIDE et FOLLOW (propres au front) hors du panneau.
  Ce qui a un sens dans le front agit : PLAY (lecture / pause), STOP (retour
  au début du pattern en cours), TRK, `[FUNC]` + TRK (MUTE), PTN et
  `[LEFT]`/`[RIGHT]` (lettre de bank), PAGE, LEDs de page, touches PARAMETER
  (appuis successifs = page suivante). Les autres affichent leur légende.
- `[FUNC]` est une bascule (pas de maintien à la souris) ; bouton AIDE (propre
  au front, comme FOLLOW) : un clic sur un contrôle ouvre sa fiche, ou le
  manuel à défaut. Clic = légende épinglée (fonction, FUNC, fiche, § et page), survol = aperçu
  temporaire, pour atteindre les liens sans que la légende change en route.
- Potards A-H : noms des paramètres de la page active (§11, machines par
  défaut ONESHOT et MULTI-MODE), valeurs `--` sauf NOTE / VEL du pas courant
  (seules valeurs connues de la bank). Pas de valeur éditable.
- Pilotage MIDI : table de mapping seule (CC / NRPN de l'annexe B, affichés
  dans la légende), aucun envoi ; l'envoi reste en 7.E. Hub :
  `web/src/lib/dt2.ts` ; si 7.E en a besoin côté Python, le déplacer en JSON
  partagé plutôt que dupliquer.
- Ordre des knobs = ordre du texte du manuel, à vérifier sur la machine
  (TRIG 2, FLTR 2, AMP à 9 paramètres) ; numéros FX / FLT.T / LFO.T sans
  colonne sûre dans l'extraction de l'annexe, signalés « à vérifier ».
- Route `/api/manual/outline` (§ → page) pour résoudre les liens de la façade.

**Décisions 7.H (arbitrées le 2026-10-06)** :
- Gammes reconnues : les 7 modes, mineurs harmonique et mélodique,
  pentatoniques majeure et mineure, blues, sous leurs noms KB SCALE (annexe D)
  pour être reportées telles quelles sur la machine (§8.5.2).
- Accords : triades (majeur, mineur, sus2, sus4, diminué) et quinte à vide, un
  par mesure avec confiance, « N » sans contenu tonal ; progression = accords
  distincts par section. Pas de 7e ni de résolution au temps.
- Calcul sur les stems (other en HPSS, notes dominantes par trame ; basse =
  note tenue, départage la fondamentale), repli sur le mix. Grille de mesures
  de la bank si elle existe, sinon beats du sidecar.
- Marge = écart avec la meilleure autre fondamentale ; sous 0,05 la gamme est
  « incertaine » (cas typique : modes relatifs, ex. F majeur / A# lydien). Les
  gammes voisines sur la même fondamentale sont des alternatives, pas une
  incertitude.
- Sorties : bloc `harmony` du sidecar (conservé par une re-analyse), section
  Harmonie et `scale` en frontmatter de la note de bank (pas de colonne dans
  `library.md`), front (entête du lecteur, bande d'accords, écran DT2).
- Front : `harmony` et `keyboard_setup` exposés par `GET /api/tracks/{slug}` ;
  l'écran DT2 passe par la touche [KEYBOARD] (mode KB SETUP), les trig keys
  montrent la gamme sur le clavier chromatique (pas de FOLD simulé).
- (Re)générer la bank depuis le front relance aussi `harmony.py`, sur la grille
  de la nouvelle bank ; un échec de l'harmonie ne bloque pas la bank.

**Décisions 7.J (arbitrées le 2026-10-07)** (arbre du +Drive et quotas
révisés par 7.J8) :
- 3 niveaux sur le +Drive : famille / code / fichier. Familles : HARDCORE,
  JUNGLE, DUBSTEP, TECHNO, TRIBE (pack Tribalism Vol. 1 à venir, kit
  neurotek depuis le 2026-10-07),
  AUTRES (house, EDM, world), UNIVERSEL (machines, FX, instruments, foley,
  Native Instruments, minimoog), SAMPLE (samples et resamples maison).
- Codes à 2 lettres façon Elektron (BD RM SD CP HH OH CY TM PC, boucles BR DL
  PL ML BL, puis BS ST PD FX VX RS), aussi en tête du nom :
  `<CODE> [BPM|note] <desc> <pack>`, 18 caractères au plus (≈ 14 visibles
  dans la liste des samples d'une track, où le dossier n'apparaît plus).
  RM (rumble, track 2 de la doctrine, 8.E) n'est jamais inféré d'un nom de
  fichier : seuls les rendus du sound design y entrent, par override.
  BPM en tête pour les boucles, note pour BD / BS / ST / PD / ML / BL.
- Boucles découpées au niveau 2 (pas de 4e niveau, le code reste lisible à
  l'écran) : BR break, DL drums (défaut), PL percussions / hats / tops, ML
  mélodie (synthé, lead, accords, séquences), BL basse ; une boucle de nappe
  va en PD, de voix en VX, un build en FX.
- Stéréo conservée (400 Mo de RAM par projet) ; les doublons mono d'un pack
  livré en mono et stéréo sont écartés. Pas de dossier « set » : la RAM du
  projet joue ce rôle.
- Sélection par quotas par case famille × code : 16 drums et boucles
  (BR / DL / PL / ML / BL), 8 le reste, 32 pour BD / BR / DL / PL en
  HARDCORE, JUNGLE, TRIBE (PL : JUNGLE et TRIBE) et pour UNIVERSEL/BD, tout
  SAMPLE. Révisé le 2026-10-07 : ML et BL de 8 à 16, PL à 32 en JUNGLE et
  TRIBE (trop peu de boucles retenues). Une case de moins de 4 fichiers (hors UNIVERSEL
  et SAMPLE) rejoint le même code dans UNIVERSEL.
- Candidats = 3 × quota, alternés entre sous-dossiers ; l'écoute (7.J2) passe
  chaque candidat en `keep` / `drop`. Les `keep` priment, puis les `pending`
  par rang, jamais les `drop`.
- `<MEDIA>/Samples` n'est jamais modifié. Manifeste et overrides dans le vault
  (`library/samples/`) ; le manifeste est rejouable et garde les décisions
  d'écoute.
- 7.J2 (arbitré le 2026-10-07) : le pré-filtre qualité reclasse et signale
  (drapeaux), il n'écarte rien ; l'écoute porte d'abord sur les sélectionnés,
  un drop faisant monter le candidat suivant, la réserve restant consultable ;
  vue Samples du front pilotée au clavier (K keep, D drop, flèches) avec
  forme d'onde. Changement de case à l'écoute (M) : statut gardé, écrit dans
  `overrides.json`. Un tempo dans le nom (`170_…`, `_120_`) sur 2 s ou plus,
  hors dossier one-shot, fait une boucle (moins d'une seconde : one-shot) ;
  une boucle sans tempo écrit reçoit le tempo de l'audio (calé sur les
  mesures, sinon estimé et signalé) ; les doublons exacts entre packs
  (même nom, même taille) n'en gardent qu'une copie.

**Décisions 7.J3 — export (arbitrées et faites le 2026-10-07)** :
- On exporte les retenus (`selected` : gardés, puis pending dans le quota),
  sans attendre la fin de l'écoute ; on réexporte après.
- Copie telle quelle (pas de conversion : Transfer convertit à l'envoi),
  vers `<MEDIA>/Live/samples/<FAMILLE>/<CODE>/<nom>.wav`.
- Rejouable : `library/samples/export.json` indexe les fichiers écrits par
  l'export ; seuls ceux-là peuvent être retirés (sortis des retenus ou
  changés de case), un fichier posé à la main n'est ni écrasé ni supprimé.
  Les dossiers de case vidés sont retirés.
- `samples.py --export [--dry-run]` et bouton « Exporter… » de l'onglet
  Samples (bilan d'abord, copie sur confirmation).

**Décisions 7.J4 — UX de la bibliothèque (arbitrées le 2026-10-07, faites)** :
- Non classés (407) : zone « Non classés » avec écoute ; on leur donne une
  case famille × code (glisser vers la matrice ou `M`) et des tags libres ;
  écrit dans `overrides.json`, ils deviennent candidats.
- Tags manuels en texte libre, autocomplétion sur les tags déjà utilisés,
  filtrables (liste et grille), stockés dans `overrides.json`.
- Étoiles 1 à 5 : filtrables, et un sample noté passe devant les non-notés
  dans sa case (rang) ; noter ne vaut pas garder.
- Corbeille = statut séparé de `drop` : `drop` = pas pour cette case
  (recasable), corbeille = son rejeté partout, sorti de toutes les cases et
  reclassements, restaurable, jamais supprimé du disque.
- Glisser-déposer d'un sample (ou d'une sélection) vers une case de la
  matrice ou vers la corbeille.
- Sélection multiple (clic, Maj, Cmd) et barre d'outils : garder, écarter,
  corbeille, tagger, étoiles, changer de case.
- Mise en œuvre : tags, étoiles et corbeille vivent dans `overrides.json`
  (champs `tags`, `stars`, `trash`) et sont recopiés sur les candidats du
  manifeste (`trashed` liste la corbeille). Un sample noté reste candidat
  hors du plafond de 3 × quota, comme un déplacé. La restauration renvoie en
  fin de sa case d'origine (override ou règles), sinon parmi les non classés.

**Décisions 7.J5 — vue par kit (arbitrées et faites le 2026-10-07)** :
- Un kit est un préfixe de chemin déduit de l'arborescence, sans table à
  tenir : le pack (dossier de premier niveau) puis son sous-dossier
  (`Native instrument/caribean`) ; un dossier `packs` regroupe des kits et
  est traversé (`rthm/packs/neurotek`). 29 packs, 125 kits.
- Front : pads assez gros sous la grille (zone vide de la colonne de
  gauche), un par pack, puis ceux des sous-kits du pack choisi ; re-clic
  pour tout revoir. Un pad filtre grille, cases, non classés et corbeille.
- Tout le kit est visible, plafond compris : le manifeste liste la réserve
  (`reserve`, fichiers classés au-delà de 3 × quota, non mesurés, environ
  8 000). Garder, écarter, noter ou ranger un fichier de la réserve le fait
  entrer comme candidat en fin de case (mesuré à ce moment). Sans kit, un
  second appui sur `R` ajoute la réserve hors plafond de la case (demande du
  2026-10-07) ; le nombre de fichiers hors plafond s'affiche dans l'en-tête de la case.
- Vue kit (demande du 2026-10-07) : choisir un kit ouvre à droite son
  arborescence par classement final, FAMILLE / CODE / fichiers (dossiers
  repliables, « retenus / total »), avec tous ses fichiers marqués (retenu,
  réserve, hors plafond, gardé, écarté ; corbeille exclue), nom DT2 et
  chemin source, puis un dernier dossier « Non classés ». L'écoute et les
  actions (K / D, M, étoiles, tags) y restent actives ; un clic sur une case
  de la grille revient à la liste de la case.
- Grille (2026-10-08) : colonnes dans l'ordre des tracks de la doctrine,
  section rythmique (BD RM SD CP HH OH CY TM PC, boucles BR DL PL) puis
  mélodique (BS BL ST ML PD VX FX RS, `RS` = resamples maison, track 16
  joker) ; infobulle par code (rôle et track). Dans l'arbre, dossiers de code
  colorés par section et samples en retrait ; zones matrice / kits / samples
  encadrées ; un tag hérité du kit n'est pas retirable sur le fichier.
- Corbeille d'un kit ou d'un pack = règle dans `overrides.json` (clé
  `<préfixe>/`, `trash`), qui exclut tous ses fichiers, y compris à venir ;
  reconstruction du manifeste (les cases se remplissent depuis la réserve),
  restauration d'un bloc. Les décisions d'écoute des fichiers du kit sont
  perdues ; tags et étoiles restent.
- Tags de kit (ajout demandé le 2026-10-07) : même clé `<préfixe>/`, tags
  multiples hérités par tous les fichiers du kit (filtre par tag compris) ;
  ils se retirent sur le kit, pas sur un fichier.

**Décisions 7.J6 — recherche et tags inférés (arbitrées et faites le 2026-10-08)** :
- Barre de recherche en tête de l'onglet Samples, qui filtre toute la page
  (grille, pads de kits, cases, arbre, non classés, corbeille) : texte libre
  (nom DT2 et chemin), tags, kits ou packs, instruments (codes), rythmique /
  mélodique, one-shot / boucle, étoiles. ET entre facettes, OU dans une
  facette ; puces retirables, suggestions au clavier. Les non classés ne
  passent pas un filtre de case (section, code, type).
- Tags inférés des noms de dossiers par un dictionnaire curé (`TAG_GROUPS` :
  genre, instrument, mot-clé ; synonymes regroupés), pas de mots fréquents
  automatiques (trop de noms de packs). `samples.py --tag-report` liste les
  mots fréquents non couverts pour enrichir le dictionnaire.
- Statut : `auto_tags`, recalculés à chaque reconstruction, jamais écrits
  dans `overrides.json`, affichés en pointillé et cliquables (ajout au
  filtre) ; `no_auto` (fichier ou `<préfixe>/`) en masque un.

**Décisions 7.J7 — tonalité des one-shots tonals (arbitrées et faites le 2026-10-08)** :
- Constat : la note ne vient aujourd'hui que du nom de fichier (79 BD
  candidats sur 418), rien n'est mesuré dans l'audio.
- Périmètre : tous les one-shots tonals, BD, BS, ST, PD ; les boucles ML / BL
  restent exclues.
- La note mesurée entre dans le nom DT2 comme une note lue
  (`BD G# Overd 02 vtl`) ; une note lue dans le nom reste prioritaire. Les
  noms d'export changent au prochain export (rejouable, l'index retire les
  anciens).
- Filtre par tonalité : facette « note » dans la barre de recherche (OU entre
  notes, comme les autres facettes) et une roue chromatique cliquable (12
  notes, nombre de samples par note, clic = ajout / retrait du filtre).
- Mise en œuvre : fondamentale pyin (médiane des trames voisées) sur le
  corps du son, après l'attaque (50 ms pour BD, 30 ms sinon), plage par code
  (BD 30-250 Hz, BS 27-500, PD 40-1500) ; BD en pyin seul ; BS / PD : la
  note n'est retenue que si le pic spectral donne la même, sinon
  `note_src = incertaine` (Hz gardés, pas de note dans le nom). Champs `note` (dièses), `note_hz`, `note_src` (nom /
  mesure / incertaine) sur les candidats, mesurés comme les drapeaux et
  repris du manifeste précédent ; réserve non mesurée (note du nom seule,
  mesure à la promotion) ; `SampleFilter.notes`, `GET /api/samples/notes`.
- Arbitrage en session (prototype sur les 142 one-shots notés par leur nom) :
  pyin juste pour 61/79 BD, 27/45 BS, 5/6 PD, 2/12 ST (accords : la quinte
  sort). **ST n'est pas mesuré** (note du nom seule) ; règle d'accord pyin +
  pic spectral (45/56 BD justes quand ils s'accordent, contre 16/23 sinon).
  Une note mesurée est signalée « ~G# » dans le front, pas dans le nom DT2.
- BD repassés en pyin seul (arbitré le 2026-10-08, même session) : la règle
  d'accord ne notait que 111 BD sur 339 sans note dans le nom. Variantes
  testées sans gain sur les 142 notés : pic FFT seul (47/77 BD), FFT de la
  queue avec interpolation (45/77), produit spectral harmonique (41/77), note
  de fin de glissando pyin (55 à 58/76 contre 62/76 pour la médiane : en
  sautant 50 ms, la médiane mesure déjà la queue, écart médian 0,00
  demi-ton). Les kicks distordus ont des harmoniques plus fortes que la
  fondamentale et des étiquettes souvent fausses d'un demi-ton.
- Passage actuel : BD 246 mesurées / 93 incertaines (pyin sans hauteur) / 79
  lues, BS 45 / 26 / 45, PD 14 / 28 / 6, ST 12 lues sur 76. Les notes lues des boucles ML / BL
  comptent dans la roue et le filtre (rien n'y est mesuré).

**Décisions 7.J8 — arbre par type et plafond par dossier (arbitrées et faites le 2026-10-08)** :
- Constat : l'arbre famille / code éclate un même instrument dans 7 dossiers
  et impose des quotas par case famille × code. Le total retenu plafonne
  vers 1 000 (1 056 au 2026-10-08) et pèse surtout sur les kicks : 156 BD
  contre 51 ML pour piano, nappes, atmosphères et guitare réunis. Sur la
  machine, on cherche d'abord un instrument (« il me faut un kick »), pas un
  genre.
- Arbre de l'export : `<MEDIA>/Live/samples/<BRANCHE>/<CODE>/[<SOUS>/]<nom>.wav`,
  avec six branches :
  - DRUMS : one-shots percussifs, BD SD CP HH OH CY TM PC, et RM (boucles
    de rumble du sound design, mêmes sous-dossiers que BD) ;
  - TONAL : one-shots avec note (7.J7), BS ST PD ;
  - LOOPS : BR DL PL ML BL ;
  - FX : `FX/<SOUS>/` ;
  - VX : `VX/` ;
  - SAMPLE : samples et resamples maison, par code, inchangé.

  Le préfixe `<CODE>` reste dans le nom de fichier, même sous un dossier du
  même code : la liste des samples d'une track n'affiche que le nom. Le
  format du nom (`<CODE> [BPM|note] <desc> <pack>`, 18 caractères) ne change
  pas.
- La famille sort de l'arbre et des quotas. Elle devient un tag de genre
  (hardcore, jungle, dubstep, techno, tribe…), filtrable dans le front comme
  les autres tags. La règle « case de moins de 4 fichiers vers UNIVERSEL »
  disparaît.
- Quota = plafond par dossier final, de 16 à 32 selon le code ; les
  candidats restent à 3 × plafond. Le total retenu vaut nombre de dossiers
  finaux × plafond, et dépasser 1 000 passe par plus de sous-catégories, pas
  par des dossiers plus gros. Plafonds proposés : 32 pour BR, DL et PL
  (boucles rythmiques), 16 pour le reste. À ajuster à la mise en œuvre.
- Sous-catégories inférées par les tags (dictionnaire `TAG_GROUPS` enrichi),
  puis corrigées à l'écoute : `M` permet aussi de changer de sous-catégorie,
  avec un override dans `overrides.json`. Un fichier sans sous-catégorie
  inférée reste à la racine de son code, qui compte comme un dossier final.
  Une sous-catégorie de moins de 4 fichiers remonte à la racine du code.
- Sous-niveaux de départ (liste à étendre via `--tag-report`, en commençant
  par les gros codes du catalogue : PC 1 168, SD 854, ST 745, DL 588,
  VX 574) :
  - BD : HARD (distordu), CLEAN (909, propre), SUB (boom, long), ACOU ;
  - ML : KEYS (piano, orgue), PADS, ATMOS, GUITAR ;
  - FX : RISE, HIT, NOISE, REV.

  Révision de 7.J : une boucle de nappe passe en `LOOPS/ML/PADS` au lieu de
  PD ; PD ne garde que les one-shots.
- Continuité : les décisions d'écoute (keep, drop), les étoiles, les tags et
  la corbeille sont conservés par fichier. Un override de case famille × code
  devient un override de code, et la famille passe en tag. L'export reste
  rejouable : `export.json` retire l'ancienne arborescence `<FAMILLE>/` de
  `<MEDIA>/Live/samples`. Le +Drive se nettoie à part, dans Transfer.
- Arbitrages en session de code (2026-10-08) :
  - Avec les seuls BD, ML et FX en sous-niveaux, on ne retenait que 519
    fichiers. On a donc ajouté des sous-catégories inférées (règles testées
    sur le catalogue) :
    - PC : SHAKER, SKIN, METAL, WOOD, FOLEY ;
    - PL : SKIN, TOPS, SHAKER ;
    - ST : CHORD, STAB, METAL, ANALOG (minimoog, modular…), BELL (bell,
      blip, pluck), ORCH (cordes, cuivres, sax, piano) ; sans mot reconnu,
      par durée comme BS ;
    - PD : AMBIENT, CHORD, DRONE ; sans mot reconnu, par durée : SHORT
      (moins de 4 s), LONG ;
    - VX : SPEECH, CHANT, MC, CUT ;
    - BS : SUB, WOB, DIST, ANALOG par mots ; sans mot reconnu, par durée
      (lue dans l'en-tête, sans décoder) : SHORT (moins de 0,6 s), MID,
      LONG (2 s ou plus). Les noms des BS décrivent peu le son, d'où ce
      repli ; mesurer le timbre a été écarté pour l'instant (il faudrait
      mesurer toute la réserve BS) ;
    - SD : RIM ;
    - BR et DL par tranche de tempo, nommée par sa borne basse pour le tri
      de la DT2 (`060` moins de 120, `120`, `150`, `180`) : tempo du nom,
      sinon tempo mesuré. Un tempo mesuré à un passage range la boucle au
      passage suivant.

    - Les `Low End Thumps` et `Transitions` de cinematic Noiiz (39
      fichiers) étaient classés en PD à cause du mot « cinematic ». Ils
      passent en FX (`FX/HIT` et `FX/RISE`).

    Résultat : 1 215 retenus sur 3 191 candidats, 74 dossiers.
  - Plafond : 32 pour BR, DL et PL, 16 pour le reste. Plafond propre à un
    dossier dans `FOLDER_CAPS` (prioritaire) : `LOOPS/BR/060` à 64
    (2026-10-10, breaks lents nombreux).
  - Front : arbre par branche (repliable), une ligne par code, une case
    par sous-catégorie ; les dossiers vides restent visibles comme cibles
    de dépôt. L'arbre d'un kit suit le même ordre. `M` choisit un dossier.
    (Révisé par 7.K : treeview, et dossiers masqués sous filtre.)
  - Aucun projet DT2 n'existe encore : le déplacement sur le +Drive est
    sans effet.

**Décisions 7.K — coquille du front (arbitrées et faites le 2026-10-09)** :
- Barre générale : télécommande du deck en focus (Morceau / Sample,
  commutable) ; le focus suit la vue Morceaux ou Samples, et reste sur la
  dernière en Knowledge. Une seule source joue à la fois (`remote.svelte.ts`).
  Morceaux : précédent / suivant dans l'ordre de la liste filtrée, la lecture
  continue si elle était en cours ; boucle = région calée si elle existe,
  sinon morceau entier. Samples : sample précédent / suivant de la liste,
  boucle du sample.
- Panneau latéral : icônes + libellés, réductible aux icônes (mémorisé).
  Second clic sur Morceaux : replie / déplie la liste. Les vues visitées
  restent montées (masquées) : la lecture continue en lisant une fiche ; le
  clavier d'une vue masquée est ignoré.
- Knowledge : vue pleine page (sommaire, recherche, fiche, manuel) ; `/` y
  mène. L'overlay reste pour l'aide contextuelle de la façade DT2.
- Filtre des morceaux : tags = genre + energy + mood (sans le « ? »
  d'inférence) + colonne `tags` de `library.md` ; plusieurs tags en ET.
  Tri Date (champ `added`, plus récents d'abord) ou A→Z, BPM / Key / Energy
  en second choix. API : `added` et `tags` exposés par `GET /api/tracks`.
- Ajout (7.I) fusionné dans le filtre : dernière proposition « Chercher
  « … » en ligne » (et bouton si aucun résultat), recherche lancée dans un
  panneau sous la liste, plus de bouton dans la barre.
- Historique des filtres dans les propositions (morceaux et samples) : 8
  entrées, sans doublon, un filtre qui affine le précédent le remplace.
  Retenu à la sélection d'un morceau, à l'ajout d'un tag, à Entrée.
- Arbre des samples en treeview : une ligne par dossier (code avec sa
  racine, sous-dossiers en retrait dessous), compteurs alignés à droite ;
  colonne bornée à 280-440 px, pads de kits sur trois colonnes. Sous un
  filtre (recherche ou kit), seuls les dossiers qui y répondent sont
  affichés ; `M` cible toujours tous les dossiers. Hors filtre, les
  dossiers vides restent visibles comme cibles de dépôt.
- Recherche des samples : Tab complète avec la proposition surlignée, sinon
  la première facette ; Espace valide une facette dont le nom est
  exactement saisi (« BD » puis Espace = puce instrument BD).
- Totaux dans l'arbre : chaque dossier affiche `à écouter / retenus (total)`,
  total = candidats + hors plafond ; la ligne d'un code à sous-dossiers
  ajoute le total du type à droite.
- Vue par type (gardée après essai) : un filtre d'instrument (puce code, ex. BS) ouvre à
  droite l'arborescence de tous les fichiers du type par sous-dossier
  (`GET /api/samples/tree`). Choisir un kit ne filtre que cette vue (seuls
  les sous-dossiers qui ont des fichiers du kit y restent) ; l'arbre de
  gauche n'est pas réduit au kit. Un clic à gauche déplie et
  montre le dossier à droite. Retirer le filtre d'instrument revient à la
  vue par case.
- Barre de recherche des samples sous le titre « Library » de l'arbre :
  texte, tags, kits, instruments seulement (révise 7.J6 / 7.J7 : filtres
  rythmique / mélodique, one-shot / boucle et étoiles retirés, notes hors
  de la barre). La roue des notes passe dans l'en-tête de la vue de droite
  et ne filtre que cette vue, pas l'arbre (mémorisée à part). Elle est
  alignée à droite de la forme d'onde. Ses comptes suivent la barre et le
  kit (`/api/samples/notes?…&kit=`) ; une note absente du sous-ensemble
  est blanche, sans compteur ni clic (sauf pour retirer une note déjà
  choisie).
- Filtre de tempo de la vue de droite, même principe que la roue : tranches
  `BPM_BANDS` (<90, 90-109, 110-129, 130-144, 145-159, 160-174, 175-189,
  190+), tempo écrit dans le chemin sinon mesuré (boucles) ; comptes sous
  la barre et le kit (`/api/samples/bpms`), tranches vides blanches, OU
  entre tranches ; bloc masqué si aucun fichier du sous-ensemble n'a de
  tempo. Un fichier sans tempo sort de la liste dès qu'une tranche est
  choisie.
- Un clic sur un code de l'arbre (BD, BS…) ajoute ou retire le filtre
  d'instrument correspondant (code surligné quand il est actif).
- Sous-dossier manuel (version simple, sans mot-clé) : « + » sur la ligne
  d'un code dans l'arbre, nom de 2 à 10 lettres ou chiffres (majuscules).
  Source unique `library/samples/folders.json` (`{"BD": ["RUMBLE"]}`),
  fusionnée dans `SUBS` au chargement (API, `samples.py`) ;
  `POST /api/samples/folders` rejouable. Le dossier ne se remplit que par
  rangement (`M`, glisser → override `sub`), conservé aux reconstructions ;
  plafond de 16 (32 pour BR / DL / PL), créé sur le +Drive au prochain
  export. Pas de SAMPLE. Sous un filtre d'instrument, les sous-dossiers
  vides du type restent affichés (cibles de dépôt).
- Réanalyse depuis le front : bouton « Réanalyser » de la zone Library,
  même reconstruction que `samples.py` (classement, mesures des nouveaux
  candidats, sélection ; décisions et mesures conservées) dans un thread de
  l'API, suivi par `GET /api/samples/rebuild`. Pendant le calcul, toute
  écriture sur les samples répond 409 (le manifeste reconstruit écraserait
  les décisions prises entre-temps). Bilan affiché à la fin.

**Constat à traiter** : la dérive de grille de beats du sidecar (tempo constant
légèrement faux) touche aussi `groove.py` et `rhythm_signature.py`, qui replient
sur `beat_times_s`. Le recalage `retrack_beats` de `analyzer/digitakt.py` est
réutilisable pour eux.

---

## Phase 8 — Sound design (livrée le 2026-10-10)

**But** : fabriquer de nouveaux samples à partir de ceux de la library par
des **traitements** paramétrables (premier : le **rumble**), chacun étant un
graphe de **chaînes de plugins** (pedalboard + devices maison numpy). Chaque
traitement a son **notebook** dans le front : théorie musicale, exemples
d'usage, rôle de chaque paramètre, ressources web, et des devices visuels
façon Ableton Live qui font le traitement.

Exemple concret, le rumble : un kick one-shot est séquencé au tempo
(four on the floor), passe dans deux chaînes parallèles, « Kick » (sec) et
« Rumble » (reverb 100 % wet → passe-bas → distorsion → passe-bas →
passe-haut → duck sur les coups → mono), puis dans le master (limiteur).
On garde une boucle d'une à huit mesures, sans couture.

| Sous-phase | Contenu | Statut |
|---|---|---|
| 8.A | Moteur `analyzer/sounddesign.py` (modèles Pydantic, catalogue de 15 devices, traitement rumble, rendu en boucle sans couture), presets JSON du vault, CLI `sounddesign.py`, tests | fait (presets à valider à l'oreille) |
| 8.B | API `/api/sounddesign/...` : traitements, catalogue des devices, presets (lecture, sauvegarde `PUT`), écoute à la volée (WAV en mémoire, synchrone : 0,2 s au pire pour 8 mesures à 60 BPM), écriture d'un rendu, liste et écoute des rendus | fait |
| 8.C | Vue front « Sound design » façon Ableton Live : potards (glisser vertical, Maj fin, double-clic défaut), tranches de mixage = chaînes (fader, activateur = mute, solo d'écoute), devices avec activateur = bypass, courbe de réponse à nœud pour filtres / EQ, ajout / retrait / déplacement de devices et de chaînes, presets enregistrer / enregistrer sous, source du manifeste + écoute A/B, boucle Web Audio re-rendue à chaud, rendus | fait (à valider à l'usage) |
| 8.D | Notebook rumble [[sounddesign/rumble]] (théorie, chaîne device par device, presets, usage DT2, pièges, ressources) affiché dans la vue (`GET /api/sounddesign/notebook/{t}`, « ? » d'un device = sa section) ; versement d'un rendu dans le pack `Samples/SoundDesign/` puis réanalyse : rangé en `LOOPS/BL`, révisé en 8.E (`POST /api/sounddesign/verse`, `--verse` en CLI) | fait (versement à valider sur le disque) |
| 8.E | Source = sample en cours de la vue Samples (on la change là-bas) ; nom DT2 proposé à partir de celui de la source (code du traitement + tempo, modifiable) ; code **RM** (track 2) : un rumble versé est rangé par override en `DRUMS/RM/<sous-dossier de la source>` (`GET /api/sounddesign/target`) | fait (versement à valider sur le disque) |
| 8.F | Mode **Un coup** du rumble (un kick et sa queue, longueur en temps au tempo, 1 par défaut, fondu de 20 ms : la track DT2 étant monophonique, le kick suivant coupe la queue) ; duck **anticipé** : la boucle commence et finit dans le creux, plus de clic quand on la joue une fois | fait (à valider à l'oreille) |
| 8.G | Traitement **riser** (track 15, `FX/RISE`) : source bruit blanc / rose généré ou sample en cours bouclé, montée de hauteur (varispeed), courbe, arrêt net ; **automation** générique `params_end` des devices pedalboard (rendu par blocs) ; 3 presets ; API et CLI sans source pour le bruit | fait (à valider à l'oreille) |
| 8.H | Front : colonne latérale des traitements dépliables sur leurs presets, mini barre d'outils (nouveau preset vierge, nom / description, suppression `DELETE /api/sounddesign/presets/{t}/{id}`, pas le dernier) ; source « bruit généré » sans sample ; bouton ↗ d'automation (potard « fin ») ; notebook [[sounddesign/riser]] ; dossier de rangement des rendus (`folder`) | fait (à valider à l'usage) |
| 8.I | Traitement **variations** : un one-shot rendu N fois (4 / 8 / 16 / 32, grille GRID de la DT2) en tranches égales dans un seul fichier, paramètres étagés de la tranche 1 (sobre) à N (marquée) par `params_end` + aléa reproductible, niveau égalisé (RMS des 150 premières ms) ; rangé avec la source (`BD V8 …`, même code et dossier), tag `slices` (pas de contrôle « long ») ; presets `drive_tints`, `rumble_tints` ; notebook [[sounddesign/variations]] | fait (à valider à l'oreille) |
| 8.J | Layering : source par chaîne (deuxième sample), calage des attaques en ms, mélange variable d'une tranche à l'autre | à venir |

**Décisions 8** (arbitrées le 2026-10-10) :
- **Mute à deux niveaux** : `bypass` par device (bouton on/off d'un device
  Ableton) **et** `mute` + `gain_db` par chaîne parallèle.
- **Notebook = vue du front Svelte** (panneau latéral « Sound design »), pas
  de Jupyter : le texte vit en markdown dans le vault, les devices
  appellent l'API.
- **Presets** : JSON versionnés dans `library/sounddesign/presets/<traitement>/<id>.json`,
  validés contre le catalogue (device, paramètre, bornes) ; un paramètre
  absent prend sa valeur par défaut. Le catalogue (`DEVICES`, `TREATMENTS`)
  est la source des bornes, unités et aides affichées par le front.
- **Sorties** : `<MEDIA>/SoundDesign/<traitement>/<nom DT2> <hash>.wav` (8.E)
  (48 kHz, fréquence native de la DT2, 24 bits) + sidecar `.json` (source,
  snapshot du preset effectif). Le hash porte sur le preset effectif : même
  nom et mêmes réglages = même fichier (rejouable). **Hors de
  `<MEDIA>/Samples/`**, qui reste la copie en lecture seule des packs.
- **Boucle sans couture** : coups placés à l'identique dans chaque boucle
  (pas d'arrondi cumulé), pré-roll d'au moins 4 s pour que les queues de
  reverb soient en régime, seule la dernière boucle est gardée.
- **Sources** (8.B) : l'API ne rend que des samples du manifeste (clé
  relative à `<MEDIA>/Samples`), comme l'écoute des samples : pas de chemin
  libre. Les rendus ne sont servis que s'ils ont un sidecar.
- **Filtres** (8.C) : résonance et type (LP / HP / BP, 12 / 24 dB/oct) via
  le device `filter` (LadderFilter pedalboard) ; `highpass` / `lowpass`
  restent des 1er ordre sans résonance. Un paramètre discret porte
  `choices` (sélecteur dans le front, index validé côté moteur).
- **Versement** (8.D, arbitré le 2026-10-10) : un rendu versé est copié dans
  le pack `<MEDIA>/Samples/SoundDesign/<traitement>/`, **seule exception** à
  la lecture seule de `Samples/`, puis suit le circuit des samples
  (réanalyse, écoute garder / écarter, export Transfer). Rangement révisé
  en 8.E : le versement écrit un override (code du traitement, sous-dossier,
  nom DT2) dans `overrides.json`, le nom du fichier ne range plus rien.
- **Rangement du rumble** (8.E, arbitré le 2026-10-10) : code **RM** en
  DRUMS, juste après BD, comme la track 2 de la doctrine
  ([[digitakt/doctrine]] § 1 et 9) ; il hérite du sous-dossier du kick
  source s'il existe pour RM (HARD, SUB, ACOU, CLEAN) : un kick de
  `DRUMS/BD/CLEAN` donne `DRUMS/RM/CLEAN`. Tempo et note gardés dans le
  nom ; pas de contrôle « blanc » ni « long » (c'est une boucle, creusée au
  premier coup). Le rangement 8.D en `LOOPS/BL` contredisait la doctrine.
- **Source et nom** (8.E) : la source est le sample en cours de la vue
  Samples (une seule sélection pour toute l'application). Nom DT2 proposé :
  celui de la source, code remplacé par celui du traitement, tempo ajouté
  (`BD C Punch 01 dbr` → `RM 150 C Punch dbr` : le numéro de variante part
  d'abord, puis la description est tronquée), rendu unique dans le dossier
  cible ; modifiable avant le rendu.
- **Notebooks** : un par traitement, markdown du vault (`sounddesign/<t>.md`,
  champ `notebook` du traitement) ; les titres de section reprennent les
  noms des devices pour le lien « ? ».
- **Sidechain** : pedalboard n'a pas d'entrée sidechain ; le device `duck`
  creuse le signal sur les positions de coups connues du traitement.
- **Riser** (8.G, arbitré le 2026-10-10) : source au choix, bruit généré
  (blanc ou rose, graine fixe : même preset = même fichier) ou sample en
  cours bouclé ; code **FX**, sous-dossier fixe **RISE** (track 15,
  [[digitakt/doctrine]] § 5) ; arrêt net à la fin de la dernière mesure
  (fondu de 5 ms), pas de queue de reverb : le contraste montée / silence
  fait l'effet. Sans source, nom `FX <BPM> Rise Noise`.
- **Automation** (8.G, arbitré le 2026-10-10) : valeur de **fin** par
  paramètre (`params_end` du device), interpolée depuis `params` selon la
  courbe du traitement (linéaire sur la boucle gardée pour le rumble),
  géométriquement pour un potard log. Devices pedalboard seulement, rendus
  par blocs de 256 échantillons avec état conservé (identique au rendu d'un
  seul tenant sans automation). Omis du JSON quand vide : le hash des
  rendus antérieurs ne change pas. Sert aussi au downlifter (fin < début).
- **Colonne latérale** (8.H, arbitré le 2026-10-10) : la mini barre
  d'outils nouveau / modifier / supprimer agit sur les **presets** ; les
  traitements restent définis dans le moteur (pas de création depuis le
  front). Le dernier preset d'un traitement ne se supprime pas.
- **Variations** (8.I, arbitré le 2026-10-11) : répartition **progressive +
  aléa** (tranche 1 la plus sobre, N la plus marquée, aléa d'au plus un pas,
  graine fixe) ; le hasard du jeu se fait sur la DT2 (CREATE RANDOM LOCKS
  sur `SLICE`). Niveau **égalisé** : la variation porte sur la couleur, pas
  le volume. Un seul fichier en tranches de même longueur (machine GRID).
  Le rendu garde le code et le sous-dossier de la source ; `params_end` y
  désigne la valeur de la dernière tranche (`automation: "slices"` du
  traitement). Le **layering** de plusieurs samples est reporté en 8.J.

## Décisions arbitrées (à NE PAS refaire)

- **Phase 3 (export DJ XML Rekordbox/Traktor)** : skipée intentionnellement.
  Révisé le 2026-10-07 : **Rekordbox** est le logiciel de mix (disque branché
  au Mac, pas de clé CDJ). La library ne contient donc que des formats lus par
  Rekordbox (FLAC/M4A/MP3) et les playlists passent par des `.m3u` en chemins
  absolus vers le disque. L'export XML (cues, beatgrid) reste hors scope.
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
