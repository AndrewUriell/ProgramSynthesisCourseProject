#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <conn_log_path> <output_csv_path>"
    echo "Example: $0 data/raw/zeek_run_20260416_221500/conn.log data/processed/policy_examples.csv"
    exit 1
fi

CONN_LOG="$1"
OUTPUT_CSV="$2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PYTHON_SCRIPT="$PROJECT_ROOT/scripts/build_policy_csv.py"

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

if [[ ! -f "$CONN_LOG" ]]; then
    echo "Error: conn.log not found at $CONN_LOG"
    exit 1
fi

mkdir -p "$(dirname "$OUTPUT_CSV")"

python3 "$PYTHON_SCRIPT" \
  --conn-log "$CONN_LOG" \
  --output "$OUTPUT_CSV" \
  --host-map 192.168.56.103=attacker 192.168.56.104=web_server \
  --allow-ports 80 \
  --deny-ports 22

echo "Finished building policy CSV: $OUTPUT_CSV"
