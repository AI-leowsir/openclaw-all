# OpenClaw Migration Export

This export contains the selected OpenClaw content migrated from the remote host:

- `/root/.openclaw/workspace`
- `/root/.openclaw/agents/*/agent`

Export date: `2026-04-19`

## Included

- `workspace/`
- `agents/main/agent`
- `agents/learning_agent/agent`
- `agents/seo_organizing_agent/agent`
- `agents/writing_agent/agent`

## Excluded from workspace export

These paths were intentionally excluded because they are runtime/generated state and not useful in Git:

- `workspace/backups/`
- `workspace/.tmp/`
- `workspace/tmp/`
- `workspace/state`

## Git Notes

- `.gitignore` excludes a few lock/state files that may reappear locally.
- This export is prepared for Git, but push is still blocked until the target repository is accessible with valid credentials.
