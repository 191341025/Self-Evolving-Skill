# v2 实现计划：知识治理 Skill 开发路线

> **状态**：计划草案（待确认后执行）
> **日期**：2026-04-14
> **前置设计**：`knowledge-lifecycle-v2.md`（两阶段模型 + 向量存储 + 激活机制）
> **原则**：渐进式推进，每个 Phase 有明确的完成标准和验证方式

---

## 1. 目标架构

```
.claude/skills/
├── knowledge-governor/              ← 新 skill：通用知识治理（高频触发）
│   ├── SKILL.md                     ← 触发条件 + 治理协议 + 工具列表
│   ├── scripts/
│   │   ├── core/
│   │   │   ├── formulas.py          ← 复用 v1 + 新增 distill_score
│   │   │   ├── models.py            ← 复用 v1 + 新增 Phase 1 模型
│   │   │   └── vector_store.py      ← 新：向量数据库读写层
│   │   ├── knowledge_engine.py      ← 新 CLI 入口
│   │   └── setup.py                 ← 初始化向量数据库 + embedding 模型
│   └── data/                        ← 向量数据库文件（本地）
│
└── db-investigator/                 ← 现有 skill，保持不动
```

**关键决策**：knowledge-governor 是全新 skill，不改动 db-investigator 的任何代码。两者先独立存在，未来再对接。

---

## 2. 分阶段实现

### Phase 0：技术选型验证

**目标**：锁定向量数据库和中文 embedding 模型。

**任务**：
1. 调研并选定向量数据库（要求：本地运行、Python 集成、文件可携带、中文支持）
2. 调研并选定中文 embedding 模型（要求：本地推理、中文语义质量好、模型体积可接受）
3. 编写最小验证脚本：
   - 安装依赖
   - 写入几条中文知识条目（带 metadata）
   - 测试中文语义检索（"表关系"能检索到"外键关联"吗？）
   - 测试 metadata 过滤（status=CANDIDATE / status=VALIDATED）
   - 确认 Windows 11 + Python 3.11 环境无兼容性问题

**完成标准**：
- 向量数据库 + embedding 模型选型锁定
- 验证脚本在 Windows 环境下运行通过
- 中文语义检索质量可接受

**验证方式**：验证脚本输出 + 人工确认检索结果质量

---

### Phase 1：最小可用 Skill（核心闭环）

**目标**：跑通"捕获 → 存储 → 检索"最短闭环。

**任务**：

#### 1.1 knowledge_engine.py — 3 个核心子命令

| 子命令 | 功能 | 输入 | 输出 |
|--------|------|------|------|
| `capture` | 写入 CANDIDATE | --content, --type, --source-domain | 写入确认 + entry ID |
| `query` | 语义检索 | --question, [--status], [--top-k] | 相关知识列表（含 metadata） |
| `scan` | 扫描条目状态 | [--status], [--type] | 条目统计 + 列表 |

#### 1.2 vector_store.py — 向量数据库封装

- `add_entry(content, metadata) → id`
- `search(query_text, filters, top_k) → results`
- `get_entry(id) → entry`
- `update_metadata(id, metadata)`
- `delete_entry(id)`
- `count(filters) → int`

#### 1.3 SKILL.md — 最简版

- frontmatter：宽触发条件（覆盖大部分工作场景）
- body：
  - 知识检索指令（每轮交互开始时查询相关知识）
  - 知识捕获指令（交互中观察到有价值知识时调用 capture）
  - Gate 1 VALUE 判定规则（快速判断是否值得捕获）
  - 暂不包含完整五道门（Phase 2 加入）

**完成标准**：
- 在真实 Claude Code 会话中，Skill 能被触发
- 能捕获对话中的知识碎片并存入向量数据库
- 下一次会话能检索到之前存入的知识
- pytest 覆盖 vector_store.py 和 knowledge_engine.py

**验证方式**：
- 连续 3-5 个工作会话后检查：捕获了什么？检索质量如何？
- Gate 1 拒绝率观察（大部分交互应该不产生知识写入）

---

### Phase 2：两阶段生命周期

**目标**：实现完整的 distill_score 准入 + C(t) 衰减。

**任务**：

#### 2.1 Phase 1 准入机制

- formulas.py 新增：`distill_score(history, current_time, lambda_d)` — 计算累积准入分
- models.py 新增：`classify_candidate(score, T_promote, T_expire)` — CANDIDATE / VALIDATED / EXPIRED
- knowledge_engine.py 新增子命令：
  - `confirm`：记录一次确认事件（--id, --wc, --wr）→ 更新 distill_history
  - `promote`：扫描并晋升达标 CANDIDATE → VALIDATED
  - `expire`：清理低于淘汰线的 CANDIDATE

#### 2.2 Phase 2 保鲜机制

- 移植 v1 的 confidence() + classify_confidence() 到向量数据库场景
- knowledge_engine.py 新增子命令：
  - `feedback`：记录使用反馈（--id, --result success/failure, [--weight]）
  - `freshness`：扫描所有 VALIDATED 条目，输出 TRUST/VERIFY/REVALIDATE 分布

#### 2.3 SKILL.md 扩展

- 加入完整五道门协议（适配向量数据库）
- Gate 2 ALIGNMENT：向量相似度 + LLM 矛盾判断
- Gate 3 REDUNDANCY：向量相似度去重
- 反馈指令：使用知识后的自然反馈路径

#### 2.4 五道门协议完整集成

将 Phase 1 的简单 Gate 1 扩展为完整的五道门流程，每条知识写入前走完 Gate 1-5。

**完成标准**：
- CANDIDATE → VALIDATED 晋升流程端到端跑通
- 衰减扫描输出 TRUST/VERIFY/REVALIDATE 分布
- 不对称反馈（success_w=0.3, error_w=1.5）验证
- pytest 覆盖新增的所有函数

**验证方式**：
- 10+ 个会话后观察：哪些 CANDIDATE 被晋升了？合理吗？
- 模拟时间推移后扫描衰减状态

---

### Phase 3：打磨与调参

**目标**：基于真实使用数据优化，达到日常可用状态。

**任务**：
- 阈值调参：T_promote, T_expire, λd, Wc/Wr 参考值
- SKILL.md 指令优化：根据 LLM 实际遵循情况迭代
- /harvest 补充模式（如果核心模式的捕获有遗漏）
- Knowledge-First Response 策略打磨
- 可能的 db-investigator 对接

**完成标准**：
- 日常使用 2-4 周后，能明显感知"回答越来越准确"
- 知识库中 VALIDATED 条目质量经人工审核确认

**验证方式**：
- 端到端体验验证
- 知识库快照审计

---

## 3. 测试策略

### 三层递进

| 层级 | 时机 | 场景 | 验证目标 |
|------|------|------|---------|
| 技术验证 | Phase 0-1 | 构造数据 + pytest | 技术栈能跑通，API 正确 |
| 自我验证 | Phase 1 起 | 用 skill 开发 skill 本身 | 知识捕获和检索的实际质量 |
| 业务验证 | Phase 2-3 | 真实项目工作（如 TEMS） | "同样的模型，返回越来越准确" |

### 关键检查点

| # | 检查点 | 时机 | 通过标准 |
|---|--------|------|---------|
| 1 | 中文语义检索质量 | Phase 0 | "表关系"能检索到"外键关联" |
| 2 | 知识捕获率 | Phase 1 后 3-5 会话 | 有意义的捕获 > 0，Gate 1 拒绝率 > 50% |
| 3 | 检索召回 | Phase 1 后 | 已存入的相关知识能被正确检索到 |
| 4 | 晋升合理性 | Phase 2 后 10+ 会话 | VALIDATED 的都是真正高价值知识 |
| 5 | 衰减效果 | Phase 2 后 2-4 周 | TRUST/VERIFY/REVALIDATE 分布合理 |
| 6 | 端到端价值 | Phase 3 | 可感知的"越来越准确" |

---

## 4. 技术选型（待 Phase 0 锁定）

### 向量数据库

**选型标准**：
- 本地运行，无需服务进程
- Python 集成（pip install）
- 文件可随项目目录携带
- 支持中文 embedding（自定义 embedding function 或内置中文模型）
- Metadata 过滤
- Windows 11 兼容

**已锁定：LanceDB**（2026-04-14）

选型理由：存储效率最优（7KB/3条 vs ChromaDB 1.8MB）、API 最 Pythonic（Pandas + SQL WHERE）、依赖最轻量（8个）、Windows 实测通过。淘汰 ChromaDB（依赖重）、sqlite-vec（API 低级）、Milvus Lite（不支持 Windows）。

安装：`pip install lancedb`

### 中文 Embedding 模型

**已锁定：BAAI/bge-small-zh-v1.5**（2026-04-14）

选型理由：~90MB 体积、512 维向量、C-MTEB 小模型最优、CPU 亚秒推理。升级路径清晰：bge-base-zh（768维）→ bge-large-zh（1024维），API 一致只换模型名。

安装：`pip install sentence-transformers`（首次使用自动下载模型）

> 注意：当前环境 torch/torchvision 可能有版本兼容问题，需 `pip install torchvision --upgrade` 修复。

---

## 5. 风险与缓解

| 风险 | 影响 | 缓解策略 |
|------|------|---------|
| Embedding 模型加载慢，影响 Skill 响应速度 | 用户体验差 | Phase 0 实测加载时间；考虑模型缓存/预加载 |
| 中文语义检索质量不足 | 知识检索召回率低 | Phase 0 用真实中文知识测试；必要时换模型 |
| Skill 高频触发的 context window 开销过大 | 正常工作受影响 | SKILL.md 保持精简；知识按需加载不全量注入 |
| 向量数据库在 Windows 上有兼容性问题 | 无法使用 | Phase 0 提前验证；准备备选方案 |
| LLM 不遵循知识捕获指令 | 捕获率低 | 参考 v1 SKILL.md 迭代经验；Phase 3 专项优化 |

---

## 6. 与现有资产的关系

### 直接复用

| 资产 | 来源 | 复用方式 |
|------|------|---------|
| 衰减公式 | v1 `core/formulas.py` | 复制到新 skill，新增 distill_score |
| 置信度模型 | v1 `core/models.py` | 复制到新 skill，新增 Phase 1 分类 |
| 五道门协议 | v1 SKILL.md | 适配向量数据库后写入新 SKILL.md |
| 测试框架 | v1 `scripts/tests/` | 复用 conftest 和测试模式 |

### 不复用

| 资产 | 原因 |
|------|------|
| `parser.py`（MD 标签解析） | 被 `vector_store.py` 替代 |
| `decay_engine.py`（CLI） | 被 `knowledge_engine.py` 替代（逻辑重新组织） |
| `references/`（MD 知识文件） | 被向量数据库替代 |
| `_index.md`（路由表） | 被向量检索替代 |

### db-investigator 保持不动

db-investigator 作为独立的领域 skill 继续存在，其工具（db_query/fetch_structure/fetch_index）和知识管理（v1 的 MD 方案）不受影响。未来 Phase 3+ 考虑让 db-investigator 的知识治理委托给 knowledge-governor。

---

*本文档记录实现计划，随进展更新各 Phase 的状态。*
