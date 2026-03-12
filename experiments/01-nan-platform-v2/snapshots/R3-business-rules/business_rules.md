# Business Rules

> Confirmed business logic from real interactions with nan_platform.

## Dictionary System (sys_dict + sys_dict_value)

<!-- decay: type=business_rule confirmed=2026-03-12 C0=1.0 -->
- **settle_status**: settle_in / no_settle_in / cancel_settle_in
- **emp_type**: emp_builder / emp_worker
- **emp_status**: not_live_in / live_in / leave_off
- **gender**: Male / Female
- **building_type**: worker_room / sample_building / simple_building / couple_room / great_room
- **room_type**: together / single_room / double_room / couple / washroom / three_room / four_room / six_room / eight_room
- **device_state**: store / normal / disable / error / not_found
- **rent_status**: not_rent / is_rent / rent_break / rent_losting
- **auth_type**: Face_In / Face_Out
- **emergency_rel**: couple_rel / parent_rel / bro_sis_rel / child_rel
- **company_type**: nation_com / party_com / public_com
- **brand**: tplink / wanwei_robot / smoke_gangqi / hikvision
- **park_yard**: nanzhongzhou_buiding

## Key Field Conventions

<!-- decay: type=business_rule confirmed=2026-03-12 C0=1.0 -->
- **Dict JOIN**: `sys_dict_value.code = sys_dict.code` (not via id)
- **Dict columns**: `sys_dict_value.value` (code) + `sys_dict_value.label` (display name)
