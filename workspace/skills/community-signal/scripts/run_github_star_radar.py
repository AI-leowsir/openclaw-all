from __future__ import annotations

import argparse
import html
import json
import math
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from common import (
    BASE_DIR,
    STATE_DIR,
    ensure_day,
    load_daily_stats,
    load_digest_candidates,
    load_settings,
    now_dt,
    read_json,
    save_daily_stats,
    save_digest_candidates,
    send_message,
    sha256_hex,
    today_key,
    upsert_digest_candidate,
    write_json,
)


STATE_PATH = STATE_DIR / "github_star_radar.json"
SCRAPE_GITHUB_TRENDING_PATH = BASE_DIR / "scripts" / "scrape_github_trending.mjs"
GROWTH_WINDOW_HOURS = 48
GROWTH_WINDOW_TOLERANCE_HOURS = 3
SNAPSHOT_RETENTION_DAYS = 10

AI_KEYWORDS = {
    "ai": 2,
    "artificial intelligence": 3,
    "llm": 4,
    "large language model": 4,
    "agent": 3,
    "agents": 3,
    "ai-agent": 4,
    "rag": 4,
    "mcp": 5,
    "model context protocol": 5,
    "openai": 4,
    "anthropic": 4,
    "claude": 3,
    "gemini": 3,
    "llama": 3,
    "cursor": 3,
    "copilot": 3,
    "codegen": 4,
    "code generation": 4,
    "developer tool": 4,
    "devtool": 3,
    "devtools": 3,
    "prompt": 2,
    "embedding": 3,
    "vector": 2,
    "inference": 3,
    "eval": 3,
    "evaluation": 2,
    "workflow": 2,
    "automation": 2,
    "chatbot": 2,
    "ai product": 3,
    "generative ai": 3,
    "machine learning": 3,
    "ml": 2,
    "image generation": 3,
    "video generation": 3,
    "ai image": 3,
    "ai video": 3,
}

EXCLUDE_KEYWORDS = {
    "wallpaper",
    "theme",
    "icon pack",
    "awesome list",
    "awesome-",
}

SUPPLEMENT_EXCLUDE_KEYWORDS = {
    "awesome list",
    "awesome-",
    "wallpaper",
    "theme",
    "icon pack",
}


def clean_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_int(value: Any) -> int:
    if value is None:
        return 0
    text = str(value).replace(",", "").strip()
    if not text:
        return 0
    try:
        return int(text)
    except ValueError:
        return 0


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def repo_from_cdp_item(item: dict[str, Any]) -> dict[str, Any]:
    full_name = str(item.get("full_name", "")).strip()
    return {
        "full_name": full_name,
        "html_url": item.get("html_url") or f"https://github.com/{full_name}",
        "description": item.get("description") or "",
        "stars": int(item.get("stars") or 0),
        "forks": int(item.get("forks") or 0),
        "language": item.get("language") or "",
        "topics": [],
        "created_at": item.get("created_at") or "",
        "pushed_at": item.get("pushed_at") or "",
        "archived": False,
        "fork": bool(item.get("fork")),
        "owner": full_name.split("/", 1)[0],
        "source": item.get("source") or "github_search_cdp",
        "trending_today_stars": int(item.get("trending_today_stars") or 0),
        "trending_sources": item.get("source_urls") or [item.get("page_url")],
        "search_rank": int(item.get("search_rank") or 0),
        "search_query": item.get("search_query") or "",
    }


def run_json_cmd(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or f"command failed: {' '.join(cmd)}")
    return json.loads(proc.stdout or "{}")


def collect_cdp_trending(args: argparse.Namespace) -> dict[str, dict[str, Any]]:
    cmd = [
        "node",
        str(SCRAPE_GITHUB_TRENDING_PATH),
        "--port",
        str(args.cdp_port),
        "--limit",
        str(args.scrape_limit),
        "--timeout-ms",
        str(args.timeout_ms),
        "--retries",
        str(getattr(args, "scrape_retries", 2)),
        "--settle-ms",
        str(getattr(args, "page_settle_ms", 800)),
    ]
    if args.terms:
        cmd.extend(["--terms", args.terms])
    payload = run_json_cmd(cmd)
    errors = payload.get("errors") or []
    if payload.get("ok") is False:
        detail = "; ".join(
            f"{error.get('term')}: {error.get('error')}" for error in errors if isinstance(error, dict)
        )
        raise RuntimeError(f"GitHub CDP search failed for all terms: {detail or 'unknown error'}")
    if not payload.get("items") and errors:
        raise RuntimeError(f"GitHub CDP search returned no items: {errors}")
    repos: dict[str, dict[str, Any]] = {}
    for item in payload.get("items") or []:
        repo = repo_from_cdp_item(item)
        if not repo["full_name"]:
            continue
        key = repo["full_name"].lower()
        repos[key] = merge_repo(repos.get(key, {}), repo)
    return repos


def merge_repo(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = existing | {key: value for key, value in incoming.items() if value not in ("", None, [])}
    merged["trending_today_stars"] = max(
        int(existing.get("trending_today_stars") or 0),
        int(incoming.get("trending_today_stars") or 0),
    )
    merged["trending_sources"] = sorted(
        set(existing.get("trending_sources") or []) | set(incoming.get("trending_sources") or [])
    )
    if existing.get("source") and incoming.get("source") and existing["source"] != incoming["source"]:
        merged["source"] = f"{existing['source']}+{incoming['source']}"
    return merged


def snapshot_records(record: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not record:
        return []
    snapshots = list(record.get("snapshots") or [])
    if record.get("stars") is not None and record.get("seen_at"):
        snapshots.append({"stars": int(record.get("stars") or 0), "seen_at": record.get("seen_at")})
    valid = []
    seen_keys: set[tuple[str, int]] = set()
    for snapshot in snapshots:
        seen_at = str(snapshot.get("seen_at") or "").strip()
        stars = int(snapshot.get("stars") or 0)
        if not seen_at or stars <= 0 or not parse_iso(seen_at):
            continue
        key = (seen_at, stars)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        valid.append({"seen_at": seen_at, "stars": stars})
    return sorted(valid, key=lambda item: item["seen_at"])


def growth_snapshot(record: dict[str, Any] | None, settings: dict[str, Any]) -> dict[str, Any] | None:
    now = now_dt(settings)
    candidates = []
    for snapshot in snapshot_records(record):
        seen_at = parse_iso(snapshot.get("seen_at"))
        if not seen_at:
            continue
        age_hours = (now - seen_at.astimezone(now.tzinfo)).total_seconds() / 3600
        if 1 <= age_hours <= GROWTH_WINDOW_HOURS + GROWTH_WINDOW_TOLERANCE_HOURS:
            candidates.append({"stars": snapshot["stars"], "seen_at": snapshot["seen_at"], "age_hours": age_hours})
    if not candidates:
        return None
    return max(candidates, key=lambda item: item["age_hours"])


def recent_state_repos(state: dict[str, Any], settings: dict[str, Any], days: int = 3) -> dict[str, dict[str, Any]]:
    now = now_dt(settings)
    repos: dict[str, dict[str, Any]] = {}
    for key, record in state.get("repos", {}).items():
        snapshots = snapshot_records(record)
        if not snapshots:
            continue
        last_seen = parse_iso(snapshots[-1]["seen_at"])
        if not last_seen or now - last_seen.astimezone(now.tzinfo) > timedelta(days=days):
            continue
        full_name = record.get("full_name") or key
        repos[key] = {
            "full_name": full_name,
            "html_url": record.get("html_url") or f"https://github.com/{full_name}",
            "description": record.get("description") or "",
            "stars": int(snapshots[-1]["stars"]),
            "source": "state_recent",
            "trending_today_stars": 0,
            "trending_sources": [],
        }
    return repos


def repo_state_record(repo: dict[str, Any], previous: dict[str, Any] | None, seen_at: str, settings: dict[str, Any]) -> dict[str, Any]:
    now = now_dt(settings)
    cutoff = now - timedelta(days=SNAPSHOT_RETENTION_DAYS)
    snapshots = []
    for snapshot in snapshot_records(previous):
        parsed = parse_iso(snapshot.get("seen_at"))
        if parsed and parsed.astimezone(now.tzinfo) >= cutoff:
            snapshots.append(snapshot)
    snapshots.append({"seen_at": seen_at, "stars": int(repo.get("stars") or 0)})
    return {
        "full_name": repo.get("full_name"),
        "stars": int(repo.get("stars") or 0),
        "description": repo.get("description") or "",
        "html_url": repo.get("html_url") or f"https://github.com/{repo.get('full_name')}",
        "seen_at": seen_at,
        "snapshots": snapshots[-SNAPSHOT_RETENTION_DAYS:],
    }


def relevance(repo: dict[str, Any]) -> tuple[int, list[str]]:
    fields = [
        repo.get("full_name", ""),
        repo.get("description", ""),
        repo.get("language", ""),
        " ".join(repo.get("topics") or []),
    ]
    text = " ".join(str(field).lower() for field in fields)
    if any(bad in text for bad in EXCLUDE_KEYWORDS):
        return 0, []

    score = 0
    hits: list[str] = []
    for keyword, weight in AI_KEYWORDS.items():
        pattern = r"(?<![a-z0-9])" + re.escape(keyword).replace(r"\ ", r"[\s_-]+") + r"(?![a-z0-9])"
        if re.search(pattern, text):
            score += weight
            hits.append(keyword)
    return score, hits[:6]


def classify_scene(repo: dict[str, Any], hits: list[str]) -> str:
    text = " ".join([repo.get("full_name", ""), repo.get("description", ""), " ".join(repo.get("topics") or []), *hits]).lower()
    if any(term in text for term in ("mcp", "developer tool", "devtool", "codegen", "code generation", "copilot", "cursor")):
        return "AI 开发者工具"
    if any(term in text for term in ("agent", "workflow", "automation")):
        return "AI agent / 工作流"
    if any(term in text for term in ("rag", "embedding", "vector")):
        return "RAG / 知识库"
    if any(term in text for term in ("inference", "llama", "model")):
        return "模型 / 推理工具"
    return "AI 工具 / 产品"


def search_position_signal(repo: dict[str, Any]) -> int:
    rank = parse_int(repo.get("search_rank"))
    if rank <= 0:
        return 0
    return max(3, 28 - rank)


def score_repo(repo: dict[str, Any], previous: dict[str, Any] | None, settings: dict[str, Any]) -> dict[str, Any] | None:
    if repo.get("archived") or repo.get("fork"):
        return None
    rel_score, hits = relevance(repo)
    if rel_score < 2:
        return None

    now = now_dt(settings)
    stars = int(repo.get("stars") or 0)
    created_at = parse_iso(repo.get("created_at"))
    age_days = max(1, (now - created_at.astimezone(now.tzinfo)).days) if created_at else None
    stars_per_day = stars / age_days if age_days else None
    window_snapshot = growth_snapshot(previous, settings)
    delta_48h = stars - int(window_snapshot["stars"]) if window_snapshot else None
    if delta_48h is not None and delta_48h < 0:
        delta_48h = 0
    observed_hours = round(float(window_snapshot["age_hours"]), 1) if window_snapshot else None
    normalized_48h_delta = None
    if delta_48h is not None and observed_hours and observed_hours >= 12:
        normalized_48h_delta = round(delta_48h * GROWTH_WINDOW_HOURS / observed_hours)
    trending_today = int(repo.get("trending_today_stars") or 0)
    recent_search_signal = search_position_signal(repo)
    growth_signal = max(
        normalized_48h_delta or delta_48h or 0,
        trending_today,
        min(stars_per_day, 250) if stars_per_day is not None else 0,
        recent_search_signal,
    )

    if stars < 25 and growth_signal < 10:
        return None
    if growth_signal < 3 and stars < 1000:
        return None

    rank = growth_signal * 10 + rel_score * 6 + math.log10(max(stars, 1)) * 3
    if delta_48h is not None:
        rank += min(normalized_48h_delta or delta_48h, 700)
    if trending_today:
        rank += min(trending_today, 500) * 0.5
    if age_days is not None and age_days <= 45:
        rank += 12

    repo["relevance_score"] = rel_score
    repo["relevance_hits"] = hits
    repo["scene"] = classify_scene(repo, hits)
    repo["delta_48h"] = delta_48h
    repo["growth_window_hours"] = observed_hours
    repo["normalized_48h_delta"] = normalized_48h_delta
    repo["stars_per_day"] = round(stars_per_day, 1) if stars_per_day is not None else None
    repo["recent_search_signal"] = recent_search_signal
    repo["rank_score"] = round(rank, 2)
    return repo


def score_trending_supplement(
    repo: dict[str, Any], previous: dict[str, Any] | None, settings: dict[str, Any]
) -> dict[str, Any] | None:
    if repo.get("archived") or repo.get("fork"):
        return None
    text = " ".join(
        [
            str(repo.get("full_name", "")),
            str(repo.get("description", "")),
            str(repo.get("language", "")),
        ]
    ).lower()
    if any(keyword in text for keyword in SUPPLEMENT_EXCLUDE_KEYWORDS):
        return None
    rel_score, hits = relevance(repo)
    if rel_score < 2:
        return None

    now = now_dt(settings)
    stars = int(repo.get("stars") or 0)
    if stars <= 0:
        return None
    created_at = parse_iso(repo.get("created_at"))
    age_days = max(1, (now - created_at.astimezone(now.tzinfo)).days) if created_at else None
    stars_per_day = stars / age_days if age_days else None
    window_snapshot = growth_snapshot(previous, settings)
    delta_48h = stars - int(window_snapshot["stars"]) if window_snapshot else None
    if delta_48h is not None and delta_48h < 0:
        delta_48h = 0
    observed_hours = round(float(window_snapshot["age_hours"]), 1) if window_snapshot else None
    normalized_48h_delta = None
    if delta_48h is not None and observed_hours and observed_hours >= 12:
        normalized_48h_delta = round(delta_48h * GROWTH_WINDOW_HOURS / observed_hours)
    trending_today = int(repo.get("trending_today_stars") or 0)
    recent_search_signal = search_position_signal(repo)
    growth_signal = max(
        normalized_48h_delta or delta_48h or 0,
        trending_today,
        min(stars_per_day, 250) if stars_per_day is not None else 0,
        recent_search_signal,
    )
    if growth_signal < 20:
        return None

    repo["relevance_score"] = rel_score
    repo["relevance_hits"] = hits
    repo["scene"] = classify_scene(repo, hits)
    repo["delta_48h"] = delta_48h
    repo["growth_window_hours"] = observed_hours
    repo["normalized_48h_delta"] = normalized_48h_delta
    repo["stars_per_day"] = round(stars_per_day, 1) if stars_per_day is not None else None
    repo["recent_search_signal"] = recent_search_signal
    repo["rank_score"] = round(growth_signal * 8 + math.log10(max(stars, 1)) * 2, 2)
    return repo


def format_count(value: int | float | None) -> str:
    if value is None:
        return "未知"
    return f"{int(value):,}"


def recent_push_cutoff(repo: dict[str, Any]) -> str:
    match = re.search(r"pushed:>(\d{4}-\d{2}-\d{2})", str(repo.get("search_query") or ""))
    return match.group(1) if match else ""


def growth_label(repo: dict[str, Any]) -> str:
    parts = [f"当前 {format_count(repo.get('stars'))} stars"]
    if repo.get("delta_48h") is not None:
        hours = float(repo.get("growth_window_hours") or 0)
        label = f"近 {hours:.0f} 小时 +{format_count(repo.get('delta_48h'))}"
        if repo.get("normalized_48h_delta") is not None and hours < 42:
            label += f"（按 48 小时折算约 +{format_count(repo.get('normalized_48h_delta'))}）"
        parts.append(label)
    if repo.get("trending_today_stars"):
        parts.append(f"Trending 今日 +{format_count(repo.get('trending_today_stars'))}")
    if repo.get("delta_48h") is None and not repo.get("trending_today_stars"):
        if repo.get("stars_per_day") is not None:
            parts.append(f"约 {repo.get('stars_per_day')} stars/天")
        elif repo.get("pushed_at"):
            parts.append(f"近期有 push（{str(repo.get('pushed_at'))[:10]}），等待下一次快照计算 48 小时增长")
        elif recent_push_cutoff(repo):
            parts.append(f"匹配 pushed:>{recent_push_cutoff(repo)}，等待下一次快照计算 48 小时增长")
        else:
            parts.append("进入 GitHub 仓库搜索结果，等待下一次快照计算 48 小时增长")
    return "，".join(parts)


def why(repo: dict[str, Any]) -> str:
    hits = "、".join(repo.get("relevance_hits") or [])
    signals: list[str] = []
    if repo.get("delta_48h") is not None and repo.get("delta_48h") > 0:
        hours = float(repo.get("growth_window_hours") or 0)
        signals.append(f"近 {hours:.0f} 小时 star +{format_count(repo.get('delta_48h'))}")
    if repo.get("trending_today_stars"):
        signals.append(f"GitHub Trending 今日 +{format_count(repo.get('trending_today_stars'))}")
    if not signals:
        if repo.get("stars_per_day") is not None:
            signals.append(f"新近活跃，star 速度约 {repo.get('stars_per_day')} / 天")
        elif repo.get("pushed_at"):
            signals.append(f"最近 push 于 {str(repo.get('pushed_at'))[:10]}，等待下一次快照计算真实增长")
        elif recent_push_cutoff(repo):
            signals.append(f"匹配 pushed:>{recent_push_cutoff(repo)}，等待下一次快照计算真实增长")
        else:
            signals.append("进入 GitHub 仓库搜索结果，等待下一次快照计算真实增长")
    return f"{'；'.join(signals)}，且命中 {hits or repo.get('scene')}。"


KNOWN_REPO_EXPLAINERS = {
    "alishahryar1/free-claude-code": (
        "一个非官方的 Claude Code 免费使用入口，支持在终端、VS Code 或 Discord 里调用 Claude Code。",
        "想低成本试 Claude Code、用 AI 辅助写代码但还不想直接上官方付费方案的人。",
    ),
    "anil-matcha/open-generative-ai": (
        "一个可自托管的 AI 图片和视频生成工作室，集成 200+ 生成模型，主打开源部署和不限用。",
        "做 AI 生图/视频工具、内容生成产品，或者想自己部署生成式 AI 工作台的人。",
    ),
    "mattpocock/skills": (
        "一个 Claude skills 配置样例库，展示如何把常用能力拆成可复用的 agent 技能。",
        "正在给 Claude、Codex 或其他编程 agent 搭技能库、工作流模板的人。",
    ),
    "posthog/posthog": (
        "一个开源产品数据平台，把埋点分析、会话回放、实验、错误追踪和 AI 产品助手放在一起。",
        "做 SaaS、增长分析、产品实验、用户行为分析，或者想自建产品数据平台的人。",
    ),
    "davila7/claude-code-templates": (
        "一个 Claude Code 配置和监控工具，帮你快速生成项目里的 Claude Code 模板和工作流配置。",
        "重度使用 Claude Code、想标准化项目提示词/命令/配置的开发者和团队。",
    ),
    "cjackhwang/ds2api": (
        "一个把 DeepSeek、Claude、OpenAI 等不同模型协议统一成 API 的中间层，支持多账号轮转。",
        "做模型接口代理、账号池、多模型兼容，或者要把不同模型接到同一套应用里的人。",
    ),
    "roocodeinc/roo-code": (
        "一个 VS Code 里的 AI 编程 agent 工具，把多个代码助手放进编辑器工作流。",
        "想在 IDE 里用 AI 写代码、改代码、拆任务，或者评估 AI 编程 agent 的开发者。",
    ),
    "deepseek-ai/deepep": (
        "一个给大模型 MoE 训练/推理用的高性能专家并行通信库。",
        "做大模型训练、推理基础设施、GPU 集群通信优化的人。",
    ),
    "huggingface/ml-intern": (
        "一个开源 ML 工程助手，目标是读论文、训练模型并交付机器学习模型。",
        "做机器学习工程、论文复现、模型训练自动化，或者关注 AI 研发 agent 的人。",
    ),
    "zilliztech/claude-context": (
        "一个给 Claude Code 用的代码搜索 MCP，把整个代码库变成 agent 可检索的上下文。",
        "代码库较大、想让 Claude/Codex 更准地理解项目上下文的开发者。",
    ),
}


def repo_text(repo: dict[str, Any]) -> str:
    return " ".join(
        [
            str(repo.get("full_name", "")),
            str(repo.get("description", "")),
            " ".join(repo.get("topics") or []),
        ]
    ).lower()


def short_description(repo: dict[str, Any]) -> str:
    desc = (repo.get("description") or "").strip()
    if not desc:
        return "仓库简介暂时不足，只能先按项目名和增长信号判断。"
    desc = re.sub(r"\s+", " ", desc)
    if len(desc) > 80:
        desc = desc[:77].rstrip() + "..."
    return desc


def what_it_does_for(repo: dict[str, Any]) -> str:
    key = str(repo.get("full_name", "")).lower()
    if key in KNOWN_REPO_EXPLAINERS:
        return KNOWN_REPO_EXPLAINERS[key][0]

    text = repo_text(repo)
    if "image" in text and "video" in text and ("generation" in text or "generative" in text):
        return "一个 AI 图片/视频生成工具或工作台，用来生成、管理或部署多模态内容生产能力。"
    if "claude code" in text and ("template" in text or "monitor" in text):
        return "一个 Claude Code 配置工具，用来管理项目提示词、模板和自动化工作流。"
    if "mcp" in text and ("code" in text or "context" in text or "search" in text):
        return "一个 MCP/代码上下文工具，用来让 AI agent 更好地检索和理解项目代码。"
    if "api" in text and any(term in text for term in ("openai", "claude", "deepseek", "gemini")):
        return "一个模型 API 适配或代理工具，用来统一不同模型服务的调用方式。"
    if "agent" in text and ("code" in text or "developer" in text or "editor" in text):
        return "一个 AI 编程 agent 工具，用来在开发流程里自动写代码、改代码或处理任务。"
    if "agent" in text or "workflow" in text or "scheduled job" in text:
        return "一个 AI agent / 工作流工具，用来管理 agent 会话、任务调度或自动化执行流程。"
    if "rag" in text or "embedding" in text or "vector" in text:
        return "一个 RAG/向量检索相关工具，用来给 AI 应用接入知识库和上下文检索。"
    if "inference" in text or "llama" in text or "model" in text:
        return "一个模型训练或推理相关工具，用来部署、优化或运行 AI 模型。"
    if "product analytics" in text or "analytics" in text:
        return "一个产品数据分析工具，用来做埋点、用户行为分析和产品增长实验。"
    return f"{repo.get('scene', 'AI 工具')}，仓库简介：{short_description(repo)}"


def target_users_for(repo: dict[str, Any]) -> str:
    key = str(repo.get("full_name", "")).lower()
    if key in KNOWN_REPO_EXPLAINERS:
        return KNOWN_REPO_EXPLAINERS[key][1]

    scene = str(repo.get("scene") or "")
    text = repo_text(repo)
    if "image" in text and ("video" in text or "generation" in text):
        return "做内容生成、AI 图片/视频产品、自托管生成工具的人。"
    if "claude" in text or "codex" in text:
        return "使用 Claude、Codex 或其他 coding agent 的开发者和团队。"
    if "mcp" in text:
        return "给 AI agent 接工具、接知识库、接代码上下文的人。"
    if "api" in text and any(term in text for term in ("openai", "claude", "deepseek", "gemini")):
        return "需要统一模型 API、做模型代理或多模型接入的人。"
    if "agent" in scene.lower() or "agent" in text:
        return "做 AI agent、自动化工作流、AI 编程助手的人。"
    if "RAG" in scene or "rag" in text or "vector" in text:
        return "做知识库问答、企业检索、RAG 应用的人。"
    if "模型" in scene or "inference" in text or "model" in text:
        return "做大模型训练、推理部署、AI 基础设施的人。"
    return "关注 AI 工具、AI 产品机会、开源项目选型的人。"


def why_now_for(repo: dict[str, Any]) -> str:
    signals: list[str] = []
    if repo.get("delta_48h") is not None and repo.get("delta_48h") > 0:
        hours = float(repo.get("growth_window_hours") or 0)
        signals.append(f"近 {hours:.0f} 小时 star +{format_count(repo.get('delta_48h'))}")
    if repo.get("trending_today_stars"):
        signals.append(f"Trending 今日 +{format_count(repo.get('trending_today_stars'))}")
    if signals:
        return "；".join(signals) + "，说明社区正在快速关注。"
    if repo.get("stars_per_day") is not None:
        return f"star 增长速度约 {repo.get('stars_per_day')} / 天，值得放进观察列表。"
    if repo.get("pushed_at"):
        return f"最近 push 于 {str(repo.get('pushed_at'))[:10]}，已进入仓库搜索结果；下一次快照后会计算真实 48 小时增长。"
    if recent_push_cutoff(repo):
        return f"匹配 pushed:>{recent_push_cutoff(repo)} 的近期活跃条件；下一次快照后会计算真实 48 小时增长。"
    return "已进入仓库搜索结果；下一次快照后会计算真实 48 小时增长。"


def intro_for(repo: dict[str, Any]) -> str:
    desc = (repo.get("description") or "暂无仓库简介").strip()
    if len(desc) > 160:
        desc = desc[:157].rstrip() + "..."
    scene = repo.get("scene") or "AI 工具"
    hits = "、".join(repo.get("relevance_hits") or [])
    if re.search(r"[\u4e00-\u9fff]", desc):
        return desc
    suffix = f"，关键词命中 {hits}" if hits else ""
    return f"这是一个偏 {scene} 的开源项目{suffix}；仓库原始简介：{desc}"


def render_digest(day: str, selected: list[dict[str, Any]], total: int, baseline_only: bool) -> str:
    lines = [
        f"GitHub AI 项目 Star 增长日报 | {day}",
        "",
        f"口径：优先按近 48 小时 star 增长排序；没有足够历史快照时，临时参考 GitHub 仓库搜索结果和近期 push 活跃度。",
        f"今天筛选 {total} 个 GitHub AI 相关候选，选出 {len(selected)} 个两天内增长较快或增长信号明确的项目。",
    ]
    if baseline_only:
        lines.append("首次运行已建立 star 基线；从后续日报开始会逐步切到真实近 48 小时增长。")
    lines.extend(["", "重点项目："])

    if not selected:
        lines.append("今天没有达到阈值的 AI 相关增长项目。")
        return "\n".join(lines)

    for index, repo in enumerate(selected, start=1):
        lines.extend(
            [
                f"{index}. {repo.get('full_name')} ({repo.get('scene')})",
                f"   增长：{growth_label(repo)}",
                f"   做什么的：{what_it_does_for(repo)}",
                f"   适合什么人用：{target_users_for(repo)}",
                f"   为什么现在值得看：{why_now_for(repo)}",
                f"   项目链接：{repo.get('html_url')}",
            ]
        )
    lines.extend(
        [
            "",
            "来源：OpenClaw CDP 浏览器像人工一样使用 GitHub 搜索框检索仓库，并结合本地 star 快照。",
        ]
    )
    return "\n".join(lines)


def score_for_digest(repo: dict[str, Any], index: int) -> int:
    if index <= 3 and (
        int(repo.get("normalized_48h_delta") or repo.get("delta_48h") or 0) >= 50
        or int(repo.get("trending_today_stars") or 0) >= 50
    ):
        return 9
    return 8


def digest_item_for_repo(repo: dict[str, Any], day: str, index: int, settings: dict[str, Any]) -> dict[str, Any]:
    full_name = repo.get("full_name", "")
    hits = repo.get("relevance_hits") or []
    url = repo.get("html_url") or f"https://github.com/{full_name}"
    what_it_does = what_it_does_for(repo)
    target_users = target_users_for(repo)
    why_now = why_now_for(repo)
    return {
        "title": f"GitHub 增长项目：{full_name}",
        "author": repo.get("owner") or str(full_name).split("/", 1)[0],
        "url": url,
        "canonical_url": url,
        "project_url": url,
        "source_urls": [url, *(repo.get("trending_sources") or [])],
        "platform": "github",
        "source_mode": "monitor",
        "source_name": "GitHub AI Star Radar",
        "published_at": now_dt(settings).isoformat(timespec="seconds"),
        "score": score_for_digest(repo, index),
        "one_liner": what_it_does,
        "what_it_does": what_it_does,
        "target_users": target_users,
        "why_now": why_now,
        "summary": [
            what_it_does,
            f"适合：{target_users}",
            f"增长：{growth_label(repo)}。",
        ],
        "reason": why_now,
        "topics": [repo.get("scene", "AI 工具"), *hits],
        "verdict": "digest",
        "content_id": sha256_hex(f"github-star-radar|{day}|{full_name.lower()}"),
        "processed_at": now_dt(settings).isoformat(timespec="seconds"),
        "day": day,
        "realtime_sent": False,
    }


def record_digest_candidates(
    selected: list[dict[str, Any]], total_repos: int, scored_repos: int, settings: dict[str, Any]
) -> dict[str, Any]:
    day = today_key(settings)
    digest_candidates = load_digest_candidates()
    daily_stats = load_daily_stats()
    day_stats = ensure_day(daily_stats, day)
    day_stats["feed_scanned"] = int(day_stats.get("feed_scanned", 0)) + total_repos
    day_stats["scored"] = int(day_stats.get("scored", 0)) + scored_repos

    added = 0
    updated = 0
    items = []
    for index, repo in enumerate(selected, start=1):
        item = digest_item_for_repo(repo, day, index, settings)
        was_added, stored = upsert_digest_candidate(digest_candidates, day, item)
        if was_added:
            added += 1
        else:
            updated += 1
        items.append(stored.get("title", item["title"]))
    day_stats["digest_candidates"] = int(day_stats.get("digest_candidates", 0)) + added
    save_digest_candidates(digest_candidates)
    save_daily_stats(daily_stats)
    return {"ok": True, "day": day, "added": added, "updated": updated, "items": items}


def load_state() -> dict[str, Any]:
    return read_json(STATE_PATH, {"repos": {}, "runs": []})


def save_state(state: dict[str, Any]) -> None:
    write_json(STATE_PATH, state)


def run(args: argparse.Namespace) -> dict[str, Any]:
    settings = load_settings()
    state = load_state()
    day = now_dt(settings).date().isoformat()

    if args.send and not args.force and state.get("last_digest_date") == day:
        return {"ok": True, "skipped": "already_sent_today", "day": day}

    repos = collect_cdp_trending(args)
    scored: list[dict[str, Any]] = []
    had_growth_baseline = False
    now_iso = now_dt(settings).isoformat(timespec="seconds")
    previous_repos = state.setdefault("repos", {})
    for key, repo in repos.items():
        previous = previous_repos.get(key)
        had_growth_baseline = had_growth_baseline or bool(growth_snapshot(previous, settings))
        item = score_repo(repo, previous, settings)
        if item:
            scored.append(item)
        previous_repos[key] = repo_state_record(repo, previous, now_iso, settings)

    selected = sorted(scored, key=lambda repo: repo["rank_score"], reverse=True)[: args.limit]
    if len(selected) < args.limit:
        selected_keys = {str(repo.get("full_name", "")).lower() for repo in selected}
        supplemental_items = []
        for key, repo in repos.items():
            if key in selected_keys:
                continue
            item = score_trending_supplement(repo, previous_repos.get(key), settings)
            if item:
                supplemental_items.append(item)
        selected.extend(
            sorted(supplemental_items, key=lambda repo: repo["rank_score"], reverse=True)[
                : max(0, args.limit - len(selected))
            ]
        )
    text = render_digest(day, selected, len(repos), baseline_only=not had_growth_baseline)

    state.setdefault("runs", []).append(
        {
            "day": day,
            "run_at": now_iso,
            "candidates": len(repos),
            "selected": [repo.get("full_name") for repo in selected],
            "sent": bool(args.send),
        }
    )
    state["runs"] = state["runs"][-30:]

    send_result = None
    record_result = None
    if args.record_candidates:
        record_result = record_digest_candidates(selected, len(repos), len(scored), settings)
    if args.send:
        send_result = send_message(settings, "digest", text)
        if send_result.get("ok"):
            state["last_digest_date"] = day
            state["last_digest_at"] = now_iso
    if not args.no_state_write:
        save_state(state)

    return {
        "ok": True,
        "day": day,
        "candidate_count": len(repos),
        "selected_count": len(selected),
        "message": text,
        "record_result": record_result,
        "send_result": send_result,
        "state_path": str(STATE_PATH),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily GitHub AI star growth radar for OpenClaw community-signal.")
    parser.add_argument("--send", action="store_true", help="Send the digest through community-signal settings.")
    parser.add_argument("--record-candidates", action="store_true", help="Write selected repos into community-signal daily digest candidates.")
    parser.add_argument("--force", action="store_true", help="Send even if today's digest was already sent.")
    parser.add_argument("--limit", type=int, default=10, help="Number of projects to include.")
    parser.add_argument("--scrape-limit", type=int, default=25, help="Max repos to scrape from each GitHub search query.")
    parser.add_argument("--cdp-port", type=int, default=9223, help="OpenClaw browser CDP port.")
    parser.add_argument("--timeout-ms", type=int, default=15000, help="CDP page timeout.")
    parser.add_argument("--scrape-retries", type=int, default=2, help="Retries per GitHub search term after first failure.")
    parser.add_argument("--page-settle-ms", type=int, default=800, help="Extra wait after GitHub pages/results look loaded.")
    parser.add_argument("--terms", default="", help="Optional comma-separated GitHub repository search terms.")
    parser.add_argument("--no-state-write", action="store_true", help="Do not update the local star baseline state.")
    args = parser.parse_args()
    result = run(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
