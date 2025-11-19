#!/usr/bin/env python3
"""
Complete test of the Greenspot Grocer API with detailed error logging
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def main():
    print("🚀 Starting Detailed Greenspot Grocer API Tests")
    print("=" * 60)
    
    # Test 1: Health Check
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: {data.get('status', 'unknown')}")
            print(f"✅ Database: {data.get('database', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the API server is running on port 8001")
        return
    
    # Test 2: Authentication
    print("\n🔐 Authenticating...")
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{BASE_URL}/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print("✅ Authentication successful")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Test 3: Executive Summary
    print("\n📊 Testing executive summary...")
    try:
        response = requests.get(f"{BASE_URL}/executive-summary", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Executive summary successful")
            print(f"   Total Transactions: {data.get('total_transactions', 'N/A')}")
            print(f"   Total Revenue: ${data.get('total_revenue', 'N/A')}")
        else:
            print(f"❌ Executive summary failed: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Executive summary error: {e}")
    
    # Test 4: Product Performance
    print("\n📈 Testing product performance...")
    try:
        response = requests.get(f"{BASE_URL}/product-performance?limit=5", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Product performance successful")
            print(f"   Products returned: {len(data)}")
        else:
            print(f"❌ Product performance failed: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Product performance error: {e}")
    
    # Test 5: Customer Insights
    print("\n👥 Testing customer insights...")
    try:
        response = requests.get(f"{BASE_URL}/customer-insights?limit=5", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Customer insights successful")
            print(f"   Customers returned: {len(data)}")
        else:
            print(f"❌ Customer insights failed: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Customer insights error: {e}")
    
    # Test 6: Inventory Status
    print("\n📦 Testing inventory status...")
    try:
        response = requests.get(f"{BASE_URL}/inventory-status", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Inventory status successful")
            print(f"   Products returned: {len(data)}")
        else:
            print(f"❌ Inventory status failed: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Inventory status error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 API Testing Complete!")

if __name__ == "__main__":
    main()