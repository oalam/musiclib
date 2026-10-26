# Changelog

Toutes les évolutions notables du vault et des outils `scripts/`.
Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Les slices
renvoient aux phases de [[SPEC]]. Pas de `pyproject.toml` : la version vit ici.

## [Non publié]

### Ajouté

- [7.M] [[veille-theorie]] §F : veille web du 2026-10-26 sur les phrases, la
  tension et le couple kick / basse (17 sources ouvertes, trois tableaux par
  thème, convergences, désaccords chiffrés et trous à combler par des KT
  maison : kickbass contre kick + basse, accordage du grave en intervalles,
  progression par phrases aux seules conditions et mutes de la DT2).
- [7.K2] Lecture par phrases dans le front : sous la forme d'onde, deux
  bandes tirées de la bank, les **phrases** (`phrase_bars` mesures, qui
  repartent à chaque section comme la partition de mutes) et les **tours de
  pattern** (un tour = `bars` du pattern, positions sur la grille de mesures
  recalée sur le kick, repli sur le tempo moyen), avec le tour courant
  surligné et une ligne live « pattern 03 · tour 2/4 · phrase 1/2 · mesure
  6/8 » ; double-clic sur un tour = boucle sur ce tour. Dans la chaîne de la
  vue bank, un **clic sur un maillon** place la tête de lecture au début de
  la section et boucle sur tous ses tours (second clic ou bouton « Retirer la
  boucle » = fin de boucle, Maj + clic = saut seul) ; le maillon bouclé est
  marqué. Liste des morceaux : **plage de BPM** min / max (inclusive, vide =
  pas de borne), persistée avec le reste du filtre.
- [7.M] KB tutos, lot 3 « Recettes maison » : fiche
  [[maison-rumble-dans-le-kick]], rumble fabriqué dans la queue sèche du
  kick (track 1) par lock trigs, LFO one-shot ou delay en contretemps, puis
  figé en sample ; le piège de l'envoi reverb (le send dose l'entrée, pas la
  queue) est expliqué avant les recettes. Draft, à rejouer à la machine.

### Modifié

- [7.M] Veille §F distillée dans les KT : KT5 (bandes kick / rumble /
  basse des sources, mono sous 120 Hz, cloche dans le kick, désaccord sur
  le passe-haut du rumble), KT9 (règles de bloc 16 / 32 / 8, recettes de
  fin de bloc, un seul pattern en six sections aux mutes, `1:2` / `2:2`
  qui allongent la période), KT11 (plan hypnotique de 64 mesures,
  breakdowns de 2-4 mesures, filtre en EXP), KT13 (kick conçu en premier,
  rumble en send), KT21 (double-croche du kick vide, basse en trois
  couches, release = 60 000 / BPM) ; fiche [[rumble-grave]] : table des
  repères chiffrés recalés à 180-200 BPM et sources écrites.
- [7.M] KT21 [[kt-basses]] : entrées et sorties de la 9 à l'étage de la
  décision, en miroir de la table des hats (entrée sur le 1 d'une phrase
  de 16 ou 32 pour toute la section, pas d'annonce, trou de tension d'un
  tour, break avec kick et rumble, note changée à la section), cas du
  kickbass sans basse, exercice 4.
- [7.M] KT20 [[kt-hats]] : entrées et sorties des tracks 6, 7, 8 à l'étage
  du tour (statut de chaque track, table des durées : entrée 2 tours
  minimum, annonce sur 4 mesures, respiration d'un tour, sortie sur le 1
  d'une phrase de 16 en ordre inverse), préparation dans le pattern en
  `NOT 4:4` et `3:4`, exercice 5.
- [7.A] Doctrine, révision « phrases » du 2026-10-26 : §2 un pattern main
  fait 8 mesures et est écrit pour 4 tours (cycle en conditions et
  p-locks, lignes fixes), patterns de 2-4 mesures réservés aux
  transitions, slots 1-8 nommés par rôle (intro, mains A et B, variantes,
  break, drop, sortie) ; §4 la partition de mutes est le scénario par
  défaut, un mute par phrase de 8, une décision par 16 ou 32, ajouter un
  instrument = démuter ; §6 principe 3, un étage par changement (tour :
  conditions, phrase : mutes, section : pattern). KT9 renvoie dessus.
  Idée hors doctrine notée en SPEC 7.B3 (variations par tour dans la
  bank), à venir.
- [7.M] KT9 [[kt-phrasage-tension]] : section « Compter sans compter »,
  les repères de phrase (conventions techno par étage, en regard des
  haltes et roulements mesurés sur Kodaman et Tekotak) et six façons de
  faire compter la DT2 (`1:4` sur une track de 128 pas, `NOT 4:4` pour le
  kick cut, un étage par tour, LFO de 32 mesures relancé par `LFO.T`,
  `CHANGE`, song mode), un exercice et deux pièges ; le comptage mental
  en dernier recours.
- [7.L6] Un sample peut figurer dans **plusieurs banques** d'un live, un
  item par banque (identité `(source, bank)`) avec son nom, sa track et son
  accordage sur la tonique de sa banque. L'ajout à une autre banque **copie**
  au lieu de déplacer (révise 7.L5 « une seule banque par sample ») ; le
  retrait reste par banque ; `POST .../rename` et `GET .../audio` prennent
  `bank`. Migration d'un live d'avant 7.L5 : un item par banque d'origine.
  Front : badges de banques cumulés par sample, écoute et renommage par
  banque.

### Corrigé

- [7.M] [[rumble-grave]] plaçait `OVER` sur la page AMP ; l'overdrive est
  sur la page FX (manuel §11.8), avec `OD.RT` pour le passer avant ou après
  le filtre.
- [7.M] Fader de resample ([[elektronauts-resampling]] astuce 2, exercice 2
  du panorama) : la recette du fil (profondeurs de LFO3 de signes opposés)
  ne tient pas, le CTRL-ALL est additif ; l'inversion vient de la phase du
  LFO de la track resample. Constaté puis vérifié à la machine le
  2026-10-24 : première astuce du lot 2 rejouée.
- [7.L] Un sample ajouté dans une banque déjà accordée restait à sa hauteur
  d'origine (`note` nulle, `shift` 0) jusqu'au réaccordage manuel de la
  banque. `lives.add` accorde désormais les TUNABLE ajoutés sur la tonique
  de la banque (mesure de la note comprise).

### Ajouté

- [7.M] Fiche tuto [[synthackers-techno-acid]] (lot 1 des tutos, ordre 2) :
  seconde session one-box de Synthackers (*Let's Grill a Techno Banger*,
  2025-10-14, 49 min) ramenée à vingt tricks horodatés : kick puis ligne
  acid depuis un preset Substance, sidechain du kick sur la basse et sur
  les effets, swing réglé au shaker, une seule perc tordue en texture,
  builds au breath controller, choix du clap. Statut draft, non rejouée.
- [7.M] Astuces Elektronauts dans la KB tutos, **lot 2** : le fil *Digitakt II
  Tips & Tricks* (564 posts) ramené à onze fiches, une par famille
  ([[elektronauts-presets-pool]] … [[elektronauts-raccourcis]]), chaque
  astuce déroulée pas à pas avec son post d'origine, plus un
  [[elektronauts-panorama]] (vocabulaire, pièges, exercices d'ensemble).
  Remplace la KT22 d'abord rangée dans le hub théorie (lot 5 retiré).
  Statut draft, non rejouées.

- [7.M] Fiche KB [[presets-substance]] (lot 3, ordre 37) : pack Substance de
  Synthackers (64 presets `.dt2pst`, 32 BASS / 32 SYNTH, ondes d'usine, zéro
  RAM), installation par Transfer, macros, place dans la grille et catalogue
  à remplir à l'écoute. `digitakt/presets/` ajouté au `.gitignore` (licence).

- [7.L] `digitakt/grille.html` : grille des 16 tracks interactive (face avant
  SVG avec mutes, coupures grave / aigu, breaks et montée pas à pas du §4 ;
  séquenceur 16 pas avec presets techno, tribe, hard techno, half-time tirés
  des KT, édition au clic, lecture WebAudio). Liée depuis la doctrine §1.
  Servie par `GET /api/kb/grille` et affichée dans le panneau KB du front
  (bouton « Grille », iframe comme le manuel) ; preset « Synthackers » et
  ride (8) ajoutés au séquenceur, lien depuis la fiche tuto.

- [7.M] KB : nouvelle rubrique **tutos** (`digitakt/kb/tutos/`, hub
  `_index.md`, lot 1 « Sessions complètes ») pour les sessions vidéo
  décortiquées trick par trick (track, instrument, pas, lien vers le
  chapitre, mise en regard de la grille doctrine §1). Première fiche :
  Synthackers, techno one-box sur DT2 (18 tricks). Onglet « Tutos » dans le
  panneau KB du front ; `kb.py toc` la reprend sans changement.

- [7.L5] Lives : **une seule banque par sample** (`bank`, l'ajouter ailleurs
  le déplace), **dossiers à plat** `<live>/<BANQUE>/<nom>.wav` (une banque de
  patterns = une banque RAM de la DT2 = un dossier chargé d'un coup) et **kit
  par défaut `0-KIT`** : 16 samples au plus, un par track de la doctrine
  (`track`, proposée d'après le code, `set_track` échange avec l'occupant),
  exportés `NN <nom>` pour occuper les slots A01-A16 de tout pattern vide ;
  tonalité et tempo propres. `POST /api/lives/{live}/track`. Plafond
  `LIVE_CAP` 127 par banque, compte par branche (`branches`) dans le bilan.
  Front : ligne 0-KIT en tête, numéro de track modifiable en place, compte
  par branche en filtre local, plus de badge multi-banques ; une ligne de
  la liste du live se glisse sur une autre banque pour la déplacer. Décisions dans
  SPEC « Décisions 7.L5 », doctrine solaris et README à jour.

### Modifié

- [7.L] **Grille des 16 tracks révisée le 2026-10-19** (doctrine §1, §4, §9,
  §12 ; SPEC « Décisions 7.L ») : 4 perc one-shots, 5 Id1 rythmique (BR /
  DL / PL ou seconde perc), 6 hat fermé, 7 hat ouvert, 8 ride (ordre de la
  sérigraphie DT1, aigu à droite), 9 basse BS ou BL (possède le grave),
  13 Id2 bas-médium, 14 Id3 médium-aigu. Reportée dans `TrackSpec` et la
  famille hats de `analyzer/digitakt.py` (`classify_hats` rangeait encore
  fermé / ouvert / ride sur 4 / 5 / 6, grille d'avant le 13 octobre),
  `KIT_TRACK_FOR` de `analyzer/lives.py`, les tracks du 0-KIT de solaris,
  les libellés de la vue Samples, la doctrine solaris, la fiche Maschine
  (pads 1-8, qui décrivait aussi l'ancienne grille), une quinzaine de fiches
  KB / KT et la fiche tuto Synthackers. Export du live solaris à relancer.

- [7.L5] `0-COMMON` disparaît : un live existant est migré au chargement
  (première banque gardée pour un sample de plusieurs banques, samples de
  `0-COMMON` fusionnés dans la dernière banque du live, ici F-JOKER ;
  tonalité, tempo et presets de `0-COMMON` oubliés). Le premier export
  retire l'ancien arbre (`0-COMMON/`, sous-dossiers de branche).

- [7.M] KT10 : passe par mesure et profil du kick sur Floxytek (*Micro
  Tribe*, *Roots*) et Tekotak (*L'okapi*, stems Demucs et bank générés).
  Tekotak mesure le doublé martial : kick sur le « et » du 1 toutes les
  2 mesures, accentué toutes les 4, halte long de 3 temps et demi toutes
  les 8, zéro mesure décalée. Trois architectures du grave : kick-sub
  écrêté sans rumble (Floxytek, 15 % des échantillons au pic, pas de pitch
  envelope), kick saturé plus rumble en bosse (Kodaman), kick de médiums
  avec tout le sub dans la basse (Tekotak, stem bass à +17,5 dB). Limite
  notée : Demucs range le kick-sub de Floxytek dans le stem bass sur la
  moitié des morceaux, zones non analysables.
- [7.M] `scripts/kt_kick_profile.py` : kick moyen d'un plateau depuis les
  stems (enveloppe, pitch envelope et note de la queue, spectre attaque /
  corps, indices de saturation, click, rumble par stem et profil du sub sur
  un temps). KT10 : kick et rumble de Kodaman mesurés (*Smash* : click
  1-3 kHz puis corps saturé à crêtes aplaties, pitch envelope 91 → 56 Hz
  sur 100 ms, rumble en bosse de 140 ms à +7 dB gatée à la moitié du temps ;
  *Béton* : kick de 30 ms à knock bas-médium, rumble porté par la basse),
  recette DT2 correspondante ; passe par mesure sur Béton et Floxytek
  (banks générées) : zéro mesure décalée, le halte et le roulement autour
  du 1 sont une signature de Kodaman, le rebond simple est partout.
- [7.M] `scripts/kt_kick_bars.py` : kick mesure par mesure en croches depuis
  le stem drums (attaque détectée par la montée d'enveloppe 35-130 Hz),
  période des coups sur chaque « et », séquence des mesures (temps /
  décalé d'une croche / roulement / mixte). Sur Kodaman x Mosmoz &
  Adharaa *Smash* : 21 mesures sur les temps, 21 décalées d'une croche, 20
  de roulement ; KT10 documente le rebond poussé jusqu'au déplacement du
  kick, le morceau ajouté aux références tribe du hub.
- [7.M] Correction : le « déplacement » mesuré sur *Smash* était un artefact
  de la grille fixe du sidecar (152 BPM contre 156,6 réels, dérive d'une
  croche en 4 mesures). `kt_kick_bars.py` lit désormais la grille re-suivie
  de la bank Digitakt quand elle existe ; sur *Smash* : 64 mesures sur les
  temps, 0 décalée, 10 de roulement, 19 rebonds. KT10 réécrite en
  conséquence : halte de deux temps à chaque phrase de 4, rebond en
  roulement de 4 croches autour du 1, roulement long au peak, et partition
  rythmique de la mesure type (kick, rumble sur le pas suivant, clap en
  anticipation, hats, perc, basse en contretemps) tirée de la bank.
- [7.M] KT20 hats, ride et haut du spectre (bande high par style depuis
  le hub, fermé = grille, ouvert = contretemps avec choke par AMP ou
  preset lock, profils de vélocité de grille, polymétrie des hats,
  masquage avec l'acid, quatre exercices) et KT21 basses, rythmes et
  rôles (dix rythmes de basse sur une note, le contretemps comme défaut et
  non comme limite, ducking contre contretemps, basse-Id, basse comme voix
  harmonique), ajoutées au lot 1 : 21 KT, SPEC « Décisions 7.M » complétée.
  KT10 : le rebond du kick (doublé martial une croche avant le 1, une
  mesure sur 2 ou 3, trig ajouté sous condition `2:2` / `3:3`), signature,
  vocabulaire, exercice, pièges.
- [7.M] Grabs du lot 3 et recalage de KT12-KT13 : neuf références ajoutées
  à la library (frenchcore Dr. Peacock, Sefa, Imperials, Maissouille &
  Kriptonic ; hard techno Sara Landry & Shlømo, 999999999, I Hate Models ;
  schranz Chris Liebing & André Walter, DJ Rush), quatre mauvais candidats
  de la recherche libre retirés (set complet, titre sans rapport, Bangbop,
  artiste « 08. Dr. Peacock » corrigé), sidecars frenchcore et Maureen
  réanalysés avec le tempo de la library (lus à la moitié), passe
  harmonique sur les neuf. `kt_signatures.py` : styles `frenchcore` et
  `schranz`, `hard_techno` à quatre morceaux. Hub : tables par style,
  lecture rapide, bilan des grabs. KT12 : signature mesurée (basse offbeat
  vue à moitié chez Sefa, galop chez Imperials et Mad Dog, progression i →
  bVI → bVII chez Sefa, triton chez Maissouille). KT13 : signature à six
  morceaux ; la conclusion « le hard techno suit le temps » tenue sur
  Beauz seul est corrigée, trois références sur quatre anticipent comme le
  tribe, la pression est le vrai critère ; KT3 nuancée en conséquence.
- [7.M] KT3 : les hats et la syncope (fermé = grille, ouvert = contretemps,
  « a » = anticipation, ride), définitions de syncope et de contretemps,
  lecture de la métrique `sync` du hub par style, exercice « le hat ouvert
  décide du style » ; KT1 : les deux cellules de 4 pas, contretemps `..x.`
  et anticipation `...x`.
- [7.M] KB théorie, lot 3 (styles cœur du live) : KT10 tribe / hardtek
  (boucle de référence en six tracks, pitch envelope, toms en
  appel-réponse qui anticipent, plateaux et points d'orgue, bank Kodaman
  comme exemple de forme), KT11 acid core / mental (kickbass qui tient le
  grave, acid line de trois notes, accents et slides d'abord, 15 pas,
  narration au filtre, anticipation maximale des références), KT12
  frenchcore / hardcore / bouncy (kick clippé donc mélodique, pitched
  kick, basse offbeat `.xxx` = rolling bass, galop mesuré chez Mad Dog,
  hardcore monolithique, breaks impairs), KT13 hard techno et schranz
  (double kick en millisecondes, pression, énergie après le temps à
  l'inverse du tribe, ligne sur 3 mesures ; cadré sur la rythmique, le
  son reste dans `rumble-grave`). Mad Dog ajouté aux références hardcore.
  Grab frenchcore / hard techno non fait (disque média absent) : requêtes
  proposées dans le hub, « À grabber », KT12-KT13 à recaler ensuite.
- [7.M] KB théorie, lot 2 (socle harmonique et forme) : KT5 tonalité du
  grave (notes du sub en hertz, une note sous 120 Hz, partage des bandes et
  du temps, kickbass), KT6 modes de la techno (cinq modes sur une tonique,
  note caractéristique, tonique fixe), KT7 tensions et lignes
  (pentatonique sûre, blue note, b2, triton, rapports d'intervalles, règle
  du retour), KT8 accords, voicings, rythme harmonique (qualités, voicing
  sans doublure grave, progressions lentes sur pédale, accords sur track
  monophonique, Camelot du setbuilder), KT9 phrasage et tension (phrases
  de 4 / 8 / 16 / 32 en secondes, soustraction, appel-réponse, turnaround,
  arc). Passe harmonique `scripts/kt_signatures.py --harmony` (gamme
  détectée, score, accords de la section principale par morceau de
  référence), table dans le hub ; lecture : 17 morceaux sur 32 incertains,
  quintes nues et sus2 dans 27, pentatonique ou blues dans 25.
- [7.M3] Panneau KB du front en trois onglets, Fiches machine / Doctrine /
  Théorie : `kb.doctrine_files` ajoute les doctrines de live
  (`digitakt/doctrine-*.md`) au corpus et au sommaire (groupe `doctrine`,
  un lot, doctrine générale en premier, `status` du frontmatter comme
  statut) ; les références `§N` d'une doctrine de live visent la doctrine
  comme dans `doctrine.md`. Front : barre d'onglets collante, l'onglet
  suit la note ouverte (« ← Sommaire » revient dessus), pas d'en-tête de
  lot pour la doctrine.
- [7.M] KB théorie, lot 1 (socle rythmique) : KT1 cellules rythmiques
  (tresillo, cinquillo, claves, hémiole, table E(k, n) canonique, rotation),
  KT2 polymétrie / polyrythmie / dissonance métrique (table des ppcm contre
  16 pas en mesures et en secondes à 190 BPM, groupement / déplacement de
  Butler, trois voies de polyrythmie sur la DT2), KT3 swing / microtiming /
  ghost notes / densité (table swing en millisecondes à 190 et 130 BPM,
  lecture de la métrique `swing` du hub : l'ornement tribe anticipe le
  temps au lieu de shuffler), KT4 backbeat / half-time / passerelles de
  tempo (90 / 180, 140 / 186,7 par 3 contre 4, 175 / 190 par nudge, chemin
  tribe → DnB sans changer de tempo). Chaque KT : signature théorique et
  mesurée, vocabulaire, trois exercices sur la grille de la doctrine,
  pièges, sources écrites. Hub `digitakt/kb/theorie/_index.md` : liens,
  statuts `draft`, passe `rhythm_signature` relancée (BPM réanalysés, deux
  lectures à la moitié du tempo). Veille : E(7, 16) corrigé (la forme
  notée était E(5, 16)).
- [7.M] KB théorie : veille `digitakt/veille-theorie.md` (socle rythme /
  harmonie / forme, 4 styles cœur, 6 styles connexes, ressources avec statut
  de vérification, exercices DT2), décisions 7.M dans le SPEC, hub
  `digitakt/kb/theorie/_index.md` avec les 19 KT à rédiger et la passe
  `rhythm_signature` sur les morceaux de référence par style (patterns 16
  pas tirés des sidecars). Aucune KT rédigée encore.
- [7.M2] KB théorie visible dans le front : `kb.corpus_files` lit
  `digitakt/kb/` récursivement (recherche et lecture des notes de
  `theorie/`, hubs compris) ; `kb.table_of_contents` range les lots par
  groupe (`KbLot.group` = `fiches` ou nom du sous-dossier, `KbLot.hub` =
  son `_index.md`), noms des lots lus dans le hub du dossier (`##` ou
  `###`), lots déclarés sans note émis vides. Panneau KB : un en-tête par
  groupe (clic = hub), lots vides signalés, wikilinks résolus depuis le
  dossier de la note ouverte puis par nom court ; statut autre que
  `vérifié` surligné. CLI `kb.py toc` préfixe le groupe.

- [8.L2] L'export d'un live régénère d'abord les rumbles de toutes les
  banques à presets (`sounddesign.rumble_live`, `POST /api/lives/{live}/export`
  renvoie un bilan par banque dans `rumbles`) : un preset édité ou un tempo
  changé donne de nouveaux rendus qui remplacent les anciens dans la banque,
  puis la copie vers `00-live`. Le bilan du front annonce les rumbles à
  rendre (« Rendre et copier »), CLI `sounddesign.py rumbles <live>` sans
  banque pour toutes les banques à presets.
- [8.L2] Purge des rumbles supplantés : le sidecar d'un rendu généré pour
  une banque porte `rumble` (le preset) ; `sounddesign.orphan_rumbles`
  retient ceux que plus aucun live ne référence, `purge_renders` retire
  wav, sidecar, copie versée et override ; CLI `sounddesign.py purge
  [--dry-run]`. Un rendu fait à la main (sans `rumble`) n'est jamais
  retenu. Les 72 sidecars existants ont été marqués (one-shot).
- [8.L2] Rumbles par banque de live : presets de rumble associés à chaque
  banque (`Live.rumbles`, 5 au plus, `PUT /api/lives/{live}/rumbles`) ;
  `sounddesign.rumble_bank` rend un rumble par kick de la banque et par
  preset au tempo de la banque, le verse (avec `parent`) et l'ajoute à la
  banque sans attendre la réanalyse (`lives.render_item`, `add_item`).
  Rejouable : rendu existant réutilisé, versement sans recopie, rumble déjà
  présent inchangé ; aucun preset associé = rien de généré. Route
  `POST /api/lives/{live}/rumbles` (`dry_run`), CLI `sounddesign.py
  rumbles <live> <banque>`, panneau Live : cases à cocher et bouton
  « Rumbles » sur la ligne de la banque, bilan sur une ligne.
- [8.L2] Nom DT2 du rumble en miroir du kick (`BD G Apart 01 rth` →
  `RM G Apart 01 rth`, tag du preset à la place du numéro avec plusieurs
  presets), note d'origine dans le fichier et accordage hérité du kick
  (`lives.inherit_tuning`), `LiveItem.rumble` (preset) affiché avec le tempo
  dans la liste ; au changement de tempo, le rumble du même kick et du même
  preset est remplacé dans la banque (`replaced`).
- [8.L2] Écouter un sample dans le panneau Live en fait la source du sound
  design (`focus.set`), même hors de la liste courante de la lib.
- [8.L1] Parenté kick → rendu du sound design : le versement écrit
  `parent` (clé du sample d'origine) dans `overrides.json` ; l'entrée du
  manifeste et l'item de live (`LiveItem.parent`) le reprennent,
  `samples.children_of` liste les rendus issus d'un sample. Exposé par les
  API existantes (entrées, lives), sans affichage dans le front.
- [7.J8] Note de transmission [[kt-banque-samples]] : préparer l'audio
  (seuils du pré-filtre), nomenclature des fichiers maison, classement,
  corrections et envoi sur la DT2 via un live.

### Modifié

- [7.L4] Panneau Live : « Exporter… » remonte dans l'en-tête, à droite du
  sélecteur de live, avec une icône et la couleur d'accent ; le bilan
  d'export s'affiche sous l'en-tête. « accorder le live » /
  « désaccorder » deviennent un seul bouton à bascule (diapason, bleu de
  la transposition, allumé quand le live est accordé) à côté.

### Corrigé

- [7.J8] Samples : les voix de `Movie tracks` restaient non classées. La
  règle du code `VX` ne connaissait ni le dossier `VX/` ni le mot « choir »
  (reconnu seulement pour la sous-catégorie `CHANT`). Ajout de `vx` (mot
  entier) et de `choir` aux règles `VX` (one-shots et boucles) : les 11
  samples de films vont en `VX/CHANT` et `VX/SPEECH`, sans effet sur le
  reste du disque (vérifié sur `/Volumes/xtreme/Samples`).
- [7.J2] Vue Samples : le sample en cours sortait de l'écran en naviguant
  aux flèches dans une longue liste. La ligne était cherchée par
  `getElementById` avec un id passé par `CSS.escape`, qui ne correspondait
  jamais dès que le chemin contenait espace, `/` ou parenthèse. Elle est
  maintenant trouvée et défile pour rester visible.
- [7.J2] Vue Samples : clavier inopérant (flèches haut / bas, Espace,
  étoiles, Suppr…) dès que la vue Sound design avait été ouverte une fois.
  Celle-ci reste montée, masquée, et sa colonne `aside.panel` passait pour
  un panneau ouvert par-dessus. Seul un panneau réellement affiché bloque
  désormais le clavier.
- [7.K] Vue par type : la note (roue) et la tranche de tempo choisies pour
  un instrument restaient actives, et mémorisées, en passant à un autre.
  Une note de kick vidait les boucles PL, qui n'ont pas de note. Ces deux
  filtres et l'arborescence repliée sont remis à zéro quand le filtre
  d'instrument change.
- [7.B] Frappes de drums des banks : événements (onsets du stem drums)
  classés par montée d'énergie dans la bande de chaque track, au pas le
  plus proche, au lieu du max d'enveloppe par pas qui retenait le fond
  (cymbales, pluie) et avançait une frappe d'un pas. Kick et clap / snare
  départagés par l'écart de niveau entre bandes (seuil d'Otsu sur le
  morceau), kick cherché aussi dans le corps 120-300 Hz (sub ou rumble
  continu), fuite de basse écartée ; banks Kodaman régénérées.
- [9.C] Vue Acid : le rack audio masqué restait affiché sous la colonne
  des traitements (règle `.sd` plus forte que `.hide`) et coupait la vue ;
  boutons Notes / Accent / Gate / Octave inversés, comme les « Randomize »
  de Sting : allumé = tiré par Generate, éteint = gardé (en orange, un
  verrou passait pour actif et Generate semblait sans effet).
- [8.K] Paramètres en % affichés sans unité (`52.00` au lieu de `52 %`) :
  Saturator, Overdrive.
- [8.F] Clic d'un rumble joué une seule fois : la boucle finissait en plein
  grondement (0,53 d'amplitude sur `Kick 1973 DS 1`, preset `deep`). Le
  duck anticipe désormais le coup (creux complet sur le kick, y compris
  celui de la boucle suivante) : début et fin à 0,018, jointure continue.
- [7.K] Boutons « Morceau » / « Sample » de la barre générale : ouvrent
  aussi la vue correspondante (ils ne changeaient que la cible de la
  télécommande) ; « Sample » n'est plus grisé avant la première visite.
- [7.J8] Reconstruction des samples non rejouable : une boucle BR / DL dont
  le tempo avait été mesuré le perdait en passant hors plafond (réserve sans
  tempo) et repartait à la racine au passage suivant, d'où une oscillation
  racine / tranche à chaque réanalyse. La réserve garde désormais `bpm` /
  `bpm_est` ; la reconstruction reprend les tempos des candidats et de la
  réserve. Le manifeste converge (deux passages identiques). Le filtre de
  tempo (7.K) lit aussi ce tempo pour la réserve.
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
- [7.K] Recherche des samples sous « Library », réduite à texte, tags,
  kits et instruments (filtres rythmique / mélodique, one-shot / boucle et
  étoiles retirés) ; roue des notes déplacée dans la vue de droite, qu'elle
  seule filtre, alignée avec la forme d'onde. Clic sur un code de l'arbre :
  filtre d'instrument.
- [7.K] Colonne de gauche des samples en deux zones fixes de même hauteur,
  « Library » et « Kits », chacune scrollable (titre et recherche fixes).
- [7.K] Total général sous « Library » : fichiers (candidats + hors
  plafond) toutes branches, sous le filtre courant, et retenus.
- [7.K] Arbre « Library » : libellé de l'instrument entre parenthèses à
  droite du code, précédé de la track de la doctrine (ex. « BD 01 (Kick,
  bass drum) », « PC 07-08 (…) »), détail complet en infobulle.

### Modifié

- [7.K] Vue par type : un clic sur une case de l'arbre (ex. PL / TOPS)
  restreint la vue du milieu à cette case au lieu d'y faire défiler ; un
  re-clic sur la case, ou sur l'étiquette du code, revient au type entier.
- [7.L] Vue Samples simplifiée (front seul) : garder / écarter, réserve,
  plafond, rangement (« Case… », `M`, dépôt sur une case, sous-dossiers) et
  « Exporter… » retirés ; tous les fichiers d'une case listés ; filtre local
  par tag ou style au-dessus de la liste (suggestions des tags les plus
  fréquents) ; corbeille en icône. Back et décisions écrites inchangés.
- [7.L2] Vue Samples plus lisible avec le panneau du live : aide clavier
  retirée sous la barre d'actions, colonnes Library et Live resserrées
  (210-270 et 230-290 px) au profit de la liste, pads des kits en grille
  auto (2 ou 3 par ligne), boutons de la Library sans coupure de libellé.
- [7.L1] Grille de tracks révisée de `digitakt/doctrine.md` §1 (4 ride,
  5-6 hats, 12 vocal, 13-14 Id1 / Id2) reportée dans les `TrackSpec` de
  `analyzer/digitakt.py`, l'ordre `samples.CODES` et les libellés de la
  vue Samples. Les banks déjà générées gardent l'ancienne grille jusqu'à
  leur régénération.
- [9] SPEC : cadrage de la Phase 9, générateur MIDI acid inspiré de Sting
  (if-tah) : fonctions de référence tirées de son manuel, sous-phases
  9.A-9.H, décisions (générateur du front, cibles DT2 ou VST du Mac,
  fonctions non supportées par la DT2 acceptées), moteur Python proposé.
- [7.D] Fiche KB `midi-vst` : pas à pas « figer l'acid en boucles pour le
  live » (export au tempo et dans la tonalité, machine STRETCH, longueur de
  track en PER TRACK, retouches dans la DT2) et piège du grain de STRETCH.
- [7.D] Fiche KB `slice-breaks` : étape 5 du pas à pas (amen re-séquencé à
  172) détaillée en trois patterns réservoir B13-B15 (dense, aéré, ancré),
  tirage CREATE RANDOM LOCKS relancé à chaque `[YES]`, bon tirage figé par
  temp save, points à vérifier sur la machine. Étape 1 passée en grille
  égale sans détection de transitoires (tranche n = pas n), ancrage de B15
  corrigé en conséquence, avec la grille des appuis de l'amen en 16 pas.
- [8.K] Devices du rack sound design compactés façon Live, sans espace
  vide : sélecteurs en bandeau (bascule pour Off/On comme Color ou
  Hi-Quality, segments pour Post clip ou le modèle A/B/C, menu déroulant
  pour la courbe ou le type de filtre) ; potards principaux en grille d'une
  rangée (jusqu'à 3) ou deux, qui s'étend en largeur ; paramètres activés
  par un sélecteur (Saturator : Color, Waveshaper) en sections titrées de
  champs à barre à droite (`Knob` variante `bar`, préfixe commun retiré :
  WS Drive -> Drive) ; bouton d'automation ↗ en coin du potard au lieu
  d'une ligne dédiée. Le Saturator complet passe de ~700 px de haut à ~130.
- [8.I] Variations : la tranche 1 est désormais la **source brute**, sans
  traitement (le son de référence) ; les variantes occupent les tranches 2
  à N, de la plus sobre à la plus marquée. Les rendus antérieurs ne sont pas
  touchés : la révision du rendu entre dans le hash, le nouveau fichier ne
  les écrase pas.

- [8.E] Un rumble versé n'est plus rangé en `LOOPS/BL` (contraire à la
  doctrine : le rumble est la track 2) mais en `DRUMS/RM/...` ; la
  recherche de source de la vue Sound design est retirée au profit du
  sample en cours de la vue Samples. Un rendu antérieur, sans nom DT2,
  est à re-rendre avant de le verser.
- [7.J8] Plafond de `LOOPS/BR/060` porté à 64 (`FOLDER_CAPS`, plafonds
  propres à un dossier) : 175 candidats, tous en lice, 64 retenus ; 1 183
  retenus au total (1 151 + 32).
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

### Modifié

- [7.L4] Accordage appliqué au live entier (`lives.tune_live`) : « accorder
  le live », à côté de la jauge de RAM, accorde chaque banque qui a une
  tonalité (0-COMMON compris) ; les samples d'une banque sans tonalité
  reprennent leur hauteur d'origine ; « désaccorder » remet tout le live.
  Tout ou rien si une tonalité est illisible. `POST /api/lives/{live}/tune`
  ne prend plus que `reset`. Les liens par banque disparaissent.

### Ajouté

- [7.L4] Panneau du live au clavier : après un clic sur un sample de la
  banque, flèches haut / bas parcourent sa liste (écoute accordée), gauche /
  droite changent de banque (premier sample joué), Espace rejoue ou relance
  au tempo comme dans la lib. Un choix dans la lib lui rend les flèches.
- [7.L4] Vue Samples, panneau du live ouvert : case « hors live » du
  filtre de la liste, qui masque les samples déjà pris dans le live (toutes
  banques), mémorisée ; le compteur affiche `affichés / total`. Avec le
  filtre, un ajout par `L` ou `Entrée` fait passer au sample suivant.
- [7.L4] Vue Samples, panneau du live ouvert : `Entrée` ajoute le sample en
  cours (sans la sélection) à la banque active.
- [7.L4] Écoute accordée dans le panneau du live : un sample transposé est
  joué tel qu'exporté (forme d'onde, lecture et Espace tenu), rendu par la
  même fonction que l'export (route `GET /api/lives/{live}/audio?source=`).
- [7.L4] Accordage étendu aux pads (PD, note mesurée) et aux stabs (ST,
  note du nom de fichier).
- [7.L4] Accordage par banque d'un live : bouton « accorder » de la liste
  de la banque active, qui ramène ses kicks, rumbles et basses (BD, RM, BS,
  `lives.TUNABLE`) sur la tonique de sa tonalité (`Fa m`, `sol mineur`,
  `F#m`, `Bb`… lue par `lives.key_root`), par le plus court chemin (-6 à +5
  demi-tons). Note de la source : manifeste, sinon nom du fichier, sinon
  mesurée (`measure_note`, BD / BS de la réserve) et gardée dans le live.
  Décalage gardé par sample (`shift`) et appliqué à l'export en varispeed
  (`samples.write_varispeed`, même format que la source ; l'index d'export
  note le décalage) : la lib n'est pas touchée, « désaccorder » remet la
  hauteur d'origine. Nom DT2 mis à la note d'arrivée (insérée si absente),
  RAM recalculée sur la durée transposée. Route
  `POST /api/lives/{live}/tune` (`bank`, `reset`). 0-COMMON n'est accordé
  que sur sa propre tonalité.
- [7.L2] Panneau du live : dépôt de samples directement sur la liste de
  la banque en cours (titre ou fichiers), en plus des lignes de la grille.
- [7.L2] Tempo par banque d'un live (`tempos`, `lives.set_tempo`, route
  `POST /api/lives/{live}/tempo`), champ BPM de la banque active dans le
  panneau du live. Espace tenu dans la vue Samples : le sample en cours
  est relancé à chaque temps à ce tempo (Web Audio, `web/src/lib/retrig.ts`,
  fondu de 5 ms à chaque coupe), arrêt au relâchement ; sans tempo, Espace
  rejoue une fois.
- [7.L2] Tonalité par banque d'un live : champ `keys` du live
  (`lives.set_key`, texte libre de 12 caractères), route
  `POST /api/lives/{live}/key` ; dans le panneau du live, double-clic sur
  une banque pour la saisir, affichée entre parenthèses
  (`A-HALF (Fa m)`). Grille resserrée : noms de banque sur une ligne,
  tonalité abrégée si elle est longue, une ligne par sample dans la liste ;
  colonne Live élargie (au moins 320 px, puis partage 1 / 1,3 avec la
  liste du milieu).
- [7.L2] Front des lives (`web/src/lib/LivePanel.svelte`) : bouton « Live »
  de la vue Samples, panneau en troisième colonne avec sélecteur et
  création de live, jauge de RAM du projet, grille banques × branches
  (plafond 64 en rouge), liste du dossier ou de la banque (écoute,
  renommage DT2 au double-clic, retrait par banque ou du live), export
  bilan puis copie vers `Live/00-live/<live>`. Ajout par glisser-déposer
  sur une banque ou `L` vers la banque active ; badge des banques du live
  sur les samples de la lib.
- [7.L1] Lives : `analyzer/lives.py` (live = `library/lives/<live>.json`,
  banques, samples du catalogue par banque et branche, `0-COMMON` pour un
  sample partagé, noms DT2 modifiables, pack du live pour les samples
  maison, RAM au format DT2 48 kHz / 16 bits, plafond 64 par dossier en
  avertissement) ; routes `/api/lives` ; export rejouable vers
  `<MEDIA>/Live/00-live/<live>/` (`paths.DT2_LIVES_DIR`), copie partagée
  avec l'export de la lib (`samples.sync`).
- [7.L] Doctrine de live `digitakt/doctrine-dt2-solaris.md` (set free party
  160-175 BPM, 6 banques, arborescence `00-live/solaris/` sur le +Drive),
  alignée sur la grille de `digitakt/doctrine.md` §1. Décisions
  7.L (lives : sélection de la lib par banque, `0-COMMON`, plafond 64 par
  dossier, jauge de RAM, export rejouable) arbitrées dans SPEC, à coder.

- [9.C2] Séquenceur acid étendu : 32 pas sur deux mesures (`Density` par
  mesure ; une séquence de 16 pas est complétée par sa répétition),
  `Steps` jusqu'à 32, repère ▶ / ◀ du pas de départ (`Offset`) ; lecture
  arrêtée après 1 à 8 mesures (`bars`, statut `done`) pour échantillonner ;
  mode **Arp** : arpège des triades de la gamme sur une progression
  (`I-VI-VII-I`, `I-IV-V-I`… via `GET /api/acid/progressions`), un accord
  par mesure ou demi-mesure, motif ↑ ↓ ↕ ou hasard ; 14 tests.
- [9.C] Vue « Acid · MIDI » du sound design (`web/src/lib/sd/AcidView.svelte`),
  ouverte depuis la colonne des traitements : Generate et graine, verrous
  par couche, potards de tirage (Type, Density, octaves : relancent leur
  seule couche, même graine) et de lecture (Steps, Offset, Accent, Gate,
  Swing, Transpose), Root, Scale, Direction, Tie ; grille 16 pas éditable
  (note : clic = joué / silence, molette ou flèches = degré ; accent, gate,
  octave : clic = valeur suivante ; slides marqués), pas joué surligné ;
  cible VST du Mac ou DT2, port, canal, BPM, CC de slide, Play / Stop,
  Panique ; modifications envoyées au tour suivant pendant la lecture ;
  réglages gardés dans le navigateur. Route `GET /api/acid/scales`.
- [9.B] Lecture temps réel des lignes acid (`scripts/acid_midi.py`) : cible
  DT2 (Start et horloge de la DT2, boucle, Stop = retour en attente) ou
  cible Mac (horloge interne 24 ppqn vers un bus IAC) ; nouvelle ligne
  prise au tour suivant, BPM immédiat ; slides en legato et CC de slide
  optionnel ; arrêt et panique (CC 123 sur les 16 canaux) ; routes
  `POST /api/acid/generate`, `POST|GET|DELETE /api/acid/play`,
  `POST /api/acid/panic` ; CLI ; 14 tests.
- [9.A] Moteur du générateur acid (`scripts/analyzer/acid.py`) : séquence
  de 16 pas en quatre couches (notes, accent, gate, octave) tirées par
  `generate`, une graine par couche (verrouiller une couche ne change pas
  le tirage des autres) ; `Type`, `Density`, `Accent`, `Gate`, `Root`,
  `Scale` (`harmony.SCALES`), `Transpose`, octaves bornées, `Steps`,
  `Offset`, `Direction` (avant, arrière, pendule), `Swing`, `Tie Mode`
  (slide = chevauchement, même note = prolongée) ; export `.mid` d'une
  mesure, CLI `python -m analyzer.acid` ; 23 tests.
- [7.D] Fiche KB `oneshots-synthe` (lot 3, n° 36) : one-shots mélodiques
  depuis un synthé (contraintes imposées par la DT2, réglages du synthé,
  note de référence et `TUNE`, longueurs, boucle FORWARD LOOP, tessiture
  par preset lock, accords parallèles, nommage des octaves Elektron).
- [7.D] Fiche KB `controleur-maschine` (lot 5, n° 35) : Maschine MK2 en
  mode MIDI (Controller Editor) vers la DT2, tout USB via le Mac sans DAW
  (routeur MIDI ou une ligne `mido`), notes sur l'AUTO CHANNEL ; tutos
  branchement, perc en LIVE avec la vélocité des pads, basse en STEP.
  Liée depuis l'index et `midi-config`.
- [7.D] Template Controller Editor `digitakt/maschine/DT2 Pads.ncm2`
  (Maschine MK2) : pads sur le canal 10, contrôles désactivés, 8 groupes
  (une note, chromatique, éolien, phrygien, dorien, mineur harmonique,
  phrygien dominant, penta mineure). Fiche `controleur-maschine` : import,
  tonalité réglée par `TUNE` sur la DT2.
  Groupe A remplacé par une page rythmique : notes 0-7 (pads 9-16 en
  doublon) = tracks 1-8 quelle que soit la track active (manuel §8.4,
  vérifié sur la machine). Port du routeur corrigé : `Maschine MK2 Virtual
  Input`.
  Couleurs des pads : page rythmique rangée 1 rouge, rangée 2 bleu,
  doublons sans couleur ; gammes avec tonique rouge, tierce
  jaune, quinte verte, reste à la couleur de la famille (blanc chromatique,
  bleu mineur, violet majeur), boutons GROUP idem. Pads en LED on = For
  MIDI Out : le pad frappé s'allume.
  Rangée du haut du groupe A en rouge ; couleurs de groupe reprises de
  l'export Controller Editor (`color-index`).
- [7.D] Fiche KB `enregistrement-quantize` : trois tutos (grille de bank en
  GRID ; basse en contretemps en STEP RECORDING, en STANDARD, JUMP et percs
  une par une avec `[FUNC] + [TRIG n]` ; perc jouée en LIVE puis calée par
  la quantize), gestes du STEP complétés depuis le manuel §10.2.4.
  Section « GRID ou STEP ? » : tableau de choix, accords (tracks MIDI,
  `NOT2`-`NOT4` ou clavier externe), enchaînement GRID → STEP → GRID.
- [7.D] Fiche KB `preset-pool` (lot 3, n° 34) : quatre cas d'usage en
  tuto (track Id qui change de son à chaque pas, variantes d'un même son,
  touches en pads de one-shots, palette du set multi-styles), quand le pool
  ne sert à rien (socle), proposition de rangement des slots à arbitrer.
  Liée depuis l'index et `presets-kits-pool`.
- [8.K] Courbe Color du Saturator, façon Live, en tête de la section
  Color : accentuation avant la courbe (étagère grave, nœud 1 = Freq Lo /
  Amt Lo ; aiguë, nœud 2 = Freq Hi / Amt Hi ; ±15 dB à ±100 %), au-dessus
  de 0 dB la bande sature plus. Glisser un nœud règle fréquence et
  quantité, double-clic les remet par défaut. `scale.shelfDb` (étagère
  grave ou aiguë) sert aussi au Low shelf.
- [8.E] Dossier de rangement d'un rendu au choix, avant le rendu : le
  `→ dossier` à côté du nom DT2 devient un menu (dossier proposé, ou tous
  les dossiers cibles groupés par branche) ; le nom proposé prend le code du
  dossier choisi (variation de kick en `DRUMS/RM/CLEAN` -> `RM V8 …`).
  Remis au proposé à chaque changement de traitement. API : `folder` sur
  `GET /api/sounddesign/target` et `POST /api/sounddesign/render` (422 si
  inconnu), `sounddesign.target(folder=)`.
- [8.D] Badge « versé » d'un rendu cliquable : ouvre la vue Samples sur
  son dossier (ex. `DRUMS/BD/CLEAN`), sample sélectionné et joué, sans en
  faire la source du sound design (il ne le devient que si on le
  resélectionne après un autre sample). `focus.show()` porte la demande ;
  `open()` de la vue Samples accepte un sample cible.
- [8.K] Courbe de transfert du Saturator dans le device, façon Live :
  entrée -1..1 en abscisse, sortie en ordonnée (plafonds ±1 et diagonale du
  son inchangé en pointillés) ; suit la courbe, le Drive, les potards WS, le
  Post clip, l'Output et le Dry/Wet (Color exclu : neutre sur un signal
  propre). Glisser verticalement règle le Drive (Maj = fin), double-clic le
  remet à 0 dB. Courbes portées de `saturation.py` dans
  `SaturatorCurve.svelte`, à tenir synchrones.
- [8.K] Device **Saturator**, émulation de celui de Live : 8 courbes
  (Analog Clip, Soft Sine, Bass Shaper, Medium, Hard, Sinoid Fold, Digital
  Clip, Waveshaper et ses 6 potards), Drive, Color (étagères grave / aigu
  avant la courbe, inverses après), Post clip Soft / Hard, Output,
  Dry/Wet, Hi-Quality ; automatisable. Les potards dépendant d'un
  sélecteur ne s'affichent que s'il les active (`active_when`) ; les
  sélecteurs des devices portent leur nom. Preset `variations/saturator_tints`.
- [8.K] Mode **Hi-Quality** du Dynamic Tube : courbe calculée à 4 × la
  fréquence d'échantillonnage (filtres anti-repliement à état, automation
  par blocs inchangée), 0,33 ms de latence.
- [8.K] Devices **Overdrive** et **Dynamic Tube**, émulations des devices
  de Live (`analyzer/saturation.py`) : passe-bande, saturation asymétrique
  de pédale, tonalité, dynamique, dry/wet ; lampe à modèles A / B / C dont
  le bias suit l'enveloppe (attaque / relâche), tonalité par pré- et
  désaccentuation. Automatisables (↗) comme les devices pedalboard ; preset
  `variations/tube_tints`, sections du notebook variations.
- [8.J] Forme d'onde dans le lecteur du sound design : boucle écoutée ou
  rendu du disque en lecture, tête de lecture animée, grille des tranches
  en variations.
- [8.J] **Layering** : couches en plus de la source (3 au plus), choisies
  dans la vue Samples par « + couche » (bandeau « Ajouter comme couche »,
  la source ne change pas pendant le choix). Chaque chaîne lit une couche
  (boîte « Source » en tête de ses devices) ; attaques calées
  automatiquement sur celle de la source (−30 dB de la crête) puis décalage
  ±50 ms ; gain de fin de chaîne (↗ gain) pour un mélange qui varie dans le
  temps ou d'une tranche à l'autre. API (`layers` de la requête, du sidecar,
  dans le hash), CLI `--layer`, preset `variations/layer_blend`, section
  Layering du notebook variations.
- [8.I] Traitement **variations** : jeu de variantes subtiles d'un one-shot
  (4 / 8 / 16 / 32 tranches égales dans un seul fichier, pour la machine
  GRID de la DT2 et CREATE RANDOM LOCKS sur `SLICE`) ; paramètres étagés de
  la tranche 1 à N par `params_end`, aléa reproductible, niveau égalisé.
  Presets `drive_tints` (overdrive) et `rumble_tints` (rumble dosé).
  Notebook [[sounddesign/variations]].
- [8.I] Un rendu de variations reste un son de la source : même code et
  même sous-dossier (`BD V8 C Punch dbr` en `DRUMS/BD/CLEAN`), sidecar avec
  `code` et `slices` ; versé avec le tag `slices`, que la réanalyse des
  samples exempte du contrôle « long ». `GET /api/sounddesign/target`
  accepte `slices`.
- [8.H] Preset riser `white_fall` (downlifter) : passe-bas qui se ferme de
  14 kHz à 150 Hz, volume et reverb qui tombent, courbe 0,5 ; environ
  −29 dB et plus d'aigus au-dessus de 4 kHz à la fin.
- [8.H] Vue Sound design : colonne latérale des traitements dépliables sur
  leurs presets, mini barre d'outils à icônes (nouveau preset vierge, nom et
  description, suppression) ; les sélecteurs de la barre disparaissent.
  API `DELETE /api/sounddesign/presets/{t}/{id}` (409 pour le dernier).
- [8.H] Automation dans le rack : bouton ↗ sous un potard d'un device
  pedalboard, second potard « fin » (`params_end`) ; le catalogue porte
  `automatable`.
- [8.H] Riser sans sample dans le front (« Bruit généré ») : écoute, nom
  proposé et rendu ; le traitement dit quand il demande un sample
  (`source_param` / `source_sample`).
- [8.H] Notebook [[sounddesign/riser]] (théorie, chaîne device par device,
  presets, usage DT2 avec FILL / NOT FILL, pièges).
- [8.H] Rendus : dossier de rangement (`folder`, ex. `FX/RISE`) affiché au
  versement au lieu de `DRUMS/RM` codé en dur.
- [8.G] Traitement **riser** (track 15, rangé en `FX/RISE`) : bruit blanc
  ou rose généré, ou sample en cours bouclé ; montée de hauteur en demi-tons
  (varispeed), courbe de montée, longueur de 1 à 16 mesures au tempo, arrêt
  net sur le temps. Presets `white_sweep`, `pink_thin`, `pad_lift`.
- [8.G] Automation des devices pedalboard : `params_end` (valeur atteinte en
  fin de rendu), rendu par blocs de 256 échantillons, interpolation
  géométrique des fréquences. Les presets sans automation gardent leur JSON
  (et le hash de leurs rendus).
- [8.G] API et CLI : `source` facultative quand le preset n'en demande pas
  (`POST /api/sounddesign/preview|render`, `GET /api/sounddesign/target`,
  `--source`) ; nom proposé `FX 150 Rise Noise`.

- [8.F] Mode « Un coup » du rumble (réglage `one_shot`, sélecteur Boucle /
  Un coup) : un seul kick et sa queue, sur une longueur en temps au tempo
  (`length_beats`, 1 par défaut : 60 / 150 = 0,4 s à 150 BPM), puis fondu
  de 20 ms. Une track DT2 étant monophonique, le kick suivant coupe la
  queue : la rendre en entier (5 à 8 s mesurés) ne servait à rien.
- [8.E] Le sound design s'applique au sample en cours de la vue Samples
  (« Changer dans Samples » y bascule). Nom DT2 proposé à partir de la
  source, code du traitement et tempo compris (`BD C Punch 01 dbr` →
  `RM 150 C Punch dbr`), modifiable (`--name` en CLI) ; il nomme aussi le
  fichier rendu (`<nom> <hash>.wav`). Nouveau code **RM** (rumble, track 2
  de la doctrine) en DRUMS : le versement écrit un override qui range le
  rendu en `DRUMS/RM/<sous-dossier du kick>` (`GET /api/sounddesign/target`).
- [8.D] Notebook rumble (`sounddesign/rumble.md` : théorie, chaîne device
  par device, presets, usage sur la DT2, pièges, ressources) affiché sous
  le rack, « ? » d'un device = sa section. Versement d'un rendu dans le
  pack `Samples/SoundDesign/` (bouton « Verser », `--verse` en CLI,
  `POST /api/sounddesign/verse`) suivi de la réanalyse : rangé en
  `LOOPS/BL`. Rendu markdown du vault factorisé (`web/src/lib/markdown.ts`).
- [8.C] Device « Filtre » façon Auto Filter (ladder pedalboard) : type
  LP / HP / BP en 12 ou 24 dB/oct (sélecteur), coupure, résonance, drive ;
  courbe à nœud x = coupure, y = résonance. Les passe-haut / passe-bas
  6 dB/oct (1er ordre, sans résonance possible) restent pour les coupes
  propres. `ParamSpec.choices` : paramètre discret affiché en sélecteur.
- [8.C] Vue « Sound design » du front, rack façon Ableton Live : potards
  (glisser, Maj fin, double-clic défaut), tranches de mixage par chaîne
  (fader, activateur = mute, solo d'écoute), devices avec activateur =
  bypass et courbe de réponse à nœud pour les filtres / EQ, édition de la
  chaîne (ajout, retrait, déplacement), presets enregistrer / enregistrer
  sous, choix de la source et écoute A/B, boucle Web Audio re-rendue à
  chaque réglage, liste des rendus.
- [8.B] Sound design, API `/api/sounddesign/...` : traitements et
  catalogue des devices pour le front, lecture et sauvegarde des presets
  du vault, écoute d'un preset édité sur un sample du manifeste (WAV en
  mémoire), écriture d'un rendu, liste et écoute des rendus.
- [8.A] Sound design, moteur et CLI (`sounddesign.py`,
  `analyzer/sounddesign.py`) : traitements par chaînes parallèles de
  plugins pedalboard (15 devices, dont `duck` et `width` maison), `bypass`
  par device, `mute` et gain par chaîne, rendu en boucle sans couture à
  48 kHz / 24 bits avec sidecar rejouable dans `<MEDIA>/SoundDesign/`.
  Premier traitement : rumble, avec trois presets JSON du vault
  (`library/sounddesign/presets/rumble/` : `deep`, `gritty`, `kick_rumble`).
  Dépendance `pedalboard`.

- [7.K] Bouton « Réanalyser » de la bibliothèque de samples : reconstruction
  en arrière-plan (`POST` / `GET /api/samples/rebuild`), écritures refusées
  (409) pendant le calcul, bilan candidats / retenus / hors plafond / non
  classés, suivi repris après un rechargement de la page.
- [7.K] Roue des notes : comptes sous le filtre de la barre et le kit ; les
  notes absentes du sous-ensemble sont blanches et non cliquables.
- [7.K] Filtre par tranche de tempo dans la vue de droite (à côté de la
  roue) : comptes du sous-ensemble filtré, tranches vides blanches, affiché
  seulement si des tempos sont connus. API : `bpms` dans le filtre,
  `GET /api/samples/bpms`.
- [7.K] Sous-dossier manuel dans l'arbre « Library » : « + » sur la ligne
  d'un code, rempli par rangement (`M`, glisser). `library/samples/folders.json`,
  `POST /api/samples/folders` ; chargé par l'API et `samples.py`. Sous un
  filtre d'instrument, les sous-dossiers vides du type restent visibles.
- [7.K] Vue par type des samples : un filtre d'instrument liste à
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
