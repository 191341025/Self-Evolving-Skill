**[English](03-quality-audit.md)** | **中文**

# 质量审计报告（v3 — Phase 5 增强验证）

> 实验 03-nan-platform-v3 的质量审计报告。验证 Phase 5 新增的 6 项能力：entities 标签、search 命令、步骤式 Gate 2/3、硬/软信号区分、confirmed_at 刷新、search 驱动检索。

---

## 实验概览

| 项目 | 值 |
|------|------|
| 目标数据库 | nan_platform (MySQL 8.0) |
| 轮次 | 5 轮（17 个任务） |
| 起始状态 | references/ 全部清空（从零开始） |
| 执行日期 | 2026-03-14 |
| 最终知识量 | 8 条，分布在 3 个文件中 |

---

## 验证点 — 最终状态

| # | 验证点 | Phase | 覆盖轮次 | 结果 |
|---|--------|-------|---------|------|
| V1 | Gate 2/3 步骤式执行（extract entities → search → compare） | 5D | R3 | **通过** — T3.1 去重成功, T3.2 同实体不同事实通过, T3.3 矛盾拦截 |
| V2 | entities 标签提取（inject 时 LLM 正确提取实体名） | 5A | R1, R2 | **通过** — 8/8 条目均有 entities 标签 |
| V3 | search 命令调用（Gate 2/3/检索时主动调用 search） | 5A/5C | R3, R5 | **通过** — R3 调用 3 次, R5 调用 2 次 |
| V4 | 硬/软信号区分（根据信号类型选择 --weight） | 5B | R2, R4 | **通过** — 硬信号 α+1.0, 软信号 α/β+0.3 |
| V5 | confirmed_at 刷新（feedback success 后 confirmed 更新） | 5B | R2, R5 | **通过** — 每次 feedback success 后 confirmed 均更新 |
| V6 | search 驱动检索（用 entities 匹配替代全量文件加载） | 5C | R5 | **通过** — T5.1 用 search 检索到 6 条相关条目 |

**6 个验证点全部通过。**

---

## 知识演化轨迹

| 轮次 | 条目数 | 新增 | 拒绝 | 关键事件 |
|------|--------|------|------|---------|
| R0 | 0 | — | — | 基线（空） |
| R1 | 4 | +4 | 0 | 初始结构探索；全部条目附带 entities 标签 |
| R2 | 7 | +3 | 0 | 数据查询 + 业务规则发现 + 工具经验 |
| R3 | 8 | +1 | 2 | T3.1 SKIP（去重）, T3.3 REJECT（与 SQL 验证数据矛盾） |
| R4 | 8 | 0 | 0 | 软信号 + invalidate→reset 生命周期 |
| R5 | 8 | 0 | 0 | 综合 search 驱动检索验证 |

**接受率：8 条接受 / 19 次评估 ≈ 42%**（其余约 58% 被门控拒绝或未产生知识候选）

---

## 最终知识清单

| 文件 | 条目数 | 类型 | 核心内容 |
|------|--------|------|---------|
| schema_map.md | 3 | schema ×3 | t_room/t_building JOIN, t_employee/t_employee_settle JOIN, t_building/t_floor 层级 |
| business_rules.md | 2 | business_rule ×2 | room_type 枚举 (together/washroom), building_id 无索引警告 |
| query_patterns.md | 3 | query_pattern ×2, tool_experience ×1 | 视图目录, != shell 转义, 子查询聚合模式 |
| investigation_flows.md | 0 | — | 未产生多步调查流程（结构探索型任务的预期结果） |
| **合计** | **8** | **3 个文件有内容** | |

---

## 反馈信号追踪

| 条目 | α | β | 解读 |
|------|---|---|------|
| schema_map:5 (t_room/t_building) | 4.0 | 0.0 | 使用最频繁；4 次查询成功验证 |
| schema_map:9 (t_employee/t_employee_settle) | 3.0 | 0.0 | 3 次查询成功验证 |
| schema_map:13 (t_building/t_floor) | 0.0 | 0.0 | 经历完整 invalidate→reset 生命周期；计数器清零 |
| business_rules:5 (room_type 枚举) | 0.3 | 0.3 | 软成功（R3 对齐确认）+ 软失败（R4 枚举缺失查询） |
| business_rules:9 (无索引警告) | 0.0 | 0.0 | 人工注入，尚未在查询中被引用 |
| query_patterns:5 (视图目录) | 0.0 | 0.0 | 信息性条目，未被直接使用 |
| query_patterns:9 (shell 转义) | 0.0 | 0.0 | 隐性使用（学到后避免了 !=） |
| query_patterns:13 (子查询模式) | 1.0 | 0.0 | T5.1 复杂查询中使用 |

---

## 亮点

### 1. Gate 2 矛盾检测（T3.3）

本次实验最有说服力的一刻。用户声称 room_type 是 `single_room` 和 `double_room`，但已有知识（R2 中经 SQL 验证）记录为 `together` 和 `washroom`。Gate 2 正确拦截了错误信息。这证明了协议能够防御不正确的人工输入，保护知识完整性。

### 2. 选择性生长得以实现

17 个任务仅产生 8 条知识。R3 拒绝了 2 条（1 条重复、1 条矛盾），R4/R5 零新增。知识库在 R1-R2 选择性增长后趋于稳定——恰好是设计哲学所规定的收敛模式。

### 3. 完整 invalidate → revalidate → reset 生命周期（T4.2-T4.3）

用户报告知识有误 → invalidate（C0=0.1, REVALIDATE） → 工具重新验证（fetch_structure + JOIN 查询） → 确认正确 → reset（C0=1.0, TRUST）。完整生命周期顺利闭环，证明系统既尊重用户反馈（立即降级），又要求恢复必须有证据（工具验证）。

### 4. α/β 累积讲述了一个连贯的故事

schema_map:5 最终 α=4.0——最经受考验的条目。这个信号对未来的优先级排序和信任决策有真实信息价值。

---

## 发现的问题

### 严重：inject --target 路径拼接 Bug

**严重程度：必须修复**

当 `--target` 收到相对路径（如 `.claude/skills/.../schema_map.md`）时，`run_inject()` 将其拼接到 `REFERENCES_DIR`，产生嵌套错误路径 `references/.claude/skills/.../schema_map.md`。

**影响：**
- 知识静默写入错误位置
- inject 报告成功（exit code 0，输出 `written to`）
- 实际目标文件未改变
- 违反 fail-loud 原则：写入工具写错位置时应报错，而非静默成功

**修复建议：** 校验 `--target`——如果包含路径分隔符，要么报错要么自动提取文件名。或限制为仅接受文件名。

### 设计问题：软信号语义模糊（T4.1）

协议规则"枚举/状态值查询返回空结果 → 软信号 failure"未区分：
- "枚举值确实不存在"（知识是对的）
- "枚举知识不完整"（知识是错的）

T4.1 中查询 `quad_room` 返回 0 行，恰恰**确认**了已有知识（只有 together 和 washroom）。对正确的知识记录 failure 信号逻辑上不自洽。规则需要细化。

**建议修改：** 改为"枚举值查询返回空结果 → 仅当查询值来自已有知识时记为软失败。如果查询值是用户提供且不在已知枚举中，空结果**确认**已有知识 → 记为软成功。"

### 局限：时间衰减未被测试

所有条目创建于同一天（2026-03-14），衰减公式中 t=0，C 恒等于 1.0。TRUST → VERIFY → REVALIDATE 的自然退化路径从未触发。这在 v1/v2 中已验证，但 v3 的验证点覆盖在此处存在缺口。

### 观察：协议遵守依赖 LLM 自律

五道门协议是写给 LLM 的自然语言指令。LLM 必须记得 search、正确提取 entities、选择合适的 weight、记录 feedback。缺乏机械性强制。这是一个架构层面的权衡，应在设计文档中明确承认，并将"协议遵守率"作为实验中的可观测指标。

### 观察：单行知识格式可读性

schema_map:5 等密集条目（单行 300+ 字符）在知识库增长后会变得难以审计。这是格式问题，不是架构问题。

---

## 与 v1/v2 的对比

| 指标 | v1 | v2 | v3 |
|------|----|----|-----|
| 焦点 | 基础五道门验证 | Gate 4 衰减模型 | Phase 5 增强（entities, search, 信号） |
| 起始状态 | 空 | 继承 v1 的 3 条 | 空（从零） |
| 任务数 | 22 | 25 | 17 |
| 最终条目数 | ~30 | ~10（衰减标签） | 8 |
| 接受率 | ~36% | ~24% | ~42% |
| Gate 2 纠错 | 2 次 | 1 次 | 1 次（拒绝，非纠正） |
| 验证的新能力 | 五道门协议 | 衰减模型, TRUST/VERIFY/REVALIDATE | entities, search, 硬/软信号, invalidate/reset |
| 发现的 Bug | — | — | inject 路径拼接 Bug、软信号语义模糊 |

---

## 补丁验证（2026-03-15）

R5 完成后发现并修复了两个 Bug，通过定点回放验证，无需跑完整 v4。

### PV-1：inject --target 路径剥离

**Bug：** `--target` 传入相对路径时静默写入嵌套错误位置。
**修复：** 自动剥离为文件名 + stderr 警告；拒绝非 .md 目标。

| 测试 | 输入 | 结果 |
|------|------|------|
| 路径剥离 | `--target .claude/skills/.../schema_map.md` | stderr 警告，正确写入 `schema_map.md`，无嵌套目录 |
| .md 校验 | `--target no_extension` | Exit code 1，stderr 错误信息 |

**单元测试：** 新增 `TestInjectTargetValidation` 3 个用例，全部 44/44 通过。

### PV-2：软信号语义细化

**Bug：** "枚举查询空结果 → 软失败"在用户查询不存在的值时惩罚了正确的知识。
**修复：** 细化 SKILL.md 规则，区分值来源：用户提供且不在已知枚举中 → soft SUCCESS（确认完整性）。

| 步骤 | 旧规则（v3 R4） | 新规则（PV-2） |
|------|-----------------|---------------|
| 查询 `quad_room` | cnt=0 | cnt=0 |
| 决策 | soft FAILURE (β+0.3) | soft SUCCESS (α+0.3) |
| 对知识的影响 | 惩罚了正确的枚举 | 奖励了正确的枚举 |

**端到端验证：** 真实 SQL 查询（nan_platform）返回 0 行 → LLM 按新规则判定 → `feedback --result success --weight 0.3` → α 增加（非 β）。

### 补丁验证总结

两项修复均已验证。回放后 references/ 已恢复到 R5 状态（PV 产生的数据未持久化）。
