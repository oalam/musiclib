---
tags: [technique, stems, demucs, dsp, mix-theory]
date: 2026-05-31
---

# Cleanup techno-aware des stems Demucs

Note pédagogique sur le post-processing appliqué aux stems Demucs pour
techno/tribe/hardtek. Compagne du module `scripts/analyzer/stems_cleanup.py`
et du flag `stems.py --cleanup`. Voir [[SPEC]] pour l'état d'implémentation.

## Le problème : pourquoi Demucs fuit sur la techno

Demucs (modèle `htdemucs`) a été entraîné sur **MUSDB18** — 150 tracks
majoritairement pop/rock. Le réseau a appris à séparer :

- `drums` = batterie acoustique avec hi-hat et snare aigus
- `bass` = bass guitar pitched
- `other` = guitares + claviers + synthés
- `vocals` = voix humaine

En **techno**, ces définitions se brouillent :

| Élément techno | Pourquoi le modèle hésite |
|---|---|
| Kick | Pas une grosse caisse acoustique : 50-80 Hz pur (sub-bass + transient). Demucs hésite « drum ou bass ? » → met une partie dans `bass.wav` |
| Bassline synthé | Chevauche le kick fondamental. Demucs sépare mal |
| Absence de voix | Le modèle ne trouve rien, met du **bruit / leak de leads** dans `vocals.wav` |

Résultat : `drums.wav` correct, `bass.wav` pollué de sub-kick et parfois
de leads, `vocals.wav` souvent bruité sur tracks instrumentaux.

## Trois règles domain-aware

### Règle 1 — highpass `bass.wav` à 60 Hz

> Le sub 20-60 Hz appartient au kick territory, pas à la bassline.

Théorie audio :
- Un kick techno typique fonde son **fundamental** entre 40 et 60 Hz
  (Si bémol grave ≈ 58 Hz, Mi grave ≈ 41 Hz)
- Une bassline pitched a son fundamental généralement 60-200 Hz
  (A1=55 Hz, A2=110 Hz, A3=220 Hz)
- À 60 Hz on coupe sous le kick fundamental ET sous la bassline pitched

Ce qu'on retire : le sub-kick résiduel qui faisait pulser `bass.wav`
en doublure du kick.

### Règle 2 — lowpass `bass.wav` à 500 Hz

> Une bassline techno ne monte (presque) jamais au-dessus de 500 Hz.

Une bassline électronique a typiquement :
- Fundamental : 40-200 Hz
- 2e harmonique : 80-400 Hz
- 3e harmonique : 120-600 Hz

Au-delà de 500 Hz, on est dans le territoire des **leads** (claviers,
synthé acid, voix). Donc tout signal au-dessus dans `bass.wav` = fuite.

Cas limite : **acid bass TB-303** avec résonance ouverte peut monter
plus haut. L'essentiel reste sous 1 kHz, on perd peu en coupant à 500.

### Règle 3 — merge `vocals.wav` dans `other.wav` si RMS < -40 dBFS

> Si vocals.wav est quasi-silencieux, c'est un track instrumental — le
> contenu est du leak qu'on récupère dans other.

Pourquoi **RMS** et pas peak :
- **Peak** = amplitude max instantanée. Sensible aux transients (1 sample
  fort = peak haut, pas représentatif).
- **RMS** (root mean square) = moyenne quadratique sur la durée.
  Représente l'**énergie soutenue** du signal. Plus pertinent pour
  « est-ce silencieux globalement ? ».

Pourquoi **-40 dBFS** :
- Signal à -40 dBFS = amplitude 1% (1/100ᵉ) du max
- En dessous = bruit numérique ou leak insignifiant
- Au-dessus = il y a du contenu (voix ou lead leaké à conserver)

Seuil **conservateur** : on préfère garder un vocals.wav potentiellement
utile plutôt qu'écraser.

Le merge est une simple **somme sample-par-sample** :
```
other_clean[i] = other[i] + vocals[i]
```
Pas de clipping nouveau : Demucs garantit `drums + bass + other + vocals
≈ mix_original`, donc additionner vocals à other revient à un sous-
ensemble du mix de départ.

## Le filtre Butterworth, brièvement

Un filtre Butterworth a une **bande passante plate** (pas de ripple) et
atténue progressivement au-delà du cutoff. Ordre 4 = chute de 24 dB par
octave après cutoff.

À 60 Hz cutoff, ordre 4 :

| Fréquence | Atténuation |
|---|---|
| 60 Hz | -3 dB (cutoff) |
| 30 Hz (1 octave plus bas) | -27 dB (quasi muet) |
| 120 Hz (1 octave plus haut) | ~0 dB (passe) |

On utilise `scipy.signal.filtfilt` qui applique le filtre **deux fois
(avant + arrière)** pour avoir une **réponse à phase zéro** : pas de
décalage temporel introduit. Critique pour aligner les stems entre eux.

## Résultats observés sur la library oalam (62 tracks, 2026-05-31)

- **62/64 tracks** ont reçu le cleanup `bass` (les 2 misses = audio
  absent du dossier `library/audio/`)
- **10 tracks** ont eu leur `vocals.wav` mergé (RMS < -40 dBFS) : tous
  des tracks **purement instrumentaux** — Floxytek, Hertz, Kangding Ray,
  Kontinum, Ororr, etc.
- **Aucun track à voix réelle** mergé (BAD BUNNY, Quantic/Gongora,
  MAICEE etc. ont gardé leur `vocals.wav` intact)

Le seuil -40 dBFS sépare bien les deux populations.

## Limites à connaître

### Le cleanup est destructif

Les stems d'origine sont **écrasés**. Pour comparer avant/après :
```bash
cp library/stems/<slug>/bass.wav /tmp/bass_cleaned.wav
python stems.py --force <slug>  # ré-extrait le brut
# bass.wav actuel = brut. Compare aux /tmp/bass_cleaned.wav
```

### Règles techno-aware uniquement

Sur de la **pop/rock**, le cleanup empire le résultat :
- Bass guitar peut monter à 1 kHz → lowpass 500 Hz la rogne
- Voix réelle dans vocals → seuil -40 dBFS la garde, OK mais à vérifier

Pour ta library qui est ~95% électronique, ROI net positif. Mais si tu
ajoutes du Zero 7 ou du BAD BUNNY pop, lance `--force` sans `--cleanup`
pour eux.

### Filtres Butterworth = ringing résiduel

Petites oscillations autour du cutoff. Invisible à l'écoute normale,
visible sur spectrogramme proche du seuil. Pas un problème en pratique.

### Pas une vraie séparation

On déplace l'énergie selon des règles, on ne crée pas de signal nouveau.
Si Demucs a mal séparé un kick dans `other.wav` (rare), le cleanup ne
le récupère pas. Pour ça il faudrait un fine-tune Demucs sur techno —
voir [[SPEC#État Phase 6]] pour les voies catalogues.

## Vérification à l'oreille — ce qu'on doit entendre

| Stem | Avant cleanup | Après cleanup |
|---|---|---|
| `drums.wav` | identique | identique |
| `bass.wav` | bassline + pulse fantôme du kick en sub | bassline plus claire, sans la fantôme |
| `other.wav` | mélodies/FX | identique (sauf si vocals mergé : alors un peu plus riche) |
| `vocals.wav` | bruit + leaks de leads (track instrumental) | zéros (si mergé) ou inchangé |

Si le brut sonne déjà bien sur un track donné, le cleanup ne fait rien
de magique — il améliore surtout les tracks où Demucs a clairement
fuité.

#technique #stems #demucs #dsp #cleanup
