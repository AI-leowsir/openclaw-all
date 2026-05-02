#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# tab-guard.sh — Task-scoped browser tab lifecycle manager
#
# Usage:
#   tab-guard.sh snapshot <task-id>   Record current tab IDs as baseline
#   tab-guard.sh cleanup  <task-id>   Close tabs opened after baseline
#   tab-guard.sh sweep                Close all agent-opened tabs (no baseline needed)
#   tab-guard.sh status               Show current tab guard state
# ─────────────────────────────────────────────────────────────
set -euo pipefail

STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw/state/tab-guard}"
OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"

# ── Whitelist patterns ──────────────────────────────────────
# Tabs matching ANY of these patterns are NEVER closed.
# - chrome:// and chrome-untrusted:// are browser internals
# - web-pixel-sandbox and Service Worker are browser-managed workers
# - ogs.google.com is the new-tab-page widget
WHITELIST_PATTERNS=(
  "^chrome://"
  "^chrome-untrusted://"
  "^devtools://"
  "^about:"
  "ogs\.google\.com"
  "web-pixel-sandbox"
  "web-pixel-.*sandbox/worker"
  "web-pixels@.*sandbox"
  "Service Worker"
  "/sw\.js$"
  "youtube\.com/embed/"
  "youtube\.com/s/player/"
)

# ── Helpers ─────────────────────────────────────────────────

log() { echo "[tab-guard] $*" >&2; }
die() { log "ERROR: $*"; exit 1; }

# Get all tab IDs, titles, and URLs from openclaw browser tabs.
# Output: one line per tab, format: <id> <title>|||<url>
get_tabs() {
  "$OPENCLAW_BIN" browser tabs 2>/dev/null | \
    awk '
      /^[0-9]+\./ { title = $0; sub(/^[0-9]+\. /, "", title); next }
      /^   https?:\/\// || /^   chrome/ || /^   chrome-untrusted/ || /^   about:/ || /^   devtools:/ {
        url = $0; gsub(/^[[:space:]]+/, "", url); next
      }
      /^   id: / {
        id = $0; gsub(/^[[:space:]]*id: /, "", id);
        if (url != "") print id " " title "|||" url;
        title = ""; url = ""; id = "";
      }
    '
}

# Check if a tab (title + URL) matches any whitelist pattern.
is_whitelisted() {
  local combined="$1"
  for pattern in "${WHITELIST_PATTERNS[@]}"; do
    if echo "$combined" | grep -qE "$pattern"; then
      return 0
    fi
  done
  return 1
}

# ── Commands ────────────────────────────────────────────────

cmd_snapshot() {
  local task_id="${1:?Usage: tab-guard.sh snapshot <task-id>}"
  mkdir -p "$STATE_DIR"

  local baseline_file="$STATE_DIR/${task_id}.baseline"

  # Get current tab IDs
  local tab_ids
  tab_ids=$(get_tabs | awk '{print $1}')


  if [[ -z "$tab_ids" ]]; then
    log "snapshot: no tabs found (browser may not be running)"
    echo "" > "$baseline_file"
  else
    local count
    count=$(echo "$tab_ids" | wc -l | tr -d ' ')
    echo "$tab_ids" > "$baseline_file"
    log "snapshot: recorded $count tab(s) as baseline for task [$task_id]"
  fi

  echo "ok"
}

cmd_cleanup() {
  local task_id="${1:?Usage: tab-guard.sh cleanup <task-id>}"
  local baseline_file="$STATE_DIR/${task_id}.baseline"

  if [[ ! -f "$baseline_file" ]]; then
    log "cleanup: no baseline found for task [$task_id], running sweep instead"
    cmd_sweep
    return
  fi

  # Get current tabs
  local current_tabs
  current_tabs=$(get_tabs)

  if [[ -z "$current_tabs" ]]; then
    log "cleanup: no tabs found, nothing to clean"
    rm -f "$baseline_file"
    echo "ok: 0 tabs closed"
    return
  fi

  # Load baseline IDs
  local baseline_ids
  baseline_ids=$(cat "$baseline_file")

  local closed=0
  local skipped=0
  local errors=0

  while IFS=' ' read -r tab_id tab_info; do
    # Skip if tab was in baseline
    if echo "$baseline_ids" | grep -qF "$tab_id"; then
      continue
    fi

    # Skip whitelisted tabs (check both title and URL)
    if is_whitelisted "$tab_info"; then
      skipped=$((skipped + 1))
      continue
    fi

    # Extract display URL from tab_info
    local display_url="${tab_info#*|||}"

    # Close the tab
    log "cleanup: closing tab $tab_id ($display_url)"
    if "$OPENCLAW_BIN" browser close "$tab_id" 2>/dev/null; then
      closed=$((closed + 1))
    else
      log "cleanup: failed to close tab $tab_id"
      errors=$((errors + 1))
    fi

    # Small delay to avoid overwhelming the browser
    sleep 0.2
  done <<< "$current_tabs"

  # Clean up baseline file
  rm -f "$baseline_file"

  log "cleanup: done — closed=$closed skipped=$skipped errors=$errors"
  echo "ok: $closed tabs closed, $skipped whitelisted, $errors errors"
}

cmd_sweep() {
  log "sweep: scanning all tabs for agent-opened pages..."

  local current_tabs
  current_tabs=$(get_tabs)

  if [[ -z "$current_tabs" ]]; then
    log "sweep: no tabs found"
    echo "ok: 0 tabs closed"
    return
  fi

  local closed=0
  local skipped=0
  local errors=0

  while IFS=' ' read -r tab_id tab_info; do
    # Skip whitelisted tabs (check both title and URL)
    if is_whitelisted "$tab_info"; then
      skipped=$((skipped + 1))
      continue
    fi

    # Extract URL from tab_info
    local display_url="${tab_info#*|||}"

    # Only close http/https tabs (real pages)
    if echo "$display_url" | grep -qE "^https?://"; then
      log "sweep: closing tab $tab_id ($display_url)"
      if "$OPENCLAW_BIN" browser close "$tab_id" 2>/dev/null; then
        closed=$((closed + 1))
      else
        log "sweep: failed to close tab $tab_id"
        errors=$((errors + 1))
      fi
      sleep 0.2
    else
      skipped=$((skipped + 1))
    fi
  done <<< "$current_tabs"

  # Clean up any stale baseline files
  if [[ -d "$STATE_DIR" ]]; then
    find "$STATE_DIR" -name "*.baseline" -mmin +120 -delete 2>/dev/null || true
  fi

  log "sweep: done — closed=$closed skipped=$skipped errors=$errors"
  echo "ok: $closed tabs closed, $skipped skipped, $errors errors"
}

cmd_status() {
  echo "=== Tab Guard Status ==="

  # Show active baselines
  echo ""
  echo "Active baselines:"
  if [[ -d "$STATE_DIR" ]] && ls "$STATE_DIR"/*.baseline 1>/dev/null 2>&1; then
    for f in "$STATE_DIR"/*.baseline; do
      local task_id
      task_id=$(basename "$f" .baseline)
      local count
      count=$(wc -l < "$f" | tr -d ' ')
      local age
      age=$(( ( $(date +%s) - $(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null) ) / 60 ))
      echo "  - task=$task_id baseline_tabs=$count age=${age}min"
    done
  else
    echo "  (none)"
  fi

  # Show current tab count
  echo ""
  echo "Current browser tabs:"
  local current_tabs
  current_tabs=$(get_tabs)
  if [[ -z "$current_tabs" ]]; then
    echo "  (none / browser not running)"
  else
    local total http_count whitelisted_count
    total=$(echo "$current_tabs" | wc -l | tr -d ' ')
    http_count=$(echo "$current_tabs" | awk '{print $2}' | grep -cE "^https?://" || true)
    whitelisted_count=$((total - http_count))
    echo "  total=$total  http_pages=$http_count  internal/workers=$whitelisted_count"
  fi
}

# ── Main ────────────────────────────────────────────────────

case "${1:-}" in
  snapshot) cmd_snapshot "${2:-}" ;;
  cleanup)  cmd_cleanup "${2:-}" ;;
  sweep)    cmd_sweep ;;
  status)   cmd_status ;;
  *)
    echo "Usage: tab-guard.sh {snapshot|cleanup|sweep|status} [task-id]"
    echo ""
    echo "Commands:"
    echo "  snapshot <task-id>   Record current tab IDs as baseline before browser work"
    echo "  cleanup  <task-id>   Close tabs opened after baseline (task completion)"
    echo "  sweep                Close ALL agent-opened http/https tabs (emergency cleanup)"
    echo "  status               Show current tab guard state"
    exit 1
    ;;
esac
