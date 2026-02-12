from database import get_db_connection
import mysql.connector

def create_appeal(course_id: int, student_name: str, content: str, is_secret: bool = True):
    """이의신청을 등록합니다."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO appeals (course_id, student_name, content, is_secret)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (course_id, student_name, content, is_secret))
        conn.commit()
        cursor.close()
    except mysql.connector.Error as err:
        return {"success": False, "message": f"작성 실패: {str(err)}"}
    finally:
        conn.close()
    return {"success": True, "message": "이의신청이 등록되었습니다."}

def get_appeals(course_id: int):
    """특정 강좌의 이의신청 목록을 반환합니다."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT * FROM appeals WHERE course_id = %s ORDER BY created_at DESC
        """
        cursor.execute(sql, (course_id,))
        appeals = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()
    return appeals
