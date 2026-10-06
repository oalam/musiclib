---
tags: [digitakt, kb]
theme: Projet, sauvegarde, Transfer
lot: 1
ordre: 1
manuel: "§5.2, §6.9, §14.1, §14.3, §17 (p16, 20-21, 75-76, 88-89)"
os: "1.17"
statut: draft
---

# Projet, sauvegarde, Transfer

**En une phrase** : un set = un projet (128 patterns, 16 songs, pool de
samples) ; on le crée vide, on le sauvegarde souvent, et on l'archive sur
l'ordinateur avec Transfer avant chaque date.

## Gestes rapides

| Action | Touches |
|---|---|
| Sauvegarder le projet (écrase) | `[FUNC] + [SETTINGS]` |
| Sauvegarde temporaire du pattern | `[FUNC] + [YES]` |
| Recharger le pattern (annule les modifs) | `[FUNC] + [NO]` |
| Recharger un preset depuis sa dernière sauvegarde | `[TRK] + [TRIG 1-16] + [NO]` |
| Menu projet | `[SETTINGS]` > PROJECT |

## Pas à pas

1. **Créer** : `[SETTINGS]` > PROJECT > LOAD PROJECT > `CREATE NEW` (tout en
   bas de la liste). Le projet actif est remplacé : sauvegarder l'ancien avant.
2. **Nommer et poser** : `SAVE PROJECT AS`, choisir un slot, nommer (ex.
   `FREE-2026-11`). Indispensable : un pattern ne peut être sauvé dans le
   projet qu'après une première sauvegarde du projet.
3. **Travailler** : `[FUNC] + [YES]` fige l'état d'un pattern avant une
   expérimentation, `[FUNC] + [NO]` y revient.
4. **Sauvegarder** : `[FUNC] + [SETTINGS]` à chaque étape franchie.
5. **Protéger** : MANAGE PROJECTS > `[RIGHT]` > `TOGGLE` (cadenas) sur le
   projet du set une fois prêt.
6. **Archiver** : USB vers le Mac, Transfer > CONNECT > EXPLORE, choisir le
   type de fichier, glisser vers MY COMPUTER.

## En live techno

- Un projet par set, nommé par date / lieu. Garder un projet `TEMPLATE` avec
  le pattern modèle et le kit modèle (cf. [[../doctrine]] §8) : on le charge,
  puis `SAVE PROJECT AS` sous le nom du nouveau set **avant toute modif**.
- Avant de partir jouer : sauvegarde projet, cadenas, backup Transfer. Le
  jour J on improvise sur une copie protégée, pas sur le seul exemplaire.
- `PURGE ALL` (MANAGE PROJECTS, projet actif) vide le pool des samples non
  utilisés : à faire en fin de préparation pour alléger les 400 Mo du projet.

## Pièges

- Charger un projet remplace l'état actif sans demander : sauvegarder avant.
- `CLEAR` d'un pattern (`[SETTINGS]` > PATTERN) n'est définitif qu'une fois
  sauvé ; `[FUNC] + [NO]` rattrape tant que ce n'est pas fait.
- Supprimer un sample du +Drive le retire de tous les presets et patterns qui
  l'utilisent.

## À essayer (5 min)

Créer `TEMPLATE`, le sauvegarder, modifier un pattern, `[FUNC] + [YES]`,
casser le pattern, `[FUNC] + [NO]` : vérifier le retour. Puis
`SAVE PROJECT AS` sous un autre nom et constater que `TEMPLATE` est intact.

Source : manuel DT2 OS 1.17, §5.2, §6.9, §14.1, §14.3, §17.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=237) : « Projects » (3:57) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=933) : « Create a new project » (15:33) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=3034) : « Save project » (50:34) · DT2, 2024
- [Bass Robotics — What Is A Pattern Versus A Project](https://youtu.be/RNduFPMOxF4) (vidéo entière) · DT2, 2024
- [Ricky Tinez — How to Backup Samples, Projects & Patterns](https://youtu.be/5AQKcNNr6ts?t=403) : « Backing up projects » (6:43) · DT1, principe identique, 2018
