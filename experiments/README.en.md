# Experiments — Empirical Validation

> Empirical validation of the Self-Evolving Skill design pattern. Each subdirectory is a complete experiment, testing the real-world effectiveness of the Five-Gate Governance Protocol across different databases and domains.

## Experiment Overview

| # | Experiment | Target Domain | Database Scale | Skill | Rounds | Status | Key Findings |
|---|-----------|---------------|---------------|-------|--------|--------|-------------|
| 01 | [nan-platform](01-nan-platform/) | Smart building management (智能楼宇管理) | MySQL · 29 tables · 590 MB | db-investigator | 5 | ✅ Complete | Rejection rate 63.6%, incremental convergence +75→+1 |
| 02 | [telecom-billing](02-telecom-billing/) | Telecom billing (desensitized) | MySQL · Large | db-investigator | - | 🔧 In progress | Cross-domain reproducibility validation |

## Standard Structure per Experiment

```
NN-experiment-name/
├── README.md              ← Experiment overview card (start here)
├── 00-baseline.md         ← Baseline snapshot: Skill state on first contact with the database
├── 01-task-set.md         ← Task set: test tasks organized by round
├── 02-evolution-log.md    ← Evolution log: Five-Gate decisions per round (core data)
├── 03-quality-audit.md    ← Quality audit: rejection rate, accuracy, bloat, and other metrics
└── snapshots/             ← Full snapshots of references/ after each round
    ├── R0-baseline/       ← Initial template state
    ├── R1-xxx/            ← State after Round 1
    └── ...                ← Use diff tools to compare any two rounds
```

**Reading guide**: Start with the experiment README for conclusions, then follow the 00→01→02→03 sequence for details. Use `snapshots/` with a diff tool to visually inspect incremental knowledge changes per round.

## How to Add a New Experiment

1. Copy `examples/db-investigator/` to `.claude/skills/db-investigator/` (or the corresponding Skill)
2. Configure the database connection and execute the task set
3. Create an `NN-short-name/` directory under `experiments/`, following the standard structure
4. Update the overview table in this file
