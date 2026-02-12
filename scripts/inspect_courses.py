import mysql.connector
import os
from dotenv import load_dotenv

# .env 로드
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "fashion_app"),
    )

def inspect_courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    print("\n--- 📚 COURSES (강좌 목록) ---")
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()
    for c in courses:
        print(f"[{c['id']}] {c['name']} (강사: {c['instructor']}) - 정원: {c['capacity']}")

    print("\n--- 📝 ENROLLMENTS (수강신청 내역) ---")
    cursor.execute("""
        SELECT e.id, e.student_name, c.name, e.created_at 
        FROM enrollments e 
        JOIN courses c ON e.course_id = c.id
    """)
    enrollments = cursor.fetchall()
    
    if not enrollments:
        print("(아직 신청 내역이 없습니다)")
    else:
        for e in enrollments:
            print(f"- {e['student_name']}님이 '{e['name']}' 강좌를 신청함 ({e['created_at']})")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    inspect_courses()
