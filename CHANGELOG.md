# Changelog

Toutes les évolutions notables du vault et des outils `scripts/`.
Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Les slices
renvoient aux phases de [[SPEC]]. Pas de `pyproject.toml` : la version vit ici.

## [Non publié]

### Ajouté

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

### Corrigé

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
