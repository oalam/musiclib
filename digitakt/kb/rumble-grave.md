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
| Saturer | page FX, `OVER` (`OD.RT` = PRE pour saturer avant le filtre) | [[amp-overdrive-bitreduction]] |
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
- Variante **sans track 2** : rumble fabriqué dans la queue sèche du kick
  (lock trigs, LFO one-shot ou delay en contretemps), plus sec et plus
  tribe ; recette dans [[tutos/maison-rumble-dans-le-kick]].

## Repères chiffrés des sources

Valeurs relevées dans [[../veille-theorie]] §F, données pour 125-140 BPM
et à recaler sur nos tempos ; la doctrine §9 reste la recette, ceci sert
de point de départ pour les réglages.

| Étape | Repère | À 180-200 BPM |
|---|---|---|
| Kick source | 150-300 ms, fondamentale 50-65 Hz, accordé tonique / quinte / octave | idem, note sur la queue (KT5) |
| Avant la reverb | passe-haut 100-150 Hz (Myloops) **ou** 30 Hz (Futureproof) : désaccord, deux départs | `HPF` de la reverb, à trancher à l'oreille |
| Reverb | 100 % wet, pré-delay 0, `DEC` 1,5 s au-dessus de 135 BPM, jamais plus de 4 s | la croche vaut 60 / 190 / 2 = 158 ms : viser 1 à 1,5 s |
| Après la reverb | passe-bas 24 dB/oct à 200-250 Hz (peak) ou 130-170 Hz (hypnotique), passe-haut 30 Hz | LOWPASS 4 de la 2, étalonné (fiche [[filtres]]) |
| Saturation | après la reverb (Futureproof), douce sur 150-400 Hz, mix 30-50 % (Myloops) | resample puis `OVER` de la 2, `OD.RT` = PRE |
| Ducking | ratio 4:1 à 8:1, attaque 0,1-1 ms, release une croche (100-200 ms), 6-12 dB | `SCS` = TRK1 ; release 150-170 ms à la croche |
| Reverb, piège | diffusion haute, **aucune modulation** sur la queue (sinon le sub « wobble »), pas de petite pièce (boxy), pas de cathédrale au-delà de 3 s | la reverb DT2 n'a pas de modulation : rien à faire |
| Resample | bounce de 2 mesures, crête vers -6 dBFS sans écrêter, puis couper l'envoi d'origine ; un second traitement (saturation, filtre) est possible sans boucle de retour | prise normalisée : baisser `VOL` de la 2 après coup ; `OVER` et LOWPASS 4 sur le sample figé |
| Pitch du rumble | **-5 à -12 demi-tons** en vari-speed (pas de correction de formants, pas de granulaire) ; un shifter qui fait « bouger » la hauteur est un piège | `TUNE` de la 2 (appuyer en tournant = demi-tons), machine ONESHOT ou REPITCH ; vérifier la note contre le kick (KT5) |
| Couche sinus | sinus **une octave sous** la fondamentale du kick, attaque lente 200 ms, mixée 10-12 dB sous le rumble | second preset de la 2 ou la 9 en variante sans basse, `ATK` 200 ms, sample sinus accordé |
| Ducking, piège | lookahead désactivé, sinon le creux arrive après l'attaque du kick | sans objet sur la DT2 ; sur le Mac, « Pre-comp » de ReaComp à 0 ([[tutos/maison-grave-projet-reaper]] §2.3) |
| Ducking qui vit | sidechain **automatisé** : moins de ducking en intro, à fond à partir du drop | `THR` du compresseur en perform kit (fiche [[perform-kit-temp-save]]), ou `ATK` de l'AMP de la 2 par pattern |
| Niveau | rumble resamplé mixé **sous le kick**, mono sous 120 Hz ; réduction de gain 6-12 dB à chaque kick ; si le rumble noie le kick sur moniteurs, passe-bas vers 170 Hz | la 2 sous la 1, pan centré |
| Vie du rumble | passe-bas résonant (20-30 %) 140-280 Hz automatisé sur 16-32 mesures, en courbe plutôt qu'en rampe ; send qui bouge de 1-2 dB (Bonedo) | LFO lent sur `FREQ` de la 2 (KT9, KT11) |
| Break | second reverb de 6 s ou plus, passe-haut vers 300 Hz : le rumble devient nappe | reverb `DEC` à fond et `HPF` monté sur un pattern de break, ou riser de la 15 (doctrine §5) |

Variantes sans reverb relevées sur Syntakt : kick dupliqué et décalé de 2
pas avec passe-haut et delay, **LFO one-shot sur le send** pour n'envoyer
que le corps du kick, rumble par résonance de filtre et p-locks seuls ;
même famille que [[tutos/maison-rumble-dans-le-kick]].

## Rumble par sample et couche de poids

Myloops donne une seconde recette qui ne passe pas par la reverb : un
**sample** (bruit filtré, drone, field recording, loop) traité comme le
rumble, passe-haut 30 Hz, passe-bas 200-250 Hz, même sidechain sur le kick,
saturation douce, mixé 3 à 6 dB sous le niveau où on l'entend seul. Sur la
DT2 c'est la recette la plus directe : un sample de drone ou de bruit sur
la 2, LOWPASS 4 fermé, `OVER`, compresseur `SCS` = TRK1, `TUNE` sur la
tonique. Les sources sont dans la banque (fiche [[../kt-banque-samples]],
branche TONAL, drones et textures).

La **combinaison** des deux est la cible : le rumble par reverb pour
l'interaction dynamique avec le kick (il gonfle et se creuse à chaque
coup), la couche sample pour le poids constant qui ne dépend pas du
kick. En machine, deux presets de la 2 (`rumble_F#` et `drone_F#`)
chargés selon le pattern, ou le drone sur la 9 quand la basse en
contretemps n'est pas jouée (variante sans basse, doctrine §9).

Ce que l'article dit du reste du mix, à recouper avec doctrine §9 et §12 :
passe-haut 200-300 Hz sur synthés et percussions sauf besoin de grave ;
la basse sidechainée sur le kick **avec la même forme** que le rumble ;
la basse peut disparaître dans les sections principales, le rumble suffit ;
vérifier sur moniteurs, casque, téléphone et **en mono** : si le rumble
disparaît en mono, le grave est stéréo.

## Dépannage (Myloops)

| Symptôme | Geste | Sur la DT2 |
|---|---|---|
| Kick sans punch | ducking plus rapide ou plus profond, rumble baissé de 2-3 dB | `ATK` du compresseur au minimum, `THR` plus bas, `VOL` de la 2 |
| Mix boueux | passe-bas du rumble à 180 Hz ou moins ; passe-haut avant reverb mal réglé | `FREQ` de la 2 ; `HPF` de la reverb avant resample |
| Rumble inaudible sur téléphone | saturation sur 150-400 Hz (harmoniques 2 et 3) | `OVER` de la 2 avec `OD.RT` = PRE |
| Statique après quelques mesures | automatiser le cutoff ou le seuil du sidechain | LFO lent sur `FREQ`, `THR` en perform kit |
| Conflit avec la basse | notch sur la basse aux pics du rumble, sidechain de la basse | base-width de la 9 monté, `SCS` = TRK1 pour la 9 aussi |
| Wobble dans le sub | couper la modulation de la reverb, relever le passe-haut avant reverb | `HPF` de la reverb |
| Disparaît en mono | mono sous 120 Hz | pan de la 2 centré, pas de chorus ni de width sur la 2 |
| Boom qui s'accumule | decay plus court, ducking plus profond | `DEC` de la reverb, `THR` plus bas ; jamais plus de 4 s de queue |
| Rumble qui masque le transitoire | baisser le rumble, passe-bas vers 170 Hz | `VOL` et `FREQ` de la 2 |

## Pièges

- La reverb est un **envoi partagé** : sans resampling, tout ce qui est
  envoyé à la reverb « rumble » aussi.
- Prise normalisée : régler le niveau de la 2 **sous** le kick après coup.
- Kick, rumble et basse mal accordés s'annulent dans le sub : vérifier la
  note avant de chercher un problème de niveau.
- Un kick déjà long (600 ms) ne fait pas un rumble : la reverb l'étale
  sans rien ajouter. Partir d'un kick de 150-300 ms, le sub de la queue
  coupé avant la reverb, sinon le sub devient un drone flou.
- Saturation trop forte : du « fizz » au lieu d'harmoniques. Drive faible,
  mix 30-50 %, écouter sur téléphone pour juger.

## À essayer (5 min)

Faire deux rumbles du même kick (reverb courte et longue), les comparer sur
la 2 au même niveau, garder celui qui laisse respirer la basse en
contretemps.

Source : manuel DT2 OS 1.17, §11.5-11.8, §12.3, §12.5, §13 ; doctrine §9.
La même recette sur le Mac, plug-in par plug-in (ReaVerbate, Trash Lite,
ReaComp en sidechain) : [[tutos/maison-grave-rumble]] (hub
[[tutos/maison-sounddesign-grave-reaper]]).

## Vidéos

Ajoutées depuis [[../veille-live]] (2026-10-07), non visionnées : recettes
à comparer à la doctrine §9, qui fait foi.

- [Techno rumble kick tutorial / Elektron Digitakt jam (Almec Beats #27)](https://www.youtube.com/watch?v=eqXsdujBUoQ) (vidéo entière) · DT1
- [Techno kick with rumble — Digitakt](https://www.youtube.com/watch?v=lfKkU0DWYy0) (vidéo entière) · DT1
- [Essential hard techno techniques with the Digitakt II](https://www.youtube.com/watch?v=N2xsQEeRinA) (vidéo entière) · DT2

## Sources écrites

- Myloops, *How To Build a Techno Kick Rumble That Actually Mixes* :
  <https://www.myloops.net/creating-techno-kick-rumbles> `[V]`
- Futureproof, *How to Make Hard Techno* :
  <https://futureproofmusicschool.com/blog/making-hard-techno-a-path-to-unique-sound-design> `[V]`
- Gearnews, *Sidechain Compression in Techno* :
  <https://www.gearnews.com/sidechain-compression-in-techno-workshop/> `[V]`
- Bonedo, *Bass Drum Rumble & Rattle for Techno* (allemand) :
  <https://www.bonedo.de/?p=932209> `[V]`
- Elektronauts, *Elektron Syntakt techno rumble* :
  <https://www.elektronauts.com/t/elektron-syntakt-techno-rumble/178253> `[V]`
