#!/usr/bin/env python3
"""
Simple test script to make HTTP requests and check if logging is working.
"""

import requests
import time

def test_requests():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing API requests...")
    
    try:
        # Test health endpoint
        print("1. Testing /health")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        time.sleep(0.5)
        
        # Test root endpoint
        print("\n2. Testing /")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        time.sleep(0.5)
        
        # Test API docs
        print("\n3. Testing /docs")
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        time.sleep(0.5)
        
        # Test non-existent endpoint
        print("\n4. Testing /nonexistent")
        response = requests.get(f"{base_url}/nonexistent", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        print("\n✓ All requests completed")
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Is it running on port 8000?")
    except Exception as e:
        print(f"✗ Error making requests: {e}")

if __name__ == "__main__":
    test_requests()
