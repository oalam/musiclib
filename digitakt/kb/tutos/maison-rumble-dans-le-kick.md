---
tags: [digitakt, kb, tutos]
theme: Rumble fabriqué dans la track du kick (lock trigs, LFO one-shot, delay)
lot: 3
ordre: 1
source: "échange de travail du 2026-10-25"
auteur: Tom (idée), rédaction à vérifier à la machine
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-25
---

# Maison 1 — Rumble dans la track du kick

**En une phrase** : au lieu de resampler un kick réverbéré sur la track 2
(doctrine §9), on transforme la **queue sèche du kick lui-même** en rumble,
dans la track 1, en poussant l'overdrive et en fermant le filtre *après*
l'attaque, par lock trigs, par LFO one-shot ou par le delay.

Fiches des gestes : [[../parameter-preset-locks]] (lock trigs),
[[../lfo]] (modes `ONE` / `HLF`), [[../amp-overdrive-bitreduction]] (page FX),
[[../filtres]], [[../send-fx-compresseur]] (delay). Recette de référence :
[[../rumble-grave]] et [[../../doctrine]] §9.

## Sur notre grille

La track 1 garde le kick ; le rumble en est une **variation de queue**, pas
un son séparé. La track 2 reste libre pour le rumble resamplé de la
doctrine §9, ou reçoit la version resamplée de cette recette (recette 4).
Comme toute variation de la 1, elle sort du CTRL-ALL (doctrine §4) et se
pose avant le kit, dans le preset du kick.

## Le piège physique, avant de câbler

Un **lock trig** (trig jaune, `[FUNC] + [TRIG]`) ne déclenche rien : il
change les paramètres de la track au moment où le séquenceur le passe. Il
n'agit donc que sur ce qui **sonne encore** à cet instant.

- **La reverb est un envoi.** Le knob de send dose le signal *entrant* ;
  une fois le kick parti dans la reverb, monter le send sur le contretemps
  n'ajoute rien à la queue déjà en cours. Pour qu'un kick nourrisse la
  reverb, le send se locke **sur le trig du kick** (haut sur les kicks
  pleins, bas sur les ghosts). Et il n'y a pas de drive dédié sur le
  retour de reverb : seuls son `HPF` / `LPF` foncent la queue ; le seul
  drive en aval est l'overdrive master du mixer, qui tape tout.
- **L'overdrive et le filtre sont inline.** Là, un lock trig agit, à
  condition que le kick ait encore un **corps** à saturer : il faut un
  `DEC` (AMP) long ou un `REL` qui porte jusqu'au temps suivant. Avec un
  kick court, il n'y a plus rien à transformer.

Ce qu'on obtient est une queue de kick distordue et filtrée : plus sèche,
plus « sub tenu », très tribe. Ce n'est pas la reverb saturée de la chaîne
[[../../../sounddesign/rumble]], plus dub.

## Recettes

### 1. Lock trigs sur la queue sèche

- **Résultat** : à chaque kick, la queue se sature et se ferme sur le
  contretemps, puis le kick suivant remet la track à ses valeurs.
- **Pas à pas** :
  1. Track 1, page AMP : allonger `DEC` (ou `REL`) jusqu'à ce que le kick
     porte encore au 3e seizième. Page FLTR : machine LOWPASS 4, `FREQ`
     ouvert, un peu de `RESO`.
  2. `[RECORD]`, poser un lock trig (`[FUNC] + [TRIG]`) au pas 3 (et 7, 11,
     15 pour un kick en noires).
  3. Maintenir ce trig jaune, tourner `OVER` (page FX) vers le haut et
     `FREQ` (page FLTR) vers le bas ; les valeurs tiennent jusqu'au prochain
     trig rouge, qui remet les valeurs par défaut du preset.
  4. Page FX, `OD.RT` = PRE : l'overdrive passe **avant** le filtre, qui
     retire ensuite les harmoniques aiguës créées par la saturation (même
     ordre que la chaîne de [[../../../sounddesign/rumble]]).
  5. Doser `FREQ` pour que la queue ne monte pas dans les médiums
     (doctrine §9, partage des fréquences).
- **Attention** : le lock trig s'applique aussi à un ghost kick posé entre
  deux temps ; poser les locks après les ghosts ou locker `DEC` court sur
  les ghosts.
- **Chez nous** : les lock trigs prennent une **condition** (`COND`,
  [[../fill-conditions]]). Un rumble qui n'apparaît qu'en `FILL` ou en
  `2:4` est un bouton de tension gratuit.

### 2. LFO one-shot à la place des lock trigs

- **Résultat** : même mouvement, mais continu et relancé à chaque kick ;
  rien à reposer si la grille change.
- **Pas à pas** :
  1. `[MOD]` LFO 1 : `DEST` = FLTR `FREQ`, `WAVE` = EXP, `MODE` = `ONE`,
     `DEP` positif. Régler le `FREQ` de base à la valeur **fermée**
     (celle du rumble) : l'EXP ouvre le filtre à l'impact puis le laisse
     retomber.
  2. LFO 2 : `DEST` = FX `OVER`, `WAVE` = EXP, `MODE` = `ONE`, `DEP`
     **négatif**, `OVER` de base à la valeur **haute** : la saturation est
     retenue à l'impact et revient quand le kick a dégonflé. Un peu plus
     lent que le LFO 1.
  3. Durée : `SPD` × `MULT` = 128 donne un cycle de 16 pas
     ([[../lfo]]). Un cycle d'un temps (4 pas) = 512 (`SPD` 32 × `MULT`
     16), de 2 pas = 1024 (`SPD` 64 × `MULT` 16).
  4. Variante : `WAVE` = TRI, `MODE` = `HLF` (un demi-cycle, donc un
     balayage dans un seul sens) ; la durée effective est la moitié du
     cycle, doubler `SPD` ou `MULT`. `SPH` fixe le point de départ.
  5. `FADE` à 0.
- **Attention** : `LFO.T` (page TRIG 1) décide si un trig relance le LFO ;
  il se locke par trig. *À vérifier à la machine* : si un lock trig jaune
  avec `LFO.T` ON relance aussi le LFO, le mettre à OFF sur les trigs
  jaunes pour qu'ils ne cassent pas la descente. `FLT.T` fait de même pour
  l'enveloppe de filtre.
- **Chez nous** : `DEP` à 0 locké sur les ghost kicks, pour qu'ils ne
  déclenchent pas de rumble ; `DEP` ou `SPD` différents sur le 1er et le
  3e temps.

### 3. Delay comme générateur de rumble en contretemps

- **Résultat** : le kick ressort filtré à contretemps, sans toucher à son
  enveloppe ; le vieux « rumble on the off-beat ».
- **Pas à pas** :
  1. Page DELAY : `TIME` = 16 (l'unité est le 1/128 de mesure, 16 = une
     croche), `FDBK` modéré, `LPF` du delay bien bas, `HPF` contre l'infra.
  2. Track 1, page FX : send delay sur les kicks pleins seulement
     (lock bas sur les ghosts).
  3. Combiner avec l'overdrive de la track (recette 1 ou 2) : la répétition
     filtrée est saturée avec le kick.
- **Attention** : le delay est un envoi partagé comme la reverb ; tout ce
  qui y est envoyé répète à la croche. Réserver le delay au grave ou
  garder la reverb pour le reste.
- **Chez nous** : le delay a son **propre filtre**, contrairement à la
  reverb ; c'est ce qui rend cette variante jouable sans resample.

### 4. Figer en sample

Quand une combinaison plaît : muter tout sauf la 1, `[SAMPLING]`, `SRC` =
MAIN, `R.LEN` = 4 (un temps) ou 16, retailler pour garder la queue, poser
sur la track 2 ([[../sampling-resampling]]). On retrouve la liberté de la
track kick et la stabilité d'un sample, la recette de la doctrine §9 reprend
à l'étape 3 (sculpter, accorder).

## À essayer (5 min)

Même kick, deux versions au même niveau : recette 1 (lock trig au pas 3) et
recette 2 (deux LFO en `ONE`). Comparer au casque la tenue du sub entre deux
kicks, puis ajouter la basse en contretemps (track 9) et garder celle qui
lui laisse de la place.

## Liens

[[../rumble-grave]] · [[../lfo]] · [[../parameter-preset-locks]] ·
[[../fill-conditions]] · [[../amp-overdrive-bitreduction]] ·
[[../send-fx-compresseur]] · [[../sampling-resampling]] ·
[[../../../sounddesign/rumble]] · [[../../doctrine]] §4, §9
