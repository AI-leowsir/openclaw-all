# Current sync scope

Target repo:
- `AI-leowsir/openclaw`
- branch: `main`
- target path: `app/memory/`

Current approved sync set:
- `MEMORY.md`
- `SELF_REVIEW.md`
- `AGENTS.md`
- `SOUL.md`
- `USER.md`
- `IDENTITY.md`
- `TOOLS.md`
- `HEARTBEAT.md`
- `memory/`
- `skills/self-improving-agent`
- `skills/deep-review`
- `skills/push-git-skill`

Notes:
- This sync scope is allowlist-based; do not add more files/folders unless the user explicitly approves.
- The script rebuilds the staging tree under `.tmp/openclaw-memory-sync/` on each run.
- The script pushes only when there is a staged diff.
- The script currently uses SSH key `/root/.ssh/openclaw_github`.
