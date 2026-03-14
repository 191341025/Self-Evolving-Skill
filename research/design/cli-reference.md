# decay_engine.py CLI 参考

> Self-Evolving Skill 设计文档
> 状态：已实现（143 个 pytest 用例通过）
> 关联文档：`computation-layer-design.md`（分层架构）、`formula-opportunity-analysis.md`（设计决策来源）

---

## 概述

`decay_engine.py` 是知识生命周期的统一 CLI 入口。所有操作（查看、搜索、反馈、重置、注入、修正）通过子命令暴露，由 SKILL.md 指令驱动 LLM 调用。

```
decay_engine.py
  ├── scan         查看知识置信度状态
  ├── search       按实体/置信度搜索知识
  ├── feedback     记录使用反馈（硬/软信号）
  ├── reset        重验证通过后恢复为全新状态
  ├── inject       注入新知识条目
  └── invalidate   标记知识为待验证
```

**调用路径**：

```bash
S=".claude/skills/db-investigator/scripts"
python $S/decay_engine.py <subcommand> [options]
```

---

## 标签格式

### decay 标签

```html
<!-- decay: type=<type> confirmed=<YYYY-MM-DD> C0=<float> [alpha=<float>] [beta=<float>] -->
```

| 字段 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| type | string | 是 | — | 知识类型：schema, business_rule, tool_experience, query_pattern, data_range, data_snapshot |
| confirmed | date | 是 | — | 上次确认日期（YYYY-MM-DD）。feedback success 会刷新为今天 |
| C0 | float | 是 | 1.0 | 初始置信度。invalidate 设为 0.1 |
| alpha | float | 否 | 0 | 累计正面反馈权重。硬信号 +1.0，软信号 +0.3 |
| beta | float | 否 | 0 | 累计负面反馈权重。硬信号 +1.0，软信号 +0.3 |

### entities 标签

```html
<!-- entities: <entity1>, <entity2>, ... -->
```

紧跟 decay 标签下一行。存储实体名（表名/SP名/业务概念），用于 Gate 2/3 匹配和 search 检索。粒度为实体名，不含字段名。

**完整知识条目示例**：

```markdown
<!-- decay: type=schema confirmed=2026-03-14 C0=1.0 -->
<!-- entities: t_room, t_building -->
- t_room 通过 building_id 关联 t_building，但 building_id 在某些老数据中可能为 NULL
```

---

## 子命令

### scan — 置信度扫描

扫描 markdown 文件中的 decay 标签，计算置信度并分类。

```bash
python decay_engine.py scan --file <path>
python decay_engine.py scan --path <dir>
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| --file | string | 二选一 | 扫描单个 markdown 文件 |
| --path | string | 二选一 | 递归扫描目录下所有 .md 文件（跳过 _index.md） |

**输出格式**：

```
[TRUST       ] schema_map.md:7              C=0.951  schema      α=3 β=0  17d
[VERIFY      ] query_patterns.md:33         C=0.723  tool_exp    α=1 β=1  65d
[REVALIDATE  ] business_rules.md:8          C=0.412  biz_rule    α=0 β=2  112d
---
3 entries: 1 TRUST, 1 VERIFY, 1 REVALIDATE
```

输出按置信度升序排列（最需要关注的排前面）。

**退出码**：

| 码 | 含义 |
|----|------|
| 0 | 全部 TRUST |
| 1 | 有 VERIFY（无 REVALIDATE） |
| 2 | 有 REVALIDATE |

---

### search — 知识搜索

按实体名和/或置信等级搜索知识条目。输出按置信度降序排列。

```bash
python decay_engine.py search [--path <dir>] [--entities "<names>"] [--level TRUST|VERIFY|REVALIDATE] [--min-confidence <float>]
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| --path | string | 否 | 搜索目录（默认 references/） |
| --entities | string | 否 | 逗号分隔的实体名，OR 匹配（大小写不敏感） |
| --level | string | 否 | 最低置信等级过滤。TRUST=≥0.8, VERIFY=≥0.5, REVALIDATE=全部 |
| --min-confidence | float | 否 | 最低置信度数值过滤（与 --level 互斥） |

**过滤逻辑**：
- --entities 和 --level/--min-confidence 是 AND 关系
- --entities 内部是 OR 关系（匹配任一实体即返回）
- 无任何过滤参数时返回全部条目

**输出格式**（含 entities 显示）：

```
[TRUST       ] schema_map.md:7              C=0.951  schema      α=3 β=0  17d  [t_room, t_building]
---
1 entries matched.
```

**退出码**：0 = 有匹配，1 = 无匹配或错误。

**SKILL.md 典型用法**：

```bash
# Gate 2/3：提取实体名后搜索已有知识
python $S/decay_engine.py search --path $S/../references/ --entities "t_room,t_building"

# 知识检索：只加载可信条目
python $S/decay_engine.py search --path $S/../references/ --entities "t_room" --level TRUST
```

---

### feedback — 使用反馈

记录知识的使用反馈（成功/失败），更新 alpha/beta。

```bash
python decay_engine.py feedback --file <path> --line <n> --result success|failure [--weight <float>]
```

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| --file | string | 是 | — | 包含 decay 标签的 markdown 文件 |
| --line | int | 是 | — | decay 标签的 1-based 行号 |
| --result | string | 是 | — | success 或 failure |
| --weight | float | 否 | 1.0 | 反馈权重。硬信号 1.0，软信号 0.3 |

**反馈信号分级**：

| 信号类型 | weight | 示例 |
|---------|--------|------|
| 硬信号 | 1.0（默认） | SQL 执行成功/失败、结构查询比对、数值统计比对 |
| 软信号 | 0.3 | Gate 2 纠正、枚举值查询返回空、用户显式确认 |

**行为差异**：

| result | alpha/beta | confirmed_at | 理由 |
|--------|------------|-------------|------|
| success | alpha += weight | 刷新为今天 | 成功使用 = 确认知识当前有效 |
| failure | beta += weight | 不变 | 失败 = 否认，t 继续累积加速淘汰 |

**退出码**：0 = 成功，1 = 错误。

---

### reset — 重置

REVALIDATE 通过后，将知识恢复为全新状态。

```bash
python decay_engine.py reset --file <path> --line <n>
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| --file | string | 是 | 包含 decay 标签的 markdown 文件 |
| --line | int | 是 | decay 标签的 1-based 行号 |

**效果**：confirmed=today, C0=1.0, alpha=0, beta=0。type 不变。

**退出码**：0 = 成功，1 = 错误。

---

### inject — 注入新知识

将新知识条目写入 references/ 文件。

```bash
python decay_engine.py inject --type <type> --content "<text>" --target <filename> [--entities "<e1>,<e2>"]
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| --type | string | 是 | 知识类型（6 种之一） |
| --content | string | 是 | 知识文本（单行） |
| --target | string | 是 | 目标文件名（在 references/ 下） |
| --entities | string | 否 | 逗号分隔的实体名 |

**写入格式**：

```markdown

<!-- decay: type=business_rule confirmed=2026-03-14 C0=1.0 -->
<!-- entities: t_order, refund -->
- order_status=5 表示已退款
```

- 目标文件不存在时自动创建（最小模板）
- entities 标签仅在 --entities 参数指定时写入
- 返回 decay 标签的行号

**退出码**：0 = 成功。

**注意**：inject 只做 Gate 4-5（写入），Gate 1-3（VALUE/ALIGNMENT/REDUNDANCY）由 LLM 在调用前判断。

---

### invalidate — 标记待验证

将知识置为 REVALIDATE 状态，用于人工修正。

```bash
python decay_engine.py invalidate --file <path> --line <n>
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| --file | string | 是 | 包含 decay 标签的 markdown 文件 |
| --line | int | 是 | decay 标签的 1-based 行号 |

**效果**：C0=0.1, alpha=0, beta=0。confirmed 和 type 不变。

C(t) 立即跌入 REVALIDATE 区间（< 0.5），无论 t 是多少。

**退出码**：0 = 成功，1 = 错误。

---

## 知识生命周期

```
inject (--entities)
  → 新条目 TRUST (C0=1.0)
  → search (--entities) 检索
  → 使用知识
  → feedback (--result success/failure, --weight 1.0/0.3)
  → 时间流逝 → C(t) 自然衰减
  → scan → TRUST / VERIFY / REVALIDATE
  → 人工修正 → invalidate (C0=0.1)
  → 工具重新验证 → reset (恢复全新)
```

---

## 公式

```
C(t) = C0 × e^( -λ_base × (β+1)/(α+1) × t )
```

| 符号 | 含义 | 来源 |
|------|------|------|
| C0 | 初始置信度 | decay 标签。正常=1.0，invalidate=0.1 |
| λ_base | 基础衰减率 | 按 type 查表：schema=0.003 ~ data_snapshot=0.050 |
| α | 正面反馈累计 | feedback success。硬信号 +1.0，软信号 +0.3 |
| β | 负面反馈累计 | feedback failure。硬信号 +1.0，软信号 +0.3 |
| t | 距上次确认天数 | today - confirmed。feedback success 刷新 confirmed |

**分类阈值**：C ≥ 0.8 → TRUST / C ≥ 0.5 → VERIFY / C < 0.5 → REVALIDATE

---

*创建日期：2026-03-14*
*关联文档：`computation-layer-design.md`、`formula-opportunity-analysis.md`、`bayesian-feedback-design.md`*
