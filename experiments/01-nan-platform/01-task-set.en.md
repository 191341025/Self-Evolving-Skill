# Experiment Task Set

> Design principle: Cover the full difficulty gradient from simple queries to complex multi-step investigations. Each task may trigger a Five-Gate decision.
> Tasks are executed in rounds; after each round, check for changes in references/.

## Round 1: Structural Exploration (Let the Skill learn the database)

| # | Task | Expected Knowledge Tier |
|---|------|------------------------|
| 1.1 | What tables exist in this database? What is the business purpose of each? | schema_map |
| 1.2 | What is the relationship between buildings, floors, and rooms? | schema_map |
| 1.3 | How are employees linked to settle-in records? | schema_map |
| 1.4 | Which field associates access records with employees? | schema_map |
| 1.5 | How is the dictionary system designed? List all dictionary types and values. | schema_map + business_rules |

## Round 2: Data Investigation (Single-step queries)

| # | Task | Expected Knowledge Tier |
|---|------|------------------------|
| 2.1 | How many buildings are there? What are their types? | query_patterns |
| 2.2 | How many rooms does each building have? What is the occupancy rate? | query_patterns |
| 2.3 | What is the gender and age distribution of currently residing employees? | query_patterns |
| 2.4 | What is the trend of access records over the past week? | query_patterns |
| 2.5 | What is the device status distribution? How many faulty devices are there? | query_patterns |
| 2.6 | Which building has the highest device density? | query_patterns |

## Round 3: Business Rule Discovery (Requires reasoning)

| # | Task | Expected Knowledge Tier |
|---|------|------------------------|
| 3.1 | Is the meaning of the status field consistent across tables? What does '1' mean? | business_rules |
| 3.2 | Are there employees with settle-in records whose settle_status is not settle_in? | business_rules |
| 3.3 | What does the result field in emp_record store? What are its possible values? | business_rules |
| 3.4 | Are there employees with expired ID cards still active in the system? | business_rules |
| 3.5 | Are there anomalies in access records such as "entry without exit" or "exit without entry"? | business_rules |

## Round 4: Complex Investigation (Multi-step)

| # | Task | Expected Knowledge Tier |
|---|------|------------------------|
| 4.1 | Find the building with the lowest occupancy rate and analyze the cause — many rooms but few residents, or few rooms to begin with? | investigation_flows |
| 4.2 | Build a full profile of a random employee who has records: basic info, settle-in location, access frequency. | investigation_flows |
| 4.3 | Compare the management status of two buildings: occupancy rate, device count, access activity. | investigation_flows |
| 4.4 | Find "ghost employees": people with settle-in records but no access records in the past 30 days. | investigation_flows |
| 4.5 | Analyze access peak hours and identify the morning and evening rush time windows. | investigation_flows |

## Round 5: Repetition & Evolution Verification (Redo earlier tasks to see if the Skill is faster and more accurate)

| # | Task | Verification Goal |
|---|------|-------------------|
| 5.1 | Ask again: "What is the occupancy rate of each building?" | Does it directly use an existing template from query_patterns? |
| 5.2 | Query again: "Employee age distribution" | Does it skip the structural exploration phase? |
| 5.3 | Redo the "ghost employees" investigation | Does it use the flow from investigation_flows? |
| 5.4 | Ask a new question that has not been asked before | Compare response speed and accuracy with Round 1. |

## Post-Round Checklist

After completing each round, record the following in the evolution log:

1. **references/ change diff**: Which files were modified? What content was added?
2. **Five-Gate decision log**: Record the decision process each time the Five-Gate was triggered (especially rejections).
3. **Quality assessment**: Is the newly added knowledge accurate? Is there a risk of bloat?
4. **Efficiency comparison**: For repeated tasks, was the response faster than the first time?
