-- =====================================================
-- Table: t_floor
-- Database: nan_platform
-- Generated: 2026-03-14 17:19:46
-- =====================================================

-- DDL
CREATE TABLE `t_floor` (
  `id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '房间名',
  `park_yard` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '园区，字典',
  `building_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '所属建筑',
  `floor_no` int DEFAULT NULL COMMENT '楼层',
  `capacity` int DEFAULT NULL COMMENT '容纳人数',
  `create_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='楼层';

-- =====================================================
-- Columns
-- =====================================================
-- id: varchar(50) NOT NULL [PRI] 
-- name: varchar(255) NULL  房间名
-- park_yard: varchar(50) NULL  园区，字典
-- building_id: varchar(50) NULL  所属建筑
-- floor_no: int NULL  楼层
-- capacity: int NULL  容纳人数
-- create_by: varchar(50) NULL  
-- create_time: datetime NULL  
-- update_by: varchar(50) NULL  
-- update_time: datetime NULL  
-- status: char(1) NULL  

-- =====================================================
-- Sample data (first 2 rows)
-- =====================================================
-- {'id': '1A3tIruP', 'name': '3F', 'park_yard': 'nanzhongzhou_buiding', 'building_id': 'SyuW0sbi', 'floor_no': 3, 'capacity': None, 'create_by': 'NQ67P5vR', 'create_time': datetime.datetime(2026, 1, 21, 21, 1, 58), 'update_by': 'NQ67P5vR', 'update_time': datetime.datetime(2026, 1, 21, 21, 1, 58), 'status': '1'}
-- {'id': '1If6rtZ0', 'name': '1F', 'park_yard': 'nanzhongzhou_buiding', 'building_id': 'MTlQmW83', 'floor_no': 1, 'capacity': None, 'create_by': 'NQ67P5vR', 'create_time': datetime.datetime(2026, 1, 21, 20, 57, 56), 'update_by': 'NQ67P5vR', 'update_time': datetime.datetime(2026, 1, 21, 20, 57, 56), 'status': '1'}

