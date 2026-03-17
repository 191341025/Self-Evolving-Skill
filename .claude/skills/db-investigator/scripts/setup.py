# -*- coding: utf-8 -*-
"""
Interactive setup wizard for db-investigator skill.

Collects MySQL connection info, writes db_config.ini, tests the
connection, and initializes the knowledge system via decay_engine.py.

Usage:
    python setup.py
    python setup.py --help
"""

import configparser
import getpass
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "db_config.ini"
DECAY_ENGINE = SCRIPT_DIR / "decay_engine.py"

BANNER_LINE = "\u2550" * 42


def check_pymysql():
    """Verify pymysql is available; exit with guidance if not."""
    try:
        __import__("pymysql")
    except ImportError:
        print("Error: pymysql is required but not installed.")
        print("  Install it with:  pip install pymysql")
        sys.exit(1)


def prompt(label, default=None, required=False, hide=False):
    """Prompt the user for input with an optional default value.

    Args:
        label: Display label for the prompt.
        default: Default value shown in brackets; None means no default.
        required: If True and input is empty (no default), raise ValueError.
        hide: If True, use getpass to hide typed characters.

    Returns:
        The user-provided string, or the default if input was empty.
    """
    if default is not None:
        suffix = " [{}]: ".format(default)
    else:
        suffix = ": "

    display = "  {} {}".format(label, suffix) if default is not None else "  {}: ".format(label)

    if hide:
        # getpass.getpass prints its own prompt; we match the format
        value = getpass.getpass(prompt=display)
    else:
        value = input(display)

    value = value.strip()

    if not value:
        if default is not None:
            return str(default)
        if required:
            raise ValueError("{} is required.".format(label))
        return ""

    return value


def write_config(host, port, user, password, database, charset="utf8"):
    """Write db_config.ini using configparser."""
    config = configparser.ConfigParser()

    config["database"] = {
        "host": host,
        "port": str(port),
        "user": user,
        "password": password,
        "charset": charset,
    }

    config["target"] = {
        "database": database,
    }

    config["output"] = {
        "base_path": "../db_schemas/",
    }

    with open(str(CONFIG_PATH), "w", encoding="utf-8") as f:
        config.write(f)


def test_connection(host, port, user, password, database, charset="utf8"):
    """Test MySQL connection with SELECT 1.

    Returns:
        (True, None) on success, (False, error_message) on failure.
    """
    import pymysql

    try:
        conn = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            charset=charset,
            connect_timeout=10,
        )
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        finally:
            conn.close()
        return True, None
    except pymysql.Error as exc:
        return False, str(exc)


def run_decay_init():
    """Call decay_engine.py init as a subprocess."""
    cmd = [sys.executable, str(DECAY_ENGINE), "init"]
    result = subprocess.run(
        cmd,
        cwd=str(SCRIPT_DIR),
        capture_output=True,
        text=True,
    )
    # Print stdout regardless of exit code
    if result.stdout:
        for line in result.stdout.rstrip("\n").split("\n"):
            print(line)
    if result.stderr:
        for line in result.stderr.rstrip("\n").split("\n"):
            print(line)
    return result.returncode


def configure_hook():
    """Register the PostToolUse hook in .claude/settings.json.

    Finds the project root (parent of .claude/skills/) and adds the
    post-investigation hook to .claude/settings.json if not already present.
    Idempotent: safe to re-run.
    """
    # Walk up from scripts/ to find .claude/ directory
    skill_dir = SCRIPT_DIR.parent  # db-investigator/
    claude_dir = skill_dir.parent.parent  # .claude/
    settings_path = claude_dir / "settings.json"

    hook_command = "python .claude/skills/db-investigator/hooks/post_investigation.py"

    # Load existing settings or start fresh
    settings = {}
    if settings_path.exists():
        try:
            with open(str(settings_path), "r", encoding="utf-8") as f:
                settings = json.loads(f.read())
        except (json.JSONDecodeError, OSError):
            settings = {}

    # Check if hook already registered
    hooks = settings.get("hooks", {})
    post_hooks = hooks.get("PostToolUse", [])

    already_registered = False
    for entry in post_hooks:
        entry_hooks = entry.get("hooks", [])
        for h in entry_hooks:
            if h.get("command", "") == hook_command:
                already_registered = True
                break

    if already_registered:
        print("\u2713 Hook already registered")
        return

    # Add the hook
    new_hook_entry = {
        "matcher": "Bash",
        "hooks": [
            {
                "type": "command",
                "command": hook_command,
            }
        ],
    }
    post_hooks.append(new_hook_entry)
    hooks["PostToolUse"] = post_hooks
    settings["hooks"] = hooks

    with open(str(settings_path), "w", encoding="utf-8") as f:
        f.write(json.dumps(settings, indent=2, ensure_ascii=False))

    print("\u2713 Registered post-investigation hook")


def main():
    """Run the interactive setup wizard."""
    # --help support
    if "--help" in sys.argv or "-h" in sys.argv:
        print("usage: python setup.py")
        print()
        print("Interactive setup wizard for db-investigator skill.")
        print("Collects MySQL connection info, writes db_config.ini,")
        print("tests the connection, and initializes the knowledge system.")
        return 0

    # Check dependency first
    check_pymysql()

    print()
    print(BANNER_LINE)
    print("  db-investigator \u2014 Setup Wizard")
    print(BANNER_LINE)
    print()
    print("This skill requires a MySQL database connection.")
    print()

    # Check for existing config
    if CONFIG_PATH.exists():
        # Detect placeholder/unconfigured state — skip confirmation
        try:
            cfg = configparser.ConfigParser()
            cfg.read(str(CONFIG_PATH), encoding="utf-8")
            host_val = cfg.get("database", "host", fallback="")
            db_val = cfg.get("target", "database", fallback="")
            is_placeholder = (
                not host_val
                or host_val.startswith("<")
                or not db_val
                or db_val.startswith("<")
            )
        except Exception:
            is_placeholder = True

        if not is_placeholder:
            overwrite = input("  db_config.ini already exists. Overwrite? [y/N]: ").strip().lower()
            if overwrite not in ("y", "yes"):
                print("  Aborted. Existing config preserved.")
                return 0
            print()

    # Collect connection info
    try:
        host = prompt("Host", default="localhost")
        port_str = prompt("Port", default="3306")
        user = prompt("User", default="root")
        password = prompt("Password", hide=True)
        database = prompt("Database name", required=True)
    except ValueError as exc:
        print()
        print("Error: {}".format(exc))
        return 1
    except (KeyboardInterrupt, EOFError):
        print()
        print("  Setup cancelled.")
        return 1

    # Validate port
    try:
        port = int(port_str)
    except ValueError:
        print()
        print("Error: port must be a number, got '{}'.".format(port_str))
        return 1

    # Write config
    print()
    write_config(host, port, user, password, database)
    print("\u2713 Created db_config.ini")

    # Test connection
    print()
    print("Testing connection...")
    ok, err = test_connection(host, port, user, password, database)
    if ok:
        print("\u2713 Connected to {}:{}/{}".format(host, port, database))
    else:
        print("\u2717 Connection failed: {}".format(err))
        print()
        print("The config file has been written. You can edit it manually:")
        print("  {}".format(CONFIG_PATH))
        print()
        print("Check your credentials, ensure the database exists, and that")
        print("the MySQL server is running and accessible.")
        # Do NOT delete the config -- let user fix manually
        # Still run init so the knowledge system is ready
        print()
        print("Initializing knowledge system anyway...")
        run_decay_init()
        return 1

    # Initialize knowledge system
    print()
    print("Initializing knowledge system...")
    run_decay_init()

    # Register hook for automatic knowledge evolution
    print()
    print("Registering post-investigation hook...")
    configure_hook()

    # Success banner
    print()
    print(BANNER_LINE)
    print("  Setup complete! The skill is ready to use.")
    print(BANNER_LINE)
    print()
    print("Next steps:")
    print("  1. Start a Claude Code conversation")
    print("  2. Ask any database question \u2014 the skill activates automatically")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
