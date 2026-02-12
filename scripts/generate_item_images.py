
import os
import time
import base64
import mysql.connector
from google import genai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Gemini 클라이언트 설정
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# DB 연결 설정
dbconfig = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "fashion_app"),
}

IMAGE_OUTPUT_DIR = "c:/Users/User/Desktop/intelAI5/fastapi-hello/리액트실습/리액트실습/public/items"
# 윈도우 경로 이슈 방지
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

def generate_image_for_item(item_name, description):
    """
    Imagen 3 모델을 사용하여 아이템 이미지를 생성합니다.
    스타일: Cyberpunk, Neon, Tron-legacy style, Matrix code background, High quality, 3D render
    """
    prompt = f"Cyberpunk style {item_name}. {description}. Neon glowing lights, Tron legacy aesthetic, Matrix digital rain background. High quality 3D render, futuristic object isolated."
    
    print(f"🎨 Generating image for: {item_name}...")
    
    try:
        response = client.models.generate_images(
            model="imagen-3.0-generate-001",
            prompt=prompt,
            config=genai.types.GenerateImagesConfig(
                number_of_images=1,
            )
        )
        if response.generated_images:
            return response.generated_images[0].image.image_bytes
    except Exception as e:
        print(f"❌ Failed to generate image for {item_name}: {e}")
        return None
    return None

def main():
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor(dictionary=True)
    
    # 이미지 URL이 없거나 'http'로 시작하는(임시) 아이템 조회
    # (여기서는 모든 아이템의 이미지를 새로 생성한다고 가정)
    cursor.execute("SELECT id, name, description, image_url FROM items")
    items = cursor.fetchall()
    
    print(f"Found {len(items)} items to process.")
    
    for item in items:
        # 파일명 안전하게 변환 (공백 -> 언더바)
        safe_name = "".join([c if c.isalnum() else "_" for c in item['name']])
        filename = f"item_{item['id']}_{safe_name}.png"
        filepath = os.path.join(IMAGE_OUTPUT_DIR, filename)
        
        # 이미지가 이미 있으면 스킵할 수도 있지만, 유저 요청("통일하고 싶다")에 따라 덮어쓰기 or 스킵 선택
        # 여기서는 강제 재생성 (Tron 스타일 통일)
        
        image_bytes = generate_image_for_item(item['name'], item['description'])
        
        if image_bytes:
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            print(f"✅ Saved: {filename}")
            
            # DB 업데이트 (Public URL 경로로 저장)
            # React의 public 폴더에 저장했으므로, 접근 URL은 /items/filename
            public_url = f"/items/{filename}"
            cursor.execute("UPDATE items SET image_url = %s WHERE id = %s", (public_url, item['id']))
            conn.commit()
            
            # API Rate Limit 고려 (잠시 대기)
            time.sleep(2)
        else:
            print(f"⚠️ Skipping DB update for {item['name']}")

    conn.close()
    print("✨ All done! Shop items have been cyber-fied.")

if __name__ == "__main__":
    main()
