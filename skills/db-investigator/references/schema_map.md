# Schema Map

> This file is populated by the AI through real interactions.
> Below is an example structure — replace with your actual domain knowledge.

## Databases

| Database | Role | Key Tables |
|----------|------|-----------|
| `example_db` | Main application database | orders, customers, products |

## Table Relationships

```
example_db.customers
  ├─ customers.id = orders.customer_id
  └─ customers.status = 'active' (soft-delete filter)

example_db.orders
  ├─ orders.id = order_items.order_id
  └─ orders.created_at → partition key
```

## SP Map

| SP | Database | Role |
|----|----------|------|
| SP_PROCESS_ORDER | example_db | Order processing pipeline entry point |
| SP_GENERATE_REPORT | example_db | Monthly report generation |
