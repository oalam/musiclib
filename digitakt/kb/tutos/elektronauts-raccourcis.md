---
tags: [digitakt, kb, tutos]
theme: Raccourcis d'écran et réglages (Elektronauts)
lot: 2
ordre: 11
source: "https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556"
auteur: communauté Elektronauts
modele: DT2
os: "1.17"
statut: draft
updated: 2026-10-23
---

# Elektronauts 11 — Raccourcis d'écran et réglages

**En une phrase** : page loop et page mute depuis le grid recording, mutes
sans quitter l'édition, sous-menus aux flèches, PTN sans tenir, sous-page
mémorisée, reset de LFO par pas ; moins de menus pendant le live.

Panorama : [[elektronauts-panorama]]. Fiches du geste : [[../page-setup]],
[[../mutes]], [[../lfo]], [[../copier-coller]], [[../microtiming-retrigs]].

## Sur notre grille

Les mutes sont le séquenceur du live ([[../../doctrine]] §4) : tout ce qui
les rend accessibles sans quitter le grid recording compte.

## Astuces

### 1. Page loop et page mute

- **Source** : [#7](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/7).
- **Pas à pas** :
  1. En GRID RECORDING, tenir `[PAGE]`.
  2. Touches 1 à 8 : sauter à la page ; touches 9 à 16 : muter une page.
- **Attention** : bugs de lecture live signalés sous l'OS 1.01, à revérifier.

### 2. Mutes depuis le grid recording

- **Source** : [#449](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/449), [#545](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/545).
- **Pas à pas** :
  1. En grid recording : `[TRK]` **puis** `[FUNC]` (dans cet ordre) : le mode
     mute s'affiche le temps de l'appui.
  2. `[FUNC]` puis `[TRK]` fait l'inverse : sortie du grid recording.

### 3. Menus secondaires aux flèches

- **Source** : [#31](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/31), [#32](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/32).
- **Pas à pas** :
  1. Flèches haut / bas : passer d'un sous-menu à l'autre dans une page.
  2. Depuis FLTR, `[FUNC] + [SRC]` ouvre le choix du type de filtre ; depuis
     SRC, le choix de machine ; flèches gauche / droite entre les choix.

### 4. PTN sans tenir, copier-coller rapide

- **Source** : [#33](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/33).
- **Pas à pas** :
  1. Appui court sur `[PTN]`, puis flèches pour la banque, touche de trig
     pour le pattern.
  2. Copier un pattern : tenir sa touche, `[FUNC] + [REC]`, lâcher ; tenir
     la touche cible, `[FUNC] + [STOP]`.
- Fiche : [[../copier-coller]].

### 5. Remember subpage

- **Source** : [#114](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/114).
- **Pas à pas** : SETTINGS > PERSONALIZE > « Remember subpage » : la machine
  rouvre chaque menu sur sa dernière sous-page.

### 6. Micro timing à tout encodeur

- **Source** : [#417](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/417).
- **Pas à pas** : trig tenu, le micro timing se règle aussi aux encodeurs, pas
  seulement aux flèches ([[../microtiming-retrigs]]).

### 7. Reset de LFO par pas

- **Source** : [#553](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/553).
- **Résultat** : la phase du LFO se recale sur le pas voulu et se conserve
  ensuite.
- **Pas à pas** :
  1. Plutôt que locker LFO.T, locker le **mode** du LFO (TRIG, HOLD, ONE ou
     HALF) sur le pas qui doit recaler.
  2. FREE sur les autres pas : la phase se conserve en passant d'un mode à
     FREE.

### 8. Changer de machine déplace les p-locks

- **Source** : [#351](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/351).
- **Pas à pas** : les locks restent à la même position d'écran et tombent sur
  le paramètre de la nouvelle machine, MIDI compris ; vérifier la page SRC
  après un changement de machine.

### 9. Quatre volumes

- **Source** : [#279](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/279).
- **Pas à pas** :
  1. Niveau du sample (page SRC) et AMP : gain staging.
  2. Mixer par track : le mix.
  3. Volume de pattern (page du compresseur) : le niveau global.
  4. LFO sur l'AMP pour le tremolo, jamais sur le mixer.
- Fiche : [[../mixer-setup]].

### 10. Clics de fin de note

- **Source** : [#215](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/215).
- **Pas à pas** : attaque, decay ou release au-dessus de 0, et notes de la
  longueur exacte du trig moins un peu.

### 11. Portamento legato

- **Source** : [#480](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/480).
- **Pas à pas** : LEGATO ON dans le SETUP ; seules les notes qui se
  chevauchent glissent, les autres restent nettes.

### 12. Renommer et ranger dans Transfer

- **Source** : [#242](https://www.elektronauts.com/t/digitakt-ii-tips-tricks/212556/242).
- **Pas à pas** : renommage et création de dossiers directement sur le
  +Drive depuis Transfer, sans passer par la machine.

## Liens

[[elektronauts-panorama]] · [[../page-setup]] · [[../mutes]] · [[../lfo]]
· [[../copier-coller]] · [[../microtiming-retrigs]] · [[../mixer-setup]]
· [[../../doctrine]] §4
