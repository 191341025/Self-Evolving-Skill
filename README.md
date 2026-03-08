<div align="center">

# Self-Evolving Skill Pattern

**English** | **[中文](README.zh.md)**

*A design pattern for Claude Code Skills that improve through use —*
*growing more accurate and efficient over time, without bloating.*

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-lightgrey.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill_Pattern-blue.svg)](https://docs.anthropic.com/en/docs/claude-code)
[![Paper](https://img.shields.io/badge/arXiv-2507.21046v4-b31b1b.svg)](https://arxiv.org/abs/2507.21046)

</div>

> [!NOTE]
> **Academic positioning:** This pattern corresponds to *Inter-test-time Context Evolution with Text-Feedback Governance* in the self-evolving agent literature. See Gao et al. (2026) "A Survey of Self-Evolving Agents."

---

## The Problem

Traditional Skills are static — an author packages them once, users invoke them repeatedly, and knowledge never grows.

But in domains like database investigation, codebase analysis, and business system integration, **an AI continuously discovers valuable domain knowledge during use** — table relationships, query patterns, business rules, data characteristics. Without a way to persist this knowledge, every new session starts from zero, wasting both effort and context window.

---

## Quick Start

**Is this pattern right for your use case?** Ask two questions:
1. Will domain knowledge grow through use?
2. Does that growth have a natural ceiling?

If both answers are yes, this pattern fits.

```
skill-name/
├── SKILL.md                        # Trigger conditions + governance protocol
├── scripts/                        # Execution tools
└── references/                     # Living knowledge base (AI-maintained)
    ├── _index.md                   # Routing table (<40 lines)
    ├── schema_map.md               # Structural knowledge
    ├── query_patterns.md           # Reusable query templates
    ├── business_rules.md           # Confirmed business logic
    └── investigation_flows.md      # Multi-step reusable workflows
```

---

## The Five-Gate Governance Protocol

This is the core of the pattern. It prevents the knowledge base from degrading into noise.

```
Gate 1 — VALUE
  Q: Can this knowledge be reused across sessions?
  → One-time result (e.g., "query returned 42 rows at 3pm") → REJECT
  → Reusable pattern or stable fact → PASS

Gate 2 — ALIGNMENT
  Q: Does this contradict existing knowledge?
  → Contradiction found → CORRECT the existing entry (don't append)
  → Consistent → PASS

Gate 3 — REDUNDANCY
  Q: Does this already exist, possibly worded differently?
  → Exists → MERGE into existing entry, or skip
  → Doesn't exist → PASS

Gate 4 — FRESHNESS
  Q: Is this time-sensitive data?
  → Yes → Tag with date (YYYY-MM-DD); future sessions can identify and clean stale data
  → No → Store as stable fact → PASS

Gate 5 — PLACEMENT
  Q: Which file does this belong in? Which memory layer?
  → Existing topic → Add to that file
  → New topic → Only create a new file if 3+ related entries exist; update _index.md
```

**The most common outcome of the Five Gates is: do nothing.** Most interactions don't produce knowledge worth storing. The protocol's primary job is to reject, not to accept.

### Governance Capabilities

| Capability | Mechanism |
|------------|-----------|
| Add knowledge | Must pass all five gates |
| Correct errors | Gate 2 detects contradictions; fix in place |
| Deduplicate | Gate 3 merges rather than appends |
| Expire stale data | Gate 4 date-tags; sessions identify and clean outdated entries |
| Maintain structure | Gate 5 + scaling rules control file granularity |

---

## Architecture

### Three-Level Loading

| Level | Loaded when | Content | Change frequency |
|-------|-------------|---------|-----------------|
| Level 1: frontmatter | Always, in system prompt | "When to use this Skill, how to behave" | Rarely changes |
| Level 2: body | When Claude judges the task is relevant | "Which tools, how to govern knowledge" | Stable |
| Level 3: references/ | Claude navigates on demand | **Living domain knowledge** | Selective evolution |
| Level 3: scripts/ | Claude invokes on demand | Execution tools | Extend as needed |

**The key distinction:** A traditional Skill's Level 3 is static reference documentation. A Self-Evolving Skill's Level 3 is a living knowledge base, maintained by the AI under the governance protocol.

### Selective Injection via Routing Table

Knowledge is loaded by route, not in bulk:

```
Skill triggered
    ↓
Read _index.md (routing table, <40 lines, topic list + one-line summaries)
    ↓
Determine which topic files are relevant to the current conversation
    ↓
Load only 1–2 relevant topic files
    ↓
Irrelevant files are not loaded — context window preserved
```

**Why not load everything?** A Skill is a prompt injection layer — context window is a finite resource. When the knowledge base grows to 5 topic files at 50–80 lines each, bulk loading wastes 250–400 lines. The routing table keeps injection size under control regardless of how much the knowledge base grows.

### Scaling Rules

- Single topic file exceeds ~80 lines → split into sub-topics
- Total topic files exceed 8 → review for merge opportunities
- `_index.md` must stay under 40 lines (routing only, no detail)

---

## Memory Layer Model

Adapted from the hierarchical memory architecture described in Gao et al. (2026):

| Layer | What it stores | File | Example |
|-------|---------------|------|---------|
| **Structural knowledge** | Static relationships between tables, SPs, databases | `schema_map.md` | "orders.customer_id references customers.id" |
| **Business rules** | Stable rules confirmed through interaction | `business_rules.md` | "Skip if customer not found; don't create order" |
| **Query patterns** | Reusable single-step SQL templates | `query_patterns.md` | "Count orders grouped by status" |
| **Investigation flows** | Reusable multi-step investigation procedures | `investigation_flows.md` | "Debug duplicate orders: Step1 check customer → Step2 check dedup conditions → Step3 compare results" |

**Knowledge typically distills upward:** A successful investigation may first add to `schema_map.md` (new table relationship discovered), then `query_patterns.md` (effective query extracted), then `investigation_flows.md` (full procedure consolidated). But not every interaction completes the full chain — if you only learned a new field name, `schema_map.md` is enough.

---

## Tool Experience Accumulation

The survey describes three stages of tool evolution: creation → mastery → management/selection. This pattern does not pursue full tool evolution (it's not appropriate for Skills to automatically create or modify scripts), but it does support **lightweight accumulation of tool-use experience**:

- **Effective parameter combinations:** The best parameter settings for a given query script in specific scenarios
- **Boundary conditions:** Known pitfalls and caveats (e.g., "connection timeout requires reconnect")
- **Composition patterns:** Effective sequences for chaining multiple tools together

These experiences are recorded as annotations within `query_patterns.md` or `investigation_flows.md` — no separate file is created.

The goal is not to make tools evolve autonomously, but to make the AI more efficient next time it uses a tool — like a skilled mechanic knowing which wrench fits which bolt.

---

## Design Philosophy

### Three Principles

**1. Evolution is demand-driven, not self-initiated**

Every change must be triggered by real user interaction — business needs pull knowledge accumulation, not the mechanism itself pushing changes. A Skill doesn't go looking for things to learn. It waits for real business problems to drive its growth.

This is a deliberate divergence from academic systems like Voyager, which autonomously explore. Those systems operate at the model parameter level. At the Skill (prompt injection) level, evolution signals should come from real business scenarios, not artificially generated exploration tasks.

**2. Selective growth, not continuous growth**

Not every interaction should change anything. "Admission is harder than deletion" — each of the five gates asks "do you really need to add this?" The survey literature calls this *Selective Evolution* vs. *Continuous Evolution*. A stable, high-quality rule beats ten vague notes.

**3. Maturity means stability**

A sufficiently mature Skill that stops growing is healthy — it's the intended end state, not a failure. When domain knowledge covers 90%+ of everyday scenarios, the Skill should converge. New growth is only triggered when the business itself changes (new tables, new rules, new processes).

This directly addresses the stability-plasticity dilemma described in the literature: excessive plasticity (constant change) causes catastrophic forgetting; timely stability is the mark of a mature system.

### Positioning Against the Academic Framework

From Gao et al. (2026)'s four-dimensional classification:

| Dimension | Full spectrum (paper) | This pattern's position | Design rationale |
|-----------|-----------------------|------------------------|-----------------|
| **What** evolves | Model weights / context / tools / architecture | **Context (memory + prompts)** + lightweight tool experience | Skills cannot modify model weights or architecture; context is the only persistable evolution site |
| **When** to evolve | Intra-test-time / Inter-test-time | **Inter-test-time** (cross-session) | Knowledge persists in references/ and is reused across sessions |
| **How** to evolve | Reward-driven / imitation learning / population evolution | **Text-feedback + Five-Gate governance** | AI judgment as "reward signal"; Five Gates as governance constraint |
| **Where** to evolve | General / specialized domains | **Specialized domains** (e.g., database investigation) | Domains where knowledge grows through use |

**Intentional non-goals:**
- No model weight modification — not possible or necessary at the Skill layer
- No architecture search — Skill structure is stable; only knowledge content changes
- No autonomous exploration — evolution is driven by real interaction, not self-generated tasks
- No perpetual growth — convergence to stability is the goal, not a problem

---

## Misevolution Protection

The survey literature introduces *Misevolution* — quality degradation during self-evolution. In the Skill context:

| Risk | Manifestation | Protection |
|------|---------------|------------|
| Knowledge pollution | Incorrect rules written in, causing downstream errors | Gate 2 (ALIGNMENT) + user confirmation for critical business rules |
| Information bloat | Low-value knowledge accumulates, burying important rules | Gate 1 (VALUE) + Gate 3 (REDUNDANCY) + scaling rules |
| Stale data | Deprecated table structures or SPs remain in knowledge base | Gate 4 (FRESHNESS) + date tagging + proactive review on business changes |
| Instruction conflict | SKILL.md instructions contradict references/ knowledge | SKILL.md changes rarely; references/ isolated via routing |

**The fundamental safety advantage:** A Self-Evolving Skill operates entirely at the context layer. It does not modify model parameters or system architecture. Even if the knowledge base develops an error, the worst case is "one bad reference fact" — not "irreversible behavioral change in the model." This is a natural safety advantage over model-level self-evolution.

---

## Maturity Signals

No KPI-style metrics are needed. Watch for these qualitative signals:

| Signal | Meaning |
|--------|---------|
| Most database questions can be answered without consulting references/ | Knowledge has been internalized into conversational capability |
| Five Gates repeatedly return "do nothing" | Knowledge base covers common scenarios |
| `_index.md` topic list has stabilized | Domain structure has converged |
| New knowledge is mostly Gate 4 freshness updates, not new facts | Framework is stable; only data is refreshing |

### Maturity Stages

```
Nascent:  references/ nearly empty; most interactions produce new knowledge
    ↓
Growing:  Core structure and rules established; new additions slowing
    ↓
Mature:   Knowledge base stable; updates only on business changes
    ↓
Business change triggers: new systems, schema refactors → partial return to Growing
```

---

## Comparison with Traditional Skills

| | Traditional Skill | Self-Evolving Skill |
|--|------------------|-------------------|
| **Knowledge source** | Author-defined at creation | Predefined + accumulated through use |
| **Lifecycle** | Fixed after creation | Selective evolution → convergence to maturity |
| **Quality control** | Manual author maintenance | Five-Gate protocol (self-governing) |
| **Context efficiency** | Full body injection | Routing table + selective injection |
| **Cross-project reuse** | Copy entire Skill | Copy Skill skeleton + clear references/; accumulate fresh in new project |
| **Cross-session continuity** | None | Knowledge persists in references/ |
| **End state** | Never changes | Stable (not changing = success) |

---

## When to Use (and When Not To)

**Use this pattern when:**
- Database investigation — table relationships and query patterns accumulate through use
- Codebase analysis — architectural understanding deepens over time
- Business system integration — business rules get confirmed through conversation
- Any domain where **knowledge grows through use and has a natural ceiling**

**Don't use this pattern when:**
- Pure tool Skills (e.g., a PDF reader — no domain knowledge to accumulate)
- Fully predetermined knowledge Skills (e.g., coding style guides — rules don't change through use)
- Unbounded knowledge growth scenarios (these require model-level evolution, not Skill-level)

---

## Reference Implementation

This repository includes a complete reference implementation: [`examples/db-investigator/`](examples/db-investigator/)

A Self-Evolving Skill for MySQL database investigation, demonstrating:

| Component | File | Description |
|-----------|------|-------------|
| Skill definition | [`SKILL.md`](examples/db-investigator/SKILL.md) | frontmatter (triggers) + body (tool selection, Five-Gate protocol, scaling rules) |
| Knowledge routing | [`references/_index.md`](examples/db-investigator/references/_index.md) | Routing table example |
| Domain knowledge | [`references/*.md`](examples/db-investigator/references/) | Four-layer memory model file examples (with template placeholders) |
| Execution tools | [`scripts/`](examples/db-investigator/scripts/) | Three read-only tools: data query, structure fetch, metadata index |
| Structure cache | [`db_schemas/`](examples/db-investigator/db_schemas/) | Offline cache directory for tool outputs |

> The references/ files contain template examples. In real use, the AI populates them with actual domain knowledge through the Five-Gate protocol during real interactions.

---

## Empirical Validation

We ran full evolution experiments on real databases to validate the design pattern.

**→ [View all experiment data](experiments/)**

| Experiment | Domain | Rounds | Key Findings |
|-----------|--------|--------|-------------|
| [#01 nan-platform](experiments/01-nan-platform/) | Smart Building Mgmt (29 tables) | 5 | 63.6% rejection rate, increments converge +75→+1, 2 Gate 2 self-corrections |

Each experiment includes full evolution logs, Five-Gate decision records, quality audits, and per-round knowledge snapshots — you can diff any two rounds to observe exactly how the Skill's knowledge grew.

---

## Implementation Checklist

```
1. Define domain boundaries
   Ask: Will knowledge grow through use? Does growth have a ceiling?
   If both yes → proceed.

2. Create directory structure
   skill-name/
   ├── SKILL.md
   ├── scripts/
   └── references/
       └── _index.md

3. Write SKILL.md
   - frontmatter: trigger conditions + behavioral guidelines
   - body: tool selection + Five-Gate governance protocol + scaling rules

4. Initialize references/
   - _index.md: empty routing table
   - 0–2 initial topic files (if domain knowledge is already known)

5. Begin using
   - AI discovers valuable knowledge through real interactions
   - Knowledge passes through Five Gates before being written
   - _index.md updated accordingly

6. Let it converge naturally
   - Knowledge grows selectively; Five Gates prevent bloat
   - Files split or merge when thresholds are reached
   - Mature Skill stabilizes; updates only when the business changes
```

---

## References

- Gao, H., Geng, J., et al. (2026). "A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve on the Path to Artificial Super Intelligence." *Transactions on Machine Learning Research*. arXiv:2507.21046v4. ([arXiv](https://arxiv.org/abs/2507.21046))
- This pattern primarily relates to Section 3.2 (Context Evolution: Memory + Prompt) and Section 4.2 (Inter-test-time Evolution) of the above survey.
- The Five-Gate protocol aligns with the memory management operations (ADD / MERGE / UPDATE / DELETE) described in Mem0, with a more systematic governance structure layered on top.
- The memory layer model is inspired by MUSE's hierarchical memory architecture (strategic / procedural / tool-use), adapted for the Skill context as a four-layer structure.

---

## Contributing

This pattern is derived from real-world use in telecom expense management (database investigation and billing audit scenarios). Feedback, case studies, and adaptations to other domains are welcome via Issues and PRs.

If you apply this pattern to a new domain, consider sharing:
- What domain you applied it to
- How long it took to reach the "Mature" stage
- Which of the Five Gates fired most frequently in your case

---

## License

This project is licensed under [CC BY-SA 4.0](LICENSE).

The Self-Evolving Skill design pattern — including the Five-Gate Governance Protocol, three-level progressive loading architecture, selective injection mechanism, memory layer model, and maturity stage framework — is an original creation by the author. The pattern was independently conceived and subsequently positioned against the self-evolving agent survey by Gao et al. (2026). That survey addresses self-evolution at the agent and model parameter level; this pattern's distinct contribution is applying self-evolution principles to the Skill layer (prompt injection layer), operating entirely within the context window without modifying model weights or system architecture.
