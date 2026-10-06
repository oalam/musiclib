---
tags: [digitakt, kb]
theme: Copier, coller, effacer
lot: 1
ordre: 3
manuel: "§6.4, §10.1.1, §17 (p19, 40, 88)"
os: "1.17"
statut: draft
---

# Copier, coller, effacer

**En une phrase** : partout la même logique, `RECORD` = copier, `STOP` =
coller, `PLAY` = effacer, combinés à la touche qui désigne l'objet (pattern,
track, page, trig, preset).

## Gestes rapides

| Objet | Copier | Coller | Effacer | Contexte |
|---|---|---|---|---|
| Pattern actif | `[FUNC] + [RECORD]` | `[FUNC] + [STOP]` | `[FUNC] + [PLAY]` | hors GRID RECORDING |
| Autre pattern (sans le quitter) | `[PTN]`, `[TRIG] + [RECORD]` | `[TRIG] + [STOP]` | `[TRIG] + [PLAY]` | menu pattern |
| Séquence de la track | `[FUNC] + [RECORD]` | `[FUNC] + [STOP]` | `[FUNC] + [PLAY]` | GRID RECORDING |
| Page de 16 pas | `[PAGE] + [RECORD]` | `[PAGE] + [STOP]` | `[PAGE] + [PLAY]` | GRID RECORDING |
| Trig + ses locks | `[TRIG] + [RECORD]` | `[TRIG] + [STOP]` | `[TRIG] + [PLAY]` | GRID RECORDING |
| Preset d'une track | `[TRK] + [RECORD]` | `[TRK] + [STOP]` | `[TRK] + [PLAY]` | partout |

Coller ou effacer **une deuxième fois** annule l'opération.

## Pas à pas : dupliquer le pattern modèle vers une bank

1. Sélectionner le pattern modèle (ex. H16) : `[PTN]`, `[RIGHT]` jusqu'à H,
   `[TRIG 16]`.
2. Rester dessus, appuyer `[PTN]`, puis `[TRIG 16] + [RECORD]` : copié.
3. Toujours dans `[PTN]`, aller sur la bank du morceau (`[LEFT]`/`[RIGHT]`)
   et faire `[TRIG n] + [STOP]` sur chaque slot à remplir (01, 02, 03…).
4. `[FUNC] + [SETTINGS]` pour sauvegarder le projet.

## En live techno

- Construire une variation : copier le pattern du groove (`[FUNC] +
  [RECORD]`), coller sur le slot suivant, puis retirer ou ajouter une track.
  Les deux patterns partagent tout le reste : la bascule est propre.
- Un break de 1 mesure dans un pattern de 8 : copier la page 1
  (`[PAGE] + [RECORD]`), la coller sur la page 8, puis l'alléger.
- La correspondance avec la bank générée (`library/digitakt/<slug>.md`) :
  un slot de la chaîne = un pattern collé depuis le modèle, puis rempli.

## Pièges

- Même combinaison, deux effets : `[FUNC] + [RECORD]` copie le pattern
  hors GRID RECORDING, la séquence de la track active en GRID RECORDING.
- **Un seul presse-papiers** : copier un trig efface le pattern copié
  auparavant.
- Les copies de track, page et trig ne marchent qu'en GRID RECORDING
  (`[RECORD]` allumé).

## À essayer (5 min)

Copier le pattern modèle vers A01-A04 sans quitter le modèle, puis effacer
A04 (`[PTN]`, `[TRIG 4] + [PLAY]`) et annuler en refaisant la même
combinaison.

Source : manuel DT2 OS 1.17, §6.4, §10.1.1, §17.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=3526) : « Copy, Paste » (58:46) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=3766) : « Copy/ Paste Patterns and tracks » (1:02:46) · DT2, 2024
- [soffter — Every Elektron Copy & Paste & Undo Function](https://youtu.be/c9E55vhiGPs) (vidéo entière) · Elektron, générique, 2023
