#!/usr/bin/env python3

import argparse
import csv
import json
from pathlib import Path


def parse_mapping(items):
    """
    Convert a list like:
    ["192.168.56.103=attacker", "192.168.56.104=web_server"]
    into a dictionary.
    """
    mapping = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid mapping '{item}'. Expected format: key=value")
        key, value = item.split("=", 1)
        mapping[key.strip()] = value.strip()
    return mapping


def parse_port_list(port_string):
    """
    Convert a comma-separated string like '80,443,22'
    into a set of integers.
    """
    if not port_string:
        return set()
    return {int(p.strip()) for p in port_string.split(",") if p.strip()}


def load_conn_log(conn_log_path):
    """
    Read Zeek conn.log in JSON-lines format.
    Skip blank lines and any non-JSON lines safely.
    """
    records = []
    with open(conn_log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # Ignore anything that is not a JSON record
                continue
    return records


def decide_port(port, allow_ports, deny_ports):
    """
    Assign a decision label based on destination port.
    Returns:
        'allow', 'deny', or None if the port is not in scope.
    """
    if port in allow_ports:
        return "allow"
    else:
        return "deny"
    return None


def build_rows(records, host_map, allow_ports, deny_ports):
    """
    Convert Zeek records into reduced policy rows.
    Keeps only:
    - id.orig_h
    - id.resp_h
    - proto
    - id.resp_p
    - derived decision
    """
    rows = []
    seen = set()

    for record in records:
        proto = record.get("proto")
        src_ip = record.get("id.orig_h")
        dst_ip = record.get("id.resp_h")
        dst_port = record.get("id.resp_p")

        if proto != "tcp":
            continue
        if src_ip is None or dst_ip is None or dst_port is None:
            continue

        try:
            dst_port = int(dst_port)
        except (TypeError, ValueError):
            continue

        decision = decide_port(dst_port, allow_ports, deny_ports)
        if decision is None:
            continue

        src_host = host_map.get(src_ip, src_ip)
        dst_host = host_map.get(dst_ip, dst_ip)

        row = (src_host, dst_host, proto, dst_port, decision)

        # Deduplicate repeated connections with the same reduced meaning
        if row not in seen:
            seen.add(row)
            rows.append(row)

    return rows


def write_csv(rows, output_path):
    """
    Write the reduced dataset to CSV.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["src_host", "dst_host", "protocol", "port", "decision"])
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Convert Zeek conn.log JSON output into a reduced policy CSV."
    )
    parser.add_argument(
        "--conn-log",
        required=True,
        help="Path to Zeek conn.log file",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV file",
    )
    parser.add_argument(
        "--host-map",
        nargs="*",
        default=[],
        help="Host mappings like 192.168.56.103=attacker 192.168.56.104=web_server",
    )
    parser.add_argument(
        "--allow-ports",
        default="80",
        help="Comma-separated allow ports, e.g. 80,443",
    )
    parser.add_argument(
        "--deny-ports",
        default="22",
        help="Comma-separated deny ports, e.g. 22,3306",
    )

    args = parser.parse_args()

    conn_log_path = Path(args.conn_log)
    output_path = Path(args.output)

    if not conn_log_path.exists():
        raise FileNotFoundError(f"conn.log not found: {conn_log_path}")

    host_map = parse_mapping(args.host_map)
    allow_ports = parse_port_list(args.allow_ports)
    deny_ports = parse_port_list(args.deny_ports)

    records = load_conn_log(conn_log_path)
    rows = build_rows(records, host_map, allow_ports, deny_ports)
    write_csv(rows, output_path)

    print(f"Processed {len(records)} Zeek records")
    print(f"Wrote {len(rows)} policy rows to {output_path}")


if __name__ == "__main__":
    main()
