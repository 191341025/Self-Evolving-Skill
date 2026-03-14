# Query Patterns

> 通过五道门治理协议管理。查询模板：可复用 SQL、工具使用经验。

<!-- decay: type=query_pattern confirmed=2026-03-14 C0=1.0 -->
<!-- entities: v_employee_distribution, t_employee -->
- v_employee_distribution view provides pre-aggregated employee stats with columns: category(age/gender/province), label, count. Use this instead of manual GROUP BY on t_employee for dashboard queries. Also available: v_room_overview, v_building_overview, v_room_type_stats, v_worker_detail, v_room_workers.
