#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../linux-client"
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
linmic
