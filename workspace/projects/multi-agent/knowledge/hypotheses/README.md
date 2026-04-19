# Hypotheses

`knowledge/hypotheses/` 是保留层，不是当前标准 SEO 写作链路的正式知识层。

## 用途

这里只允许存放：
- 证据不足的观察
- 待验证的结构模式
- 暂时不能进入正式规则库的候选方向

## 不用于

- `seo_organizing_agent retrieval` 的正式检索范围
- `writing_agent` 的直接输入
- 用户修改意见的默认归档位置

## 处理规则

- 如果内容后来被证实为稳定、可复用、可追溯，应提升到 `knowledge/core/`、`knowledge/playbooks/seo/` 或 `knowledge/feedback/`
- 如果内容长期无法验证，应在任务产物或 compact 报告中说明边界，而不是伪装成正式规则
- 修改任务里的候选反馈应写到 `tasks/<task-id>/review/feedback-candidate.yaml`，而不是写到这里
