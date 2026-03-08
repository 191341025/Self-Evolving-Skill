# -*- coding: utf-8 -*-
"""
Database read-only query tool.

Executes SELECT queries against the configured database and prints
formatted results. Reuses connection config from db_config.ini.

Safety: only SELECT/SHOW/DESCRIBE/EXPLAIN statements are allowed.
"""

import sys
import argparse
import configparser
import re
from pathlib import Path

try:
    import pymysql
except ImportError:
    print("Error: pymysql required. Run: pip install pymysql")
    sys.exit(1)


ALLOWED_PREFIXES = ("SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN")
FORBIDDEN_KEYWORDS = (
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "RENAME", "REPLACE", "GRANT", "REVOKE", "CALL",
)


def validate_sql(sql: str) -> None:
    """Ensure the SQL is read-only."""
    stripped = sql.strip().rstrip(";").strip()
    upper = stripped.upper()

    if not any(upper.startswith(p) for p in ALLOWED_PREFIXES):
        print(f"Error: only SELECT/SHOW/DESCRIBE/EXPLAIN allowed.")
        sys.exit(1)

    # Check for forbidden keywords that might appear in subqueries or injections
    # Simple heuristic: split by whitespace and check tokens
    tokens = re.split(r'[\s(]+', upper)
    for kw in FORBIDDEN_KEYWORDS:
        if kw in tokens:
            print(f"Error: forbidden keyword '{kw}' detected.")
            sys.exit(1)


def load_config():
    config_path = Path(__file__).parent / "db_config.ini"
    if not config_path.exists():
        print(f"Error: config not found: {config_path}")
        sys.exit(1)
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")
    return config


def run_query(config, database, sql, limit):
    db_name = database or config.get("target", "database")
    conn = pymysql.connect(
        host=config.get("database", "host"),
        port=config.getint("database", "port"),
        user=config.get("database", "user"),
        password=config.get("database", "password"),
        database=db_name,
        charset=config.get("database", "charset"),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
        read_timeout=30,
    )

    try:
        with conn.cursor() as cur:
            conn.ping(reconnect=True)
            cur.execute(sql)
            rows = cur.fetchmany(limit)
            total = cur.rowcount

            if not rows:
                print(f"[{db_name}] No results.")
                return

            # Print header
            cols = list(rows[0].keys())
            # Calculate column widths
            widths = {c: len(str(c)) for c in cols}
            for row in rows:
                for c in cols:
                    widths[c] = max(widths[c], len(str(row[c] if row[c] is not None else "NULL")))

            # Cap column width at 60
            for c in cols:
                widths[c] = min(widths[c], 60)

            # Format
            header = " | ".join(str(c).ljust(widths[c])[:widths[c]] for c in cols)
            sep = "-+-".join("-" * widths[c] for c in cols)

            print(f"[{db_name}] {total} row(s) total, showing {len(rows)}:\n")
            print(header)
            print(sep)
            for row in rows:
                vals = []
                for c in cols:
                    v = str(row[c]) if row[c] is not None else "NULL"
                    vals.append(v.ljust(widths[c])[:widths[c]])
                print(" | ".join(vals))

            if total > len(rows):
                print(f"\n... ({total - len(rows)} more rows not shown, use --limit to increase)")

    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Read-only database query tool")
    parser.add_argument("--sql", required=True, help="SELECT query to execute")
    parser.add_argument("--database", type=str, help="Target database (default: from config)")
    parser.add_argument("--limit", type=int, default=100, help="Max rows to display (default: 100)")
    args = parser.parse_args()

    validate_sql(args.sql)
    config = load_config()
    run_query(config, args.database, args.sql, args.limit)


if __name__ == "__main__":
    main()
