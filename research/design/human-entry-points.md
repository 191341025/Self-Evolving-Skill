# 人工入口设计：注入与修正

> Self-Evolving Skill 设计文档
> 状态：设计定稿 v3 — 所有开放问题已锁定，可进入开发
> 前置依赖：五道门协议（SKILL.md）、`bayesian-feedback-design.md`
> 更新：2026-03-14 v3 — 锁定写入格式、invalidate 机制、source 字段决策

---

## 1. 问题陈述

当前五道门协议的触发时机是「AI 主动发现知识并准备写入」。但很多高价值知识来自两个 AI 无法自主触发的场景：

1. **人在对话中说出领域知识**（"这个字段其实指向的是那个表"）— 需要注入入口
2. **人发现已有知识有误**（"这条规则已经变了"）— 需要修正入口

这两个入口缺失会导致：
- 注入缺失：高价值的演化性知识、异常性知识无法进入系统（这类知识 AI 很难自主发现）
- 修正缺失：错误知识通过"表面成功使用"不断累积 α，被确认偏差强化

---

## 2. 架构：触发层与处理层分离

### 2.1 核心原则

**入口不同，质量管道相同。** 人工注入的知识同样要过五道门，不跳关。

**触发层是平台适配器，处理层是平台无关内核。** 人工入口的实现方式不应把 skill 锁死在任何特定 AI 平台上。

### 2.2 架构图

```
触发层（平台相关 — 薄适配器）         处理层（平台无关 — Python + MD）
┌──────────────────────────┐         ┌─────────────────────────────┐
│ Claude Code:             │         │                             │
│   SKILL.md 指令识别      │         │  LLM 判断 Gate 1-3          │
│   用户自然语言 ──────────┼────┐    │    ├── VALUE（值得存吗）     │
│                          │    │    │    ├── ALIGNMENT（冲突吗）   │
│ 其他 AI Agent:           │    ├───→│    └── REDUNDANCY（重复吗）  │
│   API call / Webhook ────┼────┤    │                             │
│                          │    │    │  Python 执行 Gate 4-5       │
│ 人直接 CLI:              │    │    │    ├── FRESHNESS（衰减参数） │
│   终端命令 ──────────────┼────┘    │    └── PLACEMENT（写入位置） │
│                          │         │                             │
│                          │         │  decay_engine.py inject     │
│                          │         │  decay_engine.py invalidate │
└──────────────────────────┘         └─────────────────────────────┘
```

### 2.3 为什么不用 slash command

早期考虑过 Claude Code 的 slash command 方案。否决理由：

- slash command 是 Claude Code 特有机制，会导致 skill 的人工入口被平台锁定
- Python CLI 是万能接口 — 任何能调用 Python 的环境都能用
- 两种方案都需要用户使用指南，实现成本无差异
- Python CLI 方案天然融入现有工具体系（`decay_engine.py` 已有 scan/feedback/reset）

---

## 3. 人工注入入口

### 3.1 触发路径的评估

| 方案 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| **路A：人主动触发** | 人显式说「记住这个」，AI 走五道门写入 | 简单直接，成本极低 | 依赖人的自觉 |
| **路B：AI 识别后询问** | AI 识别到高价值信息，主动问「要不要存？」 | 自然，不依赖人主动 | 识别准确率未知，可能打断节奏 |
| **路C：会话结束统一处理** | 会话结束前回顾对话，打包确认 | 不打断开发节奏 | 依赖会话生命周期钩子 |

**第一阶段：只做路 A。** 理由不变：实现成本极低，路 B/C 的前置条件未满足。

### 3.2 五道门的分工：LLM 判断 + Python 执行

这是人工注入设计的关键决策。五道门中，部分门需要 LLM 的语义判断，部分门是可编程的机械操作：

| Gate | 内容 | 执行者 | 原因 |
|------|------|--------|------|
| Gate 1 VALUE | 这条知识值得存吗？ | **LLM** | 需要理解知识的领域价值 |
| Gate 2 ALIGNMENT | 和已有知识冲突吗？ | **LLM** | 需要读 references/ 并做语义比对 |
| Gate 3 REDUNDANCY | 已经存过了吗？ | **LLM** | 需要判断语义重复 |
| Gate 4 FRESHNESS | 分配衰减参数 | **Python** | 按知识类型查 LAMBDA_TABLE |
| Gate 5 PLACEMENT | 写到哪个文件 | **Python** | 按知识类型路由到目标文件 |

**LLM 做判断（Gate 1-3），Python 做执行（Gate 4-5 + 写入）。** 这和项目的架构核心原则「LLM 做判断，Python 做计算」完全一致。

### 3.3 完整流程

```
用户："order_status=5 表示已退款，不是已取消"
  │
  ├── LLM 判断 Gate 1-3
  │     ├── Gate 1 VALUE：领域知识，有长期价值 → 通过
  │     ├── Gate 2 ALIGNMENT：与已有 schema_map 不冲突 → 通过
  │     ├── Gate 3 REDUNDANCY：未记录过 → 通过
  │     └── 不通过任一门 → 告知用户原因，不写入
  │
  └── 调用 Python 工具完成写入（Gate 4-5）：
      python decay_engine.py inject \
        --type business_rule \
        --content "order_status=5 表示已退款，不是已取消" \
        --target business_rules.md
```

### 3.4 `inject` 子命令设计

扩展现有 `decay_engine.py`，新增 `inject` 子命令：

```bash
python decay_engine.py inject \
  --type <knowledge_type> \       # schema|business_rule|query_pattern|...
  --content "<知识内容>" \         # 要写入的知识文本
  --target <filename.md>          # 目标文件（references/ 下）
```

**写入格式（已锁定）：** 沿用现有 `query_patterns.md` 的格式，追加"空行 + decay tag 行 + 内容行"：

```markdown

<!-- decay: type=business_rule confirmed=2026-03-14 C0=1.0 -->
- order_status=5 表示已退款，不是已取消
```

不自动生成 heading。heading 是组织层（分组），不是条目层。条目自动归属到文件末尾最近的 heading 下。Phase 1 的 `--content` 只支持单行文本。

**目标文件不存在时（已锁定）：** 自动创建，使用最小模板：

```markdown
# <文件名转标题>

> 通过五道门治理协议管理。
```

**脚本职责：**
1. 校验 `--type` 是否在 VALID_TYPES 中（复用 `core/parser.py` 的校验）
2. 目标文件不存在时自动创建（最小模板）
3. 生成 decay tag：`confirmed=today, C0=1.0`（alpha/beta 默认为 0，不显式写入新条目）
4. 将空行 + decay tag + `- ` 内容行追加到目标文件
5. 输出写入确认信息（含文件名、行号、知识类型）

**脚本不做的事：**
- 不判断知识是否有价值（Gate 1 是 LLM 的活）
- 不检查是否冲突或重复（Gate 2-3 是 LLM 的活）
- 不决定知识类型（由 LLM 判断后通过 `--type` 传入）
- 不在 tag 中嵌入 source 字段（来源信息通过输出日志和 git 历史追踪）

### 3.5 SKILL.md 指令示例

```
Human injection: When user explicitly shares domain knowledge
  (signals: "记住", "注意这个", "这个要记下来", "remember this")
  → Treat as knowledge candidate
  → Run Gate 1-3 (VALUE / ALIGNMENT / REDUNDANCY) as normal
  → If all pass: run `python $S/decay_engine.py inject --type <t> --content "<c>" --target <f>`
  → If any gate fails: explain why to user, do not write
```

### 3.6 路 B+C 的后续条件

当以下条件满足时考虑路 B：
- 有足够的实验数据判断 AI 识别高价值知识的准确率
- 有明确的"静默标记"机制设计，不打断用户

当以下条件满足时考虑路 C：
- Claude Code 提供会话结束钩子或类似机制
- 路 A 的使用数据显示用户确实会忘记主动触发

---

## 4. 人工修正入口

### 4.1 为什么需要即时修正

错误知识的自然衰减可能需要数月（schema 类 λ=0.003，半衰期 231 天）。如果知识已经累积了 α，有效 λ 更小，衰减更慢。等自然衰减是不可接受的。

### 4.2 修正机制（已锁定）

**人工修正 = 立即将知识置为 REVALIDATE 状态。**

实现方式：通过 `decay_engine.py` 新增 `invalidate` 子命令，**直接修改 C0 而非 beta**：

```bash
python decay_engine.py invalidate --file schema_map.md --line 7
# 效果：C0 设为 0.1，alpha/beta 清零
# C(t) 立即跌入 REVALIDATE 区间（阈值 0.5），无论 t 是多少
```

**为什么不用 beta=99（v2 方案的缺陷）：**

```
C(t) = C0 × e^(-λ_eff × t)
当 t ≈ 0（最近确认的知识）：C(0) = C0 × e^0 = C0 = 1.0
```

beta 只加速未来的衰减速率，但如果知识是最近确认的（t 很小），无论 beta 多大，C(t) 都接近 C0。**beta=99 对最近确认的知识无效。**

**正确方案 — 直接修改 C0：**

| 字段 | invalidate 设置 | 理由 |
|------|----------------|------|
| C0 | **0.1** | 直接将 C(t) 拉到 REVALIDATE（< 0.5），无论 t 是多少 |
| alpha | **0** | 过去的"成功使用"证据已失效 |
| beta | **0** | 旧计数无意义，重新开始 |
| confirmed | 不变 | 事实记录，不伪造 |
| type | 不变 | 知识类型未变 |

### 4.3 触发方式

**第一阶段：显式命令。** 用户说"这条知识有问题"或"这个规则已经变了"，AI 执行 invalidate。

**SKILL.md 指令示例：**

```
Human correction: When user indicates existing knowledge is wrong
  (signals: "这个变了", "这条不对", "这个规则已经废弃了")
  → Identify the knowledge entry in references/
  → Run: python $S/decay_engine.py invalidate --file <f> --line <n>
  → Immediately treat as REVALIDATE: verify with tools before further use
```

### 4.4 与 reset 的区别

| 命令 | 语义 | 场景 |
|------|------|------|
| `reset` | 知识已重新验证为正确，恢复为全新状态 | REVALIDATE 通过后 |
| `invalidate` | 知识被人标记为可能错误，立即进入待验证 | 人工修正触发 |

`invalidate` → REVALIDATE → 工具验证 → `reset`（如果验证通过）或删除条目（如果确认错误）。

---

## 5. CLI 全景：统一的工具接口

更新后，`decay_engine.py` 的完整子命令体系：

```
decay_engine.py
  ├── scan         ← 查看知识置信度状态（已实现）
  ├── feedback     ← 记录使用反馈 success/failure（已实现）
  ├── reset        ← 重验证通过后恢复为全新状态（已实现）
  ├── inject       ← 人工注入新知识（待实现）
  └── invalidate   ← 人工标记知识为待验证（待实现）
```

**所有知识的生命周期操作都通过同一个 CLI 入口。** 这意味着：
- 任何 AI 平台只需要知道如何调用 Python 命令即可集成
- 人类用户在终端也能直接操作（高级场景）
- 所有操作的行为都可以用 pytest 覆盖

---

## 6. 两种使用模式

无论哪种模式，最终都调用同一个 Python CLI，指南只需说明两种入口：

### 6.1 通过 AI 对话（推荐，日常使用）

用户只需自然语言表达，AI 负责判断 + 调用工具：

```
用户：  "记住这个：order_status=5 表示已退款，不是已取消"
AI：    [Gate 1-3 判断] → [调用 inject 命令] → "已记录到 business_rules.md"

用户：  "schema_map 里那条外键关系变了"
AI：    [定位条目] → [调用 invalidate 命令] → "已标记为待验证，下次使用时会重新确认"
```

### 6.2 直接 CLI（高级用户 / 非 AI 环境 / 批量操作）

跳过 LLM 判断，直接操作（用户自行承担 Gate 1-3 的判断责任）：

```bash
# 注入
python decay_engine.py inject \
  --type business_rule \
  --content "order_status=5 表示已退款" \
  --target business_rules.md

# 修正
python decay_engine.py invalidate --file schema_map.md --line 7

# 查看状态
python decay_engine.py scan --path references/
```

---

## 7. 实施路径

### Phase 1：CLI 扩展（已完成 2026-03-14）
- [x] `core/parser.py` 新增 `append_entry()` 追加写入函数
- [x] `core/models.py` 修正 `confidence()` 支持 C0 参数（invalidate 依赖）
- [x] `decay_engine.py` 新增 `inject` 子命令
- [x] `decay_engine.py` 新增 `invalidate` 子命令
- [x] pytest 覆盖：99 个测试全部通过（含 9 个新增）
- [x] SKILL.md 增加 Human Entry Points 指令块
- [x] 端到端验证：inject → scan(TRUST) → invalidate → scan(REVALIDATE) → reset → scan(TRUST)

### Phase 2：智能识别（待条件成熟）
- 路 B：AI 静默标记 + 会话结束确认
- 需要先有路 A 的使用数据作为基线

---

## 8. 设计决策记录（v3 锁定）

以下问题在 v2 中为开放状态，v3 中已全部锁定：

### 已锁定

| # | 问题 | 决策 | 理由 |
|---|------|------|------|
| 1 | inject 写入格式 | 空行 + decay tag + `- ` 内容行，不生成 heading | 沿用 `query_patterns.md` 已验证格式，parser 的 context 机制自动处理归属 |
| 2 | target 文件不存在 | 自动创建（最小模板：标题 + 说明注释） | 优于报错；已有文件预建好，新场景按需创建 |
| 3 | invalidate 机制 | 设 C0=0.1, α=0, β=0（不用 beta=99） | beta=99 对 t≈0 数学上无效（详见 §4.2 证明） |
| 4 | source 字段 | Phase 1 不加入 tag 格式 | 纯审计元数据，不参与计算；改 parser 成本高收益低；git 历史已可追溯来源 |

### 延后到 Phase 2

| # | 问题 | 等待条件 |
|---|------|---------|
| 5 | 路 B 识别粒度 | 需要路 A 的使用数据作为基线，评估 AI 识别准确率 |
| 6 | source 字段扩展 | 若有真实分析需求（如统计人类 vs AI 贡献比），再作为独立改动加入 |

---

*创建日期：2026-03-14*
*v2 更新：2026-03-14 — 从 slash command 方案演进为 Python CLI 方案*
*v3 更新：2026-03-14 — 锁定所有开放问题，设计定稿，可进入开发*
*来源：design-question.md 第三、四节蒸馏 + 对话讨论*
*关联文档：`bayesian-feedback-design.md`（确认偏差防线）*
