---
tags: [digitakt, kb]
theme: Tempo et métronome
lot: 1
ordre: 5
manuel: "§7.3, §17 (p22-23, 89)"
os: "1.17"
statut: draft
---

# Tempo et métronome

**En une phrase** : fixer le BPM du set (global ou par pattern), le swing,
et les outils pour caler à l'oreille : tap, nudge, métronome.

## Gestes rapides

| Action | Touches |
|---|---|
| Menu TEMPO | `[TEMPO]` |
| BPM entier / par 4 | DATA ENTRY A (appuyer en tournant = pas de 4) |
| BPM décimal | DATA ENTRY B |
| Tempo projet ou par pattern | `[FUNC]` + DATA ENTRY E |
| Préparer un BPM sans l'appliquer | `[FUNC]` maintenu + A (« PREP. »), appliqué au relâchement |
| Swing (50-80 %) | DATA ENTRY D |
| Tap tempo | `[FUNC] + [TEMPO]` en rythme (moyenne dès 4 taps) |
| Nudge ±10 % temporaire | `[LEFT]` / `[RIGHT]` maintenus, en lecture |
| Métronome on / off | `[TEMPO] + [YES]` |

## Pas à pas

1. `[TEMPO]`, choisir le mode : **projet** (un BPM pour tout) ou **pattern**
   (chaque pattern porte le sien).
2. Régler le BPM avec A, affiner avec B.
3. Swing avec D si besoin (souvent 50 % en techno droite).
4. Métronome : `METRO` on, `SIG.` (signature), `PREROLL` (mesures de décompte
   avant LIVE RECORDING), `VOL`.

## En live techno

- **Mode projet** pour un set continu : un seul BPM, monté ou descendu à la
  main. Le geste « PREP. » (`[FUNC]` maintenu + A) permet de préparer
  190 → 195 et de le déclencher pile au relâchement, sur un drop.
- **Mode pattern** si chaque bank doit garder le tempo de son morceau de
  référence (cf. `bpm` dans `library/digitakt/<slug>.json`) : attention aux
  sauts de tempo à la bascule, à réserver aux ruptures voulues (ouverture
  DnB, ralenti dubstep).
- Le nudge sert à caler la DT2 à l'oreille sur une autre source (platine,
  sound system d'un autre live) sans toucher au BPM réglé.

## Pièges

- En mode pattern, copier un pattern copie aussi son BPM.
- Le nudge est temporaire : relâcher la touche ramène au tempo réglé.
- Le `PREROLL` ne joue qu'en LIVE RECORDING.

## À essayer (5 min)

Mode projet à 190 BPM, lancer un pattern, maintenir `[FUNC]` et monter A à
196, relâcher sur le 1 d'une mesure. Puis taper `[FUNC] + [TEMPO]` sur un
morceau joué à côté et comparer.

Source : manuel DT2 OS 1.17, §7.3, §17.

## Vidéos

Repérées par les chapitres YouTube (non visionnées en entier) ; la fiche fait foi pour l'OS 1.17.

- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=1424) : « Metronome » (23:44) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=1480) : « Changing the tempo (bpm) » (24:40) · DT2, 2024
- [True Cuckoo — Digitakt 2 Beginner's MEGA TUTORIAL](https://youtu.be/651_lCCJ1-w?t=1827) : « Set Preroll for Live rec count-in » (30:27) · DT2, 2024
