#!/usr/bin/env python3

import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test user data
test_user_data = {
    "email": "debug_test@example.com",
    "password": "TestPassword123!",
    "full_name": "Debug Test User",
    "role": "client"
}

print("1. Registering user...")
register_response = client.post("/api/v1/auth/register", json=test_user_data)
print(f"Register status: {register_response.status_code}")
print(f"Register response: {register_response.json()}")

print("\n2. Logging in...")
login_data = {
    "email": test_user_data["email"],
    "password": test_user_data["password"]
}
login_response = client.post("/api/v1/auth/login", json=login_data)
print(f"Login status: {login_response.status_code}")
login_data_response = login_response.json()
print(f"Login response: {json.dumps(login_data_response, indent=2)}")

refresh_token = login_data_response.get("refresh_token")
print(f"\n3. Got refresh token: {refresh_token[:50]}..." if refresh_token else "No refresh token!")

print("\n4. Attempting refresh...")
refresh_data = {
    "refresh_token": refresh_token
}
refresh_response = client.post("/api/v1/auth/refresh", json=refresh_data)
print(f"Refresh status: {refresh_response.status_code}")
print(f"Refresh response: {refresh_response.json()}")

# Let's also inspect the refresh token payload
import jwt
from app.config.config import settings

print(f"\n5. Decoding refresh token...")
try:
    payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
    print(f"Decoded payload: {json.dumps(payload, indent=2)}")
except Exception as e:
    print(f"Error decoding token: {e}")
