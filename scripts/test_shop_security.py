import requests
import sys

BASE_URL = "http://localhost:8000"

def test_shop_security():
    # 1. Login to get token
    print("1. Logging in as 'authtest'...")
    try:
        res = requests.post(f"{BASE_URL}/auth/token", data={"username": "authtest", "password": "password123"})
        if res.status_code != 200:
            print("   Login Failed. Attempting Register first...")
            reg_res = requests.post(f"{BASE_URL}/auth/register", json={"username": "authtest", "password": "password123", "name": "Test User"})
            print(f"   Register Response: {reg_res.status_code} {reg_res.text}")
            
            res = requests.post(f"{BASE_URL}/auth/token", data={"username": "authtest", "password": "password123"})
            if res.status_code != 200:
                print(f"   Login Retry Failed: {res.status_code} {res.text}")
                return
        
        token = res.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print("   Login Success!")
    except Exception as e:
        print(f"   Fatal Error: {e}")
        return

    # 2. Test Protected Endpoint (Inventory) WITHOUT Token
    print("\n2. Testing Inventory WITHOUT Token...")
    res = requests.get(f"{BASE_URL}/shop/inventory/me")
    if res.status_code == 401:
        print("   ✅ Success: 401 Unauthorized received (As expected)")
    else:
        print(f"   ❌ Failed: Expected 401, got {res.status_code}")

    # 3. Test Protected Endpoint (Inventory) WITH Token
    print("\n3. Testing Inventory WITH Token...")
    res = requests.get(f"{BASE_URL}/shop/inventory/me", headers=headers)
    if res.status_code == 200:
        print("   ✅ Success: Inventory retrieved")
    else:
        print(f"   ❌ Failed: {res.status_code} {res.text}")

    # 4. Test Buy Item (With Token)
    print("\n4. Testing Buy Item (Item ID 1)...")
    res = requests.post(f"{BASE_URL}/shop/buy", json={"item_id": 1}, headers=headers)
    print(f"   Response: {res.status_code} {res.json()}")

if __name__ == "__main__":
    test_shop_security()
