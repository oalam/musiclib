#!/bin/sh
# Mise à jour, une fois par démarrage du Pi, quand le réseau est là
# (mk-brain-pull.service, SPEC « Service et retour arrière »).
# git pull limité à 30 s ; si mk-brain/ a changé, dépendances à jour puis
# une relance du service (coupure de quelques secondes). Sans réseau : rien.
cd "$(dirname "$0")/.." || exit 0
RUN=/run/mk-brain
mkdir -p "$RUN"
head=$(git rev-parse HEAD)
if timeout 30 git pull -q --ff-only; then
    echo "sync $(git rev-parse --short HEAD)" > "$RUN/sync"
    if ! git diff --quiet "$head" HEAD -- .; then
        if ! git diff --quiet "$head" HEAD -- pyproject.toml; then
            .venv/bin/pip install -q -e . || echo "pip install en échec"
        fi
        echo "nouveau code $(git rev-parse --short HEAD) : relance de mk-brain"
        sudo systemctl restart mk-brain
    fi
else
    echo "offline $(git log -1 --format=%cs)" > "$RUN/sync"
fi
exit 0
