{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run bot once",
      "type": "shell",
      "command": "python run_bot.py --config config.json --once",
      "group": "test",
      "problemMatcher": []
    },
    {
      "label": "Run backtest",
      "type": "shell",
      "command": "python run_backtest.py --config config.json --pages 5",
      "group": "test",
      "problemMatcher": []
    },
    {
      "label": "Run unit tests",
      "type": "shell",
      "command": "python -m unittest discover -s tests -v",
      "group": "test",
      "problemMatcher": []
    },
    {
      "label": "Export SQLite logs to CSV",
      "type": "shell",
      "command": "python scripts/export_logs.py --db data/paper_trading.sqlite3 --out exports",
      "group": "test",
      "problemMatcher": []
    }
  ]
}
