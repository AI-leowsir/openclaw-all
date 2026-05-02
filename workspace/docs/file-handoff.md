# 文件交接规范

## 任务目录标准结构

```text
<task_id>/
  task.json
  status.json
  inputs/
  learning-agent/
    status.json
    normalized/
    observations/
    artifacts/
    done.marker
  seo-organizing-agent/
    status.json
    extracted-rules/
    artifacts/
    done.marker
  writing-agent/
    input/
      context-pack.md
      context-pack.reviewed.md
      context-pack.blocked.md
    status.json
    drafts/
    revisions/
    seo-package/
    done.marker
  review/
    change-request.md
    conflict-decision.md
    feedback-candidate.yaml
    context-pack-diff.md
  logs/
  done.marker
```

## 输出根目录判定
- 本文默认描述的是标准 task 模式；此时 worker agent 的输出根目录分别是 `learning-agent/`、`seo-organizing-agent/`、`writing-agent/`。
- 如果 worker agent 被直接单独打开，当前工作区会是 `agent-workspaces/<agent-name>/`，而不是某个 `<task_id>/` 任务目录。
- 在这种独立调用模式下，输出必须写到 agent workspace 下的 `runs/<run-id>/`，不能在当前目录下再创建同名子目录。
- 例如：`agent-workspaces/learning-agent/learning-agent/`、`agent-workspaces/seo-organizing-agent/seo-organizing-agent/`、`agent-workspaces/writing-agent/writing-agent/` 都属于错误结构。

## 学习 Agent 输出
- `normalized/combined-text.md`
- `normalized/source-map.yaml`
- `observations/buyer-signals.yaml`
- `observations/content-structure.yaml`
- `observations/persuasion-patterns.yaml`
- `artifacts/source-summary.md`
- `artifacts/modality-report.yaml`
- `artifacts/fetch-report.md`
- `artifacts/learning-output-manifest.yaml`

### 学习 Agent 输出约束
- `fetch-report.md` 必须列出 URL、抓取方式、结果、失败原因、置信度。
- `source-map.yaml` 必须能反映来源页是否完整抓取，不能把 `partial` 页面伪装成完整来源。
- 对站点拆解类任务，FAQ / pricing / about / tools 等未完整覆盖时，必须在学习产物里单列 coverage gaps。

## SEO整理 Agent 输出
- `extracted-rules/*.md`
- `artifacts/synthesis-summary.md`
- `artifacts/evidence-map.yaml`
- `artifacts/reuse-boundary.md`
- `artifacts/knowledge-write-report.md`
- `artifacts/conflict-report.md`
- `artifacts/retrieval-summary.md`
- `artifacts/compact-summary.md`
- `writing-agent/input/context-pack.md`
- `writing-agent/input/context-pack.blocked.md`

### SEO整理 Agent 输出约束
- `evidence-map.yaml` 必须把规则映射回学习来源与置信度。
- `reuse-boundary.md` 必须明确哪些内容可直接复用，哪些只是迁移建议，哪些仍需补证据。
- `knowledge-write-report.md` 必须列出本轮新增、合并、覆盖、降级或归档的 knowledge 路径。
- `conflict-report.md` 必须记录自动冲突裁决的依据与结果。
- `context-pack.md` 只作为当前任务的原始临时检索包，不得被主 Agent 直接覆盖。

## 主 Agent 评审产物
- `writing-agent/input/context-pack.reviewed.md`
- `review/change-request.md`
- `review/conflict-decision.md`
- `review/feedback-candidate.yaml`
- `review/context-pack-diff.md`

### 主 Agent 评审产物约束
- `context-pack.reviewed.md` 必须基于原始 `context-pack.md` 生成，不得覆盖原文件。
- `change-request.md` 记录用户原始修改意见或结构化改写要求。
- `conflict-decision.md` 记录与 `Required Rules`、`Writing Boundaries`、`Source Evidence` 的冲突点和用户确认结果。
- `feedback-candidate.yaml` 只保存候选反馈，供 compact 每两天分析，不直接入正式规则。
- `context-pack-diff.md` 记录原始包与修订包的关键差异，便于追溯和复盘。

## 写作 Agent 输出
- `drafts/v1.md`
- `revisions/v2.md`
- `seo-package/metadata.yaml`
- `seo-package/outline.yaml`
- `seo-package/faq.yaml`
- `seo-package/internal-links.yaml`

## 下游启动条件
1. 上游 `status.json.status == done`
2. 上游 `done.marker` 存在
3. 上游 `output_files` 齐全
4. `learning-agent -> seo-organizing-agent` 交接时，`artifacts/fetch-report.md` 与 `normalized/source-map.yaml` 必须存在
5. 凡是面向可复用 SEO 模板、模块骨架、playbook、FAQ 模板、栏目页框架的结果，必须先经过 `seo_organizing_agent`，再交给主 agent 或 `writing-agent`
6. 写作修订任务中，如果主 Agent 显式指定 `context-pack.reviewed.md`，`writing_agent` 只读取该修订包，不回退到原始 `context-pack.md`
