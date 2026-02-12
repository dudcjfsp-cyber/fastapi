import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def inspect_members():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "fashion_app"),
    )
    cursor = conn.cursor(dictionary=True)
    
    print("--- MEMBERS TABLE ---")
    cursor.execute("SELECT username, name, gold FROM members")
    for member in cursor.fetchall():
        print(member)
        
    conn.close()

if __name__ == "__main__":
    inspect_members()
