**English** | **[中文](README.zh.md)**

# Experiment 01-nan-platform-v2

> Re-test of nan_platform with upgraded Gate 4 (Confidence Decay Model)

## Experiment Info

| Item | Value |
|------|-------|
| Target Database | nan_platform (MySQL 8.0) |
| Business Domain | Smart building / worker dormitory management platform |
| Data Scale | 29 tables, ~95K rows, 590MB |
| Skill Used | db-investigator (Gate 4 upgraded) |
| Execution Date | 2026-03-12 |
| Rounds | 5 rounds (structure exploration -> data queries -> rule discovery -> complex investigation -> repeat verification) |
| Starting State | 3 tool_experience notes carried from v1; all other references reset to templates |

## Experiment Objective

Validate the upgraded Gate 4 confidence decay model against the same database and task set as v1. The key question: does replacing binary date tagging with `C(t) = e^(-lambda * t)` and type-specific decay rates produce better knowledge governance decisions?

## Key Upgrade: Gate 4 Confidence Decay Model

| Aspect | v1 (Binary Date Tagging) | v2 (Confidence Decay) |
|--------|--------------------------|----------------------|
| Staleness check | Binary: fresh vs stale based on last_confirmed date | Continuous: C(t) = e^(-lambda * t) per knowledge type |
| Knowledge types | Not differentiated | 6 types with distinct lambda values |
| Response levels | Accept / Reject | TRUST (C >= 0.8) / VERIFY (0.5 <= C < 0.8) / REVALIDATE (C < 0.5) |
| High-decay data | No special handling | data_range and data_snapshot (lambda >= 0.035) prefer rejection |
| Index metadata | No confidence column | Min Confidence column added to _index.md |

### Six Knowledge Types and Decay Rates

| Type | lambda | Half-life (days) | Example |
|------|--------|------------------|---------|
| schema | 0.003 | 231 | Table columns, primary keys |
| tool_experience | 0.005 | 139 | Shell pitfalls, parameter tips |
| business_rule | 0.008 | 87 | Status field meanings, enum values |
| query_pattern | 0.015 | 46 | SQL templates, JOIN paths |
| data_range | 0.035 | 20 | Row counts, value ranges |
| data_snapshot | 0.050 | 14 | Specific query results, distributions |

## Key Results

| Metric | Result |
|--------|--------|
| Total Knowledge | 176 lines (vs v1 ~120 lines at comparable stage; difference mainly from decay metadata) |
| Acceptance Rate | ~24% (vs v1 ~30% -- stricter due to decay-based rejection) |
| Gate 2 Self-Corrections | 1 (room_type enum correction) |
| R5 Verification | 4/4 first-try success, 0 structure lookups |
| Accuracy | 100% (0 incorrect knowledge entries survived) |

## Key Changes from v1

1. **Confidence Decay Model**: Every knowledge entry tagged with type-specific lambda and confirmed date
2. **Three-level response**: TRUST (C >= 0.8) / VERIFY (0.5 <= C < 0.8) / REVALIDATE (C < 0.5)
3. **High-decay type preference**: data_range and data_snapshot (lambda >= 0.035) prefer rejection over storage
4. **Min Confidence column**: Added to _index.md for quick staleness overview

## File Navigation

| File | Content | Reading Priority |
|------|---------|-----------------|
| [`01-task-set.md`](01-task-set.md) | 5 rounds, 25 tasks (same as v1, with reuse annotations) | Understand experiment design |
| [`02-evolution-log.md`](02-evolution-log.md) | **Core data**: per-round Gate decisions, confidence scores, written content | Must-read |
| [`03-quality-audit.md`](03-quality-audit.md) | Quality audit with decay model effectiveness analysis | Must-read |
| [`04-comparison.md`](04-comparison.md) | Head-to-head v1 vs v2 comparison | Must-read |

### snapshots/ -- Per-Round Knowledge Snapshots

Each subdirectory is a full copy of `references/` at the end of that round. You can diff any two rounds to see the changes:

| Snapshot | Point in Time | Notes |
|----------|---------------|-------|
| `R0-baseline/` | Before experiment | Template + 3 tool_experience notes from v1 |
| `R1-structure/` | After Round 1 | Table schema + dictionary enum entries |
| `R2-queries/` | After Round 2 | SQL templates with confidence metadata |
| `R3-rules/` | After Round 3 | Business rules (includes Gate 2 self-correction) |
| `R4-investigations/` | After Round 4 | Investigation workflows + pitfalls |
| `R5-verification/` | After Round 5 | Validates knowledge reuse under decay model |

**Quick diff example** (after local clone):
```bash
diff snapshots/R0-baseline/business_rules.md snapshots/R5-verification/business_rules.md
```

## Key Findings

1. **Decay model effectively rejects volatile data** -- data_range and data_snapshot types are rejected at ~80% rate, preventing knowledge bloat from time-sensitive counts and distributions
2. **VERIFY level adds nuance** -- Instead of binary accept/reject, borderline knowledge is flagged for re-confirmation, reducing both false accepts and unnecessary rejections
3. **Gate 2 self-correction still works** -- Detected and corrected room_type enum error despite the new Gate 4 mechanics
4. **R5 reuse is stronger than v1** -- Confidence scores let the Skill make instant trust decisions without re-querying structure
5. **Carried tool_experience proved valuable** -- The 3 notes from v1 (shell encoding, `!=` vs `<>`, fetch_structure.py usage) eliminated all tooling friction from Round 1 onward
