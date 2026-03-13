# 计算层架构设计：从 Prompt 到 Tool

> Self-Evolving Skill 设计文档
> 状态：设计草案，待评审
> 前置依赖：`bayesian-feedback-design.md`（反馈机制）、`decay-model-notes.md`（公式推导）

---

## 1. 问题陈述

### 1.1 当前设计的缺陷

当前所有计算逻辑（衰减公式、λ 查表、阈值判定、α/β 更新）都写在 SKILL.md 的指令集中，由 LLM 在推理时"心算"执行。

问题：
- **准确性差**：LLM 做指数运算不精确，尤其涉及 `e^(-0.003 × 0.75 × 100)` 这类多步浮点计算
- **上下文浪费**：SKILL.md 中 ~30 行专门描述公式、λ 表、阈值，这些内容 LLM 需要"理解"但不擅长"执行"
- **扩展性差**：未来公式会更复杂（嵌套、组合），全放进 prompt 会让指令集臃肿、遵循率下降
- **不可测试**：写在 prompt 里的计算逻辑无法做单元测试

### 1.2 核心设计原则

**LLM 做判断，Python 做计算。**

- Prompt 层（SKILL.md）：定义"何时调用"和"如何响应结果"
- 工具层（Python）：执行所有数学计算，返回清晰的结论
- LLM 不需要知道公式，只需要知道"运行这个工具，按输出行动"

---

## 2. 分层架构

```
┌──────────────────────────────────────────┐
│  第 3 层：CLI 命令（SKILL.md 直接调用）     │
│  decay_engine.py scan / feedback / ...    │
├──────────────────────────────────────────┤
│  第 2 层：组合模型（业务逻辑）              │
│  core/models.py                           │
│  confidence() = decay() × bayesian()      │
├──────────────────────────────────────────┤
│  第 1 层：原子公式（纯数学，无副作用）       │
│  core/formulas.py                         │
│  exponential_decay() / bayesian_factor()  │
├──────────────────────────────────────────┤
│  I/O 层：标签解析 + 文件读写               │
│  core/parser.py                           │
│  parse_decay_tags() / write_decay_tag()   │
└──────────────────────────────────────────┘
```

### 2.1 第 1 层：原子公式（core/formulas.py）

纯函数，无副作用，无 I/O。每个函数接收数值参数，返回数值结果。

设计约束：
- 每个公式独立可测试
- 公式之间无直接依赖（组合在第 2 层完成）
- 新公式直接追加，不修改已有公式

当前公式：
- `exponential_decay(lambda_val, t)` → `e^(-λt)`
- `bayesian_factor(alpha, beta)` → `(β+1)/(α+1)`
- `effective_lambda(lambda_base, alpha, beta)` → `λ_base × bayesian_factor`

预留扩展：
- 未来的权重公式、评分公式、排序公式等，都在此层定义

### 2.2 第 2 层：组合模型（core/models.py）

将原子公式组装成业务模型。这一层知道"业务含义"但不知道"数据从哪来"。

当前模型：
- `confidence(type, confirmed_date, alpha, beta)` → 计算置信度 C(t)，返回数值
- `classify_confidence(c_value)` → 根据阈值返回 TRUST / VERIFY / REVALIDATE

预留扩展：
- 未来可能有 `relevance_score(confidence, last_used, usage_count)` 等组合模型
- 模型 A 的输出可以作为模型 B 的输入，形成公式链

### 2.3 I/O 层（core/parser.py）

负责 markdown 文件中 decay 标签的解析和写入。

- `parse_decay_tags(file_path)` → 从 .md 文件提取所有 decay 标签及其位置
- `write_decay_tag(file_path, line, updates)` → 更新指定位置的标签字段
- `scan_references(dir_path)` → 扫描整个 references/ 目录

### 2.4 第 3 层：CLI 命令（decay_engine.py）

面向 SKILL.md 的调用接口。解析命令行参数，调用 core，格式化输出。

```bash
# 扫描所有知识条目，返回置信度级别
python decay_engine.py scan [--path references/] [--file schema_map.md]

# 输出示例：
# [TRUST]      schema_map.md:7       C=0.951  schema      α=3 β=0  17d
# [VERIFY]     query_patterns.md:33  C=0.723  tool_exp    α=1 β=1  65d
# [REVALIDATE] business_rules.md:8   C=0.412  biz_rule    α=0 β=2  112d

# 记录反馈（成功/失败）
python decay_engine.py feedback --file schema_map.md --line 7 --result success
python decay_engine.py feedback --file schema_map.md --line 7 --result failure

# 重置（REVALIDATE 通过后）
python decay_engine.py reset --file schema_map.md --line 7
```

---

## 3. 文件结构

```
scripts/
├── db_query.py              ← 已有：SQL 执行
├── fetch_structure.py       ← 已有：结构获取
├── fetch_index.py           ← 已有：元数据索引
├── decay_engine.py          ← 新增：CLI 入口（第 3 层）
└── core/                    ← 新增：计算内核
    ├── __init__.py
    ├── formulas.py           ← 第 1 层：原子公式
    ├── models.py             ← 第 2 层：组合模型
    └── parser.py             ← I/O 层：标签解析
```

---

## 4. SKILL.md 的瘦身效果

### 4.1 当前 Gate 4 描述（~30 行）

包含：完整公式、λ 表（6 行）、阈值定义、三级响应规则、计算示例

### 4.2 瘦身后 Gate 4 描述（~10 行）

```
Gate 4 — FRESHNESS (write): Assign decay metadata
  → Classify type: schema | business_rule | tool_experience |
                   query_pattern | data_range | data_snapshot
  → Write: <!-- decay: type=<type> confirmed=<YYYY-MM-DD> C0=1.0 alpha=0 beta=0 -->

Gate 4 — FRESHNESS (read): On-demand confidence scan
  → Run: python $S/decay_engine.py scan --file <topic_file>
  → TRUST: use directly, no mention of confidence
  → VERIFY: use but flag for opportunistic verification
  → REVALIDATE: verify with tools BEFORE using

Gate 4 — FRESHNESS (feedback): After operations using knowledge
  → Success: python $S/decay_engine.py feedback --file <f> --line <n> --result success
  → Failure: python $S/decay_engine.py feedback --file <f> --line <n> --result failure
```

公式细节、λ 表、阈值数值全部从 SKILL.md 移到 Python 代码中。LLM 不需要知道 0.003 还是 0.008。

---

## 5. 设计约束

### 5.1 公式的可组合性

未来新增的公式遵循同一模式：
1. 在 `formulas.py` 定义原子公式
2. 在 `models.py` 组合成业务模型
3. 在 `decay_engine.py` 暴露为 CLI 子命令
4. 在 SKILL.md 中只写调用方式和响应规则

### 5.2 工具间的关系

```
decay_engine.py          独立运行，不依赖其他工具
db_query.py              独立运行
fetch_structure.py       独立运行
fetch_index.py           独立运行
```

工具之间不直接调用。编排由 SKILL.md 指令驱动 LLM 完成：
- LLM 运行 `decay_engine.py scan` → 发现 REVALIDATE
- LLM 运行 `fetch_structure.py` → 获取最新结构
- LLM 对比结果 → 运行 `decay_engine.py feedback/reset`

### 5.3 配置集中

λ 值表、阈值等参数集中在 `core/models.py` 或独立的配置常量中，不散落在多处。

---

## 6. 实施路径

### Phase 1：核心计算（最小可行）
- 实现 core/formulas.py（exponential_decay, bayesian_factor）
- 实现 core/parser.py（parse_decay_tags）
- 实现 core/models.py（confidence, classify_confidence）
- 实现 decay_engine.py scan 子命令
- 单元测试覆盖所有公式
- SKILL.md Gate 4 read 路径切换到工具调用

### Phase 2：反馈写入
- 实现 decay_engine.py feedback 子命令
- 实现 core/parser.py 的写入功能
- 实现 decay_engine.py reset 子命令
- SKILL.md Gate 4 feedback 路径接入

### Phase 3：SKILL.md 全面瘦身
- 移除 SKILL.md 中所有公式描述和 λ 表
- 移除 DECAY_GOVERNANCE.md 中与 SKILL.md 重复的部分
- 验证瘦身后指令遵循率

---

## 7. 已决定的问题

1. **DECAY_GOVERNANCE.md**：已删除。设计哲学保留在 `research/design/` 文档中，实施细节全部在代码中。

2. **scan 的触发时机**：**按需 scan（方案 A）**。LLM 通过 `_index.md` 路由确定需要读哪个文件后，先 scan 该文件再读取。不做全量 scan，与选择性加载协议一致，上下文零浪费。

---

*草案日期：2026-03-14*
*关联文档：`bayesian-feedback-design.md`（反馈来源）、`decay-model-notes.md`（公式推导）*
