import mysql.connector
import os
from dotenv import load_dotenv

# 환경 변수 로드 (.env)
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))


def get_db_connection():
    """MySQL 연결을 생성하여 반환합니다."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "fashion_app"),
    )


def get_all_members():
    """전체 팀원 목록을 딕셔너리 리스트로 반환합니다."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()

    # 리액트(MemberSidebar)에서 'id'(숫자)와 'role'을 요구하므로 주입
    result = []
    for idx, m in enumerate(members):
        item = dict(m)
        item["id"] = idx + 1
        item["role"] = "Style Agent"
        result.append(item)

    return result


def get_member(username: str):
    """특정 팀원의 상세 정보를 딕셔너리로 반환합니다."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM members WHERE username = %s", (username,))
        member = cursor.fetchone()
        cursor.close()
    finally:
        conn.close()
    return member


def get_ootd(day: str):
    """특정 요일의 OOTD(코디) 기록을 반환합니다."""
    try:
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT outfit FROM ootd_log WHERE day = %s", (day,))
            ootd = cursor.fetchone()
            cursor.close()
        finally:
            conn.close()

        if ootd:
            return ootd["outfit"]
    except mysql.connector.Error as err:
        print(f"Error accessing ootd_log: {err}")

    return None
