# Business Rules

## Key Field Conventions

- `status = '1'` 表示有效/活跃（主数据表：building/floor/room/employee/device/car 等）
- **⚠️ 例外：记录表（t_emp_record, t_car_record）的 status 全部为 '0'**，查这两张表不要加 `WHERE status='1'`，否则返回 0 条结果
- 主键统一使用 `varchar(50)`，值为短随机字符串或 UUID
- 无外键约束，全靠业务层 ID 关联
- 审计字段统一：create_by / create_time / update_by / update_time
- create_by 常见值：`sys_sync`（系统同步）、`NQ67P5vR`（管理员）
- t_emp_record 数据范围：2025-12-10 ~ 2026-02-28 (2026-03-08 确认，可能持续增长)

## t_emp_record Fields

- `result` = 人脸识别置信度分数（0-99 整数，均值约 90）
- `auth_type` = Face_In / Face_Out（进出标志）
- `device_mac` + `device_name` = 识别设备（如"通道2入口"）

## t_employee Date Fields

- `id_start_time` / `id_end_time` = 身份证有效期（通常到 2045 年，几乎不会过期）
- `start_time` / `end_time` = **名单有效期**（业务上真正关注的过期日期）
- 查"过期员工"时用 `end_time < CURDATE()`，不要用 `id_end_time`

## Dictionary System (sys_dict_value)

### auth_type（出入标志）
- `Face_In` = 进入
- `Face_Out` = 离开

### building_type（楼型）
- `worker_room` = 工人宿舍
- `couple_room` = 夫妻房

### emp_type（员工类型）
- `emp_builder` = 建设者
- `emp_worker` = 职工

### emp_status（员工状态）
- `not_live_in` = 未入驻
- `live_in` = 已入驻
- `leave_off` = 暂离

### settle_status（入驻状态）
- `settle_in` = 已入驻
- `no_settle_in` = 未入驻
- `cancel_settle_in` = 已退驻

### room_type（房型）
- `together` = 集体宿舍
- `couple` = 夫妻宿舍
- `washroom` = 卫浴间

### rent_status（承租状态）
- `not_rent` = 已起租（免租期内）
- `is_rent` = 已起租（租约期内）
- `rent_break` = 已起租（逾期/违约）
- `rent_losting` = 已退租（租约结束）

### device_state（设备状态）
- `store` = 在库
- `normal` = 正常
- `disable` = 停用
- `error` = 故障
- `not_found` = 无法访问

### device_type（设备类型）
- `check_robot` = 巡检机器人
- `smoke_alarm` = 烟雾报警器
- `camera` = 监控

### gender
- `Male` = 男
- `Female` = 女

### company_type（企业类型）
- `nation_com` = 国企
- `party_com` = 央企
- `public_com` = 民营

### park_yard（园区）
- `nanzhongzhou_buiding` = 南中轴建设者之家园区
