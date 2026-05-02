---
name: community-signal
description: 面向 OpenClaw 的社群情报推送 skill。用于监控指定人物和指定社群的新帖子，按 AI 工具、AI 产品、AI 出海、SEO、PLG、定价等主题筛选高质量内容，只通过飞书日报和少量实时提醒推送，不做知识库沉淀。
version: 0.1.0
metadata:
  openclaw:
    primaryEnv: OPENCLAW_HOME
---

# Community Signal

## 目标
- 监控指定人物与指定社群的新内容
- 只推送高价值信号，不做知识库
- 通过日报和少量实时提醒保护注意力
- 把去重、预算、投递记录、反馈偏好都落到本地状态文件

## 输出边界
- 对外输出只有两种：`digest`（日报）和 `realtime`（实时提醒）
- 不写 Obsidian
- 不把所有抓到的内容都存档
- 本地状态文件只服务于去重、节流、投递和反馈记忆

## 目录约定
```text
~/.openclaw/workspace/skills/community-signal/
├── SKILL.md
├── config/
│   ├── targets.yaml
│   ├── platforms.yaml
│   └── settings.yaml
├── prompts/
│   ├── scoring.txt
│   ├── digest.txt
│   └── realtime.txt
├── scripts/
│   ├── common.py
│   ├── due_targets.py
│   ├── mark_target_scan.py
│   ├── record_item.py
│   ├── build_digest.py
│   ├── send_message.py
│   ├── manage_targets.py
│   ├── show_status.py
│   ├── apply_feedback.py
│   └── cleanup_targets.py
└── state/
    ├── scrape_history.json
    ├── delivery_history.json
    ├── daily_stats.json
    ├── digest_candidates.json
    └── retry_queue.json
```

## 配置文件说明
- `config/*.yaml` 当前使用 **JSON-compatible YAML**。
- 也就是文件扩展名是 `.yaml`，但内容写成 JSON 语法，便于用 Python 标准库直接解析。
- 不要手动改成缩进式 YAML，除非同时给脚本补上真正的 YAML 解析器。

## 运行原则
1. 先看 `config/settings.yaml`、`config/targets.yaml`、`~/.openclaw/workspace/MEMORY.md`
2. 用 `scripts/due_targets.py` 判断当前应该抓哪些对象
3. 抓取通道：
   - 所有网页抓取、搜索结果读取、页面学习、内容提取、站点监控和资料采集只允许使用 OpenClaw 管理的 Chrome CDP/browser
   - 禁止 `web_fetch`、`web_search`、`browserless-fetch`、`curl`、`requests`、`urllib`、`httpx`、搜索引擎/API、old/mobile/JSON 端点直连或临时脚本抓取网页数据
   - CDP/browser 不可用时记录 coverage gap 并停止该来源，不做非 CDP 降级
4. 对每一条新内容都做主题匹配和质量评分
5. 每处理完一条内容，调用 `scripts/record_item.py`
6. 每处理完一个目标，调用 `scripts/mark_target_scan.py`
7. 到日报时间，调用 `scripts/build_digest.py --send`
8. 用户反馈进入 `scripts/apply_feedback.py`

## 抓取流程

## scys 平台
- 监控 `scys.com` 时，优先直接运行：
  ```bash
  node ~/.openclaw/workspace/skills/community-signal/scripts/scrape_scys.mjs \
    --entry-url "https://scys.com" \
    --limit 20 \
    --details
  ```
- 这个脚本会复用 OpenClaw 浏览器已有登录态，只从 `9223` 调试端口取首页卡片和可进入的详情页。
- 默认会先把首页切到 `全部 + 最新发布 + 简洁` 这套监控状态，再输出结构化 JSON。
- 第一阶段输出包含：首页标题、作者、标签、preview，以及 `scys` 详情页壳层的正文摘要、评论、外链。
- `scys` 首页卡片不是都能直接跳详情。没有 `/articleDetail/` 链接的卡片，先用首页 preview 筛；有详情链接的卡片，再看全文和评论后决定是否推送。
- 很多 `scys` 精华帖的完整正文在飞书 wiki。对已经 shortlisted 的候选，再补一跳：
  ```bash
  node ~/.openclaw/workspace/skills/community-signal/scripts/scrape_scys.mjs \
    --entry-url "https://scys.com" \
    --limit 20 \
    --details \
    --expand-feishu
  ```
- `--expand-feishu` 会跟进 `scys` 详情页里的飞书链接，滚动飞书文档内部容器，把完整正文拉全。任何依赖飞书正文才能判断质量的帖子，都不要只看 `scys` 摘要就最终打分。

### 盯人模式
1. 运行：
   ```bash
   python3 {baseDir}/scripts/due_targets.py --mode person
   ```
2. 对每个 due 的人物主页抓取新帖
3. 对每条新帖：
   - 提取标题、作者、URL、发布时间、正文、评论
   - 使用 `prompts/scoring.txt` 打 1-10 分
   - 生成一句话结论、三句话摘要、为什么值得看
4. 将结构化结果写成 JSON，喂给：
   ```bash
   python3 {baseDir}/scripts/record_item.py --input /tmp/item.json
   ```
5. 本轮人物抓取完成后：
   ```bash
   python3 {baseDir}/scripts/mark_target_scan.py \
     --mode person \
     --target-id "<target-id>"
   ```

### 社群监控模式
1. 运行：
   ```bash
   python3 {baseDir}/scripts/due_targets.py --mode monitor
   ```
2. 对每个 due 的社群页抓取上次检查之后的新帖
   - `scys` 目标优先跑 `node {baseDir}/scripts/scrape_scys.mjs --entry-url "<entry_url>" --limit <max_posts_per_scan> --details`
   - 对标题/标签/preview 命中的候选，再追加 `--expand-feishu` 拿完整正文
3. 使用 `prompts/scoring.txt` 评分
4. 每条内容都调用 `scripts/record_item.py`
5. 每个社群扫描完毕后，调用 `scripts/mark_target_scan.py`

## `record_item.py` 输入 JSON 结构
最小字段：
```json
{
  "title": "Reddit 获客的三个关键转折点",
  "author": "张三",
  "url": "https://example.com/post/1",
  "platform": "scys",
  "source_mode": "person",
  "source_name": "张三",
  "published_at": "2026-04-22T15:20:00+08:00",
  "score": 9,
  "summary": [
    "第一句摘要",
    "第二句摘要",
    "第三句摘要"
  ],
  "reason": "有明确转化数据和执行过程",
  "topics": ["AI出海", "SEO"],
  "verdict": "digest_or_realtime"
}
```

说明：
- `score` 必填，范围 `1-10`
- `summary` 最好是 2-3 句数组
- `verdict` 不是最终动作，最终动作由脚本根据阈值、预算、去重状态决定

## 每日工作流
### 实时提醒
- 当前关闭实时提醒：`realtime_max_per_day` 为 0，候选只进入日报。

### scys 监控
- 每天 23:45 只扫描 `scys.com` 当天出现的新帖子，命中候选写入次日的日报日期。
- 扫描命令：
  ```bash
  python3 {baseDir}/scripts/run_scan.py --mode monitor --platform scys --force
  ```

### 日报
- 到 `config/settings.yaml` 里的 `digest_time` 时运行：
  ```bash
  python3 {baseDir}/scripts/build_digest.py --date today --send
  ```

### GitHub AI Star Radar
- 每天监控 GitHub 上 star 上升较快的 AI 相关项目，覆盖 AI 工具、AI 产品、AI 开发者工具、AI agent、RAG、MCP、代码生成、评测、工作流自动化、模型/推理工具。
- 推送渠道复用 `config/settings.yaml`，当前飞书群：`oc_db72f7eba6d99f25f22e79678fb65e25`。
- 运行抓取并写入当日日报候选：
  ```bash
  python3 {baseDir}/scripts/run_github_star_radar.py --record-candidates
  ```
- 脚本通过 OpenClaw CDP 浏览器打开 GitHub 页面，像人工一样使用 GitHub 搜索框检索仓库，并在 `state/github_star_radar.json` 记录 star 快照。
- 首次运行会建立 baseline；后续日报优先按近 48 小时 star 增长排序，缺少两天历史时会参考 GitHub 仓库搜索结果和近期 push 活跃度，避免在缺少创建时间时伪造 stars/day。
- 输出默认中文，必须包含中文介绍、增长信号和 GitHub 项目链接。
- 每天默认写入 10 条 GitHub 搜索项目；AI 命中不足时，用增长明显的开发者/产品项目补齐。
- 它不是单独 skill、agent 或 LaunchAgent；由 `community-signal-digest` 在每天 17:00 先写入候选，再统一调用 `build_digest.py --date today --send` 推送。

## 管理命令
### 目标管理
```bash
python3 {baseDir}/scripts/manage_targets.py list
python3 {baseDir}/scripts/manage_targets.py add-person \
  --name "张三" \
  --platform "scys" \
  --profile-url "https://example.com/u/zhangsan" \
  --topics "AI出海,SEO" \
  --priority high \
  --temporary-days 30
python3 {baseDir}/scripts/manage_targets.py remove-person --name "张三"
python3 {baseDir}/scripts/manage_targets.py add-monitor \
  --name "某出海社群全局监控" \
  --platform "scys" \
  --community-url "https://example.com/community" \
  --topics "AI出海,AI工具,SEO" \
  --digest-threshold 7 \
  --realtime-threshold 9 \
  --scrape-interval-hours 4
```

### 状态查看
```bash
python3 {baseDir}/scripts/show_status.py --date today
```

### 反馈写入
```bash
python3 {baseDir}/scripts/apply_feedback.py --feedback "太浅了"
python3 {baseDir}/scripts/apply_feedback.py --feedback "多推定价策略"
```

### 清理过期临时对象
```bash
python3 {baseDir}/scripts/cleanup_targets.py
```

### 安装定时任务
```bash
python3 {baseDir}/scripts/install_cron.py
```

## 报告格式要求
- 实时提醒使用 `prompts/realtime.txt` 的结构
- 日报使用 `prompts/digest.txt` 的结构
- 默认中文输出
- 摘要要短，不写空话
- “为什么值得看”必须具体，不能只写“有价值”

## 边界
- 不改 OpenClaw 全局路由
- 不把低分内容也强行推送
- 不重复发送同一内容
- 不突破 `realtime_max_per_day` 和 `digest_max_items`
- 不把用户临时反馈包装成长期事实；只写入 `MEMORY.md` 的 `情报推送偏好` 区块
