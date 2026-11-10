# mk-brain

Maschine MK2 en HID brut devant la Digitakt II. La spec fait foi :
[SPEC.md](SPEC.md). Avancement : [CHANGELOG.md](CHANGELOG.md).

## Installation (Mac, prototype)

```bash
cd mk-brain
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

## Configuration

`config/default.yaml` : canal, courbe de vélocité, quantize, longueur de phrase,
couleurs, dispositions du clavier (B-H), table `mpc` des 16 pads (track, tranche,
label, couleur).

Guide utilisateur : [docs/GUIDE.md](docs/GUIDE.md) ; captures régénérées par
`.venv/bin/python docs/screens.py` (écrans et LED rendus par le vrai code).

`projects/<set>.yaml` : fiche de chaque banque (titre, tempo, tonique, mode,
phrase), **généré** par `mk-brain convert` depuis le front matter `mkbrain:` de
la doctrine du set (`digitakt/doctrine-dt2-<set>.md`), recoupé avec le
`library/lives/<set>.json` qu'il référence (banques, tonalités, tempos : une
divergence est une erreur qui donne la ligne fautive). Ne pas l'éditer à la
main : modifier la doctrine, reconvertir, commiter les deux.
En live, la banque du dernier Program Change reçu de la DT2 donne la phrase,
la tonique et le mode affichés ; en design, celle choisie par GROUP.
`tests/test_convert.py` échoue si le projet commité est périmé.

## Commandes

```bash
.venv/bin/mk-brain list               # interfaces HID de la MK2
.venv/bin/mk-brain spike              # mire, balayage LED, écho des contrôles, bilan à Ctrl-C
.venv/bin/mk-brain spike --raw --no-chase   # + rapports bruts en hexa
.venv/bin/mk-brain play               # sélection de projet (maître : choisir, appui : charger ;
                                      # dernier joué présélectionné, SHIFT + BROWSE = y revenir),
                                      # pads en MPC (table mpc), PAD MODE = MPC / clavier,
                                      # GROUP A-H = banque, boutons d'écran 1-4 = menu
                                      # (maître : régler l'entrée au focus,
                                      # appui : focus suivant),
                                      # flèches BROWSE = page d'encodeurs ◀ ▶ en boucle,
                                      # flèches de transport = octave du clavier (±4),
                                      # compteur de phrases (SHIFT + PLAY / GROUP n = recalage)
.venv/bin/mk-brain play --dry-run     # sans DT2, notes affichées
.venv/bin/mk-brain play --project projects/solaris.yaml   # projet chargé sans sélection
                                      # derniers réglages repris de state/session-<projet>.json
.venv/bin/mk-brain convert ../digitakt/doctrine-dt2-solaris.md   # → projects/solaris.yaml
.venv/bin/mk-brain clock              # BPM, transport, gigue d'arrivée des ticks
.venv/bin/mk-brain clock --bench-note 3   # + note 3 (track 4) envoyée à chaque noire, gigue d'envoi
```

## Tests

```bash
.venv/bin/pytest                                  # tout (hors matériel)
.venv/bin/pytest tests/test_hid_mk2.py            # un fichier
.venv/bin/pytest tests/test_hid_mk2.py::test_encoder_wraps_both_ways   # un test
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy src tests
```
