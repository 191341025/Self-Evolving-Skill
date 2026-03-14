"""
CLI entry point for the confidence decay engine.

Phase 1: scan subcommand — scans markdown files for decay tags and
reports confidence levels with classification.

Phase 2: feedback and reset subcommands — record feedback (success/failure)
on individual decay tags, or reset them to fresh state.

Usage:
    python decay_engine.py scan --file <path>
    python decay_engine.py scan --path <dir>
    python decay_engine.py feedback --file <path> --line <n> --result success|failure
    python decay_engine.py reset --file <path> --line <n>
"""

import argparse
import sys
from pathlib import Path

from core.models import confidence, classify_confidence
from core.parser import (
    VALID_TYPES,
    append_entry,
    increment_feedback,
    parse_decay_tag,
    parse_decay_tags,
    reset_entry,
    scan_directory,
    update_decay_tag,
)
from core.formulas import days_since

# Directory where reference knowledge files are stored
REFERENCES_DIR = Path(__file__).resolve().parent.parent / "references"

# Short display names for knowledge types
TYPE_SHORT: dict[str, str] = {
    "schema":          "schema",
    "business_rule":   "biz_rule",
    "tool_experience": "tool_exp",
    "query_pattern":   "qry_pat",
    "data_range":      "data_rng",
    "data_snapshot":   "data_snap",
}


def format_entry(entry: dict, use_relative: bool = False) -> str:
    """Format a single decay entry into one display line.

    Args:
        entry: Dict with keys from parser (line, type, confirmed, C0,
               alpha, beta, context) and optionally 'file'.
        use_relative: If True, use entry['file'] (relative path from
                      --path mode). If False, use just the filename.

    Returns:
        Formatted string for terminal output.
    """
    c_val = confidence(
        entry["type"],
        entry["confirmed"],
        alpha=entry["alpha"],
        beta=entry["beta"],
        c0=entry["C0"],
    )
    level = classify_confidence(c_val)
    t = days_since(entry["confirmed"])
    short_type = TYPE_SHORT.get(entry["type"], entry["type"])

    if use_relative and "file" in entry:
        location = f"{entry['file']}:{entry['line']}"
    else:
        # Extract just the filename when using --file mode
        if "file" in entry:
            fname = Path(entry["file"]).name
        else:
            fname = "unknown"
        location = f"{fname}:{entry['line']}"

    alpha = entry["alpha"]
    beta = entry["beta"]

    return (
        f"[{level:<12s}] "
        f"{location:<30s} "
        f"C={c_val:.3f}  "
        f"{short_type:<10s} "
        f"\u03b1={alpha} \u03b2={beta}  "
        f"{t}d"
    )


def run_scan(args: argparse.Namespace) -> int:
    """Execute the scan subcommand.

    Returns:
        Exit code: 0 = all TRUST, 1 = has VERIFY, 2 = has REVALIDATE.
    """
    if not args.file and not args.path:
        print("Error: --file or --path is required.", file=sys.stderr)
        return 1

    use_relative = False
    entries: list[dict] = []

    if args.file:
        fpath = args.file
        if not Path(fpath).exists():
            print(f"Error: file not found: {fpath}", file=sys.stderr)
            return 1
        tags = parse_decay_tags(fpath)
        # Attach filename so format_entry can extract it
        fname = Path(fpath).name
        for tag in tags:
            tag["file"] = fname
        entries = tags

    elif args.path:
        dpath = args.path
        if not Path(dpath).exists():
            print(f"Error: directory not found: {dpath}", file=sys.stderr)
            return 1
        entries = scan_directory(dpath)
        use_relative = True

    if not entries:
        print("No decay tags found.")
        return 0

    # Compute confidence for sorting (low to high)
    def sort_key(e: dict) -> float:
        return confidence(
            e["type"], e["confirmed"],
            alpha=e["alpha"], beta=e["beta"],
            c0=e["C0"],
        )

    entries.sort(key=sort_key)

    # Print each entry
    for entry in entries:
        print(format_entry(entry, use_relative=use_relative))

    # Summary
    levels = []
    for entry in entries:
        c_val = confidence(
            entry["type"], entry["confirmed"],
            alpha=entry["alpha"], beta=entry["beta"],
            c0=entry["C0"],
        )
        levels.append(classify_confidence(c_val))

    trust_count = levels.count("TRUST")
    verify_count = levels.count("VERIFY")
    revalidate_count = levels.count("REVALIDATE")
    total = len(levels)

    print("---")
    print(
        f"{total} entries: "
        f"{trust_count} TRUST, "
        f"{verify_count} VERIFY, "
        f"{revalidate_count} REVALIDATE"
    )

    # Exit code
    if revalidate_count > 0:
        return 2
    if verify_count > 0:
        return 1
    return 0


def run_feedback(args: argparse.Namespace) -> int:
    """Execute the feedback subcommand.

    Increments alpha (success) or beta (failure) for a decay tag at the
    specified file and line, then prints the updated state.

    Returns:
        Exit code: 0 on success, 1 on error.
    """
    try:
        result = increment_feedback(args.file, args.line, args.result)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Recompute confidence with the updated counters
    c_val = confidence(
        result["type"],
        result["confirmed"],
        alpha=result["alpha"],
        beta=result["beta"],
        c0=result["C0"],
    )
    short_type = TYPE_SHORT.get(result["type"], result["type"])
    fname = Path(args.file).name
    print(
        f"Updated {fname}:{args.line} — "
        f"{result['action']} ({short_type}, C={c_val:.3f})"
    )
    return 0


def run_reset(args: argparse.Namespace) -> int:
    """Execute the reset subcommand.

    Resets a decay tag to fresh state (confirmed=today, alpha=0, beta=0)
    and prints the result.

    Returns:
        Exit code: 0 on success, 1 on error.
    """
    try:
        result = reset_entry(args.file, args.line)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # After reset, confidence is 1.0 (confirmed today, C0=1.0, alpha=0, beta=0)
    c_val = confidence(
        result["type"],
        result["confirmed"],
        alpha=result["alpha"],
        beta=result["beta"],
        c0=result["C0"],
    )
    fname = Path(args.file).name
    print(
        f"Reset {fname}:{args.line} — "
        f"{result['action']} → C={c_val:.3f}"
    )
    return 0


def run_inject(args: argparse.Namespace) -> int:
    """Handle the 'inject' subcommand."""
    target_path = REFERENCES_DIR / args.target
    lineno = append_entry(str(target_path), args.type, args.content)
    print(f"[inject] \u2713 written to {args.target}:{lineno} (type: {args.type})")
    return 0


def run_invalidate(args: argparse.Namespace) -> int:
    """Handle the 'invalidate' subcommand."""
    try:
        # Read the target line and parse its current tag state
        path = Path(args.file)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {args.file}")

        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()

        total_lines = len(lines)
        if args.line < 1 or args.line > total_lines:
            raise ValueError(
                f"Line number {args.line} out of range "
                f"(file has {total_lines} lines)"
            )

        parsed = parse_decay_tag(lines[args.line - 1])
        if parsed is None:
            raise ValueError(f"No decay tag found at line {args.line}")

        # Record old values for output
        old_c0 = parsed["C0"]
        old_alpha = parsed["alpha"]
        old_beta = parsed["beta"]

        # Apply invalidation: set C0=0.1, alpha=0, beta=0
        update_decay_tag(args.file, args.line, {
            "C0": 0.1,
            "alpha": 0,
            "beta": 0,
        })

        fname = Path(args.file).name
        print(
            f"[invalidate] \u2713 {fname}:{args.line} "
            f"C0 \u2192 0.1 (was: C0={old_c0} "
            f"\u03b1={old_alpha} \u03b2={old_beta})"
        )
        return 0

    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser with subcommands."""
    ap = argparse.ArgumentParser(
        prog="decay_engine",
        description="Confidence decay engine for knowledge management.",
    )
    subparsers = ap.add_subparsers(dest="command", help="Available commands")

    # scan subcommand
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan files for decay tags and report confidence levels.",
    )
    scan_parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a single markdown file to scan.",
    )
    scan_parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="Path to a directory to scan recursively.",
    )

    # feedback subcommand
    fb_parser = subparsers.add_parser(
        "feedback",
        help="Record success/failure feedback for a decay tag.",
    )
    fb_parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to the markdown file containing the decay tag.",
    )
    fb_parser.add_argument(
        "--line",
        type=int,
        required=True,
        help="1-based line number of the decay tag.",
    )
    fb_parser.add_argument(
        "--result",
        type=str,
        required=True,
        choices=["success", "failure"],
        help="Feedback result: 'success' increments alpha, 'failure' increments beta.",
    )

    # reset subcommand
    reset_parser = subparsers.add_parser(
        "reset",
        help="Reset a decay tag to fresh state (confirmed=today, alpha=0, beta=0).",
    )
    reset_parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to the markdown file containing the decay tag.",
    )
    reset_parser.add_argument(
        "--line",
        type=int,
        required=True,
        help="1-based line number of the decay tag.",
    )

    # inject subcommand
    sp_inject = subparsers.add_parser(
        "inject",
        help="Inject new knowledge entry",
    )
    sp_inject.add_argument(
        "--type",
        required=True,
        choices=sorted(VALID_TYPES),
        help="Knowledge type",
    )
    sp_inject.add_argument(
        "--content",
        required=True,
        help="Knowledge text (single line)",
    )
    sp_inject.add_argument(
        "--target",
        required=True,
        help="Target filename in references/",
    )

    # invalidate subcommand
    sp_inv = subparsers.add_parser(
        "invalidate",
        help="Mark knowledge as needing revalidation",
    )
    sp_inv.add_argument(
        "--file",
        required=True,
        help="Markdown file containing the tag",
    )
    sp_inv.add_argument(
        "--line",
        required=True,
        type=int,
        help="1-based line number of the decay tag",
    )

    return ap


def main() -> int:
    """Main entry point. Returns the process exit code."""
    ap = build_parser()
    args = ap.parse_args()

    if args.command is None:
        ap.print_help()
        return 1

    if args.command == "scan":
        return run_scan(args)

    if args.command == "feedback":
        return run_feedback(args)

    if args.command == "reset":
        return run_reset(args)

    if args.command == "inject":
        return run_inject(args)

    if args.command == "invalidate":
        return run_invalidate(args)

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
