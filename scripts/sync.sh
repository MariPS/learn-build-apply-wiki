#!/usr/bin/env bash
# Commit + push su entrambe le repo: privata (tutto) e pubblica (solo il tool).
set -euo pipefail
cd "$(dirname "$0")/.."
msg="${1:?uso: scripts/sync.sh \"messaggio di commit\"}"
pub()  { git --git-dir=.git-public  --work-tree=. "$@"; }
priv() { git --git-dir=.git-private --work-tree=. "$@"; }

[ "$(pub remote get-url origin)" != "$(priv remote get-url origin)" ] \
  || { echo "ERRORE: le due repo puntano allo stesso remote"; exit 1; }

pub add -A
if pub ls-files | grep -qE '^(job-wiki|study-wiki|project-wiki)/|^wiki-config\.json$|^\.obsidian/'; then
  echo "ERRORE: dati personali nella repo pubblica, interrompo"; exit 1
fi

priv add -A
priv diff --cached --quiet || priv commit -m "$msg"
pub  diff --cached --quiet || pub  commit -m "$msg"

priv push -u origin main
pub  push -u origin main
