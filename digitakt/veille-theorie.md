---
tags: [digitakt, veille, theorie, rythme, harmonie, curation]
updated: 2026-10-15
status: arbitré le 2026-10-15 (SPEC « Décisions 7.M »)
---

> **Arbitrage du 2026-10-15** : dossier `digitakt/kb/theorie/`, 19 KT sans
> regroupement, socle KT1-KT9 d'abord, passe `rhythm_signature` avant chaque
> KT, sources écrites seulement. Suivi dans [[kb/theorie/_index]].

# Veille — théorie musicale de la techno, style par style

Liste **candidate** issue d'une recherche web du 2026-10-15, à curer avant
rédaction des notes de KT (notes de transmission, comme
[[kt-banque-samples]]). But : poser les bases théoriques de la construction
rythmique et harmonique d'un morceau dans chaque style du live et des styles
connexes, avec des ressources pour approfondir et des exercices sur la DT2,
pour **enrichir le vocabulaire de musicien par la pratique**.

**Méthode et limites**

- Trois recherches parallèles (styles cœur du live, styles connexes,
  transversal rythme / harmonie / forme). Les patterns, tempi et modes
  viennent de la connaissance des genres, pas des sources : **à valider à
  l'oreille**.
- Statut des liens : `[V]` page ouverte et contenu lu ; `[R]` remontée par la
  recherche, non ouverte ; `[?]` existence seule. **Aucune vidéo n'a été
  visionnée** ; aucune URL YouTube n'est donnée, seulement des chaînes à
  chercher par nom.
- Le web ne documente presque pas la théorie du mental / acid core
  (Teksa, Crystal Distortion, 69db) ni Regis / Surgeon / Dozzy : pour ces
  styles, les fiches se construiront à l'oreille et par analyse de morceaux
  de la library (`scripts/analyze.py`, `groove.py`, `rhythm_signature.py`).
- Ce qui existe déjà dans le vault et ne doit pas être réécrit : machine
  côté [[kb/polymetrie]], [[kb/euclidien]], [[kb/keyboard-gammes]],
  [[kb/microtiming-retrigs]], [[kb/fill-conditions]], [[kb/rumble-grave]],
  [[kb/kick-mental-vst]], [[kb/slice-breaks]] ; doctrine §11 (tonalité,
  modes sur tonique fixe, progressions, Camelot) et §12 (Id) ; notebooks
  [[../sounddesign/rumble]] et [[../sounddesign/riser]] ; générateur acid
  9.A (`analyzer/acid.py`, gammes de `harmony.SCALES`). Une note de KT
  renvoie à ces fiches pour le *comment*, elle apporte le *pourquoi* et le
  vocabulaire.

Notation : 16 pas = 1 mesure 4/4 en doubles croches, `x` trig, `.` vide,
`X` accent. Numéros de tracks = grille de la [[doctrine]] §1.

---

## A. Socle transversal

### A1. Rythme : cellules, polymétrie, dissonance métrique

**Concepts**

- **Tresillo** `x..x..x.` (3+3+2, E(3,8)) : base du dembow, des kicks
  breakbeat, de la basse offbeat et du galop ; **cinquillo** `x.xx.xx.`
  (E(5,8)) ; **clave son** 3-2 `x..x..x...x.x...`, **rumba**
  `x..x...x..x.x...` ; **hémiole** 3:2 (`x.x.x.` contre `x..x..` sur 6 pas).
- **Euclidien E(k,n)** (Toussaint) : k attaques réparties au plus
  régulièrement sur n pas. E(3,8) tresillo, E(5,8) cinquillo, E(7,16)
  `x..x..x..x..x...`, E(4,7) `x.x.x.x`, E(3,12). La rotation d'un pas change
  la clave (3-2 devient 2-3).
- **Polyrythmie** (subdivisions concurrentes dans un même cycle : 3:2, 3:4,
  5:4) contre **polymétrie** (cycles de longueurs différentes qui dérivent
  et se réalignent au ppcm). La longueur de track de la DT2 fait de la
  polymétrie ; l'euclidien ou le micro-timing fait de la polyrythmie.
- **Dissonance métrique** (Krebs, repris par Butler) : *de groupement* (une
  ligne en 3 pas contre un kick en 4) ou *de déplacement* (motif décalé d'un
  pas). Le groove est la tension entre pulsation stable et événements qui la
  contrarient.
- **Backbeat** (2 et 4), **half-time** / **double-time** (même BPM, densité
  divisée ou doublée), **turnaround** (variation de fin de phrase),
  **ghost note** (vélocité faible qui texture sans accentuer), **swing**
  (50 % = droit chez MPC / Logic, 0 % chez Cubase / FL ; 66 % = ternaire),
  **microtiming** (Danielsen : décalages de quelques ms, et timbre de
  l'attaque, au-delà du pourcentage).

**Ressources**

- Toussaint, *The Euclidean Algorithm Generates Traditional Musical
  Rhythms* (Bridges 2005) : <https://cgm.cs.mcgill.ca/~godfried/publications/banff.pdf> `[?]` PDF présent, non extrait. Catalogue des E(k,n) mappés sur les rythmes traditionnels.
- Wikipedia *Euclidean rhythm* : <https://en.wikipedia.org/wiki/Euclidean_rhythm> `[V]` tableau des E(k,n) en notation `x.`.
- Wikipedia *Clave (rhythm)* : <https://en.wikipedia.org/wiki/Clave_(rhythm)> `[V]` son / rumba, 3-2 / 2-3.
- Wikipedia *Hemiola* : <https://en.wikipedia.org/wiki/Hemiola> `[V]`.
- Wikipedia *Tresillo (rhythm)* : <https://en.wikipedia.org/wiki/Tresillo_(rhythm)> `[V]`.
- Attack Magazine, Passing Notes *Polyrhythms* : <https://www.attackmagazine.com/technique/passing-notes/polyrhythms/> `[V]` 4/4 contre 6/8 sur grille de 48es, hats en 6/8 sur kick 4/4.
- Attack Magazine, *DAW & Drum Machine Swing* : <https://www.attackmagazine.com/technique/passing-notes/daw-drum-machine-swing/> `[V]` swing de Roger Linn, conventions de pourcentage.
- Ableton, *New Horizons in Music: Polyrhythms* (Adam Neely, Loop 2017) : <https://www.ableton.com/en/blog/new-horizons-music-polyrhythms> `[V]` polyrythmie comme perception.
- Groove Pizza (MusEDLab / NYU, Ethan Hein) : <https://apps.musedlab.org/groovepizza/> `[?]` cercle de pas pour voir la géométrie d'un groove. Blog Hein, étiquette groove-pizza : <https://www.ethanhein.com/wp/tag/groove-pizza/> `[R]`.
- Livres (catalogue vérifié, pas de PDF libre) : Butler, *Unlocking the Groove* (Indiana UP, 2006) ; London, *Hearing in Time* (OUP, 2004 / 2012) ; Danielsen, *Presence and Pleasure* (Wesleyan UP, 2006) ; Toussaint, *The Geometry of Musical Rhythm* (CRC, 2013).
- Chaînes YouTube à chercher par nom (non vérifiées) : Adam Neely (polymètre, groove), 12tone (harmonie, tension), Tantacrul.

**Sur la DT2**

1. Kick (1) en 16, hat fermé (5) en 12, perc A (7) en 5 : écouter 4 min
   sans toucher, repérer à l'oreille le point de réalignement (ppcm 240 pas
   = 15 mesures) et le `RESET` à 64 qui le force.
2. Banque de claves : E(3,8), E(5,8), E(7,16) sur 7, 8 et 6 ; rotation d'un
   pas de chacune ; comparer son 3-2 / 2-3 et rumba.
3. Micro-timing : hats 16 pas, décaler les pas pairs seuls (+ quelques
   ticks), puis les impairs, puis vélocité 30 sur un pas sur deux ; noter le
   seuil où le droit bascule en shuffle (cf. [[kb/microtiming-retrigs]]).

### A2. Harmonie et tonalité

**Concepts**

- Hauteur = **couleur** en techno : tonique tenue (drone, pédale), 1 à 3
  notes de ligne, **harmonic rhythm** lent (un accord toutes les 4 à 16
  mesures ; à 190 BPM, 8 mesures = 10 s environ).
- **Accordage du grave** : le kick est une sinusoïde de 40-60 Hz qui a une
  note (F1 = 43,65 Hz, G1 = 49,0 Hz, A1 = 55 Hz). Kick, rumble et basse sur
  la tonique ou la quinte (doctrine §11) ; un kick court et sec n'a pas de
  note, c'est alors la basse qui fixe la tonalité.
- **Modes** en A : éolien A B C D E F G (défaut techno) ; phrygien A Bb C D E
  F G (tension par la b2, acid core, hard techno) ; dorien A B C D E F# G
  (ouvert, dub) ; phrygien dominant A Bb C# D E F G (psy, oriental) ;
  mineur harmonique A B C D E F G# (sensible). Changer de mode sur la même
  tonique colore sans réaccorder le grave (doctrine §11).
- **Tensions** : seconde mineure (1 demi-ton, signature phrygienne), triton
  (6 demi-tons, instable, symétrique), **blue note** (b5 ajoutée à la
  pentatonique mineure A C D E G), chromatisme de passage, clusters,
  atonalité contrôlée (industrial).
- **Accords** : stabs min7 / min9 / min11 / sus4, quintes nues (power
  chord) ; **voicing** ouvert sans doublure grave (dub techno) ; track audio
  monophonique, donc accords par samples transposés ou une voix par track
  (doctrine §11).
- **Camelot** : même numéro, ±1, ou changement de lettre (relatif) ;
  système de `setbuilder.py` (SPEC Phase 4).

**Ressources**

- Ableton *Learning Music* : <https://learningmusic.ableton.com/> `[V]` accords, gammes, modes, voicings, inversions, septièmes ; gratuit, interactif.
- Ableton *Theory Hacks*, leçon 2 (Scale device, défi en phrygien dominant) : <https://www.ableton.com/de/classroom/support/theory-hacks/lesson-2/> `[V]`.
- Attack Magazine, Passing Notes (index) : <https://www.attackmagazine.com/technique/passing-notes/> `[V]` *Further Chords*, *5 Tips To Improve Your Synth Basslines*.
- Hooktheory Trends : <https://www.hooktheory.com/trends> `[V]` probabilités d'enchaînements d'accords (culture pop, écart attendu avec la techno) ; TheoryTab par mode : <https://www.hooktheory.com/theorytab> `[R]`.
- musictheory.net : <https://www.musictheory.net/lessons> `[V]` gammes, intervalles, métrique (pas de leçon sur les modes).
- Ethan Hein, *Chord pizzas* : <https://www.ethanhein.com/wp/2018/chord-pizzas/> `[R]` le même heptagone donne la gamme majeure sur la roue des hauteurs et le bell pattern sur la Groove Pizza : lien rythme / harmonie.
- Mixed In Key, *Camelot Wheel* : <https://mixedinkey.com/workflows/how-to-use-the-camelot-wheel/> `[R]`.
- Leçon *Phrygian* (Tomas George, CreativeLive) : <https://site.creativelive.com/class/music-theory-for-electronic-producers-tomas-george/lessons/phrygian> `[R]`.

**Sur la DT2**

1. Kick (1) et basse (9) calés sur F1, puis G, puis A : noter ce qui masque
   ou renforce le rumble (2) (cf. [[kb/rumble-grave]]).
2. Ligne de 8 pas sur 10 en pentatonique mineure ; remplacer une seule note
   par Bb (phrygien), puis Eb (triton), puis G# (sensible) ; quatre variantes
   enregistrées, comparer la tension (gamme fixée dans [[kb/keyboard-gammes]]).
3. Rythme harmonique : drone sur 11, tonique changée par p-lock de note
   toutes les 2, 8 puis 16 mesures ; noter quand ça sonne « progression »
   plutôt que « texture ».

### A3. Forme et tension

**Concepts**

- **Phrasage** 4 / 8 / 16 / 32 mesures ; tout changement tombe sur le 1
  d'une phrase. À 190 BPM : 16 mesures = 20 s, 32 mesures = 40 s.
- **Build** (densité rythmique et spectrale, retrigs de plus en plus
  rapides), **breakdown** (kick coupé), **drop** (retour kick + basse) ; en
  live, arrangement **par soustraction** (mutes) plus que par ajout.
- **Répétition et variation** : une seule variable qui bouge sur une boucle
  fixe vaut mieux que plusieurs changements simultanés (Butler : la forme
  comme processus).
- **Call and response** entre deux tracks (conditions 1:2 / 2:2, A:B),
  **turnaround**, **fill**, **densité spectrale** (l'énergie perçue dépend
  du spectre autant que du nombre de notes).

**Ressources**

- Butler, *Unlocking the Groove* (chapitres sur la forme : couches,
  boucles de longueur régulière, rôle du DJ).
- Attack Magazine, Beat Dissected (index) : <https://www.attackmagazine.com/technique/beat-dissected/> `[V]` ; dont *raw hypnotic techno like Silent Servant*, *techno like Dave Clarke*, *dark cinematic hypnotic techno* `[R]`.
- Dancecult (revue en accès libre, Huddersfield) : <https://dj.dancecult.net/> (déjà cité dans [[../refs/free-tek-sources]] ; site injoignable lors de la veille, passer par DOAJ).
- Attack Magazine, *The Secrets of Techno Production* (livre, payant) : <https://store.attackmagazine.com/products/the-secrets-of-techno-production> `[R]` meilleur point d'entrée écrit sur les sous-genres.

**Sur la DT2**

1. Build en soustraction : pattern complet, couper une track toutes les 4
   mesures jusqu'au kick seul, tout remettre sur le 1 d'une phrase de 16 ;
   compter à voix haute (cf. [[kb/mutes]]).
2. Un clap en `1:4`, un en `3:4`, un en `FILL` : une mesure devient une
   phrase de 4 (cf. [[kb/fill-conditions]]).
3. Appel sur 13 en `1:2`, réponse sur 14 en `2:2`, retrig croissant 1/8,
   1/16, 1/32 en fin de phrase comme turnaround.

---

## B. Styles cœur du live

### B1. Tribe / tribecore / hardtek

- **Tempo** : free tekno 150-185 (Wikipedia) ; tribe et hardtek 160-180 ;
  180-200 = haut de fourchette, côté mental / frenchcore.
- **Signature** : kick « bouncy » à **pitch envelope** audible (descente
  rapide vers la fondamentale), peu distordu comparé au gabber ; toms graves
  accordés et percussions en **call and response** ; hats en léger shuffle
  (50-56 %) ; samples vocaux et filmiques en **points d'orgue**.
- **Patterns** (à valider) : kick `x...x...x...x...` ; offbeat
  `..x...x...x...x.` ; toms `...x..x.....x.x.`.
- **Basse / mélodie** : sub court ou kickbass en contretemps, riff de 1-2
  notes ; quasi atonal ou pentatonique mineure sur une tonique.
- **Structure** : plateaux de 8-16 mesures, un élément entre ou sort par
  phrase ; live de 20 min en 4-6 plateaux.
- **Vocabulaire** : tribe kick, pitch envelope, offbeat, call and response,
  shuffle, plateau, drop-out, sample hook.

**Ressources** : Wikipedia *Free tekno* <https://en.wikipedia.org/wiki/Free_tekno> `[V]` ; *Spiral Tribe* <https://en.wikipedia.org/wiki/Spiral_Tribe> `[V]` ; DJ Mag, histoire de Spiral Tribe <https://djmag.com/features/history-spiral-tribe-uks-most-notorious-travelling-sound-system> `[R]` (403 anti-bot) ; Maelstrom, 10 hymnes de teknival <https://dmy.co/news/the-10-best-teknival-anthems-according-to-maelstrom/> `[R]` ; forum Renoise, kick gabber en couches <https://forum.renoise.com/t/making-gabber-kicks-and-making-them-not-take-over-your-mix/44325> `[V]` (click, corps, sub 50 Hz, filtrage de la queue). Rien d'écrit sur Heretik, Keja, Tekno Mental : voir [[../refs/free-tek-sources]] et [[../inspirations/sets]].

**Sur la DT2** : kick à pitch env. marquée (p-lock de hauteur ou LFO court
sur TUNE) ; deux toms sur 7 en 12 pas contre le kick en 16 ; vocal sur 12 en
`1:8` ou `1:16` ; hats de 5 décalés de 5-15 ticks puis à 0 pour comparer.

### B2. Acid core / mental

- **Tempo** : 170-200.
- **Signature** : kickbass accordé sur la tonique (queue qui joue la note),
  distordu ; acid line 303 dans le médium (500 Hz-2 kHz) ; basse en
  contretemps.
- **Patterns** (à valider) : kick `x...x...x...x...` ; basse
  `..x...x...x...x.` ; acid `X.xx.xx.X.xx.xx.` avec slides sur les notes
  liées.
- **Acid line** : une voix, 16 pas, 3 à 5 notes distinctes, **accent**
  (volume + cutoff), **slide** (portamento jusqu'à la note suivante, bend
  avec saut d'octave), **env mod**, résonance ; longueur 13 ou 15 pas pour
  décaler le motif (MusicTech) ; saisir vite, sans réfléchir.
- **Harmonie** : mineur naturel ou phrygien sur la tonique du kickbass ;
  b2 et triton en slide pour le sombre.
- **Structure** : narration par automation cutoff / résonance sur 16-32
  mesures, break acid seul, retour kick plein.
- **Vocabulaire** : accent, slide, résonance, env mod, kickbass, longueur
  impaire, distorsion en série (gain staging).

**Ressources** : Attack, *How to make an acid house bassline* <https://www.attackmagazine.com/technique/tutorials/how-to-make-an-acid-house-bassline/> `[V]` ; MusicTech, *Chicago-style acid bassline* <https://musictech.com/guides/essential-guide/how-to-create-a-chicago-style-acid-house-bassline> `[V]` (slides et accents d'abord, 13 / 15 pas) ; Attack, *30 years of acid* <https://www.attackmagazine.com/features/long-read/you-just-have-move-your-feet-30-years-acid/> `[V]` ; Wikipedia *Acid techno* <https://en.wikipedia.org/wiki/Acid_techno> `[V]` ; Attack Beat Dissected *Armando acid house* <https://www.attackmagazine.com/technique/beat-dissected/armando-acid-house/> `[R]` (note aiguë tous les trois 16es contre le 4x4) ; MusicRadar, guide TB-303 <https://www.musicradar.com/news/producers-guide-roland-tb-303> `[?]`. Rien de fiable sur Teksa, Crystal Distortion, 69db, Mat Weasel ; la page Wikipedia Mentalcore n'existe pas.

**Sur la DT2** : acid sur 10 avec 3 notes (tonique, b2, quinte), p-locks de
cutoff / résonance, accent = vélocité forte + cutoff haut, puis 15 pas contre
le kick en 16 ; kickbass (1) sur la tonique, acid une octave au-dessus,
tester un demi-ton de décalage ; break 8 mesures acid seule avec cutoff
montant. Générateur 9.A pour les tirages (vue « Acid · MIDI »).

### B3. Frenchcore / hardcore / gabber / bouncy

- **Tempo** : hardcore 160-200+ ; frenchcore 180-220 en set.
- **Signature** : kick dent de scie clippé (quasi carré, donc mélodique),
  **pitched kick** accordé sur la progression ; **offbeat bassline**
  distordue entre les kicks ; hoovers, screeches ; breaks en 3/4 ou 5/8
  (Wikipedia) et influences classiques.
- **Patterns** (à valider) : gabber `x...x...x...x...` ; frenchcore kick
  long + basse `.xxx.xxx.xxx.xxx` ; bouncy (reconstruction, à confirmer par
  analyse de morceaux) galop `x..xx..xx..xx..x`.
- **Harmonie** : mineur, progressions de 2-4 accords portées par le pitch du
  kick ; changement de tonalité par le kick lui-même.
- **Vocabulaire** : kick en trois couches (click / corps / sub), gating de la
  queue, offbeat bassline, pitched kick, galop, hoover.

**Ressources** : Wikipedia *Frenchcore* <https://en.wikipedia.org/wiki/Frenchcore> `[V]` ; Wikipedia *Hardcore (EDM)* <https://en.wikipedia.org/wiki/Hardcore_(electronic_dance_music_genre)> `[?]` ; forum Renoise (ci-dessus) `[V]` ; Ableton, *Sara Landry high-end hard techno* <https://www.ableton.com/en/blog/sara-landry-high-end-hard-techno/> `[V]` (kick construit en premier, distorsion multi-étages). **Aucune source écrite sur le bouncy techno 2022+ ni le bouncy kick frenchcore** : à documenter par analyse (`rhythm_signature.py` sur des morceaux de la library).

**Sur la DT2** : kick en trois tracks (1 click, 2 corps, 13 sub) avant
resample en un sample ; basse `.xxx` sur 9 avec kick long ; galop avec trigs
4, 7, 10 en `3:4` ; queue de kick alternée tonique / quinte toutes les 4
mesures par p-lock.

### B4. Hard techno moderne (150-160) et schranz

- **Signature** : **double kick** (kick court punchy sur le temps + kick
  rumble à longue queue, réverbéré, passe-bas, sidechain), hats offbeat,
  shaker 16es à vélocités variables, **pression** par la basse en contretemps
  ; acid ou lead polymétrique (ligne sur 3 mesures contre 4, Sara Landry).
- **Patterns** : kick `x...x...x...x...` ; rumble `.xxx.xxx.xxx.xxx` ; hat
  ouvert `..x...x...x...x.` ; shaker `xxxxxxxxxxxxxxxx`.
- **Harmonie** : atonal ou mineur sur une tonique.
- **Structure** : intro 16-32, plateaux de 16 ou 32, break 8-16, retour.
  Schranz et hard groove non sourcés.
- **Vocabulaire** : rumble, double kick, sidechain, offbeat hat, pression,
  gain staging, reverse kick.

**Ressources** : Attack Beat Dissected *Dark techno rumble* <https://www.attackmagazine.com/technique/beat-dissected/dark-techno-rumble/> `[V]` ; Ableton Sara Landry (ci-dessus) `[V]` ; Production Music Live, *rumbling techno kick (Johannes Menzel)* <https://productionmusiclive.com/blogs/news/6-steps-to-create-that-rumbling-techno-kick-you-love-with-johannes-menzel> `[R]` ; Sinee, *Next generation hard techno* <https://sinee.de/en/next-generation-hard-techno-how-to-make-a-track/HTMAT-007/> `[R]` payant. Doublon partiel avec [[../sounddesign/rumble]] et [[kb/rumble-grave]].

**Sur la DT2** : rumble (2) en `.xxx` passe-bas, avec et sans ducking ;
hats (5) micro-timing 0-10 ticks + `PRE` / `NEI` ; acid (10) en 12 pas
contre 16, écouter 3 cycles.

---

## C. Styles connexes

### C1. Dub techno

- **Tempo** : 118-135. Kick 4/4 doux, sidechain sur tout ; pas de sub
  séparé, le kick tient le grave.
- **Patterns** : kick `x...x...x...x...` ; hat ouvert `..x...x...x...x.` ;
  stab `..x.......x.....`, le delay fait le reste.
- **Harmonie** : un accord (parfois deux) pendant 16 à 64 mesures ; min7,
  min9, min11, maj7, sus ; **voicing ouvert** sans doublure grave ;
  tonalités courantes D#m, Fm, Gm, Am.
- **Techniques** : **delay pointé 3/16** (polyrythmie 3 contre 4 avec le
  kick), feedback 3-4 répétitions, **scoop** des médiums vers 600 Hz,
  passe-haut plutôt que passe-bas, tape echo, nudge des notes de l'accord.
- **Vocabulaire** : chord stab, dotted delay, feedback, voicing, scoop,
  sidechain, loose nudge.

**Ressources** : Attack Beat Dissected *Basic Channel-style dub techno* <https://www.attackmagazine.com/technique/beat-dissected/basic-channel-style-dub-techno/> `[V]` (145 BPM, accord D#m échantillonné, delays pointés) ; Attack Synth Secrets *Dub techno synth chords* <https://www.attackmagazine.com/technique/synth-secrets/dub-techno-synth-chords/> `[V]` ; Soundbridge, *techno chord* <https://soundbridge.io/techno-chord-sound-tutorial> `[R]` ; Gearspace, *chord sounds Basic Channel* <https://gearspace.com/threads/chord-sounds-basic-channel.521312/> `[R]`.

**Sur la DT2** : un sample d'accord sur 13 en 7 ou 11 pas avec delay 3/16,
kick en 16 ; stab en `1:4` avec cutoff baissé sur 32 mesures ; transposer
l'accord de +3 demi-tons sur un seul trig.

### C2. Techno hypnotique / loop / minimale

- **Tempo** : 125-140 (Dozzy, Mills, Hood, Surgeon). Kick monolithique ;
  le groove vient des hats, rims, percs.
- **Patterns** : percs en cycles 3, 5, 7 (`x..`, `x..x.`, `x.x..x.`) qui ne se
  recalent qu'au bout de 105 pas.
- **Harmonie** : modale et statique, une note ou un intervalle.
- **Techniques** : **arrangement soustractif**, **dubbing live** (mutes,
  sends, filtres joués comme un instrument), layering par bande de
  fréquence, **pattern shift** d'un pas, **microvariation** (une vélocité,
  un pas, jamais un nouveau motif), seuils de 8 / 16 / 32 mesures.

**Ressources** : Production Music Live, *hypnotic polymetric lead* <https://productionmusiclive.com/blogs/news/hypnotic-polymetric-lead-in-analog-melodic-techno-ableton-tutorial> `[V]` (motif de 7 notes sur grille 4/4) ; *how to make hypnotic tracks* <https://www.productionmusiclive.com/blogs/news/techno-music-production-how-to-make-hypnotic-tracks> `[R]` ; Sinee, *raw hypnotic techno* <https://sinee.de/en/raw-hypnotic-techno-how-to-make-a-track> `[R]` ; Attack Beat Dissected *Silent Servant* `[R]` (A3). Rien d'écrit sur Dozzy, Hood, Surgeon.

**Sur la DT2** : percs 7, 8, 6 en 5, 7, 9 pas, écouter 3 min ; set de 6
tracks joué aux mutes seuls sur un plan de 8 / 16 mesures ; une seule
variation `3:4` sur un rim.

### C3. Techno industrielle / Birmingham / Detroit / broken

- **Tempo** : 126-138 (Attack : industrial 126-130, UR *Final Frontier*
  138) ; Birmingham / broken 130-145.
- **Patterns** : 909 kick `x...x...x...x...`, clap `....x.......x...`, hats
  `..x...x...x...x.`, toms `...x..x....x..x.` ; **broken** kick
  `x..x..x...x..x..` (3+3+4+3+3, hémiole).
- **Harmonie** : phrygien / éolien, triton, seconde mineure, clusters ;
  Detroit garde des accords de synthé mineurs, cinématiques.
- **Techniques** : **tom interplay** (toms qui répondent au kick, UR,
  Mills), velocity ducking, bitcrush 6 bits, resampling, rolls.

**Ressources** : Attack Beat Dissected *Industrial techno* <https://www.attackmagazine.com/technique/beat-dissected/industrial-techno/> `[V]` ; *UR, The Final Frontier* <https://www.attackmagazine.com/technique/beat-dissected/underground-resistance-the-final-frontier/> `[V]` (808, toms, conga en écho 1/8 pointé) ; index techno Attack <https://www.attackmagazine.com/search/techno/page/2> `[R]`. Rien de vérifié sur Regis / Surgeon.

**Sur la DT2** : kick 3+3+4+3+3 sur 1 avec clap fixe sur 2 et 4 ; retrait
d'un trig de kick sur 2 mesures comblé par un tom sur 7 ; retrig 1/16 à
vélocité décroissante + bitcrush (cf. [[kb/amp-overdrive-bitreduction]]).

### C4. Electro / breakbeat

- **Tempo** : 120-135 classique, 130-150 moderne.
- **Patterns** : kick tresillo `x..x..x.x..x..x.` ; clave son 3-2 ;
  **electro bounce** kick `x.....x...x...x.` + clap `....x.......x...`.
- **Harmonie** : phrygien / éolien, nappes en quartes / quintes, basses FM
  à portamento.
- **Vocabulaire** : tresillo, cinquillo, clave, anticipation, ghost note,
  808 decay accordé sur la basse.

**Ressources** : Toussaint et Wikipedia (A1) ; arXiv, *On the Euclidean Algorithm: Rhythm Without Recursion* <https://arxiv.org/pdf/2206.12421> `[?]` ; Attack Beat Dissected *Punchy house* <https://www.attackmagazine.com/technique/beat-dissected/punchy-house/> `[R]` et *Deep afro house* <https://www.attackmagazine.com/technique/beat-dissected/deep-afro-house/> `[R]` (kick syncopé). Pas de tutoriel electro classique fiable.

**Sur la DT2** : kick en euclidien E(3,8) puis hat E(5,16) (cf.
[[kb/euclidien]]) ; clave sur 8 décalée d'un pas toutes les 4 mesures ;
fills de clap par retrig 1/8 en `A:B`.

### C5. Dubstep halftime et DnB / jungle

- **Tempo** : dubstep 140 (ressenti 70) ; DnB 170-175 (ressenti 85-87) ;
  jungle 160-175. **Passerelles** avec le live : 90 = moitié de 180 ; 140 =
  3/4 de 186,7 ; 175 voisin de 174-176.
- **Patterns** : dubstep kick `x...............`, snare `........x.......`,
  hats `x.x.x.x.x.x.x.x.` ou 3/16, swing 50 % (Mystik) ; DnB kick
  `x.........x.....`, snare `....x.......x...` ; **2-step** = second kick
  avancé avant le snare ; Amen (indicatif, original à 137 BPM) kick
  `x.x.......xx....`, snare `....x..x.x..x..x`.
- **Basse** : sub + médium (reese, wobble sync 1/4, 1/8, 1/8T), **sub / mid
  split** ; jungle : basse échantillonnée transposée vers E-G.
- **Harmonie** : mineur modal, 1-2 accords ; jungle : pads jazz / soul.
- **Structure** : intro, drop 16, break, retour ; **turnaround** toutes les
  8 mesures.
- **Vocabulaire** : half-time, 2-step, chopping, time-stretch, reese,
  wobble, ghost snare.

**Ressources** : Attack Beat Dissected *Mystik dubstep* <https://www.attackmagazine.com/technique/beat-dissected/mystik-dubstep/> `[V]` ; Ableton, *Beats Dissected* (présentation, dont Found Sound 2-Step) <https://www.ableton.com/en/blog/beats-dissected-diverse-drum-beat-tutorials-attack-magazine/> `[V]` ; EDMProd, *How to make jungle* <https://www.edmprod.com/how-to-make-jungle-music/> `[V]` ; MusicRadar, *6 jungle and DnB grooves* <https://www.musicradar.com/how-to/how-to-program-6-different-jungle-and-drum-n-bass-grooves> `[?]` paywall ; MusicRadar, *Amen-style break* <https://musicradar.com/tuition/tech/how-to-program-an-amen-style-break-637374> `[R]` ; Attack, *5/4 drum and bass (Machinedrum)* <https://www.attackmagazine.com/technique/video-tutorials/beat-dissected-5-4-drum-and-bass-inspired-by-machinedrum-using-loopcloud/> `[R]`. Complète [[../technique/patches/dnb]], [[../technique/patches/dubstep]] et [[kb/slice-breaks]].

**Sur la DT2** : tempo 90, halftime snare sur 3, puis 180 : même pattern,
ressenti changé ; Amen en 16 slices réordonnées avec `2:4` ; sub (9) en 12
pas contre kick 16.

### C6. Trance / hard trance / psytrance

- **Tempo** : trance 128-140, hard trance 140-150, psy 140-148, dark /
  forest 145-165.
- **Patterns** : kick `x...x...x...x...` ; **rolling bass**
  `.xxx.xxx.xxx.xxx` (trois 16es après chaque kick, jamais sur le temps,
  filtre mouvant) ; hats `..x...x...x...x.`.
- **Harmonie** : phrygien, phrygien dominant, mineur harmonique ; trance
  classique i-VI-III-VII ; psy : 1-2 notes de basse + **gated arp** 1/16.
- **Passerelle vers le mental** : rolling bass → basse offbeat frenchcore ;
  acid 303 commune ; monter de 150 à 180.

**Ressources** : Ableton Theory Hacks leçon 2 (A2) `[V]` ; Elektronauts, *psytrance kick bass parameters* <https://www.elektronauts.com/t/psytrance-kick-bass-parameters/253875> `[R]` ; forum Ableton, *rolling trance bass* <https://forum.ableton.com/viewtopic.php?p=1083205> `[R]` ; Sonic Pi, *psytrance loop* <https://in-thread.sonic-pi.net/t/psytrance-loop-bass-line-kick/8399> `[R]`. Pas de tutoriel écrit fiable sur le rolling bass.

**Sur la DT2** : basse (9) `.xxx` par temps, une note, pitch 1 / b2 / 1 / b3
; arpège 16 pas sur 10, gate court, phrygien dominant ; rolling bass à 150
puis 180 pour sentir le lien avec le tribe.

---

## D. Ressources transverses (tableau de bord)

| Ressource | Usage | Statut |
|---|---|---|
| Ableton Learning Music <https://learningmusic.ableton.com/> | modes, accords, voicings, structure | `[V]` |
| Ableton Learning Synths <https://learningsynths.ableton.com/> | synthèse interactive | `[?]` |
| Attack Beat Dissected <https://www.attackmagazine.com/technique/beat-dissected/> | un beat par style, en 16 pas | `[V]` |
| Attack Passing Notes <https://www.attackmagazine.com/technique/passing-notes/> | mélodie, accords, basses | `[V]` |
| Hooktheory Trends <https://www.hooktheory.com/trends> | enchaînements d'accords | `[V]` |
| musictheory.net <https://www.musictheory.net/lessons> | bases, intervalles | `[V]` |
| Ethan Hein <https://www.ethanhein.com/wp/> | groove, métriques impaires, Groove Pizza | `[V]` |
| Elektronauts, *Digitakt unofficial guide* <https://www.elektronauts.com/t/digitakt-unofficial-guide/40705> | conditions, humanisation | `[V]` |
| Elektronauts, *Digitakt II tips* <https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556> | idem DT2 | `[R]` |
| Butler, London, Danielsen, Toussaint (livres) | académique | catalogue |

---

## E. Notes de KT candidates

À cocher ensemble. Chaque KT : *En une phrase* ; *Signature* (tableau tempo
/ patterns 16 pas) ; *Vocabulaire* (termes définis) ; *Pourquoi ça marche*
; *Sur la DT2* (exercices de 5-10 min sur la grille de la doctrine, renvoi
aux fiches KB pour le geste) ; *Pièges* ; *Ressources* ; *Liens vault*.
Format et emplacement à arbitrer (voir questions en fin de note).

### Socle (priorité 1)

- [ ] **KT1 Cellules rythmiques** : tresillo, cinquillo, claves, hémiole,
  table E(k,n), rotation. Théorie derrière [[kb/euclidien]].
- [ ] **KT2 Polymétrie, polyrythmie, dissonance métrique** : ppcm, 3:4, 5:4,
  7:8, groupement / déplacement (Butler), tableau des cycles. Théorie
  derrière [[kb/polymetrie]].
- [ ] **KT3 Swing, microtiming, ghost notes, densité** : binaire / ternaire,
  pourcentages, vélocité, accents, conditions de trig comme outil de
  densité. Théorie derrière [[kb/microtiming-retrigs]] et
  [[kb/fill-conditions]].
- [ ] **KT4 Backbeat, half-time, double-time, passerelles de tempo** :
  90 / 180, 140 / 186, 175 ; comment un live à 190 ouvre vers DnB et dubstep.
- [ ] **KT5 Tonalité du grave** : kick / rumble / basse accordés, repères en
  Hz, kickbass, qui occupe quelle bande. Théorie derrière doctrine §11,
  [[kb/rumble-grave]], [[kb/kick-mental-vst]], [[../sounddesign/rumble]].
- [ ] **KT6 Modes de la techno** : éolien, phrygien, dorien, phrygien
  dominant, mineur harmonique ; formules, couleur, changement de mode sur
  tonique fixe. Théorie derrière [[kb/keyboard-gammes]].
- [ ] **KT7 Tensions et lignes** : pentatonique, blue note, seconde mineure,
  triton, chromatisme, atonalité contrôlée ; applicable à l'acid et aux Id.
- [ ] **KT8 Accords, voicings, rythme harmonique** : min7 / min9 / sus /
  quintes nues, voicing ouvert, accords sur track monophonique, harmonic
  rhythm, Camelot entre parties. Complète doctrine §11 « progressions ».
- [ ] **KT9 Phrasage et tension** : 4 / 8 / 16 / 32, build / breakdown /
  drop, soustraction, call and response, turnaround, durées à 190 BPM.
  Complète doctrine §6 et [[kb/mutes]], [[kb/patterns-chaines]].

### Styles cœur (priorité 1)

- [ ] **KT10 Tribe / hardtek** : tribe kick et pitch envelope, toms en call
  and response, samples en points d'orgue, plateaux.
- [ ] **KT11 Acid core / mental** : acid line 303 (accents, slides, octaves,
  longueurs 13 / 15), phrygien, kickbass, narration au filtre. Lien avec le
  générateur 9.A.
- [ ] **KT12 Frenchcore / hardcore / bouncy** : offbeat bassline `.xxx`,
  galop, pitched kick, kick en trois couches, breaks en 3/4 et 5/8. Bouncy à
  documenter par analyse de morceaux.
- [ ] **KT13 Hard techno et schranz** : double kick, pression, hats offbeat,
  ligne sur 3 mesures. Risque de doublon avec [[kb/rumble-grave]] : à
  cadrer sur la rythmique, pas le son.

### Styles connexes (priorité 2)

- [ ] **KT14 Dub techno** : accords et voicings, delay 3/16, scoop,
  évolution lente.
- [ ] **KT15 Techno hypnotique / loop** : soustraction, cycles 3-5-7,
  microvariation, dubbing live.
- [ ] **KT16 Industrial / Birmingham / Detroit / broken** : 3+3+4+3+3, tom
  interplay, clusters.
- [ ] **KT17 Electro / breakbeat** : tresillo au kick, electro bounce,
  clave. Fusion possible avec KT1 ou KT16.
- [ ] **KT18 Dubstep / DnB / jungle** : halftime, 2-step, Amen, chopping,
  sub / mid split. Complète les patches Tidal et [[kb/slice-breaks]].
- [ ] **KT19 Trance / psy** : rolling bass, gated arp, phrygien dominant,
  passerelle vers le mental.

### Questions à arbitrer

1. **Emplacement** : `digitakt/kt-*.md` (à côté de [[kt-banque-samples]])
   ou un dossier `theorie/` à la racine du vault, les KT n'étant pas
   propres à la DT2 ? Hub d'index à créer dans les deux cas.
2. **Granularité** : 19 KT (ci-dessus), ou regrouper les connexes en 3
   (dub + hypnotique, industrial + electro, dubstep + DnB + trance) ?
3. **Ordre de rédaction** : socle d'abord (KT1-KT9) puis styles, ou un
   style complet d'abord (KT10 tribe avec ses renvois au socle) pour
   valider le format à l'oreille ?
4. **Validation** : les patterns 16 pas sont des reconstructions. Faut-il
   une passe `rhythm_signature.py` / `groove.py` sur 2-3 morceaux de
   référence par style de la library pour ancrer chaque KT sur du réel
   avant rédaction ?
5. **Vidéos** : en lister (non visionnées, comme [[veille-live]]) ou s'en
   tenir aux sources écrites et aux livres ?

Liens : [[veille-live]] · [[doctrine]] · [[kb/_index]] ·
[[../refs/free-tek-sources]] · [[../inspirations/sets]] ·
[[../technique/patches/_index]]
