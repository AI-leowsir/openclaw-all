# Agent 执行入口

## 主流程
1. 主 Agent（main）或人工初始化任务
2. 主 Agent（main）或人工触发学习 Agent
3. 学习 Agent 写文件并标记完成
4. SEO整理 Agent 的 synthesis 晚于学习 Agent，读取学习 Agent 输出后启动
5. SEO整理 Agent 写文件、维护 knowledge/ 并标记完成
6. 写作 Agent 的 retrieval / 写作链路晚于 SEO整理 Agent，读取整理结果后启动
7. 如有需要，主 Agent（main）或 cron 可额外触发 SEO整理 Agent 的 compact mode

## 1. 初始化任务

```bash
sudo -n /root/.openclaw/workspace/projects/multi-agent/tools/init-task.sh 2026-04-15-001 product-page auto
```

## 2. 填充来源
- 编辑 `tasks/<task-id>/inputs/source-list.yaml`
- 把正文、文档、图片、视频等放到 `tasks/<task-id>/inputs/raw/` 或 `inputs/attachments/`

## 3. 触发学习 Agent

```bash
sudo -n /root/.openclaw/workspace/projects/multi-agent/tools/run-learning-agent.sh 2026-04-15-001
```

## 4. 触发 SEO整理 Agent
- 正常链式任务通过 `tools/run-chain.sh`
- 如需单独维护，可调用：

```bash
sudo -n /root/.openclaw/workspace/projects/multi-agent/tools/run-seo-organizing-agent.sh 2026-04-15-001 --mode compact
```

## 5. 投递规则
- 学习 Agent、SEO整理 Agent、写作 Agent 完成后都通过 OpenClaw 向飞书群发送摘要
- compact 完成和 blocked 事件也必须发送摘要
