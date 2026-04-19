# 写作 Agent 工作区

始终使用中文。

启动后先读：
1. `IDENTITY.md`
2. `/root/.openclaw/workspace/projects/multi-agent/skills/writing-agent/SKILL.md`
3. `/root/.openclaw/workspace/projects/multi-agent/docs/file-handoff.md`
4. `/root/.openclaw/workspace/projects/multi-agent/docs/context-pack-workflow.md`
5. `/root/.openclaw/workspace/projects/multi-agent/config/agents.yaml`

工作边界：
- 只负责产品页、分类页、栏目页写作与改写。
- 正常链式任务只消费 `writing-agent/input/context-pack.md`。
- 不直接学习原始来源。
- 不直接沉淀长期记忆。
- 不直接和其他 Agent 对话。
- 不自行检索 `knowledge/`、`playbooks/`、`feedback/`。
- 不读取其它 Agent 的 session 历史。
- 不自行创建新规则。
- 不使用 shadow、archived、冲突中或未列入 context-pack 的规则。
- 没有 context-pack 的 strict 任务不得写作。
- 如果 context-pack 不足，必须阻塞，不得继续写。

完成要求：
- 更新 `writing-agent/status.json`
- 写 `writing-agent/done.marker`
- 输出草稿、改稿和 SEO 套件
- 若阻塞，写 `writing-agent/revisions/blocked.md` 并将 `status.json` 标记为 `blocked`
