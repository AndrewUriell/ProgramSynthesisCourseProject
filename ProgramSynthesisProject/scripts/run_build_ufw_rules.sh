#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <input_policy_json> <output_script>"
    echo "Example: $0 sketch/output/run_001/synthesized_policy.json firewall/generated/apply_ufw.sh"
    exit 1
fi

INPUT_JSON="$1"
OUTPUT_SCRIPT="$2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_SCRIPT="$PROJECT_ROOT/scripts/build_ufw_rules.py"

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

if [[ ! -f "$INPUT_JSON" ]]; then
    echo "Error: input JSON not found at $INPUT_JSON"
    exit 1
fi

mkdir -p "$(dirname "$OUTPUT_SCRIPT")"

python3 "$PYTHON_SCRIPT" \
  --input "$INPUT_JSON" \
  --output "$OUTPUT_SCRIPT"

echo "Finished building ufw script: $OUTPUT_SCRIPT"
