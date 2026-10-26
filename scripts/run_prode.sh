#!/usr/bin/env bash
# ==============================================================================
# PRODE Local Platform Daemon Manager
# Usage: ./scripts/run_prode.sh {start|stop|status}
# ==============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT_DIR/.prode.pid"
LOG_FILE="$ROOT_DIR/.prode.log"
HOST="${PRODE_HOST:-127.0.0.1}"
PORT="${PRODE_PORT:-8080}"

case "${1:-status}" in
  start)
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "PRODE Control Center is already running (PID: $(cat "$PID_FILE")) at http://$HOST:$PORT"
      exit 0
    fi
    cd "$ROOT_DIR"
    nohup python3 -m prode serve --host "$HOST" --port "$PORT" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    sleep 1
    echo "PRODE Control Center started (PID: $(cat "$PID_FILE")) -> http://$HOST:$PORT"
    ;;
  stop)
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      kill "$(cat "$PID_FILE")"
      rm -f "$PID_FILE"
      echo "PRODE Control Center stopped."
    else
      rm -f "$PID_FILE"
      echo "PRODE Control Center is not running."
    fi
    ;;
  status)
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "PRODE Control Center is RUNNING (PID: $(cat "$PID_FILE")) at http://$HOST:$PORT"
    else
      echo "PRODE Control Center is STOPPED."
    fi
    ;;
  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
