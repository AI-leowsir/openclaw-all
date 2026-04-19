# MEMORY.md


## Long-term rules


### 用户与输出
- 用户偏好中文交流、先讲结论、少废话、精简。
- 默认采用“直接执行 + 分阶段反馈”。
- 复盘类任务不能只看当前窗口；必须补足当天（北京时间算）所有相关会话、transcript、工具结果和关键文件。
- MEMORY.md 只存长期稳定偏好、长期规则、长期协作约束；不存周报式细节和过程摘要。
-所有任务优先判断是否能够调用agent执行


### 通用调度
- 定时流程是否“跑通”不能只看文件产出；还必须确认已成功发送完成通知。若渠道支持回执，进一步检查回执。
- 路由先判 3 件事：任务目标、输入状态、目标输出；先判角色，再选 agent。
- 输入状态只分 4 类：原始材料、结构化中间层、草稿、已确认成品/执行指令。
- 任务一旦分错 agent，先停止并回退到正确角色，再继续执行。
- 不允许在学习类任务里凭感觉猜 URL；只能使用用户给出的 URL，或从导航、站内链接、sitemap、已验证搜索结果中确认存在的 URL。


### 角色边界
- 学习/研究/取证型 agent 只处理原始材料与证据；不直接出最终成稿。
- 整理/规划/抽象型 agent 只负责产出结构化中间层；不直接承担最终写作或执行。
- 写作/生成型 agent 只接结构化中间层或已确认 brief；不得直接吃原始材料。
- 审核/评估型 agent 只审草稿或既有结果；不代替学习或写作，除非角色声明明确允许。
- 执行/发布型 agent 只接已确认成品/执行指令或审核后的结果；不得从原始材料直接推断外发动作。


### SEO 多 agent 协作
- SEO 协作按 4 层流转：素材层 -> 知识层 -> 任务规则层 -> 表达层。
- `lobster_main` 负责任务分流、链路选择、用户意见整理、冲突升级和最终调度。
- `learning_agent` 只处理新素材、抓取、取证、标准化；不直接写正文。
- `seo_organizing_agent(synthesis)` 负责把学习结果沉淀为正式长期知识。
- `seo_organizing_agent(retrieval)` 负责从知识层和当前任务输入中检索本轮可用规则，生成写作包。
- `writing_agent` 只根据 `context-pack.md` 或 `context-pack.reviewed.md` 写作；不直接读知识库，不自行补规则。


### SEO 默认链路
- 学习任务：`lobster_main -> learning_agent -> seo_organizing_agent(synthesis)`
- 写作任务：`lobster_main -> seo_organizing_agent(retrieval) -> writing_agent`
- 修改任务：`lobster_main -> seo_organizing_agent(retrieval) -> context-pack.md -> lobster_main 整理用户意见/冲突检查 -> context-pack.reviewed.md -> writing_agent`
- 学习+写作任务：`lobster_main -> learning_agent -> seo_organizing_agent(synthesis) -> seo_organizing_agent(retrieval) -> writing_agent`


### 规则包与反馈
- `context-pack.md` 是检索基线，必须保留；不得直接覆盖。
- 修改意见只通过 `context-pack.reviewed.md` 承接，不直接覆盖基线包。
- 用户意见若与规则边界或证据冲突，必须先确认，不能静默覆盖。
- 本轮新增学习结果，必须先经 `seo_organizing_agent(synthesis)` 沉淀后，才能进入 `retrieval` 或长期知识层。
- 正式页面写作默认基于检索后的规则包；仅标题、短 FAQ、翻译、润色等明确小任务允许 `writing_agent --direct` 例外。
- 用户修改意见默认只进入任务级 review 产物，不直接进入正式规则。
- 候选反馈写入 `tasks/<task-id>/review/feedback-candidate.yaml`。
- `knowledge/feedback/` 只接收用户已明确确认、可跨任务复用的长期偏好。
- `seo_organizing_agent(compact)` 每两天分析一次候选反馈；可以分析，不自动入正式规则。
