---
name: db-investigator
description: |
  Self-evolving database investigation skill for MySQL databases.
  TRIGGER when conversation involves:
  - Querying or verifying data (counts, distributions, status checks, field values)
  - Understanding table schemas, column names, or indexes
  - Reading stored procedure / function definitions
  - Comparing data between tables or databases
  - Discussing SP logic and needing to confirm actual deployed code
  - Any question that could be answered by looking at the database
  BEHAVIOR:
  - DO NOT ask the user for database info you can look up yourself — query first, report findings
  - When a data question arises mid-conversation, use this skill immediately without announcing "let me write a script"
  - All tools are read-only; for write operations, generate SQL for user to review
allowed-tools: Bash(python *db_query*), Bash(python *fetch_index*), Bash(python *fetch_structure*), Bash(python *decay_engine*)
---

## Tool Selection

| Need | Tool |
|------|------|
| Data investigation (counts, WHERE, GROUP BY, JOIN) | `db_query.py` |
| Table structure (DDL, columns, indexes, sample rows) | `fetch_structure.py --tables` |
| SP/Function source code | `fetch_structure.py --procedures` |
| Database overview (list all objects) | `fetch_index.py` |

**Decision flow**: Data question → `db_query.py`. Structure → `fetch_structure.py`. Don't know what exists → `fetch_index.py`.

**Tool experience**: When a query pattern or parameter combination proves especially effective (or a pitfall is discovered), note it in the relevant references/ file alongside the query template or investigation flow.

## Domain Knowledge System

### Selective Loading Protocol

Domain knowledge lives in `references/` as a topic-based structure:

1. **Always read `references/_index.md` first** — lightweight routing table listing all topics with one-line summaries
2. Based on current conversation topic, read **only** the relevant topic file(s)
3. Never bulk-read all topic files — context is expensive

### Knowledge Governance Protocol

Before modifying any knowledge file, pass **all five gates in order**:

```
Gate 1 — VALUE: Reusable across conversations?
  One-time result → DO NOT add (this is the MOST COMMON outcome)
  Recurring pattern / stable fact → proceed

Gate 2 — ALIGNMENT: Contradicts existing knowledge?
  Yes → CORRECT existing entry, do not add duplicate
  No → proceed

Gate 3 — REDUNDANCY: Already captured (possibly different wording)?
  Yes → MERGE into existing or skip
  No → proceed

Gate 4 — FRESHNESS (write): Assign decay metadata
  → Classify type: schema | business_rule | tool_experience |
                    query_pattern | data_range | data_snapshot
  → Write: <!-- decay: type=<type> confirmed=<YYYY-MM-DD> C0=1.0 -->
  → High-decay types (data_range/data_snapshot): prefer rejection

Gate 4 — FRESHNESS (read): On-demand confidence scan
  → Run: python $S/decay_engine.py scan --file <topic_file>
  → TRUST: use directly, no mention of confidence
  → VERIFY: use but flag for opportunistic verification
  → REVALIDATE: verify with tools BEFORE using

Gate 4 — FRESHNESS (feedback): After operations using knowledge
  → Success (SQL ran, structure matched, result correct):
    python $S/decay_engine.py feedback --file <f> --line <n> --result success
  → Failure (SQL error involving known column/table, Gate 2 correction):
    python $S/decay_engine.py feedback --file <f> --line <n> --result failure
  → No clear outcome: do NOT record feedback
  → After REVALIDATE passes:
    python $S/decay_engine.py reset --file <f> --line <n>

Decay boundary rules:
  → Never auto-delete entries even if C→0; deletion requires user confirmation
  → Confidence resets only via reset command after tool-verified revalidation
  → If REVALIDATE finds contradiction → Gate 2 (ALIGNMENT) takes priority

Gate 5 — PLACEMENT: Which topic file? Which memory tier?
  Structure knowledge → schema_map.md
  Business rules → business_rules.md
  Reusable SQL → query_patterns.md
  Multi-step investigation procedure → investigation_flows.md
  New topic needed → only if 3+ related facts justify a new file
  Update _index.md if new file created OR existing file's scope changed significantly
```

**Default outcome is NO CHANGE.** Most interactions do not produce knowledge worth persisting. The gates' primary job is to reject, not to accept.

### Scaling Rules

- Single topic file exceeds ~80 lines → split into sub-topics
- Total topic files exceed 8 → review for consolidation
- `_index.md` must stay under 40 lines (pure routing, no detail)
- **Active check**: After each knowledge write, verify the target file's line count; if approaching 80, plan the split before next write

## Commands

```bash
S=".claude/skills/db-investigator/scripts"

python $S/db_query.py --sql "<SELECT>" --database <db> [--limit N]
python $S/fetch_structure.py --tables <t>[,t2] [--sample N] [--database <db>]
python $S/fetch_structure.py --procedures <sp>[,sp2] [--database <db>]
python $S/fetch_index.py [--database <db>]
python $S/decay_engine.py scan --file <topic_file>
python $S/decay_engine.py scan --path $S/../references/
python $S/decay_engine.py feedback --file <f> --line <n> --result success|failure
python $S/decay_engine.py reset --file <f> --line <n>
```

## Constraints

- **Read-only enforced**: `db_query.py` whitelist-validates SQL (SELECT/SHOW/DESCRIBE/EXPLAIN only)
- **Write operations**: Generate SQL and present to user for manual execution
- **No credentials in output**: never print db_config.ini content
- **Timeout**: connect_timeout=10s, read_timeout=30s; retry once or narrow scope
- **Cached schemas**: `db_schemas/` has previously fetched structures — check before re-fetching
