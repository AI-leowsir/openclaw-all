from __future__ import annotations

import json
import subprocess

from common import load_settings


SCAN_JOB_NAME = "community-signal-scan"
DIGEST_JOB_NAME = "community-signal-digest"


def run_json(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr or proc.stdout or f"command failed: {' '.join(cmd)}")
    return json.loads(proc.stdout or "{}")


def existing_jobs(binary: str) -> dict[str, dict]:
    result = run_json([binary, "cron", "list", "--all", "--json"])
    return {job.get("name", ""): job for job in result.get("jobs", [])}


def add_job(binary: str, args: list[str]) -> dict:
    return run_json([binary, "cron", "add", "--json", *args])


def edit_job(binary: str, job_id: str, args: list[str]) -> dict:
    proc = subprocess.run([binary, "cron", "edit", job_id, *args], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr or proc.stdout or f"command failed: {binary} cron edit {job_id}")
    return {"id": job_id, "ok": True, "stdout": proc.stdout.strip()}


def main() -> None:
    settings = load_settings()
    binary = settings.get("openclaw_binary", "openclaw")
    tz = settings.get("timezone", "Asia/Shanghai")
    digest_hour, digest_minute = settings.get("digest_time", "17:00").split(":")
    digest_expr = f"{int(digest_minute)} {int(digest_hour)} * * *"
    scan_expr = "45 23 * * *"

    jobs = existing_jobs(binary)
    created = []
    updated = []

    scan_message = (
        "Use the exec tool to run this command exactly once:\n"
        "python3 /Users/wusir/.openclaw/workspace/skills/community-signal/scripts/run_scan.py --mode monitor --platform scys --force\n"
        "Do not add ask/security/allowlist fields to the exec call. "
        "If exec reports an allowlist/security denial, retry once with only command, workdir, timeout, and yieldMs. "
        "After the command finishes, reply NO_REPLY."
    )
    scan_args = [
        "--name",
        SCAN_JOB_NAME,
        "--cron",
        scan_expr,
        "--tz",
        tz,
        "--exact",
        "--session",
        "isolated",
        "--message",
        scan_message,
        "--tools",
        "exec",
        "--thinking",
        "minimal",
        "--no-deliver",
        "--timeout-seconds",
        "1800",
    ]
    if SCAN_JOB_NAME in jobs:
        updated.append(edit_job(binary, jobs[SCAN_JOB_NAME]["id"], scan_args[2:]))
    else:
        created.append(add_job(binary, scan_args))

    digest_message = (
        "Use the exec tool to run this command exactly once:\n"
        "python3 /Users/wusir/.openclaw/workspace/skills/community-signal/scripts/run_github_star_radar.py "
        "--record-candidates --limit 10 && "
        "python3 /Users/wusir/.openclaw/workspace/skills/community-signal/scripts/build_digest.py --date today --send\n"
        "Do not add ask/security/allowlist fields to the exec call. "
        "If exec reports an allowlist/security denial, retry once with only command, workdir, timeout, and yieldMs. "
        "After the command finishes, reply NO_REPLY."
    )
    digest_args = [
        "--name",
        DIGEST_JOB_NAME,
        "--cron",
        digest_expr,
        "--tz",
        tz,
        "--session",
        "isolated",
        "--message",
        digest_message,
        "--tools",
        "exec",
        "--thinking",
        "minimal",
        "--no-deliver",
        "--timeout-seconds",
        "1800",
    ]
    if DIGEST_JOB_NAME in jobs:
        updated.append(edit_job(binary, jobs[DIGEST_JOB_NAME]["id"], digest_args[2:]))
    else:
        created.append(add_job(binary, digest_args))

    print(json.dumps({"ok": True, "created": created, "updated": updated}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
