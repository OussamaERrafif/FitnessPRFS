#!/usr/bin/env python3
"""
Test script for FitnessPR API endpoints.

This script tests the basic functionality of the API.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_health_check():
    """Test health check endpoint."""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Health check error: {e}")
    print()

def test_user_registration():
    """Test user registration."""
    print("Testing user registration...")
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "client"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 200:
            print("✓ User registration successful")
            data = response.json()
            print(f"User ID: {data['user_id']}")
            print(f"Username: {data['username']}")
            print(f"Role: {data['role']}")
            return data['access_token']
        else:
            print(f"✗ User registration failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ User registration error: {e}")
    print()
    return None

def test_user_login():
    """Test user login."""
    print("Testing user login...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✓ User login successful")
            data = response.json()
            print(f"Access token received: {data['access_token'][:50]}...")
            return data['access_token']
        else:
            print(f"✗ User login failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ User login error: {e}")
    print()
    return None

def test_get_profile(token):
    """Test get user profile."""
    print("Testing get user profile...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            print("✓ Get profile successful")
            data = response.json()
            print(f"User: {data['username']} ({data['email']})")
            print(f"Role: {data['role']}")
        else:
            print(f"✗ Get profile failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ Get profile error: {e}")
    print()

def test_list_users(token):
    """Test list users."""
    print("Testing list users...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/users/", headers=headers)
        if response.status_code == 200:
            print("✓ List users successful")
            data = response.json()
            print(f"Total users: {len(data)}")
            if data:
                print(f"First user: {data[0]['username']}")
        else:
            print(f"✗ List users failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ List users error: {e}")
    print()

def main():
    """Run all tests."""
    print("="*50)
    print("FitnessPR API Test Suite")
    print("="*50)
    print()
    
    # Test health check
    test_health_check()
    
    # Test registration
    token = test_user_registration()
    
    # If registration failed, try login
    if not token:
        token = test_user_login()
    
    # Test authenticated endpoints
    if token:
        test_get_profile(token)
        test_list_users(token)
    else:
        print("✗ No valid token available, skipping authenticated tests")
    
    print("="*50)
    print("Tests completed!")
    print("="*50)

if __name__ == "__main__":
    main()
