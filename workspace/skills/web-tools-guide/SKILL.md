---
name: web-tools-guide
description: "Web 工具策略指南。MUST trigger when 用户提到：搜索/上网/查资料/打开网站/抓取网页/获取网络信息/新闻/热点/browser use/浏览器自动化/JS 渲染页面。所有网页数据采集只能走 OpenClaw Chrome CDP/browser。"
---

<!-- baseDir = /root/.openclaw/workspace/skills/web-tools-guide -->

# Web 工具策略

遵循 ReAct 范式，但网页数据采集只有一个通道：

```
Level 1:   browser/CDP         — OpenClaw Chrome 9223，处理搜索页、网页读取、登录、交互、截图
```

不要把 `web_fetch`、`web_search`、browserless、HTTP 库或搜索/API 端点作为降级或替代路径。

---

## 决策流程

```
有明确 URL？
├─ YES → 直接 browser/CDP
└─ NO  → browser/CDP 打开搜索页并读取结果
```

---

## Browser Timeout 容错

- **首次 browser 冷启动必须串行**：第一次调用 browser 时，禁止并发发多个 `browser open` / `navigate` / `snapshot` 作为探测。先成功打开 1 个页面，并完成一次 `tabs` / `snapshot` 验证，再开第二个页面。
- **慢站点优先放宽超时**：如果工具参数支持显式超时，`open` / `navigate` 优先使用 `30000-45000ms`，`snapshot` 优先使用 `30000ms+`，不要沿用短超时去探测 Reddit、X、重 JS 站点。
- **超时恢复只做一次**：如果 browser 首次超时，先检查 `openclaw browser status` 或 `openclaw gateway status`；若 gateway/browser 异常，执行一次 `openclaw gateway restart`，然后只重试一次。不要对同一路径连续盲重试。
- **CDP-only 不允许降级**：所有网页抓取、搜索结果读取、页面学习、内容提取、站点监控和资料采集，browser/CDP 是唯一数据来源。一次恢复重试仍超时，就标记 `cdp_unavailable` / `needs_login_or_permission` / `rate_limited`，停止该来源并向用户报告；禁止改用 `web_fetch`、`web_search`、`browserless-fetch`、`curl`、`requests`、`urllib`、`httpx`、搜索引擎/API、old/mobile/JSON 端点直连或临时脚本抓取。
- **无非 CDP 降级路径**：CDP 不可用时只能报告缺口并等待处理，不能用公开静态文档、API/JSON 或搜索 API 作为替代页面证据。

---

## 搜索

**何时用**：没有明确 URL，需要搜索信息（新闻、热点、查资料、比较信息）。

**怎么用**：使用 `browser` 打开搜索页面，在 CDP 接管的浏览器内输入查询并读取搜索结果。

**结果处理**：搜索结果页本身也是 CDP 证据；后续打开结果 URL 仍必须使用 `browser`。

**失败时**：记录 `cdp_unavailable` / `rate_limited` / coverage gap，等待用户处理。

---

## Level 2: browser

**何时用**：所有已知 URL、搜索结果页、需要读取网页的场景。

**怎么用**：直接调用 `browser`，不要再走 `web_fetch`、`web_search`、`browserless-fetch` 或 HTTP 脚本。

**默认动作**：导航到目标 URL，等待关键元素，提取内容；如果需要登录、交互或截图，继续在同一浏览器上下文完成。

**CDP-only 明确要求**：所有页面数据必须来自 OpenClaw 管理的 Chrome CDP。禁止为了批量、提速或规避超时改用 `web_fetch`、`web_search`、`curl`、Python HTTP 库、old.reddit、公开 JSON 端点等非 CDP 路径；失败就报告失败和缺口。

### 何时用

- **需要登录态**：登录后才可见的内容、管理后台
- **页面交互**：点击按钮、填写表单、翻页、滚动加载更多
- **截图需求**：需要页面视觉信息
- **已知 URL / 搜索结果需要深入读取**

### 操作流程

**信息获取（只读）：**
1. 导航到目标 URL
2. 等待关键元素出现（不要用固定时间等待）
3. 提取所需内容（文本、链接、图片等）
4. 返回结果给��户

**登录操作：**
1. 查找登录页 URL → `read {baseDir}/references/well-known-sites.json`
2. **告知用户即将执行登录操作，获取确认**
3. 导航到登录页
4. 填写凭证（用户提供）或提示用户扫码
5. 等待登录成功，确认后继续后续操作

**页面交互：**
1. 导航到目标页面
2. 使用 CSS 选择器定位元素（辅以文本内容匹配）
3. 执行交互：点击、输入、选择、滚动
4. 等待响应/页面变化
5. 提取结果或截图

### 关键注意事项

- **登录操作必须获得用户授权** — 任何涉及账号登录的操作前，先告知用户并等待确认
- **敏感操作必须二次确认** — 发帖、删除、支付等不可逆操作
- **优先 CSS 选择器** — 比 XPath 更稳定，辅以文本匹配
- **智能等待** — 等待目标元素出现，而非 `sleep(3)` 式固定等待
- **CAPTCHA/验证码** — 无法自动处理时告知用户需手动介入
- **首次 browser 冷启动必须串行** — 不要把多个 `browser open` 当作冷启动探测并发发送；先验证第一个页面可读，再扩展到第二个页面
- **超时恢复只允许一次** — 先查 `openclaw browser status` / `openclaw gateway status`，必要时 `openclaw gateway restart`，然后仅重试一次
- **CDP-only 不降级** — browser 失败后只能报告 `cdp_unavailable` 等状态，不能换到 `web_fetch` / `web_search` / `browserless-fetch` / 脚本 HTTP 抓取
- **标签页用完即关（硬性规则）** — 每个 browser 标签完成抓取后立即关闭，严禁关闭浏览器窗口或进程

---

## 禁用项处理

**当任务需要搜索或网页信息时，不要调用 `web_search`，也不要引导配置搜索 API。**

1. 用 `browser` 打开搜索引擎或目标站点搜索页。
2. 用 CDP snapshot/页面读取获取结果。
3. CDP 不可用时记录 coverage gap，停止该来源。

---

## 常用网站

需要常用网站 URL 时（登录页、搜索引擎、热搜榜等）：

```
read {baseDir}/references/well-known-sites.json
```

通过 key 查找（如 `social.weibo.login`、`search.baidu`）。带 `{query}` 的 URL 替换为实际搜索词。

---

## 搜索

**何时用**：没有明确 URL，需要搜索信息（新闻、热点、查资料、比较信息）。

**怎么用**：使用 `browser` 打开搜索页面，在 CDP 接管的浏览器内输入查询并读取搜索结果。

**结果处理**：返回的 URL 继续用 `browser` 深入获取。

**失败时**：记录 coverage gap 并停止该来源。

---

## Level 2: browser

**何时用**：已知 URL 需要深入读取，或搜索结果需要打开后提取内容。

**默认动作**：
1. 告知用户将直接使用 `browser`
2. 在同一浏览器上下文中打开并读取目标 URL
3. 不要改走 `web_fetch` / `web_search` / `browserless-fetch` / HTTP 脚本

---

## Browser 详细操作

这是最重量级的工具，也是当前问题最多的场景。以下是详细操作指引。

### 何时用

- **JS 渲染页面**：SPA、动态加载内容（微博 feed、知乎回答、小红书瀑布流）
- **需要登录态**：登录后才可见的内容、管理后台
- **页面交互**：点击按钮、填写表单、翻页、滚动加载更多
- **截图需求**：需要页面视觉信息
- **已知 URL / 搜索结果的默认处理**：需要深入读取网页内容时，直接走 browser，不先走其他网页抓取路径

### 操作流程

**信息获取（只读）：**
1. 导航到目标 URL
2. 等待关键元素出现（不要用固定时间等待）
3. 提取所需内容（文本、链接、图片等）
4. 返回结果给用户

**登录操作：**
1. 查找登录页 URL → `read {baseDir}/references/well-known-sites.json`
2. **告知用户即将执行登录操作，获取确认**
3. 导航到登录页
4. 填写凭证（用户提供）或提示用户扫码
5. 等待登录成功，确认后继续后续操作

**页面交互：**
1. 导航到目标页面
2. 使用 CSS 选择器定位元素（辅以文本内容匹配）
3. 执行交互：点击、输入、选择、滚动
4. 等待响应/页面变化
5. 提取结果或截图

### 关键注意事项

- **登录操作必须获得用户授权** — 任何涉及账号登录的操作前，先告知用户并等待确认
- **敏感操作必须二次确认** — 发帖、删除、支付等不可逆操作
- **优先 CSS 选择器** — 比 XPath 更稳定，辅以文本匹配
- **智能等待** — 等待目标元素出现，而非 `sleep(3)` 式固定等待
- **CAPTCHA/验证码** — 无法自动处理时告知用户需手动介入
- **页面加载超时** — 设置合理超时，失败时告知用户并建议重试
- **多步操作保持状态** — 登录后的后续操作复用同一浏览器上下文，不要重新打开
- **同一路径固定** — 所有网页采集任务都是 `browser/CDP -> report gap`，没有非 CDP degraded mode。不要把 `web_fetch` / `web_search` / `browserless-fetch` 当作主路径。
- **标签页用完即关（硬性规则）** — 每个 browser 标签完成抓取后立即关闭该标签页，任务结束前确认无遗留。关闭标签页 ✅ / 关闭浏览器窗口或进程 ❌ 严禁。

---

## 禁用项处理

**当任务需要搜索或网页信息时，不要调用 `web_search`，也不要引导配置搜索 API。**

1. 用 `browser` 打开搜索引擎或目标站点搜索页。
2. 用 CDP snapshot/页面读取获取结果。
3. CDP 不可用时记录 coverage gap，停止该来源。

---

## 常用网站

需要常用网站 URL 时（登录页、搜索引擎、热搜榜等）：

```
read {baseDir}/references/well-known-sites.json
```

通过 key 查找（如 `social.weibo.login`、`search.baidu`）。带 `{query}` 的 URL 替换为实际搜索词。
