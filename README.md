# EECS 700 Firewall Synthesis Pipeline

## Overview

This project is a small proof-of-concept pipeline for synthesizing simple firewall behavior from observed network traffic.

Current pipeline:

1. Generate traffic from the Kali attacker VM to the Ubuntu target VM
2. Capture traffic with Zeek on Ubuntu
3. Convert Zeek `conn.log` into a reduced CSV dataset
4. Manually write a Sketch program (`policy.sk`)
5. Run Sketch to synthesize a simple policy
6. Parse the Sketch output into a JSON policy object
7. Generate a `ufw` firewall script from the synthesized policy
8. Apply the firewall rules
9. Test whether the behavior matches the synthesized policy

Current tested example:
- allow inbound HTTP on port 80
- deny inbound SSH on port 22
- deny all other inbound traffic by default

---

## Current VM Roles

### Kali VM
Used as the attacker / traffic generator

### Ubuntu VM
Used as the target web server and policy enforcement machine

Ubuntu is also where:
- Zeek runs
- Sketch runs
- `ufw` rules are generated and applied

---

## Important Notes Before Running

- Keep a **local terminal open on the Ubuntu VM** before applying firewall rules
- Review generated firewall rules before applying them
- The current pipeline assumes:
  - attacker VM IP maps to `attacker`
  - Ubuntu VM IP maps to `web_server`
- The Sketch file is still written **manually**
- The rest of the pipeline around Sketch is partially automated

---

## Project Structure

Expected structure:

```text
project-root/
├── data/
│   ├── raw/
│   └── processed/
├── firewall/
│   └── generated/
├── scripts/
│   ├── run_zeek_capture.sh
│   ├── build_policy_csv.py
│   ├── run_build_policy_csv.sh
│   ├── run_sketch.sh
│   ├── parse_sketch_output.py
│   ├── run_parse_sketch_output.sh
│   ├── build_ufw_rules.py
│   └── run_build_ufw_rules.sh
├── sketch/
│   ├── manual/
│   └── output/
└── README.md
```

## Full Run Example from ~/ProgramSynthesisProject
### All bash scripts have example usages when running them
# 1. Start Zeek capture
```
./scripts/run_zeek_capture.sh enp0s3 data/raw
```
# 2. From Kali:
# curl http://<UBUNTU_IP>
# ssh <UBUNTU_USERNAME>@<UBUNTU_IP>

# 3. Stop Zeek with Ctrl+C

# 4. Build reduced CSV
```
./scripts/run_build_policy_csv.sh \
  data/raw/zeek_run_YYYYMMDD_HHMMSS/conn.log \
  data/processed/policy_examples.csv
```

```
python3 scripts/create_assertions.py
```
# 5. Manually update sketch/manual/policy.sk

# 6. Run Sketch
```
./scripts/run_sketch.sh \
  sketch/manual/policy.sk \
  sketch/output/run_001
```
# 7. Parse Sketch output
```
./scripts/run_parse_sketch_output.sh \
  sketch/output/run_001/sketch_output.txt \
  sketch/output/run_001/synthesized_policy.json
```
# 8. Build ufw rules
```
./scripts/run_build_ufw_rules.sh \
  sketch/output/run_001/synthesized_policy.json \
  firewall/generated/apply_ufw.sh
```
# 9. Review/apply rules
```
./firewall/generated/apply_ufw.sh
```
# 10. From Kali, test:
# curl http://<UBUNTU_IP>
# ssh <UBUNTU_USERNAME>@<UBUNTU_IP>
