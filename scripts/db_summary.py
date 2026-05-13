from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def main() -> None:
    parser = argparse.ArgumentParser(description="Print a small SQLite summary")
    parser.add_argument("--db", default="data/paper_trading.sqlite3", help="SQLite database path")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}. Run 'make run-once' first.")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
        ]
        print("tables")
        for table in tables:
            print(f"- {table}: {table_count(conn, table)} rows")

        event = conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT 1").fetchone()
        if event:
            print("\nlatest event")
            event_dict = dict(event)
            if event_dict.get("execution_json"):
                try:
                    event_dict["execution_json"] = json.loads(event_dict["execution_json"])
                except json.JSONDecodeError:
                    pass
            for key, value in event_dict.items():
                print(f"- {key}: {value}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
