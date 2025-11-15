#!/usr/bin/env python3
"""
Test script to validate admin user creation functionality
"""
import requests
import json
import os
from typing import Dict, Any

# Configuration
WEB_API_URL = os.getenv('WEB_API_URL', 'https://encryptu.onrender.com')
ADMIN_EMAIL = "admin@encryptu.com"  # Replace with your admin email
ADMIN_PASSWORD = "admin123456"      # Replace with your admin password

def test_admin_login() -> str:
    """Login as admin and get auth token"""
    print("🔐 Testing admin login...")
    
    try:
        response = requests.post(
            f"{WEB_API_URL}/api/login",
            json={
                'email': ADMIN_EMAIL,
                'password': ADMIN_PASSWORD
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f" Admin login successful!")
            
            # Get the auth token from cookies
            auth_token = response.cookies.get('auth')
            if not auth_token:
                print(" No auth token found in cookies")
                return None
                
            print(f" Auth token received: {auth_token[:20]}...")
            return auth_token
        else:
            print(f" Admin login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f" Admin login error: {e}")
        return None

def test_create_user(auth_token: str, user_data: Dict[str, Any]) -> bool:
    """Test creating a new user through admin panel"""
    print(f"👤 Testing user creation: {user_data['name']}...")
    
    try:
        # Set cookies for authenticated admin session
        cookies = {'auth': auth_token}
        
        response = requests.post(
            f"{WEB_API_URL}/api/admin/users",
            json=user_data,
            cookies=cookies,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('ok') and data.get('user'):
                print(f" User created successfully!")
                print(f"   ID: {data['user']['id']}")
                print(f"   Name: {data['user']['name']}")
                print(f"   Email: {data['user']['email']}")
                print(f"   Role: {data['user']['role']}")
                return True
            else:
                print(f" User creation failed - invalid response format")
                return False
        else:
            print(f" User creation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f" User creation error: {e}")
        return False

def test_login_new_user(user_data: Dict[str, Any]) -> bool:
    """Test login with the newly created user"""
    print(f"🔑 Testing login with new user: {user_data['email']}...")
    
    try:
        response = requests.post(
            f"{WEB_API_URL}/api/login",
            json={
                'email': user_data['email'],
                'password': user_data['password']
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✅ New user login successful!")
                print(f"   Role: {data.get('role')}")
                print(f"   Redirect: {data.get('redirect')}")
                return True
            else:
                print(f"❌ New user login failed - invalid response")
                return False
        else:
            print(f"❌ New user login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ New user login error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Admin User Creation Tests\n")
    
    # Test configuration
    test_users = [
        {
            'name': 'Usuario Soporte Test',
            'email': 'soporte.test@encryptu.com',
            'password': 'password123',
            'role': 'soporte'
        },
        {
            'name': 'Usuario Normal Test', 
            'email': 'usuario.test@encryptu.com',
            'password': 'password123',
            'role': 'usuario'
        }
    ]
    
    # Step 1: Admin login
    auth_token = test_admin_login()
    if not auth_token:
        print("❌ Cannot proceed without admin authentication")
        return False
    
    print()
    
    # Step 2: Test user creation for each role
    results = {'created': [], 'failed': []}
    
    for user_data in test_users:
        success = test_create_user(auth_token, user_data)
        if success:
            results['created'].append(user_data)
        else:
            results['failed'].append(user_data)
        print()
    
    # Step 3: Test login with newly created users
    for user_data in results['created']:
        success = test_login_new_user(user_data)
        if not success:
            print(f"⚠️ User {user_data['name']} created but login failed")
        print()
    
    # Summary
    print("📊 Test Results Summary:")
    print(f"Total users created: {len(results['created'])}")
    print(f"Failed creations: {len(results['failed'])}")
    
    if results['created']:
        print("\n✅ Successfully created users:")
        for user in results['created']:
            print(f"   - {user['name']} ({user['email']}) - {user['role']}")
    
    if results['failed']:
        print("\n❌ Failed creations:")
        for user in results['failed']:
            print(f"   - {user['name']} ({user['email']}) - {user['role']}")
    
    success_rate = len(results['created']) / len(test_users) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All tests passed! Admin user creation is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)