---
tags: [digitakt, kb]
theme: Tracks MIDI pour piloter un synthé
lot: 5
ordre: 24
manuel: "§5.3.2, §16.3, annexe A.2.7 (p17, 87, 101-104)"
os: "1.17"
statut: draft
---

# Tracks MIDI pour piloter un synthé

**En une phrase** : n'importe laquelle des 16 tracks devient une track MIDI
en lui donnant la machine MIDI : elle ne fait plus de son, elle séquence un
synthé externe (notes, accords de 4 notes, CC, program change).

## Gestes rapides

| Action | Touches / chemin |
|---|---|
| Passer une track en MIDI | `[FUNC] + [SRC]`, catégorie SRC, machine MIDI, `[YES]` |
| Canal de sortie de la track | `[SRC]`, `CHAN` (1-16, `OFF` = track éteinte) |
| Activer / désactiver un paramètre | maintenir `[FUNC]` + appui sur le knob |
| Accord (jusqu'à 4 notes) | page TRIG 1, `NOT2`-`NOT4` (décalages depuis la note) |
| CC assignables (16) | `[FLTR]` = VAL1-8, `[AMP]` = VAL9-16 |
| Bank / program change | `[SRC]`, `BANK`, `SBNK`, `PROG` |

Branchement (§16.3) : MIDI OUT de la DT2 vers MIDI IN du synthé ; PORT
CONFIG : `OUT PORT FUNC` = `MIDI`, `OUTPUT TO` = `MIDI` (ou USB pour un
synthé logiciel sur le Mac).

## Pas à pas : une basse acid sur un synthé externe

1. Choisir une track, `[FUNC] + [SRC]`, machine MIDI.
2. `[SRC]`, `CHAN` = canal du synthé ; activer `PROG` si le synthé doit
   changer de son avec le pattern.
3. `[FLTR]` : activer VAL1, choisir le CC du cutoff du synthé, idem VAL2
   pour la résonance.
4. Programmer la ligne comme une track audio : p-locks sur VAL1 pour
   l'acid, longueur de trig courte ; pour un slide, allonger `LEN` pour que
   la note chevauche la suivante (si le synthé fait du legato, *à vérifier*).
5. LFO 1 sur VAL1 pour un balayage lent (cf. [[lfo]]).

## En live techno

- **Garder l'invariant de la doctrine** : une track MIDI prend la place d'un
  rôle existant (la 9 « basse » pilote une basse externe, la 10 « lead » un
  synthé lead), elle ne crée pas un 17e rôle. Les mutes restent les mêmes
  réflexes.
- Mutes, fills, conditions de trig et song mode marchent aussi sur les
  tracks MIDI (cf. [[mutes]], [[fill-conditions]]).
- `PROG` en p-lock sur le premier trig : chaque pattern rappelle le bon son
  du synthé.

## Pièges

- `CHAN` ne se p-locke pas.
- Plusieurs tracks sur le même canal : la track de plus petit numéro gagne
  en cas de conflit de paramètres.
- Paramètres sur `OFF` par défaut : rien n'est envoyé tant qu'on ne les a
  pas activés avec `[FUNC]` + knob.
- Deux LFO seulement sur une track MIDI (trois en audio), pas de page FX.
- Le son du synthé ne passe pas par la DT2 : il faut une table ou une
  entrée audio pour le mixer (cf. [[audio-routing-overbridge]]).

## À essayer (5 min)

Track 10 en MIDI vers un synthé (ou un synthé logiciel via USB), accord
mineur avec `NOT2` = 3 et `NOT3` = 7, VAL1 sur le cutoff, un p-lock de
VAL1 par trig.

Source : manuel DT2 OS 1.17, §5.3.2, §16.3, annexe A.2.7.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [Optoproductions — Digitakt 2 MIDI Setup](https://youtu.be/noEAqTsXL8M) (vidéo entière) · DT2, 2024
- [XNB — Elektron DIGITAKT MIDI Tracks deep dive](https://youtu.be/ZTFFs89y5gg) (vidéo entière) · DT1 : 8 tracks MIDI dédiées, sur DT2 toute track peut l'être, 2023
- [Elektron — Digitakt — The MIDI Tracks](https://youtu.be/ZyFY0o44DK8) (vidéo entière) · DT1 : 8 tracks MIDI dédiées, sur DT2 toute track peut l'être, 2017
- [Elektron Video Klub — Using MIDI with External Hardware](https://youtu.be/0Vf4GClejb0?t=241) : « turn the 16 steps into a single octave keyboard » (4:01) · DT1 : 8 tracks MIDI dédiées, sur DT2 toute track peut l'être, 2020
