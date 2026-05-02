# Web Search API Configuration Disabled

This reference is intentionally disabled.

OpenClaw on this machine must not configure or use `web_search` providers such as
Tavily, Kimi, Brave, OpenAI native web search, or any other search API for web
collection.

Allowed source for webpage search/result reading/page extraction:

```text
OpenClaw-managed Chrome CDP: http://127.0.0.1:9223
```

If CDP cannot access the source, record `cdp_unavailable`,
`needs_login_or_permission`, or `rate_limited`, then stop that source and report
the coverage gap.
