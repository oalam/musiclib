#!/bin/sh
# Avant chaque lancement (SPEC « Service et retour arrière ») :
# retour à state/last_good après 2 échecs d'un nouveau code.
# Le git pull n'est plus ici : pull.sh le fait à part, à l'arrivée du
# réseau, pour que le jeu démarre sans l'attendre.
# Ne fait jamais échouer le lancement : on joue avec la copie locale.
cd "$(dirname "$0")/.." || exit 0
RUN=/run/mk-brain
mkdir -p state "$RUN"
head=$(git rev-parse HEAD)
good=$(cat state/last_good 2>/dev/null)
fails=$(cat state/fails 2>/dev/null || echo 0)

# Nouveau code = mk-brain/ diffère de last_good (un commit du reste du dépôt ne compte pas).
if [ -n "$good" ] && [ "$fails" -ge 2 ] && ! git diff --quiet "$good" HEAD -- .; then
    echo "retour arrière : $head ne démarre pas, $good"
    git reset -q --hard "$good"
    if ! git diff --quiet "$head" HEAD -- pyproject.toml; then
        .venv/bin/pip install -q -e . || echo "pip install en échec"
    fi
    rm -f state/fails
    echo "back $(git rev-parse --short HEAD)" > "$RUN/sync"
fi
exit 0
