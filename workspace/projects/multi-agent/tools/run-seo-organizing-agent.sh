#!/usr/bin/env bash
# Low-level runner. Normal user-facing entry is tools/run-chain.sh.
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
usage: run-seo-organizing-agent.sh <task-id> [--mode synthesis|retrieval|compact]
       run-seo-organizing-agent.sh <task-id> [synthesis|retrieval|compact]

Modes:
  synthesis   Read learning_agent outputs and directly maintain SEO rules in knowledge/.
  retrieval   Retrieve active SEO rules/knowledge for this writing task and emit context-pack.md.
  compact     Layer, merge, compress, and re-index the SEO knowledge base.
USAGE
  exit 1
}

SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
TASK_ID=""
MODE="synthesis"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)
      [ "$#" -ge 2 ] || usage
      MODE="$2"
      shift 2
      ;;
    synthesis|retrieval|compact)
      MODE="$1"
      shift
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

case "$MODE" in
  synthesis|retrieval|compact) ;;
  *) echo "invalid seo organizing mode: $MODE" >&2; usage ;;
esac

TASK_DIR="$ROOT/tasks/$TASK_ID"
if [ ! -d "$TASK_DIR" ]; then
  echo "task not found: $TASK_DIR" >&2
  exit 1
fi

STAGE_DIR="$TASK_DIR/seo-organizing-agent"

mkdir -p \
  "$STAGE_DIR/extracted-rules" \
  "$STAGE_DIR/artifacts" \
  "$TASK_DIR/writing-agent/input"

if [ "$MODE" = "synthesis" ]; then
  MESSAGE=$(cat <<MSG
这是一次 SEO整理 Agent 执行任务，模式：synthesis（SEO 规则沉淀入库）。

项目根目录：$ROOT
任务目录：$TASK_DIR
任务阶段目录：$STAGE_DIR

请按以下顺序执行：
1. 读取你的工作区 AGENTS.md 与 /root/.openclaw/workspace/projects/multi-agent/skills/seo-organizing-agent/SKILL.md
2. 读取 $TASK_DIR/task.json
3. 优先读取 $TASK_DIR/learning-agent/artifacts/learning-output-manifest.yaml，并按 manifest 中列出的文件路径整理
4. 若 manifest 缺失，则读取以下标准目录并在 synthesis-summary.md 标记 manifest 缺口：
   - $TASK_DIR/learning-agent/normalized/
   - $TASK_DIR/learning-agent/observations/
   - $TASK_DIR/learning-agent/artifacts/
5. 只在 $STAGE_DIR/ 下写任务产物；SEO 规则维护结果直接写入 knowledge/
6. 直接维护这些目录：
   - $ROOT/knowledge/core/
   - $ROOT/knowledge/playbooks/seo/
   - $ROOT/knowledge/feedback/
   - $ROOT/knowledge/indexes/
7. 若上游输入不足，写阻塞说明到 $STAGE_DIR/artifacts/blocked.md，并把 $STAGE_DIR/status.json 更新为 waiting_input 或 blocked
8. 若执行成功，至少产出：
   - extracted-rules/
   - artifacts/synthesis-summary.md
   - artifacts/evidence-map.yaml
   - artifacts/reuse-boundary.md
   - artifacts/knowledge-write-report.md
   - artifacts/conflict-report.md
   - done.marker
9. 更新 $STAGE_DIR/status.json
10. 最后只返回一段中文摘要，必须包含更新过的 knowledge 路径

强制规则：
- 不产出待审批规则文件，不等待 approval。
- 只把可追溯的 SEO 规则写入 knowledge/。
- 相同规则要自动合并证据与来源，不重复落库。
- 冲突规则要自动裁决：更具体、更高置信、更新证据更强的规则保持 active；弱规则在 knowledge 中降为 shadow 或 archived，并在 conflict-report.md 记录。
- 中低置信结论不得伪装成稳定规则；如不能直接入库，写入 $STAGE_DIR/artifacts/reuse-boundary.md 或 blocked 说明边界。
- 不写最终文案。
- 只维护 SEO 相关规则；非 SEO 领域不要写入本知识库。
MSG
)
elif [ "$MODE" = "retrieval" ]; then
  MESSAGE=$(cat <<MSG
这是一次 SEO整理 Agent 执行任务，模式：retrieval（写作前 SEO 规则检索打包）。

项目根目录：$ROOT
任务目录：$TASK_DIR
任务阶段目录：$STAGE_DIR
context-pack 输出目录：$TASK_DIR/writing-agent/input

你的任务不是写文章，而是在写作前根据当前任务主题检索 active SEO 规则、知识和反馈，生成给 writing_agent 使用的临时上下文文件。

必须读取：
1. 你的工作区 AGENTS.md
2. /root/.openclaw/workspace/projects/multi-agent/skills/seo-organizing-agent/SKILL.md
3. /root/.openclaw/workspace/projects/multi-agent/docs/context-pack-workflow.md
4. $TASK_DIR/task.json

允许检索的范围：
- $ROOT/knowledge/indexes/
- $ROOT/knowledge/core/
- $ROOT/knowledge/playbooks/seo/
- $ROOT/knowledge/feedback/
- $STAGE_DIR/artifacts/
- $TASK_DIR/inputs/

禁止：
- 不写最终文案
- 不新增规则
- 不改写 knowledge/ 下的稳定内容
- 不使用 shadow、archived、证据不足或范围不匹配的规则
- 不读取其它 agent 的 session 历史作为规则来源
- 不根据常识、经验或猜测补充未命中的规则
- 不添油加醋；只检索、引用、打包和说明边界

成功时必须生成：
- $TASK_DIR/writing-agent/input/context-pack.md
- $STAGE_DIR/artifacts/retrieval-summary.md
- 更新 $STAGE_DIR/status.json 为 done
- 写 $STAGE_DIR/done.marker

context-pack.md 必须包含这些章节：
1. Task Profile
2. Matched Rules
3. Required Rules
4. Optional References
5. Source Evidence
6. Writing Boundaries
7. Required Output
8. Missing / Excluded Items

如果缺少适用的 active SEO 规则、规则与主题不匹配、只有 shadow/archived 规则、或资料不足，则不要生成 context-pack.md；必须生成：
- $TASK_DIR/writing-agent/input/context-pack.blocked.md
- $STAGE_DIR/artifacts/retrieval-summary.md
- 更新 $STAGE_DIR/status.json 为 blocked

blocked 文件必须写清：
- 阻塞原因
- 已检索范围
- 找到但不能用的内容
- 需要主 Agent 的下一步

最后只返回一段中文摘要，必须包含生成的 context-pack 路径或 blocked 路径。
MSG
)
else
  MESSAGE=$(cat <<MSG
这是一次 SEO整理 Agent 执行任务，模式：compact（SEO 规则分层压缩整理）。

项目根目录：$ROOT
任务目录：$TASK_DIR
任务阶段目录：$STAGE_DIR

你的任务不是写文章，而是对现有 SEO 知识库做自动整理。

必须读取：
1. 你的工作区 AGENTS.md
2. /root/.openclaw/workspace/projects/multi-agent/skills/seo-organizing-agent/SKILL.md
3. /root/.openclaw/workspace/projects/multi-agent/docs/context-pack-workflow.md
4. $ROOT/knowledge/indexes/
5. $ROOT/knowledge/core/
6. $ROOT/knowledge/playbooks/seo/
7. $ROOT/knowledge/feedback/
8. 如有必要，可参考 $STAGE_DIR/artifacts/ 下最近一次 synthesis/retrieval 产物

必须执行：
- 分层整理现有 SEO 规则
- 合并重复规则与重复证据
- 压缩冗长规则，保留可检索短规则与来源引用
- 将更强规则上提为 active，将过时或较弱冲突规则降为 shadow 或 archived
- 清理失效索引并重建 knowledge/indexes/
- 明确记录本轮 compact 的合并、裁决、归档和保留原因

成功时必须生成：
- $STAGE_DIR/artifacts/compact-summary.md
- $STAGE_DIR/artifacts/knowledge-write-report.md
- $STAGE_DIR/artifacts/conflict-report.md
- 更新 $STAGE_DIR/status.json 为 done
- 写 $STAGE_DIR/done.marker

禁止：
- 不写最终文案
- 不删除仍被更强规则引用的证据
- 不扩展到非 SEO 行业规则
- 不根据猜测生成新规则

若知识库状态不足以 compact，写 $STAGE_DIR/artifacts/blocked.md 并把 $STAGE_DIR/status.json 更新为 blocked。

最后只返回一段中文摘要，必须包含本轮整理过的 knowledge 路径。
MSG
)
fi

JSON=$("$SCRIPT_DIR/run-openclaw.sh" agent --agent seo_organizing_agent --message "$MESSAGE" --timeout 900 --json)
SUMMARY=$(printf '%s' "$JSON" | node -e 'let s="";process.stdin.on("data",d=>s+=d);process.stdin.on("end",()=>{const j=JSON.parse(s); const text=(j.result?.payloads?.[0]?.text)||(j.result?.finalAssistantVisibleText)||j.summary||""; process.stdout.write(String(text).replace(/\s+/g," ").trim());});')
printf '%s\n' "$JSON"
"$SCRIPT_DIR/send-feishu-report.sh" "SEO整理 Agent [$MODE] 已完成任务 $TASK_ID：$SUMMARY"
