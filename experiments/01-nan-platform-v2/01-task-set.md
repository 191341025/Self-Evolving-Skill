# Experiment Task Set (v2)

> Same 25 tasks as v1, re-executed with the upgraded Gate 4 confidence decay model.
> Annotations indicate which knowledge was carried over from v1 and which was freshly acquired.
>
> Design principle: Cover the full difficulty gradient from simple queries to complex multi-step investigations. Each task may trigger a Gate decision with confidence scoring.
> Tasks are executed in rounds; after each round, check for changes in references/.

## Starting State

| Component | State |
|-----------|-------|
| schema_map | Reset to template (empty) |
| business_rules | Reset to template (empty) |
| query_patterns | Reset to template (empty) |
| investigation_flows | Reset to template (empty) |
| tool_experience | **3 notes carried from v1**: shell encoding, `!=` vs `<>` in MySQL, fetch_structure.py usage |
| _index.md | Reset to template (with new Min Confidence column) |

---

## Round 1: Structure Exploration (Let the Skill learn the database)

**Goal**: Rebuild schema knowledge from scratch; tool_experience reuse should eliminate tooling friction.

| # | Task | Method | Expected Knowledge Tier | v1 Reuse |
|---|------|--------|------------------------|----------|
| 1.1 | What tables exist in this database? What is the business purpose of each? | fetch_index.py | schema_map | None -- fresh discovery |
| 1.2 | What are the core table structures? Show columns, types, and keys for the main tables. | fetch_structure.py | schema_map | tool_experience reuse (fetch_structure.py usage note) |
| 1.3 | What are the entity relationships (buildings -> floors -> rooms, employees -> settle records)? | SQL exploration | schema_map | None -- fresh discovery |
| 1.4 | Verify JOIN paths: can you join emp_record to employee? What is the key chain? | SQL verification | schema_map | None -- fresh discovery |
| 1.5 | How is the dictionary system designed? List all dictionary types and values. | SQL exploration | schema_map + business_rules | None -- fresh discovery |

**Round 1 Decay Notes**:
- All schema knowledge written with lambda=0.003 (half-life 231 days) -- highly durable
- Dictionary enum values written as business_rule (lambda=0.008)

---

## Round 2: Data Queries (Single-step queries)

**Goal**: Build query templates; expect higher rejection rate than v1 due to data_snapshot decay.

| # | Task | Expected Knowledge Tier | Confidence Type | v1 Reuse |
|---|------|------------------------|-----------------|----------|
| 2.1 | How many buildings are there? What are their types? | query_patterns | data_range | None |
| 2.2 | How many rooms does each building have? What is the occupancy rate? | query_patterns | query_pattern + data_snapshot | None |
| 2.3 | What is the gender and age distribution of currently residing employees? | query_patterns | query_pattern + data_snapshot | None |
| 2.4 | What is the trend of entry/exit records over the past week? | query_patterns | query_pattern + data_snapshot | None |
| 2.5 | What is the device status distribution? How many faulty devices? | query_patterns | query_pattern + data_snapshot | None |
| 2.6 | Which building has the highest device density? | query_patterns | query_pattern + data_range | None |

**Round 2 Decay Notes**:
- SQL template patterns (lambda=0.015) are stored; specific counts and distributions (lambda=0.050) are rejected
- This is the key difference from v1: v1 stored some data snapshots; v2 rejects them via confidence decay

---

## Round 3: Business Rules (Requires reasoning)

**Goal**: Discover and validate business rules; Gate 2 self-correction expected.

| # | Task | Expected Knowledge Tier | Confidence Type | v1 Reuse |
|---|------|------------------------|-----------------|----------|
| 3.1 | What are the employee type distributions? What does each type mean? | business_rules | business_rule | None |
| 3.2 | What is the settle_status lifecycle? What states exist and what transitions are valid? | business_rules | business_rule | None |
| 3.3 | What is the relationship between room_type and room capacity? | business_rules | business_rule | None -- Gate 2 correction expected here |
| 3.4 | What is the device brand distribution? How many brands are in the system? | business_rules + query_patterns | business_rule + data_snapshot | None |
| 3.5 | What is the relationship between company type and building rent? | business_rules | business_rule + data_range | None |

**Round 3 Decay Notes**:
- Business rules stored with lambda=0.008 (half-life 87 days)
- Gate 2 self-correction on room_type: initial assumption corrected after data verification
- data_snapshot components (brand counts, rent figures) rejected via decay model

---

## Round 4: Complex Multi-step Investigation

**Goal**: Build investigation workflows; test confidence-based trust in earlier schema knowledge.

| # | Task | Expected Knowledge Tier | Confidence Type | v1 Reuse |
|---|------|------------------------|-----------------|----------|
| 4.1 | Which companies are in the highest-occupancy buildings? Cross-reference company, settle, building tables. | investigation_flows | query_pattern | Schema knowledge trusted (C >= 0.95) |
| 4.2 | Find employees with ID cards expiring within 3 months. What are their settle statuses? | investigation_flows | query_pattern | Schema knowledge trusted |
| 4.3 | Who are the top 10 most frequent entry/exit employees? Build their profiles. | investigation_flows | query_pattern | Schema + query_patterns trusted |
| 4.4 | Find cancelled employees who still have subsequent entry/exit records. | investigation_flows | query_pattern | Schema + business_rules trusted |
| 4.5 | Which building has the highest device fault rate? Analyze by device type. | investigation_flows | query_pattern | Schema + query_patterns trusted |

**Round 4 Decay Notes**:
- Investigation flows stored with lambda=0.015 (half-life 46 days)
- All earlier schema entries have C >= 0.95 (only 4 days old with lambda=0.003) -- TRUST level
- Specific result counts from investigations rejected (data_snapshot, lambda=0.050)

---

## Round 5: Repetition & Evolution Verification

**Goal**: Verify that the Skill reuses knowledge without re-querying. All 4 tasks are repeats of earlier rounds.

| # | Task | Repeats | Verification Goal | v1 Reuse |
|---|------|---------|-------------------|----------|
| 5.1 | How many settled employees does each building have? | R2.2 variant | Does it reuse query_patterns template? Does confidence score allow TRUST? | Pattern should be trusted (C >= 0.9) |
| 5.2 | What is the gender ratio of currently residing employees? | R2.3 variant | Does it skip structure exploration? Is schema knowledge trusted? | Pattern should be trusted (C >= 0.9) |
| 5.3 | What is the device brand distribution? | R3.4 repeat | Does it reuse business_rules? Is data_snapshot rejected again? | Rule trusted; snapshot re-rejected |
| 5.4 | What is the recent entry/exit record trend? | R2.4 repeat | Does it use existing pattern? Compare response speed with Round 2. | Pattern trusted; snapshot re-rejected |

**Round 5 Decay Notes**:
- All query_pattern entries (lambda=0.015) are 0-4 days old -- C >= 0.94 -- TRUST level
- All schema entries are TRUST level
- Expected: 0 structure lookups, 4/4 first-try success

---

## Post-Round Checklist

After completing each round, record the following in the evolution log:

1. **references/ change diff**: Which files were modified? What content was added?
2. **Gate decision log**: Record each Gate decision with confidence scores (especially rejections and VERIFY-level decisions)
3. **Confidence snapshot**: Current min/max/avg confidence per knowledge type
4. **Quality assessment**: Is the newly added knowledge accurate? Are decay parameters appropriate?
5. **Efficiency comparison**: For repeated tasks, was the response faster? Did confidence scoring avoid unnecessary re-verification?

## Summary Statistics

| Round | Tasks | Focus | Key Decay Behavior |
|-------|-------|-------|--------------------|
| R1 | 5 | Structure Exploration | schema (lambda=0.003) written; tool_experience reused from v1 |
| R2 | 6 | Data Queries | query_pattern stored; data_snapshot rejected |
| R3 | 5 | Business Rules | business_rule stored; Gate 2 self-correction on room_type |
| R4 | 5 | Complex Investigation | query_pattern stored; earlier knowledge TRUST-level |
| R5 | 4 | Repetition Verification | 0 new writes expected; all reuse at TRUST level |
| **Total** | **25** | | |
