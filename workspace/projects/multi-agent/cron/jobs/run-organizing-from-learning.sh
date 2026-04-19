#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(cd -- "$SCRIPT_DIR/../.." && pwd)
for TASK_DIR in "$ROOT"/tasks/*; do
  [ -d "$TASK_DIR" ] || continue
  [ -f "$TASK_DIR/learning-agent/status.json" ] || continue
  [ -f "$TASK_DIR/learning-agent/done.marker" ] || continue
  [ -f "$TASK_DIR/seo-organizing-agent/status.json" ] || continue
  grep -q '"status": "done"' "$TASK_DIR/learning-agent/status.json" || continue
  grep -q '"status": "pending"' "$TASK_DIR/seo-organizing-agent/status.json" || continue
  TASK_ID=$(basename "$TASK_DIR")
  echo "[$(date -Is)] starting seo_organizing_agent for $TASK_ID"
  "$ROOT/tools/run-seo-organizing-agent.sh" "$TASK_ID"
done
