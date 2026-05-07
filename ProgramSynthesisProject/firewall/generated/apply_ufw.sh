#!/usr/bin/env bash
set -euo pipefail

echo "Applying synthesized ufw policy..."
sudo ufw reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 80/tcp
sudo ufw enable
sudo ufw status verbose
