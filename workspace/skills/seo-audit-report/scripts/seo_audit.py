#!/usr/bin/env python3
"""Disabled direct HTTP SEO crawler.

OpenClaw web collection is CDP-only on this machine. This script remains only so
old SEO audit commands fail closed instead of crawling pages through urllib.
"""

import json
import sys


def main() -> int:
    json.dump(
        {
            "status": "disabled",
            "error": "seo-audit direct HTTP crawler is disabled; collect pages through OpenClaw Chrome CDP/browser only",
            "allowed_source": "http://127.0.0.1:9223",
        },
        sys.stdout,
        ensure_ascii=False,
    )
    sys.stdout.write("\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
