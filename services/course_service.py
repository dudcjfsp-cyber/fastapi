from database import get_db_connection
import mysql.connector

def get_all_courses():
    """개설된 전체 강좌 목록과 현재 수강 인원을 반환합니다."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        # courses 테이블과 enrollments 테이블을 조인하여 수강 인원(enrolled_count) 계산
        sql = """
            SELECT c.*, COUNT(e.id) as enrolled_count 
            FROM courses c 
            LEFT JOIN enrollments e ON c.id = e.course_id 
            GROUP BY c.id
        """
        cursor.execute(sql)
        courses = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()
    return courses

def register_student(student_name: str, course_id: int):
    """학생을 강좌에 등록합니다. (정원 체크, 중복 체크 포함)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. 강좌 존재 여부 및 정원 확인
        cursor.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
        course = cursor.fetchone()
        if not course:
            return {"success": False, "message": "강좌를 찾을 수 없습니다."}
        
        # 현재 수강 인원 확인
        cursor.execute("SELECT COUNT(*) as count FROM enrollments WHERE course_id = %s", (course_id,))
        current_count = cursor.fetchone()['count']
        
        if current_count >= course['capacity']:
             return {"success": False, "message": "수강 정원이 초과되었습니다."}

        # 1.5. 멤버 존재 여부 확인 (수강신청 실명 인증)
        cursor.execute("SELECT * FROM members WHERE username = %s", (student_name,))
        member = cursor.fetchone()
        if not member:
             return {"success": False, "message": "등록되지 않은 학생입니다. (멤버 리스트에 있는 이름만 가능)"}

        # 2. 이미 등록했는지 확인
        cursor.execute("SELECT * FROM enrollments WHERE student_name = %s AND course_id = %s", (student_name, course_id))
        if cursor.fetchone():
             return {"success": False, "message": "이미 수강 신청한 강좌입니다."}

        # 3. 등록 처리
        cursor.execute("INSERT INTO enrollments (student_name, course_id) VALUES (%s, %s)", (student_name, course_id))
        conn.commit()
        
        cursor.close()
        return {"success": True, "message": "수강 신청이 완료되었습니다!"}
        
    except mysql.connector.Error as err:
        return {"success": False, "message": f"DB 오류: {str(err)}"}
    finally:
        conn.close()

def get_enrollments(course_id: int):
    """특정 강좌의 수강생 목록을 반환합니다."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT e.id, e.student_name, e.created_at, e.course_id
            FROM enrollments e
            WHERE e.course_id = %s
            ORDER BY e.created_at DESC
        """
        cursor.execute(sql, (course_id,))
        enrollments = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()
    return enrollments

def delete_enrollment(enrollment_id: int):
    """수강신청을 취소(삭제)합니다."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM enrollments WHERE id = %s", (enrollment_id,))
        if cursor.rowcount == 0:
            return {"success": False, "message": "삭제할 내역이 없습니다."}
        conn.commit()
        cursor.close()
    except mysql.connector.Error as err:
        return {"success": False, "message": f"삭제 실패: {str(err)}"}
    finally:
        conn.close()
    return {"success": True, "message": "수강신청이 취소되었습니다."}
