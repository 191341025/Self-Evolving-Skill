-- =====================================================
-- Table: t_employee
-- Database: nan_platform
-- Generated: 2026-03-14 17:09:16
-- =====================================================

-- DDL
CREATE TABLE `t_employee` (
  `id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '姓名',
  `emp_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '员工类型',
  `id_card` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '身份证号',
  `gender` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '性别，字典',
  `birthday` datetime DEFAULT NULL COMMENT '生日',
  `native_place` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '籍贯',
  `address` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '家庭住址',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '联系方式，电话',
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '头像照片',
  `emp_status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '员工状态，字典',
  `id_start_time` datetime DEFAULT NULL COMMENT '有效期起始',
  `id_end_time` datetime DEFAULT NULL COMMENT '有效期结束',
  `start_time` datetime DEFAULT NULL COMMENT '名单有效期起始',
  `end_time` datetime DEFAULT NULL COMMENT '名单有效期结束',
  `emergency_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '紧急联系人',
  `emergency_rel` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '紧急联系人关系',
  `emergency_tel` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '紧急联系人电话',
  `create_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_id_card` (`id_card`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='员工';

-- =====================================================
-- Columns
-- =====================================================
-- id: varchar(50) NOT NULL [PRI] 
-- name: varchar(255) NULL  姓名
-- emp_type: varchar(50) NULL  员工类型
-- id_card: varchar(20) NULL [MUL] 身份证号
-- gender: varchar(50) NULL  性别，字典
-- birthday: datetime NULL  生日
-- native_place: varchar(200) NULL  籍贯
-- address: varchar(500) NULL  家庭住址
-- phone: varchar(20) NULL  联系方式，电话
-- avatar: varchar(255) NULL  头像照片
-- emp_status: varchar(50) NULL  员工状态，字典
-- id_start_time: datetime NULL  有效期起始
-- id_end_time: datetime NULL  有效期结束
-- start_time: datetime NULL  名单有效期起始
-- end_time: datetime NULL  名单有效期结束
-- emergency_name: varchar(20) NULL  紧急联系人
-- emergency_rel: varchar(50) NULL  紧急联系人关系
-- emergency_tel: varchar(20) NULL  紧急联系人电话
-- create_by: varchar(50) NULL  
-- create_time: datetime NULL  
-- update_by: varchar(50) NULL  
-- update_time: datetime NULL  
-- status: char(1) NULL  

-- =====================================================
-- Sample data (first 3 rows)
-- =====================================================
-- {'id': '00274cab-58d4-455a-8b23-0621600fa4f7', 'name': '吕铁梅', 'emp_type': 'emp_builder', 'id_card': '410327197009188228', 'gender': 'Female', 'birthday': datetime.datetime(1970, 9, 18, 0, 0), 'native_place': '河南省', 'address': '河南省宜阳县张午乡程午村', 'phone': None, 'avatar': '["PeopleImg/410327197009188228/410327197009188228_1.jpg"]', 'emp_status': None, 'id_start_time': datetime.datetime(2021, 1, 7, 9, 17, 8), 'id_end_time': datetime.datetime(2046, 1, 7, 9, 17, 8), 'start_time': datetime.datetime(2006, 1, 19, 0, 0), 'end_time': datetime.datetime(2027, 1, 13, 0, 0), 'emergency_name': None, 'emergency_rel': None, 'emergency_tel': None, 'create_by': 'sys_sync', 'create_time': datetime.datetime(2026, 1, 7, 9, 17, 9), 'update_by': 'sys_sync', 'update_time': datetime.datetime(2026, 1, 7, 9, 17, 9), 'status': '1'}
-- {'id': '00510df8-0cd4-404b-a830-c9f0d8d67d22', 'name': '曲金福', 'emp_type': 'emp_builder', 'id_card': '23022319670903241X', 'gender': 'Male', 'birthday': datetime.datetime(1967, 9, 3, 0, 0), 'native_place': '黑龙江', 'address': '黑龙江省依安县新发乡新里村2组', 'phone': None, 'avatar': '["PeopleImg/23022319670903241X/23022319670903241X_1.jpg"]', 'emp_status': None, 'id_start_time': datetime.datetime(2020, 10, 30, 14, 26, 2), 'id_end_time': datetime.datetime(2045, 10, 30, 14, 26, 2), 'start_time': datetime.datetime(2025, 10, 30, 0, 0), 'end_time': datetime.datetime(2026, 3, 1, 14, 25, 40), 'emergency_name': None, 'emergency_rel': None, 'emergency_tel': None, 'create_by': 'sys_sync', 'create_time': datetime.datetime(2025, 10, 30, 14, 26, 2), 'update_by': 'sys_sync', 'update_time': datetime.datetime(2025, 10, 30, 14, 26, 2), 'status': '1'}
-- {'id': '00718b61-8f13-49e7-bcee-979b33ffeeb8', 'name': '申志顺', 'emp_type': 'emp_builder', 'id_card': '130423198604203418', 'gender': 'Male', 'birthday': datetime.datetime(1986, 4, 20, 0, 0), 'native_place': '河北省', 'address': '河北省邯郸市临漳县柳园镇申村南环路朝合巷9号', 'phone': None, 'avatar': '["PeopleImg/130423198604203418/130423198604203418_1.jpg"]', 'emp_status': None, 'id_start_time': datetime.datetime(2020, 12, 26, 17, 10, 37), 'id_end_time': datetime.datetime(2045, 12, 26, 17, 10, 37), 'start_time': datetime.datetime(2025, 12, 26, 0, 0), 'end_time': datetime.datetime(2026, 3, 1, 0, 0), 'emergency_name': None, 'emergency_rel': None, 'emergency_tel': None, 'create_by': 'sys_sync', 'create_time': datetime.datetime(2025, 12, 26, 17, 10, 37), 'update_by': 'sys_sync', 'update_time': datetime.datetime(2025, 12, 26, 17, 10, 37), 'status': '1'}

