---
name: push-git-skill
description: Push approved OpenClaw memory, rule files, and selected skills into a target Git repository. Use when the user asks to sync/push memory files, rules, review files, or selected skills to Git/GitHub, or asks to create, inspect, modify, or schedule a Git push workflow for the approved sync scope.
---

# Push Git Skill

Use this skill when the task is to push the approved OpenClaw memory/rule/skill set into the configured Git repository, or when the user asks to inspect or extend that push workflow.

## What this skill covers

- Run the approved Git sync manually
- Inspect which files/folders are in the sync allowlist
- Modify the sync allowlist when the user explicitly approves changes
- Prepare or update a cron job that runs the sync script on a schedule
- Explain whether a given file/skill is included in the sync scope

## Current source of truth

Before answering scope questions, read:
- `references/sync-scope.md`

Before changing the push implementation, read and edit:
- `scripts/push_openclaw_memory_to_repo.sh`

## Rules

- Treat the sync scope as allowlist-based.
- Do not add extra files/folders unless the user explicitly asks.
- If the user asks to schedule the push, prefer reusing `scripts/push_openclaw_memory_to_repo.sh` instead of inventing a second implementation.
- If the user asks what is synced, answer from the actual script/scope file rather than guessing.
- If a push affects an external repo, treat it as an external action and get confirmation before actually running the push unless the user already made that intent explicit.

## Manual run

Run this script:
- `skills/push-git-skill/scripts/push_openclaw_memory_to_repo.sh`

The script currently pushes the approved sync set into:
- repo: `AI-leowsir/openclaw`
- branch: `main`
- subdir: `app/memory/`

## Scheduling

When scheduling a cron job for this push flow:
- make the cron payload invoke the script above via shell
- keep the job description explicit about which repo/path it pushes to
- if the user wants notifications, make that requirement explicit in the cron design instead of assuming it already exists

## Keep scope lean

This skill should stay focused on Git push sync for the approved memory/rule/skill set. Do not turn it into a general Git skill.
