**English** | **[中文](README.zh.md)**

# Experiment #02 — Telecom Billing Database (Anonymized)

## Experiment Details

| Item | Value |
|------|-------|
| Target Database | [Anonymized] Telecom billing system (MySQL) |
| Business Domain | Telecom billing / charge management |
| Data Scale | Large (TBD) |
| Skill Used | db-investigator |
| Start Date | 2026-03-08 |
| Status | In progress |

> **Privacy Notice**: This experiment involves a production-grade telecom billing database (test environment). All records have been desensitized — table names use semantic aliases, and no customer billing details or personally identifiable information are included. The experiment focuses on Skill evolution patterns, not the business data itself.

## Objective

Validate the **cross-domain reproducibility** of the Self-Evolving Skill design pattern — whether the Five-Gate Governance Protocol can again produce reasonable knowledge convergence on a fundamentally different database (large-scale telecom billing vs. small-scale smart building management).

## Key Differences from Experiment #01

| Dimension | #01 nan-platform | #02 telecom-billing |
|-----------|-----------------|---------------------|
| Scale | 29 tables, 590 MB | Large (TBD) |
| Domain | Smart building management (智能楼宇) | Telecom billing |
| Starting point | Completely blank | 3 cross-database tool tips retained |
| Record policy | Fully public | Anonymized before publishing |

## Pre-Experiment Decision Log

### Decision 1: references/ Reset Strategy

**Conclusion**: Clear domain knowledge, retain tool experience

| Category | Action | Rationale |
|----------|--------|-----------|
| schema_map.md | Reset to template | nan_platform table relationships are irrelevant to the new database |
| business_rules.md | Reset to template | Dictionary enums, status conventions, etc. are nan_platform-specific |
| query_patterns.md | Clear SQL templates, **retain 3 Tool Usage Notes** | Tool experience is database-agnostic (shell escaping, Chinese parameter passing, data gap periods) |
| investigation_flows.md | Reset to template | Investigation flows are tied to specific nan_platform tables |
| _index.md | Reset to generic routing template | Summary must match the new file contents |

**Retained tool tips**:
1. `!=` must be replaced with `<>` — shell parameter-passing limitation of db_query.py
2. Always check the data time range first — avoid misdiagnosis caused by data gap periods
3. Avoid Chinese strings in SQL — shell parameter-passing encoding issues

**Rationale**: These 3 tips are tool-level experience, independent of domain. Retaining them also tests an additional dimension: cross-database knowledge transfer.

### Decision 2: Five-Gate Protocol Adjustments

Based on observations from Experiment #01, two minor adjustments were made to SKILL.md before starting Experiment #02:

1. **Gate 5 expansion**: The _index.md update trigger was broadened from "when a new file is created" to "when a new file is created or an existing file's scope changes significantly"
2. **Scaling Rules active check**: Added an active check — verify the target file's line count after each write

### Decision 3: Anonymization Strategy

- Table names use semantic aliases (e.g., `[billing-T1]`) or anonymized generic names (e.g., `t_bill_detail`)
- Field names retain semantics but omit business specifics
- SQL templates preserve structure with substituted names
- Rejected knowledge entries record only the Gate number and rejection category, not the specific content
- All numeric values use approximate descriptions ("tens of thousands of rows" rather than exact counts)

## File Navigation

| File | Content | Status |
|------|---------|--------|
| `00-baseline.md` | Database baseline snapshot (anonymized) | To be created |
| `01-task-set.md` | Experiment task set | To be created |
| `02-evolution-log.md` | Evolution log (anonymized) | To be created |
| `03-quality-audit.md` | Quality audit | To be created |
| `snapshots/` | Per-round knowledge snapshots (anonymized) | To be created |
