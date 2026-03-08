# Schema Map

## Database

| Database | Role |
|----------|------|
| `nan_platform` | 智能楼宇/工人宿舍管理平台 |

## Entity Relationships

```
t_building（楼栋）
  ├─ t_floor.building_id → building.id（楼层）
  │   └─ t_room.building_id + room.floor → building/floor（房间）
  ├─ t_device.building_id → building.id（设备，可选关联 floor_id/room_id）
  └─ t_building_rent（承租记录）

t_employee（员工）
  ├─ t_employee_settle.emp_id → employee.id（入驻记录，1:1）
  │   └─ settle 关联 building_id / floor_id / room_id / bed_id
  └─ t_emp_record.id_card → employee.id_card（进出记录，通过身份证号关联）

t_car（车辆）
  └─ t_car_record（车辆进出记录）

t_company（企业/公司）

sys_dict + sys_dict_value（字典系统）
  └─ 通过 code 字段关联（不是通过 id）
  └─ 业务表中的字典字段存储 sys_dict_value.value
```

## Table Categories

| 分类 | 表 |
|------|-----|
| 系统基础 | sys_dict, sys_dict_value, sys_user, sys_role, sys_menu, sys_office, sys_log |
| 空间管理 | t_building, t_floor, t_room, t_bed |
| 人员管理 | t_employee, t_employee_settle, t_emp_record, t_emp_health, t_emp_logs |
| 设备管理 | t_device, t_device_series, t_device_location |
| 车辆管理 | t_car, t_car_record |
| 经营管理 | t_company, t_building_rent |
| 其他 | t_alarm, t_alarm_setting, t_case, t_customer, t_emergency_person, t_project |

## Key Join Paths

| 从 → 到 | JOIN 条件 |
|---------|----------|
| building → floor | `t_floor.building_id = t_building.id` |
| building → room | `t_room.building_id = t_building.id` |
| room → floor | `t_room.floor = t_floor.id` |
| employee → settle | `t_employee_settle.emp_id = t_employee.id` |
| employee → record | `t_emp_record.id_card = t_employee.id_card` |
| settle → room | `t_employee_settle.room_id = t_room.id` |
| device → building | `t_device.building_id = t_building.id` |
| dict → dict_value | `sys_dict_value.code = sys_dict.code`（非 id 关联） |
