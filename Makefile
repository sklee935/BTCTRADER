.PHONY: setup test run-once run backtest export summary clean

setup:
	mkdir -p data exports
	@if [ ! -f config.json ]; then cp config.example.json config.json; fi
	touch exports/.keep

test: setup
	python -m unittest discover -s tests -v

run-once: setup
	python run_bot.py --config config.json --once

run: setup
	python run_bot.py --config config.json

backtest: setup
	python run_backtest.py --config config.json --pages 5

export: setup
	python scripts/export_logs.py --db data/paper_trading.sqlite3 --out exports

summary: setup
	python scripts/db_summary.py --db data/paper_trading.sqlite3

clean:
	rm -rf __pycache__ src/free_btc_bot/__pycache__ tests/__pycache__ exports/*.csv
