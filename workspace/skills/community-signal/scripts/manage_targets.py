from __future__ import annotations

import argparse
import json
from datetime import timedelta

from common import load_settings, load_targets, now_dt, save_targets


def comma_topics(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def list_targets() -> None:
    print(json.dumps(load_targets(), ensure_ascii=False, indent=2))


def add_person(args: argparse.Namespace) -> None:
    settings = load_settings()
    targets = load_targets()
    now = now_dt(settings).date()
    entry = {
        "name": args.name,
        "platform": args.platform,
        "profile_url": args.profile_url,
        "focus_topics": comma_topics(args.topics),
        "priority": args.priority,
        "scrape_interval_hours": args.scrape_interval_hours,
    }
    if args.temporary_days:
        entry["added_at"] = now.isoformat()
        entry["expires_at"] = (now + timedelta(days=args.temporary_days)).isoformat()
        bucket = targets.setdefault("person_targets", {}).setdefault("temporary_targets", [])
    else:
        bucket = targets.setdefault("person_targets", {}).setdefault("core_targets", [])
    bucket.append(entry)
    save_targets(targets)
    print(json.dumps({"ok": True, "added": entry}, ensure_ascii=False, indent=2))


def remove_person(args: argparse.Namespace) -> None:
    targets = load_targets()
    removed = []
    for key in ["core_targets", "temporary_targets"]:
        bucket = targets.setdefault("person_targets", {}).setdefault(key, [])
        kept = []
        for item in bucket:
            if item.get("name") == args.name:
                removed.append(item)
            else:
                kept.append(item)
        targets["person_targets"][key] = kept
    save_targets(targets)
    print(json.dumps({"ok": True, "removed": removed}, ensure_ascii=False, indent=2))


def add_monitor(args: argparse.Namespace) -> None:
    targets = load_targets()
    entry = {
        "name": args.name,
        "platform": args.platform,
        "community_url": args.community_url,
        "type": "community_monitor",
        "focus_topics": comma_topics(args.topics),
        "digest_threshold": args.digest_threshold,
        "realtime_threshold": args.realtime_threshold,
        "scrape_interval_hours": args.scrape_interval_hours,
        "max_posts_per_scan": args.max_posts_per_scan,
    }
    targets.setdefault("monitoring_targets", []).append(entry)
    save_targets(targets)
    print(json.dumps({"ok": True, "added": entry}, ensure_ascii=False, indent=2))


def remove_monitor(args: argparse.Namespace) -> None:
    targets = load_targets()
    removed = []
    kept = []
    for item in targets.get("monitoring_targets", []):
        if item.get("name") == args.name:
            removed.append(item)
        else:
            kept.append(item)
    targets["monitoring_targets"] = kept
    save_targets(targets)
    print(json.dumps({"ok": True, "removed": removed}, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage community-signal targets.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list")

    add_person_parser = sub.add_parser("add-person")
    add_person_parser.add_argument("--name", required=True)
    add_person_parser.add_argument("--platform", required=True)
    add_person_parser.add_argument("--profile-url", required=True)
    add_person_parser.add_argument("--topics", required=True)
    add_person_parser.add_argument("--priority", default="medium")
    add_person_parser.add_argument("--scrape-interval-hours", type=int, default=8)
    add_person_parser.add_argument("--temporary-days", type=int, default=0)

    remove_person_parser = sub.add_parser("remove-person")
    remove_person_parser.add_argument("--name", required=True)

    add_monitor_parser = sub.add_parser("add-monitor")
    add_monitor_parser.add_argument("--name", required=True)
    add_monitor_parser.add_argument("--platform", required=True)
    add_monitor_parser.add_argument("--community-url", required=True)
    add_monitor_parser.add_argument("--topics", required=True)
    add_monitor_parser.add_argument("--digest-threshold", type=int, default=7)
    add_monitor_parser.add_argument("--realtime-threshold", type=int, default=9)
    add_monitor_parser.add_argument("--scrape-interval-hours", type=int, default=4)
    add_monitor_parser.add_argument("--max-posts-per-scan", type=int, default=50)

    remove_monitor_parser = sub.add_parser("remove-monitor")
    remove_monitor_parser.add_argument("--name", required=True)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "list":
        list_targets()
    elif args.command == "add-person":
        add_person(args)
    elif args.command == "remove-person":
        remove_person(args)
    elif args.command == "add-monitor":
        add_monitor(args)
    elif args.command == "remove-monitor":
        remove_monitor(args)


if __name__ == "__main__":
    main()
