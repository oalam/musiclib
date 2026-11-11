#!/bin/sh
# Après chaque arrêt : compte les arrêts en erreur (lu par sync.sh).
# Le code de sortie 3 (boot.EXIT_NO_HARDWARE : MK2 ou DT2 absente) ne compte
# pas : la panne vient du branchement, pas du code tiré.
cd "$(dirname "$0")/.." || exit 0
[ "$SERVICE_RESULT" = "success" ] && exit 0
[ "$EXIT_CODE" = "exited" ] && [ "$EXIT_STATUS" = "3" ] && exit 0
mkdir -p state
n=$(cat state/fails 2>/dev/null || echo 0)
echo $((n + 1)) > state/fails
