# v3 实验任务集

> 目标：验证 Phase 5 新增能力（entities 标签、search 命令、硬/软信号、步骤式 Gate 2/3）
> 数据库：nan_platform (MySQL 8.0)
> 起始状态：references/ 全部清空，从零开始

---

## 验证点映射

| # | 验证点 | 对应 Phase | 预期覆盖轮次 |
|---|--------|-----------|-------------|
| V1 | Gate 2/3 步骤式执行（extract entities → search → compare） | 5D | R3 |
| V2 | entities 标签提取（inject 时 LLM 正确提取实体名） | 5A | R1, R2 |
| V3 | search 命令调用（Gate 2/3/检索时主动调用 search） | 5A/5C | R3, R5 |
| V4 | 硬/软信号区分（根据信号类型选择 --weight） | 5B | R2, R4 |
| V5 | confirmed_at 刷新（feedback success 后 confirmed 更新） | 5B | R2, R5 |
| V6 | search 驱动检索（用 entities 匹配替代全量文件加载） | 5C | R5 |

---

## R1: 初始探索（4 任务）

**焦点**：知识从零积累，验证 entities 提取 (V2)

| # | 任务 | 预期行为 |
|---|------|---------|
| T1.1 | 探索 t_room 表的结构（字段、索引）和与 t_building 的关联关系 | inject 写入 schema_map.md，entities 含 t_room/t_building |
| T1.2 | 探索 t_employee 和 t_employee_station 表的结构和关联 | inject 写入 schema_map.md，entities 含 t_employee/t_employee_station |
| T1.3 | 查看系统中有哪些存储过程，选一个典型的看源码 | 可能产生 tool_experience 或 query_pattern |
| T1.4 | 了解 t_building 和 t_floor 的层级关系 | inject 写入 schema_map.md，entities 含 t_building/t_floor |

**R1 后检查**：
- [ ] scan 显示 R1 写入的条目全部 TRUST
- [ ] 每条知识都有 entities 标签
- [ ] search --entities "t_room" 能找到相关条目

---

## R2: 数据查询（4 任务）

**焦点**：使用 R1 知识执行查询，验证硬信号反馈 (V4) 和 confirmed_at 刷新 (V5)

| # | 任务 | 预期行为 |
|---|------|---------|
| T2.1 | 统计各楼栋的房间数量分布 | 使用 R1 的 t_room/t_building JOIN 知识；SQL 成功 → feedback success（硬信号，weight=1.0） |
| T2.2 | 查询 room_type 各类型的数量分布 | 可能产生 business_rule（枚举值发现） |
| T2.3 | 统计各员工站点的入住人数 | 使用 R1 的 t_employee_station 知识；SQL 成功 → feedback success |
| T2.4 | 查询入住率：哪些楼栋入住率最高/最低 | 需要 R1 的多表 JOIN 知识 |

**R2 后检查**：
- [ ] scan 显示被成功引用的条目 alpha > 0
- [ ] 被引用条目的 confirmed 已刷新为今天
- [ ] 新发现的业务规则有 entities 标签

---

## R3: 矛盾与去重（3 任务）

**焦点**：验证 Gate 2/3 步骤式执行 (V1) 和 search 匹配 (V3)

| # | 任务 | 预期行为 |
|---|------|---------|
| T3.1 | 再次探索 t_room 的表结构 | Gate 3 应触发：search --entities "t_room" 找到已有知识 → 判定重复 → 不写入 |
| T3.2 | 用户说："记住这个：t_room 的 building_id 外键没有索引，查询时需注意性能" | Gate 2/3 判定：与已有知识是同一实体不同事实 → 应通过并写入 |
| T3.3 | 用户说："记住这个：room_type 包含 single_room 和 double_room 两种" | 如果 R2 已记录更完整的枚举值 → Gate 3 判定为部分重复，应 MERGE 或 SKIP |

**R3 后检查**：
- [ ] T3.1 未产生新知识（去重成功）
- [ ] T3.2 产生新知识，entities 含 t_room
- [ ] T3.3 正确处理了部分重复（MERGE/SKIP/新增，取决于 R2 结果）
- [ ] 整个 R3 过程中 search 被至少调用 2 次

---

## R4: 软信号与修正（3 任务）

**焦点**：验证软信号 --weight (V4)、invalidate/reset 流程

| # | 任务 | 预期行为 |
|---|------|---------|
| T4.1 | 查询 room_type='quad_room' 的房间数量 | 如果该值不存在返回 0 行 → 软信号 failure（--weight 0.3）on room_type 枚举知识 |
| T4.2 | 用户说："schema_map 里 t_building 和 t_floor 的关系描述变了，这条不对了" | LLM 执行 invalidate → C0=0.1 → scan 显示 REVALIDATE |
| T4.3 | 重新验证 T4.2 中被 invalidate 的知识（用 fetch_structure 确认） | 验证通过 → reset → scan 显示恢复为 TRUST |

**R4 后检查**：
- [ ] T4.1 中如果触发了软信号：beta 增加 0.3（而非 1）
- [ ] T4.2 后 scan 显示该条目 REVALIDATE（C0=0.1）
- [ ] T4.3 后 scan 显示该条目恢复 TRUST（confirmed=today, alpha=0, beta=0）

---

## R5: 综合检索（3 任务）

**焦点**：验证 search 驱动检索 (V6)、全流程回归

| # | 任务 | 预期行为 |
|---|------|---------|
| T5.1 | 复杂查询：统计每栋楼每种房型的房间数和入住人数 | 需要 t_room + t_building + t_employee_station 知识；LLM 应用 search --entities 检索而非全量加载 |
| T5.2 | 全量 scan：检查所有知识的置信度状态 | 验证 confirmed_at 刷新正确、alpha/beta 累积合理、entities 标签完整 |
| T5.3 | 按实体搜索：search --entities "t_room" 列出所有 t_room 相关知识 | 验证 entities 标签覆盖度、search 返回结果正确性 |

**R5 后检查**：
- [ ] T5.1 中 LLM 使用了 search 命令（检查对话历史）
- [ ] T5.2 的 scan 输出合理（无异常状态）
- [ ] T5.3 的 search 返回覆盖了 R1-R4 中所有 t_room 相关条目

---

## 总览

| 轮次 | 任务数 | 焦点 | 验证点 |
|------|--------|------|--------|
| R1 | 4 | 初始探索 | V2 |
| R2 | 4 | 数据查询 | V4, V5 |
| R3 | 3 | 矛盾去重 | V1, V3 |
| R4 | 3 | 软信号修正 | V4 |
| R5 | 3 | 综合检索 | V5, V6 |
| **合计** | **17** | | **V1-V6 全覆盖** |
