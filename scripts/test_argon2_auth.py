#!/usr/bin/env python3
"""
Test script to validate Argon2 authentication implementation
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
WEB_API_URL = os.getenv('WEB_API_URL', 'https://encryptu.onrender.com')
TEST_USER = {
    'name': 'Test User',
    'email': 'test@example.com',
    'password': 'test_password_123'
}

def test_registration():
    """Test user registration with Argon2 hashing"""
    print("🔐 Testing user registration...")
    
    try:
        response = requests.post(
            f"{WEB_API_URL}/api/auth",
            json={
                'name': TEST_USER['name'],
                'email': TEST_USER['email'],
                'password': TEST_USER['password']
            },
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Registration successful! User ID: {data.get('id')}")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_login():
    """Test user login with Argon2 verification"""
    print("🔑 Testing user login...")
    
    try:
        response = requests.post(
            f"{WEB_API_URL}/api/login",
            json={
                'email': TEST_USER['email'],
                'password': TEST_USER['password']
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful! Role: {data.get('role')}, Redirect: {data.get('redirect')}")
            
            # Check if we got a session token
            cookies = response.cookies
            if 'auth' in cookies:
                print("✅ Session token received")
                return True
            else:
                print("⚠️ No session token found in cookies")
                return False
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def test_wrong_password():
    """Test login with wrong password to ensure security"""
    print("🛡️ Testing wrong password rejection...")
    
    try:
        response = requests.post(
            f"{WEB_API_URL}/api/login",
            json={
                'email': TEST_USER['email'],
                'password': 'wrong_password'
            },
            timeout=10
        )
        
        if response.status_code == 401:
            print("✅ Wrong password correctly rejected")
            return True
        else:
            print(f"❌ Wrong password accepted: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Wrong password test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Argon2 Authentication Tests\n")
    
    # Test results
    results = {
        'registration': False,
        'login': False,
        'wrong_password': False
    }
    
    # Run tests
    results['registration'] = test_registration()
    print()
    
    if results['registration']:
        results['login'] = test_login()
        print()
        
        results['wrong_password'] = test_wrong_password()
        print()
    
    # Summary
    print("📊 Test Results Summary:")
    print(f"Registration: {'✅ PASS' if results['registration'] else '❌ FAIL'}")
    print(f"Login: {'✅ PASS' if results['login'] else '❌ FAIL'}")
    print(f"Wrong Password Rejection: {'✅ PASS' if results['wrong_password'] else '❌ FAIL'}")
    
    all_passed = all(results.values())
    print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️ Some tests failed!'}")
    
    return all_passed

if __name__ == "__main__":
    main()