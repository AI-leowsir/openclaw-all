#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(cd -- "$SCRIPT_DIR/../.." && pwd)
echo "[$(date -Is)] TODO: 这里后续接学习 Agent 的官方 skill 巡检执行逻辑。"
echo "建议入口: $ROOT/tools/run-openclaw.sh agent --agent main ..."
