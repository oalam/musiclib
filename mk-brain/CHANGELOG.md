# Changelog — mk-brain

Format [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Chaque slice
de `SPEC.md` § Phases = une entrée balisée `[N]` et une version mineure.

## [0.1.0] - 2026-11-09

### Ajouté

- [0] Paquet `mk-brain` (Python 3.12, hidapi, Pillow ; ruff, mypy strict,
  pytest) et CLI `mk-brain`.
- [0] `hid_mk2.py` : décodage des rapports MK2 repris de cabl (boutons et
  encodeurs 0x01, pads 0x20), rapports LED 0x80/0x81/0x82, accès hidapi,
  exceptions typées `Mk2NotFoundError`, `Mk2OpenError`, `Mk2ReportError`.
- [0] `display.py` : image Pillow 1 bit → 8 rapports `0xE0|écran` de 256
  octets, mire de test.
- [0] `mk-brain list` et `mk-brain spike` : mire sur les deux écrans,
  balayage des LED, écho des contrôles (LED et écran droit), bilan des
  contrôles jamais vus.
- [0] Essai sur la MK2 : mire nette sur les deux écrans, LED justes,
  48 boutons, 16 pads et 9 encodeurs décodés (constats dans `SPEC.md`).

### Modifié

- [0] Bouton `MAIN` de cabl renommé `MASTER_PUSH` (appui sur l'encodeur
  maître, vérifié).
