# 架构总览

## 1. 命名

展示名：
- 主 Agent（main）
- 学习 Agent
- SEO整理 Agent
- 写作 Agent

内部 ID：
- `main`
- `learning_agent`
- `seo_organizing_agent`
- `writing_agent`

## 2. 职责

### 主 Agent（main）
- 唯一主 Agent
- 接收用户任务与修改意见
- 创建任务、决定调用链、汇总结果
- 需要时触发 `seo_organizing_agent compact mode`

### 学习 Agent
- 处理域名、链接、样文、文档、图片、视频输入
- 输出标准化提取结果与观察结果
- 每周六主动学习 OpenClaw 官方 skill 的新增、更新、废弃情况

### SEO整理 Agent
- 读取学习 Agent 的标准化产物
- 直接维护 `knowledge/core`、`knowledge/playbooks/seo`、`knowledge/feedback`、`knowledge/indexes`
- 负责 SEO 规则分层沉淀、写作前检索、定期 compact 整理
- 只处理 SEO 相关规则；其他行业未来应建立独立整理 Agent

### 写作 Agent
- 只读取 `context-pack.md` 中列出的 active SEO 规则与引用
- 输出产品页、分类页、栏目页初稿和改稿
- 生成标题、描述、FAQ、内链建议等 SEO 套件

## 3. 启动机制
- 实时任务由主 Agent（main）发起
- 定时维护可由 system cron 触发 `seo_organizing_agent compact mode`
- Agent 之间不互相启动
- 接力执行靠 `status.json` 与 `done.marker`

## 4. 调用策略
- `auto`：主 Agent（main）自主编排
- `force:<agent>`：只调用指定 Agent
- `skip:<agent>`：跳过指定 Agent
- `chain:[...]`：指定调用顺序

## 5. Session 策略
- 主 Agent（main）实时对话：`main`
- 子 Agent 执行任务：`isolated`
- 一次性任务：`isolated + delete-after-run`

## 6. 投递策略
- 默认通知渠道：飞书群 `oc_18670e031c0c78335ff946d6d1fff3ee`
- 每个 Agent 每轮任务完成后必须汇报
- 中间碎步骤不直接投递，只落盘状态
- 遇到阻塞、自动冲突裁决或 compact 完成时立即投递摘要
