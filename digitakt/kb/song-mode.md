---
tags: [digitakt, kb]
theme: Song mode
lot: 4
ordre: 19
manuel: "§10.9 (p50-52)"
os: "1.17"
statut: draft
---

# Song mode

**En une phrase** : un song est une liste de lignes (pattern, nombre de
tours, longueur, tempo, mutes) jouées dans l'ordre : on y fige la chaîne
d'une bank générée pour la rejouer sans y penser, ou pour répéter un set.

## Gestes rapides

| Action | Touches |
|---|---|
| Choisir un song et entrer en SONG mode | `[SONG]` puis `[TRIG 1-16]` |
| Ouvrir l'écran SONG EDIT | `[FUNC] + [SONG]` |
| Ajouter une ligne (copie de la ligne courante) | `[FUNC] + [DOWN]` |
| Supprimer la ligne | `[FUNC] + [UP]` |
| Copier / coller / réinitialiser une ligne | `[FUNC] + [RECORD]` / `[STOP]` / `[PLAY]` |
| Boucler la ligne en cours (et sortir de la boucle) | `[SONG] + [LEFT]` |
| Choisir la prochaine ligne à jouer | `[SONG] + [UP]/[DOWN]` |
| Revenir au début du song | `[STOP]` deux fois |
| Quitter le SONG mode | `[PTN]` + `[TRIG 1-16]` (choisir un pattern) |

Colonnes d'une ligne : `LABEL` (intro, main, break...), `PTN`, nombre de
tours, longueur en pas (2 à 1024), `BPM` (hérité du pattern par défaut),
mutes de la ligne. La ligne `END` finale vaut `LOOP` ou `STOP`. Jusqu'à 99
lignes par song, 16 songs par projet.

## Pas à pas : rejouer la chaîne d'une bank générée

1. Ouvrir `library/digitakt/<slug>.md`, tableau *Patterns* : colonnes
   `Slot`, `Section`, `Tours`.
2. `[SONG]` + un slot vide, puis `[FUNC] + [SONG]`.
3. Choisir `CREATE ROWS FROM CHAIN`, `[YES]`, taper les slots dans l'ordre
   du tableau (`[LEFT]/[RIGHT]` pour changer de bank), `[YES]`.
4. Pour chaque ligne : `LABEL` = la section, nombre de tours = la colonne
   `Tours` arrondie (x2.8 → 3).
5. Ligne `END` sur `STOP` pour une répétition, `LOOP` pour tourner en fond.
6. `[NO]` pour sortir, `[PLAY]`, puis sauvegarder le projet (cf.
   [[projet-sauvegarde]]).

## En live techno

- Le song mode sert surtout à **préparer** : écouter l'enchaînement complet
  d'une bank, mesurer la durée d'un set, caler les tours. En live, la doctrine
  privilégie les mutes à la main (cf. [[mutes]]).
- `[SONG] + [LEFT]` sur une ligne qui marche : elle tourne tant qu'on veut,
  on relâche la boucle quand la foule est prête.
- Les mutes de ligne écrivent la partition de mutes de la note de bank : une
  ligne par phrase, mêmes pattern, mutes différents.
- Un tempo de song (sur n'importe quelle ligne) écrase tous les tempos :
  pratique pour jouer toute la bank à 190 BPM d'un coup.

## Pièges

- Les songs sont enregistrés automatiquement **dans le projet en cours** :
  changer de projet sans sauvegarder les perd.
- Les mutes d'une ligne reprennent les mutes du pattern au moment où l'on
  choisit le pattern ; les modifier ensuite ne touche pas le pattern.
- Le swing se règle toujours par ligne, même avec un tempo de song.
- Choisir un pattern fait sortir du SONG mode : la chaîne s'arrête.
- Tours fractionnaires (x1.4) : arrondir, ou régler la longueur de ligne en
  pas (tours x longueur du pattern) *(comportement au-delà de la longueur
  du pattern à vérifier)*.

## À essayer (5 min)

Song de 4 lignes depuis une bank générée, `END` sur `LOOP` ; pendant la
lecture, `[SONG] + [LEFT]` sur la ligne main, la laisser tourner 4 tours,
relâcher et écouter la reprise.

Source : manuel DT2 OS 1.17, §10.9.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [XNB — DIGITAKT II Song Mode & Chain](https://youtu.be/55fCA4d2vNw?t=199) : « Song » (3:19) · DT2, 2024
- [Elektron — Using pattern mutes per row to quickly arrange a Song](https://youtu.be/Isb0EiRSrJw) (vidéo entière) · Digitakt, OS song mode, 2022
- [EZBOT — ELEKTRON SONG MODE: Full Tutorial](https://youtu.be/e-4qQbD5hxQ) (vidéo entière) · Elektron, générique, 2022
