# International Search Reference (CDP-only)

This reference only helps construct search URLs. It must not be used as a
non-browser fetch guide.

## Hard Rule

All result pages and target pages must be opened and read in the OpenClaw-managed
Chrome CDP browser at `http://127.0.0.1:9223`.

Do not use `web_fetch`, `web_search`, browserless, Tavily, curl, requests, urllib,
httpx, search APIs, direct JSON endpoints, old/mobile endpoints, or temporary
scripts to read search results or page data.

## Useful URLs

- Google: `https://www.google.com/search?q={query}`
- Google news: `https://www.google.com/search?q={query}&tbm=nws`
- Google images: `https://www.google.com/search?q={query}&tbm=isch`
- Google Scholar: `https://scholar.google.com/scholar?q={query}`
- Bing: `https://www.bing.com/search?q={query}`
- DuckDuckGo: `https://duckduckgo.com/?q={query}`
- Brave: `https://search.brave.com/search?q={query}`
- Startpage: `https://www.startpage.com/sp/search?query={query}`
- GitHub: `https://github.com/search?q={query}`

## Operators

- Exact phrase: `"machine learning"`
- Site filter: `site:github.com browser cdp`
- File type: `filetype:pdf annual report`
- Exclude: `python -snake`
- Either term: `cat OR dog`
- Time filter: add Google `tbs=qdr:h`, `tbs=qdr:d`, `tbs=qdr:w`, `tbs=qdr:m`, or `tbs=qdr:y`.

If CDP cannot load or verify the result page, stop that source and report the
coverage gap.
