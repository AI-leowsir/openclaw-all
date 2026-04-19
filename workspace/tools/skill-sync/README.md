# self-improving-agent auto sync

Auto-sync local `self-improving-agent` skill to GitHub repo `AI-leowsir/skill-`.

## Files

- `sync_self_improving_agent.sh` — sync script
- `config/self_improving_agent.env.example` — config template

## Setup

1. Copy config template:

```bash
cp tools/skill-sync/config/self_improving_agent.env.example tools/skill-sync/config/self_improving_agent.env
```

2. Fill in a fresh GitHub PAT:

```bash
vim tools/skill-sync/config/self_improving_agent.env
```

3. Make script executable:

```bash
chmod +x tools/skill-sync/sync_self_improving_agent.sh
```

4. Test once manually:

```bash
bash tools/skill-sync/sync_self_improving_agent.sh
```

## Cron (every 3 days)

Example cron entry:

```cron
0 3 */3 * * /bin/bash /root/.openclaw/workspace/tools/skill-sync/sync_self_improving_agent.sh >> /root/.openclaw/workspace/tools/skill-sync/sync.log 2>&1
```

## Notes

- Uses PAT over HTTPS
- Sync target path:
  - `apps/self-improving-agent skill/`
- Keeps repo branch hard-reset to remote before each sync
- Only commits when local synced content changed
- Uses a lock file at `/tmp/self-improving-agent-sync.lock` to avoid overlapping runs
- Commit messages include timestamp for easier audit
- Supports Feishu completion notification via `NOTIFY_TARGET`
- On success/failure, sends a short message with result summary; failure message points to `SYNC_LOG_PATH`
