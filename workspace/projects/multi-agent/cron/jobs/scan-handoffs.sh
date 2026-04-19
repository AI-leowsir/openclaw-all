#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(cd -- "$SCRIPT_DIR/../.." && pwd)
echo "[$(date -Is)] TODO: 这里后续接文件交接扫描逻辑，读取 tasks/*/{status.json,done.marker} 决定是否启动下游 Agent。"
echo "当前项目根目录: $ROOT"
