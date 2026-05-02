# 知识采集 Skill — 开发规格文档 v4.1

## 0. 一句话定位

> 一个 OpenClaw Skill，通过三种模式（盯人、投喂、社群监控）采集付费社群中的高质量内容，写入本地 Obsidian 知识库，每天 18:30 推送日报到飞书知识群，通过用户自然语言反馈持续优化筛选精度。

---

## 1. 整体架构

```
主 Agent（日常对话对象 + 知识群交互）
├── 知识群消息 → 检测 chat_id → 加载知识 Skill 逻辑
├── 处理反馈 → 更新 MEMORY.md 中的偏好记录
├── 手动投喂 → 直接抓取写入 Obsidian
├── cron 定时 → spawn 临时会话执行抓取任务
│   └── 临时会话：CDP 抓取 → 判断/打分 → 写 Obsidian → 推日报 → 退出
└── MEMORY.md：偏好 + 状态
```

**核心原则：**
- 这是一个 Skill，不是独立 Agent
- 主 Agent 按 SKILL.md 处理知识群交互和反馈
- 重活（CDP 抓取 + 打分 + 写入）由 cron 定时 spawn 临时会话执行
- Obsidian 是唯一知识载体
- MEMORY.md 是唯一偏好载体

---

## 2. 三种采集模式

### 模式一：盯人（Person Follow）

**场景：** 你指定了一个人（如 @张三），Agent 自动抓取他在某平台发的所有帖子。

**触发：** cron 定时自动执行
**打分：** 不打分。只做简单判断——这条帖子跟用户关注方向相关吗？有实质内容吗？
**入库规则：**
- 相关且有实质 → 直接入库
- 不相关或纯闲聊 → 跳过
- 不确定 → 进 _pending/ 待确认

**抓取深度：** 主贴 + 点赞 Top 5 评论

### 模式二：手动投喂（Manual Feed）

**场景：** 你在知识群里发一条链接或粘贴一段内容。

**触发：** 你手动发送
**打分：** 不打分
**入库规则：** 直接入库，来源标记 `source: manual`
**回复：** "已入库 ✅"

如果是 URL → 主 Agent 用 CDP 浏览器打开抓取正文
如果是纯文本 → 直接存储

### 模式三：社群监控（Community Monitor）

**场景：** 你想知道整个社群今天发了什么跟你相关的内容，不限于特定人物。

**触发：** cron 定时自动执行
**打分：** 1-10 分制
**入库规则：**
- ≥ 7 分 → 直接入库 + 日报推送
- 5-6 分 → 进 _pending/ 待确认
- < 5 分 → 丢弃（不记录）
- ≥ 9 分 → 入库 + 实时推送到知识群

**抓取范围：** 社群公共讨论区的新帖（按时间倒序，抓取上次检查后的新内容）

---

## 3. 文件结构

```
~/.openclaw/workspace/skills/knowledge-agent/
├── SKILL.md                    # Skill 定义
├── config/
│   ├── targets.yaml            # 学习对象 + 监控对象列表
│   ├── platforms.yaml          # 平台抓取规则
│   └── settings.yaml           # 全局配置
└── state/
    └── scrape_history.json     # 抓取记录（防重复）
```

**Obsidian vault 目录：**

```
{VAULT_PATH}/
├── 知识库/
│   ├── AI出海/
│   ├── SEO/
│   ├── AI工具/
│   ├── PLG增长/
│   └── _MOC.md                 # 自动生成的索引页
├── _pending/                   # 待确认内容
└── _archive/                   # 已归档过期内容
```

---

## 4. 配置文件设计

### 4.1 targets.yaml

```yaml
# 模式一：盯人
person_targets:
  core_targets:
    - name: "张三"
      platform: "scys"
      profile_url: "https://scys.com/u/zhangsan"
      focus_topics: ["AI出海", "SEO"]
      priority: high
      scrape_interval_hours: 8

    - name: "李四"
      platform: "indie_hackers"
      profile_url: "https://indiehackers.com/lisi"
      focus_topics: ["PLG增长", "定价策略"]
      priority: medium
      scrape_interval_hours: 24

  temporary_targets: []
  # 通过对话命令添加，自动带 expires_at 字段
  # 格式同 core_targets，额外字段：
  #   added_at: "2026-04-22"
  #   expires_at: "2026-05-22"

# 模式三：社群监控
monitoring_targets:
  - name: "某出海社群全局监控"
    platform: "scys"
    community_url: "https://scys.com/community/xxx"
    type: community_monitor
    focus_topics: ["AI出海", "SEO", "AI工具", "PLG增长"]
    score_threshold: 7         # ≥7 才入库
    pending_threshold: 5       # 5-6 进待确认
    scrape_interval_hours: 4
    max_posts_per_scan: 50     # 每次最多扫描 50 条新帖
```

### 4.2 platforms.yaml

```yaml
platforms:
  scys:
    name: "某付费社群"
    base_url: "https://scys.com"
    login_required: true
    selectors:
      post_list: ".post-card"
      post_title: ".post-card h2"
      post_content: ".post-body"
      post_date: ".post-date"
      post_author: ".post-author"
      comments: ".comment-item"
      next_page: ".pagination .next"
    max_comments: 5
    max_pages: 3
    notes: "需要登录态，OpenClaw CDP 管理"

  indie_hackers:
    name: "Indie Hackers"
    base_url: "https://indiehackers.com"
    login_required: true
    selectors:
      # ... 选择器配置
    notes: "页面结构复杂时走 LLM 提取兜底"

  llm_fallback:
    enabled: true
    prompt: "从以下页面内容中提取：标题、作者、正文、发布时间、评论（前5条）"
```

### 4.3 settings.yaml

```yaml
# Obsidian
vault_path: ""                          # 用户填
knowledge_dir: "知识库"
pending_dir: "_pending"
archive_dir: "_archive"

# 推送
digest_time: "18:30"
digest_channel: "feishu"
digest_group_id: ""                     # 飞书知识群 chat_id，用户填
realtime_push_score: 9                  # 社群监控模式 ≥9 实时推送

# 抓取
max_scrape_time_per_target: 600         # 单个上限 10 分钟
max_scrape_time_total: 1800             # 一轮总上限 30 分钟
default_scrape_interval_hours: 8

# 临时学习对象
temp_target_duration_days: 30
```

---

## 5. 核心流程

### 5.1 盯人抓取流程（cron 临时会话执行）

```
1. 读取 targets.yaml 中的 person_targets
2. 按 priority 排序（high > medium > low）
3. 检查 scrape_history.json，跳过未到间隔的对象
4. 逐个串行抓取（CDP 同一时间只操作一个页面）：
   a. browser 打开目标人物主页
   b. 按 platforms.yaml 选择器提取帖子列表
   c. 对比 scrape_history，过滤已抓过的（按 URL 判断）
   d. 抓取新帖子的正文 + Top 5 高赞评论
   e. 选择器失败时走 LLM 兜底提取
   f. LLM 判断：相关且有实质？→ 入库 / 跳过 / 不确定进 pending
   g. 超时（10分钟/单个）跳下一个
5. 一轮总超时 30 分钟
6. 更新 scrape_history.json
```

### 5.2 社群监控流程（cron 临时会话执行）

```
1. 读取 targets.yaml 中的 monitoring_targets
2. browser 打开社群讨论区页面
3. 获取上次抓取时间之后的新帖列表（最多 max_posts_per_scan 条）
4. 逐条处理：
   a. 提取标题、作者、正文摘要
   b. LLM 打分 1-10（prompt 包含 focus_topics + 用户偏好）
   c. ≥ 7 → 抓取完整正文 + 评论 → 写入 Obsidian
   d. 5-6 → 抓取完整正文 → 写入 _pending/
   e. < 5 → 跳过
   f. ≥ 9 → 写入 + 实时推送到知识群
5. 更新 scrape_history.json
```

### 5.3 社群监控打分 Prompt

```
你是一个内容筛选助手。用户是一个做 AI 产品出海的创业者。

用户关注的方向：
{focus_topics}

用户的偏好（从历史反馈积累）：
{preferences_from_memory}

请为以下帖子评分（1-10）：
- 1-4：不相关或无实质价值
- 5-6：沾边但不确定是否需要
- 7-8：相关且有价值
- 9-10：高度相关，有数据/案例/深度洞察，必看

帖子标题：{title}
作者：{author}
正文前 500 字：{content_preview}

评分：___
一句话理由：___
推荐主题分类：___
```

### 5.4 手动投喂流程（主 Agent 直接执行）

```
用户在知识群发送内容：
├── 是 URL → browser 打开抓取正文 + 评论 → 写入 Obsidian → 回复"已入库 ✅"
├── 是纯文本 → 直接写入 Obsidian → 回复"已入库 ✅"
└── 附带"存一下"等指令 → 跳过任何判断，直接存

frontmatter 标记 source: manual
```

### 5.5 写入 Obsidian

**文件命名：** `{YYYY-MM-DD}-{title_slug}.md`
**唯一标识：** URL hash（更新时覆盖同文件）
**目录：** 按 LLM 判断的主题归入对应子目录

**frontmatter 模板：**

```yaml
---
title: "帖子标题"
author: "张三"
platform: "scys"
url: "https://..."
url_hash: "abc123"
published_at: "2026-04-20"
scraped_at: "2026-04-22T14:00:00+08:00"
updated_at: "2026-04-22T14:00:00+08:00"
score: 8                          # 社群监控模式才有分数
status: confirmed                 # confirmed / pending / archived
source: auto_person                # auto_person / auto_monitor / manual
topics: ["AI出海", "SEO"]
tags: ["竞品分析", "Reddit"]
source_type: post
comment_count: 5
also_posted_on: []
---
```

**正文结构：**

```markdown
# {标题}

> 作者：{author} | 平台：{platform} | 日期：{published_at}

## 核心内容

{正文}

## 精选评论（Top 5）

1. **{评论者1}**：{评论内容}
2. ...

## 元数据

- 原文链接：{url}
- 抓取时间：{scraped_at}
- 来源模式：{source}
```

**MOC 索引页（`_MOC.md`）：** 每次写入后自动更新，按主题分组列出所有条目。

### 5.6 日报推送

**触发：** cron 每日 18:30
**推送到：** 飞书知识群
**如果抓取未完成：** 最多等 30 分钟，推已有内容标注"部分数据"

**日报格式：**

```
📚 知识日报 | 4月22日

【今日概要】
今天从 3 个学习对象抓取了 8 条内容，社群监控发现 4 条
高质量帖子。张三发了一篇关于 Reddit 获客的深度复盘，
数据很扎实，值得重点看。

【盯人 · 已入库】
1. 张三：Reddit 获客的三个关键转折点
   三句话摘要...
2. 李四：2026 反链策略实战
   三句话摘要...

【社群监控 · 高分内容（已入库）】
3. 某人：AI 写作工具出海复盘（8分）
   三句话摘要...

【待确认】
4. 王五：关于 PLG 的一些思考 (6分)
5. 赵六：AI 工具定价漫谈 (5分)

回复"确认 4,5"入库 | 回复"4 不要"拒绝
回复任何反馈都会被记住，用于优化后续推送
```

**无新内容时：** 推一条"今日无新增内容"。

### 5.7 实时推送

**触发条件：** 社群监控模式中评分 ≥ 9 的内容
**推送到：** 飞书知识群

```
🔥 高质量内容提醒

社群中发现一条高价值帖子：

《AI 工具出海日本市场的三个关键点》⭐9/10
作者：某人
三句话摘要...

已自动入库。
```

### 5.8 反馈处理（主 Agent 在知识群中执行）

**确认命令：**
- `确认 4,5` → 将 `_pending/` 中对应内容移入正式知识库目录
- `确认全部` → 全部待确认内容入库

**拒绝命令：**
- `4 不要` → 从 `_pending/` 删除
- `这类不要` / `太浅了` / 任何自然语言反馈 → 写入 MEMORY.md 偏好区

**偏好存储：** MEMORY.md 中的 `知识采集偏好` 区块：

```markdown
## 知识采集偏好

- 不要纯观点，要有数据或案例支撑
- 定价策略类的内容多推
- 太短的帖子（3句话以内）不要
- 王五的内容质量一般，社群监控中可以降权
```

临时会话每次启动时读取此区块，注入打分/判断 prompt。

---

## 6. 对话命令

**在知识群中支持（主 Agent 处理）：**

**学习对象管理：**
- `关注 @张三 在 scys，重点看 AI 出海` → 添加临时盯人对象（30天）
- `长期关注 @张三 在 scys` → 添加为 core_target
- `取消关注 @张三` → 移除
- `关注列表` → 显示所有盯人对象 + 监控对象

**知识库管理：**
- `知识库状态` → 总条目、今日新增、待确认数、各主题分布
- `暂停抓取` / `恢复抓取` → 暂停/恢复 cron
- `立即抓取` → 手动触发一轮抓取

**手动投喂：**
- 直接发 URL → 抓取入库
- 直接发文本 → 存入库
- `存一下 {URL}` → 强制入库

**反馈：**
- `确认 1,3,5` → 待确认入库
- `4 不要` → 拒绝
- 自然语言反馈 → 记录偏好

---

## 7. cron 配置

```yaml
cron_tasks:
  # 盯人抓取 + 社群监控（每 4 小时）
  - name: "knowledge_scrape"
    schedule: "0 */4 * * *"
    action: spawn_subagent
    task: "执行知识采集任务：盯人抓取 + 社群监控"
    skill: "knowledge-agent"
    timeout: 1800

  # 每日日报（18:30）
  - name: "knowledge_digest"
    schedule: "30 18 * * *"
    action: spawn_subagent
    task: "生成今日知识日报，推送到知识群"
    skill: "knowledge-agent"
    channel: "{digest_group_id}"

  # 临时对象过期检查（每天 0:00）
  - name: "temp_target_cleanup"
    schedule: "0 0 * * *"
    action: spawn_subagent
    task: "检查临时学习对象过期状态"
    skill: "knowledge-agent"
```

---

## 8. 跨平台去重

- **同平台去重：** URL 精确匹配（scrape_history.json）
- **跨平台去重：** 同一作者，标题相似度 > 0.95 或内容相似度 > 0.8
- **处理方式：** 保留首份，后续在 frontmatter 加 `also_posted_on: ["platform2"]`
- **不同作者的相似内容不算重复**

---

## 9. 错误处理

- **单次抓取失败：** 重试 1 次，仍失败记录日志，下轮继续
- **连续 3 次同平台失败：** 日报末尾标注"⚠️ {平台} 抓取连续失败，请检查登录态"
- **Session 失效：** 推送告警到知识群
- **Obsidian 写入失败：** 内容暂存 state/ 目录，下轮重试

---

## 10. 环境依赖

**前置条件：**
- OpenClaw 已部署，CDP 浏览器已接管
- 各平台登录态已建立
- Obsidian vault 目录已创建
- 飞书知识群已建，OpenClaw bot 已加入
- settings.yaml 中 vault_path 和 digest_group_id 已填写

**不需要：**
- ❌ Python / pip
- ❌ 向量数据库 / embedding
- ❌ Obsidian REST API 插件
- ❌ 独立进程 / 独立 Agent 实例
- ❌ MCP Server
- ❌ EMA 偏好模型
- ❌ 三维打分

---

## 11. 验收标准

1. CDP 抓取成功率：主要平台连续 7 天 ≥ 90%
2. 盯人模式：指定人物的新帖 24 小时内被抓取并入库
3. 社群监控：LLM 打分与人工复核偏差 ≤ 2 分（抽查 30 条）
4. 日报准时：18:30 推送偏差 ≤ 5 分钟
5. 确认命令：响应 ≤ 10 秒
6. 偏好生效：反馈后下轮 prompt 包含该偏好
7. Obsidian 写入 ≥ 99%
8. 手动投喂：发链接后 30 秒内入库并回复
9. 实时推送：≥ 9 分内容抓到后 1 分钟内推送

---

## 12. 实施路线

**Phase 1（第 1-2 周）：盯人模式**
- CDP 抓取一个平台一个人跑通
- Obsidian 写入 + frontmatter
- scrape_history 防重复

**Phase 2（第 3 周）：手动投喂 + 知识群**
- 飞书知识群绑定
- 手动发链接/文本 → 入库
- 基础对话命令

**Phase 3（第 4 周）：日报 + 反馈**
- 18:30 日报生成 + 推送
- 确认/拒绝命令
- 自然语言偏好写入 MEMORY.md

**Phase 4（第 5-6 周）：社群监控**
- 社群全局扫描 + 1-10 打分
- 待确认队列
- 实时推送（≥ 9 分）

**Phase 5（第 7-8 周）：完善**
- 多平台扩展
- 跨平台去重
- 临时学习对象管理
- MOC 索引页自动维护
- 对话命令完善

---

*文档版本 v4.1 | 2026-04-22 | Skill + cron 架构 | 三种采集模式*
