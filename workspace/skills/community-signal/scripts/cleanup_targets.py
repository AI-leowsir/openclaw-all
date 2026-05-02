from __future__ import annotations

import json
from datetime import date

from common import load_targets, save_targets


def main() -> None:
    targets = load_targets()
    today = date.today().isoformat()
    temporary = targets.setdefault("person_targets", {}).setdefault("temporary_targets", [])
    kept = []
    removed = []
    for target in temporary:
        expires_at = str(target.get("expires_at", "")).strip()
        if expires_at and expires_at < today:
            removed.append(target)
        else:
            kept.append(target)
    targets["person_targets"]["temporary_targets"] = kept
    save_targets(targets)
    print(json.dumps({"ok": True, "removed": removed}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
