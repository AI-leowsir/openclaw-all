# HEARTBEAT.md

## 定期检查项

- [ ] **浏览器标签清理**：每 2-4 小时检查一次，如果没有正在运行的 browser 任务但仍有残留的 http/https 标签页，执行 `exec bash ~/.openclaw/workspace/skills/browser-tab-guard/scripts/tab-guard.sh sweep` 清理。
