#!/bin/sh
# Avant chaque lancement (SPEC « Service et retour arrière ») :
# retour à state/last_good après 2 échecs d'un nouveau commit, sinon
# git pull une fois par démarrage du Pi, limité à 10 s.
# Ne fait jamais échouer le lancement : on joue avec la copie locale.
cd "$(dirname "$0")/.." || exit 0
RUN=/run/mk-brain
mkdir -p state "$RUN"
head=$(git rev-parse HEAD)
good=$(cat state/last_good 2>/dev/null)
fails=$(cat state/fails 2>/dev/null || echo 0)

reinstall() {  # dépendances à jour si pyproject.toml a bougé entre $1 et HEAD
    if ! git diff --quiet "$1" HEAD -- pyproject.toml; then
        .venv/bin/pip install -q -e . || echo "pip install en échec"
    fi
}

if [ -n "$good" ] && [ "$head" != "$good" ] && [ "$fails" -ge 2 ]; then
    echo "retour arrière : $head ne démarre pas, $good"
    git reset -q --hard "$good"
    reinstall "$head"
    rm -f state/fails
    echo "back $(git rev-parse --short HEAD)" > "$RUN/sync"
    exit 0
fi

[ -e "$RUN/pulled" ] && exit 0
touch "$RUN/pulled"
if timeout 10 git pull -q --ff-only; then
    reinstall "$head"
    echo "sync $(git rev-parse --short HEAD)" > "$RUN/sync"
else
    echo "offline $(git log -1 --format=%cs)" > "$RUN/sync"
fi
exit 0
