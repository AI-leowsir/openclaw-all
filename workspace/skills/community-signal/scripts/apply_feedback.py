from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import expand_user, load_settings


SECTION_HEADER = "## 情报推送偏好"


def upsert_feedback(memory_path: Path, feedback: str) -> bool:
    line = f"- {feedback.strip()}"
    text = memory_path.read_text(encoding="utf-8") if memory_path.exists() else "# MEMORY.md\n\n"
    if line in text:
        return False

    if SECTION_HEADER not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += f"\n{SECTION_HEADER}\n\n{line}\n"
        memory_path.write_text(text, encoding="utf-8")
        return True

    pattern = re.compile(rf"(^## .*$)", re.MULTILINE)
    start = text.index(SECTION_HEADER)
    section_end = len(text)
    after_header = text[start + len(SECTION_HEADER) :]
    match = pattern.search(after_header)
    if match:
        section_end = start + len(SECTION_HEADER) + match.start()
    updated = text[:section_end].rstrip() + f"\n{line}\n" + text[section_end:]
    memory_path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Append a long-term push preference into MEMORY.md.")
    parser.add_argument("--feedback", required=True)
    args = parser.parse_args()

    settings = load_settings()
    memory_path = Path(expand_user(settings["memory_file"]))
    changed = upsert_feedback(memory_path, args.feedback)
    print(
        json.dumps(
            {"ok": True, "changed": changed, "memory_file": str(memory_path)},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
