"""
Decay tag parser layer for markdown knowledge files.

Reads and extracts decay metadata tags embedded as HTML comments in
markdown files. Phase 1 provides read-only scanning; Phase 2 adds
in-place update, feedback increment, and reset operations. Phase 5A
adds entities tag support for entity-level matching.

Tag format:
    <!-- decay: type=schema confirmed=2026-01-15 C0=1.0 [alpha=2] [beta=1] -->
    <!-- entities: t_room, t_building -->
"""

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

# Valid values for the 'type' field
VALID_TYPES = frozenset({
    "schema",
    "business_rule",
    "tool_experience",
    "query_pattern",
    "data_range",
    "data_snapshot",
})

# Regex for the overall decay tag structure
_DECAY_TAG_RE = re.compile(
    r"<!--\s*decay:\s*(.+?)\s*-->"
)

# Regex for the entities tag structure
_ENTITIES_TAG_RE = re.compile(
    r"<!--\s*entities:\s*(.+?)\s*-->"
)

# Regex for individual key=value pairs inside the tag
_KV_RE = re.compile(
    r"(\w+)=([\S]+)"
)

# Required fields that must be present in every valid tag
_REQUIRED_FIELDS = ("type", "confirmed", "C0")

# Date format validation
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_decay_tag(line: str) -> Optional[Dict[str, Any]]:
    """Parse a single line for a decay tag and return its fields.

    Extracts key=value pairs from a decay HTML comment. Returns None if
    the line does not contain a decay tag or if the tag is malformed
    (missing required fields, invalid values). Malformed tags produce a
    warning on stderr.

    Args:
        line: A single line of text (may or may not contain a tag).

    Returns:
        A dict with keys {type, confirmed, C0, alpha, beta} on success,
        or None if the line has no decay tag or the tag is malformed.

    Example:
        >>> parse_decay_tag('<!-- decay: type=schema confirmed=2026-01-15 C0=1.0 -->')
        {'type': 'schema', 'confirmed': '2026-01-15', 'C0': 1.0, 'alpha': 0, 'beta': 0}
    """
    match = _DECAY_TAG_RE.search(line)
    if not match:
        return None

    raw_body = match.group(1)
    pairs = dict(_KV_RE.findall(raw_body))

    # Check required fields
    for field in _REQUIRED_FIELDS:
        if field not in pairs:
            print(
                f"[decay-parser] WARNING: malformed tag (missing '{field}'): "
                f"{line.strip()}",
                file=sys.stderr,
            )
            return None

    # Validate type
    tag_type = pairs["type"]
    if tag_type not in VALID_TYPES:
        print(
            f"[decay-parser] WARNING: invalid type '{tag_type}': "
            f"{line.strip()}",
            file=sys.stderr,
        )
        return None

    # Validate confirmed date format
    confirmed = pairs["confirmed"]
    if not _DATE_RE.match(confirmed):
        print(
            f"[decay-parser] WARNING: invalid date format '{confirmed}': "
            f"{line.strip()}",
            file=sys.stderr,
        )
        return None

    # Parse C0
    try:
        c0 = float(pairs["C0"])
    except ValueError:
        print(
            f"[decay-parser] WARNING: invalid C0 value '{pairs['C0']}': "
            f"{line.strip()}",
            file=sys.stderr,
        )
        return None

    # Parse optional alpha (default 0) — float to support weighted feedback
    alpha_raw = pairs.get("alpha", "0")
    try:
        alpha = float(alpha_raw)
        if alpha < 0:
            raise ValueError("negative")
    except ValueError:
        print(
            f"[decay-parser] WARNING: invalid alpha value '{alpha_raw}': "
            f"{line.strip()}",
            file=sys.stderr,
        )
        return None

    # Parse optional beta (default 0) — float to support weighted feedback
    beta_raw = pairs.get("beta", "0")
    try:
        beta = float(beta_raw)
        if beta < 0:
            raise ValueError("negative")
    except ValueError:
        print(
            f"[decay-parser] WARNING: invalid beta value '{beta_raw}': "
            f"{line.strip()}",
            file=sys.stderr,
        )
        return None

    return {
        "type": tag_type,
        "confirmed": confirmed,
        "C0": c0,
        "alpha": alpha,
        "beta": beta,
    }


def parse_entities_tag(line: str) -> Optional[List[str]]:
    """Parse a single line for an entities tag and return entity names.

    Args:
        line: A single line of text (may or may not contain a tag).

    Returns:
        A list of entity name strings on success, or None if the line
        has no entities tag.

    Example:
        >>> parse_entities_tag('<!-- entities: t_room, t_building -->')
        ['t_room', 't_building']
    """
    match = _ENTITIES_TAG_RE.search(line)
    if not match:
        return None
    raw = match.group(1)
    entities = [e.strip() for e in raw.split(",") if e.strip()]
    return entities if entities else None


def parse_decay_tags(file_path: str) -> List[Dict[str, Any]]:
    """Scan an entire markdown file and extract all decay tags.

    Reads the file line by line, collecting valid decay tags along with
    their line numbers and contextual headings.

    Args:
        file_path: Absolute or relative path to the markdown file.

    Returns:
        A list of dicts, each containing:
            line     - 1-based line number where the tag was found
            type     - knowledge type
            confirmed - confirmation date string (YYYY-MM-DD)
            C0       - initial confidence value
            alpha    - positive feedback count
            beta     - negative feedback count
            context  - nearest preceding heading or first non-empty text

    Raises:
        FileNotFoundError: If file_path does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    results: List[Dict[str, Any]] = []
    current_context: str = ""

    with open(path, "r", encoding="utf-8") as fh:
        lines = list(fh)

    for idx, line in enumerate(lines):
        line_num = idx + 1
        stripped = line.strip()

        # Track headings and first non-empty text as context
        if stripped.startswith("#"):
            current_context = stripped.lstrip("#").strip()
        elif stripped and not current_context:
            current_context = stripped

        parsed = parse_decay_tag(line)
        if parsed is not None:
            # Lookahead: check next line for entities tag
            entities: List[str] = []
            if idx + 1 < len(lines):
                entities_parsed = parse_entities_tag(lines[idx + 1])
                if entities_parsed is not None:
                    entities = entities_parsed

            entry = {
                "line": line_num,
                "context": current_context,
                "entities": entities,
                **parsed,
            }
            results.append(entry)

    return results


def scan_directory(
    dir_path: str, pattern: str = "*.md"
) -> List[Dict[str, Any]]:
    """Scan all matching files in a directory for decay tags.

    Recursively searches for files matching the glob pattern, extracts
    decay tags from each, and returns a combined list with file paths.

    Args:
        dir_path: Absolute or relative path to the directory.
        pattern:  Glob pattern for file matching (default: "*.md").

    Returns:
        A list of dicts. Each dict is the same as parse_decay_tags output
        plus a "file" key containing the path relative to dir_path.

    Raises:
        FileNotFoundError: If dir_path does not exist.
    """
    base = Path(dir_path)
    if not base.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    results: List[Dict[str, Any]] = []

    for md_file in sorted(base.rglob(pattern)):
        # Skip _index.md files
        if md_file.name == "_index.md":
            continue

        tags = parse_decay_tags(str(md_file))
        rel_path = str(md_file.relative_to(base))
        # Normalise path separators to forward slash for consistency
        rel_path = rel_path.replace("\\", "/")

        for tag in tags:
            tag["file"] = rel_path
            results.append(tag)

    return results


# ---------------------------------------------------------------------------
# Phase 2: Write operations
# ---------------------------------------------------------------------------

# Fixed field order for tag reconstruction
_TAG_FIELD_ORDER = ("type", "confirmed", "C0", "alpha", "beta")


def _rebuild_entities_line(
    entities: List[str], leading_whitespace: str
) -> str:
    """Reconstruct an entities tag line from a list of entity names.

    Args:
        entities: List of entity name strings.
        leading_whitespace: Whitespace prefix to preserve indentation.

    Returns:
        A complete entities tag line (without trailing newline).
    """
    body = ", ".join(entities)
    return f"{leading_whitespace}<!-- entities: {body} -->"


def _rebuild_tag_line(fields: Dict[str, Any], leading_whitespace: str) -> str:
    """Reconstruct a decay tag line from field values.

    Args:
        fields: Dict with keys type, confirmed, C0, alpha, beta.
        leading_whitespace: Whitespace prefix to preserve indentation.

    Returns:
        A complete tag line (without trailing newline).
    """
    parts = []
    for key in _TAG_FIELD_ORDER:
        val = fields[key]
        if key == "C0":
            # C0 always has a decimal point
            val = f"{float(val):.1f}" if float(val) == int(float(val)) else str(float(val))
        elif key in ("alpha", "beta"):
            # Show as int when whole number, float when fractional
            fval = float(val)
            val = str(int(fval)) if fval == int(fval) else str(fval)
        parts.append(f"{key}={val}")
    body = " ".join(parts)
    return f"{leading_whitespace}<!-- decay: {body} -->"


def update_decay_tag(
    file_path: str, line_number: int, updates: Dict[str, Any]
) -> bool:
    """Update specific fields of a decay tag at a given line in a file.

    Reads the file, validates the target line contains a decay tag,
    applies the requested field updates, and writes the file back.
    Only the specified fields are changed; all other fields and all
    other lines in the file are preserved exactly.

    Args:
        file_path:   Absolute or relative path to the markdown file.
        line_number: 1-based line number of the decay tag to update.
        updates:     Dict of field names to new values. Supported keys:
                     alpha (int), beta (int), confirmed (str), C0 (float).

    Returns:
        True on success.

    Raises:
        FileNotFoundError: If file_path does not exist.
        ValueError: If line_number is out of range, the target line has
                    no decay tag, or updates is empty.
    """
    if not updates:
        raise ValueError("No updates provided")

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    total_lines = len(lines)
    if line_number < 1 or line_number > total_lines:
        raise ValueError(
            f"Line number {line_number} out of range "
            f"(file has {total_lines} lines)"
        )

    idx = line_number - 1
    target_line = lines[idx]

    parsed = parse_decay_tag(target_line)
    if parsed is None:
        raise ValueError(f"No decay tag found at line {line_number}")

    # Determine leading whitespace of the original line
    stripped = target_line.lstrip()
    leading_ws = target_line[: len(target_line) - len(stripped)]

    # Merge updates into parsed fields
    merged = dict(parsed)
    merged.update(updates)

    # Rebuild the tag line, preserving trailing newline if present
    new_tag = _rebuild_tag_line(merged, leading_ws)
    trailing = "\n" if target_line.endswith("\n") else ""
    lines[idx] = new_tag + trailing

    with open(path, "w", encoding="utf-8") as fh:
        fh.writelines(lines)

    return True


def update_entities_tag(
    file_path: str, line_number: int, entities: List[str]
) -> bool:
    """Update the entities tag at a given line in a file.

    Reads the file, validates the target line contains an entities tag,
    replaces it with the new entity list, and writes the file back.

    Args:
        file_path:   Absolute or relative path to the markdown file.
        line_number: 1-based line number of the entities tag to update.
        entities:    New list of entity names.

    Returns:
        True on success.

    Raises:
        FileNotFoundError: If file_path does not exist.
        ValueError: If line_number is out of range, the target line has
                    no entities tag, or entities is empty.
    """
    if not entities:
        raise ValueError("entities list must not be empty")

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    total_lines = len(lines)
    if line_number < 1 or line_number > total_lines:
        raise ValueError(
            f"Line number {line_number} out of range "
            f"(file has {total_lines} lines)"
        )

    idx = line_number - 1
    target_line = lines[idx]

    parsed = parse_entities_tag(target_line)
    if parsed is None:
        raise ValueError(f"No entities tag found at line {line_number}")

    # Determine leading whitespace
    stripped = target_line.lstrip()
    leading_ws = target_line[: len(target_line) - len(stripped)]

    new_tag = _rebuild_entities_line(entities, leading_ws)
    trailing = "\n" if target_line.endswith("\n") else ""
    lines[idx] = new_tag + trailing

    with open(path, "w", encoding="utf-8") as fh:
        fh.writelines(lines)

    return True


def increment_feedback(
    file_path: str, line_number: int, result: str, weight: float = 1.0
) -> Dict[str, Any]:
    """Increment alpha or beta for a decay tag and return updated info.

    Convenience wrapper around update_decay_tag that bumps alpha or beta
    by the given weight. Hard signals use weight=1.0 (default), soft
    signals use weight=0.3.

    On success, confirmed_at is also refreshed to today (the knowledge
    was used successfully, so it's effectively re-confirmed). On failure,
    confirmed_at is NOT updated (time continues to accumulate).

    Args:
        file_path:   Path to the markdown file.
        line_number: 1-based line number of the decay tag.
        result:      "success" to increment alpha, "failure" to increment beta.
        weight:      Feedback weight (default 1.0). Use 0.3 for soft signals.

    Returns:
        Dict with keys: type, confirmed, C0, alpha, beta, action.

    Raises:
        ValueError: If result is not "success" or "failure", weight <= 0,
                    or the target line has no decay tag.
    """
    if result not in ("success", "failure"):
        raise ValueError(
            f"result must be 'success' or 'failure', got '{result}'"
        )
    if weight <= 0:
        raise ValueError(f"weight must be > 0, got {weight}")

    # Read current tag state
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    total_lines = len(lines)
    if line_number < 1 or line_number > total_lines:
        raise ValueError(
            f"Line number {line_number} out of range "
            f"(file has {total_lines} lines)"
        )

    parsed = parse_decay_tag(lines[line_number - 1])
    if parsed is None:
        raise ValueError(f"No decay tag found at line {line_number}")

    today_str = date.today().isoformat()
    weight_label = f"+{weight}" if weight != 1.0 else "+1"

    if result == "success":
        new_alpha = parsed["alpha"] + weight
        updates: Dict[str, Any] = {
            "alpha": new_alpha,
            "confirmed": today_str,
        }
        update_decay_tag(file_path, line_number, updates)
        action = f"alpha {weight_label} → {new_alpha}, confirmed → {today_str}"
        return {
            "type": parsed["type"],
            "confirmed": today_str,
            "C0": parsed["C0"],
            "alpha": new_alpha,
            "beta": parsed["beta"],
            "action": action,
        }
    else:
        new_beta = parsed["beta"] + weight
        update_decay_tag(file_path, line_number, {"beta": new_beta})
        action = f"beta {weight_label} → {new_beta}"
        return {
            "type": parsed["type"],
            "confirmed": parsed["confirmed"],
            "C0": parsed["C0"],
            "alpha": parsed["alpha"],
            "beta": new_beta,
            "action": action,
        }


def reset_entry(
    file_path: str, line_number: int
) -> Dict[str, Any]:
    """Reset a decay tag to fresh state after revalidation.

    Sets confirmed to today, C0 to 1.0, and alpha/beta to 0.
    The type field is preserved.

    Args:
        file_path:   Path to the markdown file.
        line_number: 1-based line number of the decay tag.

    Returns:
        Dict with keys: type, confirmed, alpha, beta, action.

    Raises:
        FileNotFoundError: If file_path does not exist.
        ValueError: If line_number is out of range or the target line
                    has no decay tag.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    total_lines = len(lines)
    if line_number < 1 or line_number > total_lines:
        raise ValueError(
            f"Line number {line_number} out of range "
            f"(file has {total_lines} lines)"
        )

    parsed = parse_decay_tag(lines[line_number - 1])
    if parsed is None:
        raise ValueError(f"No decay tag found at line {line_number}")

    # Remember old values for the action description
    old_confirmed = parsed["confirmed"]
    old_alpha = parsed["alpha"]
    old_beta = parsed["beta"]

    today_str = date.today().isoformat()

    update_decay_tag(file_path, line_number, {
        "confirmed": today_str,
        "C0": 1.0,
        "alpha": 0,
        "beta": 0,
    })

    return {
        "type": parsed["type"],
        "confirmed": today_str,
        "C0": 1.0,
        "alpha": 0,
        "beta": 0,
        "action": (
            f"reset (was: confirmed={old_confirmed} "
            f"\u03b1={old_alpha} \u03b2={old_beta})"
        ),
    }


def append_entry(
    file_path: str,
    knowledge_type: str,
    content: str,
    entities: Optional[List[str]] = None,
) -> int:
    """Append a new knowledge entry (decay tag + content line) to a file.

    If the target file does not exist, it is created with a minimal
    markdown template (title + description comment).

    Args:
        file_path:      Absolute or relative path to the target markdown file.
        knowledge_type: Must be one of VALID_TYPES.
        content:        Single-line knowledge text (written as a markdown bullet).
        entities:       Optional list of entity names (table/SP/concept).

    Returns:
        1-based line number of the newly written decay tag.

    Raises:
        ValueError: If knowledge_type is not in VALID_TYPES.
    """
    if knowledge_type not in VALID_TYPES:
        raise ValueError(
            f"Invalid knowledge_type '{knowledge_type}'. "
            f"Must be one of: {sorted(VALID_TYPES)}"
        )

    path = Path(file_path)

    if not path.exists():
        # Create file with minimal markdown template
        stem = path.stem  # filename without .md
        title = stem.replace("_", " ").capitalize()
        template = f"# {title}\n\n> 通过五道门治理协议管理。\n"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(template, encoding="utf-8")

    # Read existing content
    existing = path.read_text(encoding="utf-8")

    # Build the text to append
    today_str = date.today().isoformat()
    tag_line = f"<!-- decay: type={knowledge_type} confirmed={today_str} C0=1.0 -->"
    content_line = f"- {content}"

    # If file doesn't end with newline, add one first (so we get blank-line separation)
    parts = []
    if existing and not existing.endswith("\n"):
        parts.append("\n")
    parts.append("\n")           # blank line separator
    parts.append(tag_line + "\n")
    if entities:
        entities_line = f"<!-- entities: {', '.join(entities)} -->"
        parts.append(entities_line + "\n")
    parts.append(content_line + "\n")

    append_text = "".join(parts)

    with open(path, "a", encoding="utf-8") as fh:
        fh.write(append_text)

    # Determine the 1-based line number of the tag line.
    # Layout: [decay tag] [entities tag if present] [content line]
    full = path.read_text(encoding="utf-8")
    total_lines = len(full.splitlines())
    # Content is always last; entities (if present) is second-to-last; decay tag before that
    lines_after_tag = 2 if entities else 1
    tag_lineno = total_lines - lines_after_tag

    return tag_lineno
