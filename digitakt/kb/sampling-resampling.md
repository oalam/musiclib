---
tags: [digitakt, kb]
theme: Sampling et resampling interne
lot: 3
ordre: 11
manuel: "§7.5, §13.1-13.4 (p23, 68-70)"
os: "1.17"
statut: draft
---

# Sampling et resampling interne

**En une phrase** : la DT2 enregistre une entrée externe, l'USB, une de ses
tracks ou sa sortie principale ; resampler sa propre sortie est le moyen de
fabriquer le rumble, des boucles figées ou des queues de transition.

## Gestes rapides

| Action | Touches |
|---|---|
| Menu SAMPLING | `[SAMPLING]` |
| Armer / désarmer | `[SAMPLING] + [YES]` / `[SAMPLING] + [NO]` |
| Enregistrer tout de suite | `RECORD NOW` + `[YES]` (ignore seuil et ARM) |
| Préécouter après la prise | `[FUNC] + [YES]` |
| Abandonner la prise | `[FUNC] + [NO]` |
| Menu SAMPLES (+Drive, RAM) | `[FUNC] + [SAMPLING]` |

Paramètres : `SRC` (MAIN, USB, TRK1-16, IN), `CHAN` (stéréo, mono L / R /
L+R), `R.LEN` (1-128 pas ou MAX = 66 s), `R.STRT` (au `[PLAY]` ou au seuil),
`THRES`, `ARM`. Après la prise : `TRIM START` (E), `TRIM END` (H), zoom (F).

## Pas à pas : rumble à partir du kick

1. Track 1 : kick avec beaucoup de reverb (envoi `REV` page FX, `DEC` long
   sur la reverb, cf. [[send-fx-compresseur]]). Couper les autres tracks.
2. `[SAMPLING]` : `SRC` = MAIN, `CHAN` = MONO L+R, `R.LEN` = 16 (une
   mesure), `R.STRT` = PLAY.
3. Armer, `[PLAY]` : la prise dure exactement une mesure au tempo du set.
4. Retailler (E / H), `[YES]`, nommer `RUMBLE-190`, assigner à la track 2.
5. Track 2 : filtre passe-bas bas (cf. [[filtres]]), trigs sur les mêmes pas
   que le kick, avec ducking (cf. [[send-fx-compresseur]], doctrine §9).

## En live techno

- `R.LEN` en pas = des boucles qui tombent juste au BPM du set : figer 4
  mesures de percs complexes (`R.LEN` 64) pour libérer des tracks.
- `SRC` = TRK n enregistre une seule track. *À vérifier* : si la reverb et
  le delay (effets d'envoi globaux) sont inclus ; sinon passer par MAIN en
  coupant les autres tracks.
- Échantillonner la fin d'une reverb ou d'un delay en feedback pour faire un
  « impact » de la track 15.

## Pièges

- La prise est **normalisée automatiquement** : régler le niveau ensuite sur
  la track, pas en comptant sur le volume de la prise.
- `MON` = PRE MIX coupe l'entrée externe dans le mixer : remonter `IN L R`
  sur la page EXTERNAL MIXER sinon on n'entend rien.
- Le son enregistré depuis IN est toujours **sec** (sans effets DT2).
- 66 s max par prise, disponibles même si les 400 Mo du projet sont pleins.

## À essayer (5 min)

Faire le rumble ci-dessus, puis refaire la prise avec `R.LEN` = 8 et
comparer les deux en `FORWARD LOOP` (page SRC).

Source : manuel DT2 OS 1.17, §7.5, §13.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [XNB — DIGITAKT II Sampling](https://youtu.be/tDBeHZV-qnU) (vidéo entière) · DT2, 2024
- [Optoproductions — Digitakt 2 Creative Resampling](https://youtu.be/pvR1gMepME0) (vidéo entière) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=4616) : « Sampling your first sample » (1:16:56) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=4795) : « Sample a loop » (1:19:55) · DT2, 2024
