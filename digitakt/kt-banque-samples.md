---
tags: [digitakt, samples, kt]
theme: Créer une banque de samples maison
updated: 2026-10-14
---

# Créer une banque de samples maison

Note de transmission : comment préparer ses propres samples (extraits de
films, prises, resamples) pour que `scripts/samples.py` les classe tout seul
dans l'arbre de la DT2, puis les envoyer sur la machine via un live.
Référence technique : `scripts/README.md` § samples.py ; décisions : [[../SPEC]]
§ 7.J et 7.J8 ; grille des tracks : [[doctrine]] § 1.

## Exemple réel : `Movie tracks`

```
/Volumes/xtreme/Samples/Movie tracks/
├── Dune/dune_sardaukar_chant_01.wav        → VX/CHANT   « VX Sardauka 01 mov »
├── Ghost In the shell/gits_choir_01.wav    → VX/CHANT   « VX Gits Cho 01 mov »
└── Matrix/matrix_smith_speech_01.wav       → VX/SPEECH  « VX Smith Sp 01 mov »
```

- Le **dossier de premier niveau** (`Movie tracks`) est le pack : il donne le
  suffixe de 3 lettres du nom DT2 (`mov`) et le pad de kit dans le front.
- Le **sous-dossier** (`Dune`, `Matrix`) est le kit : on filtre dessus dans
  la vue Samples.
- Le **nom de fichier** porte le mot-clé qui décide du code (`speech`,
  `chant`, `choir`) et de la sous-catégorie, et le numéro de variante.

## 1. Préparer l'audio

| Critère | Recommandation | Pourquoi (seuil du pré-filtre) |
|---|---|---|
| Format | WAV 48 kHz, 16 ou 24 bits | fréquence native de la DT2 |
| Canaux | mono pour voix, one-shots, basses ; stéréo seulement si l'image compte | la stéréo double la place dans les 400 Mo de RAM du projet |
| Niveau | crête vers -1 dBFS (normaliser) | drapeau `faible` sous -18 dBFS, `muet` sous -40 dBFS |
| Saturation | aucun plateau à pleine échelle | drapeau `sature` au-delà de 0,1 % du fichier |
| Début | couper au ras de l'attaque, moins de 30 ms de silence | drapeau `blanc` : le trig part en retard |
| Fin | fondu de 5 à 10 ms | évite le clic en fin de sample |
| Durée one-shot drum | moins de 2 s | drapeau `long` au-delà |
| Boucles | coupées sur 1, 2, 4, 8 ou 16 mesures exactes | le tempo est recalé sur les mesures |
| Voix, phrases | une phrase par fichier, 2 à 15 s | lisible sur un trig, tient dans la RAM |

Les drapeaux ne suppriment rien : ils font passer le sample en fin de case.
Exemple : les 4 Dune ont `blanc` ; les rogner les fait remonter.

## 2. Nommer : la nomenclature

Forme du fichier :

```
<source>_<sujet>_<mot-clé>[_<BPM>][_<note>]_<NN>.wav
matrix_smith_speech_01.wav
dune_drum_loop_120_01.wav        → LOOPS/DL/120   « DL 120 Dune 01 mov »
dune_drone_C#_01.wav             → TONAL/PD/DRONE « PD C# Drone 01 mov »
akira_kaneda_shout_01.wav        → VX/MC          « VX Kaneda S 01 mov »
```

- minuscules, mots séparés par `_` ; numéro de variante sur 2 chiffres à la
  fin ;
- **le mot-clé décide du code**. Mots reconnus (extraits de `CODE_RULES`) :

| Code | Mots-clés | Sous-catégories (mot du chemin) |
|---|---|---|
| VX | `vox` `vocal` `voice` `chant` `choir` `speech` `shout` `acapella` `adlib` | SPEECH (`speech`, `talk`, `spoken`, `news`), CHANT (`chant`, `choir`, `sing`), MC (`mc`, `shout`, `hype`), CUT (`cut`, `chop`) |
| FX | `fx` `sfx` `rise` `riser` `impact` `sweep` `noise` `whoosh` `reverse` `drop` `transition` | RISE, REV, HIT, NOISE |
| PD | `pad` `drone` `texture` `ambient` `atmos` `cinematic` | AMBIENT, CHORD, DRONE, sinon SHORT / LONG (4 s) |
| ST | `stab` `chord` `hit` `riff` `lead` `synth` `piano` `string` | CHORD, STAB, ANALOG…, sinon SHORT / MID / LONG |
| BS | `bass` `sub` `reese` `808` | SUB, WOB, DIST, ANALOG, sinon SHORT / MID / LONG |
| Drums | `kick` `snare` `clap` `hat` `crash` `tom` `perc`… | voir `SUB_RULES` |
| Boucle | `loop` ou un BPM dans le nom (fichier de 1 s ou plus) | BR / DL par tranche de tempo (060, 120, 150, 180) |

- **BPM** (boucles) et **note** (BD, BS, ST, PD, boucles ML / BL) écrits
  dans le nom sont prioritaires sur la mesure et reportés dans le nom DT2.
  Pour VX, la note n'entre pas dans le nom : la mettre en tag si utile (les
  4 Dune et GITS 01 sont en si).
- Le nom DT2 fait **18 caractères au plus** (`<CODE> [BPM|note] <desc> <NN>
  <pack>`) ; les mots déjà présents dans un nom de dossier sont retirés
  (`dune` dans `Dune/` : « Sardauka », pas « Dune Sard »).

### Pièges

- **Le premier code qui matche gagne**, dans l'ordre BR, BD, SD, CP, OH, HH,
  CY, TM, PC, BS, VX, FX, PD, ST. `blade_kick_it_speech_01.wav` part en `BD`,
  `amen_speech` en `BR`, `bass_riser` en `BS`. Éviter les mots de drums ou
  de basse dans le nom d'une voix ou d'un FX.
- Le chemin entier compte, dossiers compris : un dossier `Vocals/` ou `FX/`
  suffit à donner le code.
- La famille vient du pack (`FAMILY_RULES`) ; un pack absent de la table
  tombe en `UNIVERSEL` (cas de `Movie tracks`). Pour le ranger en `SAMPLE`
  (samples maison, sans plafond), ajouter son préfixe à `FAMILY_RULES`, ou
  `family` dans un override.

## 3. Classer et vérifier

```bash
cd scripts
.venv/bin/python samples.py --dry-run       # grille, sans écrire
.venv/bin/python samples.py                 # reconstruit le manifeste
.venv/bin/python samples.py --unclassified  # ce qui n'a pas de code
```

Ou le bouton de reconstruction de la vue Samples du front. Puis, dans la vue
Samples : pad du kit (`Movie tracks`), arbre à droite, écoute (`Espace`),
étoiles (`1`…`5`), tags (`T`), corbeille (`Suppr`).

Si un fichier est mal rangé, deux corrections possibles :

1. **Renommer** avec le bon mot-clé (à préférer : la règle sert aussi aux
   prochains samples), puis relancer `samples.py`.
2. **Override** dans `library/samples/overrides.json`, clé = chemin relatif
   à `Samples/` :
   `{"Movie tracks/Matrix/matrix_smith_speech_01.wav": {"code": "VX", "sub": "SPEECH"}}`
   (champs `family`, `code`, `sub`, `name`, `tags`, `stars`, `trash` ; une
   clé finie par `/` vise tout un kit).

Si le code des règles (`analyzer/samples.py`) a changé, **redémarrer
`api.py`** avant de reconstruire depuis le front : l'API garde l'ancien code
en mémoire.

## 4. Envoyer sur la DT2

Ajouter les samples à un live depuis la vue Samples (`L`, ou `Entrée` pour
le sample en cours, dans la banque active), puis exporter le live : les
fichiers sont copiés vers `<MEDIA>/Live/00-live/<live>/<BANQUE>/<BRANCHE>/`
(accordés à la tonalité de la banque, cf. 7.L4), à envoyer sur le +Drive
avec Transfer.

## Check-list

- [ ] WAV 48 kHz, mono sauf besoin, crête vers -1 dBFS, sans saturation
- [ ] silence de tête < 30 ms, fondu de fin
- [ ] `Samples/<Pack>/<Kit>/<source>_<sujet>_<mot-clé>_<NN>.wav`
- [ ] pas de mot de drums / basse dans une voix ou un FX
- [ ] BPM dans le nom des boucles, note dans le nom des sons tonals
- [ ] `samples.py --unclassified` vide pour le pack
- [ ] écoute dans la vue Samples, puis ajout au live et export
