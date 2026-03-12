# Baseline Snapshot: nan_platform Database (v2)

> Generated: 2026-03-12
> Purpose: Record the starting state (R0) of the v2 experiment — a re-run of 01-nan-platform with the upgraded Gate 4 confidence decay model. Unlike v1's clean "zero point," v2 begins with 3 tool_experience entries carried from v1.

## Database Overview

| Item | Value |
|------|-------|
| Database Name | nan_platform |
| DBMS | MySQL 8.0 |
| Business Domain | Smart building / worker dormitory management platform |
| Table Count | 29 |
| View Count | 12 |
| Stored Procedures | 0 |
| Estimated Total Rows | 95,517 |
| Data Size | 589.53 MB |

> Database is identical to v1. See [v1 baseline](../01-nan-platform/00-baseline.md) for full schema description, entity relationships, dictionary system, and data distributions.

## Skill Under Test

| Item | Value |
|------|-------|
| Skill | db-investigator |
| Key Upgrade | Gate 4 split into write mode (assign decay) and read mode (confidence-based response) |
| Decay Model | C(t) = e^(-lambda * t), 6 knowledge types with distinct lambda values |
| Response Levels | TRUST (C >= 0.8) / VERIFY (0.5 <= C < 0.8) / REVALIDATE (C < 0.5) |
| Scaling Rules | Active line count check after each write |
| Gate 5 Change | _index.md update trigger expanded |

### Confidence Decay Reference Table

| Knowledge Type | lambda | Half-life (days) | Example |
|----------------|--------|------------------|---------|
| schema | 0.003 | 231 | Table columns, primary keys |
| tool_experience | 0.005 | 139 | Tool quirks, workarounds |
| business_rule | 0.008 | 87 | Status field meanings, enum values |
| query_pattern | 0.015 | 46 | SQL templates, JOIN paths |
| data_range | 0.035 | 20 | Row counts, value ranges |
| data_snapshot | 0.050 | 14 | Specific query results, distributions |

## Starting State (R0)

### Total Line Count

| File | Lines | Content |
|------|-------|---------|
| `_index.md` | 12 | Routing table with Min Confidence column (template + 1 real entry for query_patterns) |
| `schema_map.md` | 29 | Template only (example headers + placeholder tables) |
| `business_rules.md` | 20 | Template only (example enums + rules) |
| `query_patterns.md` | 40 | Template SQL examples + **3 real tool_experience notes** |
| `investigation_flows.md` | 43 | Template only (example flows) |
| **Total** | **144** | |

### Carried-Over Knowledge (3 entries)

All three entries are `tool_experience` type, confirmed on 2026-03-08, with initial confidence C0 = 1.0.

At experiment start (2026-03-12, t = 4 days), their confidence is:
- C(4) = e^(-0.005 * 4) = **0.980** (tool_experience lambda = 0.005)

| # | Decay Metadata | Content |
|---|---------------|---------|
| 1 | `<!-- decay: type=tool_experience confirmed=2026-03-08 C0=1.0 -->` | Avoid `!=` in SQL; use `<>` instead (shell escaping issue with `!=`) |
| 2 | `<!-- decay: type=tool_experience confirmed=2026-03-08 C0=1.0 -->` | Check data time range first — tables may have data gaps; confirm MIN/MAX timestamps before trend queries |
| 3 | `<!-- decay: type=tool_experience confirmed=2026-03-08 C0=1.0 -->` | Avoid Chinese strings in SQL WHERE clauses — shell parameter passing with Chinese characters may cause exit code 127; use numeric fields instead |

### Key Differences from v1 Baseline

| Aspect | v1 (R0) | v2 (R0) |
|--------|---------|---------|
| Prior knowledge | 0 entries (completely clean) | 3 tool_experience entries from v1 |
| Total lines | 144 (all template) | 144 (templates + 3 real entries) |
| Decay metadata | Not used | Every real entry carries `<!-- decay: ... -->` |
| Gate 4 model | Binary: fresh vs stale | Continuous: C(t) = e^(-lambda * t) per type |
| `_index.md` format | No confidence column | Min Confidence column added |
| SKILL.md Gate 4 | Single mode | Split into write mode (assign decay) and read mode (confidence-based response) |
| SKILL.md Scaling | Not present | Active line count check after each write |
| SKILL.md Gate 5 | Basic trigger | Expanded _index.md update trigger |
| SKILL.md new section | N/A | Confidence Decay Model reference table |

## references/ Initial State

Template files contain example placeholder content with no real domain knowledge about nan_platform, except for the 3 tool_experience notes in `query_patterns.md`. These notes represent the only knowledge transfer from v1 to v2.

Full R0 snapshot available at: `snapshots/R0-baseline/`
