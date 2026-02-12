import requests

BASE_URL = "http://localhost:8000"

def test_auth():
    # 1. Register
    print("1. Registering new user...")
    username = "authtest"
    password = "password123"
    name = "Auth Tester"
    
    # Try login first to see if exists (cleanup) - actually just try register, if fails it might exist
    try:
        res = requests.post(f"{BASE_URL}/auth/register", json={"username": username, "password": password, "name": name})
        print(f"   Register Response: {res.status_code} {res.json()}")
    except Exception as e:
        print(f"   Register Failed (might exist): {e}")

    # 2. Login
    print("\n2. Logging in...")
    res = requests.post(f"{BASE_URL}/auth/token", data={"username": username, "password": password})
    if res.status_code == 200:
        token_data = res.json()
        print(f"   Login Success! Token: {token_data['access_token'][:20]}...")
        return token_data['access_token']
    else:
        print(f"   Login Failed: {res.status_code} {res.text}")
        return None

if __name__ == "__main__":
    token = test_auth()
