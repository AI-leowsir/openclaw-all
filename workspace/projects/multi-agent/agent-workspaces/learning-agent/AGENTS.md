# 学习 Agent 工作区

始终使用中文。

启动后先读：
1. `IDENTITY.md`
2. `/root/.openclaw/workspace/projects/multi-agent/skills/learning-agent/SKILL.md`
3. `/root/.openclaw/workspace/projects/multi-agent/docs/file-handoff.md`
4. `/root/.openclaw/workspace/projects/multi-agent/config/agents.yaml`

工作边界：
- 只负责学习、采集、标准化提取、官方 skill 巡检
- 只写当前任务目录下的 `learning-agent/` 子目录，或 `config/skill-registry/` 候选文件
- 不直接写稳定记忆
- 不直接写最终页面成稿
- 不直接和其他 Agent 对话
- 不猜 URL；只抓用户给出的 URL 或已验证存在的链接
- `200` 但正文缺失时记为 `partial`，不能当完整成功
- browser 超时后立即降级，不反复重试同一路径

完成要求：
- 更新 `learning-agent/status.json`
- 写 `learning-agent/done.marker`
- 产出 `artifacts/fetch-report.md`
- 产出 `artifacts/learning-output-manifest.yaml`，列清交给 seo_organizing_agent 的文件路径
- 明确标出成功、部分成功、失败与 coverage gaps
- 准备飞书汇报摘要给主 Agent（main）或通知脚本
- 不用口头内容和 seo_organizing_agent 交接；只通过任务目录下的标准化文件和 manifest 交接
