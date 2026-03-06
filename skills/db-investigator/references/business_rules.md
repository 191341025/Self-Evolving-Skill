# Business Rules

> Confirmed business logic from code analysis and team communication.
> This file is populated by the AI through real interactions.
> Below are example entries — replace with your actual domain rules.

## Enums

- **order_status**: 1=Pending, 2=Processing, 3=Shipped, 4=Delivered, 9=Cancelled
- **payment_type**: 1=Credit Card, 2=Bank Transfer, 3=Cash

## Processing Rules

- **Duplicate check condition**: `customer_id + YEAR(order_date) + MONTH(order_date) + is_active=1`
- **Customer not found** → skip, do not create order

## Key Field Conventions

- `is_active = 1` is the standard soft-delete filter across all major tables
- `created_at` / `updated_at` are auto-managed timestamp fields
