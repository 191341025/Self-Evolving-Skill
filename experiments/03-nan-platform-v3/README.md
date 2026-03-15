**English** | **[中文](README.zh.md)**

# Experiment 03-nan-platform-v3

> Phase 5 Enhancement Validation: entities tag, search command, hard/soft signals, step-wise Gate 2/3

## Experiment Info

| Item | Value |
|------|-------|
| Target Database | nan_platform (MySQL 8.0) |
| Business Domain | Smart building / worker dormitory management platform |
| Data Scale | 29 tables, ~95K rows, 590MB |
| Skill Used | db-investigator (Phase 5 enhancements) |
| Execution Date | 2026-03-14 |
| Rounds | 5+1 rounds, 17 tasks + R6 time decay spot check |
| Starting State | references/ fully cleared — from zero |

## Experiment Objective

Validate 6 new capabilities introduced in Phase 5, using the same database as v1/v2 but starting from an empty knowledge base:

| # | Capability | What's New |
|---|-----------|------------|
| V1 | Step-wise Gate 2/3 | Extract entities -> search -> compare (replaces holistic LLM judgment) |
| V2 | Entities tag | `<!-- entities: t_room, t_building -->` extracted and attached on inject |
| V3 | Search command | `decay_engine.py search --entities` for targeted knowledge retrieval |
| V4 | Hard/soft signal distinction | `--weight 1.0` (default) for hard signals, `--weight 0.3` for soft signals |
| V5 | confirmed_at refresh | `feedback success` updates the `confirmed=YYYY-MM-DD` timestamp |
| V6 | Search-driven loading | Use entities to match files selectively instead of bulk loading |

## Key Results

| Metric | Result |
|--------|--------|
| Verification points passed | **6/6** (V1-V6 all pass) |
| Final knowledge entries | 8 (across 3 files) |
| Acceptance rate | ~42% (8 accepted / 19 evaluations) |
| Gate 2 contradiction rejections | 1 (T3.3 — false enum values rejected) |
| Gate 3 deduplication | 1 (T3.1 — repeated exploration correctly skipped) |
| Soft signal accuracy | weight=0.3 correctly applied (beta +0.3, not +1.0) |
| invalidate->reset lifecycle | Completed cleanly (T4.2-T4.3) |
| Bugs found | 1 critical (inject --target path concatenation) |

## Key Findings

1. **Entities + search enable precise Gate 2/3** — Step-wise execution (extract -> search -> compare) replaces holistic LLM judgment with structured evidence-based decisions
2. **Hard/soft signal distinction works correctly** — alpha accumulates at +1.0 for hard signals (SQL success), +0.3 for soft signals (alignment confirmation, enum miss)
3. **Gate 2 defends against incorrect human input** — T3.3 correctly rejected user-claimed enum values that contradicted SQL-verified data
4. **invalidate->reset lifecycle completes cleanly** — User report -> C0=0.1 -> tool verification -> reset to TRUST
5. **inject --target path bug is critical** — Silent write to wrong location; must be fixed before production use

## File Navigation

| File | Content | Priority |
|------|---------|----------|
| [`task-set.md`](task-set.md) | 5 rounds, 17 tasks with verification point mapping | Understand experiment design |
| [`03-quality-audit.md`](03-quality-audit.md) | **Core document**: quality audit, highlights, issues, v1/v2 comparison | Must-read |

### snapshots/ — Per-Round Knowledge Snapshots

Each subdirectory is a full copy of `references/` at the end of that round:

| Snapshot | Point in Time | Notes |
|----------|---------------|-------|
| `R0-baseline/` | Before experiment | All files empty (headers only) |
| `R1-initial-exploration/` | After Round 1 | 4 entries: t_room/t_building, t_employee/t_employee_settle, t_building/t_floor schemas, views catalog |
| `R2-data-queries/` | After Round 2 | +3 entries: room_type enum, shell escaping tip, subquery aggregation pattern |
| `R3-dedup-contradiction/` | After Round 3 | +1 entry (no-index warning); 1 SKIP, 1 REJECT |
| `R4-soft-signal-correction/` | After Round 4 | No new entries; soft signal + invalidate/reset tested |
| `R5-comprehensive/` | After Round 5 | Final state; search-driven retrieval validated |
| `R6-time-decay/` | Day 2 (2026-03-15) | Time decay spot check: natural decay + feedback refresh + projections |

**Quick diff example** (after local clone):
```bash
diff snapshots/R0-baseline/schema_map.md snapshots/R5-comprehensive/schema_map.md
```

## Additional Discovery

- **Table name correction:** task-set referenced `t_employee_station` which does not exist; actual table is `t_employee_settle`
- **Database has 0 stored procedures** but 12 views (v_employee_distribution, v_room_overview, etc.)
