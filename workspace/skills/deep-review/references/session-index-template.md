# Session Index Template

用于日复盘 / 周复盘前，先生成会话索引，明确本次复盘到底基于哪些候选会话与 transcript。

## 日索引输出结构
1. 时间范围
2. 发现到的全部候选 session / transcript
3. 判定为相关的 session / transcript
4. 判定为不相关的 session / transcript
5. 最终纳入复盘的证据集合
6. 覆盖风险与缺口

## 周索引输出结构
1. 时间范围
2. 发现到的全部候选 session / transcript
3. 判定为相关的 session / transcript
4. 判定为不相关的 session / transcript
5. 最终纳入复盘的证据集合
6. 覆盖风险与缺口

## 必须记录的字段
对于每个候选 session / transcript，至少记录：
- sessionKey 或 transcript 文件名
- chat 类型（group / direct / sub-session / unknown）
- 最后更新时间
- 判定结果：相关 / 不相关 / 待确认
- 判定理由
- 是否最终纳入复盘

## 输出路径
- 日索引：`memory/review/index/YYYY-MM-DD-session-index.md`
- 周索引：`memory/review/index/YYYY-MM-DD-weekly-session-index.md`

## 规则
- 不要只记录最终纳入的会话，必须把排除项也记下来
- 不要只凭关键词命中就直接跳到最终复盘
- 必须先有索引，再写复盘
- 优先读取 `memory/review/session-history-index.json` 从中提取目标日期的全部候选会话列表（包括历史 .reset 文件）
- 如果 `sessions_list` 不完整或索引文件缺失，必须结合本地 transcript 手动枚举结果补足候选集合
- 对 direct transcript：忽略所有带 `(System)` 标签的记录，只把 `[User]` 聊天视为可复盘证据
