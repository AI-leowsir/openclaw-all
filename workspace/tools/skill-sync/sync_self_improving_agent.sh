#!/usr/bin/env bash
set -euo pipefail

LOCK_FILE="/tmp/self-improving-agent-sync.lock"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "Another sync is already running."
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$SCRIPT_DIR/config/self_improving_agent.env}"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Missing config file: $CONFIG_FILE" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$CONFIG_FILE"

required_vars=(
  GITHUB_USERNAME
  GITHUB_PAT
  REPO_HTTPS_URL
  REPO_BRANCH
  SOURCE_DIR
  TARGET_SUBDIR
  WORKDIR
  GIT_AUTHOR_NAME
  GIT_AUTHOR_EMAIL
)

for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "Missing required config: $var" >&2
    exit 1
  fi
done

notify() {
  local text="$1"
  if command -v openclaw >/dev/null 2>&1; then
    openclaw message send --channel feishu --target "$NOTIFY_TARGET" --message "$text" >/dev/null 2>&1 || true
  fi
}

run_status="failed"
summary=""
commit_sha=""

finish() {
  local exit_code=$?
  if [[ -z "${NOTIFY_TARGET:-}" ]]; then
    exit "$exit_code"
  fi

  local title="[self-improving-agent sync]"
  local body
  if [[ "$exit_code" -eq 0 ]]; then
    body="${summary:-同步完成，但没有生成摘要。}"
  else
    body="同步失败。请查看日志：${SYNC_LOG_PATH:-$SCRIPT_DIR/sync.log}"
    if [[ -n "$summary" ]]; then
      body="$body
$summary"
    fi
  fi

  notify "$title $body"
  exit "$exit_code"
}
trap finish EXIT

mkdir -p "$WORKDIR"
REPO_DIR="$WORKDIR/repo"

AUTH_REPO_URL="https://${GITHUB_USERNAME}:${GITHUB_PAT}@${REPO_HTTPS_URL#https://}"

if [[ ! -d "$REPO_DIR/.git" ]]; then
  rm -rf "$REPO_DIR"
  git clone --branch "$REPO_BRANCH" "$AUTH_REPO_URL" "$REPO_DIR"
else
  git -C "$REPO_DIR" remote set-url origin "$AUTH_REPO_URL"
  git -C "$REPO_DIR" fetch origin "$REPO_BRANCH"
  git -C "$REPO_DIR" checkout "$REPO_BRANCH"
  git -C "$REPO_DIR" reset --hard "origin/$REPO_BRANCH"
fi

DEST_DIR="$REPO_DIR/$TARGET_SUBDIR"
mkdir -p "$DEST_DIR"

find "$DEST_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
cp -R "$SOURCE_DIR"/. "$DEST_DIR"/

cd "$REPO_DIR"
git config user.name "$GIT_AUTHOR_NAME"
git config user.email "$GIT_AUTHOR_EMAIL"

if git diff --quiet && git diff --cached --quiet; then
  summary="无变更，本次未同步。"
  exit 0
fi

git add "$TARGET_SUBDIR"
if git diff --cached --quiet; then
  summary="add 后无暂存变更，本次未同步。"
  exit 0
fi

commit_message="Sync self-improving-agent skill ($(date +%F' '%T))"
git commit -m "$commit_message"
git push origin "$REPO_BRANCH"

commit_sha="$(git rev-parse --short HEAD)"
summary="同步完成：已推送到 ${REPO_BRANCH}，commit ${commit_sha}。"
run_status="success"

echo "Sync complete."
