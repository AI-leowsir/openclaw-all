# Knowledge 目录

## 定义

`knowledge/` 只存放长期、可复用、可追溯的正式知识。

这里不存放两类内容：
- 任务级临时上下文，例如 `context-pack.md`、`context-pack.reviewed.md`
- 未确认的用户修改意见或候选反馈

当前系统明确区分三层：

```text
1. knowledge/                              长期正式知识
2. tasks/<task-id>/writing-agent/input/   任务级临时 context-pack
3. tasks/<task-id>/review/                候选反馈与冲突记录
```

## 当前有效分层

- `core/`
  通用稳定知识。包括产品事实、受众、品牌语气、术语表、来源注册等。
- `playbooks/`
  渠道与页面类型规则。当前第一阶段主用 `playbooks/seo/`。
- `feedback/`
  只存用户已确认的长期偏好。只允许 confirmed 的全局、渠道、页面类型偏好进入这里。
- `indexes/`
  供 `seo_organizing_agent retrieval` 使用的轻量索引。
- `hypotheses/`
  保留层。只放证据不足、暂不允许进入正式知识的观察性内容；不属于当前标准写作检索范围。

## 第一阶段目标范围

- SEO 产品页
- SEO 分类页
- SEO 栏目页
- 公众号与推特规则预留

## 检索范围

`seo_organizing_agent` 在 `retrieval` 模式下只允许检索：

```text
knowledge/indexes/
knowledge/core/
knowledge/playbooks/seo/
knowledge/feedback/
```

默认不检索：

```text
knowledge/hypotheses/
tasks/*/review/feedback-candidate.yaml
其它 agent 的 session 历史
```

## 写入规则

### synthesis mode

`seo_organizing_agent` 在 `synthesis` 模式下只应直接维护：

```text
knowledge/core/
knowledge/playbooks/seo/
knowledge/feedback/
knowledge/indexes/
```

前提是内容满足以下条件：
- 可追溯
- 可复用
- 证据充分
- 不只是单任务临时要求

### compact mode

`seo_organizing_agent` 在 `compact` 模式下可以：
- 合并和压缩正式规则
- 重建索引
- 读取 `tasks/*/review/feedback-candidate.yaml` 做两天一次候选反馈分析

但不可以：
- 自动把候选反馈写入正式规则
- 把单任务临时修改意见伪装成长期规则

## 关于 feedback

`knowledge/feedback/` 只表示：
- 用户明确确认过
- 可以跨任务复用
- 已经具备长期偏好性质

以下内容不能直接进入 `knowledge/feedback/`：
- 本次修改任务的临时要求
- 仅出现一次、尚未确认的写法偏好
- 与现有规则冲突、但尚未被用户明确确认的 override

这些内容应先写到：

```text
tasks/<task-id>/review/change-request.md
tasks/<task-id>/review/conflict-decision.md
tasks/<task-id>/review/feedback-candidate.yaml
```

## 关于 hypotheses

`knowledge/hypotheses/` 不是当前标准 SEO 写作链路的正式输入层。

它只用于存放：
- 证据不足的观察
- 待验证的结构模式
- 尚未满足正式入库条件的候选方向

如果后续被证实为稳定、可复用、且得到确认，应提升到：
- `knowledge/core/`
- `knowledge/playbooks/seo/`
- `knowledge/feedback/`

而不是继续停留在 `hypotheses/`。
