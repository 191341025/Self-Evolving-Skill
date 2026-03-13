# Query Patterns

> Pre-built SQL templates for common investigations.
> Auto-populated by the skill through real interactions.

## Tool Usage Notes

<!-- decay: type=tool_experience confirmed=2026-03-08 C0=1.0 -->
- **避免在 SQL 中使用 `!=`**：db_query.py 传参时 `!=` 会被 shell 转义出错，必须用 `<>` 替代

<!-- decay: type=tool_experience confirmed=2026-03-08 C0=1.0 -->
- **先查数据时间范围**：记录表可能有数据空窗期，查趋势前先确认 MIN/MAX 时间戳

<!-- decay: type=tool_experience confirmed=2026-03-08 C0=1.0 -->
- **SQL 中避免中文字符串**：shell 传参含中文可能 exit code 127，用数值字段替代中文字段做 WHERE 条件
