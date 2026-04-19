#!/usr/bin/env bash
set -euo pipefail
export HOME=/root
source /root/.nvm/nvm.sh >/dev/null 2>&1
exec /root/.local/share/pnpm/openclaw "$@"
