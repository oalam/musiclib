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
couleurs, dispositions A-H.

## Commandes

```bash
.venv/bin/mk-brain list               # interfaces HID de la MK2
.venv/bin/mk-brain spike              # mire, balayage LED, écho des contrôles, bilan à Ctrl-C
.venv/bin/mk-brain spike --raw --no-chase   # + rapports bruts en hexa
.venv/bin/mk-brain play               # pads → DT2 (AUTO CHANNEL), GROUP A-H = disposition,
                                      # compteur de phrases (SHIFT + PLAY / GROUP n = recalage)
.venv/bin/mk-brain play --dry-run     # sans DT2, notes affichées
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
