CREATE DATABASE IF NOT EXISTS practice_db;
USE practice_db;

SELECT DATABASE();
DROP TABLE IF EXISTS notes;
CREATE TABLE notes (
  note_id INT AUTO_INCREMENT PRIMARY KEY,
  title   VARCHAR(50) NOT NULL,
  body    VARCHAR(200) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
SHOW TABLES;
DESC notes;

INSERT INTO notes (title, body)
VALUES
  ('1일차', 'MySQL 테이블을 만들었다.'),
  ('2일차', 'INSERT와 SELECT를 연습했다.'),
  ('3일차', 'UPDATE와 DELETE까지 해봤다.');
  
  SELECT * FROM notes;

