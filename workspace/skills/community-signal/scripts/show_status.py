from __future__ import annotations

import argparse
import json

from common import (
    load_daily_stats,
    load_delivery_history,
    load_digest_candidates,
    load_settings,
    parse_day,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Show daily delivery status.")
    parser.add_argument("--date", default="today")
    args = parser.parse_args()

    settings = load_settings()
    day = parse_day(args.date, settings)
    stats = load_daily_stats().get("days", {}).get(day, {})
    candidates = load_digest_candidates().get("days", {}).get(day, [])
    delivery_history = load_delivery_history().get("items", {})
    realtime_delivered = sum(
        1 for item in delivery_history.values() if item.get("realtime_at", "").startswith(day)
    )

    print(
        json.dumps(
            {
                "day": day,
                "stats": stats,
                "digest_candidate_count": len(candidates),
                "realtime_delivered": realtime_delivered,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
