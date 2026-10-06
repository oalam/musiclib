---
tags: [digitakt, kb]
theme: Parameter locks et preset locks
lot: 2
manuel: "§10.8.1, §10.8.2, §9.1.1, §11.2 (p29, 47-48, 53)"
os: "1.17"
statut: draft
---

# Parameter locks et preset locks

**En une phrase** : chaque trig peut porter ses propres valeurs de paramètres
(parameter lock) ou même un autre son du pool (preset lock, équivalent des
« sound locks » de la DT1) : c'est ce qui donne vie à une boucle de 16 pas.

## Gestes rapides

| Action | Touches |
|---|---|
| Locker un paramètre sur un trig | maintenir `[TRIG]` + tourner DATA ENTRY (GRID) |
| Retirer un lock | maintenir `[TRIG]` + appuyer sur le knob locké |
| Lock trig (sans note) | `[FUNC] + [TRIG]` (GRID), puis le maintenir et tourner |
| Locker tous les trigs de la page | `[TRIG] + [PAGE]` ou `[TRK]` + tourner |
| Preset lock | maintenir le trig + tourner LEVEL/DATA (liste du pool) |
| Enregistrer des locks en temps réel | LIVE RECORDING, tourner les knobs |
| Effacer un lock en live | LIVE, maintenir `[NO]` + maintenir le knob |
| Sauver le son d'un trig comme preset | `[TRIG] + [PRESET/KIT]` (GRID) |

## Pas à pas : accentuer un hat

1. `[RECORD]`, track 4 (hat fermé), trigs en contretemps posés.
2. Maintenir le trig du pas 15 : tourner `DEC` (page AMP) plus long, et
   `FREQ` (FLTR) plus ouvert. Le trig clignote rouge : il est locké.
3. Pour le kick alternatif : ajouter le preset au pool (`[PRESET/KIT]` >
   MANAGE > `[LEFT]` > `ADD TO PRESET POOL`), puis sur le trig du pas 13 de
   la track 1, maintenir + LEVEL/DATA, choisir le preset, relâcher.

## En live techno

- Les vélocités des banks générées se traduisent en lock de `VEL` (page
  TRIG) : n'en garder que deux niveaux (accent / normal), plus lisible.
- Lock trigs (jaunes) sur la track 15 : ouvrir un filtre ou un envoi reverb
  sur un seul pas sans déclencher de son, pour une queue de transition.
- Preset locks sur la basse (track 9) : deux timbres sur la même ligne sans
  occuper une track de plus, ce qui préserve la grille des 16 tracks.

## Pièges

- 80 paramètres lockables par pattern (un paramètre compte une fois, quel
  que soit le nombre de trigs).
- Les paramètres de la page TRIG sont sauvés avec le **pattern**, pas avec
  le preset.
- Effacer puis reposer une note trig retire tous ses locks.
- Un preset lock ne puise que dans le **pool** du projet (128 presets), pas
  dans le +Drive (cf. [[presets-kits-pool]]).

## À essayer (5 min)

Sur un hat 16e, locker `FREQ` différemment sur 4 trigs, puis `[TRIG] +
[YES]` sur chacun pour entendre la préécoute avec locks.

Source : manuel DT2 OS 1.17, §9.1.1, §10.8.1, §10.8.2, §11.2.
