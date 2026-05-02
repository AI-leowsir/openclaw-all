# Multi Search Engine

## Current Status

This skill is CDP-only. It is retained only as a search URL and operator reference.

## Usage

Open search URLs in the OpenClaw-managed Chrome CDP browser:

- `https://www.google.com/search?q=python`
- `https://duckduckgo.com/?q=privacy`
- `https://www.google.com/search?q=site:github.com+python`

Do not use `web_fetch`, `web_search`, browserless, Tavily, curl, requests, urllib,
httpx, search APIs, direct JSON endpoints, old/mobile endpoints, or temporary
scripts for search result or page data.
