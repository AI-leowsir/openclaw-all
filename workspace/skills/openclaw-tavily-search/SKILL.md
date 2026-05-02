---
name: tavily-search
description: "Disabled. OpenClaw web collection is CDP-only; do not use Tavily or any search API for web search, source lookup, link discovery, or page extraction."
---

# Tavily Search Disabled

This skill is intentionally disabled for this OpenClaw workspace.

All webpage search, source lookup, link discovery, page learning, content extraction,
site monitoring, and research collection must use the OpenClaw-managed Chrome CDP
browser at `http://127.0.0.1:9223`.

Do not use Tavily, `web_search`, `web_fetch`, browserless, curl, requests, urllib,
httpx, search APIs, direct JSON endpoints, old/mobile endpoints, or temporary scripts
as a replacement.

If CDP cannot access the source, record `cdp_unavailable`,
`needs_login_or_permission`, or `rate_limited`, then stop that source and report the
coverage gap.
