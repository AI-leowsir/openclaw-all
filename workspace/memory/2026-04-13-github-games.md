# Session: 2026-04-13 13:06:22 UTC

- **Session Key**: agent:main:feishu:group:oc_18670e031c0c78335ff946d6d1fff3ee
- **Session ID**: 739493da-98c8-4605-b4f0-a6876b847947
- **Source**: feishu

## Conversation Summary

assistant: [[reply_to_current]] 这个我先提醒一句：**“按今年开源”如果要做准，最好直接按 GitHub 的创建时间筛，不然普通网页搜索很容易混进老项目、只是今年活跃。**

你现在这个条件我建议按这套来找，结果才靠谱：

### 你真正想筛的条件
- **created:2026-01-01..2026-12-31**
- **纯前端 / 网页**
- **游戏项目，不是引擎**
- **尽量不是大型项目**
- 再按 **stars desc** 排

### GitHub 上可直接用的搜索语法
你可以先看这个方向：

```text
topic:game topic:javascript stars:>50 created:2026-01-01..2026-12-31
```

如果再强调网页前端，可以继续加：

```text
(game OR html5-game OR web-game) language:JavaScript created:2026-01-01..2026-12-31 stars:>20
```

或者更偏前端实现：

```text
(web game) (html css javascript) created:2026-01-01..2026-12-31 stars:>10
```

### 我建议你重点盯的，不是“星最多”，而是这三类今年新项目
1. **Wordle / 2048 / 扫雷 / 数独 / Snake 这种轻玩法新变体**
   - 适合看：玩法包装、主题化、SEO 长尾

2. **AI + game 的轻网页 demo**
   - 适合看：传播点、话题性、社交分享

3. **超轻量 HTML/CSS/JS 游戏模板**
   - 适合看：能不能快速改成自己的站群素材

### 实战判断标准
你找到项目后，优先保留：
- 有在线 demo
- 代码轻
- UI 完整
- 一眼能玩懂
- star 虽然不一定特别高，但**增长快**

剔除：
- 游戏引擎
- 课程 demo
- 桌面封装
- Unity/Godot 导出的网页壳
- 大型多人游戏

如果你要，我下一步可以继续直接帮你做两件事里的一个：

1. **我继续帮你人工筛一版“2026 年新开源、值得看”的具体 repo 清单**  
2. **我直接给你一条 GitHub 搜索链接模板，你点进去自己翻最省事**

你要我继续帮你筛具体项目，我就接着找。
user: <relevant-memories>
The following are stored memories for user "default". Use them to personalize your response:
- As of date unknown, the user allows FAQ content to be more specific than the uploaded document if it does not conflict with the source, may reference common competitor-style phrasing, and must avoid unsupported absolute promises.
- As of date unknown, the user requires real-time verification of group chat names in the review workflow.
- As of date unknown, user uploaded FAQ source documents named '0120-励鸿诺-FAQ.docx' with file keys 'file_v3_0010n_a4ba731a-89d8-465c-826d-d7c1d4894d7g' and 'file_v3_0010n_c793e787-ffc3-4a12-b4e4-70282bc1a2ag'.
- As of date unknown, the user prefers中文内容页文案采用统一风格：FAQ要“短、直、先给答案、少废话”，能一句说清就一句说清，有区间直接给区间，有明确结论直接给结论，保留必要弹性但不要冗长拖尾，并避免以“通常根据……”这类绕弯表述开头。
- As of 2026-04-13, the user may be addressed as "Leo" and prefers communication in Chinese.

Session memories:
- As of 2026-04-12, for review output, when a group `chat_id` is identified, the assistant must query and verify the current group name in real time, use the group name in the body, and include `chat_id` only when necessary.
- As of date unknown, `sessions_list` is treated as a partial discovery source only and not a guaranteed complete source for all group chats, private chats, or sub-sessions in a day; transcript scanning is required for fuller coverage.
- As of 2026-04-12, review outputs must be organized by group rather than by task; when a group chat `chat_id` is involved, the current group name must be queried and verified in real time, the body should prefer the group name, and `chat_id` should be included only when necessary.
</relevant-memories>

Conversation info (untrusted metadata):
```json
{
  "message_id": "om_x100b52f990bfed08c21751c1eb6f613",
  "sender_id": "ou_f8403fe80fca27f9322804bba837c396",
  "conversation_label": "oc_18670e031c0c78335ff946d6d1fff3ee",
  "sender": "ou_f8403fe80fca27f9322804bba837c396",
  "timestamp": "Mon 2026-04-13 20:13 GMT+8",
  "group_subject": "oc_18670e031c0c78335ff946d6d1fff3ee",
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

[message_id: om_x100b52f990bfed08c21751c1eb6f613]
ou_f8403fe80fca27f9322804bba837c396: 1
assistant: 我继续筛一版具体 repo，按“2026 新开源 + 前端网页小游戏 + 非大型”。
assistant: [[reply_to_current]] 我筛了一轮，**今年新开的、同时又满足“前端网页小游戏、非大型”这个条件的高质量项目，公开结果其实不多**。  
原因很简单：这类项目今年很多还很新，star 没积起来，而且 GitHub 搜索会混进引擎、课程 demo、脚本、甚至“不是游戏的 snake”。

### 目前能先看到、相对贴边的几类
1. **Minimalistic minesweeper with Vim support**
   - 这是今年新项目里比较贴“轻量网页小游戏”的
   - 类型：扫雷变体
   - 人群：喜欢极简工具感 / 开发者审美 / 轻逻辑游戏的人

2. **FPOM Meme Hunt**
   - 轻量 Pac-Man 风格 promo game
   - 类型：网页轻游戏 + 营销用途
   - 人群：加密社区、meme 用户、活动传播场景

3. **Legendary Gravity Defied game - web browser port**
   - 浏览器版移植
   - 类型：老游戏网页化
   - 人群：怀旧玩家、轻动作玩法用户

4. **The web game that simulate a student's life who study in Germany**
   - 模拟类网页游戏
   - 类型：叙事 / 生活模拟
   - 人群：学生、轻角色代入用户

5. **Web-based game to learn Git by solving git mysteries**
   - 游戏化学习
   - 类型：网页互动学习游戏
   - 人群：开发者、新手程序员、教育场景

---

## 结论
如果你要的是：
### **“今年新开源 + 真正值得抄的前端网页小游戏”**
现在公开面上我会优先看这三类：

- **扫雷/2048/Wordle 这类轻玩法新变体**
- **Pac-Man / Snake 这种老玩法的新包装**
- **游戏化学习类网页项目**

但老实说，**今年真正星很高、又小而美、又是纯前端网页小游戏的，还没形成特别明显的大爆款。**

### 所以这件事更适合两种打法：
1. **找今年新项目看方向**
2. **找老高 star 项目看成熟玩法模板**

这两个结合才最有用。

---

### 我现在给你的判断
如果你是想找：
- **参考玩法模板** → 看老项目（2048、扫雷、Wordle）
- **看新机会** → 看今年新项目里的“轻包装、轻社交、轻教育、轻 meme 化”

如果你要，我下一条可以直接给你做两版之一：

1. **“今年新开的前端网页小游戏 repo 候选池”**  
2. **“老高 star + 今年新项目”混合对照表，方便你看该抄成熟模板还是追新方向”**

如果只选一个，我建议我直接给你做 **第 2 个**，更有参考价值。
user: <relevant-memories>
The following are stored memories for user "default". Use them to personalize your response:
- As of date unknown, the user allows FAQ content to be more specific than the uploaded document if it does not conflict with the source, may reference common competitor-style phrasing, and must avoid unsupported absolute promises.
- As of date unknown, the user requires real-time verification of group chat names in the review workflow.
- As of date unknown, user uploaded FAQ source documents named '0120-励鸿诺-FAQ.docx' with file keys 'file_v3_0010n_a4ba731a-89d8-465c-826d-d7c1d4894d7g' and 'file_v3_0010n_c793e787-ffc3-4a12-b4e4-70282bc1a2ag'.
- As of date unknown, the user prefers中文内容页文案采用统一风格：FAQ要“短、直、先给答案、少废话”，能一句说清就一句说清，有区间直接给区间，有明确结论直接给结论，保留必要弹性但不要冗长拖尾，并避免以“通常根据……”这类绕弯表述开头。
- As of 2026-04-12, the user’s OpenClaw memory architecture treats mem0 as the structured long-term memory layer for searchable facts such as preferences, rules, decisions, configuration facts, and project status; `MEMORY.md` is used as a local human-readable long-term summary; daily memory is used for day-level logs; transcripts/sessions are treated as raw source-of-truth records.

Session memories:
- As of 2026-04-13, the user may be addressed as "Leo" and prefers communication in Chinese.
- As of 2026-04-12, for review output, when a group `chat_id` is identified, the assistant must query and verify the current group name in real time, use the group name in the body, and include `chat_id` only when necessary.
- As of date unknown, `sessions_list` is treated as a partial discovery source only and not a guaranteed complete source for all group chats, private chats, or sub-sessions in a day; transcript scanning is required for fuller coverage.
- As of 2026-04-12, the user proposed a review-filtering optimization for misclassified direct transcripts: ignore all records tagged '(System)' and only review chats labeled '[User]'; this was identified as a rule to apply later, but documents were not yet changed because the user said '先不动'.
</relevant-memories>

Conversation info (untrusted metadata):
```json
{
  "message_id": "om_x100b52f9a82a18a8c11e29f13152dd8",
  "sender_id": "ou_f8403fe80fca27f9322804bba837c396",
  "conversation_label": "oc_18670e031c0c78335ff946d6d1fff3ee",
  "sender": "ou_f8403fe80fca27f9322804bba837c396",
  "timestamp": "Mon 2026-04-13 20:15 GMT+8",
  "group_subject": "oc_18670e031c0c78335ff946d6d1fff3ee",
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

[message_id: om_x100b52f9a82a18a8c11e29f13152dd8]
ou_f8403fe80fca27f9322804bba837c396: 2
assistant: [[reply_to_current]] 行，我直接给你一个 **“老高 star 模板 vs 今年新项目方向”** 的混合对照表，重点不是凑数量，而是帮你看：**哪些是成熟玩法模板，哪些是新包装方向。**

---

# 一、成熟模板：适合抄“玩法骨架”
这些不是今年新的，但**最适合拿来反推产品结构**。

## 1. 2048
<https://github.com/gabrielecirulli/2048>

**是什么**
- 数字合并益智游戏

**人群**
- 最大众休闲用户
- 碎片时间用户
- 手机上直接玩的人

**适合抄什么**
- 极简规则
- 一局短、复玩强
- 分数驱动
- 几乎不需要教学

**你该学的不是 UI，是这个公式**
- **3 秒懂规则 + 10 秒上手 + 10 分钟停不下来**

---

## 2. emoji-minesweeper / XP 扫雷类
- <https://github.com/muan/emoji-minesweeper>
- <https://github.com/ShizukuIchi/minesweeper>

**是什么**
- 扫雷的轻包装版 / 怀旧复刻版

**人群**
- 经典逻辑游戏用户
- 怀旧用户
- 对“老游戏新皮肤”有感觉的人

**适合抄什么**
- 老玩法套新主题
- 怀旧 UI 直接带情绪价值
- 搜索词清晰，适合 SEO

**你该学的是**
- **不要重新发明玩法，先重新包装认知**

---

## 3. Wordle 类
- <https://github.com/jlumbroso/wordle-react-clone>
- <https://github.com/doeixd/Wordle-Vanilla>

**是什么**
- 猜词游戏

**人群**
- 英语用户
- 喜欢 daily challenge 的用户
- 喜欢发战绩和社交分享的人

**适合抄什么**
- 每日挑战
- 分享战绩
- 低成本社交传播
- 单页循环访问

**你该学的是**
- **轻玩法 + 高频回访机制**

---

# 二、今年新项目：适合看“包装方向”
这些不一定最成熟，但**更有“2026 新机会”的味道**。

## 1. Pac-Man / Snake / 扫雷的新变体
比如这次筛到的：

- **FPOM Meme Hunt**  
  轻量 Pac-Man 风格 promo game

- **Minimalistic minesweeper with Vim support**  
  极简扫雷变体

**方向价值**
- 不是发明新游戏
- 是把老玩法重新做成：
  - meme 化
  - 社区化
  - 极客化
  - 活动传播化

**适合人群**
- 社区用户
- 极客用户
- 活动流量
- niche 圈层

**你该学的是**
- **经典玩法 + 明确主题人群 = 新项目也能起量**

---

## 2. 游戏化学习类
比如：

- **Web-based game to learn Git by solving git mysteries**

**是什么**
- 用游戏形式学 Git

**人群**
- 开发者
- 编程初学者
- 技术培训 / 教育产品用户

**为什么值得看**
- 这不是纯娱乐，而是：
  - 学习任务
  - 互动挑战
  - 有“学完有收获”的理由

**你该学的是**
- **游戏机制不一定只服务娱乐，也可以服务学习 / 工具 / onboarding**

---

## 3. 轻叙事 / 生活模拟
比如：

- **The web game that simulate a student's life who study in Germany**

**是什么**
- 网页模拟类小游戏

**人群**
- 学生
- 海外留学人群
- 轻叙事偏好用户

**为什么值得看**
- 玩法可能不复杂，但更有代入感
- 题材本身可以带流量

**你该学的是**
- **题材比玩法更新鲜时，流量入口可能来自“身份共鸣”而不是机制创新**

---

# 三、怎么理解“老项目 vs 新项目”

## 老高 star 项目告诉你的
**什么玩法长期有效**
- 2048：极简、成瘾、无学习成本
- 扫雷：经典、逻辑、怀旧
- Wordle：日更、分享、轻社交

## 今年新项目告诉你的
**这些老玩法今天还能怎么重新卖**
- 加 meme
- 加主题人群
- 加学习目标
- 加社区传播
- 加身份认同

---

# 四、如果你从“出海网页小游戏站”角度看

## 最值得做成熟模板变体的
### 1）2048 类
- 最稳
- 全球认知强
- 可做无数主题皮肤版
- 适合广告变现 / SEO / 多语言

### 2）Wordle 类
- 适合做每日挑战
- 适合做语言、领域、垂类主题版
- 适合分享传播

### 3）扫雷类
- 适合怀旧流量
- 适合极简产品
- 适合办公场景 / PC 网页流量

---

## 最值得看“新方向包装”的
### 1）游戏化学习
- 比纯游戏更容易带“有用”标签
- 更容易做付费、订阅、课程引流

### 2）社区 / meme 化小游戏
- 更容易借热点
- 更适合冷启动传播

### 3）特定身份题材
- 留学、程序员、职场、语言学习
- 容易做小圈层高点击

---

# 五、我直接给你结论
如果你现在是为了**找能做出海站的方向**，不要盯“今年有没有全新原创玩法爆款”，这个方向反而容易空。

你更该看的是这条线：

## 最靠谱路线
**老爆款玩法骨架 + 今年的新包装方向**

也就是：
- 2048 / Wordle / 扫雷 做底层模板
- 再叠加：
  - AI 主题
  - 留学主题
  - 开发者主题
  - meme 主题
  - 每日挑战
  - SEO 长尾页

---

如果你要，我下一条可以直接给你出：
**“基于这个思路，最适合你做的 10 个出海网页小游戏选题”**  
我直接按“玩法 + 人群 + 流量入口”写。
user: <relevant-memories>
The following are stored memories for user "default". Use them to personalize your response:
- As of date unknown, the user allows FAQ content to be more specific than the uploaded document if it does not conflict with the source, may reference common competitor-style phrasing, and must avoid unsupported absolute promises.
- As of date unknown, the user prefers中文内容页文案采用统一风格：FAQ要“短、直、先给答案、少废话”，能一句说清就一句说清，有区间直接给区间，有明确结论直接给结论，保留必要弹性但不要冗长拖尾，并避免以“通常根据……”这类绕弯表述开头。
- As of date unknown, user uploaded FAQ source documents named '0120-励鸿诺-FAQ.docx' with file keys 'file_v3_0010n_a4ba731a-89d8-465c-826d-d7c1d4894d7g' and 'file_v3_0010n_c793e787-ffc3-4a12-b4e4-70282bc1a2ag'.
- As of date unknown, the user requires real-time verification of group chat names in the review workflow.
- As of date unknown, the user confirmed Bra 与 Adult Bra 两个页面的中文版当前版本已定稿，不需要继续优化，并要求后续同类页面按这一版作为基准延续写法。

Session memories:
- As of 2026-04-13, the user may be addressed as "Leo" and prefers communication in Chinese.
- As of 2026-04-12, the user proposed a review-filtering optimization for misclassified direct transcripts: ignore all records tagged '(System)' and only review chats labeled '[User]'; this was identified as a rule to apply later, but documents were not yet changed because the user said '先不动'.
- As of 2026-04-12, when a group such as `工作组` has a verified current name but no local transcript hit for the target week, it should be labeled: `已核实名称，但本机未命中本周记录`.
- As of 2026-04-12, for review output, when a group `chat_id` is identified, the assistant must query and verify the current group name in real time, use the group name in the body, and include `chat_id` only when necessary.
</relevant-memories>

Conversation info (untrusted metadata):
```json
{
  "message_id": "om_x100b52fa12fd6ca0c455c681c66c287",
  "sender_id": "ou_f8403fe80fca27f9322804bba837c396",
  "conversation_label": "oc_18670e031c0c78335ff946d6d1fff3ee",
  "sender": "ou_f8403fe80fca27f9322804bba837c396",
  "timestamp": "Mon 2026-04-13 20:46 GMT+8",
  "group_subject": "oc_18670e031c0c78335ff946d6d1fff3ee",
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

[message_id: om_x100b52fa12fd6ca0c455c681c66c287]
ou_f8403fe80fca27f9322804bba837c396: 这还是要看搜索量的
assistant: [[reply_to_current]] 对，**最后还是得看搜索量**。  
GitHub star 只能告诉你“开发者圈里有人看”，**不能证明用户真的会搜**。

## 你真正该看的顺序
### 1. 先看有没有搜索需求
先判断这个词有没有人搜：

- `2048`
- `play 2048`
- `minesweeper online`
- `wordle unlimited`
- `daily word game`
- `sudoku online`
- `snake game online`

如果核心词本身没量，项目再酷也不值钱。

---

### 2. 再看这个需求是不是适合网页承接
有些词有量，但不一定适合做网页小游戏站。

### 适合网页承接的词
- 带明显玩法意图
- 带 `online / free / play / browser`
- 规则简单，一打开就能玩

比如：
- `minesweeper online`
- `play snake`
- `2048 game`
- `sudoku online`
- `wordle unlimited`

这类最适合。

---

### 3. 再看竞争难度
不是有量就做，要看是不是已经被巨头占满。

比如：
- `wordle` 本词很大，但 NYT 占得太死
- `snake game` 也可能被大站和游戏站压住
- `2048 online` 这种反而更适合做变体和长尾页

---

## 所以正确打法不是“先看 GitHub 有啥”
而是：

### **先看搜索词 → 再决定做哪种游戏模板**

也就是：

- 搜索量高的词
- 对应什么轻玩法
- 市场上现有页面做得烂不烂
- 你能不能更快做一个更好的页面

---

## 如果按 SEO/出海站思路，最值得优先验证的词类通常是
### 第一类：经典 evergreen
- `2048`
- `2048 game`
- `2048 online`
- `minesweeper`
- `minesweeper online`
- `snake game`
- `sudoku online`
- `solitaire online`

### 第二类：带动作意图
- `play 2048`
- `play snake`
- `play sudoku online`
- `play minesweeper`

### 第三类：长尾变体
- `2048 unlimited`
- `hard sudoku online`
- `easy minesweeper`
- `daily word puzzle`
- `retro minesweeper`

---

## 你现在这件事最该做的不是继续找 repo
而是先做一个表：

- **关键词**
- **月搜索量**
- **关键词难度**
- **SERP 长什么样**
- **现有页面质量**
- **适合哪种游戏模板**
- **能不能做差异化**

---

## 我给你一个很直接的判断
### GitHub 适合干嘛
- 找模板
- 看玩法实现
- 找 UI/交互灵感
- 找能快速改造的开源底子

### 搜索量适合干嘛
- 判断值不值得做
- 决定先做哪个赛道
- 决定标题、域名、内容结构

---

## 最佳流程
**搜索量定方向 → GitHub 找实现模板 → 快速上线验证**

而不是反过来。

如果你要，我下一条可以直接帮你出一版：

### **“适合做出海网页小游戏站的关键词候选池”**
我会按：
- 核心词
- 搜索意图
- 适合的游戏类型
- 值不值得做

给你一版初筛框架。
user: <relevant-memories>
The following are stored memories for user "default". Use them to personalize your response:
- As of date unknown, the user allows FAQ content to be more specific than the uploaded document if it does not conflict with the source, may reference common competitor-style phrasing, and must avoid unsupported absolute promises.
- As of date unknown, the user prefers中文内容页文案采用统一风格：FAQ要“短、直、先给答案、少废话”，能一句说清就一句说清，有区间直接给区间，有明确结论直接给结论，保留必要弹性但不要冗长拖尾，并避免以“通常根据……”这类绕弯表述开头。
- As of date unknown, user uploaded FAQ source documents named '0120-励鸿诺-FAQ.docx' with file keys 'file_v3_0010n_a4ba731a-89d8-465c-826d-d7c1d4894d7g' and 'file_v3_0010n_c793e787-ffc3-4a12-b4e4-70282bc1a2ag'.
- As of date unknown, the user confirmed Bra 与 Adult Bra 两个页面的中文版当前版本已定稿，不需要继续优化，并要求后续同类页面按这一版作为基准延续写法。
- As of date unknown, the user requires real-time verification of group chat names in the review workflow.

Session memories:
- As of 2026-04-13, the user may be addressed as "Leo" and prefers communication in Chinese.
- As of 2026-04-12, the user proposed a review-filtering optimization for misclassified direct transcripts: ignore all records tagged '(System)' and only review chats labeled '[User]'; this was identified as a rule to apply later, but documents were not yet changed because the user said '先不动'.
- As of 2026-04-12, when a group such as `工作组` has a verified current name but no local transcript hit for the target week, it should be labeled: `已核实名称，但本机未命中本周记录`.
- As of date unknown, `sessions_list` is treated as a partial discovery source only and not a guaranteed complete source for all group chats, private chats, or sub-sessions in a day; transcript scanning is required for fuller coverage.
</relevant-memories>

Conversation info (untrusted metadata):
```json
{
  "message_id": "om_x100b52fa2a50e0a4c36566353b0ff13",
  "sender_id": "ou_f8403fe80fca27f9322804bba837c396",
  "conversation_label": "oc_18670e031c0c78335ff946d6d1fff3ee",
  "sender": "ou_f8403fe80fca27f9322804bba837c396",
  "timestamp": "Mon 2026-04-13 20:49 GMT+8",
  "group_subject": "oc_18670e031c0c78335ff946d6d1fff3ee",
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

[message_id: om_x100b52fa2a50e0a4c36566353b0ff13]
ou_f8403fe80fca27f9322804bba837c396: 找找有没有游戏集合站的开源项目吧
assistant: 我先帮你找“游戏集合站/网页小游戏站”的开源项目，重点看能不能直接拿来改造成站点。
assistant: 先拿到几个入口了。我再抓这几个仓库/主题页，看哪些更像“现成游戏集合站模板”，哪些只是列表。
assistant: [[reply_to_current]] 有，而且这次找到的里，**真正像“游戏集合站/小游戏门户”能直接拿来改的**，我先给你挑最有用的，不给你堆纯列表。

## 最值得先看
### 1. attogram / games
<https://github.com/attogram/games>

**这是什么**
- 一个现成的 **games website / 游戏集合站**
- 仓库描述就很直白：  
  **“Your own games website, filled with open source goodness! Automated installation of a plethora of open source web games. Fully customizable.”**

**为什么值得看**
- 它不是单个游戏
- 也不是纯 awesome list
- 是更接近你要的：**自己搭一个小游戏站**

**适合拿来干嘛**
- 直接二开成自己的游戏集合站
- 改 UI、改分类、改 SEO 页
- 把精选游戏接进去做门户

**我对它的判断**
- 这是这批里**最贴“站点模板”**的一类

---

### 2. MonkeyGG2 / monkeygg2.github.io
<https://github.com/MonkeyGG2/monkeygg2.github.io>

**这是什么**
- 一个 **feature-rich games site**
- 仓库描述里直接写了：**150+ games**

**为什么值得看**
- 更像一个已经做出来的“游戏站”
- 不是纯资源列表，而是偏实际站点结构
- 适合参考：
  - 首页排布
  - 分类方式
  - 游戏入口组织
  - 多游戏站的前端壳

**注意**
- 这类项目常常会带一些“代理/学校环境访问”场景色彩
- 你要的是结构和实现，不一定照单全收

---

## 也值得看，但更偏“数据源 / 目录”
### 3. michelpereira / awesome-open-source-games
<https://github.com/michelpereira/awesome-open-source-games>

**这是什么**
- 开源游戏大列表
- 有 Browser-Based 分类

**适合干嘛**
- 当“采集池 / 种子库”
- 用来找可嵌入、可精选的开源网页游戏

**不适合干嘛**
- 它本身不是现成站点模板
- 更像数据库入口，不是产品壳

---

### 4. proyecto26 / awesome-jsgames
<https://github.com/proyecto26/awesome-jsgames>

**这是什么**
- JavaScript 游戏精选列表

**适合干嘛**
- 找前端小游戏资源
- 看哪些项目适合被你收进站里

**不适合干嘛**
- 它也是列表，不是门户站模板

---

## 如果你要做“游戏集合站”，我建议你把它们这样用

### 用法 A：站点模板
优先看：
- **attogram/games**
- **monkeygg2.github.io**

这两个更接近“壳子已经有了”。

### 用法 B：游戏来源池
优先看：
- **awesome-open-source-games**
- **awesome-jsgames**

这两个更适合给你补内容库。

---

## 我直接给你结论
### 最像你想要的“开源游戏集合站”
1. **attogram/games**  
2. **MonkeyGG2/monkeygg2.github.io**

### 最适合做内容源的
3. **michelpereira/awesome-open-source-games**  
4. **proyecto26/awesome-jsgames**

---

## 如果你下一步是要“能做站”
我建议你先看这条路：

- **拿 `attogram/games` 当站点骨架**
- 再从 `awesome-open-source-games` 里挑轻量网页游戏
- 自己重做：
  - 首页
  - 分类页
  - 单游戏页
  - SEO 描述
  - tag / keyword 长尾页

这样最像一门正经产品，而不是单纯收集仓库链接。

如果你要，我下一条可以直接继续帮你做：
**“这几个项目里，哪个最适合你现在拿来二开，为什么”**  
我会按“开发成本 / SEO 适配 / 后续扩展”来排。
user: <relevant-memories>
The following are stored memories for user "default". Use them to personalize your response:
- As of date unknown, the user allows FAQ content to be more specific than the uploaded document if it does not conflict with the source, may reference common competitor-style phrasing, and must avoid unsupported absolute promises.
- As of date unknown, the user prefers中文内容页文案采用统一风格：FAQ要“短、直、先给答案、少废话”，能一句说清就一句说清，有区间直接给区间，有明确结论直接给结论，保留必要弹性但不要冗长拖尾，并避免以“通常根据……”这类绕弯表述开头。
- As of date unknown, user uploaded FAQ source documents named '0120-励鸿诺-FAQ.docx' with file keys 'file_v3_0010n_a4ba731a-89d8-465c-826d-d7c1d4894d7g' and 'file_v3_0010n_c793e787-ffc3-4a12-b4e4-70282bc1a2ag'.
- As of date unknown, the user confirmed Bra 与 Adult Bra 两个页面的中文版当前版本已定稿，不需要继续优化，并要求后续同类页面按这一版作为基准延续写法。
- As of date unknown, the user requires real-time verification of group chat names in the review workflow.

Session memories:
- As of 2026-04-13, the user may be addressed as "Leo" and prefers communication in Chinese.
- As of 2026-04-12, the user proposed a review-filtering optimization for misclassified direct transcripts: ignore all records tagged '(System)' and only review chats labeled '[User]'; this was identified as a rule to apply later, but documents were not yet changed because the user said '先不动'.
- As of date unknown, README documentation was updated to describe the sync notification mechanism.
- As of 2026-04-12, OpenClaw was confirmed to be using an OpenAI-compatible gateway at https://tarotap.pro/v1, but the response format is not fully standard OpenAI-compatible, so successful requests do not imply full standards compatibility.
</relevant-memories>

Conversation info (untrusted metadata):
```json
{
  "message_id": "om_x100b52faca3fa4a0c32177713381ac0",
  "sender_id": "ou_f8403fe80fca27f9322804bba837c396",
  "conversation_label": "oc_18670e031c0c78335ff946d6d1fff3ee",
  "sender": "ou_f8403fe80fca27f9322804bba837c396",
  "timestamp": "Mon 2026-04-13 20:57 GMT+8",
  "group_subject": "oc_18670e031c0c78335ff946d6d1fff3ee",
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

[message_id: om_x100b52faca3fa4a0c32177713381ac0]
ou_f8403fe80fca27f9322804bba837c396: 找一下github上面今年关于游戏收藏最高的star，不论什么类型 技术，记得给我做好介绍
assistant: 我按“今年创建 + GitHub star 高”的口径去找，不限游戏类型和技术栈，然后给你一版带简介的榜单。
assistant: [[reply_to_current]] 我先给你结论：**GitHub 里“今年新建 + 游戏相关 + star 高”的结果，公开搜索非常容易混进引擎、AI 工具、学习游戏、甚至只是带 game 关键词的项目。**  
所以这次我先按“今年新建且目前能看到热度高、确实和游戏强相关”的方向，给你做一版**可读的候选榜**，并顺手说明它们到底是什么。

---

# 今年 GitHub 上高热度的游戏相关项目（候选整理版）

## 1. **面向 Claude Code 的游戏开发工作室类项目**
**它是什么**
- 这类项目不是“游戏本体”，而是**让 AI 帮你做游戏开发**的工作流/技能系统
- 搜索结果里出现了类似：
  - *Turn Claude Code into a full game dev studio*
  - *Claude Code skills that build complete Godot 4 projects from a game description*

**为什么 star 会高**
- 今年 AI + coding 赛道热
- “一句话生成游戏项目”这种叙事很容易吸引开发者收藏

**适合谁**
- 独立开发者
- 想快速做原型的人
- AI coding / agent workflow 玩家

**我的判断**
- **这是“游戏开发工具爆火”，不是“游戏爆火”**
- 如果你想找产品机会，这类更像**生产工具**，不是面向终端玩家的内容

---

## 2. **AI Werewolf / Mafia（LLM 驱动狼人杀）**
**它是什么**
- 让多个大模型扮演玩家，跑社交推理游戏
- 本质是 **AI 多角色博弈 demo / social deduction game**

**为什么会火**
- 很符合今年的 AI 叙事：
  - 多智能体
  - 可观赏性
  - 容易出讨论话题
- 比普通 demo 更有“戏剧性”

**适合谁**
- AI 爱好者
- 社交推理游戏用户
- 做 AI 内容传播的人

**我的判断**
- 这类项目 star 起来快，主要靠：
  - 题材熟
  - AI 角色冲突好看
  - 社交传播属性强

---

## 3. **Learn Kubernetes by playing / 用游戏学 Kubernetes**
**它是什么**
- 一个浏览器里玩的互动学习游戏
- 通过游戏任务去学 K8s、pod、CrashLoopBackOff、kubectl 等

**为什么会火**
- 它不是普通小游戏，而是 **游戏化学习**
- 开发者会觉得“这个有用，不只是玩”

**适合谁**
- 程序员
- DevOps / 云原生学习者
- 做教育产品的人

**我的判断**
- 这是很值得关注的一类：  
  **“游戏机制服务学习”**
- 这类比纯娱乐游戏更容易获得开发者 star 和传播

---

## 4. **k8sgames**
**它是什么**
- 浏览器 3D 游戏化 Kubernetes 学习项目
- 搜索结果里直接提到：
  - *Learn Kubernetes by playing. Deploy pods, fix CrashLoopBackOff, type real kubectl commands.*

**为什么值得看**
- 它代表一种很现实的趋势：
  - 不是做大众游戏
  - 是做**开发者小游戏/训练产品**

**适合谁**
- 技术教育
- 企业培训
- 开发者工具产品团队

**我的判断**
- 如果你看的是“有商业化潜力的 game-like 项目”，它比很多纯小游戏更值得分析

---

## 5. **Slay the Spire 2 MCP / Agentic runs 类项目**
**它是什么**
- 把游戏状态暴露出来，让 AI/agent 能操作游戏
- 本质是 **AI 可调用游戏接口 + agent 自动游玩**

**为什么会火**
- AI agent + 游戏天然适合演示
- 卡牌游戏状态清晰，适合被 agent 接管

**适合谁**
- AI agent 开发者
- 游戏 mod / automation 玩家
- 喜欢看 AI 玩游戏的人

**我的判断**
- 这更偏 **“AI + game infrastructure / mod tooling”**
- 不是大众游戏项目，但在开发者圈很容易涨 star

---

## 6. **轻量 2D WebAssembly / 小程序游戏引擎**
**它是什么**
- 比如搜索结果出现：
  - *Lightweight 2D game engine for WebAssembly and WeChat MiniGames*

**为什么会火**
- 游戏引擎本来就容易吃技术关注
- “轻量 + WebAssembly + 多端”是很好的技术卖点

**适合谁**
- 游戏开发者
- 小程序开发者
- Web 游戏基础设施方向的人

**我的判断**
- 这是“技术栈项目”，不是游戏本体
- 但 star 往往会比具体小众游戏涨得更快

---

# 这批项目你怎么理解

## 真正今年高 star 的，大概率分三类：
### 1）AI 做游戏开发
- 不是游戏，是生成/构建/工作流

### 2）AI 玩游戏 / AI 参与游戏
- 比如狼人杀、Slay the Spire agent

### 3）游戏化学习 / 游戏开发基础设施
- 比如 k8sgames、游戏引擎、MCP bridge

---

# 如果你问“今年最容易涨 star 的游戏相关项目是什么类型”
不是传统小游戏。  
更像是这几种：

## 最容易涨 star 的方向
- **AI + 游戏开发工具**
- **AI + 社交推理游戏**
- **游戏化学习（尤其面向开发者）**
- **游戏引擎 / 游戏桥接基础设施**
- **MCP / agent 能直接操控游戏的项目**

---

# 如果你问“这对你有什么用”
我会分成两层看：

## 如果你想找“开发者热度”
优先看：
- AI game dev studio
- Godot + Claude Code
- k8sgames
- Slay the Spire MCP

## 如果你想找“用户搜索量 / 可做网页流量站”
这批反而未必最好。  
因为它们很多：
- 开发者导向
- 传播靠圈内话题
- 不一定有大众搜索需求

---

# 我给你的直接判断
**今年 GitHub 上涨 star 快的“游戏相关项目”，主战场已经不只是游戏本体，而是“AI × 游戏”与“游戏化开发者体验”。**

如果你要，我下一步可以继续帮你做两版之一：

1. **更严格版：我继续人工筛出“今年创建 + 目前 star 最高”的具体 repo 名单**  
2. **实用版：我把这些项目按“开发者热度 / 玩家热度 / 商业化价值”给你重排**

如果只选一个，我建议做 **第 2 个**，更适合判断值不值得跟。
