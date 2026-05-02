# OpenClaw Migration Export

This export contains selected OpenClaw content from the local workstation:

- `/Users/wusir/.openclaw/workspace`
- `/Users/wusir/.openclaw/agents/*/agent`

Export date: `2026-05-02`

## Included

- `workspace/skills/`
- `workspace/config/`
- `workspace/docs/`
- `workspace/specs/`
- `workspace/scripts/`
- `workspace/tools/`
- selected top-level workspace rule/profile files
- `agents/*/agent`
- `openclaw.example.json` with secrets redacted
- `agents/community_signal_agent/agent`
- `agents/consultant_agent/agent`
- `agents/learning_agent/agent`
- `agents/main/agent`
- `agents/seo_organizing_agent/agent`
- `agents/writing_agent/agent`

## Excluded from workspace export

These paths were intentionally excluded because they are runtime state, credentials, local caches, or personal/operational history:

- `.env`, `credentials/`, `service-env/`
- `logs/`, `sessions/`, `browser/`, `plugin-runtime-deps/`
- `workspace/memory/`
- `workspace/extensions/`
- `workspace/**/config/*.env`
- SQLite databases and WAL/SHM files

## Git Notes

- `.gitignore` excludes runtime, credential, cache, and local database files that may reappear locally.
- The raw `~/.openclaw/openclaw.json` is not committed; use `openclaw.example.json` for a redacted config reference.
