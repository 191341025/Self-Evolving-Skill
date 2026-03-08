# Baseline Snapshot: nan_platform Database

> Generated: 2026-03-08
> Purpose: Record the "zero point" of the Skill evolution experiment — all information the AI learned upon first contact with the database

## Database Overview

| Item | Value |
|------|-------|
| Database Name | nan_platform |
| Business Domain | Smart building / worker dormitory management platform (智能楼宇/工人宿舍管理平台) |
| Table Count | 29 |
| View Count | 12 |
| Stored Procedures | 0 |
| Estimated Total Rows | 95,517 |
| Data Size | 589.53 MB |

## Core Entity Relationships (Initial Inference)

```
t_building (building, 23 rows)
  ├─ t_floor (floor, 55 rows) → floor.building_id = building.id
  │   └─ t_room (room, 575 rows) → room.building_id = building.id, room.floor = floor.id
  │       └─ t_employee_settle (settlement records, 1819 rows) → settle.room_id = room.id
  │           └─ t_employee (employee, 2131 rows) → settle.emp_id = employee.id
  │
  ├─ t_device (device, 233 rows) → device.building_id = building.id
  │
  └─ t_building_rent (lease records, 14 rows) → rent.building_id = building.id (inferred)

t_emp_record (face entry/exit records, 81781 rows) → record.id_card = employee.id_card
t_car_record (vehicle entry/exit records, 2033 rows) → record linked to t_car (162 rows)
t_company (company, 8 rows)
```

## Dictionary System

| Dictionary Code | Meaning | Values |
|----------------|---------|--------|
| auth_type | Entry/exit flag | Face_In=entry, Face_Out=exit |
| building_type | Building type | worker_room=worker dormitory, couple_room=couple room |
| emp_type | Employee type | emp_builder=builder, emp_worker=staff |
| emp_status | Employee status | not_live_in=not settled in, live_in=settled in, leave_off=temporarily away |
| settle_status | Settlement status | settle_in=settled in, no_settle_in=not settled in, cancel_settle_in=checked out |
| room_type | Room type | together=shared dormitory, couple=couple dormitory, washroom=bathroom |
| rent_status | Lease status | not_rent=rent-free period, is_rent=active lease, rent_break=overdue breach, rent_losting=lease ended |
| device_state | Device status | store=in storage, normal=normal, disable=disabled, error=fault, not_found=unreachable |
| device_type | Device type | check_robot=inspection robot, smoke_alarm=smoke alarm, camera=surveillance camera |
| gender | Gender | Male=male, Female=female |
| company_type | Company type | nation_com=state-owned, party_com=central state-owned, public_com=private |
| park_yard | Campus/park | nanzhongzhou_buiding=Nanzhongzhou Builder's Home Campus (南中轴建设者之家园区) |

## Key Data Distribution

### Employees
- emp_builder (builder): 2009
- emp_worker (staff): 1
- NULL (uncategorized): 61

### Settlement Status
- no_settle_in (not settled in): 1362
- settle_in (settled in): 640
- Empty value: 69

### Entry/Exit Records
- Face_In (entry): 46,112 records
- Face_Out (exit): 40,563 records
- Total: 86,675 records

## Design Characteristics

1. **All primary keys use varchar(50)**, with values being short random strings or UUIDs
2. **Soft delete uniformly uses the status field**: '1' = active (opposite of the common convention where '0' = active)
3. **Dictionary system**: sys_dict + sys_dict_value, linked by code; many field values are dictionary values
4. **Association method**: No foreign key constraints; all relationships rely on application-layer ID associations
5. **Uniform audit fields**: All tables have create_by / create_time / update_by / update_time
6. **Data source**: create_by is mostly 'sys_sync' (system sync) or 'NQ67P5vR' (administrator)

## references/ Initial State

All files contain template placeholder content with no real domain knowledge. This is the "zero point" of evolution.
