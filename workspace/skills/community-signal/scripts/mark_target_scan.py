from __future__ import annotations

import argparse
import json

from common import load_scrape_history, load_settings, now_iso, save_scrape_history


def main() -> None:
    parser = argparse.ArgumentParser(description="Record that a target has been scanned.")
    parser.add_argument("--mode", choices=["person", "monitor"], required=True)
    parser.add_argument("--target-id", required=True)
    parser.add_argument("--new-items", type=int, default=0)
    args = parser.parse_args()

    settings = load_settings()
    history = load_scrape_history()
    target_state = history.setdefault("targets", {}).setdefault(args.target_id, {})
    target_state["mode"] = args.mode
    target_state["last_scraped_at"] = now_iso(settings)
    target_state["last_new_items"] = args.new_items
    if args.new_items > 0:
        target_state["last_new_item_at"] = now_iso(settings)
    save_scrape_history(history)

    print(
        json.dumps(
            {
                "ok": True,
                "target_id": args.target_id,
                "mode": args.mode,
                "new_items": args.new_items,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
