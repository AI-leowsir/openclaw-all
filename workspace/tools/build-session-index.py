#!/usr/bin/env python3
"""
Build a session history index for deep-review discovery.
Scans all .jsonl and .jsonl.reset.* files, extracts metadata,
and produces a date-indexed JSON file for fast lookup.
"""

import json
import re
import os
import sys
import fcntl
from datetime import datetime, timezone, timedelta

SESSIONS_DIR = "/root/.openclaw/agents/main/sessions"
SESSIONS_JSON = os.path.join(SESSIONS_DIR, "sessions.json")
OUTPUT_INDEX = "/root/.openclaw/workspace/memory/review/session-history-index.json"

CST = timezone(timedelta(hours=8))


def parse_utc_ts(ts_str):
    """Parse UTC timestamp string to datetime."""
    if not ts_str:
        return None
    try:
        # Handle formats like "2026-04-12T13:57:19.017Z"
        ts_str = ts_str.rstrip("Z")
        if "." in ts_str:
            return datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
    except Exception:
        return None


def to_beijing(dt):
    """Convert UTC datetime to Beijing time string."""
    if dt is None:
        return None
    return dt.astimezone(CST).isoformat()


def to_beijing_date(dt):
    """Convert UTC datetime to Beijing date string YYYY-MM-DD."""
    if dt is None:
        return None
    return dt.astimezone(CST).strftime("%Y-%m-%d")


def scan_transcript(filepath):
    """Scan a transcript file and extract metadata efficiently."""
    meta = {
        "file": filepath,
        "filename": os.path.basename(filepath),
        "sessionId": None,
        "startTime": None,
        "endTime": None,
        "startTimeBeijing": None,
        "endTimeBeijing": None,
        "startDateBeijing": None,
        "endDateBeijing": None,
        "beijingDates": [],
        "lineCount": 0,
        "userMessageCount": 0,
        "assistantMessageCount": 0,
        "toolResultCount": 0,
        "fileSize": os.path.getsize(filepath),
        "isReset": ".reset." in filepath,
        "resetTimestamp": None,
        "topics": [],
    }

    # Extract reset timestamp from filename if present
    basename = os.path.basename(filepath)
    if ".reset." in basename:
        reset_part = basename.split(".reset.")[1]
        # Convert format like 2026-04-13T02-36-57.175Z -> 2026-04-13T02:36:57.175Z
        reset_ts = reset_part.replace("-", ":", 2)  # only first few dashes
        # Actually need more careful parsing
        parts = reset_part.split("T")
        if len(parts) == 2:
            date_part = parts[0]  # e.g. 2026-04-13
            time_part = parts[1].rstrip("Z")  # e.g. 02-36-57.175
            time_part = time_part.replace("-", ":", 2)
            reset_ts = f"{date_part}T{time_part}Z"
            meta["resetTimestamp"] = reset_ts

    # Extract sessionId from filename UUID
    uuid_part = basename.split(".jsonl")[0]
    meta["sessionId"] = uuid_part

    first_ts = None
    last_ts = None
    dates_seen = set()
    user_snippet_parts = []

    try:
        with open(filepath, "r") as f:
            for i, line in enumerate(f):
                meta["lineCount"] += 1
                try:
                    entry = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

                ts = parse_utc_ts(entry.get("timestamp"))
                if ts:
                    if first_ts is None:
                        first_ts = ts
                    last_ts = ts
                    beijing_date = to_beijing_date(ts)
                    if beijing_date:
                        dates_seen.add(beijing_date)

                entry_type = entry.get("type", "")

                # Count message types
                if entry_type == "message" and "message" in entry:
                    msg = entry["message"]
                    if isinstance(msg, dict):
                        role = msg.get("role", "")
                        if role == "user":
                            meta["userMessageCount"] += 1
                            # Extract first 50 chars of user messages for topic hints
                            content = msg.get("content", "")
                            # content can be a string or a list of {type, text} blocks
                            text = ""
                            if isinstance(content, str):
                                text = content
                            elif isinstance(content, list):
                                # Extract text from content blocks, skip system/memory blocks
                                for block in content:
                                    if isinstance(block, dict) and block.get("type") == "text":
                                        block_text = block.get("text", "")
                                        # Strip memory injection prefix if present
                                        if "<relevant-memories>" in block_text:
                                            end_tag = "</relevant-memories>"
                                            tag_idx = block_text.find(end_tag)
                                            if tag_idx >= 0:
                                                block_text = block_text[tag_idx + len(end_tag):].strip()
                                            else:
                                                continue  # malformed memory block, skip
                                        # Also skip system session reset messages
                                        if block_text.startswith("A new session was started via"):
                                            continue
                                        # Strip feishu conversation metadata prefix
                                        if block_text.startswith("Conversation info (untrusted metadata):"):
                                            # Find the end of the JSON code block after the prefix
                                            marker = "```\n"
                                            last_fence = block_text.rfind(marker)
                                            if last_fence >= 0:
                                                block_text = block_text[last_fence + len(marker):].strip()
                                            else:
                                                continue  # can't parse, skip
                                        # Strip feishu per-message metadata: [message_id: xxx]
                                        # Strip feishu per-message metadata
                                        block_text = re.sub(r"\[message_id:[^\]]*\]\s*\nou_[a-f0-9]+:\s*", "", block_text)
                                        if block_text.strip() and len(block_text.strip()) > 3:
                                            text = block_text.strip()
                                            break
                                snippet = text[:80].replace("\n", " ").strip()
                                if snippet and len(user_snippet_parts) < 5:
                                    user_snippet_parts.append(snippet)
                        elif role == "assistant":
                            meta["assistantMessageCount"] += 1
                elif entry_type == "tool_result":
                    meta["toolResultCount"] += 1

                # For session header
                if entry_type == "session":
                    meta["sessionId"] = entry.get("id", meta["sessionId"])

    except Exception as e:
        meta["error"] = str(e)

    meta["startTime"] = first_ts.isoformat() if first_ts else None
    meta["endTime"] = last_ts.isoformat() if last_ts else None
    meta["startTimeBeijing"] = to_beijing(first_ts)
    meta["endTimeBeijing"] = to_beijing(last_ts)
    meta["startDateBeijing"] = to_beijing_date(first_ts)
    meta["endDateBeijing"] = to_beijing_date(last_ts)
    meta["beijingDates"] = sorted(dates_seen)
    meta["topics"] = user_snippet_parts

    return meta


def build_session_key_map():
    """Build sessionId -> sessionKey mapping from sessions.json."""
    mapping = {}
    try:
        with open(SESSIONS_JSON) as f:
            data = json.load(f)
        for key, info in data.items():
            sid = info.get("sessionId")
            if sid:
                mapping[sid] = {
                    "sessionKey": key,
                    "displayName": info.get("displayName"),
                    "chatType": info.get("chatType"),
                    "groupId": info.get("groupId"),
                    "channel": info.get("channel"),
                }
    except Exception as e:
        print(f"Warning: could not read sessions.json: {e}", file=sys.stderr)
    return mapping


def find_session_key_for_id(session_id, key_map, all_files):
    """Try to find session key for a given sessionId.
    First check current mapping, then check if any active session
    has the same UUID base (same session key produces sequential sessions).
    """
    if session_id in key_map:
        return key_map[session_id]

    # For reset files, we need to match by checking which session key
    # historically produced this sessionId. Since sessions.json only has
    # current IDs, we check if the same UUID appears in any known
    # session key chain. For now, return None and we'll use file-level
    # grouping post-hoc.
    return None


def main():
    # Prevent concurrent runs via lock file
    lock_path = OUTPUT_INDEX + ".lock"
    lock_fd = open(lock_path, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("Another instance is already running, exiting.", file=sys.stderr)
        sys.exit(0)

    print(f"Scanning {SESSIONS_DIR}...", file=sys.stderr)

    # Build sessionId -> sessionKey map from sessions.json
    key_map = build_session_key_map()
    print(f"Known session keys: {len(key_map)}", file=sys.stderr)

    # Collect all transcript files
    all_files = []
    for fname in os.listdir(SESSIONS_DIR):
        if fname == "sessions.json":
            continue
        if fname.endswith(".jsonl") or ".jsonl.reset." in fname:
            all_files.append(os.path.join(SESSIONS_DIR, fname))

    print(f"Found {len(all_files)} transcript files", file=sys.stderr)

    # Scan each file
    entries = []
    for i, fp in enumerate(sorted(all_files)):
        print(f"  [{i+1}/{len(all_files)}] {os.path.basename(fp)}...", file=sys.stderr)
        meta = scan_transcript(fp)

        # Try to resolve session key
        sid = meta["sessionId"]
        key_info = find_session_key_for_id(sid, key_map, all_files)
        if key_info:
            meta["sessionKey"] = key_info["sessionKey"]
            meta["displayName"] = key_info.get("displayName")
            meta["chatType"] = key_info.get("chatType")
            meta["groupId"] = key_info.get("groupId")
            meta["channel"] = key_info.get("channel")
        else:
            meta["sessionKey"] = None
            meta["displayName"] = None
            meta["chatType"] = None
            meta["groupId"] = None
            meta["channel"] = None

        entries.append(meta)

    # Build date index: date -> list of session entries active on that date
    date_index = {}
    for entry in entries:
        for d in entry.get("beijingDates", []):
            if d not in date_index:
                date_index[d] = []
            date_index[d].append({
                "sessionId": entry["sessionId"],
                "sessionKey": entry["sessionKey"],
                "displayName": entry["displayName"],
                "chatType": entry["chatType"],
                "filename": entry["filename"],
                "file": entry["file"],
                "startTimeBeijing": entry["startTimeBeijing"],
                "endTimeBeijing": entry["endTimeBeijing"],
                "lineCount": entry["lineCount"],
                "userMessageCount": entry["userMessageCount"],
                "assistantMessageCount": entry["assistantMessageCount"],
                "toolResultCount": entry["toolResultCount"],
                "fileSize": entry["fileSize"],
                "isReset": entry["isReset"],
                "topics": entry["topics"],
            })

    # Output
    output = {
        "generatedAt": datetime.now(CST).isoformat(),
        "totalFiles": len(all_files),
        "totalEntries": len(entries),
        "dateRange": {
            "earliest": min((e["startDateBeijing"] for e in entries if e["startDateBeijing"]), default=None),
            "latest": max((e["endDateBeijing"] for e in entries if e["endDateBeijing"]), default=None),
        },
        "knownSessionKeys": {k: v for k, v in key_map.items()},
        "dateIndex": dict(sorted(date_index.items())),
        "allSessions": entries,
    }

    os.makedirs(os.path.dirname(OUTPUT_INDEX), exist_ok=True)
    # Atomic write: write to temp file first, then rename to prevent corruption
    tmp_path = OUTPUT_INDEX + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    os.replace(tmp_path, OUTPUT_INDEX)

    print(f"\nIndex written to {OUTPUT_INDEX}", file=sys.stderr)
    print(f"Total dates covered: {len(date_index)}", file=sys.stderr)
    print(f"Date range: {output['dateRange']}", file=sys.stderr)

    # Print summary
    for d in sorted(date_index.keys()):
        sessions = date_index[d]
        total_user = sum(s["userMessageCount"] for s in sessions)
        print(f"  {d}: {len(sessions)} sessions, {total_user} user messages", file=sys.stderr)


if __name__ == "__main__":
    main()
