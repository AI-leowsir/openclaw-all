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
- `inputs/` 原始来源
- `task.json`
- 官方 skill 来源清单

## 抓取策略
1. 先从用户明确给出的 URL、主页、overview、或当前已验证入口开始。
2. 先用轻量方式：`web_fetch` / 已知静态入口。
3. 只有在静态抓取明显不完整、且确有必要时，才尝试 `browser`。
4. `browser` 只做一次健康检查与一次必要抓取；若出现超时或不可用，立即标记 `browser unavailable`，不要对同一路径反复重试。
5. 不允许凭感觉猜 slug。只能抓：
   - 用户明确给出的 URL
   - 页面真实导航或正文中的已验证链接
   - sitemap / 站内索引
   - 已验证搜索结果中确认存在的页面
6. `200` 但只有页脚、导航、壳内容、社媒链接、或明显缺正文时，记为 `partial`，不能算 `success`。
7. 直连脚本兜底时统一用 `python3`，不要用 `python`。

## 输出
- `artifacts/learning-output-manifest.yaml`
- `normalized/combined-text.md`
- `normalized/source-map.yaml`
- `observations/*.yaml`
- `artifacts/source-summary.md`
- `artifacts/fetch-report.md`
- `config/skill-registry/discovered-skills.yaml` 的候选更新

## learning-output-manifest 要求
`artifacts/learning-output-manifest.yaml` 是 learning_agent 交给 seo_organizing_agent 的文件路径清单。不得只用口头摘要交接。

至少包含：
```yaml
task_id: <task-id>
agent: learning_agent
status: done
outputs:
  normalized:
    - path: learning-agent/normalized/combined-text.md
      role: combined_source_text
    - path: learning-agent/normalized/source-map.yaml
      role: source_mapping
  observations:
    - path: learning-agent/observations/buyer-signals.yaml
      role: buyer_signals
  artifacts:
    - path: learning-agent/artifacts/fetch-report.md
      role: fetch_report
    - path: learning-agent/artifacts/source-summary.md
      role: source_summary
coverage_gaps:
  - <gap>
```

## fetch-report 必含字段
每次站点 / 页面学习任务，都必须在 `artifacts/fetch-report.md` 中至少列出：
- `url`
- `discovered_from`
- `method` (`web_fetch` / `browser` / other)
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
- 产出 `artifacts/learning-output-manifest.yaml`，列清所有交接文件路径
