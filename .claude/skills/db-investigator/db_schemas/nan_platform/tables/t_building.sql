-- =====================================================
-- Table: t_building
-- Database: nan_platform
-- Generated: 2026-03-14 17:06:53
-- =====================================================

-- DDL
CREATE TABLE `t_building` (
  `id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '楼名',
  `park_yard` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '园区，字典',
  `building_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '楼型，字典',
  `building_no` int DEFAULT NULL COMMENT '楼号',
  `create_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='建筑';

-- =====================================================
-- Columns
-- =====================================================
-- id: varchar(50) NOT NULL [PRI] 
-- name: varchar(255) NULL  楼名
-- park_yard: varchar(50) NULL  园区，字典
-- building_type: varchar(50) NULL  楼型，字典
-- building_no: int NULL  楼号
-- create_by: varchar(50) NULL  
-- create_time: datetime NULL  
-- update_by: varchar(50) NULL  
-- update_time: datetime NULL  
-- status: char(1) NULL  

-- =====================================================
-- Sample data (first 3 rows)
-- =====================================================
-- {'id': '54uouUML', 'name': '8# 工人宿舍', 'park_yard': 'nanzhongzhou_buiding', 'building_type': 'worker_room', 'building_no': 8, 'create_by': 'NQ67P5vR', 'create_time': datetime.datetime(2025, 12, 12, 0, 24, 48), 'update_by': 'NQ67P5vR', 'update_time': datetime.datetime(2026, 1, 3, 21, 37, 51), 'status': '1'}
-- {'id': '7rsGDJIL', 'name': '6# 工人宿舍', 'park_yard': 'nanzhongzhou_buiding', 'building_type': 'worker_room', 'building_no': 6, 'create_by': 'NQ67P5vR', 'create_time': datetime.datetime(2025, 12, 12, 0, 24, 37), 'update_by': 'NQ67P5vR', 'update_time': datetime.datetime(2026, 1, 3, 21, 37, 42), 'status': '1'}
-- {'id': '8iCCJ7wD', 'name': '9# 工人宿舍', 'park_yard': 'nanzhongzhou_buiding', 'building_type': 'worker_room', 'building_no': 9, 'create_by': 'NQ67P5vR', 'create_time': datetime.datetime(2025, 12, 12, 0, 24, 54), 'update_by': 'NQ67P5vR', 'update_time': datetime.datetime(2026, 1, 3, 21, 38, 1), 'status': '1'}

