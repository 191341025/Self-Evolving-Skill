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
