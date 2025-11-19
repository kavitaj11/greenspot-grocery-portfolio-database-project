"""
Final Test Script for Greenspot Grocer API
"""

import requests
import json
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from datetime import datetime

def test_api():
    """Test all API endpoints"""
    BASE_URL = "http://localhost:8000"
    
    print("🚀 GREENSPOT GROCER API - FINAL TESTING")
    print("=" * 50)
    print(f"Testing API at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("\n1️⃣ Testing Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint successful")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False
    
    # Test 2: Health check
    print("\n2️⃣ Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check successful")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Database: {data.get('database', 'N/A')}")
            
            if data.get('status') != 'healthy':
                print("⚠️  API is unhealthy - continuing with limited tests")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 3: Authentication
    print("\n3️⃣ Testing Authentication")
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{BASE_URL}/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print("✅ Authentication successful")
            print(f"   Token type: {token_data.get('token_type', 'N/A')}")
            print(f"   Expires in: {token_data.get('expires_in', 'N/A')} seconds")
            
            # Set headers for authenticated requests
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Test 4: Executive Summary
    print("\n4️⃣ Testing Executive Summary")
    try:
        response = requests.get(f"{BASE_URL}/executive-summary", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Executive summary successful")
            print(f"   Total Transactions: {data.get('total_transactions', 'N/A'):,}")
            print(f"   Total Revenue: ${data.get('total_revenue', 'N/A'):,.2f}")
            print(f"   Average Transaction: ${data.get('average_transaction_value', 'N/A'):,.2f}")
            print(f"   Unique Customers: {data.get('unique_customers', 'N/A'):,}")
        else:
            print(f"❌ Executive summary failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Executive summary error: {e}")
    
    # Test 5: Product Performance
    print("\n5️⃣ Testing Product Performance")
    try:
        response = requests.get(f"{BASE_URL}/product-performance?limit=5", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Product performance successful")
            print(f"   Products returned: {len(data)}")
            if data:
                top_product = data[0]
                print(f"   Top Product: {top_product.get('product_name', 'N/A')}")
                print(f"   Revenue: ${top_product.get('total_revenue', 'N/A'):,.2f}")
        else:
            print(f"❌ Product performance failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Product performance error: {e}")
    
    # Test 6: Customer Insights
    print("\n6️⃣ Testing Customer Insights")
    try:
        response = requests.get(f"{BASE_URL}/customer-insights?limit=5", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Customer insights successful")
            print(f"   Customers returned: {len(data)}")
            if data:
                top_customer = data[0]
                print(f"   Top Customer: {top_customer.get('customer_name', 'N/A')}")
                print(f"   Total Spent: ${top_customer.get('total_spent', 'N/A'):,.2f}")
        else:
            print(f"❌ Customer insights failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Customer insights error: {e}")
    
    # Test 7: Inventory Status
    print("\n7️⃣ Testing Inventory Status")
    try:
        response = requests.get(f"{BASE_URL}/inventory-status", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Inventory status successful")
            print(f"   Products in inventory: {len(data)}")
            
            # Count stock levels
            stock_levels = {}
            for item in data:
                status = item.get('stock_status', 'Unknown')
                stock_levels[status] = stock_levels.get(status, 0) + 1
            
            for status, count in stock_levels.items():
                print(f"   {status}: {count} products")
        else:
            print(f"❌ Inventory status failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Inventory status error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API TESTING COMPLETED")
    print("📚 Visit http://localhost:8000/docs for interactive documentation")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    # Wait a moment for server to start if just launched
    time.sleep(1)
    test_api()