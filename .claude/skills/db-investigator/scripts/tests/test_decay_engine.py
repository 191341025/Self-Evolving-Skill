"""End-to-end tests for the decay_engine CLI."""

import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)

# Allow importing decay_engine from scripts dir
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


def run_engine(*args, cwd=None):
    """Helper to invoke decay_engine.py via subprocess."""
    cmd = [sys.executable, "decay_engine.py"] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd or SCRIPTS_DIR,
    )


class TestDecayEngineCLI:
    def test_scan_file_all_trust(self, tmp_path):
        """File where all entries are confirmed today -> exit code 0, all TRUST."""
        content = (
            "# Fresh\n"
            f"<!-- decay: type=schema confirmed={date.today().isoformat()} C0=1.0 -->\n"
        )
        f = tmp_path / "fresh.md"
        f.write_text(content, encoding="utf-8")

        result = run_engine("scan", "--file", str(f))
        assert result.returncode == 0
        assert "[TRUST" in result.stdout

    def test_scan_file_has_revalidate(self, tmp_path):
        """File with a very old entry -> exit code 2, has REVALIDATE."""
        old_date = (date.today() - timedelta(days=1000)).isoformat()
        content = (
            "# Ancient\n"
            f"<!-- decay: type=data_snapshot confirmed={old_date} C0=1.0 -->\n"
        )
        f = tmp_path / "old.md"
        f.write_text(content, encoding="utf-8")

        result = run_engine("scan", "--file", str(f))
        assert result.returncode == 2
        assert "[REVALIDATE" in result.stdout

    def test_scan_file_has_verify(self, tmp_path):
        """Craft a file where confidence falls into the VERIFY band."""
        # data_snapshot lambda=0.050 -> half-life ~14 days
        # At 5 days: C = e^(-0.05*5) = e^(-0.25) ~ 0.778 -> VERIFY
        d = (date.today() - timedelta(days=5)).isoformat()
        content = (
            "# Mid\n"
            f"<!-- decay: type=data_snapshot confirmed={d} C0=1.0 -->\n"
        )
        f = tmp_path / "mid.md"
        f.write_text(content, encoding="utf-8")

        result = run_engine("scan", "--file", str(f))
        assert result.returncode == 1
        assert "[VERIFY" in result.stdout

    def test_scan_summary_line(self, tmp_path):
        """The output should contain a summary line with entry counts."""
        content = (
            "# Test\n"
            f"<!-- decay: type=schema confirmed={date.today().isoformat()} C0=1.0 -->\n"
        )
        f = tmp_path / "summary.md"
        f.write_text(content, encoding="utf-8")

        result = run_engine("scan", "--file", str(f))
        assert "---" in result.stdout
        assert "1 entries:" in result.stdout or "1 entries" in result.stdout
        assert "TRUST" in result.stdout

    def test_scan_path_directory(self, sample_dir):
        """Scan a directory with multiple files."""
        result = run_engine("scan", "--path", str(sample_dir))
        # Should contain entries from test_knowledge.md and sub/extra.md
        assert "entries:" in result.stdout
        # Exit code depends on ages but should not error out
        assert result.returncode in (0, 1, 2)

    def test_no_args_shows_error(self):
        """Running scan without --file or --path should print error."""
        result = run_engine("scan")
        assert result.returncode == 1

    def test_missing_file_reports_error(self, tmp_path):
        """Pointing --file at a nonexistent file should print an error."""
        result = run_engine("scan", "--file", str(tmp_path / "ghost.md"))
        assert result.returncode == 1
        assert "not found" in result.stderr or "not found" in result.stdout \
            or "Error" in result.stderr or "Error" in result.stdout


# ---------- feedback subcommand ----------

def _write_tag_file(tmp_path, *, alpha=0, beta=0,
                    confirmed="2026-01-15", tag_type="schema"):
    """Helper: create a markdown file with one decay tag at line 2."""
    content = (
        "# Heading\n"
        f"<!-- decay: type={tag_type} confirmed={confirmed} "
        f"C0=1.0 alpha={alpha} beta={beta} -->\n"
    )
    f = tmp_path / "fb_test.md"
    f.write_text(content, encoding="utf-8")
    return f


class TestFeedbackCLI:
    """Tests for feedback subcommand via subprocess."""

    def test_feedback_success(self, tmp_path):
        """feedback --result success outputs 'Updated' and exits 0."""
        f = _write_tag_file(tmp_path)
        result = run_engine(
            "feedback", "--file", str(f), "--line", "2", "--result", "success"
        )
        assert result.returncode == 0
        assert "Updated" in result.stdout

    def test_feedback_failure(self, tmp_path):
        """feedback --result failure outputs 'Updated' and exits 0."""
        f = _write_tag_file(tmp_path)
        result = run_engine(
            "feedback", "--file", str(f), "--line", "2", "--result", "failure"
        )
        assert result.returncode == 0
        assert "Updated" in result.stdout

    def test_feedback_modifies_file(self, tmp_path):
        """After feedback, the file's alpha/beta is actually changed."""
        f = _write_tag_file(tmp_path, alpha=0, beta=0)
        run_engine(
            "feedback", "--file", str(f), "--line", "2", "--result", "success"
        )
        content = f.read_text(encoding="utf-8")
        assert "alpha=1" in content
        assert "beta=0" in content

    def test_feedback_missing_file(self):
        """Non-existent file exits 1."""
        result = run_engine(
            "feedback", "--file", "/tmp/no_such_file_xyz.md",
            "--line", "1", "--result", "success"
        )
        assert result.returncode == 1

    def test_feedback_invalid_line(self, tmp_path):
        """Wrong line number exits 1."""
        f = _write_tag_file(tmp_path)
        result = run_engine(
            "feedback", "--file", str(f), "--line", "999", "--result", "success"
        )
        assert result.returncode == 1


# ---------- reset subcommand ----------

class TestResetCLI:
    """Tests for reset subcommand via subprocess."""

    def test_reset_success(self, tmp_path):
        """reset outputs 'Reset' and exits 0."""
        f = _write_tag_file(tmp_path, alpha=3, beta=2,
                            confirmed="2025-01-01")
        result = run_engine(
            "reset", "--file", str(f), "--line", "2"
        )
        assert result.returncode == 0
        assert "Reset" in result.stdout

    def test_reset_modifies_file(self, tmp_path):
        """After reset, alpha=0 beta=0 confirmed=today in file."""
        f = _write_tag_file(tmp_path, alpha=5, beta=3,
                            confirmed="2025-01-01")
        run_engine("reset", "--file", str(f), "--line", "2")
        content = f.read_text(encoding="utf-8")
        assert "alpha=0" in content
        assert "beta=0" in content
        assert f"confirmed={date.today().isoformat()}" in content

    def test_reset_missing_file(self):
        """Non-existent file exits 1."""
        result = run_engine(
            "reset", "--file", "/tmp/no_such_file_xyz.md", "--line", "1"
        )
        assert result.returncode == 1


# ---------- inject subcommand ----------

class TestInjectCommand:
    """Tests for inject subcommand."""

    def test_inject_basic(self, tmp_path, monkeypatch):
        """Basic injection: file created with correct decay tag and content."""
        import decay_engine

        monkeypatch.setattr(decay_engine, "REFERENCES_DIR", tmp_path)

        args = SimpleNamespace(
            command="inject",
            type="schema",
            content="users table has id, name, email columns",
            target="business_rules.md",
        )
        rc = decay_engine.run_inject(args)
        assert rc == 0

        target_file = tmp_path / "business_rules.md"
        assert target_file.exists()
        content = target_file.read_text(encoding="utf-8")
        assert f"confirmed={date.today().isoformat()}" in content
        assert "type=schema" in content
        assert "- users table has id, name, email columns" in content

    def test_inject_stdout_message(self, tmp_path, monkeypatch, capsys):
        """Stdout output contains [inject] and the target filename."""
        import decay_engine

        monkeypatch.setattr(decay_engine, "REFERENCES_DIR", tmp_path)

        args = SimpleNamespace(
            command="inject",
            type="business_rule",
            content="Order status 1=active",
            target="rules.md",
        )
        decay_engine.run_inject(args)
        captured = capsys.readouterr()
        assert "[inject]" in captured.out
        assert "rules.md" in captured.out

    def test_inject_invalid_type(self):
        """Invalid --type is rejected by argparse (exit code 2)."""
        result = run_engine(
            "inject", "--type", "bogus_type",
            "--content", "some text", "--target", "test.md"
        )
        assert result.returncode == 2

    def test_inject_chinese_content(self, tmp_path, monkeypatch):
        """Chinese content is written correctly."""
        import decay_engine

        monkeypatch.setattr(decay_engine, "REFERENCES_DIR", tmp_path)

        args = SimpleNamespace(
            command="inject",
            type="business_rule",
            content="订单状态 1=有效 2=完成 3=取消",
            target="chinese_rules.md",
        )
        rc = decay_engine.run_inject(args)
        assert rc == 0

        target_file = tmp_path / "chinese_rules.md"
        content = target_file.read_text(encoding="utf-8")
        assert "订单状态 1=有效 2=完成 3=取消" in content


# ---------- invalidate subcommand ----------

class TestInvalidateCommand:
    """Tests for invalidate subcommand."""

    def test_invalidate_basic(self, tmp_path):
        """Basic invalidate: tag becomes C0=0.1, alpha=0, beta=0."""
        f = _write_tag_file(
            tmp_path, alpha=3, beta=1,
            confirmed="2026-01-15", tag_type="schema",
        )
        result = run_engine(
            "invalidate", "--file", str(f), "--line", "2"
        )
        assert result.returncode == 0

        content = f.read_text(encoding="utf-8")
        assert "C0=0.1" in content
        assert "alpha=0" in content
        assert "beta=0" in content
        # confirmed and type should be preserved
        assert "confirmed=2026-01-15" in content
        assert "type=schema" in content

    def test_invalidate_stdout_message(self, tmp_path):
        """Stdout output contains [invalidate] and old values."""
        f = _write_tag_file(
            tmp_path, alpha=3, beta=1,
            confirmed="2026-01-15", tag_type="schema",
        )
        result = run_engine(
            "invalidate", "--file", str(f), "--line", "2"
        )
        assert result.returncode == 0
        assert "[invalidate]" in result.stdout
        # Check old values are reported
        assert "C0=1.0" in result.stdout
        assert "\u03b1=3" in result.stdout or "alpha=3" in result.stdout.lower()
        assert "\u03b2=1" in result.stdout or "beta=1" in result.stdout.lower()

    def test_invalidate_no_tag_at_line(self, tmp_path):
        """Target line without a tag -> exit code 1 + stderr error."""
        f = _write_tag_file(tmp_path)
        # Line 1 is "# Heading", not a decay tag
        result = run_engine(
            "invalidate", "--file", str(f), "--line", "1"
        )
        assert result.returncode == 1
        assert "Error" in result.stderr

    def test_invalidate_file_not_found(self, tmp_path):
        """Non-existent file -> exit code 1 + stderr error."""
        result = run_engine(
            "invalidate", "--file", str(tmp_path / "ghost.md"), "--line", "2"
        )
        assert result.returncode == 1
        assert "Error" in result.stderr

    def test_invalidate_then_scan_shows_revalidate(self, tmp_path):
        """After invalidate, C0=0.1 means effective C(t) < 0.5 -> REVALIDATE."""
        from core.models import confidence
        from core.parser import parse_decay_tags

        f = _write_tag_file(
            tmp_path, alpha=3, beta=1,
            confirmed=date.today().isoformat(), tag_type="schema",
        )
        # Invalidate the tag
        result = run_engine(
            "invalidate", "--file", str(f), "--line", "2"
        )
        assert result.returncode == 0

        # After invalidation: C0=0.1, alpha=0, beta=0, confirmed unchanged (today)
        # Verify the tag was updated in the file
        tags = parse_decay_tags(str(f))
        assert len(tags) == 1
        tag = tags[0]
        assert tag["C0"] == 0.1
        assert tag["alpha"] == 0
        assert tag["beta"] == 0

        # C(t) from models.confidence returns e^(-lambda*0) = 1.0 (t=0)
        # Effective confidence with C0 = C0 * confidence() = 0.1 * 1.0 = 0.1
        c_base = confidence(
            tag["type"], tag["confirmed"],
            alpha=tag["alpha"], beta=tag["beta"],
        )
        effective_c = tag["C0"] * c_base
        assert effective_c < 0.5, (
            f"Expected effective C < 0.5 (REVALIDATE), got {effective_c}"
        )
