import mysql.connector
import os
from dotenv import load_dotenv

# .env 로드
load_dotenv()

def init_course_tables():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "fashion_app")
        )
        cursor = conn.cursor()

        print("Creating table 'courses'...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            instructor VARCHAR(100),
            capacity INT DEFAULT 30,
            description TEXT
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        ''')

        print("Creating table 'enrollments'...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_name VARCHAR(50) NOT NULL,
            course_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id),
            UNIQUE KEY unique_enrollment (student_name, course_id)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        ''')

        # 샘플 데이터 추가
        print("Inserting sample courses...")
        courses = [
            ("AI Fashion Design 101", "Prof. Ideabong", 30, "기초 AI 패션 디자인"),
            ("Advanced Styling with MCP", "Dr. Newbie", 20, "MCP를 활용한 고급 스타일링"),
            ("React for Fashion Commerce", "Instructor Sunny", 50, "패션 커머스를 위한 리액트 실전")
        ]
        sql = "INSERT INTO courses (name, instructor, capacity, description) VALUES (%s, %s, %s, %s)"
        
        # 중복 삽입 방지 (간단하게 name으로 체크하거나 IGNORE 사용)
        # 여기서는 간단히 하기 위해, 테이블이 비어있을 때만 넣는 로직 대신
        # INSERT IGNORE는 아니지만, 테스트용으로 그냥 시도합니다.
        # 실제로는 중복 체크가 필요할 수 있음.
        
        # 테이블 비우고 다시 넣기 (실습용)
        # cursor.execute("TRUNCATE TABLE courses") # 외래키 때문에 실패할 수 있음
        # cursor.execute("DELETE FROM courses") # 수강신청 정보 있으면 실패함
        
        # 그냥 INSERT 시도 (에러나면 무시)
        try:
             cursor.executemany(sql, courses)
             print(f"Inserted {cursor.rowcount} courses.")
        except Exception as e:
            print(f"Skipping insert (maybe duplicate): {e}")

        conn.commit()
        print("Course tables created successfully!")
        
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    init_course_tables()
