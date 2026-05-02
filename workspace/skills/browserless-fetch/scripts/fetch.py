#!/usr/bin/env python3
"""Disabled browserless fetch entrypoint.

OpenClaw local policy requires all web page collection to use the
OpenClaw-managed Chrome CDP/browser session on http://127.0.0.1:9223.
"""
from __future__ import annotations

import json
import sys


def main() -> None:
    print(
        json.dumps(
            {
                "status": "disabled",
                "error": "browserless-fetch is disabled; use OpenClaw Chrome CDP/browser only",
                "allowed_source": "http://127.0.0.1:9223",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
