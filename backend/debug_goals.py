import requests
import json
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Register and login as trainer
trainer_data = {
    "email": "trainer@example.com",
    "username": "trainer",
    "password": "password123",
    "role": "trainer"
}

response = client.post("/api/v1/auth/register", json=trainer_data)
print(f"Register response: {response.status_code}")

login_data = {
    "email": "trainer@example.com",
    "password": "password123"
}
response = client.post("/api/v1/auth/login", json=login_data)
print(f"Login response: {response.status_code}")
token = response.json()["access_token"]

# Create a client
client_data = {
    "email": "client@example.com", 
    "username": "client",
    "password": "password123",
    "role": "client"
}
response = client.post("/api/v1/auth/register", json=client_data)
print(f"Client register response: {response.status_code}")

headers = {"Authorization": f"Bearer {token}"}

# Test empty goals
program_data = {
    "name": "Test Program",
    "description": "Test",
    "program_type": "strength_training",
    "difficulty_level": "beginner", 
    "duration_weeks": 4,
    "sessions_per_week": 3,
    "client_id": 2,
    "goals": []
}

response = client.post("/api/v1/programs/", headers=headers, json=program_data)
print(f"Program creation response: {response.status_code}")
print(f"Response content: {response.text}")
