from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import load_settings, send_message


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a text message using the configured backend.")
    parser.add_argument("--kind", choices=["digest", "realtime", "manual"], default="manual")
    parser.add_argument("--message", help="Literal message text")
    parser.add_argument("--file", help="Read message body from file")
    args = parser.parse_args()

    if not args.message and not args.file:
        raise SystemExit("--message or --file is required")

    text = args.message or Path(args.file).read_text(encoding="utf-8")
    result = send_message(load_settings(), args.kind, text)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
