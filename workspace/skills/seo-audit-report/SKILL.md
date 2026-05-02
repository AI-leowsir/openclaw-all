---
name: seo-audit-report
description: "CDP-only SEO audit guidance. Do not use the bundled direct HTTP crawler; collect rendered pages through OpenClaw Chrome CDP first, then analyze the captured evidence."
---

# SEO Audit Report (CDP-only)

The old direct HTTP crawler for this skill is disabled.

For SEO audits, collect pages with the OpenClaw-managed Chrome CDP browser at
`http://127.0.0.1:9223`, then audit the captured rendered evidence.

Do not use `web_fetch`, `web_search`, browserless, curl, requests, urllib, httpx,
search APIs, direct HTML/JSON endpoints, old/mobile endpoints, or temporary
scripts to crawl the site.

If CDP cannot load a page, record `cdp_unavailable`, `needs_login_or_permission`,
or `rate_limited`, then report the coverage gap instead of switching to a direct
HTTP crawler.

The legacy `scripts/seo_audit.py` entrypoint now exits with a disabled status so
old commands fail closed.
