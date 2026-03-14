**English** | **[中文](03-quality-audit.zh.md)**

# Quality Audit Report (v3 — Phase 5 Enhancement Validation)

> Quality audit for experiment 03-nan-platform-v3. Validates 6 new Phase 5 capabilities: entities tag, search command, step-wise Gate 2/3, hard/soft signal distinction, confirmed_at refresh, and search-driven loading.

---

## Experiment Overview

| Item | Value |
|------|-------|
| Target Database | nan_platform (MySQL 8.0) |
| Rounds | 5 (17 tasks) |
| Starting State | references/ fully cleared (from zero) |
| Execution Date | 2026-03-14 |
| Final Knowledge | 8 entries across 3 files |

---

## Verification Points — Final Status

| # | Verification Point | Phase | Covered In | Result |
|---|-------------------|-------|------------|--------|
| V1 | Step-wise Gate 2/3 (extract entities -> search -> compare) | 5D | R3 | **PASS** — T3.1 dedup, T3.2 same-entity-different-fact pass, T3.3 contradiction rejection |
| V2 | Entities tag extraction (LLM correctly extracts entity names on inject) | 5A | R1, R2 | **PASS** — 8/8 entries have entities tags |
| V3 | Search command invocation (Gate 2/3/retrieval actively calls search) | 5A/5C | R3, R5 | **PASS** — R3: 3 calls, R5: 2 calls |
| V4 | Hard/soft signal distinction (--weight selection by signal type) | 5B | R2, R4 | **PASS** — hard: alpha +1.0, soft: alpha/beta +0.3 |
| V5 | confirmed_at refresh (feedback success updates confirmed date) | 5B | R2, R5 | **PASS** — confirmed updated on every feedback success |
| V6 | Search-driven loading (entities match replaces bulk file loading) | 5C | R5 | **PASS** — T5.1 used search to retrieve 6 relevant entries |

**All 6 verification points passed.**

---

## Knowledge Evolution Trajectory

| Round | Entry Count | Added | Rejected | Key Events |
|-------|------------|-------|----------|------------|
| R0 | 0 | — | — | Baseline (empty) |
| R1 | 4 | +4 | 0 | Initial structure exploration; all entries get entities tags |
| R2 | 7 | +3 | 0 | Data queries + business rule discovery + tool experience |
| R3 | 8 | +1 | 2 | T3.1 SKIP (dedup), T3.3 REJECT (contradiction with SQL-verified data) |
| R4 | 8 | 0 | 0 | Soft signal + invalidate->reset lifecycle |
| R5 | 8 | 0 | 0 | Comprehensive search-driven retrieval validation |

**Acceptance rate: 8 accepted / 19 evaluations = ~42%** (remaining ~58% rejected by Gates or not producing knowledge candidates)

---

## Final Knowledge Inventory

| File | Entries | Types | Key Content |
|------|---------|-------|-------------|
| schema_map.md | 3 | schema x3 | t_room/t_building JOIN, t_employee/t_employee_settle JOIN, t_building/t_floor hierarchy |
| business_rules.md | 2 | business_rule x2 | room_type enum (together/washroom), building_id no-index warning |
| query_patterns.md | 3 | query_pattern x2, tool_experience x1 | Views catalog, != shell escaping, subquery aggregation pattern |
| investigation_flows.md | 0 | — | No multi-step flows emerged (expected for structure-focused tasks) |
| **Total** | **8** | **3 files active** | |

---

## Feedback Signal Tracking

| Entry | alpha | beta | Interpretation |
|-------|-------|------|---------------|
| schema_map:5 (t_room/t_building) | 4.0 | 0.0 | Most-used entry; 4 successful query validations |
| schema_map:9 (t_employee/t_employee_settle) | 3.0 | 0.0 | 3 successful query validations |
| schema_map:13 (t_building/t_floor) | 0.0 | 0.0 | Went through full invalidate->reset cycle; counters cleared |
| business_rules:5 (room_type enum) | 0.3 | 0.3 | soft success (R3 alignment confirmation) + soft failure (R4 enum miss) |
| business_rules:9 (no-index warning) | 0.0 | 0.0 | Human injection, not yet referenced in queries |
| query_patterns:5 (views catalog) | 0.0 | 0.0 | Informational, not directly used |
| query_patterns:9 (shell escaping) | 0.0 | 0.0 | Implicit use (avoided != after learning) |
| query_patterns:13 (subquery pattern) | 1.0 | 0.0 | Used in T5.1 complex query |

---

## Highlights

### 1. Gate 2 Contradiction Detection (T3.3)

The strongest moment of the experiment. User claimed room_type values were `single_room` and `double_room`, but existing knowledge (verified by SQL in R2) recorded `together` and `washroom`. Gate 2 correctly rejected the false information. This demonstrates the protocol's ability to defend knowledge integrity against incorrect human input.

### 2. Selective Growth Realized

17 tasks produced only 8 knowledge entries. R3 rejected 2 (1 duplicate, 1 contradiction), R4/R5 added nothing. The knowledge base grew selectively in R1-R2, then stabilized — exactly the convergence pattern the design philosophy prescribes.

### 3. Complete invalidate -> revalidate -> reset Lifecycle (T4.2-T4.3)

User reported knowledge was wrong -> invalidate (C0=0.1, REVALIDATE) -> tool re-verification (fetch_structure + JOIN queries) -> confirmed correct -> reset (C0=1.0, TRUST). The full lifecycle completed cleanly, demonstrating that the system both respects user feedback (immediate downgrade) and requires evidence for recovery (tool verification).

### 4. alpha/beta Accumulation Tells a Coherent Story

schema_map:5 ended at alpha=4.0 — the most battle-tested entry. This signal has real information value for future prioritization and trust decisions.

---

## Issues Found

### Critical: inject --target Path Concatenation Bug

**Severity: Must fix**

When `--target` receives a relative path (e.g., `.claude/skills/.../schema_map.md`), `run_inject()` concatenates it with `REFERENCES_DIR`, producing a deeply nested wrong path like `references/.claude/skills/.../schema_map.md`.

**Impact:**
- Knowledge silently written to wrong location
- inject reports success (exit code 0, `written to` message)
- Actual target file unchanged
- Violates fail-loud principle: a write tool that writes to the wrong place should error, not silently succeed

**Fix:** Validate `--target` — if it contains path separators, either error or auto-extract the filename. Or restrict to filename-only input.

### Design Concern: Soft Signal Semantic Ambiguity (T4.1)

The protocol rule "Empty result on enum/status value query -> soft failure" does not distinguish between:
- "The enum value genuinely doesn't exist" (knowledge is correct)
- "The enum knowledge is incomplete" (knowledge is wrong)

In T4.1, `quad_room` returned 0 rows, confirming the existing knowledge that only `together` and `washroom` exist. Recording a failure signal on correct knowledge is logically inconsistent. The rule needs refinement.

**Suggested fix:** Change the rule to: "Empty result on enum value query -> soft failure ONLY IF the queried value was suggested by existing knowledge. If the queried value was user-supplied and not in the known enum, the empty result CONFIRMS existing knowledge -> soft success instead."

### Limitation: Time Decay Not Tested

All entries were created on the same day (2026-03-14), so `t=0` in the decay formula `C(t) = C0 * e^(-lambda*t)`. The natural TRUST -> VERIFY -> REVALIDATE degradation path was never triggered. This was already validated in v1/v2, but v3's verification point coverage has a gap here.

### Observation: Protocol Compliance Depends on LLM Discipline

The Five-Gate protocol is natural language instructions for the LLM. The LLM must remember to search, correctly extract entities, choose appropriate weights, and record feedback. There is no mechanical enforcement. This is an architectural trade-off that should be explicitly acknowledged in design documentation, with "protocol compliance rate" tracked as an observable metric in experiments.

### Observation: Single-Line Knowledge Format Readability

Dense entries like schema_map:5 (300+ characters on one line) become hard to audit as the knowledge base grows. This is a format issue, not an architecture problem.

---

## Comparison with v1/v2

| Metric | v1 | v2 | v3 |
|--------|----|----|-----|
| Focus | Basic Five-Gate validation | Gate 4 decay model | Phase 5 enhancements (entities, search, signals) |
| Starting state | Empty | Carried 3 entries from v1 | Empty (from zero) |
| Tasks | 22 | 25 | 17 |
| Final entries | ~30 | ~10 (decay tags) | 8 |
| Acceptance rate | ~36% | ~24% | ~42% |
| Gate 2 corrections | 2 | 1 | 1 (rejection, not correction) |
| New capabilities validated | Five-Gate protocol | Decay model, TRUST/VERIFY/REVALIDATE | Entities, search, hard/soft signals, invalidate/reset |
| Bugs found | — | — | inject path concatenation bug |
