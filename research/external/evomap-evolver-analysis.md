# EvoMap Evolver 项目深度分析

> 基于 evolver v1.29.5 源码的架构理解文档。
> 用于与 Self-Evolving Skill 五道门协议的对比研究和集成探索。

---

## 1. 项目定位

**Evolver** 是 EvoMap 生态中的核心引擎 — 一个 **GEP (Genome Evolution Protocol)** 驱动的 AI agent 自我进化系统。

核心能力：
- 分析 agent 运行历史，识别失败和低效模式
- 自主生成代码补丁并应用（受约束的自我修改）
- 通过 A2A (Agent-to-Agent) 协议与 Hub 共享进化成果
- 将成功的进化模式蒸馏为可复用的 Gene/Skill

**一句话总结**：Evolver 让 AI agent 能检视自己的运行记录，发现问题，写补丁修复，验证通过后固化为经验（Capsule），最终蒸馏为可共享的技能（Skill）。

---

## 2. 核心概念（生物学隐喻）

EvoMap 大量使用生物学隐喻，理解这些概念是理解代码的前提：

### 2.1 Gene（基因）

**定义**：一个可复用的进化策略模板。

```json
{
  "type": "Gene",
  "id": "gene_auto_a1b2c3d4",
  "category": "repair | optimize | innovate",
  "signals_match": ["log_error", "protocol_drift"],
  "preconditions": ["signals_key == xxx"],
  "strategy": [
    "Extract structured signals from logs",
    "Apply smallest reversible patch",
    "Validate using declared validation steps"
  ],
  "constraints": {
    "max_files": 12,
    "forbidden_paths": [".git", "node_modules"]
  },
  "validation": ["node scripts/validate-modules.js"],
  "epigenetic_marks": []
}
```

**关键字段**：
- `signals_match` — 触发条件，类似五道门的 Gate 1 VALUE 判断
- `strategy` — 执行步骤（给 AI agent 的指令）
- `constraints` — 硬性约束（最大文件数、禁止路径）
- `validation` — 验证命令（固化前必须通过）
- `epigenetic_marks` — 环境适应标记（成功环境 +boost，失败环境 -boost）

### 2.2 Capsule（胶囊）

**定义**：一次成功进化的完整记录，包含触发条件、使用的 Gene、结果、diff。

类比五道门：Capsule ≈ 通过全部五道门后写入 references/ 的一条知识，但 Capsule 还包含了代码 diff 和置信度评分。

**关键字段**：
- `trigger` — 什么信号触发了这次进化
- `gene` — 使用了哪个 Gene
- `confidence` — 置信度 (0-1)
- `success_streak` — 连续成功次数
- `a2a.eligible_to_broadcast` — 是否有资格发布到 Hub

### 2.3 EvolutionEvent（进化事件）

**定义**：每次进化尝试（无论成败）的审计记录，append-only。

存储在 `assets/gep/events.jsonl`，形成 parent→child 的树状链。类比五道门的演化日志 (evolution-log)，但更结构化。

### 2.4 Signal（信号）

**定义**：从运行日志/用户指令中提取的结构化标签。

```
log_error, protocol_drift, windows_shell_incompatible,
user_feature_request, perf_bottleneck, stable_success_plateau
```

Signal 是整个系统的输入 — Gene 选择、Capsule 匹配、候选生成都依赖 Signal。

### 2.5 Epigenetic Mark（表观遗传标记）

**定义**：记录 Gene 在特定环境下的表现，不改变 Gene 本身但影响其"表达强度"。

- 成功 → boost +0.05（最大 +0.5）
- 失败 → boost -0.1（最小 -0.5）
- 90 天后自动衰减清除，最多保留 10 个标记

这与五道门的置信度衰减模型思路相似 — 都是"用反馈调整知识的可信度" — 但实现差距很大：
- **五道门（最新设计）**：`C(t) = e^(-λ_base × (β+1)/(α+1) × t)`，贝叶斯乘法因子动态调整 λ，值域 (0, +∞)，连续衰减
- **Evolver**：加法 boost ±0.05/0.1，硬上下限 ±0.5，90 天硬截断

详细对比见 [6.4 节](#64-衰减模型演进对比evolver-epigenetic-marks-vs-五道门贝叶斯-λ)。

---

## 3. 架构总览

### 3.1 目录结构

```
evolver/
├── index.js              ← CLI 入口（run/solidify/review/distill/asset-log）
├── src/
│   ├── evolve.js         ← 进化主循环（信号提取 → Gene选择 → 执行 → 固化）
│   ├── canary.js         ← 金丝雀检查（验证 index.js 能否正常加载）
│   ├── gep/              ← GEP 协议核心模块
│   │   ├── solidify.js   ← ★ 固化引擎（1680行，核心中的核心）
│   │   ├── selector.js   ← Gene/Capsule 选择器（信号匹配 + 漂移）
│   │   ├── candidates.js ← 候选能力提取（从 transcript 中识别模式）
│   │   ├── signals.js    ← 信号提取器
│   │   ├── mutation.js   ← 变异类型与风险评估
│   │   ├── personality.js← 人格状态（影响风险容忍度）
│   │   ├── skillDistiller.js  ← ★ 技能蒸馏（Capsule → Gene）
│   │   ├── skillPublisher.js  ← ★ 技能发布（Gene → SKILL.md → Hub）
│   │   ├── assetStore.js      ← 资产存储（genes.json, capsules.json, events.jsonl）
│   │   ├── memoryGraph.js     ← 记忆图谱
│   │   ├── contentHash.js     ← 内容哈希（资产去重）
│   │   ├── sanitize.js        ← 敏感信息清洗（发布前）
│   │   ├── validationReport.js← 验证报告构建
│   │   ├── llmReview.js       ← LLM 二次审查
│   │   ├── a2aProtocol.js     ← A2A 通信协议
│   │   ├── hubSearch.js       ← Hub 搜索（复用已有 Gene）
│   │   ├── hubReview.js       ← Hub 评价（对复用资产打分）
│   │   ├── narrativeMemory.js ← 叙事记忆
│   │   ├── taskReceiver.js    ← Hub 任务接收与完成
│   │   └── paths.js           ← 路径常量
│   └── ops/              ← 运维模块
│       ├── lifecycle.js  ← 生命周期管理
│       ├── self_repair.js← 自修复
│       ├── health_check.js← 健康检查
│       └── ...
├── assets/gep/           ← GEP 资产存储
│   ├── genes.json        ← Gene 池
│   ├── capsules.json     ← 成功胶囊
│   └── events.jsonl      ← 进化事件流（append-only）
├── scripts/              ← 工具脚本
│   ├── a2a_export.js     ← 导出资产
│   ├── a2a_ingest.js     ← 导入资产
│   ├── a2a_promote.js    ← 晋升资产
│   └── publish_public.js ← 公开发布
└── test/                 ← 测试
```

### 3.2 模块依赖关系

```
index.js
  ├── evolve.js  (run 命令)
  │     ├── signals.js        → 提取信号
  │     ├── selector.js       → 选择 Gene + Capsule
  │     ├── candidates.js     → 生成候选能力
  │     ├── hubSearch.js      → 搜索 Hub 已有方案
  │     ├── mutation.js       → 构建变异
  │     ├── personality.js    → 选择人格
  │     └── solidify.js       → 写入状态供固化读取
  │
  └── solidify.js  (solidify 命令)
        ├── assetStore.js     → 读写 Gene/Capsule/Event
        ├── memoryGraph.js    → 记忆图谱查询
        ├── selector.js       → 重新选择/确认 Gene
        ├── mutation.js       → 验证变异合法性
        ├── personality.js    → 验证人格合法性
        ├── validationReport.js → 构建验证报告
        ├── llmReview.js      → LLM 二次审查
        ├── a2aProtocol.js    → 发布到 Hub
        ├── sanitize.js       → 发布前清洗
        ├── narrativeMemory.js→ 记录叙事
        ├── hubReview.js      → 对复用资产评价
        └── skillDistiller.js → 触发蒸馏
              └── skillPublisher.js → 发布 Skill 到 Hub
```

---

## 4. 核心流程

### 4.1 完整进化周期

```
用户/cron 触发
      │
      ▼
  ┌─────────┐
  │ evolve() │  ← src/evolve.js
  └────┬──────┘
       │
       ▼
  提取 Signals (signals.js)
       │
       ▼
  选择 Gene + Capsule (selector.js)
  ┌────────────────────────────┐
  │ scoreGene(): 信号匹配打分   │
  │ driftIntensity: 种群漂移    │
  │ bannedGeneIds: 失败基因禁用 │
  └────────────────────────────┘
       │
       ▼
  搜索 Hub (hubSearch.js)
  ┌─────────────────────────┐
  │ 是否有已验证的外部方案？  │
  │ → reuse / reference     │
  └─────────────────────────┘
       │
       ▼
  构建变异 (mutation.js)
  构建 GEP Prompt (prompt.js)
       │
       ▼
  *** AI agent 执行变更 ***
  （写代码、改文件、修 bug）
       │
       ▼
  写入状态 → evolution_solidify_state.json
       │
       ▼
  ┌───────────┐
  │ solidify() │  ← src/gep/solidify.js（可立即或延后执行）
  └────┬───────┘
       │
       ▼
  （见 4.2 固化详细流程）
```

### 4.2 solidify() 固化流程（核心 1680 行）

这是整个系统最重要的函数。它决定一次进化变更是否被接受：

```
solidify()
    │
    ├─ 1. 读取状态 (evolution_solidify_state.json)
    │     → 获取 selected_gene_id, signals, mutation, personality_state
    │
    ├─ 2. 协议合规检查
    │     → mutation 是否有效？
    │     → personality_state 是否有效？
    │     → 高风险变异是否被人格允许？
    │     → intent 是否与 mutation.category 一致？
    │
    ├─ 3. 确保 Gene (ensureGene)
    │     → 有选中的就用，没有就重新匹配或自动创建
    │
    ├─ 4. 计算爆炸半径 (computeBlastRadius)
    │     → git diff 统计变更文件数和行数
    │     → 排除 baseline 前已有的 untracked 文件
    │
    ├─ 5. 约束检查 (checkConstraints)        ★ 最接近五道门的部分
    │     ├─ 爆炸半径分级: within_limit → approaching → exceeded → critical → hard_cap
    │     ├─ 系统硬上限: 60 文件 / 20000 行（不可覆盖）
    │     ├─ Gene 软上限: max_files（默认 20）
    │     ├─ 禁止路径检查: forbidden_paths
    │     ├─ 关键路径保护: CRITICAL_PROTECTED_PREFIXES/FILES
    │     ├─ 自我修改保护: 除非 EVOLVE_ALLOW_SELF_MODIFY=true
    │     ├─ 新 Skill 完整性: 目录至少 2 个文件
    │     ├─ 伦理审查: 禁止绕过安全/隐蔽监控/社工攻击等
    │     └─ 破坏性变更检测: 关键文件被删除或清空
    │
    ├─ 6. 运行验证 (runValidations)
    │     → 执行 gene.validation 中声明的命令
    │     → 仅允许 node/npm/npx 前缀，禁止 shell 操作符
    │
    ├─ 7. 金丝雀检查 (runCanaryCheck)
    │     → 在子进程中验证 index.js 能否正常加载
    │     → 最后一道安全网
    │
    ├─ 8. LLM 审查 (可选, EVOLVER_LLM_REVIEW=1)
    │     → 提交 diff 给 LLM 做二次审查
    │
    ├─ 9. 判定结果
    │     success = 约束通过 && 验证通过 && 协议合规
    │
    ├─ 10a. 成功路径:
    │     → 构建 Capsule (含 diff, strategy, 置信度)
    │     → 更新 Gene 的 epigenetic_marks
    │     → 追加 EvolutionEvent 到 events.jsonl
    │     → 写入 Capsule 到 capsules.json
    │     → 计算 success_streak，判断是否可发布
    │     → 自动发布到 Hub (如果 eligible)
    │     → 触发蒸馏检查 (shouldDistill)
    │     → 完成 Hub 任务 (如果是任务驱动)
    │     → 提交 Hub 评价 (如果复用了外部资产)
    │
    └─ 10b. 失败路径:
          → 保存 FailedCapsule (含 diff snapshot)
          → 回滚: git reset --hard 或 git stash
          → 清理新增的 untracked 文件
          → 发布 anti-pattern 到 Hub (可选)
          → 记录失败原因到 event
```

### 4.3 Publish 流程（Gene → Skill → Hub）

```
solidify() 成功
    │
    ├─ 1. 判断发布资格
    │     eligible = blastRadiusSafe && score >= 0.7 && streak >= 2
    │
    ├─ 2. 构建发布包 (buildPublishBundle)
    │     → sanitizePayload(): 清洗敏感信息
    │     → Gene + Capsule + Event 打包
    │
    └─ 3. HTTP POST → Hub /a2a/skill/store/publish
          → 201/200 = 成功
          → 409 = 已存在 → 调用 updateSkillOnHub (PUT)


独立流程: 蒸馏 (Distillation)
    │
    ├─ shouldDistill() 检查: 最近 10 个 Capsule 中 7+ 成功，总成功数 >= 10
    │
    ├─ prepareDistillation():
    │     → 聚合成功 Capsule，按 Gene 分组
    │     → 分析模式: 高频 Gene、策略漂移、覆盖空白
    │     → 生成 LLM prompt → 写入文件
    │
    ├─ completeDistillation(llmResponse):
    │     → 从 LLM 响应中提取 Gene JSON
    │     → validateSynthesizedGene(): 验证字段、去重、安全检查
    │     → 写入 genes.json
    │
    └─ publishSkillToHub(gene):
          → geneToSkillMd(): Gene → SKILL.md 格式
          → HTTP POST → Hub
```

---

## 5. 安全与治理机制

Evolver 内建了多层安全机制，以下按执行顺序列出：

| 层级 | 机制 | 位置 | 说明 |
|------|------|------|------|
| 1 | 协议合规 | solidify L1044-1057 | mutation/personality 必须有效 |
| 2 | 爆炸半径 | solidify L264-296 | 分级：approaching → exceeded → critical → hard_cap |
| 3 | 系统硬上限 | solidify L410-411 | 60 文件 / 20000 行，任何 Gene 不可覆盖 |
| 4 | 禁止路径 | solidify L300-304 | gene.constraints.forbidden_paths |
| 5 | 关键路径保护 | solidify L500-542 | 10 个核心 Skill 目录 + 12 个根文件不可修改 |
| 6 | 自我修改保护 | solidify L311-322 | 默认禁止修改 evolver 自身 |
| 7 | 伦理审查 | solidify L351-373 | 正则匹配：绕过安全/隐蔽监控/社工/利用人类 |
| 8 | 破坏性变更检测 | solidify L544-576 | 关键文件被删除或清空 → violation |
| 9 | 验证命令安全 | solidify L579-590 | 仅允许 node/npm/npx，禁止 shell 操作符 |
| 10 | Gene 验证 | solidify L592-610 | 执行 gene.validation 声明的测试命令 |
| 11 | 金丝雀检查 | solidify L616-630 | 子进程加载 index.js，验证不崩溃 |
| 12 | LLM 二次审查 | solidify L1122-1143 | 可选：提交 diff 给 LLM 做独立审查 |
| 13 | 失败回滚 | solidify L673-697 | git reset --hard / git stash |
| 14 | 发布前清洗 | sanitize.js | sanitizePayload() 清除敏感信息 |
| 15 | 表观遗传 | solidify L861-934 | 失败环境被标记抑制，成功环境被强化 |

---

## 6. 与五道门协议的映射分析

### 6.1 对应关系

| 五道门 | Evolver 对应机制 | 覆盖程度 |
|--------|-----------------|---------|
| **Gate 1: VALUE** — 知识是否有复用价值？ | `selector.js: scoreGene()` 信号匹配 + `candidates.js` 候选提取 | **部分覆盖** — Evolver 判断"哪个 Gene 匹配"而非"这条知识值不值得存" |
| **Gate 2: ALIGNMENT** — 与现有知识一致？ | `checkConstraints()` 中的禁止路径 + 破坏性检测 | **弱覆盖** — 检查的是文件冲突，不是语义一致性 |
| **Gate 3: REDUNDANCY** — 是否重复？ | `contentHash.js: computeAssetId()` 内容哈希去重 | **部分覆盖** — 哈希去重是精确匹配，缺乏语义去重 |
| **Gate 4: FRESHNESS** — 知识是否新鲜？ | `epigenetic_marks` 90天硬截断 + `shouldDistill()` 时间间隔 | **弱覆盖** — 没有连续衰减模型，只有二元的"在有效期/过期" |
| **Gate 5: PLACEMENT** — 放在正确位置？ | Gene 的 `constraints` + `isCriticalProtectedPath()` | **部分覆盖** — 控制"不能放哪"，没有"应该放哪"的路由 |

### 6.2 Evolver 有而五道门没有的

| Evolver 机制 | 说明 | 五道门可借鉴？ |
|-------------|------|-------------|
| **爆炸半径分级** | within → approaching → exceeded → critical → hard_cap | 可以。五道门目前没有对知识体量的分级预警 |
| **金丝雀检查** | 固化前在隔离环境验证不会崩溃 | 可以。知识写入后验证一次查询是否正常 |
| **表观遗传标记** | 同一知识在不同环境下表现不同 | 可以。跨数据库复用时标记适用环境 |
| **失败胶囊** | 保存失败的 diff 和原因，用于后续学习 | 可以。当前五道门拒绝了就丢弃，不记录 |
| **A2A 发布/复用** | 成功经验发布到 Hub，其他节点可复用 | 可以。但五道门面向单 agent，暂无网络层 |
| **蒸馏** | 多个 Capsule 聚合为更通用的 Gene | 可以。多次实验的共性知识蒸馏为通用模板 |

### 6.3 五道门有而 Evolver 没有的

| 五道门机制 | 说明 | Evolver 的空白 |
|-----------|------|---------------|
| **连续置信度衰减 + 贝叶斯反馈** | 基础公式 `C(t) = e^(-λt)` 已扩展为 `C(t) = e^(-λ_base × (β+1)/(α+1) × t)`，λ 不再是固定值而是被使用反馈动态调整 | Evolver 只有 90 天硬截断 + 离散 boost ±0.05/0.1，没有连续衰减也没有乘法因子调整 |
| **语义对齐检查** | Gate 2 比对新知识与已有知识的语义一致性 | Evolver 只检查文件路径冲突，不做语义对比 |
| **知识类型分类** | schema/tool_experience/business_rule/query_pattern/data_range/data_snapshot，6 种类型各有不同 λ_base | Evolver 的 Gene category 只有 repair/optimize/innovate 三类 |
| **三级响应协议** | TRUST / VERIFY / REVALIDATE | Evolver 没有基于置信度的差异化使用策略 |
| **分层加载** | frontmatter → body → references/ 按需加载 | Evolver 每次全量加载 genes.json + capsules.json |

### 6.4 衰减模型演进对比：Evolver epigenetic marks vs 五道门贝叶斯 λ

两个项目独立走到了同一个直觉 — **用使用反馈调整知识的老化速率** — 但实现路径不同：

| 维度 | 五道门（当前设计） | Evolver applyEpigeneticMarks() |
|------|-------------------|-------------------------------|
| **公式** | `λ_eff = λ_base × (β+1)/(α+1)` | `boost = clamp(boost ± delta, -0.5, 0.5)` |
| **调整方式** | 乘法因子，作用于衰减速率本身 | 加法增量，作用于选择权重 |
| **值域** | (0, +∞)，可以比原速快任意倍 | [-0.5, +0.5]，人为硬上下限 |
| **成功时** | α+1 → 分母变大 → λ_eff 变小 → 衰减变慢 | boost +0.05（封顶 +0.5） |
| **失败时** | β+1 → 分子变大 → λ_eff 变大 → 衰减变快 | boost -0.1（封底 -0.5） |
| **时间维度** | 连续衰减 `e^(-λt)` | 90 天硬截断，到期直接删 |
| **作用对象** | 知识条目的置信度 | Gene 在特定环境下的选择倾向 |
| **极端行为** | 1000 次全对 → λ_eff ≈ λ/1001（几乎不衰减） | 无论多少次成功，boost 最多 +0.5 |

**五道门方案在数学上严格优于 Evolver**：乘法因子 `(β+1)/(α+1)` 天然无界且极端情况行为合理，不需要人为设定上下限。

**设计进度**（截至 2026-03-13）：
- 合并公式已确定：`C(t) = e^(-λ_base × (β+1)/(α+1) × t)`
- 公式三条核心性质已验证：C(t) > 0 恒成立；成功减缓老化；失败加速老化
- 详细推导和数值验算记录在 `research/design/decay-model-notes.md`
- **待设计**：α/β 的反馈来源和记录机制（知道"公式长什么样"，还没定"数据从哪来"）

---

## 7. Evolver 关键入口命令

```bash
# 运行一次进化周期（分析日志 → 选择策略 → 执行变更）
node index.js run

# 固化变更（验证 → 约束检查 → 写入资产）
node index.js solidify
node index.js solidify --dry-run        # 仅检查不执行
node index.js solidify --intent=repair  # 指定意图

# 人工审查模式（查看变更 → 批准/拒绝）
node index.js review
node index.js review --approve
node index.js review --reject

# 蒸馏（多个成功 Capsule → 通用 Gene）
node index.js distill --response-file=<llm_response.txt>

# 连续循环模式（daemon）
node index.js --loop

# 查看资产操作日志
node index.js asset-log --last=20
```

---

## 8. prePublishGate() 设计空间

solidify.js 的发布逻辑（L1370-1480）目前只检查：

```javascript
eligible = isBlastRadiusSafe(blast_radius)
        && score >= 0.7
        && success_streak >= 2;
```

这里是插入 `prePublishGate()` 的最佳位置 — 在 eligible 判定之后、实际 HTTP 发布之前。

**可注入的五道门检查**：

```
prePublishGate(capsule, gene)
  ├─ VALUE:       capsule.content 是否包含可复用知识（非一次性 fix）？
  ├─ ALIGNMENT:   gene.strategy 是否与 Hub 已有方案冲突？
  ├─ REDUNDANCY:  Hub 上是否已有高度相似的 Skill？
  ├─ FRESHNESS:   capsule 中的知识类型和衰减率如何？
  └─ PLACEMENT:   应该发布到哪个 category/tag？
```

这只是设计空间的初步勾勒，具体实现需要进一步讨论。

---

## 9. 关键文件速查

| 文件 | 行数 | 职责 | 阅读优先级 |
|------|------|------|-----------|
| `src/gep/solidify.js` | 1680 | 固化引擎（核心） | ★★★ |
| `src/evolve.js` | ~1500 | 进化主循环 | ★★★ |
| `src/gep/selector.js` | 250 | Gene/Capsule 选择 | ★★ |
| `src/gep/skillDistiller.js` | 515 | 技能蒸馏 | ★★ |
| `src/gep/skillPublisher.js` | 163 | Skill 发布到 Hub | ★★ |
| `src/gep/candidates.js` | 142 | 候选能力提取 | ★ |
| `src/gep/mutation.js` | ~200 | 变异类型管理 | ★ |
| `src/gep/personality.js` | ~150 | 人格与风险容忍 | ★ |
| `src/gep/a2aProtocol.js` | ~300 | A2A 通信协议 | ★ |
| `src/gep/sanitize.js` | ~100 | 发布前清洗 | ★ |
| `SKILL.md` | 291 | 项目元数据与配置 | ★★ |

---

*分析日期：2026-03-13。基于 evolver v1.29.5 (commit latest on main)。*
*本文档用于 Self-Evolving Skill 项目的跨项目对比研究。*
