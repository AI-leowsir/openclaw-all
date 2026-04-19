# Context Pack 工作流

## 目标

Context Pack 工作流用于约束学习、SEO整理、写作三个 Agent 的协作边界。

核心原则：

```text
main agent 只负责调度、冲突判断和传递最终 context-pack 路径
learning_agent 只负责学习和标准化提取
seo_organizing_agent 负责直接维护 knowledge/、检索 active SEO 规则、生成 context-pack、定期 compact
writing_agent 只根据 main agent 明确指定的 context-pack 写作
```

## 任务链路

### 学习任务

```text
main agent
  -> learning_agent
  -> seo_organizing_agent synthesis mode
  -> 直接更新 knowledge/
  -> main agent 汇报
```

学习任务不能只停在 `learning_agent`。学习完成后必须交给 `seo_organizing_agent` 做 SEO 规则沉淀。

### 写作任务

```text
main agent
  -> seo_organizing_agent retrieval mode
  -> context-pack.md 或 context-pack.blocked.md
  -> main agent 传递 context-pack 路径
  -> writing_agent 根据 context-pack 写作
```

写作任务不能直接调用 `writing_agent`。必须先由 `seo_organizing_agent` 检索 active SEO 规则并生成临时上下文文件。

### 修改任务

```text
main agent
  -> seo_organizing_agent retrieval mode
  -> context-pack.md
  -> main agent 读取用户修改意见
  -> 如无冲突，生成 context-pack.reviewed.md
  -> 如冲突，记录冲突点并向用户确认
  -> writing_agent 根据 main agent 指定的 context-pack 写作
```

修改任务必须遵守以下规则：

```text
不得直接覆盖 seo_organizing_agent 产出的原始 context-pack.md
主 Agent 必须保留检索版 context-pack.md 作为基线
主 Agent 产出的修订版默认写到 writing-agent/input/context-pack.reviewed.md
若修改意见与 Required Rules、Writing Boundaries、Source Evidence 冲突，必须先向用户确认
用户修改意见只记录为候选反馈，不直接写入正式规则
```

### 学习 + 写作任务

```text
main agent
  -> learning_agent
  -> seo_organizing_agent synthesis mode
  -> seo_organizing_agent retrieval mode
  -> context-pack.md
  -> writing_agent
```

### 维护任务

```text
main agent 或 cron
  -> seo_organizing_agent compact mode
  -> 分层、合并、压缩、重建索引
```

## learning-output-manifest.yaml 规范

学习 Agent 必须通过文件路径清单交接给 SEO整理 Agent。默认路径：

```text
tasks/<task-id>/learning-agent/artifacts/learning-output-manifest.yaml
```

该文件至少列出：

```text
normalized/combined-text.md
normalized/source-map.yaml
observations/ 下的观察文件
artifacts/fetch-report.md
artifacts/source-summary.md
coverage gaps
```

`seo_organizing_agent synthesis mode` 必须优先读取该 manifest，并按 manifest 中列出的文件路径整理。manifest 缺失时可以降级读取标准目录，但必须在 `synthesis-summary.md` 标记这个交接缺口。

## seo_organizing_agent 的三种模式

### synthesis mode

用于学习任务之后。

职责：

```text
读取 learning_agent 标准化产物
提炼 SEO 结构、规则、证据边界
直接写入 knowledge/core、knowledge/playbooks/seo、knowledge/feedback、knowledge/indexes
自动合并重复规则并记录 knowledge-write-report
自动冲突裁决并记录 conflict-report
```

禁止：

```text
写最终文案
产出待审批规则
等待 approval 后再入库
扩展到非 SEO 行业规则
```

### retrieval mode

用于写作任务之前。

职责：

```text
根据当前任务主题检索 active SEO 规则、playbook、feedback
把可用规则和边界打包成 context-pack.md
如果缺规则或资料不足，生成 context-pack.blocked.md
```

禁止：

```text
新增规则
改写 knowledge/ 下的稳定内容
使用 shadow、archived、证据不足或范围不匹配的规则
根据常识补充未命中的规则
读取其它 agent 的 session 历史作为规则来源
写最终文案
```

### compact mode

用于维护 SEO 规则库。

职责：

```text
分层整理已有 SEO 规则
合并重复规则与重复证据
压缩冗长规则并保留来源引用
将更强规则保持为 active，将较弱或过时规则降为 shadow / archived
重建 knowledge/indexes/
分析 review/ 下沉淀的候选反馈，决定是否升级为正式规则候选
```

禁止：

```text
写最终文案
扩展到非 SEO 行业规则
根据猜测生成新规则
删除仍被强规则引用的证据
自动把候选反馈写入正式规则
```

## active / shadow / archived

SEO 规则库内部至少区分这三种状态：

```text
active    当前检索可用
shadow    已保留但不优先使用
archived  归档，不参与正常检索
```

`retrieval mode` 只允许使用 `active` 规则。

## context-pack.md 规范

默认路径：

```text
tasks/<task-id>/writing-agent/input/context-pack.md
```

必须包含以下章节：

```markdown
# Writing Context Pack

## 1. Task Profile
说明本次任务类型、页面类型、行业、语言、输入状态、输出目标。

## 2. Matched Rules
列出本次检索命中的 active SEO 规则或知识文件路径。

## 3. Required Rules
列出 writing_agent 必须遵守的规则。

## 4. Optional References
列出可以参考但不能强行套用的内容。

## 5. Source Evidence
说明关键规则或结论来自哪些知识文件、任务产物或证据。

## 6. Writing Boundaries
说明哪些不能写、不能推断、不能使用。

## 7. Required Output
说明 writing_agent 必须输出的文件和内容。

## 8. Missing / Excluded Items
说明检索过但未采用的内容，以及原因。
```

`context-pack.md` 是任务级临时文件，不是长期规则库。跨任务默认重新生成，只允许在同一 `task-id` 内按 `--resume` 复用。

## context-pack.reviewed.md 规范

默认路径：

```text
tasks/<task-id>/writing-agent/input/context-pack.reviewed.md
```

用途：

```text
由 main agent 基于原始 context-pack.md 和用户最新修改意见生成
只对当前 task-id 生效
用于修改任务或需要任务级 override 的写作
```

修订规则：

```text
不得直接覆盖原始 context-pack.md
同一任务收到新的修改意见时，必须回到原始 context-pack.md 重新生成 reviewed 包
如果 knowledge/、输入资料、页面类型或用户目标变化，必须先重新 retrieval，再生成新的 reviewed 包
reviewed 包只能承载任务级 override，不得伪装成长期规则
```

## context-pack.blocked.md 规范

默认路径：

```text
tasks/<task-id>/writing-agent/input/context-pack.blocked.md
```

出现以下情况时必须生成 blocked 文件，而不是进入写作：

```text
没有匹配的 active SEO 规则
只有 shadow / archived 规则
规则和任务类型不匹配
资料不足
当前任务需要新规则但 learning/synthesis 尚未完成
```

blocked 文件必须包含：

```markdown
# Context Pack Blocked

## Block Reason
阻塞原因。

## Searched Scope
已经检索过的范围。

## Found But Not Usable
找到但不能用的内容，例如 shadow 规则、archived 规则、页面类型不匹配的规则。

## Required Next Step
下一步需要主 Agent 做什么。
```

## 候选反馈与 compact

默认路径：

```text
tasks/<task-id>/review/feedback-candidate.yaml
```

规则：

```text
用户修改意见可以整理为候选反馈
候选反馈不直接进入 knowledge/feedback/
compact 以每两天一次的维护节奏聚合候选反馈
compact 只分析是否值得升级为正式规则候选，不自动入库
只有用户明确确认的长期偏好，才允许进入正式规则
```

## writing_agent 约束

`writing_agent` 在 context-pack 模式下必须遵守：

```text
只读取 main agent 传来的 context-pack.md 或 context-pack.reviewed.md
只使用所提供 context-pack 明确列出的规则和文件
不自行检索 knowledge/、playbooks/ 或其它 agent session
不创建新规则
不使用 shadow、archived、冲突中或未列入 context-pack 的规则
如果 context-pack 不足，必须阻塞，不得继续写
```

## 正常入口

生产任务必须通过：

```text
tools/run-chain.sh
```

修改任务推荐按以下顺序执行：

```text
1. tools/run-chain.sh <task-id> --task writing --prepare-only [--resume]
2. main agent 生成 context-pack.reviewed.md
3. tools/run-chain.sh <task-id> --task writing --resume --writing-context-pack tasks/<task-id>/writing-agent/input/context-pack.reviewed.md
```

底层脚本：

```text
tools/run-learning-agent.sh
tools/run-seo-organizing-agent.sh
tools/run-writing-agent.sh
```
