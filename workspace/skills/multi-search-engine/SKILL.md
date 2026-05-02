---
name: "multi-search-engine"
description: "CDP-only search URL planning. Use only to choose search engines/operators, then open the result page in the OpenClaw-managed Chrome CDP browser. Do not use web_fetch, web_search, search APIs, or HTTP clients."
---

# Multi Search Engine (CDP-only)

This skill is now a query-planning reference only. It must not be used as a crawler,
search API, `web_fetch` shortcut, or non-CDP fallback.

## Hard Rule

- All search result reading must happen in the OpenClaw-managed Chrome CDP browser at `http://127.0.0.1:9223`.
- Do not call `web_fetch`, `web_search`, Tavily, browserless, curl, requests, urllib, httpx, direct search endpoints, JSON endpoints, old/mobile endpoints, or temporary scripts for page data.
- If CDP is unavailable, not logged in, blocked, or rate-limited, stop that source and report `cdp_unavailable`, `needs_login_or_permission`, or `rate_limited`.

## Allowed Use

Use this file only to construct a URL that will be opened in the CDP browser:

- Google: `https://www.google.com/search?q={keyword}`
- Google HK: `https://www.google.com.hk/search?q={keyword}`
- Bing: `https://www.bing.com/search?q={keyword}`
- DuckDuckGo: `https://duckduckgo.com/?q={keyword}`
- Brave: `https://search.brave.com/search?q={keyword}`
- Startpage: `https://www.startpage.com/sp/search?query={keyword}`
- GitHub search: `https://github.com/search?q={keyword}`
- Google Scholar: `https://scholar.google.com/scholar?q={keyword}`

Domestic engines are manual-only: use them only when the user explicitly asks for that engine or explicitly requires a China-specific source.

## Operators

- `site:` searches within a site, for example `site:github.com browser cdp`.
- `filetype:` targets a document type, for example `filetype:pdf annual report`.
- Quoted text searches exact phrases.
- `-term` excludes a term.
- `OR` searches either term.
- Google time filters may be appended to the URL, for example `tbs=qdr:w` for the past week.

## Workflow

1. Build the search URL.
2. Open the URL in the CDP-controlled browser.
3. Read and verify result snippets/links from the rendered page.
4. Open target pages in the same CDP-controlled browser.
5. Record coverage gaps instead of switching to non-CDP fetching.
