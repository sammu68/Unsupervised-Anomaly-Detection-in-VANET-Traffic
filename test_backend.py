"""
Quick Backend Diagnostic Script
Run this to verify the backend is working correctly
"""
import requests
import json

API_URL = "http://localhost:8000"

print("=" * 60)
print("VANET Backend Diagnostic Test")
print("=" * 60)

# Test 1: Check if backend is running
print("\n1. Testing backend connectivity...")
try:
    response = requests.get(f"{API_URL}/", timeout=5)
    print(f"   ✓ Backend is running (Status: {response.status_code})")
    print(f"   Response: {response.json()}")
except requests.exceptions.ConnectionError:
    print("   ✗ Backend is NOT running!")
    print("   → Start backend with: cd backend && python main.py")
    exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 2: Login
print("\n2. Testing authentication...")
try:
    login_response = requests.post(
        f"{API_URL}/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=5
    )
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data["access_token"]
        print(f"   ✓ Login successful")
        print(f"   User: {token_data['user']['username']} ({token_data['user']['role']})")
        print(f"   Token: {token[:30]}...")
    else:
        print(f"   ✗ Login failed (Status: {login_response.status_code})")
        print(f"   Response: {login_response.text}")
        exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 3: Get vehicle data
print("\n3. Testing /data endpoint...")
try:
    data_response = requests.get(
        f"{API_URL}/data",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5
    )
    if data_response.status_code == 200:
        data = data_response.json()
        print(f"   ✓ Data endpoint working")
        print(f"   Vehicles: {len(data.get('vehicles', []))}")
        print(f"   Scenario: {data.get('scenario')}")
        print(f"   Anomalies: {data.get('total_anomalies')}")
        
        if len(data.get('vehicles', [])) > 0:
            print(f"\n   Sample vehicle data:")
            vehicle = data['vehicles'][0]
            print(f"   - ID: {vehicle['id']}")
            print(f"   - Position: ({vehicle['x']}, {vehicle['y']})")
            print(f"   - Speed: {vehicle['speed']}")
            print(f"   - MSE: {vehicle['reconstruction_error']}")
            print(f"   - Anomaly: {vehicle['is_anomaly']}")
        else:
            print("   ⚠ WARNING: No vehicles in response!")
    else:
        print(f"   ✗ Data endpoint failed (Status: {data_response.status_code})")
        print(f"   Response: {data_response.text}")
        exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 4: Check CORS
print("\n4. Checking CORS configuration...")
try:
    # Check if CORS headers are present
    headers = data_response.headers
    if 'access-control-allow-origin' in headers:
        print(f"   ✓ CORS enabled: {headers['access-control-allow-origin']}")
    else:
        print("   ⚠ CORS headers not found (may cause frontend issues)")
except Exception as e:
    print(f"   ⚠ Could not check CORS: {e}")

print("\n" + "=" * 60)
print("✓ All tests passed! Backend is working correctly.")
print("=" * 60)
print("\nIf frontend still shows 0 vehicles:")
print("1. Open browser console (F12)")
print("2. Check for error messages")
print("3. Verify token is being sent in requests")
print("4. Check Network tab for /data requests")
print("=" * 60)
