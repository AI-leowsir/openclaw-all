---
name: "multi-search-engine"
description: "Multi search engine integration with 17 engines (8 CN + 9 Global). Supports advanced search operators, time filters, site search, privacy engines, and WolframAlpha knowledge queries. No API keys required."
---

# Multi Search Engine v2.0.1

Integration of 17 search engines for web crawling without API keys.

## Search Engines

### Default (International-first)
- **Google**: `https://www.google.com/search?q={keyword}`
- **Google HK**: `https://www.google.com.hk/search?q={keyword}`
- **DuckDuckGo**: `https://duckduckgo.com/html/?q={keyword}`
- **Yahoo**: `https://search.yahoo.com/search?p={keyword}`
- **Startpage**: `https://www.startpage.com/sp/search?query={keyword}`
- **Brave**: `https://search.brave.com/search?q={keyword}`
- **Ecosia**: `https://www.ecosia.org/search?q={keyword}`
- **Qwant**: `https://www.qwant.com/?q={keyword}`
- **WolframAlpha**: `https://www.wolframalpha.com/input?i={keyword}`

### Domestic engines (disabled by default / manual-only)
Do not use these proactively. Use them only when the user explicitly requests a specific domestic search engine or explicitly requires a China-specific platform source:
- **Baidu**: `https://www.baidu.com/s?wd={keyword}`
- **Sogou**: `https://sogou.com/web?query={keyword}`
- **WeChat**: `https://wx.sogou.com/weixin?type=2&query={keyword}`
- **Toutiao**: `https://so.toutiao.com/search?keyword={keyword}`

## Default Routing Policy

- Default to international search engines for general web research.
- Prefer Google / Google HK / DuckDuckGo / Brave / Startpage before other sources.
- Do not proactively use domestic search engines.
- Only use a domestic engine when the user explicitly requests that engine or explicitly requires a China-specific platform source.
- After finding useful URLs, continue with `web_fetch` or `browser` as appropriate.

## Quick Examples

```javascript
// Basic search (default: international)
web_fetch({"url": "https://www.google.com/search?q=python+tutorial"})

// Site-specific
web_fetch({"url": "https://www.google.com/search?q=site:github.com+react"})

// File type
web_fetch({"url": "https://www.google.com/search?q=machine+learning+filetype:pdf"})

// Time filter (past week)
web_fetch({"url": "https://www.google.com/search?q=ai+news&tbs=qdr:w"})

// Privacy search
web_fetch({"url": "https://duckduckgo.com/html/?q=privacy+tools"})

// DuckDuckGo Bangs
web_fetch({"url": "https://duckduckgo.com/html/?q=!gh+tensorflow"})

// Domestic engine example: manual-only when explicitly requested
web_fetch({"url": "https://wx.sogou.com/weixin?type=2&query=AI+产品"})

// Knowledge calculation
web_fetch({"url": "https://www.wolframalpha.com/input?i=100+USD+to+CNY"})
```

## Advanced Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `site:` | `site:github.com python` | Search within site |
| `filetype:` | `filetype:pdf report` | Specific file type |
| `""` | `"machine learning"` | Exact match |
| `-` | `python -snake` | Exclude term |
| `OR` | `cat OR dog` | Either term |

## Time Filters

| Parameter | Description |
|-----------|-------------|
| `tbs=qdr:h` | Past hour |
| `tbs=qdr:d` | Past day |
| `tbs=qdr:w` | Past week |
| `tbs=qdr:m` | Past month |
| `tbs=qdr:y` | Past year |

## Privacy Engines

- **DuckDuckGo**: No tracking
- **Startpage**: Google results + privacy
- **Brave**: Independent index
- **Qwant**: EU GDPR compliant

## Bangs Shortcuts (DuckDuckGo)

| Bang | Destination |
|------|-------------|
| `!g` | Google |
| `!gh` | GitHub |
| `!so` | Stack Overflow |
| `!w` | Wikipedia |
| `!yt` | YouTube |

## WolframAlpha Queries

- Math: `integrate x^2 dx`
- Conversion: `100 USD to CNY`
- Stocks: `AAPL stock`
- Weather: `weather in Beijing`

## Documentation

- `references/advanced-search.md` - Domestic search guide
- `references/international-search.md` - International search guide
- `CHANGELOG.md` - Version history

## License

MIT
