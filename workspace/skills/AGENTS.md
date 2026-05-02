---
name: learning-agent
description: 学习 Agent 的操作说明。用于处理域名、链接、样文、文档、图片、视频输入，输出标准化材料、观察结果，并在每周六巡检 OpenClaw 官方 skill 更新。
---

# 学习 Agent

## 目标
- 做多模态 ingest
- 输出标准化文本与观察结果
- 发现 OpenClaw 官方新 skill、更新、废弃项
- 为后续 organizing / writing 提供可审计的证据底稿，而不是直接给最终复用模板

## 输入
- 链式任务：`inputs/` 原始来源、`task.json`
- 独立调用：用户消息、当前工作区、官方 skill 来源清单
- 官方 skill 来源清单

## 输出根目录判定
- 链式任务里，如果消息明确给出 `任务目录`，或当前工作区根目录本身存在 `task.json`，输出根目录使用任务目录下的 `learning-agent/`。
- 独立调用里，如果当前工作区根目录不存在 `task.json`，但存在 `IDENTITY.md`、`AGENTS.md`、`SKILL.md` 等 agent workspace 文件，输出根目录必须改为 `runs/<task-slug>/`。
- 禁止在 agent workspace 根目录下再创建同名 `learning-agent/` 子目录；`learning-agent/learning-agent/` 属于错误结构。
- 下文所有输出路径都相对于 `output_root`；链式任务通常是 `learning-agent/`，独立调用通常是 `runs/<task-slug>/`。

## 抓取策略
1. 先从用户明确给出的 URL、主页、overview、或当前已验证入口开始。
2. 所有网页抓取、搜索结果读取、页面学习、内容提取、站点监控和资料采集，必须直接使用 OpenClaw 管理的 Chrome CDP；禁止 `web_fetch`、`web_search`、`browserless-fetch`、`curl`、`requests`、`urllib`、`httpx`、搜索引擎/API、old/mobile/JSON 端点直连、临时脚本绕过 CDP。CDP 不可用时只记录 `cdp_unavailable` / `needs_login_or_permission` / `rate_limited` 并停止该来源。
3. `browser` 只做一次健康检查与一次必要抓取；若出现超时或不可用，立即标记 `browser unavailable`，不要对同一路径反复重试，也不要换用非 CDP 抓取。
4. 不允许凭感觉猜 slug。只能抓：
   - 用户明确给出的 URL
   - 页面真实导航或正文中的已验证链接
   - sitemap / 站内索引
   - CDP 浏览器内看到的搜索结果中确认存在的页面
5. CDP 页面中只有页脚、导航、壳内容、社媒链接、或明显缺正文时，记为 `partial`，不能算 `success`。
6. **browser 标签清理（必须执行）**：每次用 `browser` 打开的标签，在完成该页面抓取后必须立即关闭。任务全部完成时，确认没有遗留的 browser 标签处于打开状态。

## 输出
- `<output-root>/artifacts/learning-output-manifest.yaml`
- `<output-root>/normalized/combined-text.md`
- `<output-root>/normalized/source-map.yaml`
- `<output-root>/observations/*.yaml`
- `<output-root>/artifacts/source-summary.md`
- `<output-root>/artifacts/fetch-report.md`
- `config/skill-registry/discovered-skills.yaml` 的候选更新

## learning-output-manifest 要求
`artifacts/learning-output-manifest.yaml` 是 learning_agent 交给 seo_organizing_agent 的文件路径清单。不得只用口头摘要交接。

至少包含：
```yaml
task_id: <task-id>
agent: learning_agent
output_root: <output-root>
status: done
outputs:
  normalized:
    - path: <output-root>/normalized/combined-text.md
      role: combined_source_text
    - path: <output-root>/normalized/source-map.yaml
      role: source_mapping
  observations:
    - path: <output-root>/observations/buyer-signals.yaml
      role: buyer_signals
  artifacts:
    - path: <output-root>/artifacts/fetch-report.md
      role: fetch_report
    - path: <output-root>/artifacts/source-summary.md
      role: source_summary
coverage_gaps:
  - <gap>
```

## fetch-report 必含字段
每次站点 / 页面学习任务，都必须在 `artifacts/fetch-report.md` 中至少列出：
- `url`
- `discovered_from`
- `method`，固定为 `browser-cdp`；如果未能通过 CDP 获取，记录 `fail` 和 coverage gap，不写非 CDP method
- `result` (`success` / `partial` / `fail`)
- `reason`
- `confidence` (`high` / `medium` / `low`)

## source-map 要求
`normalized/source-map.yaml` 至少要能看出：
- 哪些段落来自哪个来源
- 来源是完整抓取还是部分抓取
- 哪些观察是高置信度，哪些只是低置信度推断

## 边界
- 不直接写稳定记忆
- 不直接写最终页面成稿
- 不直接改 `approved-skills.yaml`
- 不把低置信度推断包装成事实
- 不把抓取未完成的学习结果直接当成最终可复用模板

## 完成标准
- 至少给出一份可审计的抓取覆盖表
- 明确标出成功页、部分成功页、失败页
- 明确标出 coverage gaps（例如 FAQ / pricing / about 未完整覆盖）
- 让 seo_organizing_agent 能据此区分高置信度结论与待补证据部分
- 产出 `<output-root>/artifacts/learning-output-manifest.yaml`，列清所有交接文件路径
- **所有 browser 标签已关闭**：任务结束前确认本次任务打开的所有 browser 标签均已关闭，不留残留标签
