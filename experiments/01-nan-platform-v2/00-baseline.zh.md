# 基线快照：nan_platform 数据库（v2）

> 生成时间：2026-03-12
> 目的：记录 v2 实验的起始状态（R0）——使用升级后的 Gate 4 置信度衰减模型对 01-nan-platform 的重新测试。与 v1 的"零点"不同，v2 从 v1 继承了 3 条 tool_experience 条目。

## 数据库概况

| 项目 | 值 |
|------|-----|
| 数据库名 | nan_platform |
| 数据库管理系统 | MySQL 8.0 |
| 业务领域 | 智能楼宇/工人宿舍管理平台 |
| 表数量 | 29 |
| 视图数量 | 12 |
| 存储过程 | 0 |
| 估算总行数 | 95,517 |
| 数据量 | 589.53 MB |

> 数据库与 v1 完全相同。完整的 schema 描述、实体关系、字典体系和数据分布请参见 [v1 基线](../01-nan-platform/00-baseline.md)。

## 测试技能

| 项目 | 值 |
|------|-----|
| 技能 | db-investigator |
| 核心升级 | Gate 4 拆分为写模式（分配衰减）和读模式（基于置信度响应） |
| 衰减模型 | C(t) = e^(-lambda * t)，6 种知识类型各有独立 lambda 值 |
| 响应等级 | TRUST（C >= 0.8）/ VERIFY（0.5 <= C < 0.8）/ REVALIDATE（C < 0.5） |
| 缩放规则 | 每次写入后检查活跃行数 |
| Gate 5 变更 | _index.md 更新触发条件扩展 |

### 置信度衰减参考表

| 知识类型 | lambda | 半衰期（天） | 示例 |
|----------|--------|-------------|------|
| schema | 0.003 | 231 | 表结构、主键 |
| tool_experience | 0.005 | 139 | 工具特性、变通方法 |
| business_rule | 0.008 | 87 | 状态字段含义、枚举值 |
| query_pattern | 0.015 | 46 | SQL 模板、JOIN 路径 |
| data_range | 0.035 | 20 | 行数、值范围 |
| data_snapshot | 0.050 | 14 | 特定查询结果、分布 |

## 起始状态（R0）

### 文件行数总计

| 文件 | 行数 | 内容 |
|------|------|------|
| `_index.md` | 12 | 路由表，含 Min Confidence 列（模板 + query_patterns 的 1 条真实条目） |
| `schema_map.md` | 29 | 仅模板（示例表头 + 占位表格） |
| `business_rules.md` | 20 | 仅模板（示例枚举 + 规则） |
| `query_patterns.md` | 40 | 模板 SQL 示例 + **3 条真实 tool_experience 笔记** |
| `investigation_flows.md` | 43 | 仅模板（示例流程） |
| **合计** | **144** | |

### 继承的知识（3 条）

全部为 `tool_experience` 类型，确认时间 2026-03-08，初始置信度 C0 = 1.0。

实验开始时（2026-03-12，t = 4 天），其置信度为：
- C(4) = e^(-0.005 * 4) = **0.980**（tool_experience lambda = 0.005）

| # | 衰减元数据 | 内容 |
|---|-----------|------|
| 1 | `<!-- decay: type=tool_experience confirmed=2026-03-08 C0=1.0 -->` | 避免在 SQL 中使用 `!=`，必须用 `<>` 替代（shell 转义问题） |
| 2 | `<!-- decay: type=tool_experience confirmed=2026-03-08 C0=1.0 -->` | 先查数据时间范围——记录表可能有数据空窗期，查趋势前先确认 MIN/MAX 时间戳 |
| 3 | `<!-- decay: type=tool_experience confirmed=2026-03-08 C0=1.0 -->` | SQL 中避免中文字符串——shell 传参含中文可能导致 exit code 127，用数值字段替代中文字段做 WHERE 条件 |

### 与 v1 基线的关键差异

| 方面 | v1（R0） | v2（R0） |
|------|---------|---------|
| 先验知识 | 0 条（完全空白） | 3 条 v1 继承的 tool_experience |
| 总行数 | 144（全部为模板） | 144（模板 + 3 条真实条目） |
| 衰减元数据 | 未使用 | 每条真实条目携带 `<!-- decay: ... -->` |
| Gate 4 模型 | 二元判断：新鲜 vs 过时 | 连续模型：C(t) = e^(-lambda * t)，按类型区分 |
| `_index.md` 格式 | 无置信度列 | 新增 Min Confidence 列 |
| SKILL.md Gate 4 | 单一模式 | 拆分为写模式（分配衰减）和读模式（基于置信度响应） |
| SKILL.md 缩放规则 | 无 | 每次写入后检查活跃行数 |
| SKILL.md Gate 5 | 基本触发 | _index.md 更新触发条件扩展 |
| SKILL.md 新增章节 | 无 | 置信度衰减模型参考表 |

## references/ 初始状态

模板文件包含示例占位内容，没有关于 nan_platform 的真实领域知识，唯一例外是 `query_patterns.md` 中的 3 条 tool_experience 笔记。这些笔记是 v1 到 v2 唯一的知识迁移。

完整 R0 快照位于：`snapshots/R0-baseline/`
