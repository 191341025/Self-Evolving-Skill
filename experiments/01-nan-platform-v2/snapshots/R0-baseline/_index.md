# Domain Knowledge Index

> Routing table for selective knowledge loading. Read this first, then navigate to relevant topic only.

| Topic File | Summary | When to Load | Min Confidence |
|-----------|---------|-------------|----------------|
| `schema_map.md` | Database/table/SP locations and relationships | Need to know where data lives | — (template only) |
| `query_patterns.md` | Pre-built SQL templates + 3 tool pitfalls (!=, Chinese, data gaps) | Running data queries or avoiding known tool issues | 0.98 |
| `business_rules.md` | Confirmed business logic, enums, behavioral rules | Analyzing SP logic or validating data | — (template only) |
| `investigation_flows.md` | Multi-step investigation procedures (duplicate check, validation, SP diff) | Complex investigation requiring a sequence of queries + judgment | — (template only) |

> `Min Confidence` = lowest C(t) among all real (non-template) entries in that file. Recalculated after each knowledge write. `—` means file contains only template placeholders, no real knowledge yet.
