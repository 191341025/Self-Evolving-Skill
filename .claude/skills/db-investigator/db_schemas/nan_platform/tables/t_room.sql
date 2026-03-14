-- =====================================================
-- Table: t_room
-- Database: nan_platform
-- Generated: 2026-03-14 17:06:52
-- =====================================================

-- DDL
CREATE TABLE `t_room` (
  `id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '房间名',
  `park_yard` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '园区，字典',
  `building_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '所属建筑',
  `room_no` int DEFAULT NULL COMMENT '房间号号',
  `floor` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '楼层',
  `room_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '户型，字典',
  `capacity` int DEFAULT NULL COMMENT '容纳人数',
  `rent_status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '承租状态，字典',
  `is_settled` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '是否入驻，字典',
  `create_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `model_slot` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='房间';

-- =====================================================
-- Columns
-- =====================================================
-- id: varchar(50) NOT NULL [PRI] 
-- name: varchar(255) NULL  房间名
-- park_yard: varchar(50) NOT NULL  园区，字典
-- building_id: varchar(50) NULL  所属建筑
-- room_no: int NULL  房间号号
-- floor: varchar(50) NULL  楼层
-- room_type: varchar(50) NULL  户型，字典
-- capacity: int NULL  容纳人数
-- rent_status: varchar(50) NULL  承租状态，字典
-- is_settled: varchar(50) NULL  是否入驻，字典
-- create_by: varchar(50) NULL  
-- create_time: datetime NULL  
-- update_by: varchar(50) NULL  
-- update_time: datetime NULL  
-- status: char(1) NULL  
-- model_slot: varchar(50) NULL  

-- =====================================================
-- Sample data (first 3 rows)
-- =====================================================
-- {'id': '0A82AJJq', 'name': '102', 'park_yard': 'nanzhongzhou_buiding', 'building_id': 'OMeN3Z8t', 'room_no': 102, 'floor': 'LsB4zk1W', 'room_type': 'together', 'capacity': 6, 'rent_status': None, 'is_settled': None, 'create_by': 'NQ67P5vR', 'create_time': datetime.datetime(2026, 1, 22, 14, 22, 51), 'update_by': 'NQ67P5vR', 'update_time': datetime.datetime(2026, 1, 22, 14, 22, 51), 'status': '1', 'model_slot': '102'}
-- {'id': '0eI9fvoF', 'name': '207', 'park_yard': 'nanzhongzhou_buiding', 'building_id': 'pOkFgijQ', 'room_no': 207, 'floor': 'sXuLnf7F', 'room_type': 'together', 'capacity': 6, 'rent_status': None, 'is_settled': '1', 'create_by': 'NQ67P5vR', 'create_time': datetime.datetime(2025, 12, 23, 2, 35, 10), 'update_by': 'NQ67P5vR', 'update_time': datetime.datetime(2026, 1, 4, 10, 15, 58), 'status': '1', 'model_slot': '207'}
-- {'id': '0FaxONpX', 'name': '203', 'park_yard': 'nanzhongzhou_buiding', 'building_id': 'MTlQmW83', 'room_no': 203, 'floor': 'bUvPtT2E', 'room_type': 'together', 'capacity': 6, 'rent_status': None, 'is_settled': None, 'create_by': 'NQ67P5vR', 'create_time': datetime.datetime(2026, 1, 22, 10, 37, 41), 'update_by': 'NQ67P5vR', 'update_time': datetime.datetime(2026, 1, 22, 10, 37, 41), 'status': '1', 'model_slot': '203'}

