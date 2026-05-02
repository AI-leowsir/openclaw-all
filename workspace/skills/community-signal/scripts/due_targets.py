from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta

from common import (
    load_scrape_history,
    load_settings,
    load_targets,
    monitor_target_id,
    now_dt,
    person_target_id,
)


def is_due(last_scraped_at: str | None, interval_hours: int, now: datetime) -> bool:
    if not last_scraped_at:
        return True
    try:
        last = datetime.fromisoformat(last_scraped_at)
    except ValueError:
        return True
    return last + timedelta(hours=interval_hours) <= now


def build_person_due(now: datetime) -> list[dict]:
    targets = load_targets()
    settings = load_settings()
    history = load_scrape_history()
    results = []
    all_targets = targets.get("person_targets", {}).get("core_targets", []) + targets.get(
        "person_targets", {}
    ).get("temporary_targets", [])
    for target in all_targets:
        tid = person_target_id(target)
        interval = int(target.get("scrape_interval_hours", settings["default_scrape_interval_hours"]))
        state = history.get("targets", {}).get(tid, {})
        if not is_due(state.get("last_scraped_at"), interval, now):
            continue
        results.append(target | {"target_id": tid, "mode": "person"})
    return results


def build_monitor_due(now: datetime) -> list[dict]:
    targets = load_targets()
    settings = load_settings()
    history = load_scrape_history()
    results = []
    for target in targets.get("monitoring_targets", []):
        tid = monitor_target_id(target)
        interval = int(target.get("scrape_interval_hours", settings["default_scrape_interval_hours"]))
        state = history.get("targets", {}).get(tid, {})
        if not is_due(state.get("last_scraped_at"), interval, now):
            continue
        results.append(target | {"target_id": tid, "mode": "monitor"})
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="List due person/community targets.")
    parser.add_argument("--mode", choices=["person", "monitor", "all"], default="all")
    args = parser.parse_args()

    settings = load_settings()
    now = now_dt(settings)
    due = []
    if args.mode in {"person", "all"}:
        due.extend(build_person_due(now))
    if args.mode in {"monitor", "all"}:
        due.extend(build_monitor_due(now))

    print(json.dumps({"count": len(due), "items": due}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
