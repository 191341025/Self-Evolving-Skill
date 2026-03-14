-- =====================================================
-- Table: t_employee_settle
-- Database: nan_platform
-- Generated: 2026-03-14 17:09:42
-- =====================================================

-- DDL
CREATE TABLE `t_employee_settle` (
  `id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `emp_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '员工id',
  `building_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '住所建筑',
  `floor_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '楼层',
  `room_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '房间',
  `bed_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '床铺',
  `settle_status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '入驻状态',
  `skills` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工种技能，多选字典',
  `skill_age` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工种对应工龄',
  `create_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='员工';

-- =====================================================
-- Columns
-- =====================================================
-- id: varchar(50) NOT NULL [PRI] 
-- emp_id: varchar(50) NULL  员工id
-- building_id: varchar(50) NULL  住所建筑
-- floor_id: varchar(50) NULL  楼层
-- room_id: varchar(50) NULL  房间
-- bed_id: varchar(50) NULL  床铺
-- settle_status: varchar(50) NULL  入驻状态
-- skills: varchar(255) NULL  工种技能，多选字典
-- skill_age: varchar(255) NULL  工种对应工龄
-- create_by: varchar(50) NULL  
-- create_time: datetime NULL  
-- update_by: varchar(50) NULL  
-- update_time: datetime NULL  
-- status: char(1) NULL  

-- =====================================================
-- Sample data (first 3 rows)
-- =====================================================
-- {'id': '0030186e-6cd6-411e-8bd1-a82bb8f55994', 'emp_id': 'b666f6ce-4ce3-48cb-a363-90c260365b79', 'building_id': '', 'floor_id': '', 'room_id': '', 'bed_id': None, 'settle_status': 'no_settle_in', 'skills': None, 'skill_age': None, 'create_by': 'sys_sync', 'create_time': datetime.datetime(2025, 12, 3, 5, 18, 31), 'update_by': 'sys_sync', 'update_time': datetime.datetime(2025, 12, 3, 5, 18, 31), 'status': '1'}
-- {'id': '0039579f-02d6-4f11-881f-2a53230ad54e', 'emp_id': '9c2ad34f-e5f7-4a46-90ae-5b6741ad97af', 'building_id': '', 'floor_id': '', 'room_id': '', 'bed_id': None, 'settle_status': 'no_settle_in', 'skills': None, 'skill_age': None, 'create_by': 'sys_sync', 'create_time': datetime.datetime(2025, 12, 3, 5, 18, 31), 'update_by': 'sys_sync', 'update_time': datetime.datetime(2025, 12, 3, 5, 18, 31), 'status': '1'}
-- {'id': '0039894d-95b7-47d9-a0ce-8af044ce5605', 'emp_id': '48474b88-e2a9-40b3-97f1-097736437364', 'building_id': '', 'floor_id': '', 'room_id': '', 'bed_id': None, 'settle_status': 'no_settle_in', 'skills': None, 'skill_age': None, 'create_by': 'sys_sync', 'create_time': datetime.datetime(2025, 12, 3, 5, 18, 31), 'update_by': 'sys_sync', 'update_time': datetime.datetime(2025, 12, 3, 5, 18, 31), 'status': '1'}

