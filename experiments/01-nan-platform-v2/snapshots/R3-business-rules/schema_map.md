# Schema Map

> nan_platform — Smart building / worker dormitory management system (智能楼宇/工人宿舍管理平台)

## Databases

<!-- decay: type=schema confirmed=2026-03-12 C0=1.0 -->
| Database | Role | Key Tables |
|----------|------|-----------|
| `nan_platform` | Main application DB | 29 tables, 12 views |

## Table Categories

<!-- decay: type=schema confirmed=2026-03-12 C0=1.0 -->
| Category | Tables |
|----------|--------|
| Building mgmt (楼栋) | t_building, t_floor, t_room, t_bed |
| Personnel (人员) | t_employee, t_employee_settle, t_emp_record |
| Vehicle (车辆) | t_car, t_car_record |
| Device (设备) | t_device, t_device_series, t_device_location |
| Business (经营) | t_company, t_building_rent, t_project, t_customer, t_case |
| System (系统) | sys_user, sys_role, sys_office, sys_menu, sys_dict, sys_dict_value, sys_log |
| Empty/unused | t_alarm, t_alarm_setting, t_emergency_person, t_emp_health, t_emp_logs, t_bed (0 rows) |

## Entity Relationships

<!-- decay: type=schema confirmed=2026-03-12 C0=1.0 -->
```
t_building (楼栋)
  ├─ t_floor.building_id → building.id (楼层)
  │   └─ t_room.building_id + room.floor → building/floor (房间)
  ├─ t_device.building_id → building.id (设备, ⚠️ 大部分设备 building_id 为空，位置靠 address 文本)
  └─ t_building_rent.building_id → building.id (承租记录)

t_employee (员工)
  ├─ t_employee_settle.emp_id → employee.id (入驻记录)
  │   └─ settle → room/floor/building (位置)
  └─ t_emp_record.id_card = employee.id_card (进出记录，⚠️ 用 id_card 关联非 id)
```

## Key Join Paths

<!-- decay: type=schema confirmed=2026-03-12 C0=1.0 -->
| From → To | JOIN condition |
|---------|----------|
| building → floor | `t_floor.building_id = t_building.id` |
| building → room | `t_room.building_id = t_building.id` |
| room → floor | `t_room.floor = t_floor.id` |
| employee → settle | `t_employee_settle.emp_id = t_employee.id` |
| employee → record | `t_emp_record.id_card = t_employee.id_card` |
| settle → room | `t_employee_settle.room_id = t_room.id` |
| device → building | `t_device.building_id = t_building.id` |
| company → building | `t_building_rent.company_id = t_company.id` |
| dict → dict_value | `sys_dict_value.code = sys_dict.code` (非 id 关联) |
