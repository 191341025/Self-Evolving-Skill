# Research & Design Documents

本目录存放项目的设计文档和研究资料。

## 目录结构

```
research/
├── README.md                ← 本文件（文档索引）
├── design/                  ← 我们自己的设计规格
│   ├── bayesian-feedback-design.md   α/β 反馈机制设计草案
│   └── decay-model-notes.md          置信度衰减模型推导笔记
└── external/                ← 外部项目研究（学习参考，非设计目标）
    └── evomap-evolver-analysis.md    EvoMap Evolver 架构分析
```

## design/ — 设计文档

| 文件 | 状态 | 说明 |
|------|------|------|
| `decay-model-notes.md` | 已完成 | 衰减公式 `C(t) = e^(-λt)` 的推导，贝叶斯扩展 `λ_eff = λ_base × (β+1)/(α+1)` 的完整论证，含数值验算 |
| `bayesian-feedback-design.md` | 草案待评审 | α/β 反馈信号的来源定义、按知识类型的反馈分析、元数据格式扩展、实施路径 |

## external/ — 外部研究

| 文件 | 说明 |
|------|------|
| `evomap-evolver-analysis.md` | EvoMap Evolver 项目的架构理解，含与五道门协议的映射对比。仅作参考，不作为设计约束 |
