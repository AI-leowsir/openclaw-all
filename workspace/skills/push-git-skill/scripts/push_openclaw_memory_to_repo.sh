#!/usr/bin/env bash
set -euo pipefail

# Push approved OpenClaw memory/rule/skill files into the target Git repo structure.
# Current approved target:
# - Repo: AI-leowsir/openclaw
# - Branch: main
# - Subdir: app/memory/
# Current approved sync set:
# - MEMORY.md
# - SELF_REVIEW.md
# - AGENTS.md
# - SOUL.md
# - USER.md
# - IDENTITY.md
# - TOOLS.md
# - HEARTBEAT.md
# - memory/
# - skills/self-improving-agent
# - skills/deep-review
# - skills/push-git-skill

WORKSPACE="/root/.openclaw/workspace"
TARGET_REPO_URL="git@github.com:AI-leowsir/openclaw.git"
BRANCH="main"
SSH_KEY="/root/.ssh/openclaw_github"
export GIT_SSH_COMMAND="ssh -i ${SSH_KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
STAGING_ROOT="${WORKSPACE}/.tmp/openclaw-memory-sync"
TARGET_ROOT="${STAGING_ROOT}/app/memory"
COMMIT_MSG_DEFAULT="chore(memory): sync OpenClaw memory/rules/skills"
COMMIT_MSG="${COMMIT_MSG:-$COMMIT_MSG_DEFAULT}"

rm -rf "${STAGING_ROOT}"
mkdir -p "${STAGING_ROOT}"

copy_if_exists() {
  local src="$1"
  local dst="$2"
  if [ -e "$src" ]; then
    mkdir -p "$(dirname "$dst")"
    cp -a "$src" "$dst"
  else
    echo "[skip] missing: $src"
  fi
}

cd "${STAGING_ROOT}"

if [ ! -d .git ]; then
  git init
  git branch -M "${BRANCH}"
  git remote add origin "${TARGET_REPO_URL}"
else
  git remote set-url origin "${TARGET_REPO_URL}"
fi

git fetch origin "${BRANCH}" || true
if git rev-parse --verify "origin/${BRANCH}" >/dev/null 2>&1; then
  git checkout -B "${BRANCH}" "origin/${BRANCH}"
else
  git checkout -B "${BRANCH}"
fi

rm -rf "${TARGET_ROOT}/MEMORY.md" \
       "${TARGET_ROOT}/SELF_REVIEW.md" \
       "${TARGET_ROOT}/AGENTS.md" \
       "${TARGET_ROOT}/SOUL.md" \
       "${TARGET_ROOT}/USER.md" \
       "${TARGET_ROOT}/IDENTITY.md" \
       "${TARGET_ROOT}/TOOLS.md" \
       "${TARGET_ROOT}/HEARTBEAT.md" \
       "${TARGET_ROOT}/memory" \
       "${TARGET_ROOT}/skills/self-improving-agent" \
       "${TARGET_ROOT}/skills/deep-review" \
       "${TARGET_ROOT}/skills/push-git-skill"

copy_if_exists "${WORKSPACE}/MEMORY.md" "${TARGET_ROOT}/MEMORY.md"
copy_if_exists "${WORKSPACE}/SELF_REVIEW.md" "${TARGET_ROOT}/SELF_REVIEW.md"
copy_if_exists "${WORKSPACE}/AGENTS.md" "${TARGET_ROOT}/AGENTS.md"
copy_if_exists "${WORKSPACE}/SOUL.md" "${TARGET_ROOT}/SOUL.md"
copy_if_exists "${WORKSPACE}/USER.md" "${TARGET_ROOT}/USER.md"
copy_if_exists "${WORKSPACE}/IDENTITY.md" "${TARGET_ROOT}/IDENTITY.md"
copy_if_exists "${WORKSPACE}/TOOLS.md" "${TARGET_ROOT}/TOOLS.md"
copy_if_exists "${WORKSPACE}/HEARTBEAT.md" "${TARGET_ROOT}/HEARTBEAT.md"
copy_if_exists "${WORKSPACE}/memory" "${TARGET_ROOT}/memory"
copy_if_exists "${WORKSPACE}/skills/self-improving-agent" "${TARGET_ROOT}/skills/self-improving-agent"
copy_if_exists "${WORKSPACE}/skills/deep-review" "${TARGET_ROOT}/skills/deep-review"
copy_if_exists "${WORKSPACE}/skills/push-git-skill" "${TARGET_ROOT}/skills/push-git-skill"

git add app/memory

if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

git commit -m "${COMMIT_MSG}"
git push -u origin "${BRANCH}"

echo "Sync complete: ${TARGET_REPO_URL} -> app/memory"
