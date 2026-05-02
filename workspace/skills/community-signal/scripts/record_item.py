from __future__ import annotations

import argparse
import json

from common import (
    ensure_day,
    has_realtime_delivery,
    load_delivery_history,
    load_digest_candidates,
    load_daily_stats,
    load_input_json,
    load_scrape_history,
    load_settings,
    normalize_item,
    recent_realtime_within,
    record_delivery,
    render_realtime_message,
    save_delivery_history,
    save_digest_candidates,
    save_daily_stats,
    save_scrape_history,
    send_message,
    upsert_digest_candidate,
    upsert_scrape_item,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a fetched+scored item and route it.")
    parser.add_argument("--input", help="JSON file path. Reads stdin when omitted.")
    args = parser.parse_args()

    settings = load_settings()
    raw = load_input_json(args.input)
    item = normalize_item(raw, settings)

    scrape_history = load_scrape_history()
    delivery_history = load_delivery_history()
    daily_stats = load_daily_stats()
    digest_candidates = load_digest_candidates()

    day = item["day"]
    day_stats = ensure_day(daily_stats, day)
    day_stats["scanned"] += 1

    was_seen, _ = upsert_scrape_item(scrape_history, item, settings)
    if was_seen:
        day_stats["duplicates"] += 1
        save_scrape_history(scrape_history)
        save_delivery_history(delivery_history)
        save_daily_stats(daily_stats)
        save_digest_candidates(digest_candidates)
        print(
            json.dumps(
                {
                    "ok": True,
                    "content_id": item["content_id"],
                    "decision": "duplicate_skip",
                    "candidate_added": False,
                    "send_result": None,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    decision = "ignore"
    send_result = None
    candidate_added = False

    if item["score"] < int(settings["digest_min_score"]):
        day_stats["ignored"] += 1
    else:
        item["realtime_sent"] = False
        added, candidate = upsert_digest_candidate(digest_candidates, day, item)
        candidate_added = added
        if added:
            day_stats["digest_candidates"] += 1
        item = candidate
        decision = "digest"

        realtime_allowed = (
            item["score"] >= int(settings["realtime_push_score"])
            and not has_realtime_delivery(delivery_history, item)
            and day_stats["realtime_sent"] < int(settings["realtime_max_per_day"])
            and not recent_realtime_within(
                delivery_history,
                settings,
                int(settings.get("realtime_cooldown_minutes", 0)),
            )
        )
        if realtime_allowed:
            text = render_realtime_message(item)
            send_result = send_message(settings, "realtime", text)
            if send_result.get("ok"):
                item["realtime_sent"] = True
                decision = "realtime"
                day_stats["realtime_sent"] += 1
                record_delivery(delivery_history, item, "realtime", settings)

    save_scrape_history(scrape_history)
    save_delivery_history(delivery_history)
    save_daily_stats(daily_stats)
    save_digest_candidates(digest_candidates)

    print(
        json.dumps(
            {
                "ok": True,
                "content_id": item["content_id"],
                "decision": decision,
                "candidate_added": candidate_added,
                "send_result": send_result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
