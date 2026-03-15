**[English](README.md)** | **中文**

# 实验 03-nan-platform-v3

> Phase 5 增强验证：entities 标签、search 命令、硬/软信号、步骤式 Gate 2/3

## 实验信息

| 项目 | 值 |
|------|------|
| 目标数据库 | nan_platform (MySQL 8.0) |
| 业务领域 | 智能楼宇 / 工人宿舍管理平台 |
| 数据规模 | 29 表，~95K 行，590MB |
| 使用 Skill | db-investigator（Phase 5 增强版） |
| 执行日期 | 2026-03-14 |
| 轮次 | 5+1 轮，17 个任务 + R6 时间衰减定点验证 |
| 起始状态 | references/ 全部清空——从零开始 |

## 实验目的

在与 v1/v2 相同的数据库上、从空知识库出发，验证 Phase 5 新增的 6 项能力：

| # | 能力 | 新增内容 |
|---|------|---------|
| V1 | 步骤式 Gate 2/3 | extract entities → search → compare（替代整体 LLM 判断） |
| V2 | entities 标签 | `<!-- entities: t_room, t_building -->` 在 inject 时提取并附加 |
| V3 | search 命令 | `decay_engine.py search --entities` 进行定向知识检索 |
| V4 | 硬/软信号区分 | `--weight 1.0`（默认）用于硬信号，`--weight 0.3` 用于软信号 |
| V5 | confirmed_at 刷新 | `feedback success` 更新 `confirmed=YYYY-MM-DD` 时间戳 |
| V6 | search 驱动检索 | 用 entities 匹配选择性加载，替代全量文件加载 |

## 核心结果

| 指标 | 结果 |
|------|------|
| 验证点通过 | **6/6**（V1-V6 全部通过） |
| 最终知识条目 | 8 条（分布在 3 个文件中） |
| 接受率 | ~42%（8 条接受 / 19 次评估） |
| Gate 2 矛盾拒绝 | 1 次（T3.3——错误枚举值被拒绝） |
| Gate 3 去重 | 1 次（T3.1——重复探索正确跳过） |
| 软信号准确性 | weight=0.3 正确执行（β+0.3，而非+1.0） |
| invalidate→reset 生命周期 | 顺利闭环（T4.2-T4.3） |
| 发现的 Bug | 1 个严重（inject --target 路径拼接） |

## 关键发现

1. **entities + search 实现精确 Gate 2/3** — 步骤式执行（extract → search → compare）将整体 LLM 判断替换为结构化的循证决策
2. **硬/软信号区分工作正确** — α 硬信号累积 +1.0（SQL 成功），+0.3 软信号（对齐确认、枚举缺失）
3. **Gate 2 防御错误人工输入** — T3.3 正确拒绝了用户声称的枚举值（与 SQL 验证数据矛盾）
4. **invalidate→reset 生命周期完整闭环** — 用户报告 → C0=0.1 → 工具验证 → 恢复 TRUST
5. **inject --target 路径 Bug 严重** — 静默写入错误位置；生产使用前必须修复

## 文件导航

| 文件 | 内容 | 优先级 |
|------|------|--------|
| [`task-set.md`](task-set.md) | 5 轮 17 个任务 + 验证点映射 | 了解实验设计 |
| [`03-quality-audit.zh.md`](03-quality-audit.zh.md) | **核心文档**：质量审计、亮点、问题、v1/v2 对比 | 必读 |

### snapshots/ — 每轮知识快照

每个子目录是该轮结束后 `references/` 的完整拷贝：

| 快照 | 时间点 | 说明 |
|------|--------|------|
| `R0-baseline/` | 实验前 | 全部文件为空（仅标题行） |
| `R1-initial-exploration/` | Round 1 后 | 4 条：t_room/t_building, t_employee/t_employee_settle, t_building/t_floor 结构, 视图目录 |
| `R2-data-queries/` | Round 2 后 | +3 条：room_type 枚举, shell 转义提示, 子查询聚合模式 |
| `R3-dedup-contradiction/` | Round 3 后 | +1 条（无索引警告）；1 次 SKIP, 1 次 REJECT |
| `R4-soft-signal-correction/` | Round 4 后 | 无新增；软信号 + invalidate/reset 测试 |
| `R5-comprehensive/` | Round 5 后 | 最终状态；search 驱动检索验证 |
| `R6-time-decay/` | 第 2 天 (2026-03-15) | 时间衰减定点验证：自然衰减 + 反馈刷新 + 投影 |

**快速对比示例**（本地 clone 后）：
```bash
diff snapshots/R0-baseline/schema_map.md snapshots/R5-comprehensive/schema_map.md
```

## 额外发现

- **表名纠正：** task-set 中引用的 `t_employee_station` 不存在，实际表名为 `t_employee_settle`
- **数据库无存储过程**（0 个 SP），但有 12 个视图（v_employee_distribution, v_room_overview 等）
