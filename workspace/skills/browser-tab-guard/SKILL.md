---
name: browser-tab-guard
description: "浏览器标签页生命周期管理工具。任何使用 browser/CDP 的任务，必须在首次 browser 调用前执行 snapshot，在任务完成前执行 cleanup。当 agent 提到 browser/标签/tab/cleanup/清理标签 时触发。"
---

# Browser Tab Guard

自动管理 browser 标签页生命周期，防止任务完成后标签残留。

## 核心原理

- **snapshot**：在 browser 工作开始前，记录当前所有标签 ID 作为基线
- **cleanup**：在任务结束时，关闭基线之后新增的标签
- **sweep**：紧急清理，无需基线，关闭所有 agent 打开的 http/https 页面标签

## 使用方法

### 1. 任务开始前（首次使用 browser 之前）

```bash
exec bash ~/.openclaw/workspace/skills/browser-tab-guard/scripts/tab-guard.sh snapshot <task-id>
```

`<task-id>` 使用当前任务 ID 或任意唯一标识。

### 2. 任务结束时（汇报完成之前，无论成功/失败）

```bash
exec bash ~/.openclaw/workspace/skills/browser-tab-guard/scripts/tab-guard.sh cleanup <task-id>
```

> **关键规则**：即使 browser 超时或不可用，cleanup 仍必须执行。
> 这是最常被遗忘的场景 — 正是因为 browser 出了问题，agent 才会忘记清理。

### 3. 紧急清理 / Heartbeat 定期清理

```bash
exec bash ~/.openclaw/workspace/skills/browser-tab-guard/scripts/tab-guard.sh sweep
```

### 4. 查看当前状态

```bash
exec bash ~/.openclaw/workspace/skills/browser-tab-guard/scripts/tab-guard.sh status
```

## 白名单

以下标签永远不会被关闭：
- `chrome://` / `chrome-untrusted://` / `devtools://` / `about:` — 浏览器内部页面
- `ogs.google.com` — 新标签页组件
- `web-pixel-sandbox` — Shopify 等站点的 web pixel worker
- `Service Worker` — 浏览器后台 service worker

## 注意事项

- baseline 文件存放在 `~/.openclaw/state/tab-guard/`
- cleanup 完成后自动删除对应的 baseline 文件
- sweep 会自动清理超过 2 小时的过期 baseline 文件
- 如果没有找到 baseline 文件，cleanup 会自动切换为 sweep
