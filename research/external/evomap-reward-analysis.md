# EvoMap Evolver Reward 机制分析

> 外部系统调研笔记
> 数据来源：D:\IdeaProjects\evolver 代码库（2026-03-17 快照）
> 目的：了解 EvoMap 的探索评分设计，借鉴反馈信号质量判定思路

---

## 1. 核心 Reward 计算

**位置**：`src/gep/solidify.js:1261`

基础分是二值分档，叠加连续微调：

| 场景 | 基础分 | 标签 |
|------|--------|------|
| 探索成功（三条件全过） | **0.85** | success |
| 稳定无错误（没出错也没突破） | 0.60 | stable_no_error |
| 普通失败 | 0.20 | error_persisted |
| 引入新错误 | 0.15 | new_error_appeared |
| 错误被清除 | 0.85 | error_cleared |

**成功的三个硬条件**（纯规则判定，全过才算成功）：

```
constraintCheck.ok === true     // 约束检查（blast radius / safety）
validation.ok === true          // 验证测试通过
protocolViolations.length === 0 // 零协议违规
```

---

## 2. 增强评分微调

**位置**：`src/gep/memoryGraph.js`，`inferOutcomeEnhanced` 函数

在基础分上叠加两个连续微调项：

**错误减少量调整**（±0.12）：
```javascript
delta = prevErrCount - curErrCount
score += Math.max(-0.12, Math.min(0.12, delta / 50));
```
减少 50 个错误 → +0.12，增加 50 个错误 → -0.12

**性能变化比调整**（±0.06）：
```javascript
ratio = (prevScan - curScan) / prevScan
score += Math.max(-0.06, Math.min(0.06, ratio));
```
性能翻倍 → +0.06

**评分维度总结**：全部是可量化硬指标，无 LLM 判断环节。

---

## 3. 探索机制（基因选择）

**位置**：`src/gep/selector.js:86-227`

**漂变强度公式**（种群遗传学）：
```javascript
driftIntensity = 1 / sqrt(effective_population_size)
```

**四种漂变模式**：

| 模式 | 说明 |
|------|------|
| `selection` | 纯最佳匹配选择 |
| `diversity_directed` | 针对能力缺口的定向探索 |
| `random_weighted` | 新颖度加权随机探索 |
| `memory_preferred` | 记忆图谱引导（用过去成功的方案做种子） |

**关键观察**：`memory_preferred` 模式用记忆引导"选哪个方案去变异"，但不引导"探索什么问题"。探索目标（report 中的"探索目标：未指定"）和记忆内容之间没有关联。

---

## 4. Hub 资产评分（外部知识复用）

**位置**：`src/gep/hubSearch.js:103-108`

多维排名公式：
```javascript
rank = confidence × min(max(success_streak, 1), MAX_STREAK_CAP) × (reputation / 100)
```

| 维度 | 范围 | 说明 |
|------|------|------|
| confidence | 0.0-1.0 | 历史成功概率 |
| success_streak | 1-MAX_CAP | 连续成功次数 |
| reputation | 0-100（基准50） | 社区声誉评分 |

入选阈值：rank ≥ 0.2

---

## 5. Hub 评审评级

**位置**：`src/gep/hubReview.js:61-70`

| 条件 | 星级 |
|------|------|
| score ≥ 0.85 | 5 星 |
| success 但 < 0.85 | 4 星 |
| 其他失败 | 2 星 |
| 约束违规 | 1 星 |

---

## 6. 发布阈值

```javascript
const minPublishScore = Number(process.env.EVOLVER_MIN_PUBLISH_SCORE) || 0.78;
```

score ≥ 0.78 才能发布为可复用 Capsule。相当于"不是所有探索结果都值得沉淀"——类似我们的 Gate 1 VALUE。

---

## 7. 五维人格参数

**位置**：`src/gep/personality.js`

| 参数 | 默认值 | 控制什么 |
|------|--------|---------|
| rigor | 0.70 | 协议遵循严格度 |
| creativity | 0.35 | 创新意愿 |
| verbosity | 0.25 | 解释详细度 |
| risk_tolerance | 0.40 | 探索激进度 |
| obedience | 0.85 | 指令遵循度 |

所有参数 clamped to [0, 1]。

---

## 8. 置信度衰减

Hub 资产的可信度使用**半衰期模型（30-45 天）**做时间加权。与我们的 `C(t) = C0 × e^(-λt)` 是同类思路，应用场景不同：

| | EvoMap | Self-Evolving Skill |
|--|--------|-------------------|
| 衰减对象 | Hub 资产的可信度 | 领域知识的置信度 |
| 半衰期 | 30-45 天 | 14-231 天（按类型分级） |
| 反馈机制 | success_streak（连续成功） | α/β 贝叶斯因子 |

---

## 9. 与我们系统的对比观察

| 维度 | EvoMap Evolver | Self-Evolving Skill |
|------|---------------|-------------------|
| **反馈信号来源** | 规则硬指标（约束/验证/错误数） | 规则硬指标 + LLM 软信号 |
| **评分方式** | 分档基础分 + 连续微调 | 贝叶斯 α/β 累积 |
| **探索** | 有（Exploration 模块，reward 驱动） | 无（demand-driven，不主动探索） |
| **治理** | 发布阈值 0.78（简单门槛） | 五道门协议（多维治理） |
| **知识从哪来** | 探索产生 + Hub 复用 | 对话中提炼 + 人工注入 |
| **成熟度信号** | evolution_saturation, stable_success_plateau | 五道门拒绝率 + 衰减扫描 |

**关键缺口观察**：EvoMap 的 Exploration 有"用什么方案探索"（memory_preferred），但没有"探索什么问题"（探索目标：未指定）。从记忆中提炼问题作为定向探索种子，是一个理论上可行（Active Learning / Curiosity-Driven Exploration）但他们尚未实现的方向。

---

## 10. 关键文件索引

| 文件 | 核心内容 |
|------|---------|
| `src/gep/solidify.js` | Outcome score 主计算（0.85/0.2 分档） |
| `src/gep/memoryGraph.js` | 增强评分（错误/性能微调）、记忆图谱推理 |
| `src/gep/hubSearch.js` | Hub 资产排名公式（confidence × streak × reputation） |
| `src/gep/hubReview.js` | 评审评级（1-5 星） |
| `src/gep/selector.js` | 基因选择 + 四种漂变模式 |
| `src/gep/personality.js` | 五维人格参数 |
| `src/gep/strategy.js` | 进化策略分配（repair/optimize/innovate） |

---

*分析日期：2026-03-17*
*数据来源：D:\IdeaProjects\evolver 代码库快照*
*关联文档：`evomap-evolver-analysis.md`（早期分析）*
