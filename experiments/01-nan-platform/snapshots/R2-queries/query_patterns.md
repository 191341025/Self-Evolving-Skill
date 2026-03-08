# Query Patterns

Pre-built SQL templates for common investigations.

## Building Occupancy

```sql
-- 各楼栋房间数与入住率
SELECT b.name building,
  COUNT(DISTINCT r.id) rooms,
  COUNT(DISTINCT CASE WHEN es.settle_status='settle_in' THEN es.room_id END) occupied_rooms,
  ROUND(COUNT(DISTINCT CASE WHEN es.settle_status='settle_in' THEN es.room_id END)
    / COUNT(DISTINCT r.id) * 100, 1) occupy_pct
FROM t_building b
JOIN t_room r ON r.building_id = b.id AND r.status = '1'
LEFT JOIN t_employee_settle es ON es.room_id = r.id AND es.status = '1'
  AND es.settle_status = 'settle_in'
WHERE b.status = '1'
GROUP BY b.id, b.name
ORDER BY b.building_no;
```

## Employee Demographics

```sql
-- 在住员工性别分布
SELECT e.gender, COUNT(*) cnt
FROM t_employee e
JOIN t_employee_settle es ON es.emp_id = e.id AND es.status = '1'
  AND es.settle_status = 'settle_in'
WHERE e.status = '1'
GROUP BY e.gender;

-- 在住员工年龄段分布
SELECT CASE
  WHEN TIMESTAMPDIFF(YEAR, e.birthday, CURDATE()) < 30 THEN '<30'
  WHEN TIMESTAMPDIFF(YEAR, e.birthday, CURDATE()) < 40 THEN '30-39'
  WHEN TIMESTAMPDIFF(YEAR, e.birthday, CURDATE()) < 50 THEN '40-49'
  WHEN TIMESTAMPDIFF(YEAR, e.birthday, CURDATE()) < 60 THEN '50-59'
  ELSE '60+' END age_group,
  COUNT(*) cnt
FROM t_employee e
JOIN t_employee_settle es ON es.emp_id = e.id AND es.status = '1'
  AND es.settle_status = 'settle_in'
WHERE e.status = '1' AND e.birthday IS NOT NULL
GROUP BY age_group ORDER BY age_group;
```

## Entry/Exit Records

```sql
-- 按天统计进出趋势
SELECT DATE(auth_time) day, auth_type, COUNT(*) cnt
FROM t_emp_record
WHERE auth_time >= '<START_DATE>'
GROUP BY DATE(auth_time), auth_type
ORDER BY day, auth_type;

-- 数据时间范围检查
SELECT MIN(auth_time) earliest, MAX(auth_time) latest FROM t_emp_record;
```

## Device Overview

```sql
-- 设备状态分布
SELECT state, COUNT(*) cnt FROM t_device
WHERE status = '1' GROUP BY state ORDER BY cnt DESC;
```

## Tool Usage Notes

- **避免在 SQL 中使用 `!=`**：db_query.py 传参时 `!=` 会被 shell 转义出错，必须用 `<>` 替代
- **先查数据时间范围**：t_emp_record 可能有数据空窗期，查趋势前先确认 MAX(auth_time)
