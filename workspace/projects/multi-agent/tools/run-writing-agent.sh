#!/usr/bin/env bash
# Low-level runner. Normal user-facing entry is tools/run-chain.sh.
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: run-writing-agent.sh <task-id> [--direct] [--context-pack <path>]

Default mode requires tasks/<task-id>/writing-agent/input/context-pack.md
or an explicit context-pack path such as context-pack.reviewed.md.
Use --direct only for explicit small writing tasks that do not require learning/SEO rule retrieval.
USAGE
  exit 1
}

SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
TASK_ID=""
DIRECT=false
CONTEXT_PACK_OVERRIDE=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --direct)
      DIRECT=true
      shift
      ;;
    --context-pack)
      [ "$#" -ge 2 ] || usage
      CONTEXT_PACK_OVERRIDE="$2"
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

if [ "$DIRECT" = true ] && [ -n "$CONTEXT_PACK_OVERRIDE" ]; then
  echo "--context-pack cannot be used with --direct" >&2
  exit 1
fi

TASK_DIR="$ROOT/tasks/$TASK_ID"
if [ ! -d "$TASK_DIR" ]; then
  echo "task not found: $TASK_DIR" >&2
  exit 1
fi

mkdir -p "$TASK_DIR/writing-agent/input" "$TASK_DIR/writing-agent/revisions"
DEFAULT_CONTEXT_PACK="$TASK_DIR/writing-agent/input/context-pack.md"
BLOCKED_PACK="$TASK_DIR/writing-agent/input/context-pack.blocked.md"
CONTEXT_PACK="$DEFAULT_CONTEXT_PACK"

mark_blocked() {
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

file_mtime() {
  local file="$1"
  if [ -f "$file" ]; then
    stat -c %Y "$file"
  else
    echo 0
  fi
}

resolve_path() {
  local path="$1"
  case "$path" in
    /*) printf '%s\n' "$path" ;;
    *) printf '%s/%s\n' "$ROOT" "$path" ;;
  esac
}

if [ -n "$CONTEXT_PACK_OVERRIDE" ]; then
  CONTEXT_PACK=$(resolve_path "$CONTEXT_PACK_OVERRIDE")
fi

if [ "$DIRECT" != true ]; then
  if [ ! -f "$CONTEXT_PACK" ]; then
    if [ -n "$CONTEXT_PACK_OVERRIDE" ]; then
      mark_blocked "CONTEXT_PACK_OVERRIDE_MISSING" "主 Agent 指定的 context-pack 不存在，不能进入 writing_agent。" "prepare_reviewed_context_pack"
    else
      mark_blocked "CONTEXT_PACK_MISSING" "缺少 writing-agent/input/context-pack.md，不能进入 writing_agent。" "run_seo_organizing_retrieval"
    fi
    echo "context pack missing: $CONTEXT_PACK" >&2
    exit 3
  fi

  if [ -z "$CONTEXT_PACK_OVERRIDE" ] && [ -f "$BLOCKED_PACK" ] && [ "$(file_mtime "$BLOCKED_PACK")" -ge "$(file_mtime "$CONTEXT_PACK")" ]; then
    mark_blocked "CONTEXT_PACK_BLOCKED" "context-pack.blocked.md 新于或等于 context-pack.md，已中断，未进入 writing_agent。" "review_context_pack"
    echo "context pack is blocked: $BLOCKED_PACK" >&2
    exit 3
  fi
fi

if [ "$DIRECT" = true ]; then
  MESSAGE=$(cat <<MSG
这是一次写作 Agent 直接执行任务，模式：direct。

项目根目录：$ROOT
任务目录：$TASK_DIR

请按以下顺序执行：
1. 读取你的工作区 AGENTS.md 与 /root/.openclaw/workspace/projects/multi-agent/skills/writing-agent/SKILL.md
2. 读取 $TASK_DIR/task.json
3. 只处理 task.json 中已经明确的 brief 和写作要求
4. 只在 $TASK_DIR/writing-agent/ 下写文件
5. 若输入不足，写阻塞说明到 $TASK_DIR/writing-agent/revisions/blocked.md，并把 $TASK_DIR/writing-agent/status.json 更新为 waiting_input 或 blocked
6. 若执行成功，至少产出：
   - drafts/v1.md
   - seo-package/metadata.yaml
   - seo-package/outline.yaml
   - done.marker
7. 更新 $TASK_DIR/writing-agent/status.json
8. 最后只返回一段中文摘要

重要边界：
- direct 模式只适合用户已经给出明确 brief 的小型写作任务。
- 不负责学习、SEO 规则沉淀和检索。
- 不得自行检索 seo_organizing_agent 的 session 历史。
MSG
)
else
  MESSAGE=$(cat <<MSG
这是一次写作 Agent 执行任务，模式：context-pack。

项目根目录：$ROOT
任务目录：$TASK_DIR
临时上下文文件：$CONTEXT_PACK

请按以下顺序执行：
1. 读取你的工作区 AGENTS.md 与 /root/.openclaw/workspace/projects/multi-agent/skills/writing-agent/SKILL.md
2. 读取 /root/.openclaw/workspace/projects/multi-agent/docs/context-pack-workflow.md
3. 读取 $TASK_DIR/task.json
4. 读取 $CONTEXT_PACK
5. 只根据所提供 context-pack 中列出的 Required Rules、Writing Boundaries、Required Output 写作
6. 只读取该 context-pack 明确列出的文件；不得自行扩大检索范围
7. 只在 $TASK_DIR/writing-agent/ 下写文件
8. 若主 Agent 显式指定了修订版 context-pack，则必须以该文件为准，不得回退到原始 context-pack.md
9. 若 context-pack 信息不足，写阻塞说明到 $TASK_DIR/writing-agent/revisions/blocked.md，并把 $TASK_DIR/writing-agent/status.json 更新为 blocked
10. 若执行成功，至少产出：
    - drafts/v1.md
    - seo-package/metadata.yaml
    - seo-package/outline.yaml
    - done.marker
11. 更新 $TASK_DIR/writing-agent/status.json
12. 最后只返回一段中文摘要

禁止：
- 不直接学习原始来源
- 不直接沉淀长期记忆
- 不直接检索 knowledge/ 或其它 agent session
- 不自行创建新规则
- 不使用 context-pack 未列入的规则、影子规则或历史结论
- 如果 context-pack 要求中断，必须中断，不得继续写作
MSG
)
fi

JSON=$("$SCRIPT_DIR/run-openclaw.sh" agent --agent writing_agent --message "$MESSAGE" --timeout 900 --json)
SUMMARY=$(printf '%s' "$JSON" | node -e 'let s="";process.stdin.on("data",d=>s+=d);process.stdin.on("end",()=>{const j=JSON.parse(s); const text=(j.result?.payloads?.[0]?.text)||(j.result?.finalAssistantVisibleText)||j.summary||""; process.stdout.write(String(text).replace(/\s+/g," ").trim());});')
printf '%s\n' "$JSON"
"$SCRIPT_DIR/send-feishu-report.sh" "写作 Agent 已完成任务 $TASK_ID：$SUMMARY"
