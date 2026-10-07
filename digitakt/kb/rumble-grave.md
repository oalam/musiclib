---
tags: [digitakt, kb]
theme: Rumble et grave (kick, track 2, basse)
lot: 3
ordre: 28
manuel: "§11.5-11.8, §12.3, §12.5, §13 (p55-56, 62-64, 68-69)"
os: "1.17"
statut: draft
---

# Rumble et grave : les gestes machine du §9

**En une phrase** : la recette du grave (kick, rumble, basse) est arbitrée
dans la doctrine §9 ; cette fiche regroupe les gestes DT2 dispersés dans
les autres fiches, dans l'ordre où on les fait.

## Gestes rapides

| Étape | Où | Fiche |
|---|---|---|
| Kick très réverbéré, AMP courte | page FX `REV`, reverb `DEC` long, `HPF` bas | [[send-fx-compresseur]] |
| Saturer | page AMP, `OVER` | [[amp-overdrive-bitreduction]] |
| Figer en sample | `[SAMPLING]`, `SRC` = MAIN, `R.LEN` = 16 | [[sampling-resampling]] |
| Sculpter | machine LOWPASS 4, `FREQ` bas, un peu de `RESO` ; `WIDTH` borne le haut | [[filtres]] |
| Accorder sur la tonique | `TUNE` (appuyer en tournant = demi-tons) | [[machines-src]], [[keyboard-gammes]] |
| Faire pomper | COMPRESSOR ROUTING sans la 1, `SCS` = TRK1 | [[send-fx-compresseur]] |
| Disparaître pendant les breaks | trigs de la 2 en `NOT FILL` | [[fill-conditions]] |

## Pas à pas : du kick au rumble joué

1. Track 1 : kick seul, envoi reverb à fond, `DEC` de la reverb long, un peu
   de `PRE`, aigus coupés (`LPF` de la reverb). Overdrive poussé.
2. Muter tout sauf la 1, prise d'une mesure (`SRC` = MAIN, `R.LEN` = 16,
   `R.STRT` = PLAY), retailler pour ne garder que la queue.
3. Assigner à la track 2, machine LOWPASS 4, `FREQ` bas, overdrive, `TUNE`
   sur la note du kick (doctrine §11).
4. Trigs de la 2 **sur les mêmes pas** que le kick, release courte ; ducking
   par le compresseur (`SCS` = TRK1).
5. Basse (9) en contretemps, attaque franche, `DEC` court ; base-width un peu
   monté pour laisser le sub au kick.
6. Sauvegarder le rumble en **preset** (`rumble_F#`), puis le kit.

## En live techno

- Variante **sans basse** : la 2 roule sur les doubles-croches entre les
  kicks et tient seule le rôle de la basse (doctrine §9).
- Le rumble se règle au **casque ou sur un sub** : sur des enceintes de
  bureau, on le pousse toujours trop.
- Ouvrir le `FREQ` de la 2 en perform kit sur une montée, le refermer au
  drop (cf. [[perform-kit-temp-save]]).

## Pièges

- La reverb est un **envoi partagé** : sans resampling, tout ce qui est
  envoyé à la reverb « rumble » aussi.
- Prise normalisée : régler le niveau de la 2 **sous** le kick après coup.
- Kick, rumble et basse mal accordés s'annulent dans le sub : vérifier la
  note avant de chercher un problème de niveau.

## À essayer (5 min)

Faire deux rumbles du même kick (reverb courte et longue), les comparer sur
la 2 au même niveau, garder celui qui laisse respirer la basse en
contretemps.

Source : manuel DT2 OS 1.17, §11.5-11.8, §12.3, §12.5, §13 ; doctrine §9.

## Vidéos

Ajoutées depuis [[../veille-live]] (2026-10-07), non visionnées : recettes
à comparer à la doctrine §9, qui fait foi.

- [Techno rumble kick tutorial / Elektron Digitakt jam (Almec Beats #27)](https://www.youtube.com/watch?v=eqXsdujBUoQ) (vidéo entière) · DT1
- [Techno kick with rumble — Digitakt](https://www.youtube.com/watch?v=lfKkU0DWYy0) (vidéo entière) · DT1
- [Essential hard techno techniques with the Digitakt II](https://www.youtube.com/watch?v=N2xsQEeRinA) (vidéo entière) · DT2
