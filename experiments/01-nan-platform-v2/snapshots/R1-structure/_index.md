# Domain Knowledge Index

> Routing table for selective knowledge loading. Read this first, then navigate to relevant topic only.

| Topic File | Summary | When to Load | Min Confidence |
|-----------|---------|-------------|----------------|
| `schema_map.md` | 29 tables, entity relationships (building→floor→room, employee→settle→record), 9 JOIN paths | Need to know where data lives or how tables relate | 1.00 |
| `query_patterns.md` | SQL templates (TBD) + 3 tool pitfalls (!=, Chinese, data gaps) | Running data queries or avoiding known tool issues | 0.98 |
| `business_rules.md` | 13 dictionary enums, dict JOIN convention, field naming | Interpreting field values, filtering conditions, or dictionary lookups | 1.00 |
| `investigation_flows.md` | Multi-step investigation procedures (template, TBD) | Complex investigation requiring a sequence of queries + judgment | — (template only) |
