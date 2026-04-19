# Session: 2026-04-11 14:48:30 UTC

- **Session Key**: agent:main:feishu:group:oc_bf9079a6ce01cfd169741382dc1f74ad
- **Session ID**: 0c8107ce-8e31-40d5-b429-9d6c697871fd
- **Source**: feishu

## Conversation Summary

assistant: [[reply_to_current]] 对，这张图把关键东西补全了，而且说明那边其实**已经不该继续问卷了，应该直接落地**。  

我从图里提取到的关键信息：

### 已经基本定下来的部分
- 日复盘范围
- 周复盘范围
- 群消息规则
- 子会话规则
- 输出结构
- 偏差分级
- 根因规则
- 文件路径
- 周复盘与 `MEMORY.md` 的关系
- `MEMORY.md` 允许写入的内容类型

### 图里明确写的结论
> **现在整个设计已经基本闭环了**

### 图里明确写的下一步
1. **更新 `deep-review/SKILL.md`**
2. **重写 references**
   - 日复盘模板
   - 周复盘模板
   - `MEMORY.md` 提炼规则模板
3. **更新 cron prompt**

---

## 所以这轮问答其实可以停了
因为你这张图说明：
- 关键流程项不是没定义
- 而是**已经大部分定义完了**
- 剩下最该做的是**从会话内容中抽取定稿并落文件**

也就是说，当前正确动作应该从：

**“继续确认流程”**

切换成：

**“把已确认内容整理进 skill 文档和 references”**

---

## 我现在给你的最新判断
“任务组1号”当前任务状态应更新为：

### 当前状态
**流程设计基本闭环，进入落地阶段**

### 待执行事项
- 从现有会话中抽取最终规则
- 写入 `deep-review/SKILL.md`
- 重写 3 份 references
- 更新 cron prompt

### 不再优先做的事
- 不再继续大范围问答式确认
- 不再继续泛谈原则

---

## 现在最适合你的下一步
如果按这张图走，下一步最对的是：

### A. 我帮你继续从会话里抽“可直接写入 skill 的最终规则清单”
或者
### B. 我直接开始帮你起草 `deep-review/SKILL.md` 的结构稿

我建议直接 **A → B 连着做**，先抽规则，再落文档。  
如果你点头，我下一条就直接给你：

**《deep-review skill 最终规则清单（可直接写入版）》**
user: <relevant-memories>
The following are stored memories for user "default". Use them to personalize your response:
- As of 2026-04-05, the workspace includes `memory/2026-04-05.md`, base files `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `HEARTBEAT.md`, and installed skill `debug-pro`.
- As of 2026-04-05, the user prefers proactive execution with progress updates after each stage, rather than extended explanation without producing files.
- As of 2026-04-05, the user's OpenClaw workspace local repository is at `/root/.openclaw/workspace`.
- As of 2026-04-05, the automated skill sync files are in `/root/.openclaw/workspace/tools/skill-sync/`, including `sync_self_improving_agent.sh`, `config/self_improving_agent.env.example`, `config/self_improving_agent.env`, and `README.md`.
- As of 2026-04-05, the `self-improving-agent` skill was pushed to GitHub repository `https://github.com/AI-leowsir/skill-.git` under path `apps/self-improving-agent skill/` on branch `main`, with commit `6f8d4b5` and message `Add self-improving-agent skill under apps`.
</relevant-memories>

Conversation info (untrusted metadata):
```json
{
  "message_id": "om_x100b5297be9584a0c3de0c8eac285ea",
  "sender_id": "ou_f8403fe80fca27f9322804bba837c396",
  "conversation_label": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "sender": "ou_f8403fe80fca27f9322804bba837c396",
  "timestamp": "Sat 2026-04-11 20:31 GMT+8",
  "group_subject": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "is_group_chat": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "ou_f8403fe80fca27f9322804bba837c396",
  "id": "ou_f8403fe80fca27f9322804bba837c396",
  "name": "ou_f8403fe80fca27f9322804bba837c396"
}
```

[message_id: om_x100b5297be9584a0c3de0c8eac285ea]
ou_f8403fe80fca27f9322804bba837c396: 进入 [MEMORY.md](MEMORY.md) 的必须是内容本身。

\- 不要路径
\- 不要索引
\- 不要“去哪里看详细文件”
\- 要的是能直接留在 [MEMORY.md](MEMORY.md) 里的有效内容

这个标准更严格，也更像真正的“长期记忆沉淀”。那这样一来，结论就很明确了
[MEMORY.md](MEMORY.md) 里不能放“完整周复盘摘要”
因为那样还是太厚、太像周报。
[MEMORY.md](MEMORY.md) 里应该只放：
周复盘提炼后的长期有效内容。

也就是说，进入 [MEMORY.md](MEMORY.md) 的不是：

\- 本周发生了什么全量摘要
\- 本周有哪些动作
\- 本周路径在哪

而是：

\- 这周确认了哪些长期规则
\- 这周确认了哪些稳定结论
\- 这周发现了哪些会持续影响未来的模式
所以现在要把 [MEMORY.md](MEMORY.md) 的周复盘写法收得更狠
我建议变成：
每周周复盘产出两层
第一层：详细周复盘文件
写完整内容，放在 weekly 文件里
第二层：[MEMORY.md](MEMORY.md)
只写周复盘提炼后的长期内容那 [MEMORY.md](MEMORY.md) 里会是什么样子
应该像这样：
\#\# Long\-term Review Notes \- 2026\-04\-13 

\- 涉及复盘、流程设计、skill 设计时，必须先锁定对象边界、输出结构与写入位置，再展开方案。 
\- 群消息是当前任务复盘的主来源，应按链路聚合扫描和输出，不能只看局部片段。 
\- 日复盘聚焦当天执行、偏差、次日动作；长期规则只在周复盘中沉淀。 


注意这里写进去的东西必须满足：

\- 对未来还有用
\- 不是一次性周报
\- 不是临时动作
\- 不是路径索引
\- 不是详细过程
所以我们现在要重新定义
周复盘有哪些内容
周复盘详细文件里仍然保留：

\- 本周主要工作
\- 本周反复出现 / 被强调的事
\- 本周关键事实
\- 本周重复偏差
\- 本周根因归类
\- 本周产出与遗留问题
\- 下周动作
\- 长期规则沉淀
\- 复盘范围
但进入 [MEMORY.md](MEMORY.md) 的只有：
周复盘筛出来的“长期内容”
包括两类：
1. 长期规则
例如：

\- 做流程设计时先锁边界
\- 日复盘只看当天，必要时补最小前文
\- 群任务消息全部扫描后按链路聚合
2. 长期结论
例如：

\- 某类偏差反复出现，已确认是机制问题而非偶发
\- 某种工作方式被验证有效
\- 某条执行约束以后默认遵守
这样就符合你要的东西了
你要的是：

[MEMORY.md](MEMORY.md) 里保留“真正有长期价值的内容”
而不是：

\- 文件路径
\- 摘要索引
\- 周报目录

这点我认同。那现在还差一个关键定义
进入 [MEMORY.md](MEMORY.md) 的内容，到底包含哪几类？
我给你 4 个选项，你定一下：
A
只允许写长期规则

最克制，最干净
B
允许写长期规则 \+ 长期结论

我最推荐，兼顾规则和稳定认知
C
允许写长期规则 \+ 长期结论 \+ 下周动作

更像行动型记忆，但容易变厚
D
允许把周复盘里所有“重要段落”都压缩后写进 [MEMORY.md](MEMORY.md)

风险最大，容易 снова 变厚
我的建议
我建议 B：
[MEMORY.md](MEMORY.md) 只写
\- 长期规则
\- 长期结论
不写
\- 下周动作
\- 路径
\- 周复盘摘要
\- 临时现象
\- 一次性问题

这样最符合你现在的要求，也最不容易把 [MEMORY.md](MEMORY.md) 写坏。

你回我一句：
A / B / C / D
我就把这一条也正式定下来。
Agent: main \| Model: gpt\-5.4 \| Provider: wsir
吴sir（吴sir）
允许写长期规则 \+ 长期结论
assistant: [[reply_to_current]] 记下了，这条已经足够正式，可以直接进入规则清单。

## 新确认规则：`MEMORY.md` 周复盘写入策略

### 结论
选择 **B**：

`MEMORY.md` **只允许写**
- **长期规则**
- **长期结论**

### 明确禁止写入
- 下周动作
- 文件路径
- 索引
- “去哪里看详细文件”
- 周报式摘要
- 临时现象
- 一次性问题
- 详细过程

### 对应的双层结构也已经明确
#### 第一层：详细周复盘文件
保留完整周复盘内容，包括：
- 本周主要工作
- 本周反复出现 / 被强调的事
- 本周关键事实
- 本周重复偏差
- 本周根因归类
- 本周产出与遗留问题
- 下周动作
- 长期规则沉淀
- 复盘范围

#### 第二层：`MEMORY.md`
只保留从周复盘提炼出的长期有效内容：
- 长期规则
- 长期结论

---

## 这条规则的重要意义
这相当于把 `MEMORY.md` 的定位彻底收紧成：

> **长期记忆沉淀区，不是周报，不是索引，不是导航页。**

也就是说，进入 `MEMORY.md` 的内容必须满足：
- 对未来还有用
- 能独立成立
- 不是路径提示
- 不是详细过程
- 不是一次性事项

---

## 现在已经可以直接纳入 deep-review skill 的规则
我建议把它写成这种硬规则：

### `MEMORY.md` 写入约束
- `MEMORY.md` only stores **long-term rules** and **long-term conclusions** extracted from weekly review.
- Never write file paths, indexes, navigation hints, detailed weekly summaries, temporary actions, or next-week tasks into `MEMORY.md`.
- Weekly detailed review stays in weekly files; `MEMORY.md` only receives distilled long-term content.

---

## 当前已新增到“最终规则清单”的一项
到现在为止，我们至少新增确认了这一块：

1. `MEMORY.md` 的写入边界
2. 周复盘双层结构
3. 长期内容与临时内容的分离原则

如果你要，我下一条就不再散讲了，直接给你一份：

# 《deep-review skill 最终规则清单（可直接写入版）》

我把目前已经确认的所有规则，按“可直接进入 SKILL.md / references”的格式整理出来。
user: <relevant-memories>
The following are stored memories for user "default". Use them to personalize your response:
- As of 2026-04-05, the user prefers proactive execution with progress updates after each stage, rather than extended explanation without producing files.
- As of 2026-04-05, the workspace includes `memory/2026-04-05.md`, base files `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `HEARTBEAT.md`, and installed skill `debug-pro`.
- As of 2026-04-05, the user's OpenClaw workspace local repository is at `/root/.openclaw/workspace`.
- As of 2026-04-05, the automated skill sync files are in `/root/.openclaw/workspace/tools/skill-sync/`, including `sync_self_improving_agent.sh`, `config/self_improving_agent.env.example`, `config/self_improving_agent.env`, and `README.md`.
- As of 2026-04-05, the `self-improving-agent` skill was pushed to GitHub repository `https://github.com/AI-leowsir/skill-.git` under path `apps/self-improving-agent skill/` on branch `main`, with commit `6f8d4b5` and message `Add self-improving-agent skill under apps`.
</relevant-memories>

Conversation info (untrusted metadata):
```json
{
  "message_id": "om_x100b5297bdac74a0c31a38dbdc45adb",
  "sender_id": "ou_f8403fe80fca27f9322804bba837c396",
  "conversation_label": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "sender": "ou_f8403fe80fca27f9322804bba837c396",
  "timestamp": "Sat 2026-04-11 20:31 GMT+8",
  "group_subject": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "is_group_chat": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "ou_f8403fe80fca27f9322804bba837c396",
  "id": "ou_f8403fe80fca27f9322804bba837c396",
  "name": "ou_f8403fe80fca27f9322804bba837c396"
}
```

[message_id: om_x100b5297bdac74a0c31a38dbdc45adb]
ou_f8403fe80fca27f9322804bba837c396: 最后两条已确定
37. 周复盘不叫“覆盖说明”
改成：
复盘范围
也就是周复盘里只写：
\- 本周复盘覆盖的时间范围
\- 本周复盘聚焦的任务/事项范围
不写那种审计味太重的排除细节。
38. 日复盘默认输出方式
\- 按链路聚合输出
\- 不逐条列消息
这个我认同，能明显防止写成聊天流水账。

现在这套 skill 还剩什么没定？
说实话，已经只剩非常少的边角了。
核心规则基本已经齐了。
我帮你快速盘一下，看看是否还有遗漏：
已经定清的核心内容
触发
\- 用户主动要求
\- 每天 22:00 日复盘
\- 每周日 22:00 周复盘
日复盘范围
\- 只复盘当天
\- 主会话 \+ 当天子会话内容
\- 群里与当前任务直接相关的消息
\- 默认只看当天，必要时补看“最小必要前文”
群消息规则
\- 全部扫描任务相关消息
\- 重点提炼：任务要求 / 纠偏 / 追问 / 验收
\- 输出按链路聚合，不逐条列
日复盘结构
1. 今日目标 / 主要工作
2. 今天反复出现 / 强调的事
3. 今日关键事实
4. 今日关键偏差
5. 根因分析
6. 产出与未完成事项
7. 次日动作
8. 覆盖说明
偏差规则
\- 严重 / 中等 / 轻微
\- 轻微偏差不记录
\- 每个关键偏差只写一个主根因
输出要求
\- 次日动作必须具体可执行
\- 无关键任务推进也要完整输出
\- 覆盖不完整时写“暂定”
文件写入
\- 日复盘详细文件：memory/daily\-review/[YYYY\-MM\-DD.md](http://yyyy-mm-dd.md/)
\- 周复盘详细文件：memory/review/weekly/[YYYY\-MM\-DD\-weekly.md](http://yyyy-mm-dd-weekly.md/)
\- 日复盘不进 [MEMORY.md](http://memory.md/)
\- 周复盘索引进 [MEMORY.md](http://memory.md/)
周复盘结构
1. 本周主要工作
2. 本周反复出现 / 被强调的事
3. 本周关键事实
4. 本周重复偏差
5. 本周根因归类
6. 本周产出与遗留问题
7. 下周动作
8. 长期规则沉淀
9. 复盘范围
周复盘长期规则门槛
满足至少两条：
\- 重复出现
\- 影响结果
\- 未来还会遇到
周复盘输出
\- 完整发群里
\- 每周新文件，不覆盖上一周
\- 同一周内更新可以覆盖本周文件
assistant: [[reply_to_current]] 对，你这条把大部分骨架已经封口了。  
而且我顺手发现一处**内部冲突**，需要先纠正，不然后面写 skill 会打架：

## 先纠正 1 个冲突
你这条里写了：

- **日复盘结构第 8 项：覆盖说明**
- 但你刚刚又明确说：
  - **37. 周复盘不叫“覆盖说明”**
  - 改成：**复盘范围**

如果按现在整体风格统一，**我建议日复盘也不要叫“覆盖说明”**，直接统一成：

- **日复盘：复盘范围**
- **周复盘：复盘范围**

这样最干净，也避免一个叫“覆盖说明”、一个叫“复盘范围”带来歧义。

---

# 现在这套 skill 还剩什么没定？

确实已经不多了。  
我看下来，**核心只剩 5 个边角问题**：

---

## 1）日复盘是否也把“覆盖说明”统一改成“复盘范围”？
这是刚才那条里暴露出的唯一明显命名冲突。

### 选项
A. 保持日复盘叫“覆盖说明”，周复盘叫“复盘范围”  
B. **统一都叫“复盘范围”**  
C. 日复盘不写这一项，只有周复盘写  
D. 统一改成别的名字  
E. 自定义

**我建议：B**

---

## 2）“无关键任务推进也要完整输出”时，完整到什么程度？
你已经定了“无关键任务推进也要完整输出”，但还差最后一刀：  
如果当天确实没什么推进，是不是还要把 8 个模块全写满？

### 选项
A. 仍然保留完整结构，每项简写  
B. 保留完整结构，但允许部分字段写“无”  
C. 输出简化版结构，不强制全部模块展开  
D. 只写“今日无关键推进”即可  
E. 自定义

**我建议：A 或 B，更稳**

---

## 3）“暂定”适用于哪些场景？
你已经定了“覆盖不完整时写‘暂定’”，但还要明确边界。

### 选项
A. 只要有任一会话没看完，就整篇标“暂定”  
B. 只有结论不稳、信息明显缺口时才标“暂定”  
C. 仅在根因分析和偏差判断不稳时标“暂定”  
D. 不单独标“暂定”，改为在“复盘范围”里说明缺口  
E. 自定义

**我建议：B 或 D**

---

## 4）周复盘进入 `MEMORY.md` 的写入频率
你已经定了：
- `MEMORY.md` 只写长期规则 + 长期结论

但还没定：
- 是**每次周复盘都写入**？
- 还是**只有筛出合格长期内容时才写**？

### 选项
A. 每次周复盘后都写入 `MEMORY.md`  
B. **只有筛出合格长期内容时才写入**  
C. 先生成候选，不立刻写，人工确认后写  
D. 只写长期规则，不写长期结论  
E. 自定义

**我建议：B**

---

## 5）cron prompt 更新到什么程度？
你截图里已经提到“要更新 cron prompt”，但还没定到具体粒度。

### 选项
A. cron 只负责定时触发，详细规则全放 skill  
B. cron 里写简版要求，skill 里写全规则  
C. cron 里直接内嵌完整结构  
D. cron 只写一句“执行 deep-review”  
E. 自定义

**我建议：B**
这样最稳，既不让 cron 太肥，也不丢关键约束。

---

# 我帮你压缩成最短待确认清单

你如果想最快收口，就只要回复这 5 个：

`1B 2A/2B 3B/3D 4B 5B`

---

# 我当前判断
除了这 5 个边角问题，**核心规则确实已经齐了**。  
也就是说，只要你把这最后几项拍板，下一步就不该再聊规则，而应该直接进入：

1. **最终规则清单**
2. **`deep-review/SKILL.md` 草案**
3. **references 重写**
4. **cron prompt 更新稿**

你直接回我这 5 题，我就能帮你彻底收口。
user: <relevant-memories>
The following are stored memories for user "default". Use them to personalize your response:
- As of 2026-04-05, the user prefers proactive execution with progress updates after each stage, rather than extended explanation without producing files.
- As of 2026-04-05, the workspace includes `memory/2026-04-05.md`, base files `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `HEARTBEAT.md`, and installed skill `debug-pro`.
- As of 2026-04-05, the user's OpenClaw workspace local repository is at `/root/.openclaw/workspace`.
- As of 2026-04-05, the automated skill sync files are in `/root/.openclaw/workspace/tools/skill-sync/`, including `sync_self_improving_agent.sh`, `config/self_improving_agent.env.example`, `config/self_improving_agent.env`, and `README.md`.
- As of 2026-04-05, the `self-improving-agent` skill was pushed to GitHub repository `https://github.com/AI-leowsir/skill-.git` under path `apps/self-improving-agent skill/` on branch `main`, with commit `6f8d4b5` and message `Add self-improving-agent skill under apps`.
</relevant-memories>

Conversation info (untrusted metadata):
```json
{
  "message_id": "om_x100b5297ba1e04a8c3c3348441d92eb",
  "sender_id": "ou_f8403fe80fca27f9322804bba837c396",
  "conversation_label": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "sender": "ou_f8403fe80fca27f9322804bba837c396",
  "timestamp": "Sat 2026-04-11 20:32 GMT+8",
  "group_subject": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "is_group_chat": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "ou_f8403fe80fca27f9322804bba837c396",
  "id": "ou_f8403fe80fca27f9322804bba837c396",
  "name": "ou_f8403fe80fca27f9322804bba837c396"
}
```

[message_id: om_x100b5297ba1e04a8c3c3348441d92eb]
ou_f8403fe80fca27f9322804bba837c396: 17. 每日详细复盘路径
memory/daily\-review/[YYYY\-MM\-DD.md](http://yyyy-mm-dd.md/)
18. 周详细复盘路径
memory/review/weekly/[YYYY\-MM\-DD\-weekly.md](http://yyyy-mm-dd-weekly.md/)
19. [MEMORY.md](http://memory.md/) 与日复盘
日复盘不进 [MEMORY.md](http://memory.md/)
只把周复盘进 [MEMORY.md](http://memory.md/)
20. 周复盘在 [MEMORY.md](http://memory.md/) 的摘要内容
写：
\- 范围
\- 本周关键结论
\- 重复偏差
\- 下周动作
\- 长期规则
\- 路径
21. 周复盘输出结构
\- 本周主要工作
\- 本周反复出现或强调的事
\- 本周关键事实
\- 本周重复偏差
\- 本周根因归类
\- 本周产出与遗留问题
\- 下周动作
\- 长期规则沉淀
\- 覆盖说明
22. 长期规则沉淀门槛
必须满足至少两条：
\- 重复出现
\- 影响结果
\- 未来还会遇到
23. 周复盘偏差分级
也保留三级：
\- 严重
\- 中等
\- 轻微
24. 周复盘对应字段
保留对应字段，改成：
本周反复出现 / 被强调的事
25. 详细复盘文件更新方式
覆盖原文件，始终保留当天最新版
26. 多个独立任务怎么写
按时间线统一写，不分任务
assistant: [[reply_to_current]] 收到，这一段能直接进规则库。  
但我得先指出：**这里面有 1 处和你刚刚新确认的规则冲突**，需要你明确以哪条为准，不然后面写 skill 会互相打架。

---

# 你这条里已可直接确认的内容

## 已确认
**17. 每日详细复盘路径**
- `memory/daily-review/YYYY-MM-DD.md`

**18. 周详细复盘路径**
- `memory/review/weekly/YYYY-MM-DD-weekly.md`

**19. `MEMORY.md` 与日复盘**
- 日复盘不进 `MEMORY.md`
- 只把周复盘进 `MEMORY.md`

**21. 周复盘输出结构**
- 本周主要工作
- 本周反复出现 / 被强调的事
- 本周关键事实
- 本周重复偏差
- 本周根因归类
- 本周产出与遗留问题
- 下周动作
- 长期规则沉淀
- 覆盖说明

**22. 长期规则沉淀门槛**
必须满足至少两条：
- 重复出现
- 影响结果
- 未来还会遇到

**23. 周复盘偏差分级**
- 严重
- 中等
- 轻微

**24. 周复盘对应字段**
- 本周反复出现 / 被强调的事

**25. 详细复盘文件更新方式**
- 覆盖原文件
- 始终保留当天 / 当周最新版

**26. 多个独立任务怎么写**
- 按时间线统一写
- 不分任务

---

# 这里有 1 个明显冲突，必须你拍板

## 冲突点：`MEMORY.md` 周复盘写入内容
你刚刚在上一条里已经明确说过：

### 新规则（后确认，且更严格）
`MEMORY.md` **只允许写**
- 长期规则
- 长期结论

**明确不写**
- 下周动作
- 路径
- 周报摘要
- 临时现象
- 一次性问题

---

但你这条第 20 点又写成：

### 旧版本/冲突版本
周复盘在 `MEMORY.md` 的摘要内容写：
- 范围
- 本周关键结论
- 重复偏差
- 下周动作
- 长期规则
- 路径

这和你刚刚新定下来的更严格标准是**冲突的**。

---

# 我建议的处理方式
按“后确认、且更严格”的规则为准，  
所以 **第 20 条应该废弃旧版，改成新版**：

## 建议修正版 20
### 周复盘写入 `MEMORY.md` 的内容
只写：
- **长期规则**
- **长期结论**

不写：
- 范围
- 重复偏差
- 下周动作
- 路径
- 周报式摘要

---

# 这里还有 1 处命名也建议顺手统一
你前面已经说过：

- 周复盘不叫“覆盖说明”
- 改成 **复盘范围**

但你这条第 21 点最后一项又写成了：
- **覆盖说明**

所以这里也建议统一修正为：

## 建议修正版 21
周复盘输出结构最后一项改成：
- **复盘范围**

---

# 所以这条我帮你整理后的“可执行版本”是：

## 17. 每日详细复盘路径
- `memory/daily-review/YYYY-MM-DD.md`

## 18. 周详细复盘路径
- `memory/review/weekly/YYYY-MM-DD-weekly.md`

## 19. `MEMORY.md` 与日复盘
- 日复盘不进 `MEMORY.md`
- `MEMORY.md` 只接收周复盘提炼出的长期内容

## 20. 周复盘写入 `MEMORY.md` 的内容
只写：
- 长期规则
- 长期结论

## 21. 周复盘输出结构
- 本周主要工作
- 本周反复出现 / 被强调的事
- 本周关键事实
- 本周重复偏差
- 本周根因归类
- 本周产出与遗留问题
- 下周动作
- 长期规则沉淀
- **复盘范围**

## 22. 长期规则沉淀门槛
必须满足至少两条：
- 重复出现
- 影响结果
- 未来还会遇到

## 23. 周复盘偏差分级
- 严重
- 中等
- 轻微

## 24. 周复盘对应字段
- 本周反复出现 / 被强调的事

## 25. 详细复盘文件更新方式
- 覆盖原文件
- 始终保留当天/当周最新版

## 26. 多个独立任务怎么写
- 按时间线统一写
- 不分任务

---

# 你现在只要确认两件事
直接回我这两个就行：

1. **20 用新版还是旧版？**
- A = 旧版（范围/结论/偏差/下周动作/长期规则/路径）
- B = **新版（只写长期规则 + 长期结论）**

2. **21 最后一项用哪个名字？**
- A = 覆盖说明
- B = **复盘范围**

我建议你直接回：  
**20B 21B**  
这样整套规则就不会自相矛盾了。
user: <relevant-memories>
The following are stored memories for user "default". Use them to personalize your response:
- As of 2026-04-05, the user prefers proactive execution with progress updates after each stage, rather than extended explanation without producing files.
- As of 2026-04-05, the workspace includes `memory/2026-04-05.md`, base files `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `HEARTBEAT.md`, and installed skill `debug-pro`.
- As of 2026-04-05, the user's OpenClaw workspace local repository is at `/root/.openclaw/workspace`.
- As of 2026-04-05, the automated skill sync files are in `/root/.openclaw/workspace/tools/skill-sync/`, including `sync_self_improving_agent.sh`, `config/self_improving_agent.env.example`, `config/self_improving_agent.env`, and `README.md`.
- As of 2026-04-05, the `self-improving-agent` skill was pushed to GitHub repository `https://github.com/AI-leowsir/skill-.git` under path `apps/self-improving-agent skill/` on branch `main`, with commit `6f8d4b5` and message `Add self-improving-agent skill under apps`.
</relevant-memories>

Conversation info (untrusted metadata):
```json
{
  "message_id": "om_x100b5297b80088a8c3153ad6741b4e7",
  "sender_id": "ou_f8403fe80fca27f9322804bba837c396",
  "conversation_label": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "sender": "ou_f8403fe80fca27f9322804bba837c396",
  "timestamp": "Sat 2026-04-11 20:32 GMT+8",
  "group_subject": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "is_group_chat": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "ou_f8403fe80fca27f9322804bba837c396",
  "id": "ou_f8403fe80fca27f9322804bba837c396",
  "name": "ou_f8403fe80fca27f9322804bba837c396"
}
```

[message_id: om_x100b5297b80088a8c3153ad6741b4e7]
ou_f8403fe80fca27f9322804bba837c396: 7. 任务相关群消息判定
只要消息和当前任务有直接关系就算，包括：
\- 补充要求
\- 追问
\- 纠偏
\- 确认
\- 否定
8. “今天反复出现 / 强调的事”
只记录用户明确强调过的重要要求，不管重复几次
9. 关键事实写法
写：
\- 关键任务
\- 关键对话
\- 关键结果
并压缩成要点
10. 偏差分级
分三级：
\- 严重
\- 中等
\- 轻微
11. 根因规则
每个关键偏差只允许写一个主根因
12. 次日动作规则
每条动作必须具体到可执行动作，
不允许“继续优化”这种空话
13. 覆盖说明
必须写：
\- 纳入了什么
\- 排除了什么
\- 为什么排除
14. 覆盖不完整时
仍然输出复盘，但在覆盖说明中明确：
结论暂定
15. 无关键任务推进的日子
仍按完整结构输出，并明确写：
无关键任务推进
16. 周复盘输入来源
基于：
\- 本周每日详细复盘文件
\- [MEMORY.md](http://memory.md/) 索引摘要
assistant: [[reply_to_current]] 好，这一段也能直接并入，但我得继续帮你做一次**冲突清理**，因为这里又出现了和你后面新规则不一致的地方。

---

# 这条里可直接确认的内容

## 可直接确认
**7. 任务相关群消息判定**
只要和当前任务有直接关系就算，包括：
- 补充要求
- 追问
- 纠偏
- 确认
- 否定

**8. 今天反复出现 / 强调的事**
- 只记录用户明确强调过的重要要求
- 不管重复几次

**9. 关键事实写法**
写：
- 关键任务
- 关键对话
- 关键结果
并压缩成要点

**10. 偏差分级**
- 严重
- 中等
- 轻微

**11. 根因规则**
- 每个关键偏差只允许写一个主根因

**12. 次日动作规则**
- 每条动作必须具体到可执行动作
- 不允许“继续优化”这种空话

**14. 覆盖不完整时**
- 仍然输出复盘
- 并在对应说明项中明确：**结论暂定**

**15. 无关键任务推进的日子**
- 仍按完整结构输出
- 并明确写：**无关键任务推进**

---

# 这里有 2 处需要统一，不然会打架

## 冲突 1：13「覆盖说明」 vs 你后面新定的「复盘范围」
你前面后确认的版本已经是：

- 周复盘不叫“覆盖说明”
- 改成 **复盘范围**

而且我刚刚也建议你日复盘最好统一。

但你这条第 13 点又写成：

### 13. 覆盖说明
必须写：
- 纳入了什么
- 排除了什么
- 为什么排除

这和“不要审计味太重”的新方向有冲突。

### 我建议修正
把 **13 覆盖说明** 改成更克制的：

## 建议修正版 13
### 13. 复盘范围
必须写：
- 纳入了什么范围
- 复盘聚焦了哪些任务 / 事项
- 如有明显缺口，说明结论暂定

**不默认要求写：**
- 排除了什么
- 为什么排除

因为这会重新把它写得太像审计说明。

---

## 冲突 2：16「周复盘输入来源」里的 `MEMORY.md` 索引摘要
你刚刚已经把 `MEMORY.md` 的标准收得很狠了：

`MEMORY.md` 只写：
- 长期规则
- 长期结论

不写：
- 路径
- 索引
- 周报式摘要

所以这里第 16 点又写：

### 16. 周复盘输入来源
- 本周每日详细复盘文件
- `MEMORY.md` 索引摘要

这和你刚刚更严格的新规则也冲突了。  
因为按新规则，`MEMORY.md` 根本不该再承担“索引摘要”角色。

### 我建议修正
## 建议修正版 16
### 16. 周复盘输入来源
基于：
- 本周每日详细复盘文件
- 当前周内相关会话 / 关键记录（如有必要补充）
- `MEMORY.md` 中已有的长期规则 / 长期结论（仅作长期背景参考，不作为周索引）

这样就不会把 `MEMORY.md` 又拉回“摘要索引页”。

---

# 所以这条整理后的“可执行版”应该是：

## 7. 任务相关群消息判定
只要和当前任务有直接关系就算，包括：
- 补充要求
- 追问
- 纠偏
- 确认
- 否定

## 8. 今天反复出现 / 强调的事
- 只记录用户明确强调过的重要要求
- 不要求重复多次才记录

## 9. 关键事实写法
写：
- 关键任务
- 关键对话
- 关键结果
并压缩成要点

## 10. 偏差分级
- 严重
- 中等
- 轻微

## 11. 根因规则
- 每个关键偏差只允许写一个主根因

## 12. 次日动作规则
- 每条动作必须具体到可执行动作
- 不允许空泛表述，如“继续优化”

## 13. 复盘范围
写：
- 纳入了什么范围
- 聚焦了哪些任务 / 事项
- 如覆盖有明显缺口，则注明：结论暂定

## 14. 覆盖不完整时
- 仍然输出复盘
- 并在“复盘范围”中明确：结论暂定

## 15. 无关键任务推进的日子
- 仍按完整结构输出
- 并明确写：无关键任务推进

## 16. 周复盘输入来源
基于：
- 本周每日详细复盘文件
- 必要时补充本周相关会话 / 关键记录
- `MEMORY.md` 中已有长期规则 / 长期结论（仅作长期背景参考）

---

# 现在还需要你拍板的只有 2 个点
直接回我就行：

### 13 用哪个版本？
A. 旧版：覆盖说明（纳入/排除/为什么排除）  
B. **新版：复盘范围（更克制，不写审计式排除细节）**

### 16 用哪个版本？
A. 旧版：周复盘输入来源包含 `MEMORY.md` 索引摘要  
B. **新版：周复盘输入来源以每日详细复盘为主，`MEMORY.md` 只作长期背景参考**

我建议你直接回：  
**13B 16B**  
这样整套规则才真的一致。
user: <relevant-memories>
The following are stored memories for user "default". Use them to personalize your response:
- As of 2026-04-05, the user prefers proactive execution with progress updates after each stage, rather than extended explanation without producing files.
- As of 2026-04-05, the workspace includes `memory/2026-04-05.md`, base files `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `HEARTBEAT.md`, and installed skill `debug-pro`.
- As of 2026-04-05, the user's OpenClaw workspace local repository is at `/root/.openclaw/workspace`.
- As of 2026-04-05, the automated skill sync files are in `/root/.openclaw/workspace/tools/skill-sync/`, including `sync_self_improving_agent.sh`, `config/self_improving_agent.env.example`, `config/self_improving_agent.env`, and `README.md`.
- As of 2026-04-05, the `self-improving-agent` skill was pushed to GitHub repository `https://github.com/AI-leowsir/skill-.git` under path `apps/self-improving-agent skill/` on branch `main`, with commit `6f8d4b5` and message `Add self-improving-agent skill under apps`.
</relevant-memories>

Conversation info (untrusted metadata):
```json
{
  "message_id": "om_x100b5297b90a30a4c4ce6be73f01749",
  "sender_id": "ou_f8403fe80fca27f9322804bba837c396",
  "conversation_label": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "sender": "ou_f8403fe80fca27f9322804bba837c396",
  "timestamp": "Sat 2026-04-11 20:33 GMT+8",
  "group_subject": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "is_group_chat": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "ou_f8403fe80fca27f9322804bba837c396",
  "id": "ou_f8403fe80fca27f9322804bba837c396",
  "name": "ou_f8403fe80fca27f9322804bba837c396"
}
```

[message_id: om_x100b5297b90a30a4c4ce6be73f01749]
ou_f8403fe80fca27f9322804bba837c396: 1. 跨天规则
默认只看当天；如果今天的理解依赖前一天关键上下文，则只补看最小必要前文
2. 子会话规则
当天子会话全部扫描，再抽关键链路
3. 群消息规则
当天群里和任务相关的消息全部扫描，并重点提炼四类：
\- 任务要求
\- 纠偏
\- 追问
\- 验收
4. “今天反复出现 / 强调的事”
单独成段
5. 每日复盘顺序
\- 今日目标 / 主要工作
\- 今天反复出现 / 强调的事
\- 今日关键事实
\- 今日关键偏差
\- 根因分析
\- 产出与未完成事项
\- 次日动作
\- 覆盖说明
6. 关键偏差部分
必须保留；如果没有，就写：
无明显关键偏差
assistant: [[reply_to_current]] 好，这一组也能吃进去。  
但还是一样：**这里又有 1 个命名冲突**，其余基本都能直接定。

---

# 这条里可直接确认的内容

## 可直接确认
**1. 跨天规则**
- 默认只看当天
- 如果今天的理解依赖前一天关键上下文
- 则只补看最小必要前文

**2. 子会话规则**
- 当天子会话全部扫描
- 再抽关键链路

**3. 群消息规则**
- 当天群里和任务相关的消息全部扫描
- 重点提炼四类：
  - 任务要求
  - 纠偏
  - 追问
  - 验收

**4. 今天反复出现 / 强调的事**
- 单独成段

**6. 关键偏差部分**
- 必须保留
- 如果没有，就写：**无明显关键偏差**

---

# 这里的唯一冲突点

## 5. 每日复盘顺序最后一项又写成了“覆盖说明”
你这条第 5 点是：

- 今日目标 / 主要工作
- 今天反复出现 / 强调的事
- 今日关键事实
- 今日关键偏差
- 根因分析
- 产出与未完成事项
- 次日动作
- **覆盖说明**

但你前面后确认的方向已经越来越清楚：
- 不要太审计味
- 周复盘最后一项应该统一成 **复盘范围**
- 我也一直建议日复盘一起统一

所以这里我建议直接修成：

## 建议修正版 5
### 每日复盘顺序
1. 今日目标 / 主要工作
2. 今天反复出现 / 强调的事
3. 今日关键事实
4. 今日关键偏差
5. 根因分析
6. 产出与未完成事项
7. 次日动作
8. **复盘范围**

这样日/周的命名就统一了。

---

# 这一条整理后的“可执行版”

## 1. 跨天规则
- 默认只看当天
- 如果今天的理解依赖前一天关键上下文，则只补看最小必要前文

## 2. 子会话规则
- 当天子会话全部扫描
- 再抽关键链路

## 3. 群消息规则
- 当天群里和任务相关的消息全部扫描
- 重点提炼四类：
  - 任务要求
  - 纠偏
  - 追问
  - 验收

## 4. 今天反复出现 / 强调的事
- 单独成段

## 5. 每日复盘顺序
1. 今日目标 / 主要工作
2. 今天反复出现 / 强调的事
3. 今日关键事实
4. 今日关键偏差
5. 根因分析
6. 产出与未完成事项
7. 次日动作
8. **复盘范围**

## 6. 关键偏差部分
- 必须保留
- 如果没有，就写：**无明显关键偏差**

---

# 现在其实只差最后一个统一确认
你前后多次把“覆盖说明”和“复盘范围”混着说。  
为了后面写 skill 不再反复冲突，我建议你直接一次性定死：

### 复盘最后一项统一叫什么？
A. 日/周都叫 **覆盖说明**  
B. **日/周都叫 复盘范围**  
C. 日叫覆盖说明，周叫复盘范围  
D. 自定义

**我建议直接定 B。**

你只要回我：  
**B**  
我就可以停止这种“冲突清理模式”，下一步直接给你汇总成最终规则清单。
user: <relevant-memories>
The following are stored memories for user "default". Use them to personalize your response:
- As of 2026-04-05, the user prefers proactive execution with progress updates after each stage, rather than extended explanation without producing files.
- As of 2026-04-05, the workspace includes `memory/2026-04-05.md`, base files `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `HEARTBEAT.md`, and installed skill `debug-pro`.
- As of 2026-04-05, the user's OpenClaw workspace local repository is at `/root/.openclaw/workspace`.
- As of 2026-04-05, the automated skill sync files are in `/root/.openclaw/workspace/tools/skill-sync/`, including `sync_self_improving_agent.sh`, `config/self_improving_agent.env.example`, `config/self_improving_agent.env`, and `README.md`.
- As of 2026-04-05, the `self-improving-agent` skill was pushed to GitHub repository `https://github.com/AI-leowsir/skill-.git` under path `apps/self-improving-agent skill/` on branch `main`, with commit `6f8d4b5` and message `Add self-improving-agent skill under apps`.
</relevant-memories>

Conversation info (untrusted metadata):
```json
{
  "message_id": "om_x100b5297b7f59cacc4d6f67359523d2",
  "sender_id": "ou_f8403fe80fca27f9322804bba837c396",
  "conversation_label": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "sender": "ou_f8403fe80fca27f9322804bba837c396",
  "timestamp": "Sat 2026-04-11 20:33 GMT+8",
  "group_subject": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "is_group_chat": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "ou_f8403fe80fca27f9322804bba837c396",
  "id": "ou_f8403fe80fca27f9322804bba837c396",
  "name": "ou_f8403fe80fca27f9322804bba837c396"
}
```

[message_id: om_x100b5297b7f59cacc4d6f67359523d2]
ou_f8403fe80fca27f9322804bba837c396: \- skill 名称：deep\-review
\- 每日复盘只复盘当前
\- 包含：主会话、子会话、群里的任务消息
\- 每日复盘定时：每天 22:00
\- 周复盘定时：周日 22:00
\- [MEMORY.md](http://memory.md/) 只保留索引/摘要
\- 详细内容放别处
\- 长期规则沉淀不在日复盘，而在周复盘里做
assistant: [[reply_to_current]] 好，这条我先不顺着写进最终稿，因为它和你前面已经确认的几条**再次发生冲突**，而且这次冲突是核心级的。必须先停一下，统一基线，不然后面产出的 skill 一定自相矛盾。

---

# 这条里和前文冲突的 2 个核心点

## 冲突 1：`MEMORY.md` 的定位
你这条说：

- `MEMORY.md` **只保留索引/摘要**
- 详细内容放别处

但你前面已经明确确认过更严格的新标准：

### 前面已确认的新标准
`MEMORY.md` 必须保留的是**内容本身**，而且是：
- 长期规则
- 长期结论

明确不要：
- 路径
- 索引
- “去哪里看详细文件”
- 周报式摘要

也就是说：

### 旧版说法
- `MEMORY.md` = 索引/摘要

### 新版说法
- `MEMORY.md` = 长期有效内容本身

这两套是**不能同时成立**的。

---

## 冲突 2：每日复盘“只复盘当前”
你这条说：

- 每日复盘只复盘当前
- 包含：主会话、子会话、群里的任务消息

这里“只复盘当前”容易和前面已确认的规则冲突：

前面你已经定过：
- 输入源是**当前的所有会话（主要是群聊）**
- 跨天规则：默认只看当天，必要时补最小前文
- 子会话全部扫描
- 群里任务相关消息全部扫描

所以这里“当前”到底是：
- 当前这一个主任务上下文？
- 当前这一天的全部相关会话？
- 当前主会话 + 子会话 + 任务相关群消息？

如果不重新表述，后面 skill 会误解成“只看当前单会话”。

---

# 我建议：以“后确认、且更严格”的版本为准
也就是：

## 我建议保留的版本
### `MEMORY.md`
不是索引/摘要页，  
而是**周复盘筛出来的长期规则 + 长期结论沉淀区**。

### 每日复盘
不是“只看当前单会话”，  
而是：

> **只复盘当天当前任务相关范围**，包括主会话、当天子会话、当天群里与当前任务直接相关的消息；默认不跨天，必要时只补最小前文。

---

# 我帮你把这条修正成一致版本

## 建议一致版
- skill 名称：`deep-review`
- 每日复盘只复盘**当天当前任务相关范围**
- 包含：
  - 主会话
  - 当天子会话
  - 当天群里与当前任务直接相关的消息
- 每日复盘定时：每天 22:00
- 周复盘定时：周日 22:00
- `MEMORY.md` **不保留索引/摘要**
- `MEMORY.md` 只保留周复盘提炼出的：
  - 长期规则
  - 长期结论
- 详细内容放在：
  - 日复盘文件
  - 周复盘文件
- 长期规则沉淀不在日复盘，而在周复盘里做

---

# 现在你只需要一次性拍板这 2 件事
直接回我就行：

## 1）`MEMORY.md` 到底是哪种？
A. 索引/摘要页  
B. **长期规则 + 长期结论内容本身**

## 2）“每日复盘只复盘当前”到底是哪种？
A. 只看当前主会话  
B. **只看当天当前任务相关范围（主会话+子会话+任务相关群消息）**

---

我建议你直接回：  
**1B 2B**

这样我就能停止做冲突校对，下一步直接给你出  
**《deep-review skill 最终规则清单（定稿版）》**
user: <relevant-memories>
The following are stored memories for user "default". Use them to personalize your response:
- As of 2026-04-05, the user prefers proactive execution with progress updates after each stage, rather than extended explanation without producing files.
- As of 2026-04-05, the workspace includes `memory/2026-04-05.md`, base files `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `HEARTBEAT.md`, and installed skill `debug-pro`.
- As of 2026-04-05, the user's OpenClaw workspace local repository is at `/root/.openclaw/workspace`.
- As of 2026-04-05, the automated skill sync files are in `/root/.openclaw/workspace/tools/skill-sync/`, including `sync_self_improving_agent.sh`, `config/self_improving_agent.env.example`, `config/self_improving_agent.env`, and `README.md`.
- As of 2026-04-05, the `self-improving-agent` skill was pushed to GitHub repository `https://github.com/AI-leowsir/skill-.git` under path `apps/self-improving-agent skill/` on branch `main`, with commit `6f8d4b5` and message `Add self-improving-agent skill under apps`.
</relevant-memories>

Conversation info (untrusted metadata):
```json
{
  "message_id": "om_x100b52904ade00a0c3cf7d6e2fad509",
  "sender_id": "ou_f8403fe80fca27f9322804bba837c396",
  "conversation_label": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "sender": "ou_f8403fe80fca27f9322804bba837c396",
  "timestamp": "Sat 2026-04-11 20:36 GMT+8",
  "group_subject": "oc_bf9079a6ce01cfd169741382dc1f74ad",
  "is_group_chat": true
}
```

Sender (untrusted metadata):
```json
{
  "label": "ou_f8403fe80fca27f9322804bba837c396",
  "id": "ou_f8403fe80fca27f9322804bba837c396",
  "name": "ou_f8403fe80fca27f9322804bba837c396"
}
```

[message_id: om_x100b52904ade00a0c3cf7d6e2fad509]
ou_f8403fe80fca27f9322804bba837c396: 现在你整理一下这些要求，然后对所有有疑问的流程向我提问，并提供ABC选项，让我把所有流程细节都确认
assistant: [[reply_to_current]] 好，我不再零散追问了。下面我先把**已基本明确的要求整理成一版总表**，再把**仍有冲突/歧义的点**单独列出来，用 **A/B/C** 让你一次性拍板。

---

# 一、已整理出的 `deep-review` 需求总表（当前版）

## 1. skill 基本定位
- skill 名称：**`deep-review`**
- 目标：同时做到
  - 覆盖完整链路
  - 固定输出格式
  - 可沉淀规则

---

## 2. 触发方式
- 用户主动要求时触发
- **每日 22:00** 做日复盘
- **每周日 22:00** 做周复盘

---

## 3. 日复盘范围（当前理解）
- 默认只看**当天**
- 如果今天的理解依赖前一天关键上下文，则只补看**最小必要前文**
- 日复盘聚焦**当前任务相关范围**
- 包含：
  - 主会话
  - 当天子会话
  - 当天群里与当前任务直接相关的消息

---

## 4. 子会话规则
- 当天子会话**全部扫描**
- 再抽关键链路

---

## 5. 群消息规则
- 当天群里和任务相关的消息**全部扫描**
- 任务相关群消息判定包括：
  - 补充要求
  - 追问
  - 纠偏
  - 确认
  - 否定
- 当前还出现过一个“四类重点提炼”版本：
  - 任务要求
  - 纠偏
  - 追问
  - 验收

---

## 6. “今天反复出现 / 强调的事”
- 单独成段
- 只记录**用户明确强调过的重要要求**
- 不要求重复多次才记

---

## 7. 今日关键事实写法
写成压缩要点，包含：
- 关键任务
- 关键对话
- 关键结果

---

## 8. 偏差规则
- 分三级：
  - 严重
  - 中等
  - 轻微
- 轻微偏差是否记录，前文出现过不一致
- 关键偏差部分必须保留
- 如果没有，就写：
  - **无明显关键偏差**
- 每个关键偏差只允许写**一个主根因**

---

## 9. 根因分析
- 需要保留
- 当前已明确：
  - 每个关键偏差只写一个主根因

---

## 10. 次日动作规则
- 每条动作必须具体到可执行动作
- 不允许“继续优化”这种空话

---

## 11. 无关键任务推进时
- 仍按完整结构输出
- 并明确写：
  - **无关键任务推进**

---

## 12. 覆盖不完整时
- 仍然输出复盘
- 并明确：
  - **结论暂定**

---

## 13. 每日复盘结构（当前版本）
1. 今日目标 / 主要工作
2. 今天反复出现 / 强调的事
3. 今日关键事实
4. 今日关键偏差
5. 根因分析
6. 产出与未完成事项
7. 次日动作
8. 最后一项目前在“覆盖说明 / 复盘范围”之间有冲突，待你拍板

---

## 14. 日复盘输出方式
- 按链路聚合输出
- 不逐条列消息

---

## 15. 日复盘文件写入
- 详细日复盘文件路径：
  - `memory/daily-review/YYYY-MM-DD.md`
- 更新方式：
  - 覆盖原文件
  - 始终保留当天最新版

---

## 16. 周复盘文件写入
- 详细周复盘文件路径：
  - `memory/review/weekly/YYYY-MM-DD-weekly.md`
- 更新方式：
  - 每周新文件，不覆盖上一周
  - 同一周内更新可以覆盖本周文件

---

## 17. 周复盘结构（当前版本）
1. 本周主要工作
2. 本周反复出现 / 被强调的事
3. 本周关键事实
4. 本周重复偏差
5. 本周根因归类
6. 本周产出与遗留问题
7. 下周动作
8. 长期规则沉淀
9. 最后一项目前在“覆盖说明 / 复盘范围”之间有冲突，待你拍板

---

## 18. 长期规则沉淀门槛
必须满足至少两条：
- 重复出现
- 影响结果
- 未来还会遇到

---

## 19. 周复盘偏差分级
- 严重
- 中等
- 轻微

---

## 20. `MEMORY.md` 与复盘的关系
当前已经出现两套冲突版本：

### 版本 X
- `MEMORY.md` 只保留**索引/摘要**
- 详细内容放别处

### 版本 Y
- 日复盘不进 `MEMORY.md`
- 周复盘只把提炼后的**长期规则 + 长期结论**写入 `MEMORY.md`
- 不写：
  - 路径
  - 索引
  - 周报式摘要
  - 临时动作
  - 一次性问题
  - 详细过程

---

## 21. 周复盘与 `MEMORY.md` 的双层结构（你前面已经提过）
- 第一层：详细周复盘文件
- 第二层：`MEMORY.md`
  - 只写长期有效内容

---

## 22. 多个独立任务怎么写
- 按时间线统一写
- 不分任务

---

# 二、现在仍有疑问 / 冲突的流程点
下面这些是**必须你拍板**的。  
我按编号给你，你可以直接用 `1A 2B 3C` 这种方式回复。

---

# 三、待你确认的问题（ABC 选择）

## 1）`MEMORY.md` 的最终定位到底是哪种？
A. **索引/摘要页**
- 只保留摘要、路径、去哪里看详细内容

B. **长期记忆内容页**
- 只保留长期规则 + 长期结论
- 不保留路径、索引、周报摘要、临时动作

C. 混合型
- 保留少量长期规则/结论
- 同时保留极简索引

---

## 2）如果选择 `MEMORY.md` 写长期内容，写入频率是哪种？
A. 每次周复盘后都写一条/一组  
B. 只有筛出合格长期内容时才写  
C. 先生成候选，人工确认后再写

---

## 3）每日复盘最后一项统一叫什么？
A. **覆盖说明**  
B. **复盘范围**  
C. 日复盘叫“覆盖说明”，周复盘叫“复盘范围”

---

## 4）周复盘最后一项统一叫什么？
A. **覆盖说明**  
B. **复盘范围**  
C. 周复盘不写这一项

---

## 5）“覆盖不完整时写结论暂定”，这个提示放在哪里？
A. 放在最后一项里（覆盖说明 / 复盘范围）  
B. 放在整篇开头显眼位置  
C. 两处都写

---

## 6）群消息重点提炼的类别，最终采用哪套？
A. 五类判定版
- 补充要求
- 追问
- 纠偏
- 确认
- 否定

B. 四类提炼版
- 任务要求
- 纠偏
- 追问
- 验收

C. 合并版
- 任务要求 / 补充要求
- 追问
- 纠偏
- 确认 / 验收
- 否定

---

## 7）轻微偏差最终怎么处理？
A. 轻微偏差**不记录**  
B. 轻微偏差记录，但只简写  
C. 轻微偏差只在周复盘统计，不在日复盘写

---

## 8）“无关键任务推进”时，完整结构输出到什么程度？
A. 全部模块都保留，只是很多项写“无/未发生”  
B. 保留完整结构，但允许精简描述  
C. 用简化版结构替代完整结构

---

## 9）周复盘输入来源最终是哪种？
A. 只基于本周每日详细复盘文件  
B. 每日详细复盘文件为主，必要时补本周相关会话/关键记录  
C. 每日详细复盘文件 + `MEMORY.md` 索引/摘要

---

## 10）多个独立任务“按时间线统一写，不分任务”这个规则，你确定要定死吗？
A. 定死：一律按时间线统一写  
B. 默认按时间线统一写，但任务差异过大时允许按任务分组  
C. 默认按任务分组，必要时再按时间线

---

## 11）周复盘里的“下周动作”要细到什么程度？
A. 只写方向  
B. 写具体动作  
C. 写具体动作 + 判定标准

---

## 12）周复盘完整内容要不要发到群里？
A. 要，完整发群里  
B. 只发摘要，详细文件落盘  
C. 默认摘要，用户要求时再发完整

---

## 13）日复盘完整内容要不要发到群里？
A. 要，完整发群里  
B. 只发摘要，详细文件落盘  
C. 默认不发，除非用户要求

---

## 14）长期规则沉淀只在周复盘中做，这条是否要严格定死？
A. 是，**长期规则只允许在周复盘中沉淀**  
B. 默认在周复盘中做，必要时日复盘可临时标记候选  
C. 日复盘和周复盘都可以直接沉淀

---

## 15）“当前任务相关范围”的判定标准，最终更偏哪种？
A. 只要和当前任务直接相关就纳入  
B. 和当前任务直接相关 + 明显影响结果判断的内容纳入  
C. 和当前任务直接相关，但必须有实际推进价值才纳入

---

# 四、建议的最省事回复格式
你可以直接这样回我：

`1B 2B 3B 4B 5A 6C 7A 8B 9B 10B 11C 12B 13B 14B 15B`

如果你不想一次答完，也可以先答前 8 题。  
你答完后，我就把它们收束成：

1. **`deep-review` 最终规则清单（定稿版）**
2. **可直接写入的 SKILL.md 结构稿**
3. **references 清单**
