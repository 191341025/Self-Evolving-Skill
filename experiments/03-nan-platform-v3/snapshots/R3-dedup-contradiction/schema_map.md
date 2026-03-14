# Schema Map

> 通过五道门治理协议管理。结构知识：表结构、实体关系、JOIN 路径。

<!-- decay: type=schema confirmed=2026-03-14 C0=1.0 alpha=3 beta=0 -->
<!-- entities: t_room, t_building -->
- t_room.building_id = t_building.id (many-to-one). t_room: id(PK varchar50), name, park_yard(dict), building_id(FK to t_building), room_no(int), floor(varchar50 FK), room_type(dict), capacity(int), rent_status(dict), is_settled(dict), status. t_building: id(PK varchar50), name, park_yard(dict), building_type(dict), building_no(int), status. Both use varchar50 UUID PKs. No index on building_id.

<!-- decay: type=schema confirmed=2026-03-14 C0=1.0 alpha=2 beta=0 -->
<!-- entities: t_employee, t_employee_settle -->
- t_employee_settle.emp_id = t_employee.id (many-to-one, employee accommodation). t_employee: id(PK), name, emp_type, id_card(indexed), gender(dict), birthday, native_place, address, phone, emp_status(dict), status. t_employee_settle: id(PK), emp_id(FK to t_employee), building_id(FK to t_building), floor_id(FK to t_floor), room_id(FK to t_room), bed_id, settle_status(dict), skills(multi-dict), skill_age, status. No table t_employee_station exists.

<!-- decay: type=schema confirmed=2026-03-14 C0=1.0 -->
<!-- entities: t_building, t_floor -->
- Hierarchy: t_building -> t_floor -> t_room. t_floor.building_id = t_building.id (many-to-one). t_room.floor = t_floor.id (many-to-one). t_floor: id(PK varchar50), name(e.g. 3F), park_yard(dict), building_id(FK to t_building), floor_no(int), capacity(int), status. No index on building_id.
