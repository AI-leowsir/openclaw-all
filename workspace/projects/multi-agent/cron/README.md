# Cron 说明

按当前框架：
- 主 Agent（main）负责主调度与实时对话
- 学习 Agent 可由主 Agent（main）或人工触发
- SEO整理 Agent 不直接由学习 Agent 调用，而是由 cron 晚于学习 Agent 扫描文件后启动
- 写作 Agent 不直接由 SEO整理 Agent 调用，而是由 cron 晚于 SEO整理 Agent 扫描文件后启动

当前脚本：
- `jobs/weekly-skill-scout.sh`：学习 Agent 每周六巡检 OpenClaw 官方 skill
- `jobs/run-organizing-from-learning.sh`：读取 `learning-agent/` 完成标记后启动 SEO整理 Agent
- `jobs/run-writing-from-organizing.sh`：读取 `seo-organizing-agent/` 完成标记后启动写作 Agent
- `jobs/scan-handoffs.sh`：仅用于诊断文件交接状态
