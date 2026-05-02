from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import (
    ensure_day,
    has_digest_delivery,
    has_realtime_delivery,
    load_delivery_history,
    load_digest_candidates,
    load_daily_stats,
    load_settings,
    now_iso,
    parse_day,
    record_delivery,
    render_digest_message,
    save_delivery_history,
    save_daily_stats,
    send_message,
    sort_items,
    write_text,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and optionally send the daily digest.")
    parser.add_argument("--date", default="today", help="YYYY-MM-DD or 'today'")
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    settings = load_settings()
    day = parse_day(args.date, settings)
    digest_candidates = load_digest_candidates()
    delivery_history = load_delivery_history()
    daily_stats = load_daily_stats()

    day_stats = ensure_day(daily_stats, day)
    if args.send and day_stats.get("digest_summary_sent_at") and not args.force:
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "digest already sent",
                    "day": day,
                    "sent_at": day_stats["digest_summary_sent_at"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    all_items = digest_candidates.get("days", {}).get(day, [])
    realtime_count = sum(1 for item in all_items if item.get("realtime_sent"))
    unique = {item["content_id"]: item for item in all_items}
    source_counts: dict[str, int] = {}
    for item in unique.values():
        platform = str(item.get("platform") or "unknown")
        source_counts[platform] = source_counts.get(platform, 0) + 1
    unsent = [
        item
        for item in unique.values()
        if not item.get("realtime_sent")
        and not has_realtime_delivery(delivery_history, item)
        and not has_digest_delivery(delivery_history, item, day)
    ]
    selected = sort_items(unsent)[: int(settings["digest_max_items"])]
    text = render_digest_message(day, day_stats, selected, len(unique), realtime_count, source_counts)
    empty_digest = not selected and len(unique) == 0

    rendered_path = Path(__file__).resolve().parent.parent / "state" / "rendered" / f"digest-{day}.md"
    write_text(rendered_path, text + "\n")

    send_result = None
    if args.send:
        if empty_digest and not settings.get("send_empty_digest", False):
            send_result = {"ok": True, "skipped": "empty-digest"}
        else:
            send_result = send_message(settings, "digest", text)
        if send_result.get("ok") and not send_result.get("skipped"):
            for item in selected:
                record_delivery(delivery_history, item, "digest", settings)
            day_stats["digest_sent"] = len(selected)
            day_stats["digest_summary_sent_at"] = now_iso(settings)
            day_stats["digest_render_path"] = str(rendered_path)
            save_delivery_history(delivery_history)
            save_daily_stats(daily_stats)

    print(
        json.dumps(
            {
                "ok": True,
                "day": day,
                "selected_count": len(selected),
                "realtime_count": realtime_count,
                "rendered_path": str(rendered_path),
                "send_result": send_result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
