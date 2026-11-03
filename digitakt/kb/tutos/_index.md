---
tags: [digitakt, kb, tutos, index]
updated: 2026-10-31
---

# KB tutos — sessions vidéo décortiquées

Quatre sortes de fiches. Le lot 1 tire ses fiches de **sessions complètes**
(une production ou un live, du pattern vide au pattern plein), vidéo
rédigée depuis la transcription et les chapitres YouTube, ou fil écrit
quand l'auteur y déroule toute sa session. Le lot 2
tire les siennes d'un **fil de forum** (Elektronauts, *Digitakt II Tips &
Tricks*), une fiche par famille d'astuces, chaque astuce déroulée pas à pas.
Le lot 3 consigne des **recettes maison** : une idée venue en travaillant,
raisonnée contre le manuel et la doctrine, écrite au format du lot 2 et à
vérifier à la machine. Le lot 4 rassemble le **sound design
préparatoire** : ce qui se fabrique sur le Mac avant la machine (Reaper,
Vital, Kick 3, Trash Lite), un hub et six chapitres au format du lot 3.
Chaque *trick* est noté avec la track, l'instrument,
les pas et un lien vers le chapitre où il est montré, puis mis en regard de la
grille de [[../../doctrine]] (§1) et des fiches machine de [[../_index]].

Les fiches machine disent *comment* faire un geste ; les KT de
[[../theorie/_index]] disent *pourquoi* ; une fiche tuto montre *un auteur
qui enchaîne les gestes* sur un morceau réel, avec ses choix et ses
hésitations.

## Format d'une fiche

Frontmatter : `tags: [digitakt, kb, tutos]`, `theme`, `lot`, `ordre`,
`source` (URL), `auteur`, `modele` (DT1 / DT2), `duree`, `publie`,
`statut` (`draft` → `vérifié` une fois les tricks rejoués sur la machine).
Sections, dans cet ordre :

1. **En une phrase**
2. **Cadre** : contraintes de la session, matériel, packs
3. **Layout de l'auteur** : tableau track → instrument, en regard de la doctrine
4. **Tricks** : un bloc par trick, avec *Track / instrument / pas*, *Geste*,
   *Pourquoi*, *Chapitre* (lien horodaté) et renvoi à la fiche machine
5. **Chronologie** : les chapitres YouTube avec le lien direct
6. **Ce qu'il laisse en suspens**
7. **À essayer (5 min)**

### Fiche famille d'astuces (lot 2)

Frontmatter : `tags: [digitakt, kb, tutos]`, `theme`, `lot: 2`, `ordre`,
`source` (URL du fil), `auteur` (la communauté), `modele`, `os`, `statut`.
Sections : **En une phrase**, **Sur notre grille** (où la famille se pose
sur la doctrine §1), **Astuces** (un bloc par astuce : *Source* avec le ou
les posts `#n` liés, *Résultat*, *Pas à pas* numéroté, *Attention* si
besoin, *Chez nous*), **Liens**. Le panorama du fil, le vocabulaire, les
pièges et les exercices d'ensemble sont dans [[elektronauts-panorama]].

### Fiche recette maison (lot 3)

Même frontmatter et mêmes sections que le lot 2, avec `source` = la date de
l'échange et `auteur` = qui a eu l'idée. Une section **Le piège physique,
avant de câbler** peut précéder les recettes quand l'idée de départ bute sur
le fonctionnement de la machine (envoi partagé, lock trig qui ne déclenche
rien). Statut `draft` tant que la recette n'a pas été rejouée.

### Fiche sound design préparatoire (lot 4)

Même frontmatter que le lot 3, `lot: 4`, `ordre` = numéro de chapitre (0
pour le hub) et `parent` = le hub. Les chapitres gardent la numérotation
de section du tuto entier ; un renvoi « §n » vers un autre chapitre est
précédé du lien de sa fiche.

## Lot 1 — Sessions complètes

| # | Fiche | Auteur | Modèle | Statut |
|---|---|---|---|---|
| 1 | [[synthackers-techno-session]] | Synthackers (James Orvis) | DT2 | draft |
| 2 | [[synthackers-techno-acid]] | Synthackers (James Orvis) | DT2 | draft |
| 3 | [[elektronauts-un-pattern-six-sections]] | Olaf Wolkenhauer (Elektronauts, fil écrit) | DT1 | draft |

## Lot 2 — Astuces Elektronauts (fil Digitakt II)

Source : <https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556>
(564 posts, lu le 2026-10-22). Rangé ici le 2026-10-23, auparavant KT22 dans
[[../theorie/_index]].

| # | Fiche | Famille | Astuces | Statut |
|---|---|---|---|---|
| 0 | [[elektronauts-panorama]] | panorama, vocabulaire, pièges, exercices | — | draft |
| 1 | [[elektronauts-presets-pool]] | presets et preset pool | 5 | draft |
| 2 | [[elektronauts-seconde-sequence]] | seconde séquence cachée dans chaque pattern | 6 | draft |
| 3 | [[elektronauts-ctrl-all]] | CTRL-ALL comme geste de fill | 3 | draft |
| 4 | [[elektronauts-resampling]] | resampling stéréo et fondu | 4 | draft (astuce 2 vérifiée 2026-10-24) |
| 5 | [[elektronauts-velocite-macros]] | vélocité, sound macros, key tracking | 4 | draft |
| 6 | [[elektronauts-compresseur]] | compresseur, sidechain, saturation | 5 | draft |
| 7 | [[elektronauts-projet-modele]] | projet modèle, kits, banques | 6 | draft |
| 8 | [[elektronauts-grid-wavetables]] | Grid, wavetables, LFO aléatoire | 7 | draft |
| 9 | [[elektronauts-comb-delay]] | comb filter et delay accordé | 3 | draft |
| 10 | [[elektronauts-transitions]] | transitions entre patterns | 4 | draft |
| 11 | [[elektronauts-raccourcis]] | raccourcis d'écran et réglages | 12 | draft |

## Lot 3 — Recettes maison

| # | Fiche | Idée | Recettes | Statut |
|---|---|---|---|---|
| 1 | [[maison-rumble-dans-le-kick]] | rumble dans la queue sèche du kick (track 1), sans resample | 4 | draft |
| 2 | [[maison-progression-par-phrases]] | pattern main écrit pour 4 tours, partition de mutes sur 3 cycles, changement de pattern à une seule différence | 3 | draft |

L'ex-recette maison 3 (le grave fabriqué sur le Mac) est devenue le lot 4.

## Lot 4 — Sound design préparatoire

Le grave fabriqué sur le Mac avant la machine (Reaper, Vital, Drumsynth,
Kick 3, Trash Lite, SPAN, ReaComp, Acid V) et exporté pour les tracks 1, 2
et 9. Ex-recette maison 3, découpée le 2026-10-31 en un hub et six
chapitres parce que la fiche unique dépassait 800 lignes.

| Ch. | Fiche | Contenu | Statut |
|---|---|---|---|
| 0-1, 8-9 | [[maison-sounddesign-grave-reaper]] | hub : arbitrages, stack, notions Reaper, glossaire Reaper → Digitakt, pièges, exercices, ressources | draft |
| 2 | [[maison-grave-projet-reaper]] | projet Reaper modèle : construction clic par clic, pistes, durées au tempo, sidechain par canaux 3/4, saturation par bandes, mesure SPAN | draft |
| 3 | [[maison-grave-kick]] | kick : Drumsynth, Kick 3 par couches, Vital de A à Z, chaîne de sortie commune | draft |
| 4 | [[maison-grave-rumble]] | rumble : reverb saturée duckée par le kick, deux départs de passe-haut, rendu boucle ou un coup | draft |
| 5 | [[maison-grave-kickbass]] | kickbass : Vital saturé ou sinus, Kick 3, limite de tempo vers le kick-sub | draft |
| 6 | [[maison-grave-basse]] | basse en contretemps (one-shot par note), trois couches, ligne Acid V | draft |
| 7 | [[maison-grave-rendu-dt2]] | rendu 48 kHz mono et transfert ; chaîne de seize kicks choisis à la vélocité (Grid 16, essayée à la machine le 2026-10-31) | draft |
