import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def init_gacha_schema():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "fashion_app"),
    )
    cursor = conn.cursor()
    print("--- 🎰 GACHA SCHEMA UPDATE ---")

    # 1. Update 'items' table
    try:
        cursor.execute("SELECT gacha_weight FROM items LIMIT 1")
        print("✅ 'gacha_weight' column already exists in 'items'.")
    except mysql.connector.Error:
        print("➕ Adding 'gacha_weight' and 'rarity' to 'items'...")
        cursor.execute("ALTER TABLE items ADD COLUMN gacha_weight INT DEFAULT 0")
        cursor.execute("ALTER TABLE items ADD COLUMN rarity VARCHAR(20) DEFAULT 'COMMON'")
        
        # Set initial values for existing items
        # Legendary
        cursor.execute("UPDATE items SET rarity = 'LEGENDARY', gacha_weight = 10 WHERE name LIKE '%전설%' OR name LIKE '%투명%'")
        # Rare
        cursor.execute("UPDATE items SET rarity = 'RARE', gacha_weight = 30 WHERE name LIKE '%파이썬%' OR name LIKE '%무한%'")
        # Common (Default)
        cursor.execute("UPDATE items SET rarity = 'COMMON', gacha_weight = 60 WHERE gacha_weight = 0")
        print("✅ 'items' table updated.")

    # 2. Update 'members' table
    try:
        cursor.execute("SELECT gacha_fail_count FROM members LIMIT 1")
        print("✅ 'gacha_fail_count' column already exists in 'members'.")
    except mysql.connector.Error:
        print("➕ Adding 'gacha_fail_count' to 'members'...")
        cursor.execute("ALTER TABLE members ADD COLUMN gacha_fail_count INT DEFAULT 0")
        print("✅ 'members' table updated.")

    conn.commit()
    conn.close()
    print("🎉 Gacha Schema Update Complete!")

if __name__ == "__main__":
    init_gacha_schema()
