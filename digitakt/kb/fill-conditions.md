---
tags: [digitakt, kb]
theme: FILL et conditions de trig
lot: 3
ordre: 18
manuel: "§10.7.3, §10.8.4, §11.2 (p48-49, 53-54)"
os: "1.17"
statut: draft
---

# FILL et conditions de trig

**En une phrase** : une condition sur un trig décide s'il joue (probabilité,
1 tour sur N, premier ou dernier passage, mode FILL) : on prépare les
variations dans le pattern et on les déclenche en live sans rien
reprogrammer.

## Gestes rapides

| Action | Touches |
|---|---|
| FILL pendant un tour de pattern | `[YES] + [PAGE]` |
| FILL tant qu'on tient | maintenir `[PAGE]` (hors GRID) |
| FILL verrouillé | maintenir `[PAGE] + [YES]`, lâcher `[PAGE]` d'abord ; `[PAGE]` pour libérer |
| Condition d'un trig | maintenir le trig (GRID / STEP), page TRIG 1, knob H `COND` |
| Probabilité de la track | page TRIG 1, `PROB` (lockable par trig) |

Conditions : `FILL` on / off (paramètre à part, page TRIG 1), `PRE` / `NOT
PRE` (dernière condition de la track vraie / fausse), `NEI` / `NOT NEI`
(idem sur la track précédente), `1ST` / `NOT 1ST` (premier tour), `LST` /
`NOT LST` (dernier tour avant de changer de pattern), `A:B` (joue au tour A
sur un cycle de B, ex. `4:4` = un tour sur quatre).

## Pas à pas : fill de caisse à la main

1. `[RECORD]`, track 3, dernière page : poser un roulement (cf.
   [[microtiming-retrigs]]).
2. Maintenir chaque trig du roulement, `FILL` = ON : ils ne jouent qu'en
   mode FILL.
3. Sur les claps normaux de la même page : `FILL` = OFF (ils se taisent
   pendant le fill).
4. En lecture, maintenir `[PAGE]` sur la dernière mesure : le fill remplace
   le clap.

## En live techno

- `LST` sur le riser et l'impact de la track 15 : ils ne jouent qu'au
  **dernier** tour avant la bascule de pattern, donc toujours au bon moment
  dans une chaîne (cf. lot 4).
- `4:4` sur un crash ou un open hat : marque le début de chaque phrase de 4
  tours sans le programmer 4 fois.
- `PROB` 50-70 % sur une perc ghost : la boucle ne se répète jamais tout à
  fait.
- Préparer les fills dans le **pattern modèle** : ils sont recopiés dans
  chaque pattern du set (cf. [[copier-coller]]).

## Pièges

- La condition `FILL` ne joue que si le mode FILL est actif.
- `[PAGE]` maintenu n'active pas le FILL en GRID RECORDING (il sert aux
  pages).
- `A:B` compte les tours de la **track** si elle est plus courte que le
  pattern (mode PER TRACK).
- `NEI` regarde la track **précédente** (la 4 regarde la 3).

## À essayer (5 min)

Hat ouvert en `4:4`, clap de fill en `FILL` ON, riser en `LST` ; chaîner
deux patterns et vérifier que le riser tombe juste avant la bascule.

Source : manuel DT2 OS 1.17, §10.7.3, §10.8.4, §11.2.
