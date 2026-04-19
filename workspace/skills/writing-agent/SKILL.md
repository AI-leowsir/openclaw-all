---
name: writing-agent
description: 写作 Agent 的操作说明。用于根据 main agent 传入的 context-pack 生成产品页、分类页、栏目页初稿，并根据用户意见持续改写。
---

# 写作 Agent

## 目标
- 根据主 Agent 指定的 `context-pack` 生成产品页、分类页、栏目页
- 输出配套 SEO 套件
- 根据反馈改稿

## 默认输入
在正常链式任务中，唯一主输入是：

```text
writing-agent/input/context-pack.md
```

修改任务中，主 Agent 也可以显式指定：

```text
writing-agent/input/context-pack.reviewed.md
```

还需要读取：
- `task.json`
- `AGENTS.md`
- 本 Skill 文件
- `docs/context-pack-workflow.md`

## direct 模式输入
只有主 Agent 明确标记 direct 模式时，才可以不使用 context-pack。

Direct 模式只适合：
- 标题
- 短 FAQ
- 翻译
- 润色
- 用户已经给出明确 brief 的小型写作任务

Direct 模式不负责：
- 学习
- SEO 规则沉淀
- 检索旧规则

## 输出
- `drafts/*.md`
- `revisions/*.md`
- `seo-package/*.yaml`
- `done.marker`
- `status.json`

## context-pack 模式硬约束
- 必须先读取主 Agent 指定的 `context-pack`，默认是 `writing-agent/input/context-pack.md`。
- 如果主 Agent 显式指定了 `context-pack.reviewed.md`，必须以修订版为准，不回退到原始包。
- 只使用 context-pack 中列出的 Required Rules 和 Optional References。
- 只读取 context-pack 明确列出的文件。
- 不直接检索 `knowledge/`、`playbooks/`、`feedback/`。
- 不读取其它 Agent 的 session 历史。
- 不自行创建新规则。
- 不使用 shadow、archived、冲突中或未列入 context-pack 的规则。
- 如果 context-pack 不足以支撑写作，必须写 `revisions/blocked.md`，并把 `status.json` 更新为 `blocked`。

## 边界
- 不直接学习原始来源
- 不直接沉淀长期记忆
- 不绕过主 Agent（main）修改调度策略
- 不绕过 seo_organizing_agent 自行寻找规则
- 不在没有 context-pack 的 strict 任务中写作
