# 硬反馈自动化设计

> Self-Evolving Skill 设计文档
> 状态：方案分析中（三方案展开，待锁定）
> 前置依赖：`bayesian-feedback-design.md`（反馈信号定义）、`computation-layer-design.md`（CLI 架构）

---

## 1. 问题陈述

### 1.1 当前流程

```
LLM 读取知识条目（如 schema_map.md:7 "t_room.building_id → t_building.id"）
    ↓
LLM 据此编写 SQL（SELECT r.*, b.name FROM t_room r JOIN t_building b ON r.building_id = b.id）
    ↓
LLM 调用 db_query.py 执行 SQL → 得到结果
    ↓
【缺口在这里】
    ↓
LLM 应该运行: decay_engine.py feedback --file schema_map.md --line 7 --result success
```

### 1.2 缺口分析

步骤 3→4 之间存在三个认知负担：

| # | 负担 | 说明 |
|---|------|------|
| 1 | **记住去做** | LLM 在解决复杂问题时专注于业务逻辑，可能忘记 bookkeeping |
| 2 | **记住用了哪条** | 一次调查可能读了多条知识，SQL 只用了其中部分 |
| 3 | **正确判定结果** | 有些情况不明确：查询成功但返回空行，算 success 还是 failure？ |

### 1.3 v3 实验观察

v3 中反馈记录执行正确，但有前提：
- 实验协议是结构化的（每轮结束后统一回顾）
- 操作者有明确的"反馈"意识

**真实日常使用场景的风险**：多步调查中，LLM 专注于链式推理，可能跳过 feedback。特别是隐式使用知识的情况——LLM 内化了 references/ 的内容但不自觉地"引用"特定条目。

### 1.4 目标

降低反馈遗漏率，但不引入过度复杂的机制。**权衡**：自动化程度越高，机制越复杂，维护成本越大。

---

## 2. 三个方案

### 方案 A：引用模式（纯指令，零代码）

**核心思路**：在 SKILL.md 中建立"引用-反馈"范式，让 LLM 在使用知识前显式声明引用，使用后统一反馈。

**SKILL.md 指令增强**：

```
Knowledge Citation Protocol:
  Before executing SQL that uses knowledge from references/:
    1. Note which entries you are relying on (file:line)
    2. Execute the query
    3. Immediately after result, run feedback for each cited entry

  Pattern:
    # Using: schema_map.md:7 (t_room.building_id → t_building)
    python $S/db_query.py --sql "SELECT ... JOIN t_building ..."
    # Result: success (42 rows) → feedback
    python $S/decay_engine.py feedback --file schema_map.md --line 7 --result success
```

**优点**：

| 优点 | 说明 |
|------|------|
| 零代码改动 | 只改 SKILL.md |
| 立即可用 | 下一次对话就生效 |
| 灵活性最高 | LLM 自行判断哪些知识被使用，覆盖所有场景（硬/软信号） |

**缺点**：

| 缺点 | 说明 |
|------|------|
| 依赖指令遵循率 | LLM 可能在复杂调查中忘记引用/反馈 |
| 隐式引用无法捕获 | LLM 内化了知识但不显式引用时，反馈不会发生 |
| 不可验证 | 没有机制检测"LLM 用了知识但没反馈" |

**适用场景**：信任 LLM 的指令遵循能力，接受偶尔遗漏。

---

### 方案 B：输出信号增强（小幅代码改动）

**核心思路**：改进 db_query.py 的输出格式，在结果末尾追加机器可解析的状态行，降低 LLM 判断 success/failure 的认知负担。

**db_query.py 输出变更**：

当前输出：
```
[nan_platform] 42 row(s) total, showing 42:

id | name | building_id
---+------+------------
1  | 101  | 5
...
```

增强后：在末尾追加一行状态摘要：
```
...
[QUERY_OK] rows=42 tables=t_room,t_building
```

失败时：
```
Error: (1054, "Unknown column 'foo' in 'field list'")
[QUERY_FAIL] error=1054 message=Unknown column 'foo'
```

无结果时：
```
[nan_platform] No results.
[QUERY_OK] rows=0
```

**这条状态行解决了什么**：
- LLM 不需要从自由文本中推断成功/失败，有明确标记
- `tables=` 字段提示了涉及的表名，辅助 LLM 关联知识条目
- 异常退出（sys.exit(1)）不会产生状态行，这本身就是失败信号

**优点**：

| 优点 | 说明 |
|------|------|
| 降低判断门槛 | success/failure 有明确标记 |
| tables 辅助关联 | LLM 更容易回溯"这个 SQL 用了哪条知识" |
| 改动极小 | db_query.py 加 ~10 行输出代码 |
| 向后兼容 | 现有使用方式不受影响 |

**缺点**：

| 缺点 | 说明 |
|------|------|
| 不解决"记住去做" | LLM 仍需主动运行 feedback |
| 表名提取有限 | SQL 解析器复杂，简单正则只能提取部分表名 |
| 只覆盖 db_query.py | fetch_structure.py 等其他工具不受影响 |

**适用场景**：作为方案 A 的补充，降低判断难度但不单独解决遗漏。

---

### 方案 C：引用-执行-反馈管线（集成机制）

**核心思路**：在 db_query.py 调用时传入知识引用，SQL 执行后自动触发 feedback，将"执行"和"反馈"合为一步。

**两种实现路径**：

**C1: db_query.py 增加 --cite 参数**

```bash
python $S/db_query.py --sql "SELECT ..." --database nan_platform \
  --cite schema_map.md:7 --cite business_rules.md:3
```

db_query.py 内部：
1. 正常执行 SQL
2. 根据执行结果（成功/失败），自动调用 `decay_engine.py feedback`
3. 输出正常查询结果 + 反馈确认行

```
[nan_platform] 42 row(s) total, showing 42:
...
[FEEDBACK] schema_map.md:7 → success (α+1)
[FEEDBACK] business_rules.md:3 → success (α+1)
```

**C2: 新建 wrapper 命令 `decay_engine.py query`**

```bash
python $S/decay_engine.py query \
  --sql "SELECT ..." --database nan_platform \
  --cite schema_map.md:7
```

decay_engine.py 内部组合调用 db_query + feedback。

**优点**：

| 优点 | 说明 |
|------|------|
| 真正自动化 | 反馈不依赖 LLM 记忆，执行即反馈 |
| 引用关系可追溯 | --cite 参数显式记录"哪个 SQL 用了哪条知识" |
| 不可遗忘 | 只要 LLM 用 --cite 调用，反馈必然发生 |

**缺点**：

| 缺点 | 说明 |
|------|------|
| 复杂度显著增加 | db_query.py 或 decay_engine.py 要理解对方的职责 |
| 违反工具独立原则 | 当前架构设计约束：工具间不直接调用（§5.2 computation-layer-design.md） |
| --cite 仍依赖 LLM | LLM 要正确传入 --cite 参数，遗忘 --cite ≈ 遗忘 feedback |
| 只覆盖 SQL 硬信号 | 软信号（Gate 2 纠正、枚举查询）无法走这条管线 |
| 失败判定简化过度 | SQL 报错 ≠ 知识错误（可能是 SQL 写错了），自动 feedback failure 可能误判 |

**关键缺陷深挖**：

方案 C 看似"最自动"，但有一个根本矛盾：**如果 LLM 能记住传 --cite 参数，那它也能记住运行 feedback 命令**。自动化的收益建立在"LLM 会传 --cite"这个假设上，而这个假设和"LLM 会运行 feedback"在认知负担上几乎等价。

唯一的额外收益是"不用判断 success/failure"——但这引入了误判风险：SQL 报错未必是知识错误。

---

## 3. 方案对比

| 维度 | A 引用模式 | B 输出增强 | C 集成管线 |
|------|-----------|-----------|-----------|
| **代码改动** | 零 | ~10 行 | ~80-120 行 |
| **遗漏风险** | 高（纯靠指令） | 高（同 A） | 中（仍依赖 --cite） |
| **误判风险** | 低（LLM 判断） | 低（LLM 判断） | 高（自动判定可能误判） |
| **覆盖范围** | 全（硬+软信号） | 仅降低硬信号判断难度 | 仅硬信号 SQL 子集 |
| **架构一致性** | 完全一致 | 一致 | **违反工具独立原则** |
| **维护成本** | 零 | 极低 | 中等 |
| **可渐进实施** | 是 | 是 | 否（需改架构） |

---

## 4. 分析结论

### 4.1 方案 C 的否决理由

方案 C 收益看似最大，但存在三个结构性问题：

1. **违反工具独立原则**：`computation-layer-design.md` §5.2 明确约定工具间不直接调用，编排由 SKILL.md 驱动。C 方案让 db_query 调用 decay_engine（或反之），破坏了这一设计约束。
2. **自动化悖论**：LLM 记住传 --cite ≈ LLM 记住运行 feedback，核心遗漏问题并未真正解决。
3. **误判风险**：SQL 执行失败不等于知识错误（可能是 SQL 语法问题），自动触发 β+1 会污染反馈数据。

**结论：排除方案 C。**

### 4.2 A+B 组合方案

方案 A 和 B 不是互斥的，而是互补的：

- **A 解决"流程"**：建立引用-反馈范式，让 LLM 形成习惯
- **B 解决"判断"**：让结果判定从"阅读理解"降低为"读标记"

组合后的工作流：

```
1. LLM 读取知识，声明引用（A 的引用模式）
2. LLM 运行 db_query.py，得到结果 + [QUERY_OK/FAIL] 标记（B 的输出增强）
3. LLM 根据标记运行 feedback（A 的反馈步骤，但判断更简单）
```

---

## 5. 开放问题

以下问题需要在锁定方案前讨论确认：

### Q1: 方案 B 的 tables 提取如何实现？

SQL 中表名的提取有多种方式：
- **正则简单提取**：`FROM <table>` 和 `JOIN <table>` — 覆盖 80% 场景
- **SQL 解析库**：sqlparse — 更准确但增加依赖
- **不提取**：只输出 `[QUERY_OK] rows=N`，表名关联完全由 LLM 做

倾向：正则简单提取。理由：表名是辅助信息，不是关键依赖，80% 覆盖率够用。如果提取错了，LLM 自己知道真实的表名。

### Q2: 方案 A 的引用模式是否可能被 LLM 忽略？

引用模式是否会增加 SKILL.md 的复杂度导致遵循率下降？需要在 SKILL.md 指令设计时注意：
- 引用步骤必须简短（不能变成冗长的 checklist）
- 只在"使用了 references/ 中的知识"时才需要引用
- 未引用时不需要反馈（而不是"每次 SQL 都要反馈"）

### Q3: 轮次结束统一反馈 vs 即时反馈？

`bayesian-feedback-design.md` §6.2 原设计是"轮次结束时批量反馈"。但实际操作中即时反馈更自然（SQL 刚跑完就反馈），v3 也是即时反馈。

两种方式各有优劣：
- **即时反馈**：不会忘，但在一轮中多次用同一知识时会多次写文件
- **轮次结束批量**：减少文件 I/O，但容易忘

倾向：保持即时反馈（v3 已验证可行），但不强制。SKILL.md 指令表述为"在操作之后尽快记录反馈"。

### Q4: fetch_structure.py 的反馈如何处理？

方案 B 只改 db_query.py。但硬信号定义中也包括"结构查询比对"（fetch_structure.py）。是否需要同步增强 fetch_structure.py？

倾向：暂不改。理由：fetch_structure.py 用于验证/查看结构，其输出天然容易判断（DDL 能看出来列名是否存在），LLM 判断不困难。

---

## 6. 待锁定决策

| # | 决策项 | 候选 | 当前倾向 | 状态 |
|---|--------|------|---------|------|
| D1 | 总体方案选择 | A / B / C / A+B | **A+B 组合** | 待确认 |
| D2 | tables 提取方式 | 正则 / sqlparse / 不提取 | **正则简单提取** | 待确认 |
| D3 | 反馈时机 | 即时 / 轮次结束 / 不强制 | **即时，不强制** | 待确认 |
| D4 | fetch_structure.py | 同步改 / 暂不改 | **暂不改** | 待确认 |

---

*创建日期：2026-03-15*
*关联文档：`bayesian-feedback-design.md`（反馈信号定义）、`computation-layer-design.md`（工具独立原则 §5.2）*
