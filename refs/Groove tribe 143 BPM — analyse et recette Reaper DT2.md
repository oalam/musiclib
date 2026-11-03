# Groove tribe 143 BPM — analyse et recette Reaper / DT2

Nov 1, 2026 · @tom

Un extrait de live (21 s, enregistré au téléphone) à **143,25 BPM** en 4/4 : kick 4‑on‑the‑floor accordé sur A#1, stab de sub sur chaque contretemps une tierce mineure au‑dessus (C#2), charley fermé en croches avec le contretemps accentué. Le « roulement » du sub n'est ni un LFO ni un sidechain : c'est le battement à \~12 Hz entre la queue du kick (59 Hz) et le stab (71,75 Hz). Cette page sert de base à un tuto pour le reproduire sur Digitakt 2 et dans Reaper.

## Les quatre éléments

Trois sons séquencés, plus un phénomène acoustique qui naît de leur superposition. L'accordage global est \~40 cents au-dessus du 440 Hz ; les notes ci-dessous sont les plus proches.

| Élément | Hauteur | Placement | Durée | Timbre |
| --- | --- | --- | --- | --- |
| Kick | glisse de \~120 Hz à **59 Hz (A#1)** en \~110 ms, puis tient | chaque temps (steps 1, 5, 9, 13) | queue encore à −4 dB à 200 ms, audible jusqu'au temps suivant (\~400 ms) | sinus quasi pur après l'attaque ; clic d'attaque entre 400 Hz et 2 kHz |
| Stab de basse | **71,75 Hz (C#2)**, tierce mineure au-dessus du kick | chaque contretemps (steps 3, 7, 11, 15), \~15 ms en avance | \~150 ms | sub quasi pur, un peu de 2ᵉ/3ᵉ harmonique, attaque nette |
| Charley | bruit, centroïde \~1,6 kHz, énergie surtout 400–800 Hz | toutes les croches ; le contretemps 30 % plus fort et plus long | \~40 ms sur le temps, \~70 ms sur le contretemps | charley fermé sombre ou perc métallique filtrée |
| Battement du sub | 71,75 − 59 = **\~12 Hz** | de 180 ms jusqu'au kick suivant | 4 lobes par temps (\~85 ms d'écart) | pas un son : l'interférence des deux hauteurs précédentes |

Pas de snare ni de clap : les temps 2 et 4 ont exactement la même énergie que 1 et 3 dans les bandes 150–400 Hz et 1–4 kHz. Pas de charley ouvert dans le pattern : les queues de bruit retombent à −10 dB en 15 ms sur le temps comme sur le contretemps. Un seul événement aigu dans l'extrait, un crash ou open hat one-shot (\~250 ms) au 3ᵉ temps du break, mesure 4. Pas de contenu au-dessus de 8 kHz ailleurs, donc impossible de dire si le charley est sombre par choix ou par captation. À retenir pour le tuto : toute la tension vient du contretemps, et un clap sur 2 et 4 casserait le côté roulant.

## Grille 16 pas

Le cycle de base tient sur un temps et se répète quatre fois par mesure ; la mesure complète est donnée telle qu'on la programme sur la DT2 (X = fort, x = faible, . = rien).

```markdown
                 1 . . . 2 . . . 3 . . . 4 . . .
KICK             X . . . X . . . X . . . X . . .
STAB (C#2)       . . X . . . X . . . X . . . X .
CHARLEY          x . X . x . X . x . X . x . X .
```

Trois choses à retenir : rien ne tombe sur les 16ᵉ 2 et 4 (le « e » et le « a »), tout le contretemps (stab + charley) est légèrement en avance sur la grille, et c'est le contretemps qui porte l'accent, pas le temps.

## Chronologie d'un temps

À 143,25 BPM un temps dure 419 ms et un 16ᵉ 104,7 ms. Valeurs médianes sur 28 temps alignés au sample près (mesures 5 à 11) ; la régularité d'un temps à l'autre est quasi parfaite, tout est séquencé.

| Instant (ms) | Grille | Ce qui se passe |
| --- | --- | --- |
| −6 |  | le charley du temps démarre, juste avant le kick |
| 0 | step 1 | attaque du kick, pitch \~120 Hz, clic d'attaque |
| 50 |  | le kick passe \~82 Hz, charley du temps déjà éteint |
| 90–120 |  | le kick se pose sur 59 Hz ; c'est le maximum de niveau du sub |
| 105 | step 2 | rien de nouveau |
| 190–195 |  | charley du contretemps (fort) et stab C#2 démarrent ensemble, \~15 ms avant la grille |
| 209 | step 3 | position théorique du contretemps |
| 185 → 410 |  | battement : lobes du sub à \~185, 270, 345, 410 ms, espacement qui se resserre (85 → 65 ms) car la queue du kick continue à descendre légèrement |
| 314 | step 4 | rien de nouveau ; le stab est éteint vers 340 ms |
| 413 |  | charley du temps suivant |
| 419 | step 1 | kick suivant ; la queue du précédent est encore audible |

Les lobes du battement ne tombent pas sur les 16ᵉ (105, 209, 314 ms) : c'est le signe qu'ils ne sont pas séquencés.

## Le groove de basse : trois mécanismes

Le sub ne change jamais de note sur les 12 mesures : 59 Hz et 71,75 Hz sont présents sur chacun des 48 temps, même dans le break (10 dB plus bas). Le mouvement qu'on entend vient de trois choses qui se superposent.

1. **L'enveloppe de pitch du kick.** Le kick part \~1 octave au-dessus et glisse jusqu'à 59 Hz en \~110 ms, puis tient cette note avec un decay très long. C'est le kick lui-même qui fait office de sub tenu sur le temps ; il n'y a aucune note de basse séparée sur le temps ni sur le « e ».
2. **Un stab une tierce mineure au-dessus, sur le contretemps.** Court (\~150 ms), attaque franche, quasi sans harmoniques. Pendant \~200 ms il cohabite avec la queue du kick à niveau comparable.
3. **Le battement.** Deux sinus à 12 Hz d'écart produisent un tremolo à 12 Hz : c'est le « wobble » du sub. Il apparaît dès que le stab entre et dure jusqu'au kick suivant. Il n'y a ni LFO, ni sidechain, ni filtre modulé.

Ce que ça implique pour la reproduction : l'intervalle entre le kick et le stab **est** le réglage du groove. À l'unisson le sub devient lisse ; à la quinte (\~29 Hz d'écart) le battement devient une rugosité ; à la tierce mineure on obtient cette pulsation un peu plus rapide que les 16ᵉ qui fait rouler la basse sans être carrée. Et il faut que les deux queues se chevauchent : un kick à decay court tue l'effet.

## Arrangement sur les 12 mesures

Le pattern est le même d'un bout à l'autre ; le mouvement se fait par mutes, ghosts et niveau.

| Mesures | Ce qui change |
| --- | --- |
| 1–3 | pattern plein, sub à fond |
| 4 | break : sub −10 dB (toujours présent), kick amputé (`X x . . X . x x X . x . X . . x`), seul endroit avec un crash / charley ouvert |
| 5–6 | reprise plein pattern |
| 7–11 | le kick gagne des ghosts sur les 16ᵉ 2 ou 3 après le temps, densification progressive |
| 5 → 12 | le niveau du sub descend d'environ 7 dB (fader ou low-cut qu'on remonte) |
| 12 | temps 2 et 4 du kick affaiblis, 16ᵉ intermédiaires qui remontent : amorce de fill ou de transition |

## Recette Digitakt 2

Tempo 143 (ou 143,25 si on veut coller), pattern 16 steps, trois pistes. Les valeurs sont des points de départ à ajuster à l'oreille sur le sound system, pas des réglages exacts lus dans l'enregistrement. Unité de micro-timing : 1/384 de mesure, soit \~4,4 ms à 143 BPM.

| Piste | Trigs | Son | Réglages clés | Micro-timing |
| --- | --- | --- | --- | --- |
| 1 — Kick | 1, 5, 9, 13 | kick avec longue queue sinus, ou le one-shot `04_kick_seul` | TUNE pour que la queue se pose sur A#1 (59 Hz, ou B1 si on reste en 440) ; AMP decay long (la queue doit encore sonner à 350 ms) ; filtre LP pour n'avoir qu'un sinus après l'attaque ; si le sample n'a pas de glissando : LFO en mode trig ONE, forme EXP, destination TUN, depth négatif, vitesse pour \~100 ms de descente | 0 |
| 2 — Stab | 3, 7, 11, 15 | sinus pur ou le one-shot `06_stab_seul` | TUNE = note du kick + 3 demi-tons (C#2) ; AMP attack 0, decay \~150 ms, pas de sustain ; filtre LP ouvert juste assez pour l'attaque | −3 à −4 (\~15 ms en avance) |
| 3 — Charley | toutes les croches : 1, 3, 5, 7, 9, 11, 13, 15 | charley fermé, ou les one-shots `11` / `12` | filtre LP vers 3–4 kHz pour la couleur sombre ; VEL \~70 sur les temps (1, 5, 9, 13) et 110–127 sur les contretemps ; p-lock AMP decay plus long sur les contretemps (\~70 ms contre \~40) | −1 sur les temps, −3 à −4 sur les contretemps |

Points de méthode :

- Accorder le kick d'abord, puis le stab par rapport à lui. L'intervalle (tierce mineure) est ce qui fabrique le battement ; le tester à l'unisson, à la tierce, à la quinte, montre le phénomène mieux que n'importe quelle explication.
- Le battement ne se programme pas : il vient du chevauchement des queues. Si on ne l'entend pas, allonger le decay du kick ou monter le stab, pas ajouter un LFO.
- Break (mesure 4) : baisser le volume de la piste stab et du kick de \~10 dB plutôt que de les muter (le sub reste présent dans l'original), retirer des trigs de kick (garder 1 et 5, affaiblir le reste), ajouter un crash sur le step 1.
- Densification (mesures 7–11) : ghosts de kick sur les steps 2 ou 3 après chaque temps avec une trig condition (par ex. 25 % ou A:B) et une vélocité basse.
- Le fade du sub sur 8 mesures : un geste de fader ou de low-cut sur le kick + stab, à jouer en live.

Variante possible si on veut le groove sans le kick glissant : garder le kick court et mettre une vraie note de basse A#1 sur le step 1 avec un decay long. Le résultat est très proche et laisse plus de liberté sur le kick.

## Recette Reaper

Deux usages : reconstruire le pattern pour l'écouter et le démonter, et vérifier ses propres réglages DT2 contre l'original.

**Projet.** Tempo 143,25, grille 1/16, 4 pistes : Kick, Stab, Charley, et une piste Original avec `01_original_2mesures.wav` en référence (mutée par défaut). Un bus Sub où Kick et Stab envoient, avec un ReaEQ low-pass à 160 Hz qu'on active pour isoler le grave.

**Sons.** Le plus simple : ReaSamplOmatic5000 sur chaque piste avec les one-shots du zip (`04`, `06`, `11`, `12`), mode « Note (semitone shifted) » ; les samples sont déjà à la bonne hauteur, donc note de base = note jouée. Pour synthétiser plutôt que sampler : ReaSynth en sinus pur pour le stab (C#2, attack 0, decay 150 ms, sustain 0) et pour la queue de kick (A#1, release long) ; le glissando du kick est plus facile à obtenir en gardant un sample.

**MIDI.** Un item d'une mesure par piste, en boucle :

1. Kick : notes sur 1, 2, 3, 4 (chaque temps), vélocité fixe.
2. Stab : notes sur les « et », durée 1/16, puis sélectionner toutes les notes et les décaler de −15 ms (Nudge en ms, ou désactiver le snap et tirer).
3. Charley : notes sur toutes les croches ; vélocité \~70 sur les temps, \~115 sur les contretemps ; même décalage de −15 ms sur les contretemps, −6 ms sur les temps.

**Vérifier.** Sur le bus Sub, un analyseur (ReaEQ en affichage spectre, ou le JS `gfxanalyzer`) montre les deux pics à 59 et 72 Hz pendant la seconde moitié du temps ; ReaTune sur la piste Kick confirme la note d'atterrissage. Pour entendre le battement sans ambiguïté : ralentir le projet à 50 % (Rate) ou utiliser `10_sub_only_demi_vitesse.wav`. Pour tester l'effet de l'intervalle : changer la transposition du stab dans ReaSamplOmatic5000 (0 = unisson, +3 = tierce mineure, +7 = quinte) et écouter le bus Sub en boucle.

**Exporter vers la DT2.** Rendre chaque piste en one-shot 48 kHz / 16 bits mono, ou directement le kick avec sa queue longue si on veut la version « kick qui fait le sub ».

## Fichiers audio fournis

Tous dans `sons_isoles_live.zip` (44,1 kHz, 16 bits, mono, normalisés). Les boucles font 4 mesures à 143,25 BPM. Ordre d'écoute conseillé pour le tuto : 02 → 10 → 05 → 07 → 08 → 13 → 14 → 15.

| Fichier | Contenu | Ce qu'il démontre |
| --- | --- | --- |
| 01\_original\_2mesures | 2 mesures brutes | la référence |
| 02\_original\_sub\_only\_lowpass160 | l'original coupé à 160 Hz | le roulement du sub tel quel |
| 03\_temps\_moyenne\_boucle | le temps moyen (28 temps alignés) bouclé | ce qui est séquencé, sans le bruit de salle |
| 04 / 05\_kick\_seul | one-shot et boucle | glissando + queue à 59 Hz ; seul, le sub est lisse |
| 06 / 07\_stab\_seul | one-shot et boucle | le stab C#2, sub quasi pur |
| 08\_kick\_plus\_stab\_boucle | les deux réassemblés | le wobble réapparaît : preuve que c'est un battement |
| 09 / 10 — demi-vitesse | temps moyen et sub seul une octave plus bas | le battement à 6 Hz devient évident, et on entend qu'il n'est pas sur les 16ᵉ |
| 11 / 12\_charley | coup du temps, coup du contretemps | le même son, le contretemps plus fort et plus long ; le coup du temps contient le clic du kick |
| 13\_charley\_seul\_boucle | les croches seules | l'accent sur le contretemps |
| 14\_kit\_complet\_boucle | kick + stab + charley | la reconstruction complète |
| 15\_reconstruction\_vs\_original | 2 mesures reconstruites, silence, 2 mesures d'origine | ce que la décomposition capture et ce qu'elle laisse (résidu \~18 % en RMS : salle, ghosts, variations) |

Le kick isolé (04) a perdu son clic d'attaque, parti dans la piste charley puisqu'ils tombent au même endroit dans la même bande ; pour un kick complet, lui remettre un transient.

## Limites et méthode

L'enregistrement est très compressé (pic à 0 dBFS, RMS à −8 dB) et ne contient rien au-dessus de 8 kHz : les niveaux relatifs entre éléments et la couleur du charley sont à prendre avec réserve, les hauteurs et les placements sont fiables.

- Tempo : estimation par tempogramme puis affinage par maximisation de l'énergie du kick sur la grille (143,25 BPM, stable).
- Alignement : chaque temps recalé par corrélation sur la bande 40–200 Hz, puis moyenne de 28 temps (mesures 5–11). Ce qui n'est pas verrouillé en phase sur la grille (salle, bruit) s'efface d'environ 15 dB.
- Hauteurs du sub : ajustement par moindres carrés de deux sinusoïdes à fréquences libres sur 200–360 ms après chaque temps, vérifié sur les 48 temps. Une analyse à fenêtre courte fusionne les deux pics en un seul vers 65 Hz : c'est le piège classique sur ce genre de basse.
- Séparation kick / stab : extraction du ton à 59 Hz par fenêtres glissantes de 90 ms, le reste au-dessus de 150 ms étant le stab ; charleys = tout ce qui passe au-dessus de 400 Hz, découpé aux deux instants d'attaque.
- Micro-timing : la précision est d'environ ±5 ms sur les attaques nettes (charley, stab), moins bonne sur le kick dont l'attaque est noyée dans le sub.
- Les ghosts de kick des mesures 7–11 et le crash du break n'ont pas été isolés.

## Références qui recoupent l'analyse

Ce qu'on trouve en ligne confirme le squelette (kick 4/4 accordé, basse sur le contretemps, répétition hypnotique) mais aucune source trouvée ne décrit le mécanisme du battement entre la queue du kick et le stab ; c'est l'apport propre de cette analyse.

| Source | Ce qu'elle confirme | Ce qu'elle dit de différent |
| --- | --- | --- |
| [Cheperz — Hardtek : origines, sonorités et évolution](https://www.cheperz.org/hardtek.html) | basse « répétitive, rebondissante ou parfois placée en contretemps » ; la tribe « privilégie une répétition plus hypnotique et une évolution progressive » | tempo hardtek 160–190 ; notre extrait est à 143, côté tribe / mental |
| [r/Tekno — How to mental tekno](https://lr.eu.psf.lt/r/Tekno/comments/1g3s1os/how_to_mental_tekno) | remplacer un stab de basse par une queue de kick resamplée avec enveloppe de pitch pour qu'elle « rebondisse » ; kick en couches avec un sinus pour le corps | ne parle ni d'intervalle ni de battement |
| [Audiofanzine — bien caler sa basse en fonction du kick](https://fr.audiofanzine.com/groove-machine/korg/electribe-emx1sd/forums/t.565639,bien-caller-sa-basse-en-fonction-du-kick.html) | kick sur 1-5-9-13, basse sur 3-7-11-15 (hardtek) | rien sur l'accordage |
| [Attack Magazine — Low-End Theory, offbeat bass](https://www.attackmagazine.com/technique/tutorials/low-end-theory-exploring-eight-common-bassline-styles/) | basse entre chaque kick, attaque franche, decay filtré, souvent deux notes seulement | contexte house / trance |
| [Wikipedia — Free tekno](https://en.wikipedia.org/wiki/Free_tekno) | la tribe est « le principal sous-genre encore joué en hardware » ; tracks uniques créés en live | donne 150–185 BPM pour la free tekno en général |
| [Maxim Schunk — How to make Hardtekk](https://maximschunk.com/news/how-to-make-hardtekk-guide) | kick accordé « dans la tonalité du morceau », enveloppe de pitch qui tombe sur la fondamentale en 40–80 ms, « pas de basse séparée » : le kick occupe la place de la basse | Hardtekk allemand : couper la queue du kick avant le suivant, l'inverse exact de notre extrait où le chevauchement fait le groove |
| [Melodigging — Acidcore](https://www.melodigging.com/genre/acidcore) | kick 909/808 « relentless » souvent distordu, charleys en contretemps (« driving off-beat hats »), rides, arrangement long et hypnotique ; même scène free party / teknival | 150–180 BPM et la 303 au centre : en acidcore la ligne acide prend souvent la place du stab de sub sur le contretemps ; notre extrait n'a pas de 303, le sub joue ce rôle |
