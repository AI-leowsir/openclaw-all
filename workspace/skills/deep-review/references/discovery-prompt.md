# Discovery Subflow Prompt

用于 deep-review 的第一阶段：只做证据发现与索引，不直接写最终复盘。

## 目标
- 枚举时间范围内全部候选 session / transcript
- 枚举同时间窗内的输出文件、summary、tool-result 链等补充证据
- 判定相关 / 不相关 / 待确认
- 生成 session 索引
- 明确覆盖风险与缺口

## 要求
- **首先读取 `memory/review/session-history-index.json`**，从 `dateIndex[目标日期]` 获取该日全部候选 transcript 文件列表（包括已 reset 的历史文件）
- 索引文件包含每个文件的北京时间日期归属、用户消息数、行数、文件路径和主题提示
- 只有在索引文件不存在或过期时，才回退到手动扫描 transcript 目录
- 如果需要手动扫描，先用 `sessions_list` 获取可见 session
- 如果结果不完整，必须补扫本地 transcript 目录（包括 `.jsonl.reset.*` 文件）
- 不要只靠关键词命中直接决定最终复盘范围
- 必须记录排除项和排除理由
- 当前会话只是触发与通知落点，不代表复盘范围仅限当前会话
- 所有 transcript 时间归属必须先转 Asia/Shanghai，再判断是否属于目标自然日
- 禁止用原始 UTC 日期前缀、原始 `Z` 时间字符串日期部分、或文件 mtime 直接判断“是不是当天”
- 如果北京时间集合与原始 UTC 直筛集合不一致，必须以北京时间集合为准，并把 UTC 直筛结果标记为不可信的中间结果
- 除原始 transcript 外，必须同步扫描同时间窗输出文件、summary、tool-result 链，不能把 raw transcript 当成唯一证据源
- 如果同时间窗输出文件或 summary 明显多于当前发现的会话链，必须继续补扫，不能提前写复盘
- 如果用户指出“还有内容没找到”，用户点名的主题词必须进入同时间窗反查，直到能定位到对应链路或明确记录失败原因
- 只有在北京时间口径下完成候选集合重建、且同时间窗证据链基本闭合后，才能进入最终复盘

## 输出
- 日发现结果写入：`memory/review/index/YYYY-MM-DD-session-index.md`
- 周发现结果写入：`memory/review/index/YYYY-MM-DD-weekly-session-index.md`

## 完成条件
- 已列出全部候选 session / transcript
- 已列出同时间窗的关键输出文件 / summary / tool-result 证据
- 已标出相关 / 不相关 / 待确认
- 已写明最终纳入复盘的证据集合
- 已写明覆盖风险与缺口
- 已说明是否存在“同时间窗产出存在但来源链未闭合”的问题
- 只有完成上述内容后，才进入复盘子流程
