#!/usr/bin/env node

import { setTimeout as sleep } from "node:timers/promises";

const DEFAULT_TERMS = [
  "ai",
  "llm",
  "agent",
  "rag",
  "mcp",
  "openai",
  "codegen",
  "developer-tools",
  "workflow",
  "inference",
  "ai-tool",
  "ai-agent",
];
const openedTargetIds = new Set();

function parseArgs(argv) {
  const args = {
    port: 9223,
    limit: 25,
    timeoutMs: 15000,
    retries: 2,
    settleMs: 800,
    keepTabs: false,
    terms: DEFAULT_TERMS,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const part = argv[i];
    if (part === "--port") {
      args.port = Number.parseInt(argv[++i] || "9223", 10);
    } else if (part === "--limit") {
      args.limit = Number.parseInt(argv[++i] || "25", 10);
    } else if (part === "--timeout-ms") {
      args.timeoutMs = Number.parseInt(argv[++i] || "15000", 10);
    } else if (part === "--retries") {
      args.retries = Number.parseInt(argv[++i] || "2", 10);
    } else if (part === "--settle-ms") {
      args.settleMs = Number.parseInt(argv[++i] || "800", 10);
    } else if (part === "--terms") {
      args.terms = (argv[++i] || "").split(",").map((item) => item.trim()).filter(Boolean);
    } else if (part === "--keep-tabs") {
      args.keepTabs = true;
    } else if (part === "--close-tabs") {
      args.keepTabs = false;
    } else if (part === "--help" || part === "-h") {
      printHelp();
      process.exit(0);
    } else {
      throw new Error(`unknown argument: ${part}`);
    }
  }
  return args;
}

function printHelp() {
  process.stdout.write(
    [
      "Usage: node scrape_github_trending.mjs [options]",
      "",
      "Options:",
      "  --port <n>          Chrome remote debugging port, default 9223",
      "  --limit <n>         Max repos per search page, default 25",
      "  --timeout-ms <n>    Page wait timeout, default 15000",
      "  --retries <n>       Retries per search term after first failure, default 2",
      "  --settle-ms <n>     Extra wait after page/results look ready, default 800",
      "  --terms <csv>       GitHub repository search terms",
      "  --keep-tabs         Keep this run's GitHub search tab open",
      "  --close-tabs        Close this run's GitHub search tab after scraping (default)",
    ].join("\n") + "\n"
  );
}

async function httpJson(port, path, options = {}) {
  const response = await fetch(`http://127.0.0.1:${port}${path}`, options);
  const text = await response.text();
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}: ${text}`);
  }
  return text ? JSON.parse(text) : {};
}

async function httpMaybe(port, path, options = {}) {
  const response = await fetch(`http://127.0.0.1:${port}${path}`, options);
  return { ok: response.ok, status: response.status, text: await response.text() };
}

async function openTarget(port, url) {
  return httpJson(port, `/json/new?${encodeURIComponent(url)}`, { method: "PUT" });
}

async function closeTarget(port, id) {
  await httpMaybe(port, `/json/close/${id}`);
}

async function openTaskTarget(port, url) {
  const page = await openTarget(port, url);
  if (page?.id) {
    openedTargetIds.add(page.id);
  }
  return page;
}

async function closeTaskTarget(port, id, args) {
  if (!id || args.keepTabs) {
    return;
  }
  try {
    await closeTarget(port, id);
  } finally {
    openedTargetIds.delete(id);
  }
}

async function cleanupTaskTargets(port, args) {
  if (args.keepTabs) {
    return;
  }
  for (const id of Array.from(openedTargetIds)) {
    await closeTaskTarget(port, id, args);
  }
}

class CDPClient {
  constructor(wsUrl) {
    if (typeof WebSocket === "undefined") {
      throw new Error("global WebSocket is unavailable in this Node runtime");
    }
    this.wsUrl = wsUrl;
    this.ws = null;
    this.nextId = 1;
    this.pending = new Map();
  }

  async connect() {
    this.ws = new WebSocket(this.wsUrl);
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error(`CDP connect timeout: ${this.wsUrl}`)), 5000);
      this.ws.addEventListener("open", () => {
        clearTimeout(timer);
        resolve();
      });
      this.ws.addEventListener("error", (event) => {
        clearTimeout(timer);
        reject(event.error || new Error(`CDP connect failed: ${this.wsUrl}`));
      });
      this.ws.addEventListener("message", (event) => {
        const payload = JSON.parse(event.data);
        if (!payload.id || !this.pending.has(payload.id)) {
          return;
        }
        const pending = this.pending.get(payload.id);
        this.pending.delete(payload.id);
        if (payload.error) {
          pending.reject(new Error(`${pending.method}: ${JSON.stringify(payload.error)}`));
          return;
        }
        pending.resolve(payload.result);
      });
      this.ws.addEventListener("close", () => {
        for (const [id, pending] of this.pending.entries()) {
          pending.reject(new Error(`CDP socket closed before response: ${id}`));
        }
        this.pending.clear();
      });
    });
    await this.send("Page.enable");
    await this.send("Runtime.enable");
  }

  async close() {
    if (!this.ws) {
      return;
    }
    this.ws.close();
    await sleep(50);
  }

  async send(method, params = {}) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error(`CDP socket is not open for ${method}`);
    }
    const id = this.nextId++;
    const result = new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject, method });
    });
    this.ws.send(JSON.stringify({ id, method, params }));
    return result;
  }

  async evaluate(expression) {
    const result = await this.send("Runtime.evaluate", {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    return result?.result?.value;
  }

  async waitFor(expression, timeoutMs = 10000, intervalMs = 300) {
    const started = Date.now();
    while (Date.now() - started < timeoutMs) {
      const value = await this.evaluate(expression);
      if (value) {
        return value;
      }
      await sleep(intervalMs);
    }
    throw new Error(`waitFor timeout: ${expression}`);
  }
}

function toExpression(source) {
  return `JSON.stringify(${source})`;
}

function searchQueryFor(term) {
  const cutoff = new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  const normalizedTerm = String(term || "").replace(/[-_]+/g, " ").replace(/\s+/g, " ").trim();
  return `${normalizedTerm} pushed:>${cutoff} stars:>25`;
}

function repositorySearchUrl(query) {
  const params = new URLSearchParams({
    q: query,
    type: "repositories",
    s: "updated",
    o: "desc",
  });
  return `https://github.com/search?${params.toString()}`;
}

function repositorySearchReadyExpression(query) {
  return `(() => {
    if (document.readyState !== 'complete' || !document.body) return false;
    const url = new URL(location.href);
    if (url.hostname !== 'github.com' || !url.pathname.startsWith('/search')) return false;
    if (url.searchParams.get('type') !== 'repositories') return false;
    if (url.searchParams.get('s') !== 'updated' || url.searchParams.get('o') !== 'desc') return false;
    if (url.searchParams.get('q') !== ${JSON.stringify(query)}) return false;
    if (document.querySelector('a[href*="/stargazers"], li.repo-list-item, [data-testid="results-list"], div.Box-row')) return true;
    const text = document.body.innerText || '';
    return /0 results|did not match any repositories|couldn.t find any repositories/i.test(text);
  })()`;
}

async function waitForPageReady(client, timeoutMs, settleMs) {
  await client.waitFor(
    "document.readyState === 'complete' && !!document.body && document.body.innerText.trim().length > 0",
    timeoutMs,
    200
  );
  if (settleMs > 0) {
    await sleep(settleMs);
  }
}

async function waitForRepositoryResults(client, query, timeoutMs, settleMs) {
  await client.waitFor(repositorySearchReadyExpression(query), timeoutMs, 250);
  let lastSignature = "";
  let stableSince = 0;
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const signature = await client.evaluate(`(() => {
      const resultLinks = Array.from(document.querySelectorAll('a[href]'))
        .map((anchor) => anchor.getAttribute('href') || '')
        .filter((href) => /^\\/[A-Za-z0-9_.-]+\\/[A-Za-z0-9_.-]+\\/?$/.test(href))
        .slice(0, 10)
        .join('|');
      const text = document.body?.innerText || '';
      const empty = /0 results|did not match any repositories|couldn.t find any repositories/i.test(text);
      return [location.href, document.readyState, resultLinks, empty ? 'empty' : 'results'].join('::');
    })()`);
    if (signature === lastSignature) {
      if (!stableSince) {
        stableSince = Date.now();
      }
      if (Date.now() - stableSince >= Math.max(300, settleMs)) {
        return;
      }
    } else {
      lastSignature = signature;
      stableSince = 0;
    }
    await sleep(200);
  }
  throw new Error(`repository results did not stabilize for query: ${query}`);
}

async function clearAndType(client, text) {
  const cleared = await client.evaluate(`(() => {
    const visible = (el) => {
      if (!el) return false;
      const style = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
    };
    const active = document.activeElement;
    const input = active && 'value' in active
      ? active
      : Array.from(document.querySelectorAll([
          '#query-builder-test',
          'input[name="q"]:not([type="hidden"])',
          'input[type="search"]',
          'input[aria-label*="Search" i]',
          'input[placeholder*="Search" i]'
        ].join(','))).find(visible);
    if (!input || !('value' in input)) return false;
    input.focus();
    input.click();
    input.value = '';
    input.setSelectionRange?.(0, 0);
    input.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'deleteContentBackward', data: null }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  })()`);
  if (!cleared) {
    throw new Error("GitHub search input could not be cleared");
  }
  await sleep(100);
  await client.send("Input.insertText", { text });
}

async function pressEnter(client) {
  const event = {
    key: "Enter",
    code: "Enter",
    windowsVirtualKeyCode: 13,
    nativeVirtualKeyCode: 13,
  };
  await client.send("Input.dispatchKeyEvent", { ...event, type: "keyDown" });
  await client.send("Input.dispatchKeyEvent", { ...event, type: "keyUp" });
}

async function pressSearchShortcut(client) {
  await client.evaluate("document.body?.focus()");
  const event = {
    key: "/",
    code: "Slash",
    text: "/",
    unmodifiedText: "/",
    windowsVirtualKeyCode: 191,
    nativeVirtualKeyCode: 191,
  };
  await client.send("Input.dispatchKeyEvent", { ...event, type: "keyDown" });
  await client.send("Input.dispatchKeyEvent", { ...event, type: "keyUp", text: "", unmodifiedText: "" });
}

async function focusSearchInput(client) {
  const focusVisibleInput = `(() => {
    const visible = (el) => {
      if (!el) return false;
      const style = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
    };
    const directInput = Array.from(document.querySelectorAll([
      '#query-builder-test',
      'input[name="q"]:not([type="hidden"])',
      'input[type="search"]',
      'input[aria-label*="Search" i]',
      'input[placeholder*="Search" i]'
    ].join(','))).find(visible);
    if (directInput) {
      directInput.focus();
      directInput.click();
      return true;
    }
    return false;
  })()`;

  const alreadyFocused = await client.evaluate(focusVisibleInput);
  if (alreadyFocused) {
    return true;
  }

  await pressSearchShortcut(client);
  try {
    return await client.waitFor(focusVisibleInput, 3000, 150);
  } catch {
    // Fall back to GitHub's visible header button when the "/" shortcut is disabled.
  }

  const focused = await client.evaluate(`(() => {
    const visible = (el) => {
      if (!el) return false;
      const style = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
    };
    const searchButton = Array.from(document.querySelectorAll([
      'button[aria-label*="Search" i]',
      'button[data-target*="qbsearch-input.inputButton"]',
      '[data-target*="qbsearch-input.inputButton"]',
      'button[placeholder*="Search" i]'
    ].join(','))).find(visible);
    if (searchButton) {
      searchButton.click();
      return true;
    }
    return false;
  })()`);
  if (!focused) {
    return false;
  }
  await sleep(350);
  return client.waitFor(focusVisibleInput, 3000, 150);
}

async function chooseRepositoryResults(client, query, args, timeoutMs = args.timeoutMs) {
  await client.waitFor(
    "location.hostname === 'github.com' && location.pathname.startsWith('/search')",
    timeoutMs
  );
  await waitForPageReady(client, timeoutMs, args.settleMs);
  const alreadyExactSearch = await client.evaluate(repositorySearchReadyExpression(query));
  if (alreadyExactSearch) {
    await waitForRepositoryResults(client, query, args.timeoutMs, args.settleMs);
    return;
  }
  const alreadyRepositories = await client.evaluate(`(() => {
    const url = new URL(location.href);
    return url.searchParams.get('type') === 'repositories';
  })()`);
  if (alreadyRepositories) {
    await navigateToRepositorySearch(client, query, args);
    return;
  }
  const clicked = await client.evaluate(`(() => {
    const links = Array.from(document.querySelectorAll('a[href]'));
    const repoTab = links.find((link) => {
      const text = (link.textContent || '').replace(/\\s+/g, ' ').trim().toLowerCase();
      const href = link.getAttribute('href') || '';
      return href.includes('type=repositories') || text === 'repositories' || text.startsWith('repositories ');
    });
    if (!repoTab) return false;
    repoTab.click();
    return true;
  })()`);
  if (clicked) {
    await client.waitFor(
      "location.hostname === 'github.com' && location.pathname.startsWith('/search') && new URL(location.href).searchParams.get('type') === 'repositories'",
      timeoutMs,
      200
    );
  }
  await navigateToRepositorySearch(client, query, args);
}

async function navigateToRepositorySearch(client, query, args) {
  await client.send("Page.navigate", { url: repositorySearchUrl(query) });
  await waitForRepositoryResults(client, query, args.timeoutMs, args.settleMs);
}

async function submitSearch(client, term, args) {
  const query = searchQueryFor(term);
  const focused = await focusSearchInput(client);
  if (!focused) {
    throw new Error("GitHub search input not found");
  }
  await clearAndType(client, query);
  await sleep(300);
  await pressEnter(client);
  try {
    await chooseRepositoryResults(client, query, args, Math.min(5000, args.timeoutMs));
  } catch {
    // GitHub's query builder can ignore synthetic Enter in CDP. Keep the typed
    // search visible, then move to the clean repository result URL.
    await navigateToRepositorySearch(client, query, args);
  }
  return query;
}

async function scrapePageOnce(port, term, args) {
  const page = await openTaskTarget(port, "https://github.com/trending?since=daily");
  const client = new CDPClient(page.webSocketDebuggerUrl);
  try {
    await client.connect();
    await client.send("Page.navigate", { url: "https://github.com/trending?since=daily" });
    await client.waitFor("location.hostname === 'github.com'", args.timeoutMs);
    await waitForPageReady(client, args.timeoutMs, args.settleMs);
    const query = await submitSearch(client, term, args);
    await waitForRepositoryResults(client, query, args.timeoutMs, args.settleMs);
    const raw = await client.evaluate(searchResultsExpression(args.limit));
    return { query, ...JSON.parse(raw || "{}") };
  } finally {
    await client.close();
    await closeTaskTarget(port, page.id, args);
  }
}

async function scrapePage(port, term, args) {
  const attempts = Math.max(1, Number(args.retries || 0) + 1);
  let lastError = null;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await scrapePageOnce(port, term, args);
    } catch (error) {
      lastError = error;
      if (attempt < attempts) {
        await sleep(Math.min(4000, 600 * attempt));
      }
    }
  }
  throw new Error(`term "${term}" failed after ${attempts} attempt(s): ${lastError?.message || lastError}`);
}

function searchResultsExpression(limit) {
  return toExpression(`(() => {
    const parseNumber = (value) => {
      const text = String(value || '').trim().toLowerCase().replace(/,/g, '');
      const match = text.match(/([0-9]+(?:\\.[0-9]+)?)\\s*([km])?/);
      if (!match) return 0;
      const number = Number.parseFloat(match[1]);
      const unit = match[2];
      if (unit === 'm') return Math.round(number * 1000000);
      if (unit === 'k') return Math.round(number * 1000);
      return Math.round(number);
    };
    const clean = (value) => String(value || '').replace(/\\s+/g, ' ').trim();
    const rootFor = (anchor) => {
      return anchor.closest('li.repo-list-item, div.Box-row, article, div[data-testid="results-list"] > div') ||
        anchor.closest('div') ||
        anchor.parentElement;
    };
	    const repoAnchors = Array.from(document.querySelectorAll('a[href]')).filter((anchor) => {
	      const href = anchor.getAttribute('href') || '';
	      if (!/^\\/[A-Za-z0-9_.-]+\\/[A-Za-z0-9_.-]+\\/?$/.test(href)) return false;
	      const first = href.replace(/^\\//, '').split('/')[0].toLowerCase();
	      if (['search', 'topics', 'collections', 'explore', 'marketplace', 'features', 'settings', 'notifications', 'pulls', 'issues'].includes(first)) return false;
      if (anchor.closest('header, nav, footer')) return false;
      const text = clean(anchor.textContent || '');
      return text.includes('/') || text.length > 1;
	    });
	    const seen = new Set();
	    const items = [];
	    const currentQuery = new URL(location.href).searchParams.get('q') || '';
	    for (const repoLink of repoAnchors) {
	      if (items.length >= ${limit}) break;
	      const href = repoLink.getAttribute('href') || '';
	      const path = href.replace(/^\\//, '').replace(/\\/$/, '');
      const key = path.toLowerCase();
      if (seen.has(key)) continue;
      seen.add(key);
      const root = rootFor(repoLink);
      if (!root) continue;
      const starLink = Array.from(root.querySelectorAll('a[href$="/stargazers"]')).find((anchor) => {
        return (anchor.getAttribute('href') || '').includes('/' + path + '/');
      });
      const forkLink = Array.from(root.querySelectorAll('a[href$="/forks"]')).find((anchor) => {
        return (anchor.getAttribute('href') || '').includes('/' + path + '/');
      });
	      const desc = Array.from(root.querySelectorAll('p, span'))
	        .map((node) => clean(node.textContent || ''))
	        .filter((text) => {
	          if (!text) return false;
	          if (text === path || text.includes('/' + path)) return false;
          if (/^(Updated|Built by|Sponsor|Forked from)\\b/i.test(text)) return false;
          if (/^[0-9,.]+\\s*[km]?$/i.test(text)) return false;
          if (text.length < 18) return false;
          return true;
	        })
	        .sort((a, b) => b.length - a.length)[0] || '';
	      const language = clean(root.querySelector('[itemprop="programmingLanguage"]')?.textContent || '');
	      const updatedNode = root.querySelector('relative-time[datetime], time-ago[datetime]');
	      const rootText = clean(root.textContent || '');
	      items.push({
	        full_name: path,
	        html_url: 'https://github.com/' + path,
	        description: desc,
	        language,
	        stars: parseNumber(starLink?.textContent || ''),
	        forks: parseNumber(forkLink?.textContent || ''),
	        pushed_at: updatedNode?.getAttribute('datetime') || '',
	        fork: /^Forked from\\b/i.test(rootText),
	        trending_today_stars: 0,
	        search_rank: items.length + 1,
	        search_query: currentQuery,
	        page_url: location.href,
	        source: 'github_search_cdp',
	      });
    }
    return {
      url: location.href,
      title: document.title,
      extracted_items: items.length,
      items,
    };
  })()`);
}

function trendingExpression(limit) {
  return toExpression(`(() => {
    const parseNumber = (value) => {
      const text = String(value || '').trim().toLowerCase().replace(/,/g, '');
      const match = text.match(/([0-9]+(?:\\.[0-9]+)?)\\s*([km])?/);
      if (!match) return 0;
      const number = Number.parseFloat(match[1]);
      const unit = match[2];
      if (unit === 'm') return Math.round(number * 1000000);
      if (unit === 'k') return Math.round(number * 1000);
      return Math.round(number);
    };
    const clean = (value) => String(value || '').replace(/\\s+/g, ' ').trim();
    const articles = Array.from(document.querySelectorAll('article.Box-row, article')).slice(0, ${limit});
    const items = articles.map((article) => {
      const repoLink = Array.from(article.querySelectorAll('h2 a[href], a.Link[href]')).find((anchor) => {
        const href = anchor.getAttribute('href') || '';
        return /^\\/[A-Za-z0-9_.-]+\\/[A-Za-z0-9_.-]+\\/?$/.test(href);
      });
      if (!repoLink) return null;
      const path = (repoLink.getAttribute('href') || '').replace(/^\\//, '').replace(/\\/$/, '');
      const starLink = Array.from(article.querySelectorAll('a[href$="/stargazers"]')).find((anchor) => {
        return (anchor.getAttribute('href') || '').includes('/' + path + '/');
      });
      const forkLink = Array.from(article.querySelectorAll('a[href$="/forks"]')).find((anchor) => {
        return (anchor.getAttribute('href') || '').includes('/' + path + '/');
      });
      const text = clean(article.textContent);
      const todayMatch = text.match(/([0-9,.]+\\s*[km]?)\\s+stars?\\s+today/i);
      const desc = Array.from(article.querySelectorAll('p'))
        .map((node) => clean(node.textContent || ''))
        .filter((text) => {
          if (!text) return false;
          if (text.startsWith('This will remove')) return false;
          if (text.includes('{{ repoNameWithOwner }}')) return false;
          if (text.includes('There was an error while loading')) return false;
          if (text.length < 12) return false;
          return true;
        })
        .sort((a, b) => b.length - a.length)[0] || '';
      const language = clean(article.querySelector('[itemprop="programmingLanguage"]')?.textContent || '');
      return {
        full_name: path,
        html_url: 'https://github.com/' + path,
        description: desc,
        language,
        stars: parseNumber(starLink?.textContent || ''),
        forks: parseNumber(forkLink?.textContent || ''),
        trending_today_stars: todayMatch ? parseNumber(todayMatch[1]) : 0,
        page_url: location.href,
      };
    }).filter(Boolean);
    return {
      url: location.href,
      title: document.title,
      extracted_items: items.length,
      items,
    };
  })()`);
}

function mergeRepo(existing, incoming) {
  if (!existing) {
    return { ...incoming, source_urls: [incoming.page_url].filter(Boolean) };
  }
  return {
    ...existing,
    ...Object.fromEntries(Object.entries(incoming).filter(([, value]) => value !== "" && value !== 0 && value != null)),
    stars: Math.max(Number(existing.stars || 0), Number(incoming.stars || 0)),
    trending_today_stars: Math.max(Number(existing.trending_today_stars || 0), Number(incoming.trending_today_stars || 0)),
    source_urls: Array.from(new Set([...(existing.source_urls || []), incoming.page_url].filter(Boolean))),
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const repos = new Map();
  const errors = [];
  try {
    for (const term of args.terms) {
      try {
        const result = await scrapePage(args.port, term, args);
        for (const item of result.items || []) {
          const key = String(item.full_name || "").toLowerCase();
          if (!key) {
            continue;
          }
          repos.set(key, mergeRepo(repos.get(key), item));
        }
      } catch (error) {
        errors.push({ term, error: String(error?.message || error) });
      }
    }
  } finally {
    await cleanupTaskTargets(args.port, args);
  }
  process.stdout.write(
    JSON.stringify(
      {
        ok: errors.length < args.terms.length,
        source: "github_search_cdp",
        candidate_count: repos.size,
        items: Array.from(repos.values()),
        errors,
      },
      null,
      2
    ) + "\n"
  );
}

main().catch((error) => {
  process.stderr.write(String(error?.stack || error) + "\n");
  process.exit(1);
});
