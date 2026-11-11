# mk-brain

Maschine MK2 en HID brut devant la Digitakt II. La spec fait foi :
[SPEC.md](SPEC.md). Avancement : [CHANGELOG.md](CHANGELOG.md).

## Installation (Mac, prototype)

```bash
cd mk-brain
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

## Installation (Raspberry Pi, slice 7)

Pi 3 Model B sous Raspberry Pi OS Trixie Lite 64 bits (hôte `mk-brain.local`,
utilisateur `pi`). Clone partiel du seul dossier `mk-brain/`, avec une clé de
déploiement en lecture seule (`~/.ssh/mkbrain_deploy`) :

```bash
sudo apt install git python3-venv python3-dev build-essential libasound2-dev \
  libusb-1.0-0-dev libudev-dev
git clone --filter=blob:none --no-checkout git@github.com:oalam/musiclib.git
cd musiclib && git sparse-checkout set mk-brain && git checkout master
cd mk-brain && python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
sudo cp deploy/99-mk-brain.rules /etc/udev/rules.d/
sudo udevadm control --reload && sudo udevadm trigger
sudo cp deploy/mk-brain.service deploy/mk-brain-pull.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable mk-brain-pull
sudo systemctl enable --now mk-brain
journalctl -u mk-brain -f        # journal du service
```

Au démarrage : `mk-brain play` sans attendre le réseau ; le `git pull` se
fait à part quand le réseau arrive et relance le service si `mk-brain/` a
changé. Extinction propre : SHIFT + ERASE tenus 2 s. Un nouveau
commit qui échoue deux fois revient à `state/last_good` ; MK2 ou DT2
absente (code de sortie 3) ne compte pas comme un échec, le service attend
le branchement (SPEC « Service et retour arrière »).

## Configuration

`config/default.yaml` : canal, courbe de vélocité, seuils d'aftertouch, quantize, arpégiateur, ses motifs et ses presets (`arp`, `arp.motifs`, `arp.presets` ; presets sauvés depuis la MK2 dans `state/arp-presets.json`), longueur de phrase,
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
