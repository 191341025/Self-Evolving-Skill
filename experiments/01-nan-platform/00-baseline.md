# 基线快照：nan_platform 数据库

> 生成时间：2026-03-08
> 目的：记录 Skill 进化实验的"零点"——AI 首次接触数据库时了解到的全部信息

## 数据库概况

| 项目 | 值 |
|------|-----|
| 数据库名 | nan_platform |
| 业务领域 | 智能楼宇/工人宿舍管理平台 |
| 表数量 | 29 |
| 视图数量 | 12 |
| 存储过程 | 0 |
| 估算总行数 | 95,517 |
| 数据量 | 589.53 MB |

## 核心实体关系（首次推断）

```
t_building（楼栋，23条）
  ├─ t_floor（楼层，55条）→ floor.building_id = building.id
  │   └─ t_room（房间，575条）→ room.building_id = building.id, room.floor = floor.id
  │       └─ t_employee_settle（入驻记录，1819条）→ settle.room_id = room.id
  │           └─ t_employee（员工，2131条）→ settle.emp_id = employee.id
  │
  ├─ t_device（设备，233条）→ device.building_id = building.id
  │
  └─ t_building_rent（承租记录，14条）→ rent.building_id = building.id (推测)

t_emp_record（人脸进出记录，81781条）→ record.id_card = employee.id_card
t_car_record（车辆进出记录，2033条）→ record 关联 t_car（162条）
t_company（企业，8条）
```

## 字典体系

| 字典代码 | 含义 | 值 |
|----------|------|-----|
| auth_type | 出入标志 | Face_In=进入, Face_Out=离开 |
| building_type | 楼型 | worker_room=工人宿舍, couple_room=夫妻房 |
| emp_type | 员工类型 | emp_builder=建设者, emp_worker=职工 |
| emp_status | 员工状态 | not_live_in=未入驻, live_in=已入驻, leave_off=暂离 |
| settle_status | 入驻状态 | settle_in=已入驻, no_settle_in=未入驻, cancel_settle_in=已退驻 |
| room_type | 房型 | together=集体宿舍, couple=夫妻宿舍, washroom=卫浴间 |
| rent_status | 承租状态 | not_rent=免租期, is_rent=租约期内, rent_break=逾期违约, rent_losting=租约结束 |
| device_state | 设备状态 | store=在库, normal=正常, disable=停用, error=故障, not_found=无法访问 |
| device_type | 设备类型 | check_robot=巡检机器人, smoke_alarm=烟雾报警器, camera=监控 |
| gender | 性别 | Male=男, Female=女 |
| company_type | 企业类型 | nation_com=国企, party_com=央企, public_com=民营 |
| park_yard | 园区 | nanzhongzhou_buiding=南中轴建设者之家园区 |

## 关键数据分布

### 员工
- emp_builder（建设者）: 2009人
- emp_worker（职工）: 1人
- NULL（未分类）: 61人

### 入驻状态
- no_settle_in（未入驻）: 1362
- settle_in（已入驻）: 640
- 空值: 69

### 进出记录
- Face_In（进入）: 46,112条
- Face_Out（离开）: 40,563条
- 总计: 86,675条

## 设计特征观察

1. **主键全部使用 varchar(50)**，值为短随机字符串或 UUID
2. **软删除统一使用 status 字段**：'1' = 有效（与常见的 '0'=有效 相反）
3. **字典系统**：sys_dict + sys_dict_value，通过 code 关联，大量字段值是字典 value
4. **关联方式**：无外键约束，全靠业务层 ID 关联
5. **审计字段统一**：所有表都有 create_by/create_time/update_by/update_time
6. **数据来源**：create_by 多为 'sys_sync'（系统同步）或 'NQ67P5vR'（管理员）

## references/ 初始状态

所有文件均为模板占位内容，无真实领域知识。这是进化的"零点"。
