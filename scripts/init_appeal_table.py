import mysql.connector
import os
from dotenv import load_dotenv

# .env 로드
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))

def init_appeal_table():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "fashion_app"),
        )
        cursor = conn.cursor()

        print("Creating table 'appeals'...")
        # secret_mode BOOLEAN DEFAULT TRUE (비밀글 기본)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS appeals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            course_id INT NOT NULL,
            student_name VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            is_secret BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        ''')

        conn.commit()
        print("Table 'appeals' created successfully!")
        
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    init_appeal_table()
