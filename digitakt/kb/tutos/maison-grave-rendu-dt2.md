---
tags: [digitakt, kb, tutos]
theme: Grave sur Mac, ch. 7, rendu 48 kHz mono champ par champ, du rendu à la machine, chaîne de 16 kicks choisis à la vélocité (Grid 16)
lot: 4
ordre: 7
source: "échange de travail du 2026-10-29 (stack retenue) ; chapitre détaché du tuto le 2026-10-31"
auteur: Tom (stack), rédaction à vérifier dans Reaper
modele: DT2
os: "1.17"
stack: [Reaper, Vital, Maschine Drumsynth Kick, Kick 3, iZotope Trash Lite, SPAN, ReaComp, Acid V]
parent: maison-sounddesign-grave-reaper
statut: draft
updated: 2026-10-31
---

# Grave sur Mac, ch. 7 — Rendu et transfert vers la DT2

Chapitre 7 du tuto « sound design préparatoire » (lot 4 de [[_index]]).
Le hub [[maison-sounddesign-grave-reaper]] porte les arbitrages (§0), la stack et
les notions Reaper (§1), les pièges (§8) et les exercices (§9). Les numéros
de section sont ceux du tuto entier : un renvoi « §n » vise le chapitre n,
avec le lien de sa fiche quand ce n'est pas celle-ci.

## 7. Rendu et transfert vers la DT2

### 7.1 La fenêtre de rendu, champ par champ

Cmd+Opt+R (File > Render). La fenêtre fait peur la première fois ; cinq
champs comptent, le reste garde sa valeur par défaut.

| Champ | Valeur ici | Pourquoi |
|---|---|---|
| **Source** | « Master mix » quand les autres pistes sont mutées ; « Stems (selected tracks) » pour rendre la piste sélectionnée seule, avec ses effets mais **sans** les effets du master (SPAN n'y change rien) | un stem ignore les mutes des autres pistes : pas besoin de muter |
| **Bounds** | « Time selection » | le fichier fait exactement la longueur de la sélection : une note, un temps ou deux mesures ([[maison-grave-projet-reaper]] §2.2) |
| **Output > Directory, File name** | le dossier `rendus/` du projet ; nom tapé à la main (`kick_tribe_F#_165`) ; les jokers `$track` et `$project` existent pour les séries | le nom porte la note mesurée ([[maison-grave-kick]] §3.5), pas la note MIDI |
| **Sample rate, Channels** | **48000**, **Mono** | fréquence native de la DT2 ; le grave est mono (si la source est stéréo, Reaper somme gauche + droite) |
| **Format** | WAV, **24 bit PCM** ; « Normalize/limit » **décoché** pour le kick et le kickbass (garder la marge, la DT2 sature encore à l'overdrive) ; sur le rumble, normalisation de crête à -1 dB acceptée, à condition de baisser la 2 après coup | Transfer convertit en 16 bits à l'envoi |
| **Tail** | « Add tail » **décoché** (ou 0 ms) | sinon le fichier dépasse la sélection et la boucle ne tombe plus juste |
| Bouton | « Render 1 file » ; « Add to render queue » pour empiler plusieurs rendus (trois longueurs de kick) et les lancer d'un coup | |

Deux raccourcis pour les cas simples : sélectionner un item, clic droit >
**Glue items** le rend sur place avec ses fondus (sans les effets de la
piste) ; clic droit > **Apply track FX to items as new take** rend l'item
**avec** la chaîne d'effets de la piste, en gardant l'original comme prise
précédente (Cmd+Z ou le menu des prises pour y revenir). Le second est
pratique pour figer un kick traité, ou pour la variante en dossier du [[maison-grave-projet-reaper]] §2.4.

### 7.2 Du rendu à la machine

1. **Sélection temporelle** exacte (une note, un temps, une ou deux
   mesures) : glisser dans la règle avec l'aimantation active (Opt+S) ; pour
   une note seule, sélectionner l'item puis la sélection temporelle se cale
   dessus par double-clic dans la règle au-dessus de l'item (ou Time
   selection > Set time selection to items).
2. Rendu selon le tableau §7.1. Écouter le fichier rendu dans le Media
   Explorer (View > Media Explorer) : il lit au tempo du projet, ce qui
   permet de vérifier une boucle de rumble avant de l'envoyer.
3. Nommer avec le style, la note et le tempo : `kick_tribe_F#_165.wav`,
   `rumble_gritty_F#_165.wav`, `kickbass_sat_F#_160.wav`, `bass_sub_F#.wav`.
   La note vient de la mesure sur la queue, pas de la note MIDI.
4. Ranger les WAV dans la banque de samples (`/Volumes/xtreme/Samples`,
   [[../../kt-banque-samples]]) dans un pack `SoundDesign/` à côté de
   `SoundDesign/rumble/` (sous-dossier par rôle, `kick/`, `kickbass/`,
   `bass/` ; nom du pack à arbitrer avant le premier versement), puis
   réanalyse : le circuit habituel, écoute garder / écarter, export
   Transfer, conversion 16 bits.
5. Sur la machine : kick sur la 1 (ONESHOT, `TUNE` 0), rumble sur la 2 sur
   les mêmes pas que le kick, basse sur la 9 en contretemps ; preset nommé
   avec la note (`kick_tribe_F#`, `rumble_F#`, `bass_F#`), puis le kit
   (doctrine §8, §13). Garder le projet Reaper et les presets Vital / Kick 3
   dans le vault : le sample est figé, le projet est la source.

### 7.3 Chaîne de seize kicks choisis à la vélocité (Grid 16)

Seize variantes du même kick, classées de la plus douce à la plus dure,
rendues dans **un seul** WAV ; sur la DT2, la machine Grid découpe le
fichier en seize tranches égales et la vélocité du trig choisit la
tranche. C'est la chaîne de hats de [[elektronauts-velocite-macros]] §1
(étape 4) appliquée au kick ; essayée à la machine le 2026-10-31, elle
marche.

**Ce qui se varie, et dans quel ordre.** Seulement ce que la DT2 ne sait
pas faire : la courbe de pitch (Bend de Drumsynth, enveloppe de pitch de
Kick 3 ou de Vital), l'équilibre sub / corps aux potards du joiner, le
style ou le mix de Trash. Le filtre, le decay d'AMP et l'overdrive restent
des VEL MOD ordinaires. Les seize tranches sont **ordonnées par
intensité** (tranche 1 = kick doux, tranche 16 = kick dur) pour que la
vélocité garde son sens et qu'un VEL MOD → OVERDRIVE
([[elektronauts-velocite-macros]] [[maison-grave-projet-reaper]] §2) aille dans la même direction.
L'aléatoire, c'est la machine qui le met ensuite ; il ne se fige pas dans
le fichier.

**Longueur d'une tranche.** La Grid coupe net à la fin de la tranche :
elle doit dépasser la queue du kick, release comprise, sinon le coup
clique. Calcul à 165 BPM (temps = 60 / 165 = 364 ms) :

| Format du rendu | Durée | Tranche (1/16 du fichier) | Convient à |
|---|---|---|---|
| 2 mesures | 2 × 4 × 0,364 = 2,909 s | 182 ms (une croche, 2 pas) | recette A seule, queue de 60-80 ms |
| **4 mesures (défaut)** | 4 × 4 × 0,364 = 5,818 s | 364 ms (un temps, 4 pas) | kick à rumble (130-200 ms à -24 dB, la queue continue en dessous), kick + basse |
| 8 mesures | 11,636 s | 727 ms (deux temps) | kickbass qui tient jusqu'au kick suivant |

Mémoire : 4 mesures en mono 16 bits 48 kHz font 5,818 × 48 000 × 2 =
558 Ko, sans conséquence. La Grid ne lit pas le tempo du fichier : un rendu
fait à 165 sert tel quel à 160 ou 170, seule compte la longueur de la
tranche par rapport à la queue.

**Dans Reaper, pas à pas.**

1. Sur KICK, sélection temporelle de 4 mesures (aimantation active),
   Insert > New MIDI item. Dans l'éditeur, grille 1/4 : seize notes
   identiques (tonique, même vélocité, longueur un pas), une au début de
   chaque temps. Pour 2 ou 8 mesures, grille 1/8 ou 1/2.
2. Le paramètre varié : dans la fenêtre FX du plug-in, bouton **Param**
   (en haut) > **Show track envelope** sur le paramètre choisi (Bend,
   enveloppe de pitch, mix de Trash) ; une piste d'enveloppe apparaît sous
   KICK. Deux points (Shift+clic sur la ligne pose un point, double-clic
   sur le point ouvre sa valeur) : au début de l'item la valeur douce, à
   la fin la valeur dure. La rampe donne 1/16 de la plage par tranche ; la
   dérive à l'intérieur d'une note est inaudible. Variante en escalier :
   seize points, sélectionnés puis clic droit > Set shape > **Square**, la
   valeur tient pendant toute la tranche ; à préférer pour un paramètre
   lu à l'attaque (Bend, enveloppes de Kick 3). Deux paramètres se varient
   avec deux enveloppes.
3. Écouter la sélection en boucle : la progression doit s'entendre sans
   saut ni coup plus fort que les autres (Reset puis Peak dans SPAN). Si
   le dernier sort trop fort, resserrer la valeur dure plutôt que
   d'ajouter un limiteur.
4. Rendu selon §7.1 : Bounds Time selection sur les 4 mesures exactes,
   48 kHz mono 24 bits, sans tail ni normalisation. Nom
   `kick_<style>_<note>_<bpm>_x16.wav` (ex. `kick_tribe_F#_165_x16.wav`) ;
   le suffixe `_x16` dit qu'il faut une Grid. Dans le Media Explorer,
   vérifier que chaque coup part sur un temps : la Grid n'a pas de
   détection de transitoire, elle coupe à 1/16 du fichier.

**Sur la DT2.**

1. Track 1, `[FUNC] + [SRC]`, machine **GRID** ; `GRID 16`, `SLICE 1`,
   `LEN 1`, `PLAY FWD`. C'est l'exception documentée à la règle « kick en
   ONESHOT » de [[../machines-src]].
2. SETUP de la track : **VEL → VOL** sur OFF, sinon la vélocité change
   aussi le volume du kick.
3. Page TRIG, VEL MOD : destination **SRC:SLICE**, profondeur positive
   réglée pour que la vélocité 127 tombe sur la tranche 16 et pas au-delà
   (la profondeur compte en tranches, comme pour la wavetable de
   [[elektronauts-grid-wavetables]] [[maison-grave-projet-reaper]] §2 ; hors plage la machine sort du
   bruit).
4. Jouer : `VEL` locké par pas (basse sur les pas faibles, haute sur le
   premier temps), mode VELOCITY au pad, ou LFO `RAND` sur `SRC:SLICE` à
   faible profondeur pour un kick qui respire sans rien figer ; en fill,
   CTRL-ALL sur la vélocité, ou un second VEL MOD → OVERDRIVE dans le même
   sens.
5. Preset `kick_<style>_<note>_x16`, puis le kit (doctrine §8, §13). Le
   rumble de la 2 reste un rendu séparé ([[maison-grave-rumble]] §4.4) : il réagit au kick par le
   sidechain de la DT2, pas à la tranche.

**Solution de repli.** Seize WAV séparés dans seize slots consécutifs et
lock du sample par pas : déterministe, mais la vélocité ne choisit plus (le
slot de sample comme destination de VEL MOD reste à vérifier sur la
machine) ; à réserver aux variantes qui ne s'ordonnent pas.

## Liens

[[maison-sounddesign-grave-reaper]] · [[maison-grave-basse]]

#digitakt #kb #tutos #sounddesign
