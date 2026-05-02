---
name: browserless-fetch
description: "已禁用。OpenClaw 本地规则要求所有网页抓取、搜索结果读取、页面学习、内容提取、站点监控和资料采集只能使用 OpenClaw Chrome CDP/browser。"
---

# Browserless Fetch Disabled

此 skill 不再作为抓取通道使用。

## 硬规则

- 禁止使用 browserless.io、`browserless-fetch`、`web_fetch`、`web_search`、`curl`、`requests`、`urllib`、`httpx`、搜索引擎/API、old/mobile/JSON 端点或临时脚本抓取网页数据。
- 唯一允许的网页数据来源是 OpenClaw 管理的 Chrome CDP：`http://127.0.0.1:9223`。
- 需要搜索时，用 CDP 接管浏览器打开搜索页面并读取结果。
- CDP/browser 超时、未登录、无权限或被限流时，记录 `cdp_unavailable` / `needs_login_or_permission` / `rate_limited`，报告 coverage gap，并停止该来源。

## 替代入口

- 使用 `browser` 工具。
- 或使用项目内正式 CDP adapter/CLI，且必须连接同一个 OpenClaw Chrome 会话。
