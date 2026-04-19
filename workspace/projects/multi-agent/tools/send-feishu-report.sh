#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
TARGET="oc_18670e031c0c78335ff946d6d1fff3ee"
if [ "$#" -gt 0 ]; then
  MESSAGE="$*"
else
  MESSAGE=$(cat)
fi
if [ -z "$MESSAGE" ]; then
  echo "message is required" >&2
  exit 1
fi
"$SCRIPT_DIR/run-openclaw.sh" message send --channel feishu --target "$TARGET" --message "$MESSAGE"
