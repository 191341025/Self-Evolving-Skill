**[English](README.md)** | **中文**

# 实验 01-nan-platform-v2

> 使用升级版 Gate 4（置信度衰减模型）对 nan_platform 进行重测

## 实验信息

| 项目 | 值 |
|------|------|
| 目标数据库 | nan_platform (MySQL 8.0) |
| 业务领域 | 智能楼宇 / 工人宿舍管理平台 |
| 数据规模 | 29 表，~95K 行，590MB |
| 使用 Skill | db-investigator（Gate 4 已升级） |
| 执行日期 | 2026-03-12 |
| 轮次 | 5 轮（结构探索 → 数据查询 → 规则发现 → 复杂调查 → 重复验证） |
| 起始状态 | 从 v1 继承 3 条 tool_experience 笔记；其余 references 重置为模板 |

## 实验目的

在与 v1 相同的数据库和任务集上，验证升级后的 Gate 4 置信度衰减模型。核心问题：将二元日期标记替换为 `C(t) = e^(-λ×t)` 加类型特异衰减率，是否能产生更好的知识治理决策？

## 核心升级：Gate 4 置信度衰减模型

| 维度 | v1（二元日期标记） | v2（置信度衰减） |
|------|-------------------|-----------------|
| 过期检查 | 二元：根据 last_confirmed 日期判断新鲜/过期 | 连续：按知识类型计算 C(t) = e^(-λ×t) |
| 知识类型 | 不区分 | 6 种类型，各有独立 λ 值 |
| 响应级别 | 接受 / 拒绝 | TRUST (C≥0.8) / VERIFY (0.5≤C<0.8) / REVALIDATE (C<0.5) |
| 高衰减数据 | 无特殊处理 | data_range 和 data_snapshot (λ≥0.035) 倾向拒绝 |
| 索引元数据 | 无置信度列 | _index.md 中新增 Min Confidence 列 |

### 六种知识类型及衰减率

| 类型 | λ | 半衰期（天） | 示例 |
|------|---|-------------|------|
| schema | 0.003 | 231 | 表字段、主键 |
| tool_experience | 0.005 | 139 | Shell 注意事项、参数技巧 |
| business_rule | 0.008 | 87 | status 字段含义、枚举值 |
| query_pattern | 0.015 | 46 | SQL 模板、JOIN 路径 |
| data_range | 0.035 | 20 | 行数统计、值域范围 |
| data_snapshot | 0.050 | 14 | 具体查询结果、分布数据 |

## 核心结果

| 指标 | 结果 |
|------|------|
| 知识总量 | 176 行（对比 v1 同阶段 ~120 行；差异主要来自衰减元数据） |
| 接受率 | ~24%（对比 v1 ~30% —— 因衰减拒绝更严格） |
| Gate 2 自我纠错 | 1 次（room_type 枚举修正） |
| R5 验证 | 4/4 首次成功，0 次结构查找 |
| 准确率 | 100%（0 条错误知识存活） |

## 与 v1 的关键差异

1. **置信度衰减模型**：每条知识标记类型特异 λ 和确认日期
2. **三级响应**：TRUST (C≥0.8) / VERIFY (0.5≤C<0.8) / REVALIDATE (C<0.5)
3. **高衰减类型偏好**：data_range 和 data_snapshot (λ≥0.035) 倾向拒绝而非存储
4. **Min Confidence 列**：_index.md 新增，可快速总览知识过期状态

## 文件导航

| 文件 | 内容 | 阅读优先级 |
|------|------|-----------|
| [`01-task-set.md`](01-task-set.md) | 5 轮 25 个任务（与 v1 相同，附复用标注） | 了解实验设计 |
| [`02-evolution-log.md`](02-evolution-log.md) | **核心数据**：逐轮门控决策、置信度评分、写入内容 | 必读 |
| [`03-quality-audit.md`](03-quality-audit.md) | 质量审计 + 衰减模型有效性分析 | 必读 |
| [`04-comparison.md`](04-comparison.md) | v1 vs v2 正面对比 | 必读 |

### snapshots/ — 每轮知识快照

每个子目录是该轮结束后 `references/` 的完整拷贝，可用 diff 对比任意两轮的变化：

| 快照 | 时间点 | 说明 |
|------|--------|------|
| `R0-baseline/` | 实验前 | 模板 + 从 v1 继承的 3 条 tool_experience |
| `R1-structure/` | Round 1 后 | 表结构 + 字典枚举写入 |
| `R2-queries/` | Round 2 后 | 附带置信度元数据的 SQL 模板 |
| `R3-rules/` | Round 3 后 | 业务规则（含 Gate 2 自我纠错） |
| `R4-investigations/` | Round 4 后 | 调查流程 + Pitfall 写入 |
| `R5-verification/` | Round 5 后 | 验证衰减模型下的知识复用 |

**快速对比示例**（本地 clone 后）：
```bash
diff snapshots/R0-baseline/business_rules.md snapshots/R5-verification/business_rules.md
```

## 关键发现

1. **衰减模型有效拒绝易变数据** —— data_range 和 data_snapshot 类型以 ~80% 的拒绝率被过滤，防止时间敏感的计数和分布数据导致知识膨胀
2. **VERIFY 级别增加了决策维度** —— 替代二元接受/拒绝，边界知识被标记为需要再确认，同时减少误接受和不必要的拒绝
3. **Gate 2 自我纠错机制仍然有效** —— 在新 Gate 4 机制下仍能检测并修正 room_type 枚举错误
4. **R5 复用比 v1 更强** —— 置信度评分让 Skill 无需重新查询结构即可做出即时信任决策
5. **继承的 tool_experience 证明了价值** —— 从 v1 继承的 3 条笔记（shell 编码、`!=` vs `<>`、fetch_structure.py 用法）从 Round 1 开始就消除了所有工具摩擦
