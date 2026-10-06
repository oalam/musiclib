---
tags: [digitakt, kb]
theme: Send FX et compresseur master
lot: 3
ordre: 16
manuel: "§9.8.1, §12.1-12.7, §14.6.1 (p37, 61-65, 80)"
os: "1.17"
statut: draft
---

# Send FX (delay, reverb, chorus) et compresseur master

**En une phrase** : un delay, une reverb et un chorus partagés par tout le
pattern (chaque track dose son envoi), plus un compresseur sur la sortie
avec sidechain : la colle et le pompage du set.

## Gestes rapides

| Action | Touches |
|---|---|
| Pages SEND FX (delay, reverb, chorus) | `[FUNC] + [FX]`, `[UP]/[DOWN]` |
| Pages MIXER (compresseur, niveaux de tracks) | `[FUNC] + [MOD]`, `[UP]/[DOWN]` |
| Envois par track | `[FX]` : `DEL`, `REV`, `CHR` |
| Tracks routées au compresseur | `[FUNC] + [FLTR]` > KIT > COMPRESSOR ROUTING (page 1 : tracks ; `[DOWN]` page 2 : entrées et effets ; pas de tracks MIDI) |

Delay : `TIME` en 128e de mesure (16 = croche, 12 = double-croche pointée,
32 = noire), `X` ping-pong, `WID`, `FDBK`, `HPF`, `LPF`, `REV` (vers la
reverb). Reverb : `PRE`, `DEC`, `FREQ` / `GAIN` (amorti des aigus), `HPF`,
`LPF`. Compresseur : `THR`, `ATK`, `REL`, `MUP`, `RAT` (1,5 / 2 / 3 / 4 /
6 / 8 / 16 / 20), `SCS` (source sidechain), `SCF` (filtre sidechain : négatif
= passe-bas, réagit au grave ; positif = passe-haut, évite le pompage),
DRY/WET.

Le compresseur se règle à deux endroits : le **routing** dit qui est
compressé, la **source** (`SCS`) dit qui déclenche. Valeurs de `SCS` :
`TRK1`-`TRK16` (une track), `COMP MIX` (les tracks routées au compresseur),
`NOT COMP` (les tracks **non** routées), `MAIN` (la sortie main), `IN LR`
(ou `IN L` / `IN R` si `DUAL` = ON dans le mixer externe).

## Pas à pas : pompage sur le kick

1. COMPRESSOR ROUTING : toutes les tracks **sauf** 1 (kick). Le rumble
   (2), la basse (9) et les nappes (11) sont ceux qui doivent pomper. Le
   kick routé se ferait écraser par sa propre détection.
2. Page compresseur : `SCS` = TRK1 (ou `NOT COMP` si seul le kick est hors
   routing), `SCF` négatif (réagit au grave du kick).
3. `RAT` 4 ou plus pour un pompage net, `ATK` au plus rapide, `REL` court à
   moyen, réglé pour que le niveau remonte juste avant le kick suivant.
4. Descendre `THR` jusqu'à entendre nettement le creux, puis remonter un
   peu ; compenser avec `MUP` sans exagérer.
5. DRY/WET à 127 pour un ducking franc, plus bas pour un effet plus doux
   (compression parallèle).

Résultat : le kick passe sec, tout le reste se creuse à chaque coup.

## Kick fantôme : garder le pompage pendant les breaks

Problème : muter le kick pour un break arrête aussi le sidechain. Astuce
partagée sur Elektronauts :

1. Copier le kick sur la track 16 (la réserve de la grille, cf. doctrine
   §1) : même sample, mêmes trigs (cf. [[copier-coller]]).
2. AUDIO ROUTING > `TO MAIN` : retirer la 16, elle devient inaudible (cf.
   [[audio-routing-overbridge]]).
3. `SCS` = TRK16.
4. Le vrai kick peut alors être muté ou mis en `FILL` = OFF pendant les
   breaks (cf. [[mutes]], [[fill-conditions]]) : le pompage continue.
5. Inverse : muter la 16 arrête le pompage à un moment précis.

*À vérifier sur la machine* : qu'une track retirée de `TO MAIN` déclenche
encore le sidechain (non confirmé par le manuel ni sur le forum).

## En live techno

- Delay en croche pointée (`TIME` 24) sur le clap, `HPF` haut pour ne pas
  salir le bas : l'espace tribe classique.
- Transition : monter `FDBK` du delay à fond sur la fin d'un pattern, puis
  couper les tracks (cf. lot 4, mutes) : la queue fait le pont.
- Reverb : `HPF` haut pour ne jamais réverbérer le sub (kick, basse).
- Ce routing fait du compresseur un **ducker**, pas une colle sur tout le
  mix. Pour avoir les deux : pomper avec des LFO de volume sur les tracks
  concernées (cf. [[lfo]]) et garder le compresseur en compression master
  classique (tout routé, `SCS` = `MAIN`, `RAT` 2, `SCF` positif).
- Le niveau d'ensemble du pattern (`VOL` du mixer) est sauvé avec le kit :
  équilibrer les patterns entre eux avant le set.

## Pièges

- Les effets sont **par pattern** : changer de pattern peut changer la
  reverb. Garder les mêmes réglages via le kit modèle
  (cf. [[presets-kits-pool]]).
- Kick dans le routing **et** en source : il s'écrase lui-même.
- `NOT COMP` prend **toutes** les tracks hors routing : si une perc ou
  l'atmo en sort aussi, elle déclenche le pompage.
- Kick fantôme : il occupe la 16, qui ne peut plus servir de track MIDI
  dans ce kit ; il doit suivre les changements de trigs du vrai kick.
- `FDBK` élevé = signal qui s'emballe et devient très fort.
- Delay et reverb continuent après `[STOP]` ; `[STOP]` deux fois coupe
  presque net.

## À essayer (5 min)

Pompage ci-dessus sur un pattern kick + basse + hats, puis comparer `SCF`
négatif et positif, et noter le `REL` qui sonne le mieux à 190 BPM.
Puis monter le kick fantôme sur la 16, muter la 1 et vérifier que le
rumble pompe toujours.

Sources : manuel DT2 OS 1.17, §9.8.1, §10.1.2, §12, §14.6.1 ; Elektronauts
(fils *Digitakt II Tips & Tricks*, *Introducing Digitakt II*, *Can I use the
digitakt compressor on external audio?*, *Dummy Sidechain for Digitakt 2*).
