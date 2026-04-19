# Deep Review 定时触发提示词

本文件仅包含触发指令。所有规则、结构、写作要求均以 `SKILL.md` 为唯一权威源。

---

## 每天 22:00：日复盘

执行 `deep-review`，完成今天的**日复盘**。

执行前：
1. 读取 `SKILL.md` 中的完整规则
2. 读取 `references/session-index-template.md`
3. 读取 `references/discovery-prompt.md`
4. 读取 `references/daily-template.md`

按 `SKILL.md` 中的 Workflow（Phase 1 → Phase 2）和 Delivery rules 执行。

特别注意：
- 必须包含 `明日改进动作`（必填，最多3条）
- 必须包含 `昨日改进回顾`（如有昨日复盘）
- 复盘范围不限于当前会话，必须覆盖当天全部证据窗
- 时间判定以北京时间（Asia/Shanghai）为准

---

## 每周日 22:40：周复盘

执行 `deep-review`，完成本周的**周复盘**。

执行前：
1. 读取 `SKILL.md` 中的完整规则
2. 读取 `references/session-index-template.md`
3. 读取 `references/weekly-template.md`
4. 读取 `references/weekly-notification-template.md`

按 `SKILL.md` 中的 Workflow（Phase 1 → Phase 2）和 Delivery rules 执行。

特别注意：
- 必须包含 `上周动作回顾`（section 0）
- 以本周日复盘文件为主要叙事输入，sessions/transcripts 仅做覆盖验证
- 必须评估长期沉淀阈值
- `MEMORY.md` 不自动写入，必须等用户审批
- 周复盘完成后必须通知用户
