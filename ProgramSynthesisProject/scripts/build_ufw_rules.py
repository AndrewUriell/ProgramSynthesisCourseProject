#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def load_policy(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))

    if "allowed_ports" not in data or "default" not in data:
        raise ValueError("Policy JSON must contain 'allowed_ports' and 'default'")

    allowed_ports = data["allowed_ports"]
    default_policy = str(data["default"]).strip().lower()

    if not isinstance(allowed_ports, list):
        raise ValueError("'allowed_ports' must be a list")

    normalized_ports = []
    for port in allowed_ports:
        try:
            normalized_ports.append(int(port))
        except (TypeError, ValueError):
            raise ValueError(f"Invalid allowed port: {port}")

    if default_policy not in {"deny", "allow"}:
        raise ValueError("Default policy must be 'deny' or 'allow'")

    return sorted(set(normalized_ports)), default_policy


def build_ufw_script(allowed_ports, default_policy):
    lines = []
    lines.append("#!/usr/bin/env bash")
    lines.append("set -euo pipefail")
    lines.append("")
    lines.append('echo "Applying synthesized ufw policy..."')
    lines.append("sudo ufw reset")

    if default_policy == "deny":
        lines.append("sudo ufw default deny incoming")
    else:
        lines.append("sudo ufw default allow incoming")

    lines.append("sudo ufw default allow outgoing")

    for port in allowed_ports:
        lines.append(f"sudo ufw allow {port}/tcp")

    lines.append("sudo ufw enable")
    lines.append("sudo ufw status verbose")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a ufw shell script from synthesized_policy.json"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to synthesized_policy.json",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output shell script",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input policy JSON not found: {input_path}")

    allowed_ports, default_policy = load_policy(input_path)
    script_text = build_ufw_script(allowed_ports, default_policy)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(script_text, encoding="utf-8")
    output_path.chmod(0o755)

    print(f"Allowed ports: {allowed_ports}")
    print(f"Default incoming policy: {default_policy}")
    print(f"Wrote ufw script to {output_path}")


if __name__ == "__main__":
    main()
