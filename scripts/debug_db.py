import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

print(f"Connecting to MySQL...")
print(f"Host: {os.getenv('DB_HOST')}")
print(f"User: {os.getenv('DB_USER')}")
print(f"DB: {os.getenv('DB_NAME')}")

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "fashion_app")
    )
    print("Connection successful!")
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    print(f"Members: {members}")
    
    conn.close()

except mysql.connector.Error as err:
    print(f"Error: {err}")
except Exception as e:
    print(f"General Error: {e}")
