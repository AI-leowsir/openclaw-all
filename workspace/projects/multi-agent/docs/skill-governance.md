# Skill 发现与更新策略

## 原则
- 市场 skill 的发现归学习 Agent
- 市场 skill 的启用必须经过用户确认
- Agent 不允许自己给自己新增 skill

## 周期
- 每周六由学习 Agent 执行一次官方 skill 巡检
- 来源限定为 OpenClaw 官方

## 状态流转
- `discovered`
- `candidate`
- `approved`
- `enabled`
- `deprecated`

## 文件
- `config/skill-registry/discovered-skills.yaml`
- `config/skill-registry/approved-skills.yaml`
- `config/skill-registry/deprecated-skills.yaml`
- `config/agent-skill-map.yaml`
- `config/skill-registry/skill-review-log.md`

## 规则
- 学习 Agent 只能发现、评估、归档候选 skill
- 主 Agent（main）负责把推荐项汇总给用户
- 用户确认后，才允许更新 `agent-skill-map.yaml`
