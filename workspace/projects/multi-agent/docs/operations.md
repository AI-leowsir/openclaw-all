# 日常操作

## 1. 创建新任务

```bash
sudo -n /root/.openclaw/workspace/projects/multi-agent/tools/init-task.sh 2026-04-15-001 product-page auto
```

参数：
- 第 1 个参数：任务 ID
- 第 2 个参数：页面类型，默认 `product-page`
- 第 3 个参数：调用模式，默认 `auto`

## 2. 手工发送飞书汇报

```bash
sudo -n /root/.openclaw/workspace/projects/multi-agent/tools/send-feishu-report.sh "学习 Agent 已完成本轮 ingest。"
```

## 3. 调用 OpenClaw CLI

```bash
sudo -n /root/.openclaw/workspace/projects/multi-agent/tools/run-openclaw.sh status
```

## 4. 启用 system cron 前的检查项
- 确认 `cron/jobs/*.sh` 已从 TODO 脚手架升级为真实执行逻辑
- 确认飞书发送脚本可用
- 确认任务目录与状态文件已按模板初始化
