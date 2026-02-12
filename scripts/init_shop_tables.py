import mysql.connector
import os
from dotenv import load_dotenv

# .env 로드
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))

def init_shop_tables():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "fashion_app"),
        )
        cursor = conn.cursor()

        print("--- 🛒 SHOP SYSTEM INITIALIZATION ---")

        # 1. Add 'gold' column to 'members' table if not exists
        try:
            cursor.execute("SELECT gold FROM members LIMIT 1")
            print("✅ 'gold' column already exists in 'members'.")
        except mysql.connector.Error:
            print("➕ Adding 'gold' column to 'members'...")
            cursor.execute("ALTER TABLE members ADD COLUMN gold INT DEFAULT 10000")
            print("✅ 'gold' column added.")

        # 2. Create 'items' table
        print("🔨 Creating table 'items'...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price INT NOT NULL,
            description TEXT,
            image_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        ''')

        # 3. Create 'inventory' table
        print("🎒 Creating table 'inventory'...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_name VARCHAR(50) NOT NULL,
            item_id INT NOT NULL,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES items(id)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        ''')

        # 4. Insert Initial Items (Sample Data)
        print("🎁 Inserting sample items...")
        sample_items = [
            ("전설의 코딩 모자", 5000, "착용하면 버그가 보입니다. (INT +5)", "https://cdn-icons-png.flaticon.com/512/1063/1063376.png"),
            ("무한의 커피", 2000, "마셔도 마셔도 줄지 않는 커피. (체력 +100)", "https://cdn-icons-png.flaticon.com/512/751/751621.png"),
            ("투명 키보드", 15000, "소리가 나지 않는 기계식 키보드. (은신 +3)", "https://cdn-icons-png.flaticon.com/512/9891/9891564.png"),
            ("파이썬 펫", 8000, "당신의 코딩을 지켜보는 귀여운 뱀. (매력 +10)", "https://cdn-icons-png.flaticon.com/512/2103/2103665.png")
        ]
        
        # Check if items exist to avoid duplicates
        cursor.execute("SELECT COUNT(*) FROM items")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.executemany(
                "INSERT INTO items (name, price, description, image_url) VALUES (%s, %s, %s, %s)",
                sample_items
            )
            print(f"✅ Inserted {len(sample_items)} sample items.")
        else:
            print("✅ Items already exist. Skipping insertion.")

        conn.commit()
        print("\n🎉 Shop System Ready! (Gold, Items, Inventory setup complete)")
        
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")

if __name__ == "__main__":
    init_shop_tables()
