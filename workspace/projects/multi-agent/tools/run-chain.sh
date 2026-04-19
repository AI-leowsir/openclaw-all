#!/usr/bin/env bash
# Unified chain entry for multi-agent tasks.
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: run-chain.sh <task-id> [--task learning|writing|full|compact|auto] [--mode strict|direct] [--resume] [--prepare-only] [--writing-context-pack <path>]

Task types:
  learning  main -> learning_agent -> seo_organizing_agent synthesis
  writing   main -> seo_organizing_agent retrieval -> context-pack -> writing_agent
  full      main -> learning_agent -> seo_organizing_agent synthesis -> seo_organizing_agent retrieval -> context-pack -> writing_agent
  compact   main -> seo_organizing_agent compact
  auto      infer from task.json

Modes:
  strict    Use the chain rules. Writing requires context-pack.md.
  direct    Bypass retrieval and call writing_agent --direct. Only for explicit small writing tasks.

Options:
  --resume               Reuse the existing successful raw context-pack.md for the same task.
                         Does not reuse reviewed context packs across tasks.
  --prepare-only         Stop after writing context is ready. Do not call writing_agent.
  --writing-context-pack Explicit context-pack path for writing_agent, e.g. context-pack.reviewed.md.
USAGE
  exit 1
}

SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
TASK_ID=""
TASK_KIND="auto"
MODE="strict"
RESUME=false
PREPARE_ONLY=false
WRITING_CONTEXT_PACK=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --task)
      [ "$#" -ge 2 ] || usage
      TASK_KIND="$2"
      shift 2
      ;;
    --mode)
      [ "$#" -ge 2 ] || usage
      MODE="$2"
      shift 2
      ;;
    --resume)
      RESUME=true
      shift
      ;;
    --prepare-only)
      PREPARE_ONLY=true
      shift
      ;;
    --writing-context-pack)
      [ "$#" -ge 2 ] || usage
      WRITING_CONTEXT_PACK="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      if [ -z "$TASK_ID" ]; then
        TASK_ID="$1"
        shift
      else
        usage
      fi
      ;;
  esac
done

if [ -z "$TASK_ID" ]; then
  usage
fi

case "$TASK_KIND" in
  learning|writing|full|compact|auto) ;;
  *) echo "invalid task kind: $TASK_KIND" >&2; usage ;;
esac
case "$MODE" in
  strict|direct) ;;
  *) echo "invalid mode: $MODE" >&2; usage ;;
esac

TASK_DIR="$ROOT/tasks/$TASK_ID"
if [ ! -d "$TASK_DIR" ]; then
  echo "task not found: $TASK_DIR" >&2
  exit 1
fi

SEO_STAGE_NAME="seo-organizing-agent"

mkdir -p "$TASK_DIR/writing-agent/input" "$TASK_DIR/logs"

resolve_path() {
  local path="$1"
  case "$path" in
    /*) printf '%s\n' "$path" ;;
    *) printf '%s/%s\n' "$ROOT" "$path" ;;
  esac
}

if [ -n "$WRITING_CONTEXT_PACK" ]; then
  WRITING_CONTEXT_PACK=$(resolve_path "$WRITING_CONTEXT_PACK")
fi

json_status() {
  local file="$1"
  python3 - "$file" <<'PY2'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
if not p.exists():
    print('missing')
    raise SystemExit
try:
    print(json.loads(p.read_text(encoding='utf-8')).get('status', 'missing'))
except Exception:
    print('invalid')
PY2
}

is_stage_done() {
  local stage="$1"
  [ "$(json_status "$TASK_DIR/$stage/status.json")" = "done" ] && [ -f "$TASK_DIR/$stage/done.marker" ]
}

mark_writing_blocked() {
  local code="$1"
  local message="$2"
  local next_step="$3"
  python3 - "$TASK_DIR" "$code" "$message" "$next_step" <<'PY2'
import json, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

task_dir = Path(sys.argv[1])
code = sys.argv[2]
message = sys.argv[3]
next_step = sys.argv[4]
status_path = task_dir / 'writing-agent' / 'status.json'
try:
    data = json.loads(status_path.read_text(encoding='utf-8'))
except Exception:
    data = {'task_id': task_dir.name, 'owner': 'writing_agent'}
data.update({
    'task_id': task_dir.name,
    'owner': 'writing_agent',
    'status': 'blocked',
    'finished_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'output_files': [],
    'next_step': next_step,
    'error': {'code': code, 'message': message},
})
status_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
PY2
}

detect_task_kind() {
  python3 - "$TASK_DIR/task.json" <<'PY2'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text(encoding='utf-8'))
task_type = str(data.get('task_type', '')).lower()
agents = data.get('agents') or {}
learning = str(agents.get('learning_agent', '')).lower() == 'enabled'
seo_organizing = str(agents.get('seo_organizing_agent', '')).lower() == 'enabled'
writing = str(agents.get('writing_agent', '')).lower() == 'enabled'
if 'compact' in task_type:
    print('compact')
elif writing and (learning or seo_organizing or 'learn' in task_type):
    print('full')
elif 'learn' in task_type or (learning and seo_organizing and not writing):
    print('learning')
elif 'write' in task_type or writing:
    print('writing')
else:
    print('writing')
PY2
}

run_learning_stage() {
  if is_stage_done "learning-agent"; then
    echo "[run-chain] learning_agent already done"
    return
  fi
  echo "[run-chain] starting learning_agent"
  "$SCRIPT_DIR/run-learning-agent.sh" "$TASK_ID"
}

require_learning_done() {
  if ! is_stage_done "learning-agent"; then
    local status
    status=$(json_status "$TASK_DIR/learning-agent/status.json")
    echo "[run-chain] learning_agent not done: $status" >&2
    return 1
  fi
}

run_synthesis_stage() {
  if is_stage_done "$SEO_STAGE_NAME" && [ "$RESUME" = true ]; then
    echo "[run-chain] seo_organizing_agent synthesis already done"
    return
  fi
  echo "[run-chain] starting seo_organizing_agent synthesis"
  "$SCRIPT_DIR/run-seo-organizing-agent.sh" "$TASK_ID" --mode synthesis
}

require_synthesis_done() {
  if ! is_stage_done "$SEO_STAGE_NAME"; then
    local status
    status=$(json_status "$TASK_DIR/$SEO_STAGE_NAME/status.json")
    echo "[run-chain] seo_organizing_agent synthesis not done: $status" >&2
    return 1
  fi
}

file_mtime() {
  local file="$1"
  if [ -f "$file" ]; then
    stat -c %Y "$file"
  else
    echo 0
  fi
}

run_retrieval_stage() {
  local context_pack="$TASK_DIR/writing-agent/input/context-pack.md"
  local blocked_pack="$TASK_DIR/writing-agent/input/context-pack.blocked.md"
  local request_marker="$TASK_DIR/writing-agent/input/.context-pack-requested-at"
  if [ "$RESUME" = true ] && [ -f "$context_pack" ] && { [ ! -f "$blocked_pack" ] || [ "$(file_mtime "$context_pack")" -gt "$(file_mtime "$blocked_pack")" ]; }; then
    echo "[run-chain] context-pack already exists: $context_pack"
    return
  fi
  date +%s > "$request_marker"
  echo "[run-chain] starting seo_organizing_agent retrieval"
  "$SCRIPT_DIR/run-seo-organizing-agent.sh" "$TASK_ID" --mode retrieval
}

run_compact_stage() {
  echo "[run-chain] starting seo_organizing_agent compact"
  "$SCRIPT_DIR/run-seo-organizing-agent.sh" "$TASK_ID" --mode compact
}

require_context_pack() {
  local context_pack="$TASK_DIR/writing-agent/input/context-pack.md"
  local blocked_pack="$TASK_DIR/writing-agent/input/context-pack.blocked.md"
  local request_marker="$TASK_DIR/writing-agent/input/.context-pack-requested-at"
  local request_mtime
  local context_mtime
  local blocked_mtime
  request_mtime=$(file_mtime "$request_marker")
  context_mtime=$(file_mtime "$context_pack")
  blocked_mtime=$(file_mtime "$blocked_pack")

  if [ "$blocked_mtime" -ge "$request_mtime" ] && [ "$blocked_mtime" -gt 0 ]; then
    mark_writing_blocked "CONTEXT_PACK_BLOCKED" "seo_organizing_agent 本轮生成了 context-pack.blocked.md，已中断，未进入 writing_agent。" "review_context_pack"
    echo "[run-chain] context pack blocked: $blocked_pack" >&2
    return 1
  fi

  if [ "$context_mtime" -lt "$request_mtime" ] || [ "$context_mtime" -eq 0 ]; then
    mark_writing_blocked "CONTEXT_PACK_MISSING" "seo_organizing_agent 本轮未生成新的 context-pack.md，已中断，未进入 writing_agent。" "run_seo_organizing_retrieval"
    echo "[run-chain] fresh context pack missing: $context_pack" >&2
    return 1
  fi
}

run_writing_stage() {
  echo "[run-chain] starting writing_agent"
  if [ -n "$WRITING_CONTEXT_PACK" ]; then
    echo "[run-chain] writing_agent context pack override: $WRITING_CONTEXT_PACK"
    "$SCRIPT_DIR/run-writing-agent.sh" "$TASK_ID" --context-pack "$WRITING_CONTEXT_PACK"
  else
    "$SCRIPT_DIR/run-writing-agent.sh" "$TASK_ID"
  fi
}

finish_prepare_only() {
  local context_pack="$TASK_DIR/writing-agent/input/context-pack.md"
  echo "[run-chain] prepare-only: writing context ready at $context_pack"
  echo "[run-chain] prepare-only: main agent may now create context-pack.reviewed.md and rerun with --writing-context-pack"
}

if [ "$TASK_KIND" = "auto" ]; then
  TASK_KIND=$(detect_task_kind)
fi

if [ "$PREPARE_ONLY" = true ] && [ "$MODE" = "direct" ]; then
  echo "[run-chain] --prepare-only cannot be used with --mode direct" >&2
  exit 1
fi

if [ "$PREPARE_ONLY" = true ] && [ "$TASK_KIND" != "writing" ] && [ "$TASK_KIND" != "full" ]; then
  echo "[run-chain] --prepare-only only applies to writing or full tasks" >&2
  exit 1
fi

if [ "$PREPARE_ONLY" = true ] && [ -n "$WRITING_CONTEXT_PACK" ]; then
  echo "[run-chain] --writing-context-pack cannot be used with --prepare-only" >&2
  exit 1
fi

echo "[run-chain] task=$TASK_ID kind=$TASK_KIND mode=$MODE resume=$RESUME"

if [ "$MODE" = "direct" ]; then
  echo "[run-chain] direct mode: calling writing_agent --direct"
  "$SCRIPT_DIR/run-writing-agent.sh" "$TASK_ID" --direct
  exit 0
fi

case "$TASK_KIND" in
  learning)
    run_learning_stage
    require_learning_done || exit 2
    run_synthesis_stage
    require_synthesis_done || exit 2
    echo "[run-chain] learning chain completed: $TASK_ID"
    ;;
  writing)
    run_retrieval_stage
    require_context_pack || exit 3
    if [ "$PREPARE_ONLY" = true ]; then
      finish_prepare_only
    else
      run_writing_stage
      echo "[run-chain] writing chain completed: $TASK_ID"
    fi
    ;;
  full)
    run_learning_stage
    require_learning_done || exit 2
    run_synthesis_stage
    require_synthesis_done || exit 2
    run_retrieval_stage
    require_context_pack || exit 3
    if [ "$PREPARE_ONLY" = true ]; then
      finish_prepare_only
    else
      run_writing_stage
      echo "[run-chain] full chain completed: $TASK_ID"
    fi
    ;;
  compact)
    run_compact_stage
    echo "[run-chain] compact chain completed: $TASK_ID"
    ;;
esac
