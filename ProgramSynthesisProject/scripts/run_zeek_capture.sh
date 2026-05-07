#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <interface> <output_base_dir>"
    echo "Example: $0 enp0s3 ~/project/data/raw"
    exit 1
fi

INTERFACE="$1"
OUTPUT_BASE_DIR="$2"

ZEEK_BIN="/opt/zeek/bin/zeek"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${OUTPUT_BASE_DIR}/zeek_run_${TIMESTAMP}"

mkdir -p "$RUN_DIR"

if [[ ! -x "$ZEEK_BIN" ]]; then
    echo "Error: Zeek binary not found at $ZEEK_BIN"
    exit 1
fi

cat > "${RUN_DIR}/capture_metadata.txt" <<EOF
timestamp=${TIMESTAMP}
interface=${INTERFACE}
host=$(hostname)
user=$(whoami)
EOF

echo "Starting Zeek capture"
echo "Interface: $INTERFACE"
echo "Run directory: $RUN_DIR"
echo "Press Ctrl+C to stop capture"

cd "$RUN_DIR"

# Run Zeek in foreground. Ctrl+C stops it.
sudo "$ZEEK_BIN" -i "$INTERFACE" -C LogAscii::use_json=T || true

# Give Zeek a moment to flush logs
sleep 1

# Fix ownership if run with sudo
if [[ -n "${SUDO_USER:-}" ]]; then
    chown -R "$SUDO_USER":"$SUDO_USER" "$RUN_DIR" 2>/dev/null || true
fi

if [[ -f "${RUN_DIR}/conn.log" ]]; then
    echo "conn.log saved to: ${RUN_DIR}/conn.log"
else
    echo "Warning: conn.log was not found in ${RUN_DIR}"
fi
