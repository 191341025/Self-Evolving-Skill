import pytest
from datetime import date, timedelta


@pytest.fixture
def today_str():
    return date.today().isoformat()


@pytest.fixture
def days_ago():
    """Return a function: given N days, return YYYY-MM-DD string for N days ago."""
    def _days_ago(n):
        return (date.today() - timedelta(days=n)).isoformat()
    return _days_ago


@pytest.fixture
def sample_md_file(tmp_path):
    """Create a test markdown file with several decay tags."""
    content = """# Schema Knowledge

### users table
The users table has columns id, name, email.
<!-- decay: type=schema confirmed={today} C0=1.0 -->
<!-- entities: t_user, t_email -->

### order status rules
Orders use status 1=active, 2=completed, 3=cancelled.
<!-- decay: type=business_rule confirmed={old_date} C0=1.0 alpha=1 beta=2 -->

### No tag section
This section has no decay tag.

### Malformed tag
<!-- decay: confirmed=2026-01-01 C0=1.0 -->
""".format(today=date.today().isoformat(),
           old_date=(date.today() - timedelta(days=200)).isoformat())

    f = tmp_path / "test_knowledge.md"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def sample_dir(tmp_path, sample_md_file):
    """Create a test directory with multiple md files."""
    # _index.md should be skipped
    (tmp_path / "_index.md").write_text(
        "# Index\nRouting file\n<!-- decay: type=schema confirmed=2026-01-01 C0=1.0 -->\n",
        encoding="utf-8",
    )
    # File in a subdirectory
    sub = tmp_path / "sub"
    sub.mkdir()
    sub_file = sub / "extra.md"
    sub_file.write_text(
        "# Extra\n<!-- decay: type=query_pattern confirmed={} C0=1.0 -->\n".format(
            (date.today() - timedelta(days=30)).isoformat()
        ),
        encoding="utf-8",
    )
    return tmp_path
