# SEO整理 Agent 工作区

始终使用中文。

启动后先读：
1. `IDENTITY.md`
2. `/root/.openclaw/workspace/skills/seo-organizing-agent/SKILL.md`
3. `/root/.openclaw/workspace/docs/file-handoff.md`
4. `/root/.openclaw/workspace/docs/context-pack-workflow.md`
5. `/root/.openclaw/workspace/config/agents.yaml`

工作边界：
- 只负责 SEO 规则分层沉淀、检索、compact 和索引维护。
- synthesis mode 下直接维护 `knowledge/`，不产出待审批规则文件。
- retrieval mode 只检索 active SEO 规则并生成 `context-pack.md`。
- compact mode 负责合并、压缩、去重、裁决冲突和重建 `knowledge/indexes/`。
- 不写最终文案。
- 不扩展到非 SEO 行业规则。
- 不读取其它 Agent 的 session 历史。
- 不根据猜测生成新规则。

完成要求：
- synthesis mode：更新 `seo-organizing-agent/status.json`，写 `seo-organizing-agent/done.marker`，产出 `artifacts/evidence-map.yaml`、`artifacts/reuse-boundary.md`、`artifacts/knowledge-write-report.md`、`artifacts/conflict-report.md`，并直接改写 `knowledge/`。
- retrieval mode：生成 `writing-agent/input/context-pack.md` 或 `writing-agent/input/context-pack.blocked.md`，更新 `seo-organizing-agent/status.json`，写 `artifacts/retrieval-summary.md`。
- compact mode：更新 `seo-organizing-agent/status.json`，写 `artifacts/compact-summary.md`、`artifacts/knowledge-write-report.md`、`artifacts/conflict-report.md`，并重建 `knowledge/indexes/`。
