import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database import get_db_connection
import mysql.connector

def init_auth_schema():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        print("🔒 Checking 'members' table for Auth columns...")

        # 1. Add password_hash
        try:
            cursor.execute("SELECT password_hash FROM members LIMIT 1")
        except mysql.connector.Error:
            print("   -> Adding 'password_hash' column...")
            cursor.execute("ALTER TABLE members ADD COLUMN password_hash VARCHAR(255) DEFAULT NULL")
            # Set default password for existing users (hash of "1234")
            # Generated using passlib.hash.bcrypt.hash("1234")
            default_hash = "$pbkdf2-sha256$29000$ilHKGeOcE0JIidF6j7FWqg$blDLEZDgtgX9SqkBbVVaoj1/S8.24Yw2h3JHWPm6iB8" 
            cursor.execute("UPDATE members SET password_hash = %s WHERE password_hash IS NULL", (default_hash,))
            print("   -> Set default password '1234' for existing users.")

        # 2. Add role
        try:
            cursor.execute("SELECT role FROM members LIMIT 1")
        except mysql.connector.Error:
            print("   -> Adding 'role' column...")
            cursor.execute("ALTER TABLE members ADD COLUMN role VARCHAR(50) DEFAULT 'USER'")
            
        # 3. Add created_at (if not exists)
        try:
            cursor.execute("SELECT created_at FROM members LIMIT 1")
        except mysql.connector.Error:
            print("   -> Adding 'created_at' column...")
            cursor.execute("ALTER TABLE members ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            
        # 4. Add email (Optional, for now we stick to username, but good to have)
        try:
            cursor.execute("SELECT email FROM members LIMIT 1")
        except mysql.connector.Error:
            print("   -> Adding 'email' column...")
            cursor.execute("ALTER TABLE members ADD COLUMN email VARCHAR(255) DEFAULT NULL")
            # cursor.execute("ALTER TABLE members ADD CONSTRAINT unique_email UNIQUE (email)") # Might fail if NULLs 

        conn.commit()
        print("✅ Auth Schema Migration Completed!")
        
    except Exception as e:
        print(f"❌ Migration Failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_auth_schema()
