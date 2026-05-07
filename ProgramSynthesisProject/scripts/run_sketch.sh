#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <input_sketch_file> <output_dir>"
    echo "Example: $0 sketch/manual/policy.sk sketch/output/run_001"
    exit 1
fi

INPUT_SKETCH="$1"
OUTPUT_DIR="$2"

SKETCH_BIN="$HOME/sketch-1.7.6/sketch-frontend/sketch"
OUTPUT_FILE="$OUTPUT_DIR/sketch_output.txt"
INPUT_COPY="$OUTPUT_DIR/$(basename "$INPUT_SKETCH")"

if [[ ! -f "$INPUT_SKETCH" ]]; then
    echo "Error: input sketch file not found at $INPUT_SKETCH"
    exit 1
fi

if [[ ! -x "$SKETCH_BIN" ]]; then
    echo "Error: Sketch binary not found or not executable at $SKETCH_BIN"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

cp "$INPUT_SKETCH" "$INPUT_COPY"

echo "Running Sketch..."
echo "Input:  $INPUT_SKETCH"
echo "Output: $OUTPUT_FILE"

"$SKETCH_BIN" "$INPUT_SKETCH" | tee "$OUTPUT_FILE"

echo "Sketch run complete."
echo "Saved output to: $OUTPUT_FILE"
