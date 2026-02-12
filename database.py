import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

# 환경 변수 로드 (.env)
# database.py가 루트에 있거나, 호출되는 위치에 따라 경로 조정 필요
# 여기서는 data.py와 동일한 위치(루트)에 있다고 가정
load_dotenv()

# [NEW] Connection Pool 설정
dbconfig = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "fashion_app"),
}

pool = None

try:
    # Pool 생성
    pool = pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=20, 
        pool_reset_session=True, 
        **dbconfig
    )
except Exception as e:
    print(f"Pool creation warning: {e}")
    try:
        pool = None 
    except:
        pass

def get_db_connection():
    """Connection Pool에서 연결을 가져옵니다."""
    global pool
    try:
        if pool:
            return pool.get_connection()
        else:
            return mysql.connector.connect(**dbconfig)
    except Exception as e:
        print(f"Error getting connection from pool: {e}")
        return mysql.connector.connect(**dbconfig)
