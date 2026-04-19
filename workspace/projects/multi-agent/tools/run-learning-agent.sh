#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
TASK_ID=${1:-}
if [ -z "$TASK_ID" ]; then
  echo "usage: $0 <task-id>" >&2
  exit 1
fi
TASK_DIR="$ROOT/tasks/$TASK_ID"
if [ ! -d "$TASK_DIR" ]; then
  echo "task not found: $TASK_DIR" >&2
  exit 1
fi
MESSAGE=$(cat <<MSG
这是一次学习 Agent 执行任务。

项目根目录：$ROOT
任务目录：$TASK_DIR

请按以下顺序执行：
1. 读取你的工作区 AGENTS.md 与 /root/.openclaw/workspace/projects/multi-agent/skills/learning-agent/SKILL.md
2. 读取 $TASK_DIR/task.json
3. 如果存在，则读取：
   - $TASK_DIR/inputs/source-list.yaml
   - $TASK_DIR/inputs/raw/
   - $TASK_DIR/inputs/attachments/
4. 只在 $TASK_DIR/learning-agent/ 下写文件
5. 若输入不足，写阻塞说明到 $TASK_DIR/learning-agent/artifacts/blocked.md，并把 $TASK_DIR/learning-agent/status.json 更新为 waiting_input
6. 若执行成功，至少产出：
   - normalized/combined-text.md
   - normalized/source-map.yaml
   - observations/buyer-signals.yaml
   - artifacts/source-summary.md
   - artifacts/fetch-report.md
   - artifacts/learning-output-manifest.yaml
   - done.marker
7. 更新 $TASK_DIR/learning-agent/status.json
8. `artifacts/learning-output-manifest.yaml` 必须列出交给 seo_organizing_agent 的所有文件路径，不得只用口头摘要交接
9. 最后只返回一段中文摘要，说明已完成什么或缺什么，并包含 manifest 路径
MSG
)
JSON=$("$SCRIPT_DIR/run-openclaw.sh" agent --agent learning_agent --message "$MESSAGE" --timeout 900 --json)
SUMMARY=$(printf '%s' "$JSON" | node -e 'let s="";process.stdin.on("data",d=>s+=d);process.stdin.on("end",()=>{const j=JSON.parse(s); const text=(j.result?.payloads?.[0]?.text)||(j.result?.finalAssistantVisibleText)||j.summary||""; process.stdout.write(String(text).replace(/\s+/g," ").trim());});')
printf '%s\n' "$JSON"
"$SCRIPT_DIR/send-feishu-report.sh" "学习 Agent 已完成任务 $TASK_ID：$SUMMARY"
