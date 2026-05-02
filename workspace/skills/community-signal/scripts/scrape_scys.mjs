#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { setTimeout as sleep } from "node:timers/promises";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const BASE_DIR = dirname(SCRIPT_DIR);
const PLATFORM_CONFIG_PATH = join(BASE_DIR, "config", "platforms.yaml");

function parseArgs(argv) {
  const args = {
    entryUrl: "",
    limit: 10,
    details: false,
    expandFeishu: false,
    maxComments: 5,
    port: 9223,
    timeoutMs: 15000,
    keepTabs: false,
    feedFilter: "全部",
    sortValue: "",
    humanPacing: true,
    humanMinDelayMs: 800,
    humanMaxDelayMs: 2200,
    detailMinDelayMs: 3000,
    detailMaxDelayMs: 7000,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const part = argv[i];
    if (part === "--entry-url") {
      args.entryUrl = argv[++i] || "";
    } else if (part === "--limit") {
      args.limit = Number.parseInt(argv[++i] || "10", 10);
    } else if (part === "--details") {
      args.details = true;
    } else if (part === "--expand-feishu") {
      args.expandFeishu = true;
    } else if (part === "--max-comments") {
      args.maxComments = Number.parseInt(argv[++i] || "5", 10);
    } else if (part === "--port") {
      args.port = Number.parseInt(argv[++i] || "9223", 10);
    } else if (part === "--timeout-ms") {
      args.timeoutMs = Number.parseInt(argv[++i] || "15000", 10);
    } else if (part === "--keep-tabs") {
      args.keepTabs = true;
    } else if (part === "--feed-filter") {
      args.feedFilter = argv[++i] || "全部";
    } else if (part === "--sort-value") {
      args.sortValue = argv[++i] || "";
    } else if (part === "--fast") {
      args.humanPacing = false;
    } else if (part === "--human-min-delay-ms") {
      args.humanMinDelayMs = Number.parseInt(argv[++i] || "800", 10);
    } else if (part === "--human-max-delay-ms") {
      args.humanMaxDelayMs = Number.parseInt(argv[++i] || "2200", 10);
    } else if (part === "--detail-min-delay-ms") {
      args.detailMinDelayMs = Number.parseInt(argv[++i] || "3000", 10);
    } else if (part === "--detail-max-delay-ms") {
      args.detailMaxDelayMs = Number.parseInt(argv[++i] || "7000", 10);
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
      "Usage: node scrape_scys.mjs [options]",
      "",
      "Options:",
      "  --entry-url <url>       Feed entry url, defaults to platforms.scys.base_url",
      "  --limit <n>             Number of homepage cards to extract, default 10",
      "  --details               Open detail pages for cards that expose articleDetail links",
      "  --expand-feishu         Follow Feishu wiki links exposed by scys detail pages",
      "  --max-comments <n>      Max detail comments to keep, default 5",
      "  --port <n>              Chrome remote debugging port, default 9223",
      "  --timeout-ms <n>        Per page wait timeout, default 15000",
      "  --keep-tabs             Keep temporary browser tabs open",
      "  --feed-filter <text>    Normalize homepage filter before extraction, default 全部",
      "  --sort-value <text>     Normalize homepage sort before extraction",
      "  --fast                  Disable human-paced delays",
      "  --human-min-delay-ms <n> Minimum delay between human-like actions, default 800",
      "  --human-max-delay-ms <n> Maximum delay between human-like actions, default 2200",
      "  --detail-min-delay-ms <n> Minimum delay before opening each detail/doc page, default 3000",
      "  --detail-max-delay-ms <n> Maximum delay before opening each detail/doc page, default 7000",
    ].join("\n") + "\n"
  );
}

function randomInt(min, max) {
  const low = Math.max(0, Math.floor(Number(min) || 0));
  const high = Math.max(low, Math.floor(Number(max) || low));
  return low + Math.floor(Math.random() * (high - low + 1));
}

async function humanPause(args, minMs = args.humanMinDelayMs, maxMs = args.humanMaxDelayMs) {
  if (!args.humanPacing) {
    return;
  }
  await sleep(randomInt(minMs, maxMs));
}

async function humanScrollPage(client, args) {
  if (!args.humanPacing) {
    await client.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'instant' }); true");
    return;
  }
  const steps = randomInt(2, 4);
  for (let index = 0; index < steps; index += 1) {
    const distance = randomInt(260, 720);
    await client.evaluate(`window.scrollBy({ top: ${distance}, left: 0, behavior: 'smooth' }); true`);
    await humanPause(args, 900, 2400);
  }
}

async function loadFeedCards(client, args, targetCount) {
  const maxRounds = Math.min(12, Math.max(3, Math.ceil(targetCount / 10)));
  let lastCount = 0;
  let stableRounds = 0;
  for (let round = 0; round < maxRounds; round += 1) {
    const count = Number(
      await client.evaluate("document.querySelectorAll('.post-list-container .compact-card').length")
    );
    if (count >= targetCount) {
      return;
    }
    if (count <= lastCount) {
      stableRounds += 1;
    } else {
      stableRounds = 0;
    }
    if (stableRounds >= 2) {
      return;
    }
    lastCount = count;
    await humanScrollPage(client, args);
    await client.evaluate("document.querySelectorAll('.post-list-container .compact-card').length");
  }
}

async function loadPlatformConfig() {
  const raw = await readFile(PLATFORM_CONFIG_PATH, "utf8");
  const parsed = JSON.parse(raw);
  const platform = parsed?.platforms?.scys;
  if (!platform) {
    throw new Error(`missing scys config in ${PLATFORM_CONFIG_PATH}`);
  }
  return platform;
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
    const message = JSON.stringify({ id, method, params });
    const result = new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject, method });
    });
    this.ws.send(message);
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

function toAsyncExpression(source) {
  return `(async () => JSON.stringify(await ${source}))()`;
}

function normalizeExpr(value) {
  return JSON.stringify(value);
}

async function withTempPage(port, url, keepTabs, run) {
  const page = await openTarget(port, url);
  const client = new CDPClient(page.webSocketDebuggerUrl);
  try {
    await client.connect();
    await run(page, client);
  } finally {
    await client.close();
    if (!keepTabs) {
      await closeTarget(port, page.id);
    }
  }
}

function feedExpression(limit) {
  return toAsyncExpression(`(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const copiedLinks = [];
    try {
      Object.defineProperty(navigator, 'clipboard', {
        value: {
          writeText: async (text) => {
            copiedLinks.push(String(text || ''));
            return true;
          },
        },
        configurable: true,
      });
    } catch (_error) {
      try {
        navigator.clipboard.writeText = async (text) => {
          copiedLinks.push(String(text || ''));
          return true;
        };
      } catch (_innerError) {
        // Clipboard interception is best-effort; cards with anchors still work.
      }
    }
    const dispatchClick = (node, includeHover = false) => {
      if (!node) {
        return false;
      }
      const rect = node.getBoundingClientRect();
      const opts = {
        bubbles: true,
        cancelable: true,
        view: window,
        clientX: rect.left + rect.width / 2,
        clientY: rect.top + rect.height / 2,
      };
      const events = includeHover
        ? ['pointerenter', 'mouseover', 'mousemove', 'pointerdown', 'mousedown', 'mouseup', 'click']
        : ['pointerdown', 'mousedown', 'mouseup', 'click'];
      events.forEach((type) => {
        node.dispatchEvent(new MouseEvent(type, opts));
      });
      return true;
    };
    const copyPostUrl = async (card) => {
      const before = copiedLinks.length;
      const more = card.querySelector('.else-operation') || card.querySelector('.post-right-actions');
      dispatchClick(more, true);
      await sleep(180);
      const copyItem = Array.from(card.querySelectorAll('.popper .item')).find((node) => {
        return (node.textContent || '').trim() === '复制链接';
      });
      dispatchClick(copyItem);
      await sleep(220);
      for (let index = copiedLinks.length - 1; index >= before; index -= 1) {
        const url = copiedLinks[index] || '';
        if (/^https?:\\/\\//.test(url)) {
          return url;
        }
      }
      return '';
    };
    const cards = Array.from(document.querySelectorAll('.post-list-container .compact-card')).slice(0, ${limit});
    const feedSort = document.querySelector('.arco-select-view-value')?.textContent?.trim() || '';
    const secondaryFilter = document.querySelector('.vc-secondary-filter .filter-item.active')?.textContent?.trim() || '';
    const modeSelector = document.querySelector('.mode-switch-v3 .trigger-label, .mode-switch-v3, .mode-selector')?.textContent?.trim() || '';
    const items = [];
    for (const [index, card] of cards.entries()) {
      const detailAnchor = Array.from(card.querySelectorAll('a[href]')).find((anchor) => {
        const href = anchor.getAttribute('href') || '';
        return href.includes('/articleDetail/');
      });
      let detailUrl = detailAnchor ? new URL(detailAnchor.getAttribute('href'), location.origin).href : '';
      const links = Array.from(card.querySelectorAll('a[href]')).map((anchor) => new URL(anchor.getAttribute('href'), location.origin).href);
      let copiedPostUrl = '';
      if (!detailUrl) {
        copiedPostUrl = await copyPostUrl(card);
        if (copiedPostUrl.includes('/articleDetail/')) {
          detailUrl = copiedPostUrl;
        }
      }
      const mergedLinks = Array.from(new Set([detailUrl, copiedPostUrl, ...links].filter(Boolean)));
      items.push({
        index,
        title: card.querySelector('.title-text')?.textContent?.trim() || '',
        preview: card.querySelector('.content-preview')?.textContent?.trim() || '',
        author: card.querySelector('.user-name')?.textContent?.trim() || '',
        published_at_text: (card.querySelector('.time-text')?.textContent || '').replace(/^\\s*·\\s*/, '').trim(),
        tags: Array.from(card.querySelectorAll('.tag-item')).map((node) => node.textContent?.trim()).filter(Boolean),
        detail_url: detailUrl,
        links: mergedLinks,
        copied_post_url: copiedPostUrl,
        has_detail_url: Boolean(detailUrl),
      });
    }
    return {
      url: location.href,
      title: document.title,
      feed_sort: feedSort,
      secondary_filter: secondaryFilter,
      mode_selector: modeSelector,
      total_cards: document.querySelectorAll('.post-list-container .compact-card').length,
      items,
    };
  })()`);
}

async function ensureFeedFilter(client, desired, timeoutMs, args) {
  if (!desired) {
    return;
  }
  const current = await client.evaluate(
    "(document.querySelector('.vc-secondary-filter .filter-item.active')?.textContent || '').trim()"
  );
  if (current === desired) {
    return;
  }
  const clicked = await client.evaluate(`(() => {
    const target = Array.from(document.querySelectorAll('.vc-secondary-filter .filter-item')).find((node) => {
      return (node.textContent || '').trim() === ${normalizeExpr(desired)};
    });
    if (!target) {
      return false;
    }
    ['pointerdown', 'mousedown', 'mouseup', 'click'].forEach((type) => {
      target.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true, view: window }));
    });
    return true;
  })()`);
  if (!clicked) {
    throw new Error(`unable to switch homepage filter to ${desired}`);
  }
  await humanPause(args);
  await client.waitFor(
    `(document.querySelector('.vc-secondary-filter .filter-item.active')?.textContent || '').trim() === ${normalizeExpr(desired)}`,
    Math.min(timeoutMs, 5000),
    300
  );
  await client.waitFor("document.querySelectorAll('.post-list-container .compact-card').length > 0", timeoutMs, 400);
  await humanPause(args);
}

async function ensureSortValue(client, desired, timeoutMs, args) {
  if (!desired) {
    return;
  }
  const current = await client.evaluate(
    "(document.querySelector('.arco-select-view-value')?.textContent || '').trim()"
  );
  if (current === desired) {
    return;
  }
  const opened = await client.evaluate(`(() => {
    const trigger = document.querySelector('.arco-select-view');
    if (!trigger) {
      return false;
    }
    ['pointerdown', 'mousedown', 'mouseup', 'click'].forEach((type) => {
      trigger.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true, view: window }));
    });
    return true;
  })()`);
  if (!opened) {
    throw new Error(`unable to open sort selector for ${desired}`);
  }
  await humanPause(args);
  await client.waitFor("document.querySelectorAll('.arco-select-option').length > 0", 5000, 250);
  const selected = await client.evaluate(`(() => {
    const option = Array.from(document.querySelectorAll('.arco-select-option')).find((node) => {
      return (node.textContent || '').trim() === ${normalizeExpr(desired)};
    });
    if (!option) {
      return false;
    }
    ['pointerdown', 'mousedown', 'mouseup', 'click'].forEach((type) => {
      option.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true, view: window }));
    });
    return true;
  })()`);
  if (!selected) {
    throw new Error(`unable to select sort value ${desired}`);
  }
  await humanPause(args);
  await client.waitFor(
    `(document.querySelector('.arco-select-view-value')?.textContent || '').trim() === ${normalizeExpr(desired)}`,
    timeoutMs,
    300
  );
  await client.waitFor("document.querySelectorAll('.post-list-container .compact-card').length > 0", timeoutMs, 400);
  await humanPause(args);
}

function detailExpression(maxComments) {
  return toExpression(`(() => {
    const normalize = (value) => (value || '').replace(/\\s+/g, ' ').trim();
    const comments = Array.from(document.querySelectorAll('.comment-list-box .comment-block'))
      .slice(0, ${maxComments})
      .map((block) => ({
        author: normalize(block.querySelector('.block-top .user-name')?.textContent),
        content: normalize(block.querySelector('.block-top .content')?.textContent),
        date: normalize(block.querySelector('.block-bottom .date')?.textContent),
        likes: normalize(block.querySelector('.like-item span')?.textContent),
        is_reply: block.classList.contains('reply-item'),
      }))
      .filter((item) => item.author || item.content);
    return {
      url: location.href,
      title: normalize(document.querySelector('.header-entity-title')?.textContent) || normalize(document.querySelector('.post-title')?.textContent),
      author: normalize(document.querySelector('.post-item-top .name')?.textContent),
      published_at: normalize(document.querySelector('.post-item-top .date')?.textContent),
      tags: Array.from(document.querySelectorAll('.tag-item')).map((node) => normalize(node.textContent)).filter(Boolean),
      content: normalize(document.querySelector('.post-content')?.innerText || document.querySelector('.post-content')?.textContent),
      external_links: Array.from(document.querySelectorAll('.post-content a[href]')).map((anchor) => anchor.href),
      stats: Array.from(document.querySelectorAll('.stats-card .stat-item')).map((node) => normalize(node.textContent)).filter(Boolean),
      comments,
      comments_total: document.querySelectorAll('.comment-list-box .comment-block').length,
    };
  })()`);
}

async function extractFeed(port, args) {
  let payload = null;
  await withTempPage(port, args.entryUrl, args.keepTabs, async (_page, client) => {
    await client.waitFor("document.readyState === 'complete'", args.timeoutMs, 250);
    await client.waitFor("document.querySelectorAll('.post-list-container .compact-card').length > 0", args.timeoutMs, 400);
    await humanPause(args);
    await ensureFeedFilter(client, args.feedFilter, args.timeoutMs, args);
    await ensureSortValue(client, args.sortValue, args.timeoutMs, args);
    await loadFeedCards(client, args, args.limit);
    payload = JSON.parse(await client.evaluate(feedExpression(args.limit)));
  });
  return payload;
}

async function extractDetail(port, url, args) {
  let payload = null;
  await withTempPage(port, url, args.keepTabs, async (_page, client) => {
    await client.waitFor(
      "document.readyState === 'complete' && document.body && document.body.innerText.length > 200",
      args.timeoutMs,
      300
    );
    await client.waitFor(
      "Boolean((document.querySelector('.post-content')?.innerText || '').trim().length > 30)",
      args.timeoutMs,
      400
    );
    await humanPause(args, 1600, 3200);
    await humanScrollPage(client, args);
    try {
      await client.waitFor("Boolean(document.querySelector('.comment-list-box'))", 5000, 400);
    } catch (_error) {
      // Some articles expose正文 but no comment box; return detail payload anyway.
    }
    await humanPause(args, 1800, 3600);
    payload = JSON.parse(await client.evaluate(detailExpression(args.maxComments)));
  });
  return payload;
}

function looksLikeFeishu(url) {
  try {
    const parsed = new URL(url);
    return /feishu\.cn$/.test(parsed.hostname) || parsed.hostname.includes("larksuite.com");
  } catch (_error) {
    return false;
  }
}

function feishuStepExpression() {
  return toExpression(`(() => {
    const normalize = (value) => (value || '').replace(/\\u200b/g, '').replace(/\\s+/g, ' ').trim();
    const candidates = Array.from(document.querySelectorAll('*'))
      .filter((el) => {
        const style = getComputedStyle(el);
        return /(auto|scroll)/.test(style.overflowY) && el.scrollHeight > el.clientHeight + 100;
      })
      .sort((a, b) => b.scrollHeight - a.scrollHeight);
    const scroller = candidates[0] || null;
    const blocks = Array.from(document.querySelectorAll('.block.docx-text-block')).map((node) => normalize(node.innerText)).filter(Boolean);
    const title = normalize(document.querySelector('.note-title__input-text')?.textContent)
      || normalize(document.querySelector('.doc-title')?.textContent)
      || normalize(document.querySelector('.note-title')?.textContent)
      || normalize(document.title.replace(/\\s+-\\s+飞书云文档$/, ''));
    const modifiedAt = normalize(document.querySelector('.doc-info-group-time')?.innerText)
      || normalize(document.querySelector('.note-title__info')?.innerText);
    const toc = Array.from(document.querySelectorAll('.catalogue__item-title'))
      .map((node) => normalize(node.innerText))
      .filter(Boolean);
    if (!scroller) {
      return {
        title,
        modified_at: modifiedAt,
        toc,
        visible_blocks: blocks,
        scroll_top: 0,
        client_height: 0,
        scroll_height: 0,
        done: true,
      };
    }
    const maxTop = Math.max(0, scroller.scrollHeight - scroller.clientHeight);
    const nextTop = Math.min(scroller.scrollTop + scroller.clientHeight * 0.9, maxTop);
    scroller.scrollTop = nextTop;
    return {
      title,
      modified_at: modifiedAt,
      toc,
      visible_blocks: blocks,
      scroll_top: scroller.scrollTop,
      client_height: scroller.clientHeight,
      scroll_height: scroller.scrollHeight,
      done: nextTop >= maxTop - 20,
    };
  })()`);
}

async function extractFeishuDoc(port, url, args) {
  const seenBlocks = new Set();
  let title = "";
  let modifiedAt = "";
  let toc = [];
  await withTempPage(port, url, args.keepTabs, async (_page, client) => {
    await client.waitFor(
      "document.readyState === 'complete' && document.body && document.body.innerText.length > 100",
      args.timeoutMs,
      300
    );
    await client.waitFor("document.querySelectorAll('.block.docx-text-block').length > 2", args.timeoutMs, 400);

    let lastTop = -1;
    let stagnantRounds = 0;
    for (let round = 0; round < 30; round += 1) {
      const step = JSON.parse(await client.evaluate(feishuStepExpression()));
      title ||= step.title || "";
      modifiedAt ||= step.modified_at || "";
      if (!toc.length && Array.isArray(step.toc)) {
        toc = step.toc;
      }
      for (const block of step.visible_blocks || []) {
        if (block) {
          seenBlocks.add(block);
        }
      }
      if (step.scroll_top === lastTop) {
        stagnantRounds += 1;
      } else {
        stagnantRounds = 0;
      }
      lastTop = step.scroll_top;
      if (step.done || stagnantRounds >= 3) {
        await humanPause(args, 700, 1400);
        const finalStep = JSON.parse(await client.evaluate(feishuStepExpression()));
        for (const block of finalStep.visible_blocks || []) {
          if (block) {
            seenBlocks.add(block);
          }
        }
        title ||= finalStep.title || "";
        modifiedAt ||= finalStep.modified_at || "";
        if (!toc.length && Array.isArray(finalStep.toc)) {
          toc = finalStep.toc;
        }
        break;
      }
      await humanPause(args, 700, 1600);
    }
  });

  const contentBlocks = Array.from(seenBlocks);
  return {
    url,
    title,
    modified_at: modifiedAt,
    toc,
    block_count: contentBlocks.length,
    content: contentBlocks.join("\n\n"),
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const platform = await loadPlatformConfig();
  if (!args.entryUrl) {
    args.entryUrl = platform.base_url;
  }
  if (!Number.isFinite(args.limit) || args.limit <= 0) {
    throw new Error("--limit must be a positive integer");
  }
  if (!Number.isFinite(args.maxComments) || args.maxComments <= 0) {
    throw new Error("--max-comments must be a positive integer");
  }

  const feed = await extractFeed(args.port, args);
  const items = [];
  for (const item of feed.items) {
    if (!args.details || !item.detail_url) {
      items.push(item);
      continue;
    }
    try {
      await humanPause(args, args.detailMinDelayMs, args.detailMaxDelayMs);
      const detail = await extractDetail(args.port, item.detail_url, args);
      const feishuUrl = (detail.external_links || []).find((link) => looksLikeFeishu(link)) || "";
      if (args.expandFeishu && feishuUrl) {
        detail.feishu_url = feishuUrl;
        await humanPause(args, args.detailMinDelayMs, args.detailMaxDelayMs);
        detail.feishu_doc = await extractFeishuDoc(args.port, feishuUrl, args);
      }
      items.push({
        ...item,
        detail,
      });
    } catch (error) {
      items.push({
        ...item,
        detail_error: error instanceof Error ? error.message : String(error),
      });
    }
  }

  const result = {
    ok: true,
    platform: "scys",
    scanned_at: new Date().toISOString(),
    entry_url: args.entryUrl,
    feed_filter: args.feedFilter,
    feed_sort: feed.feed_sort,
    secondary_filter: feed.secondary_filter,
    mode_selector: feed.mode_selector,
    total_cards: feed.total_cards,
    extracted_items: items.length,
    detail_ready_items: items.filter((item) => item.detail?.title || item.detail?.content).length,
    feishu_ready_items: items.filter((item) => item.detail?.feishu_doc?.content).length,
    items,
  };
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

main().catch((error) => {
  const payload = {
    ok: false,
    error: error instanceof Error ? error.message : String(error),
  };
  process.stderr.write(`${JSON.stringify(payload, null, 2)}\n`);
  process.exit(1);
});
