---
tags: [digitakt, kb]
theme: Mixer et setup global
lot: 3
ordre: 17
manuel: "§4, §6.2.2, §9.8, §12.6-12.9 (p15, 19, 36-39, 65-67)"
os: "1.17"
statut: draft
---

# Mixer et setup global

**En une phrase** : les pages MIXER règlent les niveaux (tracks, retours
d'effets, entrées, overdrive master, volume du pattern), le menu SETUP règle
le comportement du kit et de chaque track ; **control all** agit sur toutes
les tracks d'un coup.

## Gestes rapides

| Action | Touches |
|---|---|
| Pages MIXER 1-5 (6 en dual mono) | `[FUNC] + [MOD]`, puis `[UP]/[DOWN]` (ou `[FUNC] + [MOD]` répété) |
| Niveau de la track active | LEVEL/DATA |
| Control all (toutes les tracks audio) | maintenir `[TRK]` + tourner un knob ; `[NO]` avant de lâcher `[TRK]` annule |
| Menu SETUP (KIT, TRACK) | `[FUNC] + [FLTR]` |

| Page MIXER | Contenu |
|---|---|
| 1 | compresseur master (cf. [[send-fx-compresseur]]) |
| 2 / 3 | niveaux des tracks 1-8 / 9-16 |
| 4 — FX MIXER | retours `CHR`, `DEL`, `REV`, **`MOVD`** (overdrive master) |
| 5 — EXTERNAL | entrées : `IN LR`, `DUAL`, `BAL`, envois `CHO` / `DEL` / `REV` |

Sur toutes les pages, LEVEL/DATA règle `VOL` = volume du pattern, sauvé avec
le kit.

## Pas à pas : équilibrer le set avant de le jouer

1. Pattern modèle : niveaux des 16 tracks (pages 2 / 3), kick et rumble
   d'abord, le reste autour.
2. Page 4 : retours d'effets assez bas pour que les transitions (feedback de
   delay, queue de reverb) ne dépassent pas le kick ; `MOVD` léger pour la
   cohésion.
3. Sauver le kit modèle, le propager (cf. [[presets-kits-pool]]).
4. Une fois les patterns remplis : passer de l'un à l'autre et ajuster le
   `VOL` de chaque pattern pour qu'aucune bascule ne saute en niveau.
5. SETUP > KIT > `CONTROL ALL CONFIG` : choisir les tracks touchées par
   control all (ex. tout sauf 1, 2, 9 pour garder kick, rumble et basse).

## En live techno

- Control all = la macro de transition : maintenir `[TRK]` et fermer le
  filtre ou monter l'envoi reverb sur toutes les tracks configurées, puis
  `[NO]` avant de lâcher pour revenir pile au réglage d'origine.
- `MOVD` monté sur un peak : tout le kit sature d'un geste ; le baisser au
  breakdown.
- Entrée externe (page 5) : mixer une autre machine ou un micro dans les
  effets de la DT2 sans la sampler.
- SETUP > TRACK : `OCTAVE` (octave de base du preset, utile avec les preset
  locks), portamento, `LEGATO`, et affectations de vélocité / keytrack à
  quatre paramètres (`VELOCITY MOD`) : une vélocité forte peut aussi ouvrir
  le filtre.

## Pièges

- Control all n'agit pas sur les tracks MIDI et touche **toujours** la track
  active, même hors configuration.
- Le LEVEL d'une track n'est pas lockable par trig ; pour des accents,
  locker `VOL` de la page AMP (cf. [[amp-overdrive-bitreduction]]).
- Après chargement d'un projet ou `[STOP] + [STOP]`, l'entrée externe ne
  passe dans les effets qu'après un premier trig audio.
- Niveaux, compresseur, effets et `MOVD` sont dans le **kit** : changer de
  kit les change aussi.

## À essayer (5 min)

Configurer control all sur les tracks 3-8 et 10-16, maintenir `[TRK]`,
fermer le filtre sur 4 mesures, puis `[NO]` avant de lâcher : vérifier le
retour exact.

Source : manuel DT2 OS 1.17, §4, §6.2.2, §9.8, §12.6-12.9.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [XNB — Digitakt II deep dive guide](https://youtu.be/8zXBNqRstxQ?t=7024) : « Mixer » (1:57:04) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=1517) : « Setting the track level » (25:17) · DT2, 2024
