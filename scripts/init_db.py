import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "fashion.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create members table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS members (
        username TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        gender TEXT,
        style TEXT,
        location TEXT
    )
    ''')

    # Create ootd_log table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ootd_log (
        day TEXT PRIMARY KEY,
        outfit TEXT NOT NULL
    )
    ''')

    # Initial Data (from original data.py)
    members_data = [
        ("ideabong", "이상봉", "남성", "시티보이 룩", "Seoul"),
        ("sunny", "박써니", "여성", "러블리 캐주얼", "Busan")
    ]

    ootd_data = [
        ("monday", "검정 슬랙스에 흰 셔츠"),
        ("tuesday", "청바지에 후드티"),
        ("wednesday", "트레이닝복 세트"),
        ("thursday", "베이지색 트렌치코트"),
        ("friday", "화려한 파티룩")
    ]

    # Insert data (ignore if exists to avoid errors on re-run)
    cursor.executemany('INSERT OR IGNORE INTO members VALUES (?, ?, ?, ?, ?)', members_data)
    cursor.executemany('INSERT OR IGNORE INTO ootd_log VALUES (?, ?)', ootd_data)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
