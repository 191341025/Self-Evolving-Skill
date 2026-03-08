# Experiments — 实证验证

> Self-Evolving Skill 设计模式的实证验证。每个子目录是一次完整实验，使用不同数据库/领域测试五道门治理协议的实际效果。

## 实验总览

| # | 实验 | 目标领域 | 数据库规模 | Skill | 轮次 | 状态 | 关键发现 |
|---|------|---------|-----------|-------|------|------|---------|
| 01 | [nan-platform](01-nan-platform/) | 智能楼宇管理 | MySQL · 29表 · 590MB | db-investigator | 5 | ✅ 已完成 | 拒绝率 63.6%，增量收敛 +75→+1 |
| 02 | [telecom-billing](02-telecom-billing/) | 电信计费（脱敏） | MySQL · 大型 | db-investigator | - | 🔧 准备中 | 跨领域可复现性验证 |

## 每个实验的标准结构

```
NN-experiment-name/
├── README.md              ← 实验概述卡片（从这里开始读）
├── 00-baseline.md         ← 零点快照：Skill 首次接触数据库时的状态
├── 01-task-set.md         ← 实验任务集：按轮次组织的测试任务
├── 02-evolution-log.md    ← 进化日志：每轮的五道门决策记录（核心数据）
├── 03-quality-audit.md    ← 质量审计：拒绝率/准确性/膨胀度等维度评估
└── snapshots/             ← 每轮结束后 references/ 的完整快照
    ├── R0-baseline/       ← 初始模板状态
    ├── R1-xxx/            ← Round 1 后的状态
    └── ...                ← 可用 diff 工具对比任意两轮的变化
```

**阅读建议**：先看实验 README 了解结论，再按 00→01→02→03 顺序深入细节。`snapshots/` 配合 diff 工具可以直观看到每轮知识的增量变化。

## 如何新增实验

1. 复制 `examples/db-investigator/` 到 `.claude/skills/db-investigator/`（或对应 Skill）
2. 配置数据库连接，执行任务集
3. 在 `experiments/` 下创建 `NN-short-name/` 目录，按标准结构记录
4. 更新本文件的总览表格
