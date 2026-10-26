---
tags: [digitakt, kb, tutos]
theme: Un morceau entier sur un seul pattern, six sections aux mutes (Wolkenhauer)
lot: 1
ordre: 3
source: "https://www.elektronauts.com/t/turning-a-daw-track-into-a-digitakt-live-performance-tutorial-how-to/42056"
auteur: Olaf Wolkenhauer (Elektronauts)
modele: DT1
duree: "fil écrit, premier post et post 8 de l'auteur"
publie: 2017-07-14
statut: draft
updated: 2026-10-26
---

# Session 3 — Un morceau entier sur un seul pattern (Wolkenhauer, 2017)

**En une phrase** : un morceau de 19 pistes de DAW ramené sur les 8 tracks
d'une Digitakt I et joué en live sur **un seul pattern**, dont la forme
(intro, transition, break percussif, boucle principale, break fill, break
mélodique, outro) n'est faite que de mutes, de conditions `FILL` /
`NOT FILL` / `3:3` / `1ST` et de one-shots lancés aux touches de track.

Source écrite, pas vidéo : la seule session complète trouvée qui traite la
**progression par phrases avec les seuls mutes et conditions** d'une
Digitakt ([[../../veille-theorie]] §F). Fiches des gestes : [[../mutes]],
[[../fill-conditions]], [[../parameter-preset-locks]],
[[../microtiming-retrigs]]. Le *pourquoi* : KT9
[[../theorie/kt-phrasage-tension]], [[../../doctrine]] §2, §4, §6.

## Cadre

- Digitakt I, OS de 2017, 8 tracks audio, un pattern de 4 pages (64 pas).
- Deux problèmes nommés par l'auteur. **Vertical** : 19 pistes à faire
  tenir sur 8 tracks, résolu en superposant un élément aigu sur un
  enregistrement grave dans le même sample (kick + hat fermé + shaker)
  puis en les séparant au filtre, et en faisant **partager une track** à
  deux sons par `FILL` et `NOT FILL`. **Horizontal** : faire vivre le
  morceau dans le temps avec un seul pattern, résolu par les mutes, les
  conditions et les p-locks.
- Exports : pistes solo, master resamplé (effets compris), clips d'un quart
  de mesure, 48 kHz mono ; les boucles de 4 mesures (basse, pluck, lead)
  qu'il qualifie lui-même de « paresseuses ».

## Layout de l'auteur

| Track DT1 | Contenu | Sur notre grille (doctrine §1) |
|---|---|---|
| 1 | kick + hat fermé + shaker (un sample, séparés au filtre) | 1 kick, 6 hat fermé, 4 perc : trois tracks, plus besoin de superposer |
| 2 | basse + bruit, boucle de 4 mesures | 9 basse ; le bruit sur la 15 |
| 3 | ride seule / ride + hat ouvert | 8 ride, 7 hat ouvert |
| 4 | percs 1 et 2 + clap, par sample locks | 4 perc, 3 clap |
| 5 | vocal FX (4 mesures) / impact | 15 FX de transition |
| 6 | violon 1 (1 mesure) / violon 2 (4 mesures), riser | 13 Id2 ; riser sur la 15 |
| 7 | pluck, boucle de 4 mesures | 14 Id3 ou 10 |
| 8 | lead, boucle de 4 mesures | 10 lead |

Logique de placement : kick et lead aux extrémités (1 et 8), basse à côté
du kick, percs au milieu, synthés près du lead. Sur 16 tracks le problème
vertical disparaît ; ce qui reste transposable est le **partage d'une
track par condition** (pour la 15) et toute la partie horizontale.

## Tricks

### 1. Deux sons sur une track : `FILL` contre `NOT FILL`

- **Track / instrument / pas** : track 1, kick + hat + shaker sur 1, 5, 9,
  13 en `NOT FILL` ; hat + shaker seuls sur 2, 6, 10, 14 en `FILL`,
  micro-timés vers la gauche pour tomber sur le temps. Même chose track 3 :
  ride + hat ouvert sur 1, 5, 9, 13 en `NOT FILL`, ride seule sur 3, 7,
  11, 15 en `FILL`.
- **Geste** : tenir `[PAGE]` et le kick disparaît, le hat continue ; le
  break percussif tient dans une touche.
- **Pourquoi** : le trig conditionnel choisit entre deux samples sur la
  même track, sans mute et sans second pattern. Les trigs `FILL` sont posés
  sur les pas **voisins** et ramenés par micro-timing : deux conditions à
  la même position.
- **Chez nous** : la 15 porte ainsi un riser (`FILL`) et un impact
  (`NOT FILL`) sur la même track ; pour kick et hat on a les tracks
  séparées, le `NOT FILL` sur le kick suffit (doctrine §5, riser + fill).
  Fiche [[../fill-conditions]].

### 2. Clap un cycle sur trois

- **Track / instrument / pas** : track 4, clap sur 5 et 13 en `3:3`, et sur
  la page 3 aux pas 5, 8, 13.
- **Geste** : rien, la condition joue seule.
- **Pourquoi** : un élément qui n'apparaît qu'un tour sur trois allonge la
  période perçue au-delà du pattern ; le motif de 4 mesures est entendu
  comme une phrase de 12.
- **Chez nous** : c'est le principe « un pattern main écrit pour 4 tours »
  (doctrine §2), en `A:4` plutôt qu'en `A:3` pour rester sur des phrases
  de 32.

### 3. Impact au premier passage seulement

- **Track / instrument / pas** : track 5, impact de 4 mesures en `1ST` au
  pas 1 (ou 2 micro-timé, le post se contredit), vocal FX en `NOT 1ST` sur
  le même pas.
- **Geste** : la bascule vers la boucle principale fait jouer l'impact une
  fois ; les tours suivants jouent le vocal.
- **Pourquoi** : le drop a son coup d'entrée sans qu'on le lance à la main.
- **Attention** : sur son OS, `1ST` ne se **réinitialise pas** en
  resélectionnant le pattern, seul un reload de projet (six clics) le
  relance ; l'auteur proposait `[FUNC] + [NO]` comme geste. *À vérifier
  sur la DT2 OS 1.17* : si `1ST` repart au changement de pattern, le
  problème est réglé ; sinon, l'impact se pose en `LST` sur le pattern
  précédent ou se lance à la touche (trick 5).

### 4. Samples choisis par lock

- **Track / instrument / pas** : track 4, percs 1 et 2 et clap par sample
  lock sur chaque trig ; track 6, violon 1 d'une mesure au pas 1 de chaque
  page en `NOT FILL`, violon 2 de 4 mesures au pas 2 de la page 1 en `FILL`
  micro-timé.
- **Pourquoi** : une track porte un kit entier de percs, et la variante
  mélodique du break fill n'occupe pas de track.
- **Chez nous** : preset locks de la DT2 (fiche
  [[../parameter-preset-locks]]), même usage sur la 4 et la 9 (deux
  timbres de basse sur une ligne).

### 5. One-shots aux touches de track

- **Track / instrument / pas** : hors mode record, presser la touche d'une
  track joue son sample. Tenir la 4 donne un crash, la 5 un shout vocal,
  la 6 un riser (pression courte = balayage de bruit).
- **Geste** : les FX de transition se lancent à la main sur le 1, sans
  trig.
- **Pourquoi** : les transitions ne sont pas figées dans le pattern, et la
  main garde la décision du moment.
- **Chez nous** : la 15 en mode trig (`[TRIG]` en CHROMATIC ou direct),
  doctrine §5 ; avantage de la méthode à trigs `LST` : elle tombe juste
  sans viser (fiche [[../patterns-chaines]]).

### 6. Filtre et sends comme vie du pattern

- Passe-bas et résonance sur la track 1 pour doser hat et shaker ; le même
  filtre ferme le kick dans l'outro. Send delay sur ride, percs et pluck
  pour ajouter du rythme ; overdrive sur le lead à la boucle principale ;
  LFO sur le pan pour simuler la largeur stéréo perdue.
- **Chez nous** : un seul paramètre qui bouge par section (doctrine §6,
  principe 2) ; le pan par LFO est inutile sur la 1 et la 9 (mono sous
  120 Hz, KT5).

## Déroulé de la session : six sections, un pattern

Durées non données par l'auteur ; états des tracks DT1, « – » = mutée.

| Section | 1 kick+hat | 2 basse | 3 ride | 4 perc | 5 FX | 6 violon | 7 pluck | 8 lead | Gestes |
|---|---|---|---|---|---|---|---|---|---|
| Intro | kick+hat | basse+bruit | ride+OH | perc+clap, delay | – | – | – | – | crash à la touche 4 |
| Transition | idem | idem | idem | idem | – | violon 1 | pluck | – | riser 4 mesures touche 6 |
| Break percussif | **hat seul** (`FILL`) | idem | idem | perc | – | violon 2 | pluck | – | balayages de filtre sur les aigus |
| Boucle principale | kick+hat | idem | idem | idem | impact `1ST` puis vocal | violon 1 | pluck | lead, overdrive | tout démuté |
| Break fill (`[PAGE]`) | hat seul | idem | ride seule | perc+clap | vocal | violon 2 | pluck | lead | riser touche 6 |
| Break mélodique | – | basse+bruit | ride+OH | – | – | violon 1 | pluck | lead | crash touche 4, shout touche 5 |
| Outro | kick fermé au filtre | basse sans bruit | ride+OH, delay | perc, delay | – | – | pluck | – | filtre |

Lecture avec la doctrine §4 et la KT9 : la forme est une **partition de
mutes** sur un pattern plein, le drop est le retour du kick, les deux
breaks se distinguent par ce qui reste (percs contre mélodie), et l'outro
est une sortie par soustraction et filtre. La variation au tour est portée
par les conditions, la décision par les mutes : les trois étages de la
doctrine §6 principe 3, sur une machine de 2017.

## Ce qu'il laisse en suspens

- Les durées des sections, donc le phrasage lui-même : rien n'est dit sur
  les frontières de 16 et 32 ; la forme est juste, le compte est à l'oreille.
- Les boucles de 4 mesures pour basse, pluck et lead : il le dit, le
  séquenceur est sous-employé ; chez nous ces lignes sont écrites en trigs
  (KT21, KT11).
- La réinitialisation de `1ST` (trick 3).
- La perte de l'image stéréo et des détails aigus : sur une DT2 à 16
  tracks, le problème vertical n'existe plus.

## À essayer (5 min)

Pattern main plein de 8 mesures (doctrine §2). Hats de la 6 en `NOT FILL`
sur les temps, hat seul en `FILL` sur les pas voisins micro-timés ; kick en
`NOT FILL`. Tenir `[PAGE]` une mesure avant le 1 d'une phrase de 32 et
lâcher sur le 1 : le break percussif de Wolkenhauer, sans second pattern.
Puis la recette complète dans [[maison-progression-par-phrases]].

## Liens

[[_index]] · [[maison-progression-par-phrases]] · [[../mutes]] ·
[[../fill-conditions]] · [[../parameter-preset-locks]] ·
[[../microtiming-retrigs]] · [[../patterns-chaines]] ·
[[../theorie/kt-phrasage-tension]] · [[../../doctrine]] §2, §4, §5, §6 ·
[[../../veille-theorie]] §F
