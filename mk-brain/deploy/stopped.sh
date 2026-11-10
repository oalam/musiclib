#!/bin/sh
# Après chaque arrêt : compte les arrêts en erreur (lu par sync.sh).
cd "$(dirname "$0")/.." || exit 0
[ "$SERVICE_RESULT" = "success" ] && exit 0
mkdir -p state
n=$(cat state/fails 2>/dev/null || echo 0)
echo $((n + 1)) > state/fails
