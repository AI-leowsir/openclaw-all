# Feedback

`knowledge/feedback/` 只存放已确认的长期偏好。

## 分层

- `global/`
  跨渠道、跨页面类型都成立的长期偏好。
- `channel/`
  只在某个渠道下成立的长期偏好，例如 `channel/seo/`。
- `page-type/`
  只在某种页面类型下成立的长期偏好，例如 `page-type/product-page/`。

## 准入条件

只有同时满足以下条件，才允许写入这里：
- 用户已经明确确认
- 不是单任务临时要求
- 可以跨任务复用
- 证据和边界足够清晰

## 禁止写入

以下内容不得直接写入 `knowledge/feedback/`：
- 当前修改任务里的临时 override
- 尚未确认的用户修改意见
- 仅一次出现、还没有沉淀价值的偏好
- 与现有正式规则冲突、但尚未确认的特殊要求

这些内容应先记录到：

```text
tasks/<task-id>/review/feedback-candidate.yaml
```

由 `seo_organizing_agent compact` 每两天分析一次，再决定是否升级为正式规则候选。
