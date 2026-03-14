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

1. **Always read `references/_index.md` first** — lightweight routing table
2. Identify task-relevant entities (table names, SP names, business concepts)
3. Run: `python $S/decay_engine.py search --path $S/../references/ --entities "<names>" --level TRUST`
4. Load only matched files; for VERIFY entries, flag for opportunistic verification
5. REVALIDATE entries: verify with tools BEFORE using
6. If no entities identified or search returns empty → fall back to topic-based file selection from `_index.md`

### Knowledge Governance Protocol

Before modifying any knowledge file, pass **all five gates in order**:

```
Gate 1 — VALUE: Reusable across conversations?
  One-time result → DO NOT add (this is the MOST COMMON outcome)
  Recurring pattern / stable fact → proceed

Gate 2 — ALIGNMENT: Contradicts existing knowledge?
  1. Extract entity names from new knowledge (table/SP/concept names)
  2. Run: python $S/decay_engine.py search --path $S/../references/ --entities "<names>"
  3. For each match: compare new knowledge with the existing entry
     - Full contradiction → CORRECT existing entry (feedback --result failure on old)
     - Partial overlap → MERGE or keep both (note differences)
     - No contradiction → proceed
  4. If no search results → proceed to Gate 3

Gate 3 — REDUNDANCY: Already captured (possibly different wording)?
  1. Use search results from Gate 2 (same entity matches)
  2. For each match: is the new knowledge semantically equivalent?
     - Same fact, different wording → SKIP (do not add)
     - Same entity, different fact → proceed (not redundant)
  3. If no matches or no redundancy → proceed to Gate 4

Gate 4 — FRESHNESS (write): Assign decay metadata + entities
  → Classify type: schema | business_rule | tool_experience |
                    query_pattern | data_range | data_snapshot
  → Extract entity names from knowledge content
  → Write both tags:
    <!-- decay: type=<type> confirmed=<YYYY-MM-DD> C0=1.0 -->
    <!-- entities: <entity1>, <entity2> -->
  → High-decay types (data_range/data_snapshot): prefer rejection

Gate 4 — FRESHNESS (read): On-demand confidence scan
  → Run: python $S/decay_engine.py scan --file <topic_file>
  → TRUST: use directly, no mention of confidence
  → VERIFY: use but flag for opportunistic verification
  → REVALIDATE: verify with tools BEFORE using

Gate 4 — FRESHNESS (feedback): After operations using knowledge
  Hard signals (weight=1.0, default):
    → SQL execution success/failure involving known columns/tables
    → Structure query match/mismatch with known schema
    → Numeric comparison within/outside ±5% of recorded value
    Command: python $S/decay_engine.py feedback --file <f> --line <n> --result success|failure

  Soft signals (weight=0.3):
    → Gate 2 ALIGNMENT correction (β+0.3 on corrected entry)
    → Empty result on enum/status value query
    → User explicit confirmation of result correctness
    Command: python $S/decay_engine.py feedback --file <f> --line <n> --result success|failure --weight 0.3

  No clear outcome → do NOT record feedback

  After REVALIDATE passes:
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

### Human Entry Points

```
Human injection: When user explicitly shares domain knowledge
  (signals: "记住", "注意这个", "这个要记下来", "remember this")
  → Treat as knowledge candidate
  → Run Gate 1-3 (VALUE / ALIGNMENT / REDUNDANCY) as normal
  → If all pass:
    python $S/decay_engine.py inject --type <t> --content "<c>" --target <f> --entities "<e1>,<e2>"
  → If any gate fails: explain why to user, do not write

Human correction: When user indicates existing knowledge is wrong
  (signals: "这个变了", "这条不对", "这个规则已经废弃了")
  → Identify the knowledge entry in references/
  → Run: python $S/decay_engine.py invalidate --file <f> --line <n>
  → Immediately treat as REVALIDATE: verify with tools before further use
```

### Scaling Rules

- Single topic file exceeds ~80 lines → split into sub-topics
- Total topic files exceed 8 → review for consolidation
- `_index.md` must stay under 40 lines (pure routing, no detail)
- **Active check**: After each knowledge write, verify the target file's line count; if approaching 80, plan the split before next write

## Commands

```bash
S=".claude/skills/db-investigator/scripts"

# Database tools
python $S/db_query.py --sql "<SELECT>" --database <db> [--limit N]
python $S/fetch_structure.py --tables <t>[,t2] [--sample N] [--database <db>]
python $S/fetch_structure.py --procedures <sp>[,sp2] [--database <db>]
python $S/fetch_index.py [--database <db>]

# Knowledge lifecycle
python $S/decay_engine.py scan --file <topic_file>
python $S/decay_engine.py scan --path $S/../references/
python $S/decay_engine.py search --path $S/../references/ --entities "<names>" [--level TRUST|VERIFY|REVALIDATE]
python $S/decay_engine.py search --path $S/../references/ [--min-confidence 0.8]
python $S/decay_engine.py feedback --file <f> --line <n> --result success|failure [--weight 0.3]
python $S/decay_engine.py reset --file <f> --line <n>
python $S/decay_engine.py inject --type <t> --content "<c>" --target <f> [--entities "<e1>,<e2>"]
python $S/decay_engine.py invalidate --file <f> --line <n>
```

## Constraints

- **Read-only enforced**: `db_query.py` whitelist-validates SQL (SELECT/SHOW/DESCRIBE/EXPLAIN only)
- **Write operations**: Generate SQL and present to user for manual execution
- **No credentials in output**: never print db_config.ini content
- **Timeout**: connect_timeout=10s, read_timeout=30s; retry once or narrow scope
- **Cached schemas**: `db_schemas/` has previously fetched structures — check before re-fetching
