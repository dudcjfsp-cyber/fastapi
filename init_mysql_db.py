import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def init_mysql():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()

        # 1. Create members table
        print("Creating table 'members'...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            username VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            gender VARCHAR(20),
            style VARCHAR(100),
            location VARCHAR(100)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        ''')

        # 2. Insert team members data
        print("Inserting data...")
        sql = "INSERT IGNORE INTO members (username, name, gender, style, location) VALUES (%s, %s, %s, %s, %s)"
        val = [
            ('ideabong', '이상봉', '남성', '시티보이 룩', 'Seoul'),
            ('sunny', '박써니', '여성', '러블리 캐주얼', 'Busan')
        ]
        cursor.executemany(sql, val)

        conn.commit()
        print("Table created and data inserted successfully!")
        
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    init_mysql()
