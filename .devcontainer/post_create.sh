#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p data exports

if [ ! -f config.json ]; then
  cp config.example.json config.json
fi

python -m unittest discover -s tests -v

cat <<'MSG'

[cloud setup complete]
Try these commands:
  make run-once
  make backtest
  make test
  make export

This project does not use OpenAI API keys and does not place real orders.
MSG
