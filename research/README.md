# Research & Design Documents

本目录存放项目的设计文档、研究资料和思考笔记。

---

## design/ — 设计文档

### v2 核心设计

| 文件 | 状态 | 说明 |
|------|------|------|
| `knowledge-lifecycle-v2.md` | **设计草案** | 两阶段知识生命周期模型：Phase 1 准入（distill_score）+ Phase 2 保鲜（C(t) 衰减）；向量数据库存储；激活机制 |
| `implementation-plan-v2.md` | **计划草案** | 分 4 阶段实现路线：Phase 0 技术选型 → Phase 1 最小可用 → Phase 2 两阶段生命周期 → Phase 3 打磨调参 |

### 通用设计（v1/v2 共用）

| 文件 | 状态 | 说明 |
|------|------|------|
| `design-principles.md` | 已确认 | 核心设计原则：VPRM（规则优先，LLM 兜底）+ 三层表达优先级（公式 > 结构化 NL > NL） |
| `knowledge-taxonomy.md` | 定稿归档 | 高价值领域知识四类分类（结构性/行为性/异常性/演化性），Gate 1 VALUE 判定框架 |

### v1 已实现设计

| 文件 | 状态 | 说明 |
|------|------|------|
| `decay-model-notes.md` | 已实现 | 衰减公式 `C(t) = C0 × e^(-λ_eff × t)` 推导，贝叶斯扩展论证，数值验算 |
| `bayesian-feedback-design.md` | 已实现 | α/β 反馈信号来源、按知识类型的反馈分析、confirmed_at 更新策略 |
| `computation-layer-design.md` | 已实现 | 计算层三层架构：formulas → models → parser → CLI，Phase 5 扩展 |
| `cli-reference.md` | 已实现 | decay_engine.py 7 个子命令完整参考（init/scan/feedback/reset/inject/invalidate/search） |
| `formula-opportunity-analysis.md` | 已实现 | 7 个 LLM 判定点的公式化机会评估，全部已决策并实现 |
| `human-entry-points.md` | 已实现 | 人工注入（inject）+ 人工修正（invalidate）入口设计 |
| `auto-feedback-design.md` | 已实现 | 反馈机制优化：自然反馈 > 强制反馈，硬信号/软信号区分 |

---

## 顶层文档

| 文件 | 说明 |
|------|------|
| `HANDOFF-2026-03-21.md` | v1→v2 过渡设计讨论记录，5 个核心结论已吸收进 `knowledge-lifecycle-v2.md` |

---

## insights/ — 思考笔记

| 文件 | 说明 |
|------|------|
| `natural-feedback-and-llm-nature.md` | 自然反馈的第一性原理：顺应 LLM 认知特点设计，不强制像机器运行 |
| `exploration-memory-governance-draft.md` | 探索-记忆-治理：反馈多源汇聚、问题生命周期、流水线分工（待验证草稿） |

---

## external/ — 外部研究（参考用，非设计目标）

| 文件 | 说明 |
|------|------|
| `evomap-evolver-analysis.md` | EvoMap Evolver 架构分析：基因系统、胶囊生命周期、蒸馏机制 |
| `evomap-reward-analysis.md` | EvoMap Reward 机制分析：评分公式、探索模式、Hub 资产排名 |
