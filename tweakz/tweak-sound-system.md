# Ma version du Tweak Sound System

> Système son **versatile et re-voiceable**, à colonne vertébrale dub mais ouvert à toutes les musiques électroniques (techno, jungle, DnB, house…). Format **light** : 20 à 50 personnes, usage **fixe + mobile**. Construction **hybride** (bas DIY + tops du commerce), montée **par étapes**, priorité **qualité**.

---

## 1. Concepts généraux

Ce qui définit ce système, ce n'est pas le dub : c'est le **TWEAK** — la capacité à **re-modeler le son en direct selon le style joué**. Tout découle de ça.

1. **Le front-end est le cœur du projet.** Un préampli + EQ multibande (+ DSP) permet de re-voicer le système morceau par morceau. C'est lui qu'on soigne en priorité, pas les boîtes.
2. **Multi-voies = moteur de la versatilité.** Chaque bande de fréquences est sur **son propre canal d'ampli + DSP**. On peut donc rééquilibrer le grave, le punch et l'aigu **indépendamment** selon le genre. C'est ça qui rend le système "tweakable" (et pas seulement le dub qui aime ça).
3. **Voicing neutre et étendu, jamais "dub-typé".** On évite les boîtes colorantes (scoop pur) : il faut un grave qui descend **bas et propre** (techno/DnB) et un haut **clair et cristallin** (l'esthétique "scène anglaise" de Tweak). Le préampli pousse ensuite le son où on veut.
4. **3 voies, chacune spécialiste.** Sub (terrien) / Kick (le claque dans le sternum) / Top (médium + aigu). Philosophie de Victor (Tweak) : une membrane qui fait une seule bande la fait bien.
5. **Mono d'abord, tops stéréo plus tard.** Le bas reste mono (inutile en stéréo). Les tops pourront passer en stéréo pour l'imaging électronique. → prévoir les canaux DSP/ampli dès le départ.
6. **Marge + limiteurs.** La techno est soutenue (énergie continue), le dub est transitoire : il faut de la réserve et des limiteurs bien réglés pour tenir les deux **sans casse**.

### Découpe en fréquences (cible)

| Voie | Bande | Pente | Rôle |
|------|-------|-------|------|
| **Sub** | ~32–100 Hz | LR24 | grave ventral, descend bas et propre |
| **Kick** | ~100–350 Hz | LR24 | le punch / claque dans la poitrine |
| **Top** | ~350 Hz – 18 kHz | LR24 (+ xover interne 12"/moteur ~1,6 kHz) | médium clair + aigu cristallin |

---

## 2. La chaîne complète (signal)

```
Source (platines / CDJ / table DJ)
        │
        ▼
[Préampli + EQ multibande + effets]   ← LE TWEAK (re-voicing live + siren/echo)
        │  (full-range)
        ▼
[DSP]   ← crossover 3 voies + limiteurs + presets par style (protection & gestion système)
        │ ┌──────────┬──────────┐
        ▼ ▼          ▼          ▼
   [Ampli 4 canaux]
     │        │           │            │
     ▼        ▼           ▼            ▼
   SUB 18"  KICK 15"   TOP (L)     TOP (R, plus tard)
```

**Topologie recommandée (crossover numérique) :** le préampli fait la **couleur + les effets** (full-range), le **DSP fait le crossover + les limiteurs**. Avantage : presets rappelables par genre, limitation précise, câblage simple.

**Variante puriste (à la Tweak, crossover analogique) :** un préampli **4 voies** fait le crossover analogique + EQ + effets → puis un processeur **par voie** limite/corrige. Plus authentique et tactile, mais plus complexe (et le préampli est 4 voies, on en utilise 3).

---

## 3. Les éléments un par un

### 3.1 Sub (grave) — DIY

- **Rôle :** 32–100 Hz. Doit descendre **bas et propre** pour la techno/DnB, pas juste "punchy dub".
- **Plan recommandé :** **Cubo 18** (freespeakerplans) — ~62×62×65 cm, 1×18", ~40 Hz, compact et transportable (idéal fixe+mobile). Plan gratuit.
  - *Alternative plus grave/plus neutre :* reflex 18"/21" accordé ~32–35 Hz, ou bandpass horn. Plus encombrant.
- **HP (qualité) :** B&C 18SW115 · 18 Sound 18LW1400 · FaitalPro 18XL1800 (~280–350 €).
  - *Budget :* Beyma SM118 (~180 €).
- **Puissance ampli :** ~1000–1500 W.
- **Réglage :** LPF ~100 Hz LR24 + limiteur.
- **Évolution :** un 2e sub (le Cubo s'empile) pour le headroom.

### 3.2 Kick (le claque) — DIY

- **Rôle :** 100–350 Hz, chargé en **pavillon court** (charge avant + chambre close arrière) → c'est le chargement pavillon qui donne le transitoire sec, le "claque".
- **Plans :**
  - **Cubo Kick** (freespeakerplans) — cohérent avec le Cubo 18, compact, simple. ✅ le plus logique pour rester portable.
  - **Sound Agency** (soundagency.fr) : **SAKB115-LCB** (kick 15" clos) ou **SACH115-FV** (kick compound 15"). Voir aussi leur "Projet Mini Sound System DUB".
  - **Horn Plans** : **MKB-230** (kick bin Marc.O).
- **HP (mid-bass, PAS un HP de sub) :**
  - 15" (claque + corps) : B&C 15PS76 / 15NW76 · 18 Sound 15ND930 · FaitalPro 15PR400 (~150–300 €).
  - 12" (plus snappy/léger, ultra-mobile) : B&C 12NDL76 · 18 Sound 12ND830 · FaitalPro 12PR320.
- **Puissance ampli :** ~500–1000 W.
- **Réglage :** BPF 100–350 Hz LR24 + limiteur. **EQ par style** : on baisse ce canal en techno, on le pousse en dub/jungle. *C'est l'incarnation du tweak.*

### 3.3 Top (médium + aigu) — commerce (ou DIY)

- **Rôle :** 350 Hz – 18 kHz. **Le juge de paix** du rendu "clair/cristallin", tous styles confondus → on investit ici.
- **Option commerce (hybride) :** top **2 voies 12" + moteur 1,4"** passif, sur le même ampli/DSP. Occasion pro : RCF, FBT, EV, Yamaha (~150–400 €/pièce).
- **Option point-source (imaging électronique) :** top **coaxial** (B&C 12CXN/15CX, ou top coaxial du commerce) — meilleure cohérence stéréo pour techno/house/DnB.
- **Option DIY :** 12" (B&C 12NDL76 / 18 Sound 12ND930) + moteur 1,4" (B&C DE500 / BMS 4552) + pavillon ; ou s'inspirer du **MT-130** (Horn Plans) en plus compact.
- **Puissance ampli :** ~300–500 W.
- **Réglage :** HPF ~350 Hz ; xover interne 12"/moteur ~1,6 kHz (passif) ou actif si canaux DSP dispo.
- **Évolution :** 2e top → couverture + passage **stéréo**.

### 3.4 Préampli — LE moteur du TWEAK

Fonctions : entrées (phono/ligne) + **EQ multibande** (le re-voicing live) + crossover actif + intégration **siren/echo**.

- **Le construire (open-source) :** **"4-way preamp"** sur OSHWLab (GuerillaTech) — préampli reggae 4 voies analogique, étage **phono RIAA**, **EQ 10 bandes**, **siren + echo** intégrés. Hardware libre → fabricable.
  - ⚠️ Vrai sous-projet d'électronique (PCB, op-amps, alim, beaucoup de potards/jacks). Faisable si l'électro t'attire.
  - Ressources : threads "Building a Pre Amp" (Speakerplans), blog Dave Cropley "DIY dub reggae sound system".
- **L'acheter d'occasion :** **JB Audio Units** (le vrai fabricant dub, `jbaudiounits.com`) — préampli 5 voies, apparaît en occasion (Audiofanzine, petites annonces dubsounds). ⚠️ **≠ "JB Systems"** (marque sono/lumière bas de gamme, rien à voir).
- **Alternative moderne :** un **DSP avec presets** par style = tweak "à rappel" (précis, moins cher, moins tactile).
- **Recommandation :** vu que c'est le cœur de ton envie → **préampli analogique** (build OSHWLab ou JB d'occas) pour le geste live + effets, **+ DSP** pour le crossover/limiteurs.

### 3.5 DSP (gestion système)

- **Rôle :** crossover 3 voies + **limiteurs par voie** (le "plus de casse" de Tweak) + **presets par genre**.
- **Modèles :** miniDSP 2x4 HD (~220 €) · t.racks DSP 408 (~250 €) · Xilica (~500 €).
- Doit avoir **assez de sorties** (≥ 4) pour viser le stéréo tops plus tard.

### 3.6 Amplification

- **Type :** ampli **4 canaux** class-D (sub / kick / top L / top R).
- **Modèles :** the t.amp Quadro · RAM Audio (4 ch) · **Crown DCi 4×** (DSP intégré → peut remplacer le DSP séparé, ce que visait Tweak) · Powersoft d'occasion.
- **Affectation :** Sub (le plus de watts, éventuellement bridgé) · Kick · Top(s).

### 3.7 Effets dub (l'âme, plus tard)

- **Siren + écho :** JB Audio Units (Double Dub Siren **DDS-1**, **Echo Unit**) ; ou DIY / pédales.
- **Anti-clipping (option) :** RC Audio **Red Alert** — superflu à domicile (les limiteurs DSP font le job), mais le principe "ne pas jouer dans le rouge" reste valable.

### 3.8 Source

- Table de mix DJ (une **rotary** colle bien à l'esprit dub) / platines vinyle / CDJ.

### 3.9 Câblage + code couleur

- Connecteurs **Speakon** partout.
- Reprendre le **code couleur mnémotechnique de Tweak** (utile en setup à plusieurs / mobile) :
  - blanc = ciel · jaune = soleil · bleu = air · marron = terre · rouge = cœur de la terre.
  - On retrouve les couleurs des étages (vertical) jusque derrière les caisses et sur les amplis.

---

## 4. Matériel existant à recycler

- **Prodipe Pro 5 V3** (×2, une HS) + **Pro 10S V3** = **monitoring de studio**, pas un PA de soirée.
  - Garder pour : **booth/monitoring**, écoute de référence, ou très petit comité.
  - La Pro 5 valide peut servir de **top provisoire** au Stage 1.
  - Ne réparer la Pro 5 HS que si c'est peu cher.

---

## 5. Feuille de route (par étapes) + budget indicatif

> Budgets approximatifs (EUR), hors source/table. À étaler.

### Stage 1 — La section rythmique (le cœur dub) · ~1000–1500 €
- Sub 18" DIY (Cubo 18) + HP 18"
- Kick 15" DIY (Cubo Kick / SAKB115) + HP 15"
- DSP (crossover + limiteurs)
- Ampli 4 canaux
- *Top provisoire : Pro 5 active via une sortie DSP.*
- → Tu as déjà le **grave + le claque** = ~90 % du feeling.

### Stage 2 — Le TWEAK + les vrais tops · ~700–1500 €
- **Préampli** (build OSHWLab **ou** JB Audio Units d'occasion) — la pièce qui te tient à cœur, à monter tôt.
- 1 top 2 voies 12"+moteur (commerce/occasion), puis un 2e.

### Stage 3 — L'âme dub + montée en puissance · ~300–800 €
- Siren + écho (JB Audio Units ou DIY).
- 2e sub / 2e kick si besoin de niveau.

### Stage 4 — Versatilité poussée · variable
- **Tops en stéréo** (DSP/ampli déjà prévus pour).
- Red Alert (si jeux DJ exigeants).

**Total light "qualité" :** ~**1500–3500 €** étalé, évolutif, sans gros achat unique.

---

## 6. Aide-mémoire : re-voicing par style (le TWEAK en pratique)

Exemples de gestes EQ/balance par canal (à affiner à l'oreille dans ton lieu) :

| Style | Sub | Kick (100–350) | Top | Effets |
|-------|-----|----------------|-----|--------|
| **Dub / reggae** | gras, présent | **poussé** (le claque) | médium chaud, aigu maîtrisé | **siren + écho** ++ |
| **Techno** | serré, descend bas | **réduit** (moins de médium-grave) | aigu net, transitoires | sobres |
| **Jungle / DnB** | très bas + rapide | rapide, présent | brillant | écho ponctuel |
| **House** | rond, contrôlé | médium chaleureux | doux et clair | légers |

---

## 7. Liens & références

**Plans de boîtes**
- Horn Plans (Marc.O) — `http://hornplans.free.fr` (HTTP seul) · MT-130 `/mt130.html` · MKB-230 `/mkb230.html`
- freespeakerplans.com — Cubo 18, Cubo Sub, Cubo Kick
- Sound Agency — `soundagency.fr` (SAKB115-LCB, SACH115-FV, Projet Mini Sound System DUB)
- Forum Dubsounds (Red Lion) — `forum.dubsounds.fr`

**Préampli**
- OSHWLab "4-way preamp" (GuerillaTech) — `oshwlab.com/GuerillaTech/4-way-preamp`
- JB Audio Units — `jbaudiounits.com` (préampli 5 voies, Echo Unit, DDS-1) — ⚠️ ≠ JB Systems
- Blog Dave Cropley — "How to build a DIY dub reggae inspired sound system"

**Le système d'origine (inspiration, refs vérifiées)**
- Tweak Sound System (collectif parisien). Stack 5 voies, full mono, plans Horn Plans (MT-130), préampli/echo/siren JB Audio Units, ampli subs **Powersoft K20**, ampli kicks **Hexagone HA2x2600D**, **RC Audio Red Alert**, HP B&C / membranes RCF, code couleur câbles.

---

*Document de travail — à affiner étape par étape. Prochaine étape au choix : comparatif préampli (build OSHWLab vs JB d'occasion) ou liste d'achat chiffrée de la section rythmique.*
