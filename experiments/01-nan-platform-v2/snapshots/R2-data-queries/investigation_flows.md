# Investigation Flows

> Reusable multi-step investigation procedures distilled from successful past investigations.
> This file is populated by the AI through real interactions.
> Below are example flows — replace with your actual domain procedures.

## Duplicate Record Check

**Trigger**: Suspecting duplicate records for the same entity and period.

```
Step 1: Identify the entity
  → query by unique identifier (e.g., account_number)
  → get primary key and related IDs

Step 2: Check existing records for that entity + period
  → SELECT with composite key conditions
  → filter by is_active = 1

Step 3: Compare with source data
  → cross-reference upstream tables or import logs

Judgment: If Step 2 returns existing active record for same period,
  new insertion would be a duplicate.
```

## SP Deployed vs Local Comparison

**Trigger**: Before modifying an SP, verify local file matches what's actually deployed.

```
Step 1: Fetch deployed SP source
  → python fetch_structure.py --procedures <SP_NAME> --database <db>

Step 2: Read local file
  → Read the .sql file in db_schemas/

Step 3: Diff key sections
  → Focus on: parameter list, core logic, WHERE conditions
  → Ignore: formatting differences, comment changes

Pitfall: Remote connection may timeout on large SPs. Use --database to target correct db.
```
