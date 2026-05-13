from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path


def export_table(conn: sqlite3.Connection, table: str, out_dir: Path) -> int:
    cursor = conn.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    out_path = out_dir / f"{table}.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export bot SQLite logs to CSV files")
    parser.add_argument("--db", default="data/paper_trading.sqlite3", help="SQLite database path")
    parser.add_argument("--out", default="exports", help="Output directory")
    args = parser.parse_args()

    db_path = Path(args.db)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}. Run 'make run-once' first.")

    conn = sqlite3.connect(str(db_path))
    try:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
        ]
        if not tables:
            raise SystemExit("No tables found in database.")

        for table in tables:
            count = export_table(conn, table, out_dir)
            print(f"exported {table}: {count} rows -> {out_dir / (table + '.csv')}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
