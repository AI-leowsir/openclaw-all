from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
STATE_DIR = BASE_DIR / "state"

SCRAPE_HISTORY_PATH = STATE_DIR / "scrape_history.json"
DELIVERY_HISTORY_PATH = STATE_DIR / "delivery_history.json"
DAILY_STATS_PATH = STATE_DIR / "daily_stats.json"
DIGEST_CANDIDATES_PATH = STATE_DIR / "digest_candidates.json"
RETRY_QUEUE_PATH = STATE_DIR / "retry_queue.json"

DEFAULT_SETTINGS = {
    "timezone": "Asia/Shanghai",
    "push_channel": "feishu",
    "push_group_id": "",
    "push_backend": "openclaw_cli",
    "digest_time": "17:00",
    "digest_max_items": 5,
    "digest_min_score": 7,
    "send_empty_digest": False,
    "realtime_push_score": 99,
    "realtime_max_per_day": 0,
    "realtime_cooldown_minutes": 20,
    "max_scrape_time_per_target": 600,
    "max_scrape_time_total": 1800,
    "default_scrape_interval_hours": 8,
    "temp_target_duration_days": 30,
    "memory_file": "~/.openclaw/workspace/MEMORY.md",
    "openclaw_binary": "openclaw",
}


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return default
    return json.loads(text)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def load_settings() -> dict[str, Any]:
    data = DEFAULT_SETTINGS | read_json(CONFIG_DIR / "settings.yaml", {})
    return data


def load_targets() -> dict[str, Any]:
    return read_json(
        CONFIG_DIR / "targets.yaml",
        {"person_targets": {"core_targets": [], "temporary_targets": []}, "monitoring_targets": []},
    )


def save_targets(data: dict[str, Any]) -> None:
    write_json(CONFIG_DIR / "targets.yaml", data)


def load_scrape_history() -> dict[str, Any]:
    return read_json(SCRAPE_HISTORY_PATH, {"items": {}, "targets": {}})


def save_scrape_history(data: dict[str, Any]) -> None:
    write_json(SCRAPE_HISTORY_PATH, data)


def load_delivery_history() -> dict[str, Any]:
    return read_json(DELIVERY_HISTORY_PATH, {"items": {}})


def save_delivery_history(data: dict[str, Any]) -> None:
    write_json(DELIVERY_HISTORY_PATH, data)


def load_daily_stats() -> dict[str, Any]:
    return read_json(DAILY_STATS_PATH, {"days": {}})


def save_daily_stats(data: dict[str, Any]) -> None:
    write_json(DAILY_STATS_PATH, data)


def load_digest_candidates() -> dict[str, Any]:
    return read_json(DIGEST_CANDIDATES_PATH, {"days": {}})


def save_digest_candidates(data: dict[str, Any]) -> None:
    write_json(DIGEST_CANDIDATES_PATH, data)


def load_retry_queue() -> dict[str, Any]:
    return read_json(RETRY_QUEUE_PATH, {"items": []})


def save_retry_queue(data: dict[str, Any]) -> None:
    write_json(RETRY_QUEUE_PATH, data)


def expand_user(path: str) -> str:
    return str(Path(path).expanduser())


def get_tz(settings: dict[str, Any]) -> ZoneInfo:
    return ZoneInfo(settings.get("timezone", DEFAULT_SETTINGS["timezone"]))


def now_dt(settings: dict[str, Any]) -> datetime:
    return datetime.now(tz=get_tz(settings))


def now_iso(settings: dict[str, Any]) -> str:
    return now_dt(settings).isoformat(timespec="seconds")


def today_key(settings: dict[str, Any]) -> str:
    return now_dt(settings).date().isoformat()


def parse_day(value: str, settings: dict[str, Any]) -> str:
    if value == "today":
        return today_key(settings)
    return value


def sha256_hex(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-") or "item"


def normalize_topics(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def normalize_summary(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


NOISY_QUERY_KEYS = {
    "from",
    "ref",
    "source",
    "share_source",
    "share_from",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
}


def normalize_url(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    try:
        parsed = urlsplit(raw)
    except ValueError:
        return raw
    if not parsed.scheme or not parsed.netloc:
        return raw

    query_pairs = [
        (key, val)
        for key, val in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in NOISY_QUERY_KEYS
    ]
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    query = urlencode(query_pairs, doseq=True)
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, query, ""))


def merge_source_urls(*values: Any) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value:
            continue
        items = value if isinstance(value, list) else [value]
        for item in items:
            normalized = normalize_url(item)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            merged.append(normalized)
    return merged


def url_rank(url: str) -> tuple[int, int, str]:
    normalized = normalize_url(url)
    if not normalized:
        return (99, 99, "")
    parsed = urlsplit(normalized)
    host = parsed.netloc.lower()
    path = parsed.path or "/"
    if "feishu.cn" in host or "larksuite" in host:
        return (0, len(path), normalized)
    if host == "github.com":
        parts = [part for part in path.split("/") if part]
        first = parts[0].lower() if parts else ""
        if len(parts) == 2 and first not in {"trending", "topics", "collections", "explore", "search"}:
            return (1, 0, normalized)
        if first in {"trending", "topics", "collections", "explore", "search"}:
            return (5, len(path), normalized)
    if "/articledetail/" in path.lower():
        return (1, len(path), normalized)
    if path not in {"", "/"}:
        return (2, len(path), normalized)
    return (3, len(path), normalized)


def candidate_urls_for(item: dict[str, Any]) -> list[str]:
    return merge_source_urls(
        item.get("source_urls"),
        item.get("canonical_url"),
        item.get("url"),
        item.get("detail_url"),
        item.get("feishu_url"),
    )


def canonical_url_for(item: dict[str, Any]) -> str:
    urls = candidate_urls_for(item)
    if not urls:
        return ""
    return min(urls, key=url_rank)


def content_id_for(item: dict[str, Any]) -> str:
    canonical_url = canonical_url_for(item)
    if canonical_url:
        return sha256_hex(canonical_url)
    parts = [
        item.get("title", ""),
        item.get("author", ""),
        item.get("platform", ""),
        item.get("source_name", ""),
    ]
    published_at = str(item.get("published_at", "")).strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}", published_at):
        parts.append(published_at)
    preview = str(item.get("preview", "")).strip()
    if preview:
        parts.append(preview[:200])
    return sha256_hex("|".join(parts))


def target_id(mode: str, platform: str, name: str) -> str:
    return f"{mode}:{platform}:{slugify(name)}"


def person_target_id(target: dict[str, Any]) -> str:
    return target_id("person", target.get("platform", "unknown"), target.get("name", "unnamed"))


def monitor_target_id(target: dict[str, Any]) -> str:
    return target_id("monitor", target.get("platform", "unknown"), target.get("name", "unnamed"))


def normalize_item(payload: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    item = dict(payload)
    item["title"] = str(item.get("title", "")).strip()
    item["author"] = str(item.get("author", "")).strip()
    item["url"] = normalize_url(item.get("url", ""))
    item["platform"] = str(item.get("platform", "")).strip()
    item["source_mode"] = str(item.get("source_mode", "community")).strip() or "community"
    item["source_name"] = str(item.get("source_name", "")).strip()
    item["published_at"] = str(item.get("published_at", "")).strip() or now_iso(settings)
    item["score"] = int(item.get("score", 0))
    item["one_liner"] = str(item.get("one_liner", "")).strip()
    item["summary"] = normalize_summary(item.get("summary"))
    item["reason"] = str(item.get("reason", "")).strip()
    item["topics"] = normalize_topics(item.get("topics"))
    item["verdict"] = str(item.get("verdict", "")).strip()
    item["source_urls"] = candidate_urls_for(item)
    item["canonical_url"] = normalize_url(item.get("canonical_url")) or canonical_url_for(item)
    if item["canonical_url"]:
        item["source_urls"] = merge_source_urls(item["canonical_url"], item["source_urls"])
    if not item["url"]:
        item["url"] = item["canonical_url"]
    item["content_id"] = item.get("content_id") or content_id_for(item)
    item["processed_at"] = now_iso(settings)
    item["day"] = str(item.get("day") or today_key(settings)).strip() or today_key(settings)
    if not item["title"]:
        raise ValueError("item.title is required")
    if not item["platform"]:
        raise ValueError("item.platform is required")
    if not item["source_name"]:
        item["source_name"] = item["author"] or item["platform"]
    return item


def ensure_day(stats: dict[str, Any], day: str) -> dict[str, Any]:
    days = stats.setdefault("days", {})
    return days.setdefault(
        day,
        {
            "scanned": 0,
            "feed_scanned": 0,
            "detail_ready": 0,
            "full_doc_ready": 0,
            "scored": 0,
            "scan_errors": 0,
            "coverage_warnings": 0,
            "ignored": 0,
            "duplicates": 0,
            "digest_candidates": 0,
            "digest_sent": 0,
            "realtime_sent": 0,
        },
    )


def sort_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(item: dict[str, Any]) -> tuple[Any, ...]:
        return (
            int(item.get("score", 0)),
            1 if item.get("source_mode") == "person" else 0,
            item.get("published_at", ""),
        )

    return sorted(items, key=key, reverse=True)


def push_group_target(settings: dict[str, Any]) -> str:
    target = str(settings.get("push_group_id", "")).strip()
    if not target:
        raise ValueError("config/settings.yaml is missing push_group_id")
    return target


def known_content_id(scrape_history: dict[str, Any], item: dict[str, Any]) -> str:
    aliases = scrape_history.get("url_aliases", {})
    for url in candidate_urls_for(item):
        content_id = aliases.get(url)
        if content_id:
            return content_id
    content_id = str(item.get("content_id", "")).strip()
    if content_id and content_id in scrape_history.get("items", {}):
        return content_id
    return ""


def upsert_scrape_item(
    scrape_history: dict[str, Any], item: dict[str, Any], settings: dict[str, Any]
) -> tuple[bool, dict[str, Any]]:
    items = scrape_history.setdefault("items", {})
    aliases = scrape_history.setdefault("url_aliases", {})
    resolved_id = known_content_id(scrape_history, item)
    if resolved_id:
        item["content_id"] = resolved_id

    now = now_iso(settings)
    record = items.get(item["content_id"])
    if record is None:
        record = {
            "title": item["title"],
            "url": item.get("url", ""),
            "canonical_url": item.get("canonical_url", ""),
            "source_urls": item.get("source_urls", []),
            "platform": item["platform"],
            "source_mode": item["source_mode"],
            "source_name": item["source_name"],
            "first_seen_at": now,
            "last_seen_at": now,
        }
        items[item["content_id"]] = record
        was_seen = False
    else:
        was_seen = True
        record["title"] = record.get("title") or item["title"]
        record["url"] = item.get("url") or record.get("url", "")
        record["platform"] = record.get("platform") or item["platform"]
        record["source_mode"] = record.get("source_mode") or item["source_mode"]
        record["source_name"] = record.get("source_name") or item["source_name"]
        record["last_seen_at"] = now

    merged_urls = merge_source_urls(
        record.get("source_urls", []),
        item.get("source_urls", []),
        record.get("canonical_url", ""),
        item.get("canonical_url", ""),
        record.get("url", ""),
        item.get("url", ""),
    )
    record["source_urls"] = merged_urls
    record["canonical_url"] = canonical_url_for(
        {
            "canonical_url": item.get("canonical_url") or record.get("canonical_url"),
            "source_urls": merged_urls,
            "url": item.get("url") or record.get("url", ""),
        }
    )
    if record["canonical_url"]:
        record["url"] = record["canonical_url"]
    for url in record.get("source_urls", []):
        aliases[url] = item["content_id"]
    if record.get("canonical_url"):
        aliases[record["canonical_url"]] = item["content_id"]
    return was_seen, record


def recent_realtime_within(
    delivery_history: dict[str, Any], settings: dict[str, Any], minutes: int
) -> bool:
    if minutes <= 0:
        return False
    cutoff = now_dt(settings) - timedelta(minutes=minutes)
    for item in delivery_history.get("items", {}).values():
        realtime_at = item.get("realtime_at")
        if not realtime_at:
            continue
        try:
            sent_at = datetime.fromisoformat(realtime_at)
        except ValueError:
            continue
        if sent_at >= cutoff:
            return True
    return False


def enqueue_retry(payload: dict[str, Any]) -> None:
    queue = load_retry_queue()
    queue.setdefault("items", []).append(payload)
    save_retry_queue(queue)


def send_message(settings: dict[str, Any], kind: str, text: str) -> dict[str, Any]:
    backend = settings.get("push_backend", "openclaw_cli")
    if backend == "stdout":
        return {"ok": True, "backend": "stdout", "text": text}

    if backend == "delivery_queue":
        queue_dir = Path(expand_user("~/.openclaw/delivery-queue/community-signal"))
        queue_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "kind": kind,
            "channel": settings.get("push_channel", "feishu"),
            "to": push_group_target(settings),
            "text": text,
            "created_at": now_iso(settings),
        }
        name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{kind}.json"
        write_json(queue_dir / name, payload)
        return {"ok": True, "backend": "delivery_queue", "path": str(queue_dir / name)}

    if backend != "openclaw_cli":
        raise ValueError(f"unsupported push backend: {backend}")

    cmd = [
        settings.get("openclaw_binary", "openclaw"),
        "message",
        "send",
        "--channel",
        settings.get("push_channel", "feishu"),
        "--target",
        push_group_target(settings),
        "--message",
        text,
        "--json",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        payload = {
            "kind": kind,
            "text": text,
            "created_at": now_iso(settings),
            "backend": backend,
            "stderr": proc.stderr,
            "stdout": proc.stdout,
        }
        enqueue_retry(payload)
        return {
            "ok": False,
            "backend": backend,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    try:
        parsed = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        parsed = {"stdout": proc.stdout}
    return {"ok": True, "backend": backend, "result": parsed}


def record_delivery(
    delivery_history: dict[str, Any], item: dict[str, Any], kind: str, settings: dict[str, Any]
) -> None:
    items = delivery_history.setdefault("items", {})
    record = items.setdefault(
        item["content_id"],
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "canonical_url": item.get("canonical_url", ""),
            "source_urls": item.get("source_urls", []),
            "platform": item.get("platform", ""),
            "source_mode": item.get("source_mode", ""),
        },
    )
    record["url"] = item.get("url") or record.get("url", "")
    record["canonical_url"] = item.get("canonical_url") or record.get("canonical_url", "")
    record["source_urls"] = merge_source_urls(record.get("source_urls", []), item.get("source_urls", []))
    if kind == "realtime":
        record["realtime_at"] = now_iso(settings)
    elif kind == "digest":
        delivered = record.setdefault("digest_dates", [])
        day = item.get("day") or today_key(settings)
        if day not in delivered:
            delivered.append(day)
    record["last_delivery_kind"] = kind
    record["last_delivery_at"] = now_iso(settings)


def has_digest_delivery(delivery_history: dict[str, Any], item: dict[str, Any], day: str) -> bool:
    record = delivery_history.get("items", {}).get(item["content_id"], {})
    return day in record.get("digest_dates", [])


def has_realtime_delivery(delivery_history: dict[str, Any], item: dict[str, Any]) -> bool:
    record = delivery_history.get("items", {}).get(item["content_id"], {})
    return bool(record.get("realtime_at"))


def upsert_digest_candidate(
    digest_candidates: dict[str, Any], day: str, item: dict[str, Any]
) -> tuple[bool, dict[str, Any]]:
    day_items = digest_candidates.setdefault("days", {}).setdefault(day, [])
    for index, existing in enumerate(day_items):
        if existing.get("content_id") != item["content_id"]:
            continue
        merged = existing | item
        merged["realtime_sent"] = bool(existing.get("realtime_sent") or item.get("realtime_sent"))
        merged["source_urls"] = merge_source_urls(
            existing.get("source_urls", []),
            item.get("source_urls", []),
            existing.get("canonical_url", ""),
            item.get("canonical_url", ""),
        )
        merged["canonical_url"] = canonical_url_for(
            {
                "canonical_url": item.get("canonical_url") or existing.get("canonical_url"),
                "source_urls": merged["source_urls"],
                "url": item.get("url") or existing.get("url", ""),
            }
        )
        if merged["canonical_url"]:
            merged["url"] = merged["canonical_url"]
        day_items[index] = merged
        return False, day_items[index]
    day_items.append(item)
    return True, item


def render_realtime_message(item: dict[str, Any]) -> str:
    score = int(item.get("score", 0))
    one_liner = item.get("one_liner") or item.get("reason") or "值得立即查看"
    lines = [
        "🔥 高价值情报提醒",
        "",
        labeled_line("标题", item.get("title", "")),
        labeled_line("作者", item.get("author", "未知")),
        labeled_line("来源", display_source_name(item)),
        labeled_line("评分", f"{score}/10"),
        labeled_line("一句话结论", one_liner),
        labeled_line("为什么建议立即看", item.get("reason", "命中高价值阈值")),
    ]
    if item.get("url"):
        lines.append(labeled_line("链接", item["url"]))
    return "\n".join(lines)


def display_source_name(item: dict[str, Any]) -> str:
    if str(item.get("platform") or "").lower() == "scys":
        return "生财有术"
    return item.get("source_name", item.get("platform", ""))


def labeled_line(label: str, value: Any) -> str:
    return f"**{label}**：{value}"


def render_digest_message(
    day: str,
    stats: dict[str, Any],
    items: list[dict[str, Any]],
    total_candidates: int,
    realtime_count: int,
    source_counts: dict[str, int] | None = None,
) -> str:
    lines = [f"📚 情报日报 | {day}", ""]
    feed_scanned = int(stats.get("feed_scanned") or 0)
    scored = int(stats.get("scored") or stats.get("scanned", 0) or 0)
    coverage_warnings = int(stats.get("coverage_warnings") or 0)
    lines.extend(
        [
            "【今日结论】",
            f"今天共检查 {feed_scanned or scored} 条候选，实际评分 {scored} 条，最终筛出 {total_candidates} 条值得关注的信号。",
        ]
    )
    if coverage_warnings:
        lines.append(labeled_line("覆盖提示", f"有 {coverage_warnings} 次扫描覆盖不足，相关目标会保留到下轮重试。"))
    if realtime_count:
        lines.append(f"其中 {realtime_count} 条已作为实时提醒发出。")
    if source_counts is not None:
        scys_count = int(source_counts.get("scys") or 0)
        github_count = int(source_counts.get("github") or 0)
        if coverage_warnings:
            lines.append(labeled_line("生财有术", "今天扫描覆盖不足，可能没有完整抓到新帖，会在下轮继续重试。"))
        elif scys_count:
            lines.append(labeled_line("生财有术", f"今天筛出 {scys_count} 条需要你看的新帖。"))
        else:
            lines.append(labeled_line("生财有术", "今天没有发现需要你处理的新帖子。"))
        if github_count:
            lines.append(labeled_line("GitHub 项目", f"今天筛出 {github_count} 个需要关注的增长项目。"))
    if not items and total_candidates == 0:
        lines.extend(["", "今天没有发现需要你处理的新帖子或新信号。"])
        return "\n".join(lines)
    lines.extend(["", "【重点情报】"])

    if not items:
        lines.append("今天没有新的日报候选，实时提醒已覆盖全部高价值内容。")
        return "\n".join(lines)

    groups = [
        ("生财有术", [item for item in items if str(item.get("platform") or "").lower() == "scys"]),
        ("GitHub", [item for item in items if str(item.get("platform") or "").lower() == "github"]),
        (
            "其他信号",
            [
                item
                for item in items
                if str(item.get("platform") or "").lower() not in {"scys", "github"}
            ],
        ),
    ]

    rendered_any = False
    for heading, group_items in groups:
        if not group_items:
            continue
        if rendered_any:
            lines.extend(["", "=========="])
        lines.append(f"# **{heading}**")
        rendered_any = True
        for idx, item in enumerate(group_items, start=1):
            lines.append(f"{idx}. {item.get('title', '')}")
            lines.append(f"   {labeled_line('作者', item.get('author', '未知'))}")
            lines.append(f"   {labeled_line('来源', display_source_name(item))}")

            what_it_does = str(item.get("what_it_does") or "").strip()
            target_users = str(item.get("target_users") or item.get("practical_use") or "").strip()
            if what_it_does:
                lines.append(f"   {labeled_line('做什么的', what_it_does)}")
            if target_users:
                lines.append(f"   {labeled_line('适合什么人用', target_users)}")

            summary = item.get("summary", [])
            if summary and not (what_it_does or target_users):
                lines.append(f"   {labeled_line('摘要', ' / '.join(summary[:3]))}")
            why_now = str(item.get("why_now") or item.get("reason") or "").strip()
            if why_now:
                lines.append(f"   {labeled_line('为什么现在值得看', why_now)}")
            item_url = item.get("project_url") or item.get("canonical_url") or item.get("url")
            if item_url:
                lines.append(f"   {labeled_line('链接', item_url)}")
    return "\n".join(lines)


def load_input_json(path_or_none: str | None) -> dict[str, Any]:
    if path_or_none:
        return json.loads(Path(path_or_none).read_text(encoding="utf-8"))
    raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("missing JSON input")
    return json.loads(raw)
