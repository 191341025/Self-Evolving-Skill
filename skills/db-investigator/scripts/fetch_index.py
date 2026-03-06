# -*- coding: utf-8 -*-
"""
Database metadata index tool.

Fetches all object names (tables, SPs, views, functions, triggers) for a
given database and writes Markdown index files for quick browsing.

Usage:
    python fetch_index.py                  # use default database from config
    python fetch_index.py --database other_db
"""

import sys
import argparse
import configparser
from datetime import datetime
from pathlib import Path

try:
    import pymysql
except ImportError:
    print("Error: pymysql required. Run: pip install pymysql")
    sys.exit(1)


def load_config():
    config_path = Path(__file__).parent / "db_config.ini"
    if not config_path.exists():
        print(f"Error: config not found: {config_path}")
        sys.exit(1)
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    return config


def get_connection(config, database=None):
    db_name = database or config.get('target', 'database')
    conn = pymysql.connect(
        host=config.get('database', 'host'),
        port=config.getint('database', 'port'),
        user=config.get('database', 'user'),
        password=config.get('database', 'password'),
        database=db_name,
        charset=config.get('database', 'charset'),
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn, db_name


def fetch_tables(cursor, database):
    cursor.execute("""
        SELECT
            TABLE_NAME as table_name,
            TABLE_ROWS as row_count,
            ROUND(DATA_LENGTH / 1024 / 1024, 2) as data_size_mb,
            ROUND(INDEX_LENGTH / 1024 / 1024, 2) as index_size_mb,
            TABLE_COMMENT as comment,
            CREATE_TIME as create_time,
            UPDATE_TIME as update_time
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = %s
          AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """, (database,))
    return cursor.fetchall()


def fetch_procedures(cursor, database):
    cursor.execute("""
        SELECT
            ROUTINE_NAME as name,
            CREATED as create_time,
            LAST_ALTERED as update_time,
            ROUTINE_COMMENT as comment
        FROM information_schema.ROUTINES
        WHERE ROUTINE_SCHEMA = %s
          AND ROUTINE_TYPE = 'PROCEDURE'
        ORDER BY ROUTINE_NAME
    """, (database,))
    return cursor.fetchall()


def fetch_functions(cursor, database):
    cursor.execute("""
        SELECT
            ROUTINE_NAME as name,
            DATA_TYPE as return_type,
            CREATED as create_time,
            LAST_ALTERED as update_time,
            ROUTINE_COMMENT as comment
        FROM information_schema.ROUTINES
        WHERE ROUTINE_SCHEMA = %s
          AND ROUTINE_TYPE = 'FUNCTION'
        ORDER BY ROUTINE_NAME
    """, (database,))
    return cursor.fetchall()


def fetch_views(cursor, database):
    cursor.execute("""
        SELECT
            TABLE_NAME as view_name
        FROM information_schema.VIEWS
        WHERE TABLE_SCHEMA = %s
        ORDER BY TABLE_NAME
    """, (database,))
    return cursor.fetchall()


def fetch_triggers(cursor, database):
    cursor.execute("""
        SELECT
            TRIGGER_NAME as name,
            EVENT_MANIPULATION as event,
            EVENT_OBJECT_TABLE as table_name,
            ACTION_TIMING as timing,
            CREATED as create_time
        FROM information_schema.TRIGGERS
        WHERE TRIGGER_SCHEMA = %s
        ORDER BY TRIGGER_NAME
    """, (database,))
    return cursor.fetchall()


def write_tables_md(tables, output_path, database):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {database} - Table Index\n\n")
        f.write(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> Total tables: **{len(tables)}**\n\n")

        f.write("## Statistics\n\n")
        total_rows = sum(t['row_count'] or 0 for t in tables)
        total_data = sum(t['data_size_mb'] or 0 for t in tables)
        total_index = sum(t['index_size_mb'] or 0 for t in tables)
        f.write(f"- Estimated total rows: {total_rows:,}\n")
        f.write(f"- Data size: {total_data:,.2f} MB\n")
        f.write(f"- Index size: {total_index:,.2f} MB\n\n")

        f.write("## Tables\n\n")
        f.write("| # | Table | Rows (est.) | Data MB | Index MB | Comment |\n")
        f.write("|---|-------|-------------|---------|----------|---------|\n")

        for i, t in enumerate(tables, 1):
            name = t['table_name']
            rows = f"{t['row_count']:,}" if t['row_count'] else '0'
            data = f"{t['data_size_mb']:.2f}" if t['data_size_mb'] else '0'
            index = f"{t['index_size_mb']:.2f}" if t['index_size_mb'] else '0'
            comment = (t['comment'] or '')[:50]
            f.write(f"| {i} | `{name}` | {rows} | {data} | {index} | {comment} |\n")

        f.write(f"\n---\n*Last updated: {datetime.now().strftime('%Y-%m-%d')}*\n")

    print(f"  Table index written: {output_path}")


def write_procedures_md(procedures, output_path, database):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {database} - Stored Procedure Index\n\n")
        f.write(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> Total SPs: **{len(procedures)}**\n\n")

        f.write("## Stored Procedures\n\n")
        f.write("| # | Name | Created | Modified | Comment |\n")
        f.write("|---|------|---------|----------|---------|\n")

        for i, p in enumerate(procedures, 1):
            name = p['name']
            created = p['create_time'].strftime('%Y-%m-%d') if p['create_time'] else '-'
            updated = p['update_time'].strftime('%Y-%m-%d') if p['update_time'] else '-'
            comment = (p['comment'] or '')[:30]
            f.write(f"| {i} | `{name}` | {created} | {updated} | {comment} |\n")

        f.write(f"\n---\n*Last updated: {datetime.now().strftime('%Y-%m-%d')}*\n")

    print(f"  Procedure index written: {output_path}")


def write_functions_md(functions, output_path, database):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {database} - Function Index\n\n")
        f.write(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> Total functions: **{len(functions)}**\n\n")

        f.write("## Functions\n\n")
        f.write("| # | Name | Return Type | Created | Modified |\n")
        f.write("|---|------|-------------|---------|----------|\n")

        for i, fn in enumerate(functions, 1):
            name = fn['name']
            ret_type = fn['return_type'] or '-'
            created = fn['create_time'].strftime('%Y-%m-%d') if fn['create_time'] else '-'
            updated = fn['update_time'].strftime('%Y-%m-%d') if fn['update_time'] else '-'
            f.write(f"| {i} | `{name}` | {ret_type} | {created} | {updated} |\n")

        f.write(f"\n---\n*Last updated: {datetime.now().strftime('%Y-%m-%d')}*\n")

    print(f"  Function index written: {output_path}")


def write_views_md(views, output_path, database):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {database} - View Index\n\n")
        f.write(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> Total views: **{len(views)}**\n\n")

        f.write("## Views\n\n")
        f.write("| # | Name |\n")
        f.write("|---|------|\n")

        for i, v in enumerate(views, 1):
            f.write(f"| {i} | `{v['view_name']}` |\n")

        f.write(f"\n---\n*Last updated: {datetime.now().strftime('%Y-%m-%d')}*\n")

    print(f"  View index written: {output_path}")


def write_triggers_md(triggers, output_path, database):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {database} - Trigger Index\n\n")
        f.write(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> Total triggers: **{len(triggers)}**\n\n")

        f.write("## Triggers\n\n")
        f.write("| # | Name | Table | Event | Timing |\n")
        f.write("|---|------|-------|-------|--------|\n")

        for i, t in enumerate(triggers, 1):
            f.write(f"| {i} | `{t['name']}` | `{t['table_name']}` | {t['event']} | {t['timing']} |\n")

        f.write(f"\n---\n*Last updated: {datetime.now().strftime('%Y-%m-%d')}*\n")

    print(f"  Trigger index written: {output_path}")


def write_summary_md(database, counts, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {database} - Database Overview\n\n")
        f.write(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Object Summary\n\n")
        f.write("| Object Type | Count | Index File |\n")
        f.write("|-------------|-------|------------|\n")
        f.write(f"| Tables | {counts['tables']} | [tables.md](tables.md) |\n")
        f.write(f"| Stored Procedures | {counts['procedures']} | [procedures.md](procedures.md) |\n")
        f.write(f"| Functions | {counts['functions']} | [functions.md](functions.md) |\n")
        f.write(f"| Views | {counts['views']} | [views.md](views.md) |\n")
        f.write(f"| Triggers | {counts['triggers']} | [triggers.md](triggers.md) |\n")

        f.write(f"\n---\n*Last updated: {datetime.now().strftime('%Y-%m-%d')}*\n")

    print(f"  Summary written: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Database metadata index tool')
    parser.add_argument('--database', type=str, help='Target database (default: from config)')
    args = parser.parse_args()

    config = load_config()

    script_dir = Path(__file__).parent
    base_path = script_dir / config.get('output', 'base_path')

    print(f"\n{'='*60}")
    print(f"Database Metadata Index Tool")
    print(f"{'='*60}")

    try:
        conn, db_name = get_connection(config, args.database)
        print(f"\nConnected to: {db_name}")

        output_dir = base_path / "_index" / db_name
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {output_dir}")

        with conn.cursor() as cursor:
            print(f"\nFetching metadata...")

            print("  - Tables...")
            tables = fetch_tables(cursor, db_name)

            print("  - Stored Procedures...")
            procedures = fetch_procedures(cursor, db_name)

            print("  - Functions...")
            functions = fetch_functions(cursor, db_name)

            print("  - Views...")
            views = fetch_views(cursor, db_name)

            print("  - Triggers...")
            triggers = fetch_triggers(cursor, db_name)

        print(f"\nWriting index files...")
        write_tables_md(tables, output_dir / "tables.md", db_name)
        write_procedures_md(procedures, output_dir / "procedures.md", db_name)
        write_functions_md(functions, output_dir / "functions.md", db_name)
        write_views_md(views, output_dir / "views.md", db_name)
        write_triggers_md(triggers, output_dir / "triggers.md", db_name)

        counts = {
            'tables': len(tables),
            'procedures': len(procedures),
            'functions': len(functions),
            'views': len(views),
            'triggers': len(triggers)
        }
        write_summary_md(db_name, counts, output_dir / "README.md")

        print(f"\n{'='*60}")
        print(f"Done!")
        print(f"  Tables: {counts['tables']}")
        print(f"  Stored Procedures: {counts['procedures']}")
        print(f"  Functions: {counts['functions']}")
        print(f"  Views: {counts['views']}")
        print(f"  Triggers: {counts['triggers']}")
        print(f"{'='*60}\n")

    except pymysql.Error as e:
        print(f"\nDatabase error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()
