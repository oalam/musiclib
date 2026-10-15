---
tags: [digitakt, kb, theorie, kt, index]
updated: 2026-10-15
spec: "7.M"
---

# KB théorie — notes de KT

Notes de transmission (KT) sur la **construction rythmique et harmonique**
d'un morceau, style par style, pour enrichir le vocabulaire de musicien par
la pratique. Source : [[../../veille-theorie]] (veille du 2026-10-15) ;
décisions : [[../../../SPEC]] « Décisions 7.M ». Les fiches de [[../_index]]
disent *comment* faire le geste sur la machine ; une KT dit *pourquoi* et
nomme les choses, puis renvoie aux fiches.

## Format d'une KT

Frontmatter : `tags: [digitakt, kb, theorie, kt]`, `theme`, `lot`, `ordre`,
`styles` (liste), `statut` (`à rédiger` → `draft` → `vérifié` une fois les
exercices joués). Sections, dans cet ordre :

1. **En une phrase**
2. **Signature** : tableau tempo / patterns 16 pas (théorique et, en
   regard, pattern moyen tiré de la passe `rhythm_signature` ci-dessous)
3. **Vocabulaire** : 5 à 10 termes, une phrase chacun
4. **Pourquoi ça marche** : la théorie, concret avant abstraction
5. **Sur la DT2** : 2 ou 3 exercices de 5-10 min sur la grille de la
   [[../../doctrine]] §1, renvoi aux fiches KB pour le geste
6. **Pièges**
7. **Ressources** : sources écrites et livres, statut `[V]` / `[R]` repris
   de la veille ; pas de vidéos
8. **Liens** : fiches KB, doctrine, sounddesign, patches Tidal

Convention : 16 pas = 1 mesure 4/4 en doubles croches ; `x` trig, `.` vide,
`X` accent.

## Les 19 KT (Dataview)

```dataview
TABLE WITHOUT ID ordre AS "#", file.link AS "KT", lot AS "Lot", styles AS "Styles", statut AS "Statut"
FROM "digitakt/kb/theorie"
WHERE ordre
SORT lot ASC, ordre ASC
```

### Lot 1 — Socle rythmique

| # | KT | Fichier | Apporte | Renvoie à | Statut |
|---|---|---|---|---|---|
| 1 | Cellules rythmiques | [[kt-cellules-rythmiques]] | tresillo, cinquillo, claves son / rumba, hémiole, table E(k,n), rotation | [[../euclidien]] | draft |
| 2 | Polymétrie, polyrythmie, dissonance métrique | [[kt-polymetrie-polyrythmie]] | ppcm, 3:4, 5:4, 7:8, groupement / déplacement (Butler), cycles | [[../polymetrie]] | draft |
| 3 | Swing, microtiming, ghost notes, densité | [[kt-swing-microtiming]] | binaire / ternaire, pourcentages, vélocité, accents, conditions comme densité | [[../microtiming-retrigs]], [[../fill-conditions]] | draft |
| 4 | Backbeat, half-time, passerelles de tempo | [[kt-halftime-passerelles]] | 90 / 180, 140 / 186, 175 ; ouvrir un live à 190 vers DnB et dubstep | [[../slice-breaks]] | draft |

### Lot 2 — Socle harmonique et forme

| # | KT | Fichier | Apporte | Renvoie à | Statut |
|---|---|---|---|---|---|
| 5 | Tonalité du grave | [[kt-tonalite-du-grave]] | kick / rumble / basse accordés, Hz, kickbass, bandes | doctrine §11, [[../rumble-grave]], [[../kick-mental-vst]], [[../../../sounddesign/rumble]] | draft |
| 6 | Modes de la techno | [[kt-modes-techno]] | éolien, phrygien, dorien, phrygien dominant, mineur harmonique ; mode sur tonique fixe | [[../keyboard-gammes]] | draft |
| 7 | Tensions et lignes | [[kt-tensions-lignes]] | pentatonique, blue note, b2, triton, chromatisme, atonalité contrôlée | générateur acid 9.A | draft |
| 8 | Accords, voicings, rythme harmonique | [[kt-accords-voicings]] | min7 / min9 / sus / quintes nues, voicing ouvert, accords monophoniques, Camelot | doctrine §11 | draft |
| 9 | Phrasage et tension | [[kt-phrasage-tension]] | 4 / 8 / 16 / 32, build / breakdown / drop, soustraction, call and response, turnaround | doctrine §6, [[../mutes]], [[../patterns-chaines]] | draft |

### Lot 3 — Styles cœur du live

| # | KT | Fichier | Apporte | Renvoie à | Statut |
|---|---|---|---|---|---|
| 10 | Tribe / hardtek | `kt-style-tribe` | tribe kick et pitch envelope, toms en call and response, samples en points d'orgue, plateaux | [[../../../technique/patches/tribe]] | à rédiger |
| 11 | Acid core / mental | `kt-style-acidcore` | acid line 303 (accents, slides, octaves, 13 / 15 pas), phrygien, kickbass, narration au filtre | 9.A, [[../kick-mental-vst]] | à rédiger |
| 12 | Frenchcore / hardcore / bouncy | `kt-style-frenchcore` | offbeat bassline `.xxx`, galop, pitched kick, kick en trois couches, breaks 3/4 et 5/8 | | à rédiger |
| 13 | Hard techno et schranz | `kt-style-hard-techno` | double kick, pression, hats offbeat, ligne sur 3 mesures ; cadrer sur la rythmique | [[../rumble-grave]] | à rédiger |

### Lot 4 — Styles connexes

| # | KT | Fichier | Apporte | Renvoie à | Statut |
|---|---|---|---|---|---|
| 14 | Dub techno | `kt-style-dub-techno` | accords et voicings, delay 3/16, scoop, évolution lente | [[../send-fx-compresseur]] | à rédiger |
| 15 | Techno hypnotique / loop | `kt-style-hypnotique` | soustraction, cycles 3-5-7, microvariation, dubbing live | [[../mutes]] | à rédiger |
| 16 | Industrial / Birmingham / Detroit / broken | `kt-style-industrial-broken` | 3+3+4+3+3, tom interplay, clusters | [[../amp-overdrive-bitreduction]] | à rédiger |
| 17 | Electro / breakbeat | `kt-style-electro` | tresillo au kick, electro bounce, clave | [[../euclidien]] | à rédiger |
| 18 | Dubstep / DnB / jungle | `kt-style-dubstep-dnb` | halftime, 2-step, Amen, chopping, sub / mid split | [[../slice-breaks]], patches dnb / dubstep | à rédiger |
| 19 | Trance / psy | `kt-style-trance-psy` | rolling bass, gated arp, phrygien dominant, passerelle vers le mental | | à rédiger |

## Passe `rhythm_signature` — morceaux de référence par style

Commande : `python scripts/kt_signatures.py [style...]` (liste des morceaux
dans `STYLES` du script ; à enrichir à chaque grab). Lecture : patterns
repliés sur 16 pas par bande (sub 20-200 Hz, mid 200-2000 Hz, high > 2 kHz),
`X` ≥ 0,6, `x` ≥ 0,3 ; **la phase du premier temps n'est pas garantie**
(le repliage cale le maximum, pas le downbeat) ; `sync` = énergie hors temps ;
`swing` = part d'énergie sur le « a » (4e double croche) contre le « e »
(2e), 0,5 = équilibré, > 0,5 = anticipations avant le temps ; `pulse` =
régularité. Sortie du 2026-10-15 (relancée le 2026-10-15 avant le lot 1 :
patterns identiques, seuls quelques BPM diffèrent après réanalyse des
sidecars, dont deux lectures à la moitié du tempo, Liberté Naturel 184,6 →
90,7 et Maureen 215,3 → 108,2, commentées dans [[kt-halftime-passerelles]]) :

### tribe

| morceau | BPM | sub | mid | high | sync | swing | pulse |
|---|---|---|---|---|---|---|---|
| floxytek_-_micro_tribe | 161.5 | `X.x...x.x..x..xx` | `Xxx.X.X.xxx.x.X.` | `XX..XxX.XXx.XxX.` | 0.42 | 0.26 | 0.90 |
| floxytek_-_roots | 161.5 | `XXx.XXx.XXXxXXXx` | `xX...xxxxxxxxXx.` | `Xx..x...X..xXX.x` | 0.52 | 0.20 | 0.90 |
| kodaman_-_beton | 161.5 | `XxX.xXx.XXXxXXXX` | `Xx..Xx..XX.xXx.x` | `X.xxX.xxX.xXXxXX` | 0.37 | 0.43 | 0.95 |
| area_23_-_indian_tribe_acidcore | 161.5 | `X...X...X...X...` | `X.xXX.xXX..XX.xX` | `X.xX..xXx..xx.xx` | 0.44 | 0.88 | 0.92 |
| apre_-_contrast | 161.5 | `X.x.X.x.X...X.x.` | `XxXXX.xXXx.XXxXx` | `xxxXx..Xxx.Xx..x` | 0.52 | 0.72 | 0.91 |
| liberte_naturel_-_tracknard | 184.6 | `X...X...X...X...` | `X..Xx.XxX..xX..x` | `X..XxxXxX..XX.xx` | 0.35 | 0.78 | 0.94 |
| tekotak_-_lokapi | 172.3 | `X...X...X.x.X.x.` | `X..XX.xXX.xXX.Xx` | `xX.Xx..XxX.Xx.xX` | 0.44 | 0.70 | 0.91 |
| **moyenne (7)** | | `Xxx.X.x.Xx..Xxxx` | `Xxxxx.xxXx.xXxxx` | `Xx.Xx.xxXx.xX.xx` | | | |

### acidcore_mental

| morceau | BPM | sub | mid | high | sync | swing | pulse |
|---|---|---|---|---|---|---|---|
| six_ou_sept_-_acid_pirate | 143.6 | `X.x.X.x.X.X.X.X.` | `Xxx.XxxXX.XXx.Xx` | `Xxx.x..Xx.xX..xx` | 0.45 | 0.76 | 0.93 |
| nailik_hypnotik_-_le_renard_de_l_avarice | 161.5 | `X...X...X...X.x.` | `X..XX..xX.xxX.xx` | `...X...X...xx.xx` | 0.42 | 0.95 | 0.93 |
| diuko303_-_mirages | 161.5 | `XX.x.XxxxX...Xx.` | `XXxxXXxxXX..xXxx` | `.XXxXXXxXXX.Xxx.` | 0.63 | 0.27 | 0.91 |
| captain_303_-_human_madness | 161.5 | `X.x.X.x.X.x.X.X.` | `xx.X...Xx..xx.xx` | `xX.X.xxX.XxX.xxX` | 0.52 | 0.76 | 0.92 |
| luche_-_whispers | 152.0 | `X.XxX.XxX.XxX.XX` | `X.X.X.X.x.X.X.X.` | `XxXxX.XxX.XxXxXx` | 0.42 | 0.79 | 0.94 |
| spice_up_teksa_vorteks_-_soldiers | 152.0 | `xXxXxx...x.XxXX.` | `..xXxx.X.x.X.x.X` | `X.XXXX.X.X.XXx.X` | 0.75 | 0.62 | 0.92 |
| ktc_smk_-_cykada | 161.5 | `X...X...X...X...` | `X..XX..xX...X..x` | `Xx.X...Xx.xXX.xX` | 0.36 | 0.92 | 0.94 |
| berio_-_path | 161.5 | `X...X...X...X...` | `X.xXx.xXX..xX.xX` | `x.xX..xXxx.Xxx.X` | 0.42 | 0.86 | 0.92 |
| **moyenne (8)** | | `X.xxX.x.X.x.X.x.` | `X.xXx.xxX.xxX.xx` | `xxxXxxxXxxxXx.xX` | | | |

### tekno_rapide

| morceau | BPM | sub | mid | high | sync | swing | pulse |
|---|---|---|---|---|---|---|---|
| unkomun_-_akira | 152.0 | `X...X.xxX...X...` | `XxxXX.XXX.xXX.XX` | `xx.Xx.xxx.xXx.XX` | 0.50 | 0.79 | 0.92 |
| ciklo_-_vrech | 161.5 | `X...X...X...X...` | `XxxXx.xXXx.XXxxx` | `..xX..xX.x.Xx..x` | 0.50 | 0.69 | 0.91 |
| moldetek_-_cybertekno | 172.3 | `X.x.X.X.X.X.X.X.` | `Xx.XX..XX..XX.xX` | `.x.X...X...Xx.xX` | 0.54 | 0.79 | 0.91 |
| neurotribe_kokko_-_cyclic_spiral | 172.3 | `X.X.X.X.X.X.X.X.` | `xX.Xx.XXXxxxX.XX` | `xX.XxxxXxXxXX.xX` | 0.46 | 0.67 | 0.90 |
| a_laan_-_live_extract | 161.5 | `X...X...X..xx...` | `X...XxxxX.Xxx.xx` | `xx.xxx.Xx.XX..xX` | 0.47 | 0.80 | 0.91 |
| axolotl_-_remix_psylotribe | 184.6 | `X.x.X.x.X.X.X.X.` | `Xx.XXX.XX.xXx.xX` | `xx.xxX.Xx.xXxxxX` | 0.45 | 0.69 | 0.90 |
| **moyenne (6)** | | `X.x.X.x.X.x.X.x.` | `Xx.XXxxXX.xXX.xX` | `xx.Xxx.Xx.xXx.xX` | | | |

### hard_techno, hardcore, dnb, dubstep, techno lente

| style | morceau | BPM | sub | mid | high | sync | swing | pulse |
|---|---|---|---|---|---|---|---|---|
| hard techno | beauz_-_bel_mercy_hard_techno_remix | 161.5 | `.XxxxxxXxx..xXx.` | `x.Xx.xXX...xxXxx` | `.xX.XxXxx.X.xXX.` | 0.64 | 0.37 | 0.91 |
| hardcore | maureen_-_kompet_x_jiggle | 215.3 | `X..xX...X..xX...` | `X..xX..xX..xX..x` | `X..XX..xxXxxx..X` | 0.41 | 0.81 | 0.96 |
| dnb | dimension_-_uk | 172.3 | `.xX.....xxXx..xx` | `xXX..XXxxxXX.XXx` | `xx.x.XX..x.X.xXx` | 0.70 | 0.44 | 0.94 |
| dnb | document_one_-_1964 | 172.3 | `x.xXx..x...x..xX` | `XXXxxx..xXXxxxXX` | `XXx.....XXXXXXXX` | 0.66 | 0.58 | 0.95 |
| dnb | tim_reaper_-_scorched_earth_a2 | 161.5 | `XX...XXXxx...xxX` | `xX.xXXXxXX.Xx...` | `xX..XXXXxXxxx.xX` | 0.67 | 0.42 | 0.89 |
| dnb | noisia_-_the_hole_pt_1 | 165 | `X.X..xxX.xXxxxxx` | `X.x.xx...X.x.x..` | `X.xxxX...X....x.` | 0.59 | 0.34 | 0.94 |
| dnb | dizrupt_mkjay_-_room_service | 172.3 | `X......xx.X.x..x` | `X.xXX.X.XXXXx.xX` | `x.xxx.xxXx.X..x.` | 0.52 | 0.76 | 0.92 |
| dnb | **moyenne (5)** | | `Xxx..xxxx.x...xX` | `XxxxxxX.xXxX.xxx` | `XxxxxxxxxXxX.xXx` | | | |
| dubstep | 2hot2play_-_keep_the_balance | 152.0 | `XXx.xXx.XXx.XX..` | `Xx..xxXxXxx.XxXx` | `X..XX.xXX..XX..X` | 0.49 | 0.45 | 0.93 |
| dubstep | densha_crisis_-_monster | 152.0 | `xxx..X.xXxXx..xx` | `.x.xxX.X.XxX.x.x` | `.xxxXXXXxXxx.x.x` | 0.75 | 0.47 | 0.92 |
| dubstep | excision_downlink_-_resistance | 152.0 | `x...X...x...x...` | `X..Xx...X..Xxx..` | `X.xXx..xX..Xxx.x` | 0.39 | 0.73 | 0.96 |
| dubstep | utk_-_kaiono | 152.0 | `X...X...X...X...` | `X.xXX.XxX..xX.Xx` | `x..X..xXx.xXx.xx` | 0.44 | 0.86 | 0.94 |
| dubstep | **moyenne (4)** | | `X...Xx..Xxx.X...` | `Xx.xxxxxXxxxXxxx` | `x..XxxxXx..Xx..x` | | | |
| techno lente | polar_inertia_-_hell_frozen_over | 129.2 | `.xXXXX.xxXx.xxxx` | `.xXXXXXXxXx.xXXx` | `XXX.xXXx.xX.x...` | 0.81 | 0.50 | 0.94 |
| techno lente | kangding_ray_-_amber_decay | 123.0 | `XXXXxXXXxxXX.xXX` | `xXx..xx..xx.xXxx` | `.XxXx.Xx..x.x..x` | 0.74 | 0.48 | 0.94 |

### Lecture rapide (à confirmer à l'oreille)

- **Tribe, acid core, tekno** : sub en four-on-floor net (`X...X...`), ou
  `X.x.X.x.` quand la basse en contretemps de croche passe sous 200 Hz ;
  mid et high chargés sur les pas 4, 8, 12, 16 (le « a » avant le temps) :
  le `swing` de 0,7 à 0,95 dit que **l'ornement tribe anticipe le temps**
  plutôt qu'il ne shuffle. Argument pour KT3 et KT10.
- **DnB** : sub cassé, syncope 0,6-0,7, high quasi continu : la grille
  16 pas « voit » le break (KT4, KT18).
- **Dubstep à 140-152** : sub rare (`X...............` chez Excision) ou
  four-on-floor quand le morceau est en fait un tekno (UTK) : le tag genre
  de la library est bruité, trier à l'oreille avant KT18.
- **Techno lente (Polar Inertia, Kangding Ray)** : sub dense et syncope
  0,8 : le repliage par maximum n'a pas trouvé de downbeat franc ; ces
  signatures ne servent pas de référence (KT14, KT15).
- **Manques dans la library** : un seul hard techno, un seul hardcore (et
  pas de frenchcore), pas de dub techno, hypnotique, industrial, electro,
  trance / psy. **À grabber avant KT12-KT17 et KT19** (2 ou 3 morceaux
  chacun via `scripts/grab.py`), puis ajouter leurs slugs à `STYLES`.

## Passe harmonique — gamme et accords par style

Commande : `python scripts/kt_signatures.py --harmony` (mêmes morceaux que
ci-dessus). Lecture : gamme détectée par `analyzer.harmony` sur le sidecar
(score, « incertain » = marge inférieure à 0,05 entre les deux premières
candidates ; la pentatonique majeure détectée est souvent la relative de la
mineure) et accords distincts de la section principale (`5` = quinte nue,
`sus2`, `dim`, `N` ignoré). Sortie du 2026-10-15, consommée par KT5-KT8 :
sur 32 morceaux analysés, 17 incertains, 25 pentatoniques ou blues, 27 avec
des accords `5` ou `sus2` dans la section principale.

### tribe

| morceau | gamme détectée | score | accords (section principale) |
|---|---|---|---|
| floxytek_-_micro_tribe | F phrygien | 0.61 | Fsus2 Csus4 Fsus2 F5 Fsus2 F Fsus2 F5 |
| floxytek_-_roots | C blues | 0.77 (incertain) | Bdim Fsus4 F |
| kodaman_-_beton | D pentatonique mineure | 0.81 | D5 |
| area_23_-_indian_tribe_acidcore | C majeur (ionien) | 0.60 (incertain) | C5 A#sus2 Adim Gdim Fm C5 F5 C5 |
| apre_-_contrast | F pentatonique mineure | 0.63 (incertain) | D#sus2 |
| liberte_naturel_-_tracknard | E pentatonique majeure | 0.59 (incertain) | F5 |
| tekotak_-_lokapi | A# pentatonique majeure | 0.55 (incertain) | Bdim Bsus2 Esus2 Bsus2 B5 |

### acidcore_mental

| morceau | gamme détectée | score | accords (section principale) |
|---|---|---|---|
| six_ou_sept_-_acid_pirate_vendetta_acidc | B blues | 0.86 | E5 F5 |
| nailik_hypnotik_-_nailik_le_renard_de_la | A# pentatonique mineure | 0.63 (incertain) | A5 |
| diuko303_-_diuko_mirages | sans analyse |  | — |
| captain_303_-_acidcore_captain_303_human | C pentatonique mineure | 0.55 (incertain) | B5 |
| luche_-_whispers_farfa_d_digital_ep_10 | G# mineur harmonique | 0.60 | G#sus2 G#5 G#sus2 G#5 |
| spice_up_teksa_vorteks_-_soldiers | E pentatonique majeure | 0.87 | E Bsus4 E5 |
| ktc_smk_-_ktc_cykada_free_download | C# blues | 0.58 (incertain) | G5 G Cm G5 |
| berio_-_path | G pentatonique majeure | 0.58 (incertain) | C#5 F#sus2 C#5 G#sus2 C#5 F#sus2 C#5 G#5 |

### tekno_rapide

| morceau | gamme détectée | score | accords (section principale) |
|---|---|---|---|
| unkomun_-_akira | D# pentatonique majeure | 0.63 (incertain) | — |
| ciklo_-_vrech | G# pentatonique mineure | 0.64 (incertain) | — |
| moldetek_-_cybertekno_forthcoming_on_cc_ | G# pentatonique mineure | 0.92 (incertain) | D#dim C#m D#dim E |
| neurotribe_kokko_-_neurotribe_vs_kokko_c | F# pentatonique mineure | 0.63 (incertain) | Esus2 F5 Esus2 F5 Esus2 F5 Esus2 F5 |
| a_laan_-_live_extract_big_brother_is_rav | G# pentatonique mineure | 0.63 (incertain) | Gsus2 F#sus2 |
| axolotl_-_remix_psylotribe_lemon_preview | sans analyse |  | — |

### hard_techno

| morceau | gamme détectée | score | accords (section principale) |
|---|---|---|---|
| beauz_-_bel_mercy_beauz_hard_techno_remi | B blues | 0.82 | E5 E E5 G#dim E Fdim E G#dim |

### hardcore

| morceau | gamme détectée | score | accords (section principale) |
|---|---|---|---|
| maureen_-_kompet_x_jiggle | D blues | 0.79 | C#5 C#sus2 C#5 C#sus2 C#5 Csus2 D5 C#5 |

### dnb

| morceau | gamme détectée | score | accords (section principale) |
|---|---|---|---|
| dimension_-_uk | C# lydien | 1.11 | F#5 Fsus2 Bsus4 C#dim Csus4 Bsus4 Csus4 A#sus2 |
| document_one_-_1964 | D# pentatonique mineure | 0.84 | D#5 D#m D#5 D#m D#5 D#m D#5 D#m |
| tim_reaper_-_scorched_earth_a2 | D blues | 0.71 (incertain) | G Gsus2 G A#m G#dim G A#m G |
| noisia_-_the_hole_pt_1 | E pentatonique mineure | 0.96 | E E5 E Esus2 E Em Esus2 E |
| dizrupt_mkjay_-_room_service | C# pentatonique majeure | 0.56 | F#5 C#sus2 F#5 C#sus2 F#5 C#sus2 F#5 C#sus2 |

### dubstep

| morceau | gamme détectée | score | accords (section principale) |
|---|---|---|---|
| 2hot2play_-_keep_the_balance | F blues | 0.73 | Fm |
| densha_crisis_-_monster | F mineur mélodique | 0.74 | E Am G#sus2 A#5 Gm Dsus4 Bdim |
| excision_downlink_-_resistance | F pentatonique mineure | 0.56 (incertain) | D#dim F#sus2 Fsus2 F#sus2 Gdim Am C#sus2 E5 |
| utk_-_kaiono | E pentatonique majeure | 0.58 (incertain) | C#m Esus2 C#m A5 |

### techno_lente_dub

| morceau | gamme détectée | score | accords (section principale) |
|---|---|---|---|
| polar_inertia_-_hell_frozen_over | E mineur harmonique | 0.64 | D#sus2 Esus4 D#sus2 Em D#sus2 Em D#sus2 |
| kangding_ray_-_kangding_ray_amber_decay | E mineur (éolien) | 0.93 | D#5 E5 |

## Avancement

| Lot | Contenu | Statut |
|---|---|---|
| 1 | KT1-KT4 socle rythmique | fait le 2026-10-15 (draft, exercices à jouer) |
| 2 | KT5-KT9 socle harmonique et forme | fait le 2026-10-15 (draft, exercices à jouer) |
| 3 | KT10-KT13 styles cœur | à venir (grabs frenchcore et hard techno avant KT12-KT13) |
| 4 | KT14-KT19 styles connexes | à venir (grabs avant) |
