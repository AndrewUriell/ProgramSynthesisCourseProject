# Program Synthesis Course Project

This project is a proof-of-concept pipeline for synthesizing a simple network
firewall policy from observed traffic.

The pipeline captures network traffic with Zeek, reduces the Zeek connection
logs into policy examples, uses Sketch to synthesize a port-based allow/deny
policy, and generates a `ufw` script that can apply the synthesized firewall
rules. The current output model is a default-deny TCP firewall policy with
synthesized allowed ports.

## Project Structure

```text
ProgramSynthesisProject/
  data/
    raw/
      zeek_run_test/
        conn.log                    Sample Zeek connection log used by the CSV step
      zeek_run_*/
        conn.log                    Captured Zeek connection log used by the CSV step
        capture_metadata.txt        Metadata written by the capture script
    processed/
      policy_examples.csv           Reduced policy examples used by Sketch

  scripts/
    run_zeek_capture.sh             Captures live traffic with Zeek
    run_build_policy_csv.sh         Wrapper for building the policy CSV
    build_policy_csv.py             Converts Zeek conn.log records to CSV rows
    create_assertions.py            Converts CSV rows to Sketch assertions
    run_sketch.sh                   Runs a Sketch policy file
    run_parse_sketch_output.sh      Wrapper for parsing Sketch output
    parse_sketch_output.py          Converts Sketch output to policy JSON
    run_build_ufw_rules.sh          Wrapper for generating a ufw script
    build_ufw_rules.py              Converts policy JSON to a ufw shell script

  sketch/
    manual/
      policy.sk                     Synthesizes one allowed port
      range_policy.sk               Synthesizes one allowed port and a range
    output/
      run_*/
        sketch_output.txt           Raw Sketch output parsed into policy JSON
        synthesized_policy.json     Parsed policy consumed by the ufw step

  firewall/
    generated/
      apply_ufw.sh                  Generated ufw policy application script

  traffic_commands.txt              Example commands for generating traffic
  sketch_assertions.txt             Generated assertions from policy_examples.csv
```

The tree above only lists files and directories used by the documented pipeline.
Zeek may produce additional logs such as `http.log`, `dns.log`, or `ssh.log`,
but this pipeline only consumes `conn.log`.

## Requirements

- Python 3
- Bash shell
- Zeek installed at `/opt/zeek/bin/zeek`
- Sketch installed at `$HOME/sketch-1.7.6/sketch-frontend/sketch`
- `ufw`, only if applying the generated firewall script
- `sudo` privileges for Zeek capture and for applying `ufw` rules

Run the pipeline commands from the `ProgramSynthesisProject` directory:

```bash
cd ProgramSynthesisProject
```

## Pipeline Walkthrough

### 1. Capture Traffic With Zeek

File: `scripts/run_zeek_capture.sh`

What it does: runs Zeek on a live network interface, writes JSON logs to a new
timestamped directory under the selected output directory, and records capture
metadata.

Command format:

```bash
./scripts/run_zeek_capture.sh <interface> <output_base_dir>
```

Example:

```bash
./scripts/run_zeek_capture.sh enp0s3 data/raw
```

This creates a directory like `data/raw/zeek_run_20260430_110535/`. Press
`Ctrl+C` to stop the live capture. The most important output for the next stage
is `conn.log`.

Traffic examples for producing test connections are in `traffic_commands.txt`.

### 2. Build Policy Examples

File: `scripts/run_build_policy_csv.sh`

What it does: wraps `scripts/build_policy_csv.py`, reads a Zeek `conn.log`, keeps
TCP connection records, maps configured hosts to names, deduplicates equivalent
connections, and writes a reduced CSV of policy examples.

Command format:

```bash
./scripts/run_build_policy_csv.sh <conn_log_path> <output_csv_path>
```

Example:

```bash
./scripts/run_build_policy_csv.sh \
  data/raw/zeek_run_test/conn.log \
  data/processed/policy_examples.csv
```

The generated CSV schema is:

```text
src_host,dst_host,protocol,port,decision
```

The wrapper currently maps `192.168.56.103` to `attacker`, maps
`192.168.56.104` to `web_server`, allows TCP port `80`, and denies other TCP
ports.

### 3. Generate Sketch Assertions

File: `scripts/create_assertions.py`

What it does: reads `data/processed/policy_examples.csv` and writes assertions
of the form `assert policy(<port>) == <decision>;` to `sketch_assertions.txt`.

Command format:

```bash
python3 scripts/create_assertions.py
```

Example:

```bash
python3 scripts/create_assertions.py
```

This script uses relative paths, so run it from `ProgramSynthesisProject`.

### 4. Run Sketch

File: `scripts/run_sketch.sh`

What it does: runs a Sketch policy file, saves the raw Sketch output to
`sketch_output.txt`, and copies the input `.sk` file into the output directory.

Command format:

```bash
./scripts/run_sketch.sh <input_sketch_file> <output_dir>
```

Example using the single-port template:

```bash
./scripts/run_sketch.sh sketch/manual/policy.sk sketch/output/run_001
```

Example using the range template:

```bash
./scripts/run_sketch.sh sketch/manual/range_policy.sk sketch/output/run_003
```

The main output for the next stage is
`sketch/output/<run>/sketch_output.txt`.

### 5. Parse the Synthesized Policy

File: `scripts/run_parse_sketch_output.sh`

What it does: wraps `scripts/parse_sketch_output.py`, extracts allowed ports
from simple Sketch output patterns such as `if (port == 80)`, and writes a
structured synthesized policy JSON file.

Command format:

```bash
./scripts/run_parse_sketch_output.sh <input_sketch_output> <output_json>
```

Example:

```bash
./scripts/run_parse_sketch_output.sh \
  sketch/output/run_001/sketch_output.txt \
  sketch/output/run_001/synthesized_policy.json
```

Example JSON output:

```json
{
  "allowed_ports": [80],
  "default": "deny"
}
```

### 6. Generate `ufw` Rules

File: `scripts/run_build_ufw_rules.sh`

What it does: wraps `scripts/build_ufw_rules.py`, reads synthesized policy JSON,
and writes an executable shell script containing the corresponding `ufw`
commands.

Command format:

```bash
./scripts/run_build_ufw_rules.sh <input_policy_json> <output_script>
```

Example:

```bash
./scripts/run_build_ufw_rules.sh \
  sketch/output/run_001/synthesized_policy.json \
  firewall/generated/apply_ufw.sh
```

The generated script resets `ufw`, sets the default incoming policy, allows
outgoing traffic, adds one TCP allow rule for each synthesized allowed port, and
prints the final verbose firewall status.

### 7. Apply the Generated Firewall Policy

File: `firewall/generated/apply_ufw.sh`

What it does: applies the generated firewall rules to the local machine.

Command format:

```bash
sudo ./firewall/generated/apply_ufw.sh
```

Example:

```bash
sudo ./firewall/generated/apply_ufw.sh
```

Review this script before running it. It resets existing `ufw` rules, so only
run it on a machine where changing firewall rules is intended.

## Important Files

- `traffic_commands.txt`: example commands for creating traffic that Zeek can
  observe.
- `data/processed/policy_examples.csv`: reduced policy dataset consumed by the
  synthesis step.
- `scripts/build_policy_csv.py`: implements the Zeek-to-policy-example
  conversion logic.
- `scripts/create_assertions.py`: generates Sketch assertions from the policy
  examples CSV.
- `scripts/parse_sketch_output.py`: converts raw Sketch output into
  `synthesized_policy.json`.
- `scripts/build_ufw_rules.py`: converts synthesized policy JSON into an
  executable `ufw` script.
- `sketch/manual/policy.sk`: Sketch template for synthesizing one allowed port.
- `sketch/manual/range_policy.sk`: Sketch template for synthesizing one allowed
  port plus an allowed range.
- `firewall/generated/apply_ufw.sh`: generated deployment artifact for applying
  the synthesized firewall policy.

## Notes

- Sample raw captures and Sketch outputs are included for repeatable
  experiments.
- Repeated Zeek captures are stored in timestamped directories named
  `data/raw/zeek_run_<timestamp>/`.
- Repeated Sketch runs are stored in output directories such as
  `sketch/output/run_001/`.
- `build_policy_csv.py` currently focuses on TCP traffic and labels configured
  allow ports as `allow`; other TCP ports are labeled `deny`.
- `parse_sketch_output.py` currently extracts `if (port == N)` patterns
  and emits a default-deny policy JSON object.
- Generated `ufw` scripts should be reviewed before execution because they can
  change or reset local firewall behavior.
