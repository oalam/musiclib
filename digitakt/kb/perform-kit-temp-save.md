---
tags: [digitakt, kb]
theme: Perform kit et temp save
lot: 4
ordre: 22
manuel: "§10.10, §10.8.6 (p49-50, 52)"
os: "1.17"
statut: draft
---

# Perform kit et temp save

**En une phrase** : deux filets de sécurité pour triturer en live sans rien
abîmer : le perform kit garde le kit tourné quand on change de pattern sans
l'enregistrer, le temp save pose un point de retour pour le pattern actif.

## Gestes rapides

| Action | Touches |
|---|---|
| Perform kit on / off (`P` clignotant, `[PRESET/KIT]` orange) | `[FUNC] + [PRESET/KIT]` |
| Recharger le kit du pattern (annuler les réglages) | `[PRESET/KIT] + [NO]` |
| Enregistrer le kit modifié | `[PRESET/KIT] + [YES]` (menu SAVE KIT) |
| Temp save du pattern actif | `[FUNC] + [YES]` |
| Temp reload (dernier temp save, sinon état sauvegardé) | `[FUNC] + [NO]` |
| Sauvegarde définitive du pattern | PATTERN MENU, `SAVE TO PROJ` (cf. [[projet-sauvegarde]]) |

## Pas à pas : une montée filtrée sur deux patterns

1. Pattern main en lecture : `[FUNC] + [YES]` (temp save, point propre).
2. `[FUNC] + [PRESET/KIT]` : perform kit actif.
3. Fermer le filtre de tout le kit avec le contrôle global (cf.
   [[mixer-setup]]), en montant.
4. Basculer sur le pattern break : le filtre reste fermé, le kit n'est pas
   rechargé.
5. Sur le 1 du retour : `[PRESET/KIT] + [NO]`, le kit d'origine claque d'un
   coup.
6. Si le pattern a été abîmé (trigs ajoutés, CONTROL ALL) : `[FUNC] + [NO]`.

## En live techno

- Perform kit = le filtre, la décroissance, l'overdrive tournés pendant un
  break **survivent** à la bascule de pattern : la montée continue au lieu
  de repartir de zéro.
- `[PRESET/KIT] + [NO]` sur le 1 = un retour brutal à l'état propre, effet
  de drop gratuit.
- Temp save **avant** chaque passage où l'on va jouer avec les trigs ou le
  contrôle global ; `[FUNC] + [NO]` répare en une touche (doctrine §3).
- Les patterns d'un même morceau partagent le kit du pattern modèle : en
  perform kit, la bascule est sans couture (cf. [[presets-kits-pool]]).

## Pièges

- En perform kit, rien n'est sauvegardé automatiquement : tout est perdu à
  l'extinction si on n'enregistre pas.
- Le perform kit garde le kit **précédent** : basculer vers un pattern qui
  utilise un autre kit (autre morceau) garde les mauvais sons. Recharger
  avec `[PRESET/KIT] + [NO]` ou sortir du mode avant de changer de morceau.
- Le temp save est perdu au changement de projet ; il ne remplace pas
  `SAVE TO PROJ`.
- Le temp reload sans temp save préalable revient à l'état sauvegardé, pas
  à l'état d'il y a 5 minutes.
- En STEP RECORDING, `[FUNC] + [YES]` / `[NO]` ne font ni temp save ni
  reload (cf. [[enregistrement-quantize]]).
- `[FUNC] + [YES]` dans l'écran `[PTN]` ouvre le créateur de chaîne (cf.
  [[patterns-chaines]]).

## À essayer (5 min)

Temp save, perform kit on, overdrive et filtre poussés, bascule sur un
autre pattern du morceau, puis `[PRESET/KIT] + [NO]` sur le 1 ; finir par
`[FUNC] + [NO]` et vérifier que tout est revenu.

Source : manuel DT2 OS 1.17, §10.10, §10.8.6.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=6691) : « Perform kit » (1:51:31) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=3413) : « The perform kit » (56:53) · DT2, 2024
- [loopop — DIGITAKT II vs OG Digitakt, detailed tutorial](https://youtu.be/nepWmWsq84g?t=420) : « Perform kit » (7:00) · DT2, 2024
- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=6906) : « Page loop » (1:55:06) · DT2, 2024
