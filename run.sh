#!/bin/sh
# One-command reproduction from a clean clone: venv, install, both charts.
set -eu
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -r requirements.txt
.venv/bin/python fig1_us_treasury_yields.py
.venv/bin/python fig2_ai_issuance_shares.py
