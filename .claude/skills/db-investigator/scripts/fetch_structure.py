# -*- coding: utf-8 -*-
"""
Database structure fetching tool.

Fetches table DDL, column info, indexes, and stored procedure definitions.
Outputs SQL files for offline analysis.

Usage:
    python fetch_structure.py --tables table1,table2
    python fetch_structure.py --procedures sp1,sp2
    python fetch_structure.py --tables t1 --database other_db
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


def fetch_table_ddl(cursor, table_name):
    try:
        cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
        result = cursor.fetchone()
        if result:
            return result.get('Create Table', '')
    except Exception as e:
        return f"-- Error: cannot fetch DDL for table {table_name}: {e}"
    return ""


def fetch_table_columns(cursor, database, table_name):
    cursor.execute("""
        SELECT
            COLUMN_NAME,
            COLUMN_TYPE,
            IS_NULLABLE,
            COLUMN_KEY,
            COLUMN_DEFAULT,
            COLUMN_COMMENT
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
    """, (database, table_name))
    return cursor.fetchall()


def fetch_table_indexes(cursor, database, table_name):
    cursor.execute("""
        SELECT
            INDEX_NAME,
            COLUMN_NAME,
            NON_UNIQUE,
            SEQ_IN_INDEX
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY INDEX_NAME, SEQ_IN_INDEX
    """, (database, table_name))
    return cursor.fetchall()


def fetch_procedure_ddl(cursor, database, proc_name):
    try:
        cursor.execute(f"SHOW CREATE PROCEDURE `{proc_name}`")
        result = cursor.fetchone()
        if result:
            return result.get('Create Procedure', '')
    except Exception as e:
        return f"-- Error: cannot fetch SP {proc_name}: {e}"
    return ""


def fetch_sample_data(cursor, table_name, limit=10):
    try:
        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT {limit}")
        return cursor.fetchall()
    except Exception:
        return []


def write_table_file(table_name, ddl, columns, indexes, sample_data, output_dir, database):
    output_path = output_dir / f"{table_name}.sql"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"-- =====================================================\n")
        f.write(f"-- Table: {table_name}\n")
        f.write(f"-- Database: {database}\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- =====================================================\n\n")

        f.write("-- DDL\n")
        f.write(ddl)
        f.write(";\n\n")

        f.write("-- =====================================================\n")
        f.write("-- Columns\n")
        f.write("-- =====================================================\n")
        for col in columns:
            nullable = "NULL" if col['IS_NULLABLE'] == 'YES' else "NOT NULL"
            key = f"[{col['COLUMN_KEY']}]" if col['COLUMN_KEY'] else ""
            comment = col['COLUMN_COMMENT'] or ""
            f.write(f"-- {col['COLUMN_NAME']}: {col['COLUMN_TYPE']} {nullable} {key} {comment}\n")
        f.write("\n")

        if sample_data:
            f.write("-- =====================================================\n")
            f.write(f"-- Sample data (first {len(sample_data)} rows)\n")
            f.write("-- =====================================================\n")
            for row in sample_data:
                f.write(f"-- {row}\n")
            f.write("\n")

    return output_path


def write_procedure_file(proc_name, ddl, output_dir, database):
    output_path = output_dir / f"{proc_name}.sql"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"-- =====================================================\n")
        f.write(f"-- Stored Procedure: {proc_name}\n")
        f.write(f"-- Database: {database}\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- =====================================================\n\n")

        f.write("DELIMITER $$\n\n")
        f.write(ddl)
        f.write("$$\n\n")
        f.write("DELIMITER ;\n")

    return output_path


def main():
    parser = argparse.ArgumentParser(description='Database structure fetching tool')
    parser.add_argument('--tables', type=str, help='Table names, comma-separated')
    parser.add_argument('--procedures', type=str, help='Stored procedure names, comma-separated')
    parser.add_argument('--sample', type=int, default=5, help='Sample data rows (default: 5)')
    parser.add_argument('--database', type=str, help='Target database (default: from config)')

    args = parser.parse_args()

    tables = []
    procedures = []

    if args.tables:
        tables.extend(args.tables.split(','))
    if args.procedures:
        procedures.extend(args.procedures.split(','))

    if not tables and not procedures:
        print("Error: specify --tables or --procedures")
        parser.print_help()
        sys.exit(1)

    config = load_config()
    script_dir = Path(__file__).parent
    base_path = script_dir / config.get('output', 'base_path')

    print(f"\n{'='*60}")
    print(f"Database Structure Fetcher")
    print(f"{'='*60}")

    try:
        conn, db_name = get_connection(config, args.database)
        print(f"\nConnected to: {db_name}")

        tables_dir = base_path / db_name / "tables"
        procedures_dir = base_path / db_name / "procedures"
        tables_dir.mkdir(parents=True, exist_ok=True)
        procedures_dir.mkdir(parents=True, exist_ok=True)

        with conn.cursor() as cursor:
            if tables:
                print(f"\nFetching table structures...")
                for table_name in tables:
                    table_name = table_name.strip()
                    print(f"  - {table_name}...")

                    ddl = fetch_table_ddl(cursor, table_name)
                    columns = fetch_table_columns(cursor, db_name, table_name)
                    indexes = fetch_table_indexes(cursor, db_name, table_name)
                    sample_data = fetch_sample_data(cursor, table_name, args.sample)

                    output_path = write_table_file(
                        table_name, ddl, columns, indexes, sample_data,
                        tables_dir, db_name
                    )
                    print(f"    -> {output_path}")

            if procedures:
                print(f"\nFetching stored procedures...")
                for proc_name in procedures:
                    proc_name = proc_name.strip()
                    print(f"  - {proc_name}...")

                    ddl = fetch_procedure_ddl(cursor, db_name, proc_name)

                    output_path = write_procedure_file(
                        proc_name, ddl, procedures_dir, db_name
                    )
                    print(f"    -> {output_path}")

        print(f"\n{'='*60}")
        print(f"Done!")
        print(f"  Tables: {len(tables)}")
        print(f"  Stored Procedures: {len(procedures)}")
        print(f"{'='*60}\n")

    except pymysql.Error as e:
        print(f"\nDatabase error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()
