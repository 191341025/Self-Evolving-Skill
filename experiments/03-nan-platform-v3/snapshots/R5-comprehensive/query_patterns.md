# Query Patterns

> 通过五道门治理协议管理。查询模板：可复用 SQL、工具使用经验。

<!-- decay: type=query_pattern confirmed=2026-03-14 C0=1.0 -->
<!-- entities: v_employee_distribution, t_employee -->
- v_employee_distribution view provides pre-aggregated employee stats with columns: category(age/gender/province), label, count. Use this instead of manual GROUP BY on t_employee for dashboard queries. Also available: v_room_overview, v_building_overview, v_room_type_stats, v_worker_detail, v_room_workers.

<!-- decay: type=tool_experience confirmed=2026-03-14 C0=1.0 -->
<!-- entities: db_query -->
- In db_query.py SQL passed via shell: use <> instead of != for not-equal comparisons, as != gets escaped by bash.

<!-- decay: type=query_pattern confirmed=2026-03-14 C0=1.0 alpha=1 beta=0 -->
<!-- entities: t_building, t_room, t_employee_settle -->
- Occupancy rate query: use subqueries to avoid cross-join when aggregating from multiple child tables to same parent. Pattern: SELECT b.*, COALESCE(rc.x,0), COALESCE(sc.y,0) FROM t_building b LEFT JOIN (SELECT building_id, agg FROM child1 GROUP BY building_id) rc ON ... LEFT JOIN (SELECT building_id, agg FROM child2 GROUP BY building_id) sc ON ...
