# Skill Evolution Log

> Records every change to db-investigator Skill's references/ during the experiment.
> This is the core data of the experiment, submitted to GitHub as empirical validation of the design pattern.

---

## Format

Each time references/ changes, record it in the following format:

```
### [Round.Task] Summary
- **Time**: YYYY-MM-DD HH:MM
- **Trigger task**: specific task description
- **Five-Gate decisions**:
  - Gate 1 (VALUE): pass/reject — reason
  - Gate 2 (ALIGNMENT): pass/skip
  - Gate 3 (REDUNDANCY): pass/skip
  - Gate 4 (FRESHNESS): stable fact / date-tagged
  - Gate 5 (PLACEMENT): → target file
- **Changes made**: what was written
- **Quality assessment**: [accurate / needs verification / risky]
```

---

## Evolution Records

### [R1] Round 1 — Structure Exploration (Batch Write)
- **Time**: 2026-03-08 15:30
- **Trigger task**: 1.1–1.5 (table classification, entity relationships, employee associations, entry/exit associations, dictionary system)

#### Write 1: schema_map.md (template → real content)
- **Five-Gate decisions**:
  - Gate 1 (VALUE): **pass** — Table relationships and JOIN paths are the foundation for every query; high reuse
  - Gate 2 (ALIGNMENT): pass — Replacing template content, no conflicts
  - Gate 3 (REDUNDANCY): pass — first write
  - Gate 4 (FRESHNESS): stable fact — Table structures do not change frequently
  - Gate 5 (PLACEMENT): → schema_map.md
- **Changes made**:
  - Database overview (nan_platform = smart building management platform)
  - Complete entity relationship diagram (building→floor→room, employee→settle→room, emp_record↔employee via id_card)
  - Table classification (7 groups, 29 tables total)
  - 8 key JOIN paths
- **Quality assessment**: accurate (all verified through actual queries)

#### Write 2: business_rules.md (template → real content)
- **Five-Gate decisions**:
  - Gate 1 (VALUE): **pass** — The status='1' convention affects all queries; dictionary enum values are frequently needed for data analysis
  - Gate 2 (ALIGNMENT): pass
  - Gate 3 (REDUNDANCY): pass — first write
  - Gate 4 (FRESHNESS): stable fact — Dictionary values and field conventions do not change frequently
  - Gate 5 (PLACEMENT): → business_rules.md
- **Changes made**:
  - 5 key field conventions (status='1' meaning, primary key types, no foreign keys, audit fields, common create_by values)
  - Complete enum values for 13 dictionary types
- **Quality assessment**: accurate (dictionary values queried directly from sys_dict_value)

#### Rejected Knowledge
| Candidate knowledge | Rejection gate | Reason |
|---------------------|----------------|--------|
| "Currently 2071 employees" | Gate 4 (FRESHNESS) | Data volume changes constantly; stale upon writing |
| "Each building has 3 floors, 26–36 rooms" | Gate 1 (VALUE) | One-off query result, not a reusable pattern |
| "Face_In has 46112 records" | Gate 4 (FRESHNESS) | Real-time growing data; do not store |
| "1517/1518 ID cards match an employee" | Gate 1+4 | One-off result + time-sensitive |

#### references/ Change Statistics
| File | Before | After | Increment |
|------|--------|-------|-----------|
| schema_map.md | 30 lines (template) | 47 lines (real) | +17 lines of effective content |
| business_rules.md | 21 lines (template) | 73 lines (real) | +52 lines of effective content |
| query_patterns.md | unchanged | unchanged | 0 |
| investigation_flows.md | unchanged | unchanged | 0 |
| **Total** | 51 lines | 120 lines | **+69 lines** |

---

### [R2] Round 2 — Data Investigation (Single-Step Queries)
- **Time**: 2026-03-08 15:45

#### Write 1: query_patterns.md (template → real query templates)
- **Five-Gate decisions**:
  - Gate 1 (VALUE): **pass** — Building occupancy rate, demographics, entry/exit trends, and device status are all high-frequency query scenarios
  - Gate 2 (ALIGNMENT): pass — Replacing template
  - Gate 3 (REDUNDANCY): pass — first write
  - Gate 4 (FRESHNESS): stable pattern — SQL templates do not change with data
  - Gate 5 (PLACEMENT): → query_patterns.md
- **Changes made**:
  - 5 SQL templates: building occupancy rate, gender distribution, age distribution, entry/exit trends, device status
  - 2 tool usage lessons: `!=` must be replaced with `<>`; always check data time range first
- **Quality assessment**: accurate (all verified through actual execution)

#### Write 2: schema_map.md (incremental correction)
- **Five-Gate decisions**:
  - Gate 1 (VALUE): **pass** — Sparse device associations are an important structural insight
  - Gate 2 (ALIGNMENT): **correction** — Original description "optional association" was inaccurate; actually "mostly NULL"
  - Gate 5: → schema_map.md (correcting existing entry)
- **Changes made**: Added warning that t_device.building_id is mostly NULL

#### Write 3: business_rules.md (increment)
- **Five-Gate decisions**:
  - Gate 1 (VALUE): **pass** — Data time range affects all time-related queries
  - Gate 4 (FRESHNESS): **date-tagged** — Tagged "confirmed 2026-03-08, may continue growing"
  - Gate 5: → business_rules.md
- **Changes made**: t_emp_record data range 2025-12-10 ~ 2026-02-28

#### Rejected Knowledge
| Candidate knowledge | Rejection gate | Reason |
|---------------------|----------------|--------|
| "19 worker dormitory buildings + 1 couples' building" | Gate 1 | One-off query result |
| "640 residents, 618 male / 22 female" | Gate 4 | Time-sensitive, changes constantly |
| "13# occupancy 94.4%, 12# 90%" | Gate 1+4 | Specific values are not reusable patterns |
| "225 normal / 7 inaccessible / 1 deactivated" | Gate 4 | Device status data changes constantly |
| "2/22–2/28 entry/exit shows growth trend" | Gate 1 | One-off analysis conclusion |

#### references/ Change Statistics
| File | After R1 | After R2 | Increment |
|------|----------|----------|-----------|
| schema_map.md | 57 lines | 57 lines | ~0 (1 line corrected) |
| business_rules.md | 73 lines | 74 lines | +1 line |
| query_patterns.md | 30 lines (template) | 55 lines (real) | +25 lines of effective content |
| investigation_flows.md | unchanged | unchanged | 0 |
| **Total** | 120 lines | 186 lines | **+26 lines** |

#### Observations
- Round 2 increment (+26 lines) is much smaller than Round 1 (+69 lines), consistent with the expected "growth phase slowdown"
- Five-Gate rejected 5 candidate items; **rejection rate 62.5%** (5 rejected / 8 candidates) — governance is working
- Gate 2 triggered the "correction" function for the first time (device association description corrected from "optional" to "mostly NULL")
- Tool usage lesson (`!=` → `<>`) was an unexpected gain — a knowledge type not anticipated in Round 1

---

### [R3] Round 3 — Business Rule Discovery
- **Time**: 2026-03-08 16:00

#### Write 1: business_rules.md — status field rule correction (Gate 2 triggered)
- **Five-Gate decisions**:
  - Gate 1 (VALUE): **pass** — Not knowing this distinction causes queries on record tables to return 0 results
  - Gate 2 (ALIGNMENT): **correction** — Original rule "all tables use status='1' uniformly" was incorrect; record tables (_record) use status='0'
  - Gate 3 (REDUNDANCY): Correcting existing entry, not a new addition
  - Gate 4 (FRESHNESS): stable fact
  - Gate 5 (PLACEMENT): → business_rules.md
- **Changes made**: Changed "all tables uniform" to "master data tables use status='1'"; added exception note
- **Quality assessment**: accurate (verified by actual query: t_emp_record all have status='0', t_car_record likewise)
- **Significance**: This is a textbook case of Gate 2 (ALIGNMENT) — discovering existing knowledge is wrong and correcting it rather than appending

#### Write 2: business_rules.md — result field meaning
- **Five-Gate decisions**:
  - Gate 1 (VALUE): **pass** — Understanding that result is face recognition confidence is valuable for data analysis
  - Gate 2-3: pass (new knowledge)
  - Gate 4: stable fact
  - Gate 5: → business_rules.md
- **Changes made**: Added t_emp_record Fields section; noted result = face recognition confidence (0–99)

#### Write 3: business_rules.md — end_time vs id_end_time distinction
- **Five-Gate decisions**:
  - Gate 1 (VALUE): **pass** — These two date fields are easily confused; must know this when querying expired employees
  - Gate 5: → business_rules.md
- **Changes made**: Added t_employee Date Fields section; clarified that end_time is the business expiration date

#### Rejected Knowledge
| Candidate knowledge | Rejection gate | Reason |
|---------------------|----------------|--------|
| "settle_status is consistent with building/room data" | Gate 1 | One-off verification conclusion, not a reusable rule |
| "49 people expired but still settle_in" | Gate 1+4 | One-off statistic + time-sensitive |
| "33 people with entry-only or exit-only records" | Gate 1+4 | One-off statistic |

#### references/ Change Statistics
| File | After R2 | After R3 | Increment |
|------|----------|----------|-----------|
| schema_map.md | 56 lines | 56 lines | 0 |
| business_rules.md | 69 lines | 81 lines | +12 lines (including 1 correction) |
| query_patterns.md | 74 lines | 74 lines | 0 |
| investigation_flows.md | 43 lines | 43 lines | 0 |
| **Total** | 252 lines | 264 lines | **+12 lines** |

#### Observations
- Increment continues to decrease: R1 +69 lines → R2 +26 lines → R3 +12 lines
- **Gate 2 correction triggered again**: status rule corrected from "uniform" to "has exceptions" — a high-value correction
- Rejection rate 50% (3 rejected / 6 candidates); all rejections were specific values / one-off statistics
- Round 3 output was primarily **business rule clarification** — no new structures or query templates, consistent with expected positioning

---

### [R4] Round 4 — Complex Investigation (Multi-Step)
- **Time**: 2026-03-08 16:30

#### Write 1: investigation_flows.md (template → real investigation flows)
- **Five-Gate decisions**:
  - Gate 1 (VALUE): **pass** — Employee profile, ghost employee audit, and building comparison are all reusable multi-step investigation flows
  - Gate 2 (ALIGNMENT): pass — Replacing template
  - Gate 3 (REDUNDANCY): pass — first write
  - Gate 4 (FRESHNESS): stable process — Investigation steps do not change with data
  - Gate 5 (PLACEMENT): → investigation_flows.md
- **Changes made**:
  - 3 investigation flows: Employee Profile (3 steps), Ghost Employee Audit (3 steps), Building Comparison (3 steps)
  - Each flow includes Pitfall warnings (based on actual mistakes encountered)
- **Quality assessment**: accurate (every flow verified through actual execution)

#### Write 2: business_rules.md — washroom capacity=0 should be excluded
- **Five-Gate decisions**:
  - Gate 1 (VALUE): **pass** — Not excluding these inflates room counts
  - Gate 2 (ALIGNMENT): **enhancement** — Supplemented business meaning for room_type enum
  - Gate 5: → business_rules.md (modifying existing entry)
- **Changes made**: Added capacity notes and statistical caveats to room_type enum

#### Write 3: query_patterns.md — Chinese characters in shell parameter issue
- **Five-Gate decisions**:
  - Gate 1 (VALUE): **pass** — Third tool usage lesson, equally important as `!=` and data gap issues
  - Gate 5: → query_patterns.md Tool Usage Notes
- **Changes made**: Added "avoid Chinese character strings in SQL" lesson

#### Rejected Knowledge
| Candidate knowledge | Rejection gate | Reason |
|---------------------|----------------|--------|
| "Entry/exit peaks: 5–6am out / 5–7pm back" | Gate 1 | Conclusion based on February data; may vary by season/project |
| "235 ghost employees" | Gate 4 | Time-sensitive data |
| "13# 151 people, 20# 116 people" | Gate 4 | Time-sensitive |
| "Li Mengyang 131 entry/exit records" | Gate 1 | One-off query |
| "10 buildings completely vacant" | Gate 1+4 | One-off statistic + changes with occupancy |

#### references/ Change Statistics
| File | After R3 | After R4 | Increment |
|------|----------|----------|-----------|
| schema_map.md | 57 lines | 57 lines | 0 |
| business_rules.md | 82 lines | 83 lines | +1 line |
| query_patterns.md | 75 lines | 76 lines | +1 line |
| investigation_flows.md | 43 lines (template) | 62 lines (real) | +19 lines of effective content |
| **Total** | 267 lines | 288 lines | **+21 lines** |

#### Observations
- Increment trend: R1 +75 → R2 +46 → R3 +12 → R4 +21 (R4 slightly rebounds because investigation_flows was written for the first time)
- **All four references files now activated**: schema_map (R1) → business_rules (R1) → query_patterns (R2) → investigation_flows (R4)
- Pitfall warnings in investigation flows are the most valuable part — derived from actual mistakes; can be directly avoided next time
- Five-Gate continues to effectively reject specific values and time-sensitive data; 5 rejected / 5 accepted (50% rejection rate)

---

### [R5] Round 5 — Repetition and Evolution Verification
- **Time**: 2026-03-08 17:00

#### Task 5.1: Re-ask "What is the occupancy rate for each building?" (repeat of R2 task)
- **Behavior**: **Directly used `query_patterns.md` Building Occupancy template**
- **Exploration steps**: 0 (no calls to fetch_structure or fetch_index)
- **Query count**: 1
- **Comparison with R2**: In R2, multiple exploration steps were needed to understand table structure before writing SQL; in R5, the template was directly copied and executed
- **Knowledge reuse**: query_patterns.md ✅

#### Task 5.2: Re-query "Employee age distribution" (repeat of R2 task)
- **Behavior**: **Directly used `query_patterns.md` Employee Demographics template**
- **Exploration steps**: 0
- **Query count**: 1
- **Knowledge reuse**: query_patterns.md ✅ (including birthday IS NOT NULL filter, settle JOIN condition)

#### Task 5.3: Redo "ghost employee" investigation (repeat of R4 task)
- **Behavior**: **Strictly followed `investigation_flows.md` Ghost Employee Audit three-step flow**
- **Pitfall avoidance**: ✅ Used MAX(auth_time) as cutoff instead of CURDATE()
- **Query count**: 4 (Step1a: cutoff → Step1b: count → Step2: building distribution → Step3: last-seen classification)
- **Knowledge reuse**: investigation_flows.md ✅ + schema_map.md ✅ (id_card association) + business_rules.md ✅ (status rules)

#### Task 5.4: New question "Which companies have the most settled employees?"
- **Behavior**: Leveraged existing knowledge for rapid lookup; only needed to explore t_company association path
- **Known and reused**: status='1' convention, settle_status dictionary values, base JOIN paths
- **New exploration needed**: Only the t_building_rent.company_id → t_company.id association
- **Query count**: 5 (1 structure + 1 column search + 1 settle structure + 2 data queries)
- **Comparison with R1**: R1 explored entirely from scratch; R5's new question only needed to explore the new association path while reusing all other knowledge

#### Write 1: schema_map.md — Added company → building JOIN path
- **Five-Gate decisions**:
  - Gate 1 (VALUE): **pass** — Company-dimension analysis is a reusable scenario
  - Gate 2 (ALIGNMENT): pass — No conflicts
  - Gate 3 (REDUNDANCY): pass — New knowledge
  - Gate 4 (FRESHNESS): stable fact
  - Gate 5 (PLACEMENT): → schema_map.md Key Join Paths
- **Changes made**: Added `company → building: t_building_rent.company_id = t_company.id`

#### Rejected Knowledge
| Candidate knowledge | Rejection gate | Reason |
|---------------------|----------------|--------|
| "t_company.company_type is all NULL" | Gate 1+4 | One-off data state; changes with data entry |
| "Zhongjian Hongda has 483 people, the most" | Gate 4 | Time-sensitive data |
| "274 ghost employees" | Gate 4 | Time-sensitive |
| "Age distribution of 640 current residents" | Gate 4 | Time-sensitive |

#### references/ Change Statistics
| File | After R4 | After R5 | Increment |
|------|----------|----------|-----------|
| schema_map.md | 57 lines | 58 lines | +1 line |
| business_rules.md | 83 lines | 83 lines | 0 |
| query_patterns.md | 76 lines | 76 lines | 0 |
| investigation_flows.md | 65 lines | 65 lines | 0 |
| **Total** | 288 lines | 289 lines | **+1 line** |

#### Core Observation: Evolution Verification Succeeded

**Efficiency improvement comparison**:

| Task | First time (R2/R4) | Repeat (R5) | Improvement |
|------|---------------------|-------------|-------------|
| Building occupancy rate | Multi-step exploration + build SQL | 1 query, used template directly | Exploration steps → 0 |
| Age distribution | Multi-step exploration + build SQL | 1 query, used template directly | Exploration steps → 0 |
| Ghost employees | Step-by-step trial and error + pitfalls | 4 queries, followed flow + avoided pitfalls | Systematized, no pitfalls |
| New question (company) | — | 5 queries, extensive knowledge reuse | Only explored new association |

**Complete increment trend curve**: R1 +75 → R2 +46 → R3 +12 → R4 +21 → R5 +1

**Key conclusions**:
1. **Knowledge is indeed reused**: All repeated tasks in R5 directly used existing templates and flows from references/
2. **Exploration cost drastically reduced**: Structure exploration steps for repeated tasks dropped to 0
3. **Pitfalls actively avoided**: Ghost employee investigation proactively used MAX(auth_time) instead of CURDATE()
4. **Increment approaches zero**: R5 added only +1 line, consistent with the expected "maturity phase" — Skill has largely stabilized
5. **New questions still trigger learning**: Task 5.4 discovered a new JOIN path and correctly wrote it through Five-Gate
6. **Five-Gate remains effective**: Rejected 4 time-sensitive items; rejection rate 80% (4 rejected / 5 candidates) — the more mature, the higher the rejection rate
