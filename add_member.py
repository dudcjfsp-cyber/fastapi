import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def add_member():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()

        print("Adding 'newbie' member...")
        sql = "INSERT INTO members (username, name, gender, style, location) VALUES (%s, %s, %s, %s, %s)"
        val = ('newbie', '신입', '무관', '캐주얼', 'Home')
        
        try:
            cursor.execute(sql, val)
            conn.commit()
            print("Successfully added 'newbie'!")
        except mysql.connector.Error as err:
            if err.errno == 1062:
                print("Member 'newbie' already exists.")
            else:
                print(f"Error inserting: {err}")

        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Connection Error: {err}")

if __name__ == "__main__":
    add_member()
