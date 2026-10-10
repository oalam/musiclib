# Changelog

Toutes les évolutions notables du vault et des outils `scripts/`.
Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Les slices
renvoient aux phases de [[SPEC]]. Pas de `pyproject.toml` : la version vit ici.

## [Non publié]

### Corrigé

- [7.K] Vue Samples : la colonne de l'arbre est bornée (280 à 440 px) au
  lieu de prendre la largeur de son contenu ; les sous-dossiers d'un code
  passent à la ligne, alignés après le code. Le bloc de lecture et de
  sélection récupère la largeur restante.
- [7.K] Arbre des samples en treeview (un dossier par ligne, compteurs à
  droite), pads de kits sur trois colonnes ; sous un filtre, seuls les
  dossiers qui y répondent sont affichés. Recherche : complétion par Tab
  et par Espace sur un nom exact de facette.
- [7.K] Liste des samples : les retenus ressortent (gras, fond plein) ; la
  réserve passe en retrait (plus petite, atténuée), le hors plafond plus
  encore (italique) ; séparateur « Réserve » marqué.
- [7.K] Arbre des samples titré « Library » (bilan en infobulle) ; panneau
  de tagging du kit ouvert au double-clic sur un pad seulement, fermable.

### Modifié

- [7.J8] Arbre du +Drive par type : une case est un dossier final
  `<BRANCHE>/<CODE>/[<SOUS>]` (DRUMS, TONAL, LOOPS, FX, VX, SAMPLE), au lieu
  de la case famille × code. Plafond par dossier (32 pour BR / DL / PL, 16
  ailleurs, SAMPLE sans plafond) ; sous-catégories inférées des mots du
  chemin (`SUB_RULES` : BD HARD / CLEAN / SUB / ACOU, PC SHAKER / SKIN /
  METAL / WOOD / FOLEY, ML KEYS / PADS / ATMOS / GUITAR, FX RISE / REV /
  HIT / NOISE, BS SUB / WOB / DIST / ANALOG, ST CHORD / STAB / METAL /
  ANALOG / BELL / ORCH, PD AMBIENT / CHORD / DRONE, VX, PL, SD), à défaut
  de la durée pour BS, ST (SHORT / MID / LONG) et PD (SHORT / LONG), ou de la tranche de tempo pour
  BR / DL (`060`, `120`, `150`, `180`), forcées par l'override `sub`. La famille ne
  range plus : elle repère SAMPLE et devient un tag de genre. Une boucle de
  nappe passe en `LOOPS/ML/PADS` ; les thumps et transitions de
  cinematic Noiiz passent de PD à FX. 1 215 retenus au lieu de 1 056, avec
  plus de dossiers et moins de kicks par dossier.
  API : `SampleCell` porte `folder` / `branch` / `code` / `sub`,
  `/api/samples/cell?folder=`, `move {code, sub}`, `GET /api/samples/folders`.
  Front : arbre des branches (une ligne par code, une case par
  sous-catégorie, dossiers vides comme cibles de dépôt), arbre du kit par
  branche, `M` vers un dossier. L'export réécrit l'arborescence au prochain
  passage (l'index retire l'ancienne).

### Ajouté

- [7.K] Vue par type des samples (essai) : un filtre d'instrument liste à
  droite tous les fichiers du type par sous-dossier ; un kit ne filtre que
  cette vue (sans ses sous-dossiers vides), l'arbre de gauche reste intact.
  API : `GET /api/samples/tree` (`kit_rows` accepte l'absence de kit).
  Arbre : total par dossier et par type (candidats + hors plafond).
- [7.K] Coquille du front : barre générale avec télécommande (Morceau ou
  Sample : précédent, lecture / pause, boucle, suivant ; une seule source
  joue à la fois) et panneau latéral minimisable à icônes (Morceaux,
  Samples, Knowledge en pleine page, `/` y mène). Les vues visitées restent
  montées. Morceaux : tags multiples en puces (genre, energy, mood, tags ;
  ET), tri Date / A→Z, historique des filtres et « Chercher en ligne » dans
  les propositions, ajout dans un panneau sous la liste. Samples : historique
  des filtres dans les propositions. API : `added` et `tags` dans
  `TrackSummary`.
- [7.E] Sortie audio du lecteur au choix (`setSinkId`) : le morceau part
  vers la Digitakt II (USB AUDIO/MIDI) pour l'échantillonner en `SRC` = USB.
  Sélecteur dans le transport, mémorisé par libellé, réappliqué au
  changement de morceau ou de périphérique ; bouton « Sorties audio… » quand
  Chrome masque les libellés (autorisation micro, flux coupé aussitôt).
- [7.J7] Tonalité des one-shots tonals : note mesurée dans l'audio pour BD,
  BS et PD (`measure_note` : fondamentale pyin après l'attaque ; BD en pyin
  seul, BS / PD retenues si le pic spectral s'accorde, sinon « incertaine »),
  écrite dans le nom DT2
  (`BD G# Overd 02 vtl`) ; la note lue dans le nom reste prioritaire, ST
  n'est pas mesuré. Champs `note`, `note_hz`, `note_src` au manifeste,
  repris d'une reconstruction à l'autre. Barre de recherche : facette note
  (puce, saisie `g#` ou `ab`) et roue chromatique cliquable avec le nombre
  de samples par note ; badge « ~G# » sur une note mesurée. API :
  paramètre `notes`, `GET /api/samples/notes`. Les noms d'export changent au
  prochain export.

- [7.J6] Barre de recherche de l'onglet Samples, qui filtre toute la page :
  texte, tags, kits / packs, instruments, rythmique / mélodique, one-shot /
  boucle, étoiles (ET entre facettes, OU dedans), avec suggestions et puces.
  API : filtre commun (`SampleFilter`) sur `/api/samples`, `/cell`, `/loose`,
  `/kits`, `/kit/tree`, et `GET /api/samples/facets`. Remplace les anciens
  filtres tag / étoiles.
- [7.J6] Tags inférés des noms de dossiers (`auto_tags`, dictionnaire curé
  genre / instrument / mot-clé), recalculés à chaque reconstruction, masquables
  par `no_auto` ; `samples.py --tag-report` liste les mots non couverts.

- [7.J5] Vue par kit de la bibliothèque de samples : un kit est un préfixe
  de chemin (pack puis sous-dossier, `rthm/packs/neurotek`). Pads sous la
  grille (packs, puis sous-kits du pack choisi) qui filtrent grille, cases,
  non classés et corbeille. Le manifeste liste la réserve hors plafond
  (`reserve`, environ 8 000 fichiers, manifeste de 0,9 à 2,3 Mo) : un
  fichier de la réserve devient candidat dès qu'on le garde, l'écarte, le
  note ou le range. Tags de kit hérités par ses fichiers et corbeille d'un
  kit entier (règle `"<préfixe>/"` dans `overrides.json`, restaurable d'un
  bloc). API : `GET /api/samples/kits`, paramètre `kit`,
  `POST /api/samples/kit/tags`, `/kit/trash`, `/kit/restore`.
- [7.J5] Arborescence du kit : choisir un kit ouvre à droite ses fichiers
  par classement final FAMILLE / CODE (dossiers repliables, retenus / total,
  marques retenu / réserve / hors plafond), puis un dossier « Non classés » ;
  écoute et actions actives (`GET /api/samples/kit/tree`).
- [7.J5] Hors plafond sans kit : un second appui sur `R` (ou le bouton
  « Afficher les hors plafond ») ajoute toute la réserve de la case
  (`GET /api/samples/cell?overflow=true`) ; le nombre de fichiers hors plafond
  s'affiche dans l'en-tête de la case.

- [7.J3] Export des samples retenus vers `<MEDIA>/Live/samples/<FAMILLE>/
  <CODE>/<nom>.wav` (copie telle quelle, Transfer convertit) :
  `samples.py --export [--dry-run]`, `POST /api/samples/export` et bouton
  « Exporter… » de l'onglet Samples (bilan puis copie confirmée). Rejouable
  via l'index `library/samples/export.json` : seuls les fichiers écrits par
  l'export sont recopiés ou retirés, jamais un fichier posé à la main ; une
  copie interrompue est reprise. Premier bilan : 1 053 fichiers, 468 Mo.
- [7.J4] Bibliothèque de samples : tags libres (normalisés, autocomplétion),
  étoiles 1 à 5 (un sample noté passe devant les non-notés de sa case et
  reste candidat hors plafond ; noter ne vaut pas garder) et corbeille,
  statut distinct de `drop` (sorti de toutes les cases et des
  reclassements, restaurable, jamais supprimé du disque). Stockés dans
  `overrides.json` (`tags`, `stars`, `trash`), recopiés dans le manifeste
  (`tags`, `stars` des candidats, liste `trashed`). Les 407 non classés
  reçoivent une case depuis le front et deviennent candidats.
- [7.J4] API : `GET /api/samples/loose` (non classés, corbeille),
  `GET /api/samples/tags`, `POST /api/samples/stars`, `/tags`, `/trash`,
  `/restore` ; filtres `tag` et `min_stars` sur la grille ; l'audio est
  servi aussi pour les non classés et la corbeille.
- [7.J4] Front (onglet Samples) : filtres tag / étoiles, zones Non classés
  et Corbeille, sélection multiple (`⌘`-clic, `Maj`-clic, `⌘A`), barre
  d'outils (garder, écarter, case, corbeille / restaurer, étoiles, tag),
  glisser-déposer d'une ligne ou de la sélection vers une case de la
  grille (vide comprise) ou la corbeille ; raccourcis `1`…`5`, `0`, `T`,
  `Suppr`.
- [7.J2] Pré-filtre qualité des samples DT2 : chaque candidat du manifeste
  est mesuré (`analyzer/samples.measure`) et reçoit des drapeaux `muet`
  (crête < -40 dBFS), `faible` (< -18 dBFS), `sature` (plus de 0,1 % des
  échantillons en plateaux d'au moins 3 valeurs à pleine échelle), `blanc`
  (plus de 30 ms de silence en tête d'un one-shot), `long` (frappe de drums
  de plus de 2 s), `illisible`. Les candidats signalés passent en fin de
  case (tri stable, le tour de rôle entre sous-packs est gardé) sans être
  écartés : la décision reste à l'oreille. Mesures reprises du manifeste
  précédent, option `--no-measure`. Premier passage : 197 drapeaux sur
  2 423 candidats (sature 87, long 67, blanc 33, faible 10).
- [7.J2] Front : onglet **Samples** (`web/src/lib/SampleView.svelte`),
  vue mémorisée. Grille famille × code (à écouter / retenus, boucles BR DL
  PL ML BL en dernières colonnes), case avec la
  sélection puis la réserve, drapeaux du pré-filtre, forme d'onde et lecture
  automatique. Raccourcis `K` garder, `D` écarter, `U` annuler, flèches
  pour le sample et la case, `Espace` rejouer, `R` réserve.
- [7.J2] Tempo des boucles : lu dans le nom quel que soit le séparateur
  (`120 Sklep Break`, `02_…_Fill_175_…` : premier nombre plausible, plus
  seulement le premier nombre) ; sinon mesuré (`estimate_bpm` : tempo
  librosa calé sur 1 à 16 mesures 4/4 quand la durée le confirme, à ×2 / ÷2
  près, zone 80-200 préférée ; librosa seul sinon, marqué `bpm_est` et
  affiché « ~N bpm » dans le front). Champs `bpm` / `bpm_est` du manifeste,
  repris d'un passage à l'autre. Retenues sans BPM : 124 → 6 sur 301
  (62 estimées).
- [7.J2] Classement : dans un dossier one-shot, une frappe de plus de 4 s ou
  un tempo dans le nom ne font plus une boucle (crash de 4,4 s → CY) ; un
  « loop », « fill » ou « break » de moins d'une seconde reprend le code de
  frappe de son nom (`BreakApartKick` neurotek → BD).
- [7.J2] Pack `rthm/packs/neurotek` (360 one-shots) basculé de JUNGLE en
  TRIBE : TRIBE passe à 96 retenus (BD 32, SD 16, HH 16, CY 16, PC 16) ;
  JUNGLE perd l'essentiel de ses kicks (BD 10/10). Ses cases de moins de
  4 fichiers (BR, CP, DL) sont repliées dans UNIVERSEL.
- [7.J2] Plus de boucles : un tempo dans le nom sans « bpm » (`170_…`,
  `CPCT_120_…`, `drm120`) sur 2 s ou plus, hors dossier one-shot, fait une
  boucle (`instru/piano`, `instru/synth` passent de ST à ML) ; tempo repris
  en tête du nom DT2, références de label à 3 chiffres (406, 516) ignorées
  comme numéro. Doublons exacts entre packs (même nom, même taille) écartés
  en gardant la copie classée puis la plus profonde (`jungle dnb rthm/` est
  une copie de `rthm/loops/jungle dnb/`). Quotas ML et BL de 8 à 16, PL à 32
  en JUNGLE et TRIBE. Boucles retenues : 260 → 300 (DL 122 + PL 66 + ML 51
  + BR 40 + BL 21) sur 996 ; non classés 496 → 407.
- [7.J2] Changement de case à l'écoute : touche `M` ou bouton « case… »
  d'une ligne, choix famille × code (`POST /api/samples/move`). Statut
  gardé, rang en fin de la nouvelle case (un pending y tombe en réserve si
  elle est pleine), nom refait avec le nouveau code, drapeaux remesurés.
  Le déplacement est écrit dans `overrides.json` et un fichier déplacé reste
  candidat à la reconstruction même hors du plafond. Toutes les familles
  sont affichées dans la grille, même vides (TRIBE).
- [7.J2] API d'écoute des samples : `GET /api/samples` (cases famille × code
  avec compteurs), `GET /api/samples/cell`, `POST /api/samples/status`
  (`keep` / `drop` / `pending`, sélection de la case recalculée : un drop
  fait monter le candidat suivant, écriture atomique du manifeste),
  `GET /api/samples/audio` (fichier servi seulement s'il figure au
  manifeste).
- [7.J1] Bibliothèque de samples DT2 : `scripts/samples.py` (logique dans
  `analyzer/samples.py`) classe les packs de `<MEDIA>/Samples` en famille
  (HARDCORE, JUNGLE, DUBSTEP, TECHNO, TRIBE, AUTRES, UNIVERSEL, SAMPLE) et code
  à 2 lettres façon Elektron (boucles découpées en BR break, DL drums, PL
  percussions, ML mélodie, BL basse), nomme chaque candidat pour l'écran de
  la DT2 (`<CODE> [BPM|note] <desc> <pack>`, 18 caractères), applique quotas
  et repli des petites cases dans UNIVERSEL, écarte les doublons mono.
  Manifeste rejouable `library/samples/manifest.json` (956 retenus sur 2 423
  candidats, 11 295 fichiers), overrides manuels
  `library/samples/overrides.json`.
  Chemins `SAMPLES_SRC_DIR`, `SAMPLES_META_DIR`, `DT2_SAMPLES_DIR`
  (`<MEDIA>/Live/samples`) dans `paths.py`.
- [7.E] Envoi à la DT2 : réglage d'octave (-5 à +5) dans le panneau
  « Envoyer à la DT2 », mémorisé par track, avec la plage de notes résultante
  (notation Elektron) ; champ `octave` de `POST /api/dt2/send`, option
  `--octave` de `dt2_midi.py`. Une basse envoyée à sa hauteur réelle
  (E1 = 28) sonnait 32 demi-tons sous le sample (60 = hauteur d'origine).
- [7.C] Front : état retrouvé au rechargement (navigateur) : dernier
  morceau ouvert, et par morceau le pattern, la track DT2, le mode et la page
  de paramètres de la façade, la page de pas, la position de lecture (sans
  relancer la lecture ; FOLLOW reprend la main en lecture).
- [7.E] Envoi d'une track de pattern à la Digitakt II depuis le front :
  `scripts/dt2_midi.py` (CLI + `Dt2Sender`) rejoue les trigs de la track sur
  l'AUTO CHANNEL, calés sur l'horloge de la DT2 à partir de son Start (un
  passage, Stop = annulation, délai de 120 s sans Start) ; routes
  `GET /api/dt2/ports`, `POST|GET|DELETE /api/dt2/send` (un envoi à la fois) ;
  panneau « Envoyer à la DT2 » dans la vue bank (port, AUTO CHANNEL, pas à
  pas côté machine, progression). Dépendance `python-rtmidi`. Notes du `.mid`
  de bank factorisées dans `track_note_events` (`analyzer/digitakt.py`).
- KB Digitakt, veille live (lot 2, DT2 + Mac) : fiches `kick-mental-vst`
  (kickbass fabriqué en VST, nommé avec sa note, Transfer ou `SRC` = USB),
  `overbridge-live-vst` (multipiste, VST sur les tracks hautes, latence),
  `midi-vst` (ligne acid et accords sur synthés VST par USB) ; lives tekno
  de la veille ajoutés à `inspirations/sets.md`.
- KB Digitakt, veille live (lot 1, Digitakt seule) : note de curation
  `digitakt/veille-live.md` (recherche web, périmètre DT2 + Mac via
  Overbridge) ; fiches `live-looping` (resampling du main en jeu),
  `rumble-grave` (gestes machine du §9), `polymetrie` (recettes avec cycles
  ppcm), `slice-breaks` (SLICE / GRID, ouvertures DnB) ;
  `patterns-chaines` (patterns pont, bank 4 × 4) et `fill-conditions`
  (Control All sur `PROB`, lock trigs en réserve) complétées ; vidéos de la
  veille ajoutées (non visionnées).
- [7.I] Correction du BPM par le style : le BPM détecté est ramené (×2 / ÷2)
  dans la plage du style (`STYLE_BPM_WINDOWS`, `analyzer/infer.py` :
  reggae / dub 60-95, shatta / dancehall 85-115, tribe / tekno / acidcore
  160-210…). Style lu dans le dossier, le genre forcé, le genre de la source
  puis ses tags (pas le titre ; soul et roots hors table, trop ambigus) ; BPM corrigé imposé à l'analyse complète, style
  reporté dans `genre` s'il est vide. Champ « Dossier / style » du front.
- [7.I] Ajout d'un morceau depuis le front : panneau « + Ajouter un
  morceau » (recherche YT/SC, candidats avec codec / débit / qualité /
  pertinence, meilleur présélectionné, lien pour écouter la source), options
  stems Demucs et bank Digitakt + harmonie, dossier facultatif ; suivi des
  étapes par polling, puis liste rechargée et morceau ouvert.
- [7.I] API : `POST /api/grab/search` (synchrone), `POST /api/grab` (job,
  503 sans disque média, 422 si URL invalide, Spotify, dossier hors library
  ou bank sans analyse), `GET /api/jobs/{id}`. `scripts/jobs.py` : file à un
  seul worker (jobs sérialisés, écritures de library.md sans concurrence),
  étapes `queued` / `running` / `done` / `error` / `skipped`.
- [7.I] `grab.py` découpé : `search()` (candidats triés), `CandidateInfo`
  (Pydantic), `track_meta()`, `ingest(url | Candidate, IngestOptions,
  on_step)` et `GrabError` ; `grab_one` (CLI) les réutilise, comportement
  inchangé.
- [7.I] Échec de téléchargement lisible : la ligne `ERROR` de yt-dlp est
  remontée (`GrabError`) au lieu de la commande, avec la piste
  `brew upgrade yt-dlp` sur un 403.

- [media] Média déplacé sur le SSD externe `xtreme`, dédié au son :
  `Mix/{audio,stems,visuals}` pour le mix (Rekordbox), `Live/{renoise,grooves,
  digitakt}` pour le live ; métadonnées (`library.md`, sidecars, banks, cache
  artistes) inchangées dans le vault. Hub `scripts/paths.py`
  (`MUSIC_MEDIA_ROOT`, marqueur `.music-media`, `MediaRootUnavailable`) importé
  par tous les scripts ; les commandes media sortent en code 2 sans le disque.
- [media] `scripts/migrate_media.py` (one-shot, rejouable, `--dry-run`,
  `--cleanup`) : rsync, transcodage opus→FLAC, réécriture `library.md`,
  `file_path` des sidecars et `.m3u`, symlinks Obsidian `library/audio` et
  `library/visuals`.

- [7.F] Fiches KB : section **Vidéos** (tutos YouTube horodatés au chapitre :
  XNB, True Cuckoo, Synthackers…) sur les 25 fiches (lots 1 à 5) ;
  liens externes du panneau KB ouverts dans un nouvel onglet.
- [7.H] Vue d'ensemble : ligne **Accords** en tête de grille, un accord par
  mesure du pattern (passage en cours, sinon le premier), mesure jouée
  encadrée, opacité = confiance.
- [7.H] Vue d'ensemble : nom de la note sur les tracks mélodiques quand elle
  change ou en début de mesure, contour sur les notes hors gamme, bouton
  **Notes** (mémorisé) ; intensité des trigs portée par le fond pour garder
  les noms lisibles.
- [7.H] « Générer / Régénérer la bank » du front relance aussi l'analyse
  harmonique (`POST /api/tracks/{slug}/bank` enchaîne `harmony.process` ; un
  échec ne bloque pas la bank) ; le front met à jour gamme et accords sans
  recharger l'audio.
- [7.H] Front : gamme dans l'entête du lecteur (incertaine soulignée, survol =
  notes, marge, réglage DT2, alternatives) et accord en cours ; bande d'accords
  par mesure sous les sections (opacité = confiance, clic = saut, suit le
  zoom) ; touche [KEYBOARD] de la façade = écran KB SETUP (SCALE / ROOT, accord,
  progression de la section) et trig keys en clavier chromatique (gamme,
  fondamentale, notes de l'accord). `GET /api/tracks/{slug}` expose `harmony`
  et `keyboard_setup`.
- [7.H] `analyzer/harmony.py` + CLI `harmony.py <slug>|--all` : gamme du
  morceau (12 gammes du KEYBOARD SETUP de la DT2, fondamentale départagée par
  la basse, marge et statut « incertaine »), accords par mesure (triades, sus,
  dim, quinte à vide) et progression par section. Bloc `harmony` dans le
  sidecar (conservé si `analyze.py` réécrit le sidecar), section Harmonie et
  `scale` dans la note de bank. `digitakt.load_sources` rendu public.
- [7.G] Chaîne : double-clic sur un maillon = boucle du lecteur sur la
  section (calée sur les mesures, ÷2 / ×2 / Retirer comme une boucle tracée).
- [7.G] Façade Digitakt II complète : les 23 contrôles du §3.1 (VOLUME,
  LEVEL/DATA, PRESET/KIT, SETTINGS, SAMPLING, TEMPO, NO/YES, knobs A-H,
  touches PARAMETER, flèches, PAGE, RECORD/PLAY/STOP, TRK/PTN/SONG, FUNC,
  KEYBOARD) avec fonctions secondaires en orange. PLAY / STOP pilotent le
  lecteur, `[FUNC]` + TRK ouvre le mode MUTE, PTN + flèches change la lettre
  de bank, les touches PARAMETER changent la page des knobs (noms tirés du
  §11, NOTE / VEL du pas courant lus dans la bank).
- [7.G] Légende sous la façade (survol) : fonction, fonction FUNC, CC / NRPN
  de l'annexe B pour chaque knob, liens vers la fiche KB et le § du manuel ;
  bouton AIDE (un clic ouvre la fiche). Hub `web/src/lib/dt2.ts`, route
  `/api/manual/outline`.
- [7.F] KB intégrée au front : bandeau « Base de connaissance / Manuel PDF »,
  panneau ouvert sur le sommaire des fiches par lot (`/api/kb/toc`, noms de
  lots tirés du hub), wikilinks entre fiches cliquables.
- [7.F] Liens vers le manuel : `kb.py` lit le sommaire du PDF (`pypdf`) pour
  résoudre chaque `§x.y` en page ; pastilles « Manuel » en tête de fiche et
  `§` du texte cliquables, `doctrine §N` renvoyant à la section de la
  doctrine. Route `/api/manual` (chemin fixe), visionneuse dans le panneau
  élargi ou nouvel onglet. `pypdf` ajouté aux dépendances, `refs/*.pdf`
  ignoré par git.
- [7.C] Vue patterns façon Digitakt II, calquée sur la façade : écran bleu
  à bandeau inversé, 16 trig keys en 2 rangées de 8 (chiffre souligné, LED en
  contour rouge, une track à la fois, clic = saut au pas), LEDs de page 2 × 4
  + PAGE / FOLLOW, colonne TRK / MUTE / PTN (sélection de track, état des
  mutes de la phrase en cours, slots de la bank avec lettre A-P mémorisée par
  morceau) et nommage des patterns A01-P16. La grille multi-tracks devient une
  vue d'ensemble secondaire.
- [7.D] `kb.py` : corpus KB (`digitakt/kb/*.md`) + doctrine découpé en
  sections, recherche plein texte insensible aux accents ; routes
  `/api/kb/search` et `/api/kb/note` (chemins limités au corpus).
- [7.D] Panneau latéral KB dans le front (touche `/`), extraits surlignés,
  note rendue avec `marked` (HTML brut échappé) et positionnée sur la section.
- [7.D] Hub `digitakt/kb/_index.md` (25 thèmes, 5 lots) et lot 1 de fiches :
  projet et sauvegarde, presets / kits / pool, copier-coller, page setup,
  tempo et métronome.
- [7.D] Lot 2 de fiches : enregistrement et quantize, configuration MIDI
  (import des `.mid` de bank), parameter / preset locks, micro timing et
  retrigs, mode euclidien.
- [7.D] Lot 3 de fiches : sampling et resampling, machines SRC, amp /
  overdrive / bit reduction, filtres, LFO (riser one-shot), send FX et
  compresseur (sidechain), mixer et setup global (control all, overdrive
  master, équilibrage des patterns), FILL et conditions de trig.
- [7.D] Lot 4 de fiches : song mode (rejouer la chaîne d'une bank),
  changement de pattern et chaînes, mutes globaux / de pattern, perform kit
  et temp save.
- [7.D] Lot 5 de fiches : CC et NRPN (numéros utiles en live), tracks MIDI
  pour piloter un synthé, audio routing et Overbridge. Base complète
  (25 fiches, statut draft).
- [7.D] Fiche send FX et compresseur : routing vs source de sidechain
  (valeurs de `SCS`), réglages de départ, kick fantôme pour garder le
  pompage pendant les breaks, ducker vs colle master.

### Modifié

- [7.J5] Onglet Samples : colonnes de la grille dans l'ordre des tracks de la
  doctrine (rythmique puis mélodique, bandeaux de section, infobulle par
  code) ; arbre du kit plus lisible (samples en retrait, dossiers de code
  colorés par section) ; zones matrice / kits / samples encadrées ; les tags
  hérités du kit (bordure en tirets) ne se retirent plus sur le fichier.
- [7.J4] `POST /api/samples/status` et `/move` agissent par lot
  (`sources` au lieu de `source`) et renvoient la grille ; une erreur sur un
  fichier annule le lot. `analyzer.samples.move` reçoit les overrides et les
  met à jour lui-même ; `classify` renvoie aussi la corbeille.
- [7.E] Noms de notes alignés sur la DT2 (convention Elektron, 60 = C5) dans
  le front et la note de bank : une basse lue D2 auparavant s'affiche D3,
  comme sur la machine (constaté sur l'écran TRIG). Les notes MIDI envoyées
  ne changent pas ; les notes de bank existantes gardent l'ancien nommage
  jusqu'à leur régénération.

- Doctrine Digitakt : points *(à vérifier)* tranchés par le manuel OS 1.17
  (source de sampling, mode de tempo et `ROW TEMPO`, step recording, FILL,
  effacement des locks et des trigs, quantize) avec renvois vers la KB ;
  corrigés : pas de commande pour effacer les locks de toutes les tracks
  (`[FUNC] + [NO]` = reload temporaire), effacer un trig = `[TRIG] + [PLAY]`,
  silence en step recording = `[NO]`. Restent à tester sur la machine :
  affichage en Hz de l'EQ, sidechain d'une track hors main, import `.mid`
  multi-canal. Nouvelle fiche KB `keyboard-gammes` (KEYBOARD SETUP, gamme,
  tonique, `KB FOLD`, `NOTE PARAM`) pour le §11 ; `sampling-resampling`
  (rumble sur le pas du kick), `filtres` et `parameter-preset-locks`
  complétées.
- Doctrine Digitakt : nouvelles sections §9 (grave : fabrication du rumble,
  placement tribe, basse en contretemps, partage des fréquences), §10
  (compresseur master : routing, sidechain, kick fantôme), §11 (tonalité et
  harmonie : le kick donne la tonique, modes, progressions), §12 (tracks
  Id1 / Id2), §13 (set multi-styles : hiérarchie projet / kit / preset,
  un kit par acte, transitions de tempo, tribe vs mental), §14
  (aide-mémoire machine). Grille §1 : rumble sur le même pas que le kick
  avec ducking (et non entre les kicks), basse 80-250 Hz + harmoniques en
  contretemps.
- [media] `grab.py` transcode en FLAC les codecs non lus par Rekordbox (Opus,
  Vorbis) ; `file` et `file_path` sont relatifs à `<MEDIA>/Mix/`.
- [media] SPEC : décision Phase 3 révisée (Rekordbox est le logiciel de mix,
  export XML toujours hors scope).

- [7.G] Vue d'ensemble et partition de mutes en onglets sous le lecteur
  (choix mémorisé) ; l'onglet vue d'ensemble donne le pattern, son nombre de
  mesures et ses répétitions (`A01 · 8 mesures · joué ×2`), l'onglet mutes le
  nombre de phrases.
- [7.G] Vue d'ensemble : défilement horizontal automatique jusqu'à la mesure
  en cours quand la lecture sort de la partie visible (en FOLLOW), colonne
  des noms de tracks figée.
- [7.G] Vue bank en deux colonnes dès 1150 px de large : DT2 et légende à
  gauche, figées au défilement et dimensionnées sur la hauteur de l'écran ;
  lecteur, chaîne, vue d'ensemble et mutes à droite. En dessous, empilement.
- [7.G] Mise en page du front : DT2 en haut, centrée, sans les cadres gris
  autour des groupes de contrôles, touche FUNC en jaune ; lecteur, chaîne et
  vue d'ensemble réunis dans un seul bloc sous la façade (même largeur,
  centré) ; barre « Régénérer la bank » en bas. Liste des morceaux repliable
  (bouton « Morceaux », choix mémorisé dans le navigateur) pour donner toute
  la largeur à la vue.
- [7.G] Façade Digitakt II redessinée à l'échelle sur le dessin du §3.1 du
  manuel : emplacements et tailles exacts des knobs, touches, flèches, LEDs et
  trig keys (positionnement absolu sur un panneau de 834 × 682 unités, qui
  s'adapte à la largeur), icônes des touches de menu et du transport,
  sérigraphie des fonctions secondaires telle qu'imprimée (Perform, Save Proj,
  µTime−…), cadres des trig keys 1 / 5 / 9 / 13. AIDE et FOLLOW, propres au
  front, sortent du panneau.
- [7.E] Requalifiée en enregistrement assisté + pré-réglage CC / NRPN :
  aucun NRPN ne pose un trig sur un pas (annexe B du manuel).

### Supprimé

- `samples.py` (catalogue et dédoublonnage de banques de samples) abandonné :
  script, tests, `SAMPLES_CATALOG` de `paths.py` et documentation retirés.

### Corrigé

- [7.J5] La grille garde les colonnes de la vue non filtrée : choisir un kit
  (ou un tag) ne redimensionne plus l'interface.
- [7.J4] Samples : dans un dossier de kicks (`…KICKS 3`), une frappe de
  plus de 4 s reste une frappe au lieu de devenir une boucle DL avec un
  tempo estimé au hasard (7 kicks Vi Ta Lee MILLENNIUM KICKS 3 rendus à
  HARDCORE/BD, renommés `BD A Millen NN vtl`). Les boucles de ces dossiers
  qui le disent dans leur nom (`Loop`, tempo) ne changent pas.
- [7.B] Trigs de basse de la bank Digitakt : posés aux débuts de note pYIN
  (`note_segments`, `place_starts`, vote `fold_note_starts`) au lieu du
  seuil sur l'onset de la bande 40-400 Hz, qui ne voyait pas un riff joué
  legato (Riders on the Storm : trigs épars au lieu des croches
  E1 B1 G1 B1 E1 A1 C#2 A1). Début de note arrondi au pas le plus proche,
  erreurs d'octave isolées écartées par le vote. Test d'intégration du riff
  sur le stem réel.
- [7.E] Envoi à la DT2 avec PREROLL : la DT2 envoie un second Start au vrai
  départ du séquenceur ; il relance désormais l'envoi au pas 0 (l'envoi
  partait une mesure trop tôt). Le panneau demande `PREROLL = 0`, seul
  réglage sûr pour un pattern d'une mesure.
- [7.B] Notes de basse de la bank Digitakt : estimées par pYIN sur le stem
  `bass` (`_pitch_steps`, octave réelle, vote majoritaire `fold_notes`) au
  lieu de l'argmax du chroma, qui prenait les 3e et 5e harmoniques pour la
  fondamentale (Riders on the Storm : B2 / G#2 au lieu du riff E1 B1 G1 B1
  en mi dorien). Chroma conservé en repli et pour le lead. Test de
  non-régression marqué `integration` sur le stem réel.
- [7.I] Titre et artiste : le préfixe artiste est retiré du titre quand il
  diffère seulement par les liaisons (« Limitlezz x Maureen » contre
  « LIMITLEZZ , Maureen »), espace avant virgule retirée de l'artiste,
  suffixes `(Clip Officiel)`, `(Audio officiel)`, `[Official Audio]`,
  `(Lyrics)`, `(Visualizer)`… retirés.

- [7.G] Légende de la façade : le clic épingle le contrôle, le survol n'en
  montre qu'un aperçu (délai 120 ms, effacé en sortie), ce qui permet de
  traverser la façade jusqu'aux liens Fiche / Manuel sans perdre la cible.
- Doctrine §8 : la copie de pattern sur la DT2 se fait avec
  `[FUNC] + [RECORD]` / `[FUNC] + [STOP]` (et non `[COPY]` / `[PASTE]`).
- Doctrine §3 : combinaison du temp save confirmée par le manuel
  (`[FUNC] + [YES]`).

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
