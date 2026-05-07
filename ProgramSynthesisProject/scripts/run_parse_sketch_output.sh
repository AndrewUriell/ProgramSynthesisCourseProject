#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <input_sketch_output> <output_json>"
    echo "Example: $0 sketch/output/run_001/sketch_output.txt sketch/output/run_001/synthesized_policy.json"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="$2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_SCRIPT="$PROJECT_ROOT/scripts/parse_sketch_output.py"

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: Sketch output file not found at $INPUT_FILE"
    exit 1
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

python3 "$PYTHON_SCRIPT" \
  --input "$INPUT_FILE" \
  --output "$OUTPUT_FILE"

echo "Finished parsing Sketch output: $OUTPUT_FILE"
