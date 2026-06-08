---
tags: [sets, etude-de-cas, theorie-mix, camelot, dj]
date: 2026-05-30
generated-by: scripts/setbuilder.py
---

# Étude de cas : un build de 60 min vers MOLIY (peak final)

> Cette note est une étude de cas pédagogique sur un set généré par
> `setbuilder.py playlist --peak`. Le but : apprendre la théorie du mix
> harmonique et énergétique en lisant chaque transition de cette playlist
> concrète, comprendre pourquoi l'algo fait ces choix, et identifier ce
> qu'un DJ humain ferait différemment.

## Le set généré

Commande utilisée :

```bash
python setbuilder.py playlist \
    --peak "moliy_silent_addy_-_moliy_shenseea_skillibeng_silent_addy_shake_it_to_the_max_fly_remix" \
    --duration 60 --max-track 15
```

Algo : **greedy backward** depuis le peak, avec plancher d'énergie auto à
`peak - 2 crans`. Plus de détails : [[setbuilder]] (ou `scripts/README.md`).

| # | Time   | BPM   | Camelot | Energy  | Track |
|---|--------|-------|---------|---------|-------|
| 1 | T+0:00  | 117.5 | 12A     | low     | Quantic, Nidia Góngora — Muévelo Negro |
| 2 | T+7:00  | 123.0 | 2A      | medium  | Bagarre — Ring Ring |
| 3 | T+9:41  | 129.2 | 3A      | low     | JuL — Pow Pow |
| 4 | T+12:53 | 129.2 | 5A      | medium  | Polar Inertia — Hell Frozen Over |
| 5 | T+21:29 | 136.0 | 5A      | low     | Zero 7 — Destiny (feat. Sia) |
| 6 | T+25:16 | 136.0 | 5A      | low     | Brainbug — Nightmare |
| 7 | T+32:06 | 129.2 | 7A      | low     | Kybba, Blaiz Fayah & Konshens — Pon Di Ting |
| 8 | T+34:26 | 129.2 | 7A      | low     | Blaiz Fayah & Tribal Kush — Bad |
| 9 | T+37:03 | 123.0 | 7B      | low     | Kangding Ray — AMBER DECAY |
| 10 | T+43:40 | 129.2 | 8B      | low     | Maïcee — Twenty twenty |
| 11 | T+46:10 | 123.0 | 8A      | low     | REBRN — KOKA (Original Mix) |
| 12 | T+52:18 | 117.5 | 8A      | low     | BAD BUNNY — NUEVAYoL |
| 13 | T+56:01 |  99.4 | 9A      | low     | MONO/POLY — WHEN I'M COMIN FOR YA |
| 14 | T+58:06 |  99.4 | 7A      | low     | Two Fingers — 296 Rhythm |
| 15 | T+61:38 | 198.8 | 5A      | **high**| **MOLIY — Shake It To The Max (Fly) Remix** |

Allure générale : un long plateau low-energy 117–136 BPM, puis chute vers
99 BPM, puis **drop half-time** vers MOLIY 198 BPM en explosion d'énergie.

---

## Théorie nécessaire pour lire ce set

### 1. La Camelot Wheel — pourquoi les codes 5A, 8A, 12B, etc.

La Camelot Wheel est un système de numérotation des 24 tonalités musicales
(12 majeures + 12 mineures) organisé en cercle pour visualiser les relations
harmoniques :

- **Lettre A = mineur, lettre B = majeur**
- **Chiffres 1 à 12** : positions sur le cercle des quintes (chaque pas
  ajoute une altération à l'armure : C majeur 8B → G majeur 9B = +1 dièse,
  etc.)
- Les couples relatifs (même armure, mode différent) partagent le chiffre :
  C majeur 8B et A mineur 8A.

Pourquoi c'est utile pour mixer : deux morceaux dans des tonalités
**proches sur la Wheel** sonneront "ensemble" (pas de dissonance harmonique
audible). Deux morceaux **éloignés** créeront des dissonances pendant le
mix in/out.

**Règles de transition** (du plus fluide au plus tendu) :

| Type | Exemple | Effet |
|---|---|---|
| Même code | 5A → 5A | Tonalité identique, mix invisible harmoniquement |
| Même chiffre, autre lettre | 8A ↔ 8B | "Mood switch" : relatif majeur/mineur, change la couleur |
| ±1 même lettre | 5A ↔ 6A ou 4A | Quinte/quarte, transition la plus classique en harmonie |
| ±2 même lettre | 5A ↔ 7A ou 3A | "Energy boost mix" : pas dans le cycle des quintes, ça réveille |
| Autre | 5A → 11A | Risque de dissonance, à éviter ou à transitionner via un break |

### 2. Le mix BPM — direct, nudge, pitch shift, half-time

Beat matching, c'est aligner les beats de deux tracks. Plus les BPM sont
proches, plus c'est facile :

| Écart | Type | Pratique |
|---|---|---|
| ±3% (ex. 130 → 134) | Direct | Mix transparent à vitesse native |
| ±6% (ex. 130 → 138) | Tempo nudge | Léger pitch sur l'un ou l'autre, audible mais OK |
| ±10% | Pitch shift | Change la tonalité (utiliser key lock si dispo) |
| 2× ou 0.5× | Half-time / double-time | **Voir section dédiée plus bas** |

### 3. La courbe d'énergie d'un set

Structure macro classique d'un set de 60 min :

```
energy
  ^
  |                                    PEAK
  |                                  ___■___
  |                               __/       \__
  |                            __/             \
  |                         __/                 \__   outro
  |             build    __/
  |          ____      _/
  |   intro_/    \___/
  |__/                                                    > time
```

- **Intro** : warm-up, basse énergie, on installe la sonorité
- **Build** : progression d'énergie sur 30-45 min, plusieurs petites
  vagues
- **Peak** : 1-2 tracks d'apothéose, le moment qui justifie le set
- **Outro** : descente, on libère

Notre set généré place MOLIY en peak final → c'est un **"build straight to
peak"** sans outro. À toi de prolonger pour un set complet.

---

## Analyse transition par transition

Pour chaque transition, on regarde : **BPM**, **Camelot**, **énergie**, et
le **score algo**.

### 1 → 2 : Quantic (12A, 117 BPM, low) → Bagarre (2A, 123 BPM, med)

Score algo : `0.79`
- BPM : `+4.7%` = tempo nudge, OK
- Camelot : 12A → 2A = `+2 sur la roue` = **energy boost mix** (pas dans
  le cycle des quintes, mais pas dissonant non plus)
- Énergie : `low → medium` = pas mal pour démarrer un build

**Lecture musicale** : Quantic c'est de la cumbia électronique, Bagarre
c'est une french touch / pop électro. Le saut stylistique est large mais
le tempo et la clé permettent la jointure. **Un DJ humain** poserait
peut-être un EQ kill sur les basses de Quantic pendant que Bagarre rentre
pour adoucir le contraste rythmique.

**Alternative** : avec 12A en sortie, un mix en `12A → 11A` (-1 même
lettre = quinte) aurait été plus harmoniquement orthodoxe — mais on n'a
pas forcément un track 11A à 120 BPM low-energy dans la library.

### 2 → 3 : Bagarre (2A, 123, med) → JuL (3A, 129, low)

Score : `0.76`
- BPM : `+5%` nudge
- Camelot : 2A → 3A = `+1 même lettre` = **quinte parfaite**, la
  transition harmonique la plus classique. Aucune dissonance.
- Énergie : `medium → low` = léger creux, acceptable

**Lecture** : transition harmonique fluide. JuL c'est du rap marseillais,
sonorité plus brute que Bagarre. Le drop d'énergie est subtil.

**Théorie à retenir** : `+1 sur la même lettre`, c'est la pierre angulaire
du mix harmonique. Un set qui tourne uniquement en `+1`/`-1` sera toujours
musicalement cohérent (mais peut manquer d'énergie/surprise).

### 3 → 4 : JuL (3A, 129, low) → Polar Inertia (5A, 129, med)

Score : `0.86`
- BPM : `direct` (même tempo)
- Camelot : 3A → 5A = `+2 même lettre` = **energy boost**
- Énergie : `low → medium`

**Lecture** : Polar Inertia c'est de la techno hypnotique (label
Dement3d), structurée et profonde. Le `+2` Camelot apporte de l'énergie
sans casser l'auditeur. **C'est le moment où le set "commence vraiment"**
après une intro un peu disparate.

**Pour un DJ humain** : c'est aussi une bonne place pour un **long blend**
(2-4 minutes) puisque les deux tracks partagent le BPM exact. Tu peux
laisser deux couches tourner ensemble longtemps.

### 4 → 5 : Polar Inertia (5A, 129, med) → Zero 7 (5A, 136, low) — ⚠ point d'interrogation

Score : `0.81`
- BPM : `+5%` nudge
- Camelot : `5A → 5A` = même tonalité parfaite
- Énergie : `medium → low` = **chute** dans un build censé monter

**Lecture** : Zero 7 — Destiny (2001, feat. Sia avant qu'elle ne soit
Sia), c'est du **downtempo chillout**. Mettre ça en plein build à 136 BPM
casse le mouvement. L'algo l'a choisi parce que la clé matche parfaitement
(5A → 5A) et que le BPM colle, mais **musicalement c'est un breakdown
inattendu**.

**Choix DJ alternatif** :
- Garder le track mais l'utiliser comme **respiration intentionnelle**
  (intro/outro d'une phrase) — un "moment d'air" avant de repartir
- Le remplacer par un autre track 130-136 BPM en 5A energy medium ou high
  s'il en existe dans la library
- L'éjecter complètement et faire passer Polar Inertia plus longtemps

**Théorie à retenir** : un mix **harmoniquement parfait** peut être
**énergétiquement faux**. La Camelot ne dit rien sur la densité, le
groove, le rôle dramatique du morceau. L'algo regarde 3 dimensions (BPM,
key, energy label), un DJ entend 20.

### 5 → 6 : Zero 7 (5A, 136, low) → Brainbug — Nightmare (5A, 136, low)

Score : `0.96` — score parfait
- BPM : direct
- Camelot : même
- Énergie : maintenue

**Lecture** : Brainbug — Nightmare est un classique trance de 1996. Sortir
de Zero 7 (chillout 2001) pour rentrer dans Nightmare (trance hardcore
1996) sur la même clé et même BPM est techniquement excellent.
**Musicalement** : ça a du sens si on a utilisé Zero 7 comme breakdown
calme avant de relancer la machine avec Nightmare.

**Pour un DJ humain** : c'est exactement le genre de transition où tu
slammes le **kick de Nightmare** au moment où le break de Zero 7 finit.
Effet "comeback" puissant.

### 6 → 7 : Brainbug (5A, 136, low) → Kybba/Blaiz Fayah (7A, 129, low)

Score : `0.75`
- BPM : `-5%` nudge (légère décélération)
- Camelot : 5A → 7A = `+2 même lettre` = energy boost
- Énergie : low → low

**Lecture** : on quitte la trance pour du dancehall/afrobeats électronique
(Kybba). Le saut stylistique est grand, mais le `+2` Camelot fournit
l'énergie nouvelle dont on a besoin pour relancer. C'est une **transition
de genre** facilitée par l'harmonie.

### 7 → 8 : Kybba (7A, 129, low) → Blaiz Fayah & Tribal Kush — Bad (7A, 129, low)

Score : `0.96`
- Tout identique (BPM, clé). Mix parfait.

**Lecture** : deux tracks dancehall très proches stylistiquement, même
artiste central (Blaiz Fayah). C'est une **continuation thématique** plus
qu'une vraie transition. Tu peux les enchaîner direct.

### 8 → 9 : Blaiz Fayah (7A, 129) → Kangding Ray (7B, 123)

Score : `0.85`
- BPM : `-5%` nudge
- Camelot : 7A → 7B = **même chiffre, lettre opposée** = **mood switch**
  (mineur → majeur)

**Lecture** : Kangding Ray c'est de la techno expérimentale très différente
(label Raster-Noton). Le mood switch mineur→majeur **éclaire** le set —
typique transition utilisée pour amener un moment plus contemplatif. Vu
qu'on est en plein build, ce n'est peut-être pas le bon moment, mais
musicalement la transition est solide.

### 9 → 10 → 11 → 12 : longue séquence d'enchainements `+1` / `mood switch`

| # | Transition | Type |
|---|---|---|
| 9 → 10  | 7B → 8B | +1 même lettre (quinte) |
| 10 → 11 | 8B → 8A | mood switch maj→min |
| 11 → 12 | 8A → 8A | même tonalité |

**Lecture** : cette séquence (Kangding Ray → Maïcee → REBRN → BAD BUNNY)
parcourt le cycle des quintes en zigzag majeur/mineur. Très orthodoxe
harmoniquement, mais **stylistiquement éclaté** (techno expérimentale →
pop indé → tech-house → reggaeton). Le set reste cohérent en clé mais
perd en identité.

**Si tu jouais ce set** : tu réorganiserais probablement pour grouper les
morceaux par sonorité, quitte à sacrifier une `+1` harmonique parfaite
pour garder une cohérence de genre.

### 12 → 13 : BAD BUNNY (8A, 117) → MONO/POLY (9A, 99) — ⚠ score 0.41

Score : `0.41` — au seuil minimum
- BPM : `99/117 = 0.846` = **incompatible** dans notre algo (hors fenêtre
  pitch shift ±10%)
- Camelot : 8A → 9A = `+1 même lettre` (parfait)
- Énergie : low → low

**Lecture** : la chute de BPM est trop grande pour un mix beat-matché. En
pratique, **un DJ humain ferait un cut sec** (couper sur un drop ou un
silence) plutôt qu'un mix. Ou ajouterait un track intermédiaire 105-110
BPM pour faire le pont.

**Pourquoi l'algo l'accepte** : la clé est tellement bonne (+1) que le
score remonte malgré le BPM nul. C'est une limite de la pondération `0.5
bpm + 0.3 key + 0.2 energy` — la key seule peut "racheter" un mix BPM
impossible.

**Théorie à retenir** : le score algo agrège plusieurs dimensions mais
**ne modélise pas l'impossibilité physique** de mixer deux BPM trop
éloignés. À l'oreille c'est éliminatoire ; à l'algo c'est rachetable.

### 13 → 14 : MONO/POLY (9A, 99) → Two Fingers — 296 Rhythm (7A, 99)

Score : `0.82`
- BPM : direct (même tempo)
- Camelot : 9A → 7A = `-2 même lettre` = energy boost

**Lecture** : les deux tracks sont du hip-hop instrumental / breakbeat
slow (~100 BPM). Le `-2` Camelot est musicalement intéressant. **À 99
BPM** on est très loin de MOLIY (198), mais c'est **volontaire** : c'est
la rampe de lancement pour le drop half-time qui suit.

### 14 → 15 : Two Fingers (7A, 99, low) → MOLIY (5A, 198, high) — LE DROP

Score : `0.71`
- BPM : `198/99 = 2.0` exactement = **double-time** (half-time relationship)
- Camelot : 7A → 5A = `-2 même lettre` = energy boost
- Énergie : `low → high` = +2 crans = drop énergétique majeur

**Lecture** : c'est le moment-clé du set. **Tout ce qui précède était une
rampe pour ce drop.** Le saut de 99 à 198 BPM n'est pas une accélération
audible (le rythme principal reste perçu à 99 BPM, MOLIY simplement
empile 2× plus de subdivisions).

**Voir section dédiée ci-dessous sur le half-time.**

---

## Le drop half-time — pourquoi 99 → 198 ne casse pas le rythme

Le half-time / double-time mixing est un device standard en DnB, dubstep,
trap, et toute musique avec une structure rythmique densément
subdivisible.

**Principe physique** : si A est à 99 BPM et B à 198 BPM, alors les
**downbeats** (le "1" de chaque mesure) coïncident toutes les 2
mesures de A et toutes les 4 mesures de B. Le **pulse principal** que
ressent l'auditeur reste à ~99 BPM tant que B garde des accents lourds
toutes les 2 noires.

**À l'oreille pendant la transition** :

```
A (99 BPM) :   X . . . X . . . X . . . X . . .
B (198 BPM):   X . X . X . X . X . X . X . X .
                ↑       ↑       ↑       ↑
                Beats principaux qui coïncident
```

Le mix se sent comme un **doublement de densité rythmique** plus que comme
une accélération. C'est exactement l'effet "drop" qu'on cherche : la
basse continue son pulse, les hi-hats explosent.

**Pour le faire en live** :
- Caler le BPM analogiquement (99 × 2 = 198 ± 0.5%)
- Faire le mix sur un **break** de A (pour que B prenne le relais sans
  surcharge)
- Couper les basses de B au début du mix (laisser la basse de A), puis
  les rentrer brutalement au "1" de la mesure suivante

Notre transition `Two Fingers → MOLIY` est exactement ce schéma : Two
Fingers a beaucoup d'espace dans ses arrangements (hip-hop), MOLIY est
explosif dès l'attaque.

---

## Lecture critique du set et choix DJ alternatifs

### Ce qui marche

- **Plateau 123-136 BPM stable** (tracks 2-6) : bon ancrage rythmique, on
  peut faire des longs blends
- **Cycle des quintes propre** dans la deuxième moitié (8-12) : harmonie
  garantie sans réfléchir
- **Drop final half-time** : technique impressionnante, justifiée par la
  rampe de 99 BPM qui précède

### Ce qui est à revoir

| Moment | Problème | Choix DJ |
|---|---|---|
| Step 5 (Zero 7) | breakdown chillout au milieu du build | éjecter ou utiliser comme respiration intentionnelle de 1-2 min max |
| Steps 9-12 | identité stylistique éclatée (4 genres différents en 15 min) | regrouper par sonorité, sacrifier une +1 si nécessaire |
| Step 13 (BAD BUNNY → MONO/POLY) | gap BPM 117→99 impossible à mixer | cut sec ou track-pont à 108-112 BPM |
| Énergie générale | low quasi tout du long, pas de mini-pic intermédiaire | placer un track high-energy vers T+25 et un autre vers T+45 |

### Si tu re-jouais ce set comme humain

1. **Reduce stylistic spread** : choisir un fil (par exemple :
   "électronique slow → techno hypnotique → dancehall → half-time
   electronic → drop DnB") et écarter les tracks qui n'y rentrent pas
2. **Ajouter une bosse d'énergie intermédiaire** vers T+25 (un track
   high à 130-135 BPM dans la même clé) pour casser la monotonie low
3. **Prolonger Polar Inertia** (track 4) : c'est le meilleur track
   structurant du build. Le laisser jouer 5-8 min en blend avec ses
   voisins
4. **Préparer le drop** par un break audible de 16 mesures avant MOLIY
   (silence sur les basses, montée des hats)
5. **Garder un track-pont 110 BPM** entre BAD BUNNY et MONO/POLY pour
   éviter le cut sec

---

## Ce qu'il faut retenir pour ta pratique de DJ

1. **La Camelot Wheel donne un filet de sécurité, pas une recette**. Tu
   peux générer un set harmoniquement parfait qui n'a aucun sens
   musicalement. L'oreille décide en dernier.

2. **L'énergie n'est pas le BPM**. Two Fingers à 99 BPM (low-energy
   instrumental hip-hop) et MOLIY à 198 BPM (afro-dance explosif)
   peuvent avoir un pulse perceptif identique mais des énergies opposées.

3. **Half-time mixing est une signature**, pas un dernier recours. Quand
   tu maîtrises le passage 1× → 2×, tu peux construire un set entier
   autour de cette dynamique (DnB ↔ trap, par exemple).

4. **Un greedy local fait des choix surprenants**. Notre algo prend la
   meilleure transition pas-à-pas et peut atterrir dans des impasses
   stylistiques. Toujours lire le résultat avant de jouer.

5. **Plus la library est dense dans une plage BPM, plus le set est
   fluide**. Pour des sets DnB/tribe 175-200 BPM propres, il faudrait
   ajouter au moins 10-15 tracks dans cette plage. Notre playlist a
   atterri en half-time parce que c'était la seule façon d'atteindre
   MOLIY à 198 BPM depuis le reste de la library qui plafonne à 136.

6. **Les transitions de genre sont permises** mais pas gratuites : elles
   doivent être justifiées par une cohérence harmonique ET un moment
   dramatique (drop, breakdown, build). Un changement de genre en plein
   plateau cohérent est jarring.

7. **Toujours préparer le drop**. Un peak qui arrive sans build ne fait
   pas peak — il fait surprise. Notre set construit pendant 58 minutes
   pour que les 3 minutes finales de MOLIY aient du sens.

---

## Outil et limites de cette étude

Cette playlist a été générée par `setbuilder.py` (Phase 4 du projet
quality-analyzer). L'algo connaît :

- BPM (mesuré par librosa + corrigé à la main dans library.md)
- Clé (Camelot via parsing du champ `key`)
- Énergie (auto-inférée 1-5 depuis LUFS + BPM + crest factor)

L'algo ne connaît pas :
- La densité rythmique (un track 99 BPM peut sonner aussi dense qu'un
  140 BPM)
- Le contenu vocal (présence d'une voix change tout en mix)
- Le genre subjectif (l'étiquette "techno" vs "tech-house" vs "minimal"
  vs "industrial techno" ne fait pas la même musique)
- La structure interne (intro silencieuse, break à mi-track, double-drop
  final)
- Le contexte narratif d'un set (les moments-clés qu'un DJ humain
  construit consciemment)

Donc l'outil est un **assistant de pré-sélection**, pas un remplaçant.
La bonne utilisation : générer 5-10 candidats avec l'algo, puis curer à
l'oreille en gardant 30-50% du résultat.

#etude-de-cas #theorie-mix #camelot #dj #peak #half-time
