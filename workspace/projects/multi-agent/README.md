# SEO Multi-Agent

这是独立站 SEO 多 Agent 系统的第一版骨架目录。

当前范围：
- 产品页
- 分类页
- 栏目页
- 公众号与推特规则预留

当前角色：
- 主 Agent（main）：总调度与实时对话
- 学习 Agent：学习、采集、技能巡检
- 整理 Agent：知识沉淀与规则整理
- 写作 Agent：页面写作与改写

当前约束：
- Agent 之间不直接对话，只通过文件交接
- 子 Agent 默认使用 isolated session
- 每个 Agent 每轮完成后必须由 OpenClaw 向飞书群 `oc_18670e031c0c78335ff946d6d1fff3ee` 汇报
- 未经用户确认的长期偏好，不允许写入稳定记忆
