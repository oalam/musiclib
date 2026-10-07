# Stage 2 — Le préampli (le TWEAK) : build vs achat + construction DIY

> Le préampli est **le cœur du projet** (le re-voicing live + les effets). Ce doc compare **le construire** (projet open-source GuerillaTech) vs **l'acheter d'occasion** (JB Audio Units), puis détaille la **construction DIY** : workflow, architecture, liste de composants.

---

## 1. D'abord : où vit le crossover ? (décision de topologie)

C'est la décision qui conditionne tout le reste.

**Option recommandée — crossover dans le DSP, préampli "full-range" :**
```
Source → Préampli (phono/line/aux + EQ 10 bandes + siren + echo) → DSP (crossover 3 voies + limiteurs) → ampli → boxes
```
- Le préampli ne sert qu'à la **couleur + les effets** (le TWEAK). On en sort un signal **full-range** (avant/à la place de l'étage crossover).
- ✅ Tu **gardes le DSP 206** du Stage 1, tu peux **ne pas construire l'étage crossover** du préampli → BOM plus simple, moins cher, moins de risque.
- ✅ Limiteurs numériques précis = protection HP.

**Option puriste — crossover analogique dans le préampli (comme Tweak) :**
```
Source → Préampli 4 voies (… + crossover analogique) → DSP 4 entrées (limiteurs par voie) → ampli → boxes
```
- Signal 100 % analogique jusqu'aux limiteurs. Plus "âme", plus tactile.
- ⚠️ Impose un **DSP à 4 entrées** (ex. **t.racks DSP 408**, 4 in / 8 out, ~250 €) au lieu du DSP 206 → à anticiper dès le Stage 1 si tu choisis cette voie.

👉 **Reco :** commence par l'**option recommandée** (préampli full-range + DSP crossover). Tu construis l'essentiel du TWEAK sans la complexité du crossover analogique, et tu peux ajouter l'étage crossover plus tard si l'envie du "tout analogique" te prend.

---

## 2. Comparatif build vs achat

| Critère | **DIY GuerillaTech** (build) | **JB Audio Units 5 voies** (occasion) | Mostec / Dub-Siren RAS (UK) |
|---|---|---|---|
| Prix | **~300–450 €** (pièces) | ~1800 € occas (1896 € neuf) | sur devis (UK, ~£600–1000+) |
| Effort | élevé (électronique + boîtier) | nul (plug & play) | nul |
| Délai | quelques semaines | immédiat | fabrication (semaines) |
| Personnalisation | **totale** (fréquences, effets, façade) | limitée (modifs possibles chez JB) | sur mesure |
| Effets inclus | **siren + echo intégrés** | selon config (souvent modules séparés) | selon modèle |
| Risque | erreurs / débogage | aucun | aucun |
| Revente | faible | **excellente** (garde sa valeur) | bonne |
| Esprit / fierté | **maximale** | — | — |

**Verdict :**
- Tu aimes l'électronique et veux l'identité TWEAK + économiser → **build** (et le JB se revend ~prix neuf, donc le DIY est *largement* plus rentable).
- Tu veux que ça marche tout de suite, zéro fer à souder → **JB d'occasion** (mais ~1800 €).
- Pour ton profil (curieux, budget par étapes, déjà partant pour DIY) → **build le front-end**, DSP pour le crossover/limiteurs.

---

## 3. Version DIY — détail de construction

### 3.1 Projet source
- **OSHWLab / EasyEDA** : `oshwlab.com/GuerillaTech/4-way-preamp`
- Miroir **CircuitMaker** (Altium 365) : `circuitmaker.com/Projects/Details/Guerillatech/4-way-Reggae-Preamp`
- Préampli reggae **4 voies analogique** : phono RIAA, EQ 10 bandes, siren + echo.

### 3.2 Workflow de fabrication (étapes macro)
1. **Ouvrir le projet** dans EasyEDA (gratuit, compte web) — ou CircuitMaker.
2. **Exporter la BOM** (liste exacte des composants + valeurs + quantités) et les **Gerbers** (fichiers de fabrication PCB).
3. **Commander les PCB** chez **JLCPCB** (ou PCBWay) à partir des Gerbers (~5 cartes, ~20–40 €).
4. **Commander les composants** chez **Mouser / TME / Digikey** (qualité) ou **LCSC** (économique) à partir de la BOM exportée.
5. **Souder** (composants traversants en majorité → accessible).
6. **Boîtier** : perçage façade (jacks, potards, switches, LEDs), montage rack 19".
7. **Câblage interne**, mise sous tension prudente, **calibration/réglages**.

> ⚠️ Les **valeurs et quantités exactes** viennent de la **BOM du projet** (export EasyEDA). La liste ci-dessous est **représentative par bloc** pour estimer le coût et l'effort, pas le BOM officiel.

### 3.3 Architecture (blocs fonctionnels)
1. **Alimentation** bipolaire régulée ±15 V
2. **Étage phono RIAA** (entrée platine)
3. **Entrées line / aux / micro** (sampler, siren externe, micro selecta)
4. **Mixage / master** (sommateur + volume master)
5. **EQ graphique 10 bandes** (le re-voicing live = le TWEAK)
6. **Siren** (oscillateur réglable)
7. **Echo** (delay numérique type PT2399)
8. **Buffers de sortie** (full-range, ou 4 voies si crossover)
9. *(Optionnel)* **Crossover actif 4 voies** Linkwitz-Riley — *à ne PAS construire si le DSP fait le crossover*

### 3.4 Liste de composants représentative (par bloc)

| Bloc | Composants typiques | Réf. exemple | Qté | ~Coût |
|------|--------------------|--------------|-----|-------|
| **Alim ±15 V** | transfo torique 2×15 V 30 VA · pont redresseur · condos 4700 µF/35 V · régulateurs · découplage · dissipateurs · embase IEC + fusible + inter | 7815/7915 (ou LM317/337) | 1 set | ~50 € |
| **Phono RIAA** | op-amp faible bruit + réseau RIAA (R précision + C film) | NE5532 / OPA2134 | 1–2 | ~10 € |
| **Entrées line/aux/mic** | jacks RCA (paires) + jacks 6,35/XLR micro · op-amps buffer · potards niveau (10k log) | NE5532 / TL072 | 4–6 | ~40 € |
| **Mixage / master** | op-amp sommateur · potard master | NE5532 | 1 | ~6 € |
| **EQ 10 bandes** | **potards à glissière 10k lin ×10** · op-amps duals ×~5 (gyrateurs) · R+C film des 10 fréquences · capuchons sliders | NE5532 | 1 set | ~55 € |
| **Siren** | IC générateur de fonction · potards rate/pitch · switch | XR2206 (ou 555/op-amp) | 1 | ~18 € |
| **Echo** | IC delay numérique (×2 pour ping-pong) · op-amps support · potards time/feedback/level | PT2399 | 1–2 | ~16 € |
| **Sorties** | buffers op-amps · connecteurs sortie XLR/jack | NE5532 | 3–4 | ~25 € |
| *(Crossover 4 voies — optionnel)* | op-amps duals ×6–8 · C film appariés + R précision · trimmers niveau ×4 | filtres Sallen-Key LR24 | 1 set | ~30 € |
| **PCB** | fabrication (Gerbers → JLCPCB) | — | ~5 | ~30 € |
| **Boîtier + UI** | rack 19" 2U/3U · knobs ×15–20 · entretoises, fil, passe-fils, visserie | — | 1 | ~120 € |

### 3.5 Coût estimé DIY
| Variante | Total pièces |
|----------|--------------|
| **Front-end seul** (sans crossover analogique, DSP fait le xover) — *recommandé* | **~340 €** |
| Avec étage crossover 4 voies (puriste) | ~370 € |
| Version "soignée" (connecteurs Neutrik, boîtier qualité, knobs alu) | ~450–500 € |

→ **3 à 5× moins cher** qu'un JB d'occasion, pour le même rôle de TWEAK.

### 3.6 Outillage & compétences
- **Outillage :** fer à souder à température réglable, pompe/tresse à dessouder, multimètre, pince coupante, perceuse + forets étagés (perçage façade), éventuellement scie cloche pour XLR.
- **Compétences :** lecture de schéma, soudure traversante (accessible débutant motivé), méthode pour le débogage. Le **plus laborieux = la façade** (perçage + câblage des dizaines de potards/jacks).
- **Temps réaliste :** 20–40 h réparties (PCB + soudure + boîtier + réglages).

### 3.7 Étapes de montage (détaillé)
1. **Souder par bloc** dans l'ordre : alim → tester ±15 V à vide (avant de brancher les op-amps).
2. Insérer les op-amps **sur supports** (DIP) → facilite le débogage.
3. Monter **phono → entrées → master** → tester le passage du signal au casque/ampli.
4. Monter l'**EQ** → vérifier l'action des 10 bandes.
5. Monter **siren** puis **echo** → tester les effets.
6. *(option)* Monter le **crossover** → régler les fréquences/niveaux.
7. **Perçage façade** (gabarit imprimé), montage des potards/jacks/switches/LEDs.
8. **Câblage interne** (masses en étoile, blindage des entrées phono).
9. **Mise sous tension via lampe série / progressive**, contrôle des tensions, écoute.
10. **Réglages/calibration** (niveaux d'entrée, gain master, trims de sortie).

### 3.8 Pièges à éviter
- **Masses / ronflette :** masse en étoile, séparer alim et audio, blinder l'entrée phono.
- **Op-amps sur supports** (jamais soudés direct au début).
- **Condos audio en film** dans le chemin du signal (pas céramique).
- **Vérifier l'orientation** des électrolytiques et régulateurs avant power-on.
- Tester **alim seule d'abord**, puis bloc par bloc.

---

## 4. Reco finale

1. **Build le front-end GuerillaTech** (phono + EQ 10 bandes + siren + echo + master full-range) → ~340 €.
2. Le **DSP** (DSP 206 du Stage 1) fait le **crossover + limiteurs**.
3. Garde l'option d'ajouter l'**étage crossover analogique** plus tard si tu veux le chemin tout-analogique (→ alors prévoir un DSP 4 entrées type DSP 408).

> Si zéro envie d'électronique : **JB Audio Units 5 voies d'occasion** (~1800 €, se joue très bien en 3 voies) — mais c'est ~5× le prix du DIY.

---

## 5. Liens

- Projet : `oshwlab.com/GuerillaTech/4-way-preamp` · `circuitmaker.com/Projects/Details/Guerillatech/4-way-Reggae-Preamp`
- PCB : JLCPCB / PCBWay · Composants : Mouser / TME / Digikey / LCSC
- Achat : JB Audio Units `jbaudiounits.com` · Mostec `mostec.co.uk` · Dub-Siren `dub-siren.com` (RAS-5000)
- Ressources build : threads "Building a Pre Amp" (Speakerplans), blog Dave Cropley "DIY dub reggae sound system"

---

*Note : la BOM ci-dessus est représentative. La liste exacte (valeurs, quantités, références) s'exporte depuis le projet dans EasyEDA avant commande.*
