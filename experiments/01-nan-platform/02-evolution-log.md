# Skill 进化日志

> 记录 db-investigator Skill 在实验过程中 references/ 的每一次变化。
> 这是实验的核心数据，将作为设计模式的实证验证提交到 GitHub。

---

## 格式说明

每次 references/ 发生变化时，按以下格式记录：

```
### [轮次.任务] 简述
- **时间**：YYYY-MM-DD HH:MM
- **触发任务**：具体任务描述
- **五道门决策**：
  - Gate 1 (VALUE): 通过/拒绝 — 理由
  - Gate 2 (ALIGNMENT): 通过/跳过
  - Gate 3 (REDUNDANCY): 通过/跳过
  - Gate 4 (FRESHNESS): 稳定事实/标注日期
  - Gate 5 (PLACEMENT): → 目标文件
- **变更内容**：具体写入了什么
- **质量评估**：[准确/待验证/有风险]
```

---

## 进化记录

### [R1] Round 1 — 结构探索（批量写入）
- **时间**：2026-03-08 15:30
- **触发任务**：1.1~1.5（表分类、实体关系、员工关联、进出关联、字典系统）

#### 写入 1：schema_map.md（从模板 → 真实内容）
- **五道门决策**：
  - Gate 1 (VALUE): **通过** — 表关系和 JOIN 路径是每次查询的基础，高复用
  - Gate 2 (ALIGNMENT): 通过 — 替换模板内容，无矛盾
  - Gate 3 (REDUNDANCY): 通过 — 首次写入
  - Gate 4 (FRESHNESS): 稳定事实 — 表结构不频繁变化
  - Gate 5 (PLACEMENT): → schema_map.md
- **变更内容**：
  - 数据库概述（nan_platform = 智能楼宇管理平台）
  - 完整实体关系图（building→floor→room, employee→settle→room, emp_record↔employee via id_card）
  - 表分类（7 组共 29 张表）
  - 8 条关键 JOIN 路径
- **质量评估**：准确（全部通过实际查询验证）

#### 写入 2：business_rules.md（从模板 → 真实内容）
- **五道门决策**：
  - Gate 1 (VALUE): **通过** — status='1' 约定影响所有查询；字典枚举值在数据分析时频繁需要
  - Gate 2 (ALIGNMENT): 通过
  - Gate 3 (REDUNDANCY): 通过 — 首次写入
  - Gate 4 (FRESHNESS): 稳定事实 — 字典值和字段约定不频繁变化
  - Gate 5 (PLACEMENT): → business_rules.md
- **变更内容**：
  - 5 条关键字段约定（status='1'含义、主键类型、无外键、审计字段、create_by 常见值）
  - 13 个字典类型的完整枚举值
- **质量评估**：准确（字典值直接从 sys_dict_value 查询获得）

#### 被拒绝的知识
| 候选知识 | 拒绝门 | 理由 |
|----------|--------|------|
| "当前有 2071 个员工" | Gate 4 (FRESHNESS) | 数据量随时变化，写入即过时 |
| "每栋楼 3 层、26-36 个房间" | Gate 1 (VALUE) | 一次性查询结果，非可复用模式 |
| "Face_In 有 46112 条记录" | Gate 4 (FRESHNESS) | 实时增长的数据，不入库 |
| "1517/1518 身份证能匹配到员工" | Gate 1+4 | 一次性结果 + 时间敏感 |

#### references/ 变化统计
| 文件 | 变化前 | 变化后 | 增量 |
|------|--------|--------|------|
| schema_map.md | 30行（模板） | 47行（真实） | +17行有效内容 |
| business_rules.md | 21行（模板） | 73行（真实） | +52行有效内容 |
| query_patterns.md | 未变 | 未变 | 0 |
| investigation_flows.md | 未变 | 未变 | 0 |
| **总计** | 51行 | 120行 | **+69行** |

---

### [R2] Round 2 — 数据调查（单步查询）
- **时间**：2026-03-08 15:45

#### 写入 1：query_patterns.md（从模板 → 真实查询模板）
- **五道门决策**：
  - Gate 1 (VALUE): **通过** — 入住率、人口统计、进出趋势、设备状态均为高频查询场景
  - Gate 2 (ALIGNMENT): 通过 — 替换模板
  - Gate 3 (REDUNDANCY): 通过 — 首次写入
  - Gate 4 (FRESHNESS): 稳定模式 — SQL 模板不随数据变化
  - Gate 5 (PLACEMENT): → query_patterns.md
- **变更内容**：
  - 5 个 SQL 模板：楼栋入住率、性别分布、年龄分布、进出趋势、设备状态
  - 2 条工具使用经验：`!=` 需替换为 `<>`、先查数据时间范围
- **质量评估**：准确（全部经过实际执行验证）

#### 写入 2：schema_map.md（增量修正）
- **五道门决策**：
  - Gate 1 (VALUE): **通过** — 设备关联稀疏是结构层面的重要认知
  - Gate 2 (ALIGNMENT): **修正** — 原描述"可选关联"不够准确，实际是"绝大部分为空"
  - Gate 5: → schema_map.md（修正已有条目）
- **变更内容**：补充 t_device.building_id 绝大部分为空的警告

#### 写入 3：business_rules.md（增量）
- **五道门决策**：
  - Gate 1 (VALUE): **通过** — 数据时间范围影响所有时间相关查询
  - Gate 4 (FRESHNESS): **标注日期** — 标注 "2026-03-08 确认，可能持续增长"
  - Gate 5: → business_rules.md
- **变更内容**：t_emp_record 数据范围 2025-12-10 ~ 2026-02-28

#### 被拒绝的知识
| 候选知识 | 拒绝门 | 理由 |
|----------|--------|------|
| "19栋工人宿舍+1栋夫妻楼" | Gate 1 | 一次性查询结果 |
| "在住640人，男618女22" | Gate 4 | 时间敏感，随时变化 |
| "13# 入住率94.4%, 12# 90%" | Gate 1+4 | 具体数值非可复用模式 |
| "225正常/7无法访问/1停用" | Gate 4 | 设备状态数据随时变化 |
| "2/22-2/28进出呈增长趋势" | Gate 1 | 一次性分析结论 |

#### references/ 变化统计
| 文件 | R1 后 | R2 后 | 增量 |
|------|-------|-------|------|
| schema_map.md | 57行 | 57行 | ~0（修正1行） |
| business_rules.md | 73行 | 74行 | +1行 |
| query_patterns.md | 30行（模板） | 55行（真实） | +25行有效内容 |
| investigation_flows.md | 未变 | 未变 | 0 |
| **总计** | 120行 | 186行 | **+26行** |

#### 观察
- Round 2 增量（+26行）远小于 Round 1（+69行），符合"成长期增量放缓"预期
- 五道门拒绝了 5 条候选知识，**拒绝率 62.5%**（5拒绝/8候选），治理在发挥作用
- Gate 2 首次触发了"修正"功能（设备关联描述从"可选"修正为"绝大部分为空"）
- 工具使用经验（`!=`→`<>`）是意外收获，属于 Round 1 未预期的知识类型

---

### [R3] Round 3 — 业务规则发现
- **时间**：2026-03-08 16:00

#### 写入 1：business_rules.md — status 字段规则修正（Gate 2 触发）
- **五道门决策**：
  - Gate 1 (VALUE): **通过** — 不知道这个区别会导致查记录表返回 0 条结果
  - Gate 2 (ALIGNMENT): **修正** — 原规则"所有表统一 status='1'"不正确，记录表（_record）的 status='0'
  - Gate 3 (REDUNDANCY): 修正已有条目，非新增
  - Gate 4 (FRESHNESS): 稳定事实
  - Gate 5 (PLACEMENT): → business_rules.md
- **变更内容**：将"所有表统一"修正为"主数据表 status='1'"，新增例外说明
- **质量评估**：准确（实际查询验证 t_emp_record 全部 status='0', t_car_record 同理）
- **意义**：这是五道门 Gate 2（ALIGNMENT）的典型案例——发现已有知识有误，修正而非追加

#### 写入 2：business_rules.md — result 字段含义
- **五道门决策**：
  - Gate 1 (VALUE): **通过** — 理解 result 是人脸置信度对数据分析有价值
  - Gate 2-3: 通过（新知识）
  - Gate 4: 稳定事实
  - Gate 5: → business_rules.md
- **变更内容**：新增 t_emp_record Fields 节，说明 result=人脸置信度(0-99)

#### 写入 3：business_rules.md — end_time vs id_end_time 区分
- **五道门决策**：
  - Gate 1 (VALUE): **通过** — 两个日期字段极易混淆，下次查过期员工时必须知道
  - Gate 5: → business_rules.md
- **变更内容**：新增 t_employee Date Fields 节，明确 end_time 才是业务过期日期

#### 被拒绝的知识
| 候选知识 | 拒绝门 | 理由 |
|----------|--------|------|
| "settle_status 与 building/room 数据一致" | Gate 1 | 一次性验证结论，非可复用规则 |
| "49人名单过期仍 settle_in" | Gate 1+4 | 一次性统计 + 时间敏感 |
| "33人只进不出/只出不进" | Gate 1+4 | 一次性统计 |

#### references/ 变化统计
| 文件 | R2 后 | R3 后 | 增量 |
|------|-------|-------|------|
| schema_map.md | 56行 | 56行 | 0 |
| business_rules.md | 69行 | 81行 | +12行（含1行修正） |
| query_patterns.md | 74行 | 74行 | 0 |
| investigation_flows.md | 43行 | 43行 | 0 |
| **总计** | 252行 | 264行 | **+12行** |

#### 观察
- 增量持续递减：R1 +69行 → R2 +26行 → R3 +12行
- **Gate 2 修正功能再次触发**：status 规则从"统一"修正为"有例外"，这是高价值修正
- 拒绝率 50%（3拒绝/6候选），拒绝的全是具体数值/一次性统计
- Round 3 主要产出是**业务规则澄清**，没有新增结构或查询模板，符合预期定位

---

### [R4] Round 4 — 复杂调查（多步骤）
- **时间**：2026-03-08 16:30

#### 写入 1：investigation_flows.md（从模板 → 真实调查流程）
- **五道门决策**：
  - Gate 1 (VALUE): **通过** — 员工画像、幽灵员工审计、楼栋对比均为可复用的多步调查流程
  - Gate 2 (ALIGNMENT): 通过 — 替换模板
  - Gate 3 (REDUNDANCY): 通过 — 首次写入
  - Gate 4 (FRESHNESS): 稳定流程 — 调查步骤不随数据变化
  - Gate 5 (PLACEMENT): → investigation_flows.md
- **变更内容**：
  - 3 个调查流程：Employee Profile（3步）、Ghost Employee Audit（3步）、Building Comparison（3步）
  - 每个流程附带 Pitfall 警告（基于实际踩坑经验）
- **质量评估**：准确（每个流程都经过实际执行验证）

#### 写入 2：business_rules.md — washroom capacity=0 应排除
- **五道门决策**：
  - Gate 1 (VALUE): **通过** — 不排除会导致房间数虚高
  - Gate 2 (ALIGNMENT): **增强** — 补充 room_type 枚举的业务含义
  - Gate 5: → business_rules.md（修改已有条目）
- **变更内容**：room_type 枚举补充 capacity 说明和统计注意事项

#### 写入 3：query_patterns.md — 中文 shell 传参问题
- **五道门决策**：
  - Gate 1 (VALUE): **通过** — 第三条工具经验，和 `!=` / 数据空窗期 同等重要
  - Gate 5: → query_patterns.md Tool Usage Notes
- **变更内容**：追加"避免 SQL 中含中文字符串"经验

#### 被拒绝的知识
| 候选知识 | 拒绝门 | 理由 |
|----------|--------|------|
| "进出高峰 5-6 点出 / 17-19 点回" | Gate 1 | 2月数据结论，可能因季节/项目变化 |
| "235 幽灵员工" | Gate 4 | 时间敏感数据 |
| "13# 151人, 20# 116人" | Gate 4 | 时间敏感 |
| "李盟阳 131 次进出" | Gate 1 | 一次性查询 |
| "10 栋楼完全空置" | Gate 1+4 | 一次性统计 + 随入驻变化 |

#### references/ 变化统计
| 文件 | R3 后 | R4 后 | 增量 |
|------|-------|-------|------|
| schema_map.md | 57行 | 57行 | 0 |
| business_rules.md | 82行 | 83行 | +1行 |
| query_patterns.md | 75行 | 76行 | +1行 |
| investigation_flows.md | 43行（模板） | 62行（真实） | +19行有效内容 |
| **总计** | 267行 | 288行 | **+21行** |

#### 观察
- 增量趋势：R1 +75 → R2 +46 → R3 +12 → R4 +21（R4 略有回升，因为首次写入 investigation_flows）
- **四个 references 文件全部激活**：schema_map(R1) → business_rules(R1) → query_patterns(R2) → investigation_flows(R4)
- 调查流程中的 Pitfall 是最有价值的部分——来自实际踩坑，下次可直接避开
- 五道门继续有效拒绝具体数值和时间敏感数据，拒绝 5 / 接纳 5（50%拒绝率）

---

### [R5] Round 5 — 重复与进化验证
- **时间**：2026-03-08 17:00

#### 任务 5.1：再问"各楼栋入住率如何"（重复 R2 任务）
- **行为**：**直接使用 `query_patterns.md` Building Occupancy 模板**
- **探索步骤**：0（未调用 fetch_structure 或 fetch_index）
- **查询次数**：1
- **对比 R2**：R2 时需要多步探索建表结构才写出 SQL；R5 直接从模板复制执行
- **知识复用**：query_patterns.md ✅

#### 任务 5.2：再查"员工年龄分布"（重复 R2 任务）
- **行为**：**直接使用 `query_patterns.md` Employee Demographics 模板**
- **探索步骤**：0
- **查询次数**：1
- **知识复用**：query_patterns.md ✅（含 birthday IS NOT NULL 过滤、settle JOIN 条件）

#### 任务 5.3：再做"幽灵员工"调查（重复 R4 任务）
- **行为**：**严格按照 `investigation_flows.md` Ghost Employee Audit 三步流程执行**
- **遵循 Pitfall**：✅ 用 MAX(auth_time) 作为截止点而非 CURDATE()
- **查询次数**：4（Step1a: 截止点 → Step1b: 计数 → Step2: 楼栋分布 → Step3: last-seen分类）
- **知识复用**：investigation_flows.md ✅ + schema_map.md ✅（id_card关联）+ business_rules.md ✅（status规则）

#### 任务 5.4：新问题"哪些企业的员工入驻最多"
- **行为**：利用已有知识快速定位，仅需探索 t_company 关联路径
- **已知并复用**：status='1' 约定、settle_status 字典值、JOIN 路径基础
- **需要新探索**：仅 t_building_rent.company_id → t_company.id 这一条关联
- **查询次数**：5（1结构 + 1列搜索 + 1settle结构 + 2数据查询）
- **对比 R1**：R1 完全从零探索，R5 新问题只需探索新关联路径，其余知识全部复用

#### 写入 1：schema_map.md — 新增 company → building JOIN 路径
- **五道门决策**：
  - Gate 1 (VALUE): **通过** — 企业维度分析是可复用场景
  - Gate 2 (ALIGNMENT): 通过 — 无矛盾
  - Gate 3 (REDUNDANCY): 通过 — 新知识
  - Gate 4 (FRESHNESS): 稳定事实
  - Gate 5 (PLACEMENT): → schema_map.md Key Join Paths
- **变更内容**：新增 `company → building: t_building_rent.company_id = t_company.id`

#### 被拒绝的知识
| 候选知识 | 拒绝门 | 理由 |
|----------|--------|------|
| "t_company.company_type 全部 NULL" | Gate 1+4 | 一次性数据状态，随录入变化 |
| "中建宏达 483人最多" | Gate 4 | 时间敏感数据 |
| "274 个幽灵员工" | Gate 4 | 时间敏感 |
| "在住 640 人年龄分布" | Gate 4 | 时间敏感 |

#### references/ 变化统计
| 文件 | R4 后 | R5 后 | 增量 |
|------|-------|-------|------|
| schema_map.md | 57行 | 58行 | +1行 |
| business_rules.md | 83行 | 83行 | 0 |
| query_patterns.md | 76行 | 76行 | 0 |
| investigation_flows.md | 65行 | 65行 | 0 |
| **总计** | 288行 | 289行 | **+1行** |

#### 核心观察：进化验证成功

**效率提升对比**：

| 任务 | 首次(R2/R4) | 重复(R5) | 提升 |
|------|------------|----------|------|
| 楼栋入住率 | 多步探索+构建SQL | 1次查询，直接用模板 | 探索步骤→0 |
| 年龄分布 | 多步探索+构建SQL | 1次查询，直接用模板 | 探索步骤→0 |
| 幽灵员工 | 逐步摸索+踩坑 | 4次查询，按流程走+避坑 | 流程化，无踩坑 |
| 新问题(企业) | — | 5次查询，大量知识复用 | 仅探索新关联 |

**增量趋势完整曲线**：R1 +75 → R2 +46 → R3 +12 → R4 +21 → R5 +1

**关键结论**：
1. **知识确实被复用**：R5 的重复任务全部直接使用 references/ 中已有模板和流程
2. **探索成本大幅降低**：重复任务的结构探索步骤降为 0
3. **Pitfall 被主动避开**：幽灵员工调查中主动用 MAX(auth_time) 而非 CURDATE()
4. **增量趋于零**：R5 仅 +1 行，符合"成熟期"预期——Skill 已基本稳定
5. **新问题仍能学习**：5.4 发现新的 JOIN 路径并正确通过五道门写入
6. **五道门持续有效**：拒绝了 4 条时间敏感数据，拒绝率 80%（4拒绝/5候选），越成熟拒绝率越高
