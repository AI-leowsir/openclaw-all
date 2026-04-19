#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
TEMPLATES="$ROOT/tasks/templates"
TASK_ID=${1:-}
PAGE_TYPE=${2:-product-page}
CALL_MODE=${3:-auto}

if [ -z "$TASK_ID" ]; then
  echo "usage: $0 <task-id> [page-type] [call-mode]" >&2
  exit 1
fi

TASK_DIR="$ROOT/tasks/$TASK_ID"
if [ -e "$TASK_DIR" ]; then
  echo "task already exists: $TASK_DIR" >&2
  exit 1
fi

mkdir -p \
  "$TASK_DIR/inputs/raw" \
  "$TASK_DIR/inputs/attachments" \
  "$TASK_DIR/learning-agent/normalized" \
  "$TASK_DIR/learning-agent/observations" \
  "$TASK_DIR/learning-agent/artifacts" \
  "$TASK_DIR/seo-organizing-agent/extracted-rules" \
  "$TASK_DIR/seo-organizing-agent/artifacts" \
  "$TASK_DIR/review" \
  "$TASK_DIR/writing-agent/input" \
  "$TASK_DIR/writing-agent/drafts" \
  "$TASK_DIR/writing-agent/revisions" \
  "$TASK_DIR/writing-agent/seo-package" \
  "$TASK_DIR/logs"

sed \
  -e "s/2026-04-15-001/$TASK_ID/g" \
  -e "s/product-page/$PAGE_TYPE/g" \
  -e "s/\"call_mode\": \"auto\"/\"call_mode\": \"$CALL_MODE\"/g" \
  "$TEMPLATES/task.json" > "$TASK_DIR/task.json"

cat > "$TASK_DIR/status.json" <<JSON
{
  "task_id": "$TASK_ID",
  "owner": "main",
  "status": "pending",
  "started_at": null,
  "finished_at": null,
  "output_files": [],
  "next_step": null,
  "error": null
}
JSON

cat > "$TASK_DIR/learning-agent/status.json" <<JSON
{
  "task_id": "$TASK_ID",
  "owner": "learning_agent",
  "status": "pending",
  "started_at": null,
  "finished_at": null,
  "output_files": [],
  "next_step": null,
  "error": null
}
JSON

cat > "$TASK_DIR/seo-organizing-agent/status.json" <<JSON
{
  "task_id": "$TASK_ID",
  "owner": "seo_organizing_agent",
  "status": "pending",
  "started_at": null,
  "finished_at": null,
  "output_files": [],
  "next_step": null,
  "error": null
}
JSON

cat > "$TASK_DIR/writing-agent/status.json" <<JSON
{
  "task_id": "$TASK_ID",
  "owner": "writing_agent",
  "status": "pending",
  "started_at": null,
  "finished_at": null,
  "output_files": [],
  "next_step": null,
  "error": null
}
JSON

cp "$TEMPLATES/source-list.yaml" "$TASK_DIR/inputs/source-list.yaml"
cp "$TEMPLATES/raw-readme.md" "$TASK_DIR/inputs/raw/README.md"

echo "initialized: $TASK_DIR"
