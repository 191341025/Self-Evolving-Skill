"""Tests for core.parser module."""

import pytest

from datetime import date

from core.parser import (
    parse_decay_tag,
    parse_decay_tags,
    scan_directory,
    update_decay_tag,
    increment_feedback,
    reset_entry,
    append_entry,
)


# ---------- parse_decay_tag ----------

class TestParseDecayTag:
    def test_valid_minimal(self):
        """A valid tag with only required fields."""
        line = "<!-- decay: type=schema confirmed=2026-01-15 C0=1.0 -->"
        result = parse_decay_tag(line)
        assert result is not None
        assert result["type"] == "schema"
        assert result["confirmed"] == "2026-01-15"
        assert result["C0"] == 1.0
        assert result["alpha"] == 0
        assert result["beta"] == 0

    def test_valid_with_alpha_beta(self):
        """A tag with optional alpha/beta."""
        line = "<!-- decay: type=business_rule confirmed=2025-06-01 C0=1.0 alpha=3 beta=1 -->"
        result = parse_decay_tag(line)
        assert result is not None
        assert result["alpha"] == 3
        assert result["beta"] == 1
        assert result["type"] == "business_rule"

    def test_no_tag_returns_none(self):
        """A line without any decay tag returns None."""
        assert parse_decay_tag("# Just a heading") is None
        assert parse_decay_tag("") is None
        assert parse_decay_tag("<!-- just a comment -->") is None

    def test_malformed_missing_type_returns_none(self):
        """Tag missing the 'type' field should return None."""
        line = "<!-- decay: confirmed=2026-01-01 C0=1.0 -->"
        assert parse_decay_tag(line) is None

    def test_malformed_missing_confirmed_returns_none(self):
        """Tag missing the 'confirmed' field should return None."""
        line = "<!-- decay: type=schema C0=1.0 -->"
        assert parse_decay_tag(line) is None

    def test_malformed_missing_c0_returns_none(self):
        """Tag missing the 'C0' field should return None."""
        line = "<!-- decay: type=schema confirmed=2026-01-01 -->"
        assert parse_decay_tag(line) is None

    def test_invalid_type_returns_none(self):
        """An unrecognized type value should return None."""
        line = "<!-- decay: type=unknown confirmed=2026-01-01 C0=1.0 -->"
        assert parse_decay_tag(line) is None

    def test_invalid_date_format_returns_none(self):
        """A bad date format should return None."""
        line = "<!-- decay: type=schema confirmed=01-15-2026 C0=1.0 -->"
        assert parse_decay_tag(line) is None

    def test_all_valid_types(self):
        """All 6 valid types should be accepted."""
        for t in ("schema", "business_rule", "tool_experience",
                  "query_pattern", "data_range", "data_snapshot"):
            line = f"<!-- decay: type={t} confirmed=2026-01-01 C0=1.0 -->"
            result = parse_decay_tag(line)
            assert result is not None, f"type={t} should be valid"
            assert result["type"] == t

    def test_negative_alpha_returns_none(self):
        """Negative alpha should be rejected."""
        line = "<!-- decay: type=schema confirmed=2026-01-01 C0=1.0 alpha=-1 -->"
        assert parse_decay_tag(line) is None


# ---------- parse_decay_tags ----------

class TestParseDecayTags:
    def test_correct_count(self, sample_md_file):
        """The sample file has 2 valid tags (schema + business_rule)."""
        results = parse_decay_tags(str(sample_md_file))
        assert len(results) == 2

    def test_line_numbers_are_one_based(self, sample_md_file):
        """Line numbers must be 1-based."""
        results = parse_decay_tags(str(sample_md_file))
        for r in results:
            assert r["line"] >= 1

    def test_context_from_heading(self, sample_md_file):
        """Context should come from the nearest preceding heading."""
        results = parse_decay_tags(str(sample_md_file))
        contexts = [r["context"] for r in results]
        assert "users table" in contexts
        assert "order status rules" in contexts

    def test_file_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            parse_decay_tags(str(tmp_path / "nonexistent.md"))


# ---------- scan_directory ----------

class TestScanDirectory:
    def test_skips_index_file(self, sample_dir):
        """_index.md should be excluded from results."""
        results = scan_directory(str(sample_dir))
        files = {r.get("file", "") for r in results}
        for f in files:
            assert "_index.md" not in f

    def test_includes_subdirectory(self, sample_dir):
        """Files in subdirectories should be included."""
        results = scan_directory(str(sample_dir))
        files = [r.get("file", "") for r in results]
        # sub/extra.md should be found
        assert any("sub/" in f or "sub\\" in f for f in files), \
            f"Expected a file under sub/, got files: {files}"

    def test_file_paths_relative(self, sample_dir):
        """File paths should be relative to the scanned directory."""
        results = scan_directory(str(sample_dir))
        for r in results:
            assert "file" in r
            # Should not contain the tmp_path prefix
            assert not r["file"].startswith("/tmp")

    def test_total_tag_count(self, sample_dir):
        """test_knowledge.md has 2 tags + sub/extra.md has 1 = 3 total."""
        results = scan_directory(str(sample_dir))
        assert len(results) == 3

    def test_directory_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            scan_directory(str(tmp_path / "nonexistent_dir"))


# ---------- update_decay_tag ----------

def _make_tag_file(tmp_path, tag_line, *, indent="", extra_lines=None):
    """Helper: create a markdown file with a decay tag at a known line."""
    lines = ["# Section heading\n", "Some description text.\n"]
    if extra_lines:
        lines.extend(extra_lines)
    lines.append(f"{indent}{tag_line}\n")
    tag_lineno = len(lines)  # 1-based
    lines.append("Trailing content.\n")
    f = tmp_path / "test_write.md"
    f.write_text("".join(lines), encoding="utf-8")
    return f, tag_lineno


class TestUpdateDecayTag:
    """Tests for update_decay_tag."""

    def test_update_alpha(self, tmp_path):
        """Update alpha field only, other fields unchanged."""
        tag = "<!-- decay: type=schema confirmed=2026-01-15 C0=1.0 alpha=0 beta=0 -->"
        f, lineno = _make_tag_file(tmp_path, tag)
        assert update_decay_tag(str(f), lineno, {"alpha": 5}) is True
        content = f.read_text(encoding="utf-8")
        assert "alpha=5" in content
        # Other fields intact
        assert "type=schema" in content
        assert "confirmed=2026-01-15" in content
        assert "beta=0" in content

    def test_update_multiple_fields(self, tmp_path):
        """Update confirmed and alpha simultaneously."""
        tag = "<!-- decay: type=business_rule confirmed=2025-06-01 C0=1.0 alpha=1 beta=2 -->"
        f, lineno = _make_tag_file(tmp_path, tag)
        update_decay_tag(str(f), lineno, {"confirmed": "2026-03-14", "alpha": 10})
        content = f.read_text(encoding="utf-8")
        assert "confirmed=2026-03-14" in content
        assert "alpha=10" in content
        # Unchanged fields preserved
        assert "type=business_rule" in content
        assert "beta=2" in content

    def test_preserves_other_lines(self, tmp_path):
        """Other lines in the file remain untouched."""
        tag = "<!-- decay: type=schema confirmed=2026-01-15 C0=1.0 alpha=0 beta=0 -->"
        f, lineno = _make_tag_file(tmp_path, tag)
        update_decay_tag(str(f), lineno, {"alpha": 9})
        content = f.read_text(encoding="utf-8")
        assert "# Section heading" in content
        assert "Some description text." in content
        assert "Trailing content." in content

    def test_preserves_leading_whitespace(self, tmp_path):
        """Indented tag lines keep their indentation."""
        tag = "<!-- decay: type=schema confirmed=2026-01-15 C0=1.0 alpha=0 beta=0 -->"
        f, lineno = _make_tag_file(tmp_path, tag, indent="    ")
        update_decay_tag(str(f), lineno, {"alpha": 1})
        lines = f.read_text(encoding="utf-8").splitlines()
        tag_line = lines[lineno - 1]
        assert tag_line.startswith("    "), f"Expected 4-space indent, got: {tag_line!r}"

    def test_file_not_found(self):
        """Non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            update_decay_tag("/tmp/nonexistent_xyz.md", 1, {"alpha": 1})

    def test_line_out_of_range(self, tmp_path):
        """Line number beyond file length raises ValueError."""
        tag = "<!-- decay: type=schema confirmed=2026-01-15 C0=1.0 -->"
        f, _ = _make_tag_file(tmp_path, tag)
        with pytest.raises(ValueError, match="out of range"):
            update_decay_tag(str(f), 9999, {"alpha": 1})

    def test_no_tag_at_line(self, tmp_path):
        """Line without decay tag raises ValueError."""
        tag = "<!-- decay: type=schema confirmed=2026-01-15 C0=1.0 -->"
        f, _lineno = _make_tag_file(tmp_path, tag)
        # Line 1 is "# Section heading", not a tag
        with pytest.raises(ValueError, match="No decay tag"):
            update_decay_tag(str(f), 1, {"alpha": 1})

    def test_empty_updates(self, tmp_path):
        """Empty updates dict raises ValueError."""
        tag = "<!-- decay: type=schema confirmed=2026-01-15 C0=1.0 -->"
        f, lineno = _make_tag_file(tmp_path, tag)
        with pytest.raises(ValueError, match="No updates"):
            update_decay_tag(str(f), lineno, {})


# ---------- increment_feedback ----------

class TestIncrementFeedback:
    """Tests for increment_feedback."""

    def test_success_increments_alpha(self, tmp_path):
        """result='success' increments alpha by 1."""
        tag = "<!-- decay: type=schema confirmed=2026-01-15 C0=1.0 alpha=0 beta=0 -->"
        f, lineno = _make_tag_file(tmp_path, tag)
        result = increment_feedback(str(f), lineno, "success")
        assert result["alpha"] == 1
        assert result["beta"] == 0
        # Verify file was actually written
        content = f.read_text(encoding="utf-8")
        assert "alpha=1" in content

    def test_failure_increments_beta(self, tmp_path):
        """result='failure' increments beta by 1."""
        tag = "<!-- decay: type=schema confirmed=2026-01-15 C0=1.0 alpha=0 beta=0 -->"
        f, lineno = _make_tag_file(tmp_path, tag)
        result = increment_feedback(str(f), lineno, "failure")
        assert result["beta"] == 1
        assert result["alpha"] == 0
        content = f.read_text(encoding="utf-8")
        assert "beta=1" in content

    def test_idempotent_multiple_calls(self, tmp_path):
        """Two successive success calls: alpha goes 0 -> 1 -> 2."""
        tag = "<!-- decay: type=schema confirmed=2026-01-15 C0=1.0 alpha=0 beta=0 -->"
        f, lineno = _make_tag_file(tmp_path, tag)
        r1 = increment_feedback(str(f), lineno, "success")
        assert r1["alpha"] == 1
        r2 = increment_feedback(str(f), lineno, "success")
        assert r2["alpha"] == 2
        content = f.read_text(encoding="utf-8")
        assert "alpha=2" in content

    def test_return_value_format(self, tmp_path):
        """Return dict has type, confirmed, alpha, beta, action."""
        tag = "<!-- decay: type=business_rule confirmed=2026-01-15 C0=1.0 alpha=3 beta=1 -->"
        f, lineno = _make_tag_file(tmp_path, tag)
        result = increment_feedback(str(f), lineno, "success")
        assert "type" in result
        assert "confirmed" in result
        assert "alpha" in result
        assert "beta" in result
        assert "action" in result
        assert result["type"] == "business_rule"
        assert result["confirmed"] == "2026-01-15"

    def test_invalid_result_raises(self, tmp_path):
        """result='invalid' raises ValueError."""
        tag = "<!-- decay: type=schema confirmed=2026-01-15 C0=1.0 -->"
        f, lineno = _make_tag_file(tmp_path, tag)
        with pytest.raises(ValueError, match="must be 'success' or 'failure'"):
            increment_feedback(str(f), lineno, "invalid")


# ---------- reset_entry ----------

class TestResetEntry:
    """Tests for reset_entry."""

    def test_resets_to_fresh(self, tmp_path):
        """confirmed=today, alpha=0, beta=0, C0=1.0, type preserved."""
        tag = "<!-- decay: type=schema confirmed=2025-01-01 C0=0.5 alpha=5 beta=3 -->"
        f, lineno = _make_tag_file(tmp_path, tag)
        result = reset_entry(str(f), lineno)
        assert result["confirmed"] == date.today().isoformat()
        assert result["alpha"] == 0
        assert result["beta"] == 0
        # Verify the file
        content = f.read_text(encoding="utf-8")
        assert f"confirmed={date.today().isoformat()}" in content
        assert "C0=1.0" in content
        assert "alpha=0" in content
        assert "beta=0" in content

    def test_return_value_has_old_info(self, tmp_path):
        """Return dict's action field contains 'was:' with old values."""
        tag = "<!-- decay: type=schema confirmed=2025-06-01 C0=1.0 alpha=3 beta=2 -->"
        f, lineno = _make_tag_file(tmp_path, tag)
        result = reset_entry(str(f), lineno)
        assert "was:" in result["action"]
        assert "confirmed=2025-06-01" in result["action"]

    def test_type_preserved(self, tmp_path):
        """The type field is not changed by reset."""
        tag = "<!-- decay: type=data_snapshot confirmed=2025-01-01 C0=0.5 alpha=5 beta=3 -->"
        f, lineno = _make_tag_file(tmp_path, tag)
        result = reset_entry(str(f), lineno)
        assert result["type"] == "data_snapshot"
        content = f.read_text(encoding="utf-8")
        assert "type=data_snapshot" in content


# ---------- append_entry ----------

class TestAppendEntry:
    """Tests for append_entry."""

    def test_append_entry_basic(self, sample_md_file):
        """Append to an existing file: correct tag, content, line number, parseable."""
        lineno = append_entry(
            str(sample_md_file), "schema", "New column added to users table"
        )
        content = sample_md_file.read_text(encoding="utf-8")
        today = date.today().isoformat()

        # Decay tag and content line present
        assert f"<!-- decay: type=schema confirmed={today} C0=1.0 -->" in content
        assert "- New column added to users table" in content

        # Line number is correct
        lines = content.splitlines()
        assert lines[lineno - 1].strip().startswith("<!-- decay:")

        # Tag is parseable
        parsed = parse_decay_tag(lines[lineno - 1])
        assert parsed is not None
        assert parsed["type"] == "schema"
        assert parsed["confirmed"] == today
        assert parsed["C0"] == 1.0

    def test_append_entry_creates_file(self, tmp_path):
        """Non-existent file is created with template, entry appended."""
        target = tmp_path / "business_rules.md"
        assert not target.exists()

        lineno = append_entry(str(target), "business_rule", "Status 1 means active")

        assert target.exists()
        content = target.read_text(encoding="utf-8")

        # Template header present
        assert content.startswith("# Business rules")
        assert "通过五道门治理协议管理" in content

        # Entry appended correctly
        today = date.today().isoformat()
        assert f"<!-- decay: type=business_rule confirmed={today} C0=1.0 -->" in content
        assert "- Status 1 means active" in content

        # Line number valid
        lines = content.splitlines()
        assert lines[lineno - 1].strip().startswith("<!-- decay:")

    def test_append_entry_invalid_type(self, tmp_path):
        """Invalid knowledge_type raises ValueError."""
        target = tmp_path / "test.md"
        target.write_text("# Test\n", encoding="utf-8")
        with pytest.raises(ValueError):
            append_entry(str(target), "invalid_type", "some content")

    def test_append_entry_multiple(self, tmp_path):
        """Two successive appends: both present, line numbers increment, blank-line separation."""
        target = tmp_path / "multi.md"
        target.write_text("# Multi\n\nSome intro text.\n", encoding="utf-8")

        lineno1 = append_entry(str(target), "schema", "First entry")
        lineno2 = append_entry(str(target), "business_rule", "Second entry")

        assert lineno2 > lineno1

        content = target.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Both tags present and parseable
        parsed1 = parse_decay_tag(lines[lineno1 - 1])
        parsed2 = parse_decay_tag(lines[lineno2 - 1])
        assert parsed1 is not None
        assert parsed2 is not None
        assert parsed1["type"] == "schema"
        assert parsed2["type"] == "business_rule"

        # Content lines follow their tags
        assert lines[lineno1].strip() == "- First entry"
        assert lines[lineno2].strip() == "- Second entry"

        # Blank line separation: line before tag should be empty
        assert lines[lineno1 - 2].strip() == ""
        assert lines[lineno2 - 2].strip() == ""

    def test_append_entry_no_trailing_newline(self, tmp_path):
        """File without trailing newline still gets correct formatting."""
        target = tmp_path / "no_newline.md"
        # Write without trailing newline
        target.write_text("# No trailing newline\n\nSome content here.", encoding="utf-8")

        lineno = append_entry(str(target), "query_pattern", "SELECT * FROM users")

        content = target.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Tag is at the correct line and parseable
        parsed = parse_decay_tag(lines[lineno - 1])
        assert parsed is not None
        assert parsed["type"] == "query_pattern"

        # Content line follows tag
        assert lines[lineno].strip() == "- SELECT * FROM users"

        # Blank line separates old content from new entry
        assert lines[lineno - 2].strip() == ""
