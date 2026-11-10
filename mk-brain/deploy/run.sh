#!/bin/sh
# Lance mk-brain play avec le commit courant (preuve de démarrage, boot.py).
cd "$(dirname "$0")/.." || exit 1
MKBRAIN_COMMIT=$(git rev-parse HEAD)
export MKBRAIN_COMMIT
exec .venv/bin/mk-brain play
