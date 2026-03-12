# 实验任务集 (v2)

> 与 v1 相同的 25 个任务，使用升级版 Gate 4 置信度衰减模型重新执行。
> 标注说明哪些知识从 v1 继承、哪些是全新获取。
>
> 设计原则：覆盖从简单查询到复杂多步调查的完整难度梯度，每个任务都可能触发带置信度评分的门控决策。
> 任务按轮次执行，每轮结束后检查 references/ 的变化。

## 起始状态

| 组件 | 状态 |
|------|------|
| schema_map | 重置为模板（空） |
| business_rules | 重置为模板（空） |
| query_patterns | 重置为模板（空） |
| investigation_flows | 重置为模板（空） |
| tool_experience | **从 v1 继承 3 条笔记**：shell 编码问题、MySQL 中 `!=` vs `<>`、fetch_structure.py 用法 |
| _index.md | 重置为模板（含新增 Min Confidence 列） |

---

## Round 1：结构探索（让 Skill 认识数据库）

**目标**：从零重建 schema 知识；tool_experience 复用应消除工具摩擦。

| # | 任务 | 方法 | 预期触发的知识层 | v1 复用 |
|---|------|------|----------------|---------|
| 1.1 | 这个数据库有哪些表？分别是什么业务含义？ | fetch_index.py | schema_map | 无 -- 全新发现 |
| 1.2 | 核心表的结构是什么？显示主要表的字段、类型和键。 | fetch_structure.py | schema_map | tool_experience 复用（fetch_structure.py 用法笔记） |
| 1.3 | 实体关系是什么（楼栋→楼层→房间，员工→入驻记录）？ | SQL 探索 | schema_map | 无 -- 全新发现 |
| 1.4 | 验证 JOIN 路径：emp_record 能关联到 employee 吗？关键链是什么？ | SQL 验证 | schema_map | 无 -- 全新发现 |
| 1.5 | 字典系统是怎么设计的？列出所有字典类型和值。 | SQL 探索 | schema_map + business_rules | 无 -- 全新发现 |

**Round 1 衰减说明**：
- 所有 schema 知识以 λ=0.003（半衰期 231 天）写入 -- 高度持久
- 字典枚举值以 business_rule（λ=0.008）写入

---

## Round 2：数据查询（单步查询）

**目标**：构建查询模板；因 data_snapshot 衰减，预期拒绝率高于 v1。

| # | 任务 | 预期触发的知识层 | 置信度类型 | v1 复用 |
|---|------|----------------|-----------|---------|
| 2.1 | 目前有多少栋楼？各是什么类型？ | query_patterns | data_range | 无 |
| 2.2 | 各楼栋分别有多少房间？入住率如何？ | query_patterns | query_pattern + data_snapshot | 无 |
| 2.3 | 在住员工的性别和年龄分布是什么样的？ | query_patterns | query_pattern + data_snapshot | 无 |
| 2.4 | 最近的进出记录量趋势如何？ | query_patterns | query_pattern + data_snapshot | 无 |
| 2.5 | 设备状态分布是什么？有多少故障设备？ | query_patterns | query_pattern + data_snapshot | 无 |
| 2.6 | 哪个楼栋的设备密度最高？ | query_patterns | query_pattern + data_range | 无 |

**Round 2 衰减说明**：
- SQL 模板模式（λ=0.015）被存储；具体计数和分布（λ=0.050）被拒绝
- 这是与 v1 的关键差异：v1 存储了部分 data_snapshot；v2 通过置信度衰减拒绝它们

---

## Round 3：业务规则（需要推理）

**目标**：发现和验证业务规则；预期 Gate 2 自我纠错。

| # | 任务 | 预期触发的知识层 | 置信度类型 | v1 复用 |
|---|------|----------------|-----------|---------|
| 3.1 | 员工类型分布是什么？每种类型代表什么？ | business_rules | business_rule | 无 |
| 3.2 | settle_status 的生命周期是什么？有哪些状态和有效转换？ | business_rules | business_rule | 无 |
| 3.3 | room_type 和房间容量之间是什么关系？ | business_rules | business_rule | 无 -- 此处预期 Gate 2 纠错 |
| 3.4 | 设备品牌分布是什么？系统中有多少品牌？ | business_rules + query_patterns | business_rule + data_snapshot | 无 |
| 3.5 | 公司类型和楼栋租金之间是什么关系？ | business_rules | business_rule + data_range | 无 |

**Round 3 衰减说明**：
- 业务规则以 λ=0.008（半衰期 87 天）存储
- Gate 2 对 room_type 自我纠错：数据验证后修正初始假设
- data_snapshot 组成部分（品牌数量、租金数据）通过衰减模型被拒绝

---

## Round 4：复杂多步调查

**目标**：构建调查工作流；测试基于置信度的早期 schema 知识信任。

| # | 任务 | 预期触发的知识层 | 置信度类型 | v1 复用 |
|---|------|----------------|-----------|---------|
| 4.1 | 入住率最高的楼栋里有哪些公司？交叉引用公司、入驻、楼栋表。 | investigation_flows | query_pattern | Schema 知识被信任 (C≥0.95) |
| 4.2 | 找出身份证在 3 个月内到期的员工，他们的入驻状态如何？ | investigation_flows | query_pattern | Schema 知识被信任 |
| 4.3 | 进出频率最高的前 10 名员工是谁？构建他们的档案。 | investigation_flows | query_pattern | Schema + query_patterns 被信任 |
| 4.4 | 找出已注销但之后仍有进出记录的员工。 | investigation_flows | query_pattern | Schema + business_rules 被信任 |
| 4.5 | 哪栋楼的设备故障率最高？按设备类型分析。 | investigation_flows | query_pattern | Schema + query_patterns 被信任 |

**Round 4 衰减说明**：
- 调查流程以 λ=0.015（半衰期 46 天）存储
- 所有早期 schema 条目 C≥0.95（仅 4 天，λ=0.003）-- TRUST 级别
- 调查中的具体结果计数被拒绝（data_snapshot，λ=0.050）

---

## Round 5：重复与进化验证

**目标**：验证 Skill 无需重新查询即可复用知识。全部 4 个任务是之前轮次的重复。

| # | 任务 | 重复来源 | 验证目标 | v1 复用 |
|---|------|---------|---------|---------|
| 5.1 | 各楼栋有多少入驻员工？ | R2.2 变体 | 是否复用 query_patterns 模板？置信度分数是否允许 TRUST？ | 模式应被信任 (C≥0.9) |
| 5.2 | 在住员工的性别比例是多少？ | R2.3 变体 | 是否跳过结构探索？schema 知识是否被信任？ | 模式应被信任 (C≥0.9) |
| 5.3 | 设备品牌分布是什么？ | R3.4 重复 | 是否复用 business_rules？data_snapshot 是否再次被拒绝？ | 规则被信任；快照再次被拒绝 |
| 5.4 | 最近的进出记录趋势如何？ | R2.4 重复 | 是否使用现有模式？与 Round 2 对比响应速度。 | 模式被信任；快照再次被拒绝 |

**Round 5 衰减说明**：
- 所有 query_pattern 条目（λ=0.015）仅 0-4 天 -- C≥0.94 -- TRUST 级别
- 所有 schema 条目为 TRUST 级别
- 预期：0 次结构查找，4/4 首次成功

---

## 每轮检查清单

每轮任务执行完毕后，记录以下内容到进化日志：

1. **references/ 变化 diff**：哪些文件被修改了？新增了什么内容？
2. **门控决策记录**：记录每次门控决策及置信度评分（尤其是拒绝和 VERIFY 级别的决策）
3. **置信度快照**：各知识类型当前的最小/最大/平均置信度
4. **质量评估**：新增的知识是否准确？衰减参数是否合适？
5. **效率对比**：重复任务时，是否更快？置信度评分是否避免了不必要的重新验证？

## 统计概览

| 轮次 | 任务数 | 侧重点 | 关键衰减行为 |
|------|--------|--------|-------------|
| R1 | 5 | 结构探索 | schema (λ=0.003) 写入；tool_experience 从 v1 复用 |
| R2 | 6 | 数据查询 | query_pattern 存储；data_snapshot 被拒绝 |
| R3 | 5 | 业务规则 | business_rule 存储；Gate 2 对 room_type 自我纠错 |
| R4 | 5 | 复杂调查 | query_pattern 存储；早期知识为 TRUST 级别 |
| R5 | 4 | 重复验证 | 预期 0 新写入；全部以 TRUST 级别复用 |
| **合计** | **25** | | |
