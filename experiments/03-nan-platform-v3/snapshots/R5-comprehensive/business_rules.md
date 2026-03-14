# Business Rules

> 通过五道门治理协议管理。业务规则：状态枚举、字段约定、业务逻辑。

<!-- decay: type=business_rule confirmed=2026-03-14 C0=1.0 alpha=0.3 beta=0.3 -->
<!-- entities: t_room -->
- t_room.room_type enum values: together (571 rooms, multi-person dorm), washroom (4 rooms). Only 2 types exist in current data.

<!-- decay: type=business_rule confirmed=2026-03-14 C0=1.0 -->
<!-- entities: t_room, t_building -->
- t_room.building_id has NO index. When joining t_room to t_building on large datasets, expect full table scan on t_room side. Consider adding index if query performance degrades.
