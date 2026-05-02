from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from common import (
    BASE_DIR,
    ensure_day,
    get_tz,
    load_targets,
    load_daily_stats,
    merge_source_urls,
    monitor_target_id,
    normalize_url,
    now_dt,
    load_settings,
    person_target_id,
    save_daily_stats,
    today_key,
)
from due_targets import build_monitor_due, build_person_due


SCORING_PROMPT_PATH = BASE_DIR / "prompts" / "scoring.txt"
SCRAPE_SCYS_PATH = BASE_DIR / "scripts" / "scrape_scys.mjs"
RUN_GITHUB_STAR_RADAR_PATH = BASE_DIR / "scripts" / "run_github_star_radar.py"
RECORD_ITEM_PATH = BASE_DIR / "scripts" / "record_item.py"
MARK_TARGET_SCAN_PATH = BASE_DIR / "scripts" / "mark_target_scan.py"
OPENCLAW_CONFIG_PATH = Path(os.environ.get("OPENCLAW_CONFIG", "~/.openclaw/openclaw.json")).expanduser()
RUN_LOG_DIR = BASE_DIR / "state" / "run_logs"


def run_json(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or f"command failed: {' '.join(cmd)}")
    return json.loads(proc.stdout or "{}")


def append_run_log(settings: dict[str, Any], payload: dict[str, Any]) -> None:
    RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = today_key(settings)
    entry = {
        "logged_at": now_dt(settings).isoformat(timespec="seconds"),
        **payload,
    }
    with (RUN_LOG_DIR / f"scan-{day}.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_openclaw_config() -> dict[str, Any]:
    if not OPENCLAW_CONFIG_PATH.exists():
        raise RuntimeError(f"OpenClaw config not found: {OPENCLAW_CONFIG_PATH}")
    return json.loads(OPENCLAW_CONFIG_PATH.read_text(encoding="utf-8"))


def model_ref_value(raw: Any) -> str:
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, dict):
        return str(raw.get("primary") or "").strip()
    return ""


def resolve_default_model_ref(cfg: dict[str, Any]) -> tuple[str, str]:
    agent_id = str(os.environ.get("OPENCLAW_AGENT_ID") or "").strip()
    agents = cfg.get("agents") or {}
    if agent_id:
        for entry in agents.get("list") or []:
            if str(entry.get("id") or "").strip() != agent_id:
                continue
            ref = model_ref_value(entry.get("model"))
            if ref:
                break
        else:
            ref = ""
    else:
        ref = ""
    if not ref:
        ref = model_ref_value((agents.get("defaults") or {}).get("model"))
    if "/" not in ref:
        raise RuntimeError("OpenClaw default model must use provider/model format")
    provider, model = ref.split("/", 1)
    if not provider or not model:
        raise RuntimeError("OpenClaw default model must use provider/model format")
    return provider, model


def extract_response_text(payload: dict[str, Any]) -> str:
    output_text = str(payload.get("output_text") or "").strip()
    if output_text:
        return output_text
    parts: list[str] = []
    for output in payload.get("output") or []:
        for content in output.get("content") or []:
            text = content.get("text")
            if text:
                parts.append(str(text))
    if parts:
        return "\n".join(parts).strip()
    choices = payload.get("choices") or []
    if choices:
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
    return ""


def run_default_model(prompt: str, settings: dict[str, Any]) -> dict[str, Any]:
    cfg = load_openclaw_config()
    provider, model = resolve_default_model_ref(cfg)
    provider_cfg = ((cfg.get("models") or {}).get("providers") or {}).get(provider) or {}
    api_kind = str(provider_cfg.get("api") or "").strip()
    base_url = str(provider_cfg.get("baseUrl") or "").rstrip("/")
    api_key = str(provider_cfg.get("apiKey") or "").strip()
    if not base_url or not api_key:
        raise RuntimeError(f"OpenClaw provider {provider!r} is missing baseUrl or apiKey")

    timeout_seconds = int(settings.get("scoring_timeout_seconds", 120) or 120)
    max_output_tokens = int(settings.get("scoring_max_output_tokens", 1200) or 1200)
    if api_kind == "openai-responses":
        url = f"{base_url}/responses"
        request_payload = {
            "model": model,
            "input": prompt,
            "max_output_tokens": max_output_tokens,
        }
    elif api_kind in {"openai-chat", "openai-completions"}:
        url = f"{base_url}/chat/completions"
        request_payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_output_tokens,
        }
    else:
        raise RuntimeError(f"unsupported default model api: {api_kind}")

    request = urllib.request.Request(
        url,
        data=json.dumps(request_payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"default model request failed: HTTP {exc.code}: {body[:500]}") from exc
    parsed = json.loads(body or "{}")
    text = extract_response_text(parsed)
    if not text:
        raise RuntimeError("default model returned no text")
    return {"outputs": [{"text": text}], "provider": provider, "model": model}


def run_item(payload: dict[str, Any]) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
        tmp_path = Path(handle.name)
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    try:
        return run_json(["python3", str(RECORD_ITEM_PATH), "--input", str(tmp_path)])
    finally:
        tmp_path.unlink(missing_ok=True)


def mark_target(mode: str, target_id: str, new_items: int) -> dict[str, Any]:
    return run_json(
        [
            "python3",
            str(MARK_TARGET_SCAN_PATH),
            "--mode",
            mode,
            "--target-id",
            target_id,
            "--new-items",
            str(new_items),
        ]
    )


def trim_text(value: str, limit: int) -> str:
    text = (value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def parse_relative_time(value: str, settings: dict[str, Any]) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    if text[:4].isdigit():
        return text

    now = now_dt(settings)
    if text == "刚刚":
        return now.isoformat(timespec="seconds")

    for suffix, unit in (("分钟前", "minutes"), ("小时前", "hours"), ("天前", "days")):
        if text.endswith(suffix):
            try:
                amount = int(text[: -len(suffix)])
            except ValueError:
                return ""
            delta = timedelta(**{unit: amount})
            return (now - delta).isoformat(timespec="seconds")

    if text == "昨天":
        return (now - timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0).isoformat()
    if text == "前天":
        return (now - timedelta(days=2)).replace(hour=12, minute=0, second=0, microsecond=0).isoformat()
    return ""


def parse_published_datetime(value: Any, settings: dict[str, Any]) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None

    relative = parse_relative_time(text, settings)
    if relative and relative != text:
        text = relative

    cleaned = (
        text.replace("发布于", "")
        .replace("发表于", "")
        .replace("年", "-")
        .replace("月", "-")
        .replace("日", "")
        .replace("/", "-")
        .strip()
    )
    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")
    if cleaned.endswith("Z"):
        cleaned = f"{cleaned[:-1]}+00:00"

    tz = get_tz(settings)
    now = now_dt(settings)

    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        parsed = None
    if parsed is not None:
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=tz)
        return parsed.astimezone(tz)

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(cleaned, fmt).replace(tzinfo=tz)
        except ValueError:
            pass

    for fmt in ("%m-%d %H:%M", "%m-%d"):
        try:
            parsed = datetime.strptime(cleaned, fmt).replace(year=now.year, tzinfo=tz)
        except ValueError:
            continue
        if parsed > now + timedelta(days=1):
            parsed = parsed.replace(year=now.year - 1)
        return parsed

    return None


def item_published_datetime(item: dict[str, Any], settings: dict[str, Any]) -> datetime | None:
    detail = item.get("detail") or {}
    for value in (detail.get("published_at"), item.get("published_at_text"), item.get("published_at")):
        parsed = parse_published_datetime(value, settings)
        if parsed is not None:
            return parsed
    return None


def freshness_status(
    target: dict[str, Any], item: dict[str, Any], settings: dict[str, Any]
) -> tuple[bool, str, str]:
    published_scope = str(target.get("published_date_scope", "")).strip()
    if published_scope in {"current_day", "today"}:
        published_at = item_published_datetime(item, settings)
        if published_at is None:
            return False, "missing_published_at", ""
        now = now_dt(settings)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if published_at < day_start:
            return False, "outside_current_day", published_at.isoformat(timespec="seconds")
        if published_at > now + timedelta(minutes=5):
            return False, "future_published_at", published_at.isoformat(timespec="seconds")
        return True, "current_day", published_at.isoformat(timespec="seconds")

    max_age_days = target.get("max_post_age_days", settings.get("max_post_age_days"))
    if max_age_days in (None, ""):
        return True, "freshness_not_configured", ""
    published_at = item_published_datetime(item, settings)
    if published_at is None:
        return False, "missing_published_at", ""
    now = now_dt(settings)
    cutoff = now - timedelta(days=float(max_age_days), minutes=5)
    if published_at < cutoff:
        return False, "outside_recent_window", published_at.isoformat(timespec="seconds")
    return True, "recent", published_at.isoformat(timespec="seconds")


def delivery_day_for_target(target: dict[str, Any], settings: dict[str, Any]) -> str:
    delay_days = int(target.get("delivery_delay_days", 0) or 0)
    return (now_dt(settings) + timedelta(days=delay_days)).date().isoformat()


def full_doc_text(item: dict[str, Any]) -> str:
    detail = item.get("detail") or {}
    feishu_doc = detail.get("feishu_doc") or {}
    return str(feishu_doc.get("content") or "").strip()


def preview_text(item: dict[str, Any]) -> str:
    detail = item.get("detail") or {}
    parts = [
        item.get("title", ""),
        item.get("preview", ""),
        detail.get("content", ""),
        " ".join(str(tag) for tag in item.get("tags") or []),
        " ".join(str(tag) for tag in detail.get("tags") or []),
    ]
    return "\n".join(str(part).strip() for part in parts if str(part or "").strip())


def item_source_urls(item: dict[str, Any]) -> list[str]:
    detail = item.get("detail") or {}
    feishu_doc = detail.get("feishu_doc") or {}
    values = [
        item.get("detail_url"),
        item.get("url"),
        detail.get("url"),
        detail.get("feishu_url"),
        feishu_doc.get("url"),
    ]
    urls: list[str] = []
    for value in values:
        if not value:
            continue
        candidates = value if isinstance(value, list) else [value]
        for candidate in candidates:
            text = str(candidate or "").strip()
            if text and text not in urls:
                urls.append(text)
    return urls


def scoring_readiness(
    target: dict[str, Any], item: dict[str, Any], settings: dict[str, Any]
) -> tuple[bool, str]:
    if full_doc_text(item):
        return True, "full_doc"
    if not target.get("final_score_requires_full_doc"):
        return True, "detail_or_preview"
    if not target.get("allow_preview_scoring_without_full_doc"):
        return False, "missing_full_doc"
    minimum_chars = int(
        target.get(
            "minimum_preview_chars_for_scoring",
            settings.get("minimum_preview_chars_for_scoring", 120),
        )
        or 0
    )
    if len(preview_text(item)) < minimum_chars:
        return False, "preview_too_short"
    if target.get("require_source_url_for_preview_scoring", True) and not item_source_urls(item):
        return False, "missing_source_url"
    return True, "preview_only"


def render_comments(item: dict[str, Any]) -> str:
    detail = item.get("detail") or {}
    comments = detail.get("comments") or []
    snippets = []
    for comment in comments[:5]:
        author = str(comment.get("author", "")).strip()
        content = str(comment.get("content", "")).strip()
        if not content:
            continue
        if author:
            snippets.append(f"{author}: {content}")
        else:
            snippets.append(content)
    return "\n".join(snippets)


def scoring_prompt(template: str, target: dict[str, Any], item: dict[str, Any], settings: dict[str, Any]) -> str:
    detail = item.get("detail") or {}
    feishu_doc = detail.get("feishu_doc") or {}
    has_full_text = bool(str(feishu_doc.get("content") or "").strip())
    published_at = (
        str(detail.get("published_at", "")).strip()
        or parse_relative_time(item.get("published_at_text", ""), settings)
        or ""
    )
    sections = [
        template.strip(),
        "",
        "请严格只输出一个 JSON 对象，不要 markdown，不要代码块，不要额外解释。",
        "",
        f"监控目标：{target.get('name', '')}",
        f"关注主题：{', '.join(target.get('focus_topics', []))}",
        "",
        "候选内容：",
        f"标题：{detail.get('title') or item.get('title', '')}",
        f"作者：{detail.get('author') or item.get('author', '')}",
        f"发布时间：{published_at}",
        f"首页标签：{', '.join(item.get('tags') or [])}",
        f"详情标签：{', '.join(detail.get('tags') or [])}",
        f"首页摘要：{trim_text(str(item.get('preview', '')), 1800)}",
        f"站内详情摘要：{trim_text(str(detail.get('content', '')), 3000)}",
    ]
    if feishu_doc:
        sections.extend(
            [
                f"飞书正文标题：{feishu_doc.get('title', '')}",
                f"飞书正文目录：{', '.join(feishu_doc.get('toc') or [])}",
                f"飞书正文：{trim_text(str(feishu_doc.get('content', '')), 12000)}",
            ]
        )
    if not has_full_text:
        sections.extend(
            [
                "",
                "注意：当前候选没有完整飞书正文，只能依据标题、标签、首页摘要和站内摘要判断。",
                "如果这些摘要没有数据、方法、案例、步骤、渠道、转化、定价或市场进入信息，不要给到 7 分以上。",
            ]
        )
    comments_text = render_comments(item)
    if comments_text:
        sections.append(f"评论摘录：{trim_text(comments_text, 2000)}")
    sections.extend(
        [
            "",
            "JSON 字段要求：score, one_liner, summary, reason, topics",
            "summary 必须是 2-3 句数组，score 必须是 1-10 的整数。",
        ]
    )
    return "\n".join(sections)


def parse_model_json(text: str) -> dict[str, Any]:
    payload = (text or "").strip()
    if not payload:
        raise ValueError("empty model output")
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        start = payload.find("{")
        end = payload.rfind("}")
        if start >= 0 and end > start:
            return json.loads(payload[start : end + 1])
        raise


def score_item(
    template: str, target: dict[str, Any], item: dict[str, Any], settings: dict[str, Any]
) -> dict[str, Any]:
    prompt = scoring_prompt(template, target, item, settings)
    result = run_default_model(prompt, settings)
    outputs = result.get("outputs") or []
    if not outputs:
        raise RuntimeError("model returned no outputs")
    parsed = parse_model_json(str(outputs[0].get("text", "")))
    parsed["score"] = int(parsed.get("score", 0))
    parsed["summary"] = parsed.get("summary") or []
    parsed["topics"] = parsed.get("topics") or []
    return parsed


def build_record_payload(
    target: dict[str, Any], item: dict[str, Any], scored: dict[str, Any], settings: dict[str, Any]
) -> dict[str, Any]:
    detail = item.get("detail") or {}
    feishu_doc = detail.get("feishu_doc") or {}
    source_urls = merge_source_urls(
        item.get("detail_url"),
        detail.get("url"),
        detail.get("feishu_url"),
        feishu_doc.get("url"),
        item.get("links"),
        detail.get("external_links"),
    )
    canonical_url = normalize_url(feishu_doc.get("url")) or normalize_url(detail.get("feishu_url"))
    canonical_url = canonical_url or normalize_url(detail.get("url")) or normalize_url(item.get("detail_url"))
    canonical_url = canonical_url or normalize_url(item.get("url"))
    published_at = (
        str(detail.get("published_at", "")).strip()
        or parse_relative_time(item.get("published_at_text", ""), settings)
        or now_dt(settings).isoformat(timespec="seconds")
    )
    return {
        "title": feishu_doc.get("title") or detail.get("title") or item.get("title", ""),
        "author": detail.get("author") or item.get("author", ""),
        "url": canonical_url,
        "canonical_url": canonical_url,
        "source_urls": source_urls,
        "platform": target.get("platform", "scys"),
        "source_mode": "community",
        "source_name": target.get("name", target.get("platform", "community")),
        "published_at": published_at,
        "day": delivery_day_for_target(target, settings),
        "score": int(scored.get("score", 0)),
        "one_liner": str(scored.get("one_liner", "")).strip(),
        "summary": scored.get("summary") or [],
        "reason": str(scored.get("reason", "")).strip(),
        "topics": scored.get("topics") or target.get("focus_topics", []),
        "detail_url": detail.get("url") or item.get("detail_url", ""),
        "feishu_url": feishu_doc.get("url") or detail.get("feishu_url", ""),
        "preview": item.get("preview", ""),
    }


def run_scys_target(
    target: dict[str, Any], scoring_template: str, settings: dict[str, Any]
) -> dict[str, Any]:
    cmd = [
        "node",
        str(SCRAPE_SCYS_PATH),
        "--entry-url",
        str(target.get("entry_url") or target.get("community_url") or "https://scys.com"),
        "--limit",
        str(int(target.get("max_posts_per_scan", 20))),
        "--details",
        "--feed-filter",
        str(target.get("preferred_feed_filter", "全部")),
    ]
    preferred_sort = str(target.get("preferred_sort", "")).strip()
    if preferred_sort:
        cmd.extend(["--sort-value", preferred_sort])
    if target.get("follow_external_doc"):
        cmd.append("--expand-feishu")

    scraped = run_json(cmd)
    outcomes: list[dict[str, Any]] = []
    new_items = 0
    full_doc_ready = 0
    recent_items = 0
    freshness_skipped = 0
    scored_items = 0
    score_errors = 0

    for item in scraped.get("items", []):
        outcome: dict[str, Any] = {
            "title": item.get("title", ""),
            "detail_url": item.get("detail_url", ""),
            "skipped": None,
        }
        is_recent, freshness_reason, parsed_published_at = freshness_status(target, item, settings)
        outcome["freshness"] = freshness_reason
        if parsed_published_at:
            outcome["published_at"] = parsed_published_at
        if not is_recent:
            freshness_skipped += 1
            outcome["skipped"] = freshness_reason
            outcomes.append(outcome)
            continue
        recent_items += 1
        ready, content_basis = scoring_readiness(target, item, settings)
        outcome["content_basis"] = content_basis
        if not ready:
            outcome["skipped"] = content_basis
            outcomes.append(outcome)
            continue
        if content_basis == "full_doc":
            full_doc_ready += 1
        try:
            scored = score_item(scoring_template, target, item, settings)
            payload = build_record_payload(target, item, scored, settings)
            record_result = run_item(payload)
            outcome["score"] = scored.get("score", 0)
            outcome["decision"] = record_result.get("decision")
            outcome["url"] = payload.get("url", "")
            scored_items += 1
            if record_result.get("decision") != "duplicate_skip":
                new_items += 1
        except Exception as exc:  # noqa: BLE001
            score_errors += 1
            outcome["error"] = str(exc)
        outcomes.append(outcome)

    scraped_total = int(scraped.get("extracted_items", 0) or len(scraped.get("items", [])))
    detail_ready_items = int(scraped.get("detail_ready_items", 0) or 0)
    feishu_ready_items = int(scraped.get("feishu_ready_items", 0) or 0)
    min_scraped = int(
        target.get("minimum_scraped_items_per_scan", settings.get("minimum_scraped_items_per_scan", 0))
        or 0
    )
    min_scored = int(
        target.get("minimum_scored_items_per_scan", settings.get("minimum_scored_items_per_scan", 0))
        or 0
    )
    effective_min_scored = min(min_scored, recent_items) if target.get("max_post_age_days") else min_scored
    coverage_ok = scraped_total >= min_scraped and scored_items >= effective_min_scored

    daily_stats = load_daily_stats()
    day_stats = ensure_day(daily_stats, delivery_day_for_target(target, settings))
    day_stats["feed_scanned"] = int(day_stats.get("feed_scanned", 0)) + scraped_total
    day_stats["detail_ready"] = int(day_stats.get("detail_ready", 0)) + detail_ready_items
    day_stats["full_doc_ready"] = int(day_stats.get("full_doc_ready", 0)) + full_doc_ready
    day_stats["scored"] = int(day_stats.get("scored", 0)) + scored_items
    day_stats["scan_errors"] = int(day_stats.get("scan_errors", 0)) + score_errors
    if not coverage_ok:
        day_stats["coverage_warnings"] = int(day_stats.get("coverage_warnings", 0)) + 1
    save_daily_stats(daily_stats)

    if coverage_ok:
        mark_result = mark_target("monitor", str(target["target_id"]), new_items)
    else:
        mark_result = {
            "ok": False,
            "skipped": "coverage_insufficient",
            "minimum_scraped_items_per_scan": min_scraped,
            "minimum_scored_items_per_scan": min_scored,
            "actual_scraped_items": scraped_total,
            "actual_scored_items": scored_items,
        }
    return {
        "target_id": target["target_id"],
        "name": target.get("name", ""),
        "platform": target.get("platform", ""),
        "scraped_total": scraped_total,
        "recent_items": recent_items,
        "freshness_skipped": freshness_skipped,
        "detail_ready_items": detail_ready_items,
        "feishu_ready_items": feishu_ready_items,
        "full_doc_ready_items": full_doc_ready,
        "scored_items": scored_items,
        "score_errors": score_errors,
        "coverage_ok": coverage_ok,
        "new_items": new_items,
        "mark_result": mark_result,
        "outcomes": outcomes,
    }


def run_github_target(target: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    cmd = [
        "python3",
        str(RUN_GITHUB_STAR_RADAR_PATH),
        "--record-candidates",
        "--limit",
        str(int(target.get("max_projects_per_digest", settings.get("digest_max_items", 8)))),
        "--scrape-limit",
        str(int(target.get("max_repos_per_query", 25))),
    ]
    terms = target.get("search_terms") or target.get("focus_terms") or []
    if isinstance(terms, list) and terms:
        cmd.extend(["--terms", ",".join(str(term) for term in terms)])
    result = run_json(cmd)
    added = int((result.get("record_result") or {}).get("added") or 0)
    updated = int((result.get("record_result") or {}).get("updated") or 0)
    mark_result = mark_target("monitor", str(target["target_id"]), added + updated)
    return {
        "target_id": target["target_id"],
        "name": target.get("name", ""),
        "platform": target.get("platform", ""),
        "candidate_count": result.get("candidate_count", 0),
        "selected_count": result.get("selected_count", 0),
        "record_result": result.get("record_result"),
        "mark_result": mark_result,
        "state_path": result.get("state_path"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic community-signal scans.")
    parser.add_argument("--mode", choices=["monitor", "person", "all"], default="monitor")
    parser.add_argument("--platform", help="Only run targets for one platform, e.g. scys or github.")
    parser.add_argument("--force", action="store_true", help="Run matching targets even if they are not due.")
    args = parser.parse_args()

    settings = load_settings()
    scoring_template = SCORING_PROMPT_PATH.read_text(encoding="utf-8")
    now = now_dt(settings)

    targets: list[dict[str, Any]] = []
    if args.force:
        configured = load_targets()
        if args.mode in {"monitor", "all"}:
            for target in configured.get("monitoring_targets", []):
                targets.append(target | {"target_id": monitor_target_id(target), "mode": "monitor"})
        if args.mode in {"person", "all"}:
            all_person_targets = configured.get("person_targets", {}).get("core_targets", []) + configured.get(
                "person_targets", {}
            ).get("temporary_targets", [])
            for target in all_person_targets:
                targets.append(target | {"target_id": person_target_id(target), "mode": "person"})
    else:
        if args.mode in {"monitor", "all"}:
            targets.extend(build_monitor_due(now))
        if args.mode in {"person", "all"}:
            targets.extend(build_person_due(now))

    if args.platform:
        wanted_platform = args.platform.strip().lower()
        targets = [target for target in targets if str(target.get("platform", "")).lower() == wanted_platform]

    results = []
    for target in targets:
        if target.get("mode") != "monitor":
            results.append(
                {
                    "target_id": target["target_id"],
                    "name": target.get("name", ""),
                    "skipped": "person_mode_not_implemented",
                }
            )
            continue
        if target.get("platform") == "github":
            results.append(run_github_target(target, settings))
            continue
        if target.get("platform") != "scys":
            results.append(
                {
                    "target_id": target["target_id"],
                    "name": target.get("name", ""),
                    "skipped": "platform_not_implemented",
                }
            )
            continue
        results.append(run_scys_target(target, scoring_template, settings))

    output = {"ok": True, "mode": args.mode, "results": results}
    append_run_log(settings, output)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        try:
            append_run_log(load_settings(), {"ok": False, "error": str(exc)})
        except Exception:
            pass
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise
