# Investigation Flows

Reusable multi-step investigation procedures distilled from successful past investigations.

## Employee Profile (Complete Portrait)

**Trigger**: Need full picture of a specific employee.

```
Step 1: Locate employee
  → SELECT from t_employee WHERE id_card='<ID_CARD>' or name/id
  → Get employee.id and id_card

Step 2: Basic info + settlement
  → JOIN t_employee_settle on emp_id → get building/floor/room
  → JOIN t_building/t_floor/t_room for human-readable names
  → Key fields: name, gender, age, emp_type, native_place, phone, start_time, end_time

Step 3: Entry/exit activity
  → SELECT from t_emp_record WHERE id_card = <id_card>
  → Aggregate: total, in_cnt, out_cnt, first_seen, last_seen, avg score

Pitfall: t_emp_record 通过 id_card 关联（不是 employee.id）
```

## Ghost Employee Audit

**Trigger**: Find employees who are "settled in" but have no recent activity.

```
Step 1: Count ghosts
  → settle_status='settle_in' AND NOT EXISTS recent emp_record
  → Use data cutoff date (check MAX(auth_time) first, don't assume CURDATE())

Step 2: Distribution by building
  → GROUP BY building_no → identify which buildings have most ghosts

Step 3: Last-seen analysis
  → For ghost employees, check MAX(auth_time)
  → Categorize: never_seen / last month / older
  → Helps distinguish "left for holiday" vs "truly missing"

Pitfall: 数据可能有空窗期，用 MAX(auth_time) 作为截止点而非 CURDATE()
```

## Building Comparison

**Trigger**: Compare management status between two or more buildings.

```
Step 1: Basic metrics
  → rooms (exclude washroom type), settled people, devices
  → Note: t_device.building_id 大部分为空, device count may be 0

Step 2: Activity level
  → Join settle → employee → emp_record to count entry/exit records
  → Scope to a time window for fairness

Step 3: Cross-analysis
  → Occupancy rate, people-per-room, activity-per-person
  → Compare to identify underperforming buildings

Pitfall: SUM(capacity) in JOIN with settle will be inflated; use COUNT(DISTINCT) instead
```
