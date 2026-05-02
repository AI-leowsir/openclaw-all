#!/usr/bin/env python3
"""Disabled Tavily search entrypoint.

OpenClaw web collection is CDP-only on this machine. This script remains only so
old references fail closed instead of silently using a search API.
"""

import json
import sys


def main() -> int:
    json.dump(
        {
            "status": "disabled",
            "error": "tavily-search is disabled; use OpenClaw Chrome CDP/browser only",
            "allowed_source": "http://127.0.0.1:9223",
        },
        sys.stdout,
        ensure_ascii=False,
    )
    sys.stdout.write("\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
