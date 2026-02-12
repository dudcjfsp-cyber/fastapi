from database import get_db_connection
import time
import random

# 간단한 인메모리 캐시
ITEMS_CACHE = None
LAST_CACHE_TIME = 0
CACHE_DURATION = 60 # 60초

def get_items():
    """상점의 모든 아이템 목록을 반환합니다. (캐싱 적용)"""
    global ITEMS_CACHE, LAST_CACHE_TIME
    
    current_time = time.time()
    
    # 캐시가 있고, 유효 기간 내라면 캐시 반환
    if ITEMS_CACHE and (current_time - LAST_CACHE_TIME < CACHE_DURATION):
        return ITEMS_CACHE

    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM items ORDER BY price ASC")
        items = cursor.fetchall()
        cursor.close()
        
        # 캐시 업데이트
        ITEMS_CACHE = items
        LAST_CACHE_TIME = current_time
        
    finally:
        conn.close()
    return items

def get_user_gold(student_name: str):
    """사용자의 현재 골드를 반환합니다. (이름으로 조회)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        # username으로 조회
        cursor.execute("SELECT gold, gacha_fail_count FROM members WHERE username = %s", (student_name,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result
        return {"gold": 0, "gacha_fail_count": 0}
    finally:
        conn.close()

def get_inventory(student_name: str):
    """사용자가 보유한 아이템 목록을 반환합니다."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        # JOIN을 사용하여 아이템 정보까지 함께 가져옴
        sql = """
            SELECT inv.id, inv.acquired_at, i.name, i.description, i.image_url, i.price
            FROM inventory inv
            JOIN items i ON inv.item_id = i.id
            WHERE inv.student_name = %s
            ORDER BY inv.acquired_at DESC
        """
        cursor.execute(sql, (student_name,))
        inventory = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()
    return inventory

def buy_item(student_name: str, item_id: int):
    """아이템 구매 (트랜잭션 처리)"""
    conn = get_db_connection()
    try:
        conn.start_transaction() # 트랜잭션 시작
        cursor = conn.cursor(dictionary=True, buffered=True)

        # 1. 사용자 골드 확인 (username으로)
        cursor.execute("SELECT gold, username FROM members WHERE username = %s FOR UPDATE", (student_name,))
        user = cursor.fetchone()
        if not user:
            return {"success": False, "message": "사용자를 찾을 수 없습니다. (DB에 등록된 이름을 입력하세요)"}
        
        # 2. 아이템 가격 확인
        cursor.execute("SELECT price, name FROM items WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        if not item:
             raise Exception("아이템이 존재하지 않습니다.")

        # 3. 구매 가능 여부 체크
        if user['gold'] < item['price']:
            return {"success": False, "message": "골드가 부족합니다!"}

        # 4. 골드 차감
        new_gold = user['gold'] - item['price']
        cursor.execute("UPDATE members SET gold = %s WHERE username = %s", (new_gold, user['username']))

        # 5. 인벤토리 추가
        cursor.execute("INSERT INTO inventory (student_name, item_id) VALUES (%s, %s)", (student_name, item_id))

        conn.commit() # 모두 성공하면 커밋
        cursor.close()
        return {"success": True, "message": f"'{item['name']}' 구매 성공! 남은 골드: {new_gold}G"}

    finally:
        conn.close()

def sell_item(student_name: str, inventory_id: int):
    """아이템 판매 (트랜잭션 처리) - 판매가는 구매가의 50%"""
    conn = get_db_connection()
    try:
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True, buffered=True)

        # 1. 인벤토리 및 아이템 정보 확인
        sql = """
            SELECT inv.id, i.price, i.name 
            FROM inventory inv
            JOIN items i ON inv.item_id = i.id
            WHERE inv.id = %s AND inv.student_name = %s FOR UPDATE
        """
        cursor.execute(sql, (inventory_id, student_name))
        item = cursor.fetchone()
        
        if not item:
            return {"success": False, "message": "판매할 아이템을 찾을 수 없습니다."}

        sell_price = int(item['price'] * 0.5)

        # 2. 아이템 삭제
        cursor.execute("DELETE FROM inventory WHERE id = %s", (inventory_id,))

        # 3. 골드 지급
        cursor.execute("UPDATE members SET gold = gold + %s WHERE username = %s", (sell_price, student_name))

        conn.commit()
        return {"success": True, "message": f"'{item['name']}' 판매 완료! +{sell_price}G"}

    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"판매 실패: {str(e)}"}
    finally:
        conn.close()

def sell_all_items(student_name: str):
    """인벤토리 전체 판매 (트랜잭션 처리)"""
    conn = get_db_connection()
    try:
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True, buffered=True)

        # 1. 판매 가능한 전체 아이템 조회
        sql = """
            SELECT inv.id, i.price, i.name 
            FROM inventory inv
            JOIN items i ON inv.item_id = i.id
            WHERE inv.student_name = %s FOR UPDATE
        """
        cursor.execute(sql, (student_name,))
        items = cursor.fetchall()
        
        if not items:
            return {"success": False, "message": "판매할 아이템이 없습니다."}

        total_sell_price = sum(int(item['price'] * 0.5) for item in items)
        count = len(items)

        # 2. 전체 삭제
        cursor.execute("DELETE FROM inventory WHERE student_name = %s", (student_name,))

        # 3. 골드 지급
        cursor.execute("UPDATE members SET gold = gold + %s WHERE username = %s", (total_sell_price, student_name))

        conn.commit()
        return {
            "success": True, 
            "message": f"총 {count}개 아이템 일괄 판매 완료! +{total_sell_price:,}G" 
        }

    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"일괄 판매 실패: {str(e)}"}
    finally:
        conn.close()

def play_gacha_fixed(student_name: str):
    """프리미엄 가챠 (1,000G) - 고정 확률"""
    conn = get_db_connection()
    try:
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # 1. 유저 골드 확인
        cursor.execute("SELECT gold, username FROM members WHERE name = %s FOR UPDATE", (student_name,))
        user = cursor.fetchone()
        if not user: return {"success": False, "message": "사용자를 찾을 수 없습니다."}
        
        COST = 1000
        if user['gold'] < COST: return {"success": False, "message": "골드가 부족합니다! (1,000G 필요)"}

        # 2. 골드 차감
        cursor.execute("UPDATE members SET gold = gold - %s WHERE username = %s", (COST, user['username']))

        # 3. 아이템 뽑기 (가중치 기반)
        cursor.execute("SELECT id, name, rarity, gacha_weight FROM items WHERE gacha_weight > 0")
        items = cursor.fetchall()
        
        weights = [item['gacha_weight'] for item in items]
        picked_item = random.choices(items, weights=weights, k=1)[0]
        
        # 4. 인벤토리 지급
        cursor.execute("INSERT INTO inventory (student_name, item_id) VALUES (%s, %s)", (student_name, picked_item['id']))
        
        conn.commit()
        return {
            "success": True, 
            "message": f"💎 프리미엄 가챠 결과: [{picked_item['rarity']}] {picked_item['name']} 획득!",
            "item_name": picked_item['name'],
            "rarity": picked_item['rarity']
        }
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"가챠 실패: {str(e)}"}
    finally:
        conn.close()

def play_gacha_dynamic(student_name: str, count: int = 1):
    """럭키 박스 (100G) - 천장 시스템 (변동 확률) - 다중 뽑기 지원"""
    conn = get_db_connection()
    try:
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True, buffered=True)

        # 1. 유저 정보 확인
        cursor.execute("SELECT gold, username, gacha_fail_count FROM members WHERE username = %s FOR UPDATE", (student_name,))
        user = cursor.fetchone()
        if not user: return {"success": False, "message": "사용자를 찾을 수 없습니다."}

        COST_PER_PULL = 100
        TOTAL_COST = COST_PER_PULL * count

        if user['gold'] < TOTAL_COST: 
            return {"success": False, "message": f"골드가 부족합니다! ({TOTAL_COST}G 필요)"}

        # 2. 다중 뽑기 시뮬레이션
        current_fail_count = user['gacha_fail_count']
        PITY_LIMIT = 50 
        
        cursor.execute("SELECT id, name, rarity FROM items")
        all_items = cursor.fetchall()
        legendaries = [i for i in all_items if i['rarity'] == 'LEGENDARY']
        others = [i for i in all_items if i['rarity'] != 'LEGENDARY']
        
        results = []
        
        for _ in range(count):
            is_pity = current_fail_count >= (PITY_LIMIT - 1)
            picked = None

            if is_pity:
                # 천장
                picked = random.choice(legendaries) if legendaries else random.choice(all_items)
            else:
                # 일반: 1% 확률
                if random.randint(1, 100) == 1:
                    picked = random.choice(legendaries) if legendaries else random.choice(all_items)
                else:
                    picked = random.choice(others) if others else random.choice(all_items)
            
            if picked['rarity'] == 'LEGENDARY':
                current_fail_count = 0
            else:
                current_fail_count += 1
            
            results.append(picked)

        # 3. 골드 및 Fail Count 업데이트
        cursor.execute("UPDATE members SET gold = gold - %s, gacha_fail_count = %s WHERE username = %s", 
                       (TOTAL_COST, current_fail_count, user['username']))

        # 4. 인벤토리 일괄 지급
        inventory_values = [(student_name, item['id']) for item in results]
        cursor.executemany("INSERT INTO inventory (student_name, item_id) VALUES (%s, %s)", inventory_values)

        conn.commit()

        legend_count = sum(1 for r in results if r['rarity'] == 'LEGENDARY')
        if count > 1:
            msg = f"총 {count}회 뽑기 완료! (전설: {legend_count}개) - 남은 Pity: {current_fail_count}/50"
        else:
            item = results[0]
            prefix = "🌟 [JACKPOT]" if item['rarity'] == 'LEGENDARY' else f"꽝... ({current_fail_count}/{PITY_LIMIT})"
            msg = f"{prefix} [{item['rarity']}] {item['name']} 획득!"

        return {
            "success": True, 
            "message": msg,
            "items": results,
            "fail_count": current_fail_count
        }

    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"가챠 실패: {str(e)}"}
    finally:
        conn.close()
