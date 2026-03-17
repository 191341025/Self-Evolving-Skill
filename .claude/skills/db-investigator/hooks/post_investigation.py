#!/usr/bin/env python3
"""PostToolUse hook for db-investigator skill.

Fires after Bash commands. If the command invoked a db-investigator tool
(db_query.py, fetch_structure.py, fetch_index.py), injects a system-level
instruction telling the AI to execute the Post-Investigation Checkpoint.

Hook input (stdin): JSON with tool_input.command and tool_response.
Hook output (stdout): JSON with hookSpecificOutput.additionalContext.
"""

import json
import sys


SKILL_TOOLS = ("db_query", "fetch_structure", "fetch_index")

CHECKPOINT_MESSAGE = (
    "[Post-Investigation Checkpoint — REQUIRED]\n"
    "A database investigation tool just completed. You MUST now:\n"
    "1. Evaluate: did this investigation reveal any domain knowledge "
    "(table relationships, business rules, query patterns, data characteristics)?\n"
    "2. If YES → run Gates 2-5 per SKILL.md Knowledge Governance Protocol, "
    "then persist via: python $S/decay_engine.py inject --type <type> "
    '--content "<knowledge>" --target <file> --entities "<entities>"\n'
    "3. If NO (pure operational output only) → skip.\n"
    "Do this BEFORE responding to the user."
)


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return

        data = json.loads(raw)
        tool_input = data.get("tool_input", {})
        command = tool_input.get("command", "")

        # Check if the command invoked a db-investigator tool
        if not any(tool in command for tool in SKILL_TOOLS):
            return

        # Inject checkpoint instruction
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": CHECKPOINT_MESSAGE,
            }
        }
        print(json.dumps(output))

    except (json.JSONDecodeError, KeyError, TypeError):
        # Silent fail — don't break the user's workflow
        pass


if __name__ == "__main__":
    main()
