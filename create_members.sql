CREATE DATABASE IF NOT EXISTS pk_fk_practice;
USE pk_fk_practice;

-- 1. Create members table
CREATE TABLE IF NOT EXISTS members (
    username VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(20),
    style VARCHAR(100),
    location VARCHAR(100)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. Insert team members data
-- REPLACE INTO: 데이터가 있으면 덮어쓰고, 없으면 새로 추가합니다.
REPLACE INTO members (username, name, gender, style, location) VALUES 
('ideabong', '이상봉', '남성', '시티보이 룩', 'Seoul'),
('sunny', '박써니', '여성', '러블리 캐주얼', 'Busan'),
('newbie', '신입', '무관', '캐주얼', 'Home');

-- 3. Verify Data
SHOW TABLES;
SELECT * FROM members;