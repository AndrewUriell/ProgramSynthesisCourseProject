#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path


def parse_allowed_ports(sketch_text: str):
    """
    Extract allowed ports from patterns like:
    if(port == 80)
    """
    pattern = re.compile(r'if\s*\(\s*port\s*==\s*(\d+)\s*\)')
    ports = sorted({int(match) for match in pattern.findall(sketch_text)})
    return ports


def build_policy_object(allowed_ports):
    """
    Build a simple structured policy object.
    For the current pipeline, default behavior is deny.
    """
    return {
        "allowed_ports": allowed_ports,
        "default": "deny"
    }


def main():
    parser = argparse.ArgumentParser(
        description="Parse Sketch output into a structured synthesized policy JSON file."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to sketch_output.txt",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to synthesized_policy.json",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Sketch output not found: {input_path}")

    sketch_text = input_path.read_text(encoding="utf-8")
    allowed_ports = parse_allowed_ports(sketch_text)
    policy = build_policy_object(allowed_ports)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(policy, indent=2), encoding="utf-8")

    print(f"Parsed allowed ports: {allowed_ports}")
    print(f"Wrote synthesized policy to {output_path}")


if __name__ == "__main__":
    main()
