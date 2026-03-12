# Query Patterns

> Pre-built SQL templates for common investigations.
> This file is populated by the AI through real interactions.
> Below are example patterns — replace with your actual domain queries.

## Order Analysis (example_db)

```sql
-- Status distribution
SELECT status, COUNT(*) FROM orders
WHERE is_active = 1
GROUP BY status ORDER BY status;

-- Find orders for customer + month
SELECT id, order_number, created_at, status
FROM orders WHERE customer_id = <CUSTOMER_ID>
AND YEAR(created_at) = <YYYY> AND MONTH(created_at) = <MM>
AND is_active = 1;
```

## Customer Lookup (example_db)

```sql
-- Check if customer exists
SELECT id, name, account_number, status
FROM customers WHERE account_number = '<ACCOUNT>'
AND is_active = 1;
```

## Tool Usage Notes

<!-- decay: type=tool_experience confirmed=2026-03-08 C0=1.0 -->
- **避免在 SQL 中使用 `!=`**：db_query.py 传参时 `!=` 会被 shell 转义出错，必须用 `<>` 替代

<!-- decay: type=tool_experience confirmed=2026-03-08 C0=1.0 -->
- **先查数据时间范围**：记录表可能有数据空窗期，查趋势前先确认 MIN/MAX 时间戳

<!-- decay: type=tool_experience confirmed=2026-03-08 C0=1.0 -->
- **SQL 中避免中文字符串**：shell 传参含中文可能 exit code 127，用数值字段替代中文字段做 WHERE 条件

<!-- decay: type=tool_experience confirmed=2026-03-12 C0=1.0 -->
- **t_room.rent_status 全为 NULL**：不能用 rent_status 判断房间入住，必须通过 `t_employee_settle WHERE settle_status = 'settle_in'` + `GROUP BY room_id` 统计实际入住房间数
