---
tags: [digitakt, kb]
theme: Live looping et resampling en jeu
lot: 4
ordre: 27
manuel: "§13.1, §13.2, A.2.3 (p68-69, 96)"
os: "1.17"
statut: draft
---

# Live looping et resampling en jeu

**En une phrase** : pendant le set, figer en sample quelques mesures de la
sortie main, puis rejouer cette boucle sur une track pour la triturer,
libérer des tracks ou faire le pont vers le morceau suivant.

## Gestes rapides

| Action | Touches |
|---|---|
| Menu SAMPLING | `[SAMPLING]` |
| Armer / désarmer | `[SAMPLING] + [YES]` / `[SAMPLING] + [NO]` |
| Prise immédiate (ignore seuil et ARM) | `RECORD NOW` + `[YES]`, `[YES]` pour arrêter |
| Retailler puis garder | knobs E / H, `[YES]` ; `[FUNC] + [NO]` pour jeter |

Réglages de prise pour le live : `SRC` = MAIN, `CHAN` = STEREO L R,
`R.LEN` en pas (16 = 1 mesure, 64 = 4 mesures), `R.STRT` = THRES, `THRES`
juste sous le niveau du kick.

## Pas à pas : figer 4 mesures et jouer avec

1. Préparer la track d'accueil **hors grille** : la 16 (réserve, doctrine
   §1), machine STRETCH, `BARS` = 4 (cf. [[machines-src]]).
2. Pendant que le pattern tourne : `[SAMPLING]`, `SRC` = MAIN, `R.LEN` = 64,
   `R.STRT` = THRES.
3. Armer (`[SAMPLING] + [YES]`) juste avant le 1 d'une phrase : la prise part
   sur le premier kick qui dépasse le seuil et dure exactement 4 mesures au
   tempo du set.
4. Retailler si besoin, `[YES]`, nommer `LOOP-xx`, assigner à la 16.
5. Trig sur le pas 1 de la 16, `LEN` du trig au plus long et enveloppe AMP
   tenue (`HLD`) pour couvrir les 4 mesures *(à vérifier : valeur max de
   `LEN`)* : la boucle rejoue ce qui vient de passer. Muter les tracks
   d'origine.
6. Triturer la 16 seule : filtre, `PLAY` en REVERSE, `STRT` locké, overdrive
   (cf. [[filtres]], [[amp-overdrive-bitreduction]]).

## En live techno

- **Pont entre deux morceaux** : figer la fin du morceau A, changer de
  pattern (kit B), laisser la boucle A tourner sur la 16 sous le nouveau
  socle, puis la filtrer jusqu'à la sortir (doctrine §13, jonctions).
- **Libérer des tracks** : figer une combinaison de percs complexe (7, 8,
  12) pour réutiliser ces tracks avec d'autres sons.
- **Break sans perdre le groove** : boucle figée du plein régime, mutes sur
  toutes les tracks sauf la 16, puis filtre qui se ferme : le break garde
  l'empreinte du peak.
- STRETCH garde la boucle calée si le tempo bouge légèrement ensuite.

## Pièges

- La prise est **normalisée** : baisser le niveau de la 16 avant de la
  démuter, sinon saut de volume.
- `SRC` = MAIN capte aussi la 16 : muter la 16 avant une nouvelle prise,
  sinon on resample la boucle précédente.
- *À vérifier sur la machine* : que `R.STRT` = PLAY démarre une prise pendant
  la lecture (le manuel ne décrit que l'appui sur `[PLAY]`). D'où le
  déclenchement par seuil, calé par le kick.
- Les 66 s max laissent de la marge : 4 mesures à 190 BPM =
  4 × 4 × 60 / 190 = 5,05 s.
- Une prise occupe de la RAM de samples : nettoyer après le set (menu
  SAMPLES, cf. [[sampling-resampling]]).

## À essayer (5 min)

Pattern plein à 190 BPM, figer 4 mesures sur la 16, muter 1 à 15, faire
tourner la boucle avec le filtre qui se ferme sur 8 mesures, puis démuter le
kick et la basse ensemble sur le 1.

Source : manuel DT2 OS 1.17, §13.1, §13.2, A.2.3.

## Vidéos

Ajoutées depuis [[../veille-live]] (2026-10-07), non visionnées : la fiche
fait foi pour l'OS 1.17.

- [My favorite trick for live looping with Digitakt II](https://www.youtube.com/watch?v=uNrHomI0YB4) (vidéo entière) · DT2
- [Techno jam live with Digitakt (mute tracks, infinite loops, LFO)](https://www.youtube.com/watch?v=FNF6S-oNCiM) (vidéo entière) · DT1, principe identique
