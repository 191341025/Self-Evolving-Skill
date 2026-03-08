# Experiment #01 — nan_platform Smart Building Management Database

## Experiment Info

| Item | Value |
|------|-------|
| Target Database | nan_platform (MySQL 8.0) |
| Business Domain | Smart building / worker dormitory management platform (智能楼宇/工人宿舍管理平台) |
| Data Scale | 29 tables, ~95K rows, 590MB |
| Skill Used | db-investigator |
| Execution Date | 2026-03-08 |
| Rounds | 5 rounds (structure exploration → data queries → rule discovery → complex investigation → repeat verification) |

## Experiment Objective

Validate the knowledge governance effectiveness of the Self-Evolving Skill design pattern in a real-world database investigation scenario — does the Skill truly become "more accurate and more efficient with use, without becoming bloated"?

## Key Results

| Metric | Result |
|--------|--------|
| Knowledge Growth | 131 lines → 289 lines (+158 lines of effective knowledge) |
| Five-Gate Rejection Rate | 63.6% (21 rejections / 33 candidates) |
| Gate 2 Self-Correction | 2 occurrences (status field rule correction, device association description correction) |
| Incremental Convergence Curve | +75 → +46 → +12 → +21 → +1 |
| Repeated Task Efficiency | Exploration steps reduced from multiple to 0; direct template reuse |
| Accuracy | 100% (0 incorrect knowledge entries survived) |

### Incremental Convergence Curve

```
Line Increment
 80 ┤
    │ ■ R1 (+75)
 60 ┤
    │
 40 ┤      ■ R2 (+46)
    │
 20 ┤                  ■ R4 (+21)
    │           ■ R3 (+12)
  0 ┤                          ■ R5 (+1)
    └──────────────────────────────────→ Round
```

### Rejection Rate Trend

```
R1: 67% ████████████████░░░░░░░░
R2: 62% ███████████████░░░░░░░░░
R3: 50% ████████████░░░░░░░░░░░░
R4: 62% ███████████████░░░░░░░░░
R5: 80% ████████████████████░░░░  ← Maturity stage: almost no new writes
```

## File Navigation

| File | Content | Reading Priority |
|------|---------|-----------------|
| [`00-baseline.md`](00-baseline.md) | Database baseline snapshot: 29-table schema, entity relationships, dictionary system | Background |
| [`01-task-set.md`](01-task-set.md) | 5 rounds, 25 tasks, from simple queries to complex investigations | Understand experiment design |
| [`02-evolution-log.md`](02-evolution-log.md) | **Core data**: per-round Five-Gate decisions, written content, rejected knowledge | ⭐ Must-read |
| [`03-quality-audit.md`](03-quality-audit.md) | 6-dimension audit (rejection rate, accuracy, bloat, etc.) + overall summary | ⭐ Must-read |

### snapshots/ — Per-Round Knowledge Snapshots

Each subdirectory is a full copy of `references/` at the end of that round. You can diff any two rounds to see the changes:

| Snapshot | Point in Time | Total Lines | Notes |
|----------|---------------|-------------|-------|
| `R0-baseline/` | Before experiment | 131 | Template only, no real knowledge |
| `R1-structure/` | After Round 1 | 206 | Table schema + dictionary enum entries written |
| `R2-queries/` | After Round 2 | 252 | SQL templates + tooling experience written |
| `R3-rules/` | After Round 3 | 264 | Business rule corrections (Gate 2 self-correction) |
| `R4-investigations/` | After Round 4 | 277 | Investigation workflows + pitfalls written |
| `R5-verification/` | After Round 5 | 289 | Only +1 line; validates knowledge reuse |

**Quick diff example** (after local clone):
```bash
diff snapshots/R0-baseline/business_rules.md snapshots/R5-verification/business_rules.md
```

## Key Findings

1. **Five-Gate effectively filters junk knowledge** — 63.6% rejection rate, primarily blocking one-off query results and time-sensitive data
2. **Gate 2 self-correction capability** — Detected and corrected the erroneous rule "all tables use status='1'"; this is the most valuable gate in the Five-Gate system
3. **Incremental convergence matches design expectations** — From +75 to +1, a clear growth stage → maturity stage curve
4. **Significant efficiency gains on repeated tasks** — All Round 5 repeated tasks required zero exploration, directly reusing existing templates and workflows
5. **Pitfalls are a high-value byproduct** — Tooling experience (`!=` → `<>`, Chinese shell encoding issues) was unexpected but proved the most practical
