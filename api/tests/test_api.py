"""
Simple test script to verify the Greenspot Grocer REST API
Run this to test API functionality before deployment
"""

import requests
import json
import time
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "greenspot2025"

def test_api_health() -> bool:
    """Test API health endpoint"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Health: {health_data['status']}")
            print(f"✅ Database: {health_data['database']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def authenticate() -> str:
    """Authenticate and get access token"""
    print("🔐 Authenticating...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": DEFAULT_USERNAME, "password": DEFAULT_PASSWORD},
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Authentication successful")
            return token_data["access_token"]
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return ""
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return ""

def test_executive_summary(token: str) -> bool:
    """Test executive summary endpoint"""
    print("📊 Testing executive summary...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/api/v1/executive-summary",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Executive Summary Retrieved:")
            print(f"   💰 Total Revenue: ${data['total_revenue']}")
            print(f"   👥 Total Customers: {data['total_customers']}")
            print(f"   📋 Total Transactions: {data['total_transactions']}")
            print(f"   📈 Average Order Value: ${data['average_order_value']}")
            print(f"   🏆 Top Product: {data['top_product']}")
            print(f"   📦 Top Category: {data['top_category']}")
            return True
        else:
            print(f"❌ Executive summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Executive summary error: {e}")
        return False

def test_product_performance(token: str) -> bool:
    """Test product performance endpoint"""
    print("📈 Testing product performance...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/api/v1/products/performance?limit=5",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data)} top products:")
            for i, product in enumerate(data[:3], 1):
                print(f"   {i}. {product['product_name']}: ${product['total_revenue']} ({product['units_sold']} units)")
            return True
        else:
            print(f"❌ Product performance failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Product performance error: {e}")
        return False

def test_customer_insights(token: str) -> bool:
    """Test customer insights endpoint"""
    print("👥 Testing customer insights...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/api/v1/customers/insights?limit=5",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data)} customer insights:")
            for i, customer in enumerate(data[:3], 1):
                print(f"   {i}. {customer['customer_name']}: ${customer['total_spent']} ({customer['customer_segment']})")
            return True
        else:
            print(f"❌ Customer insights failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Customer insights error: {e}")
        return False

def test_inventory_status(token: str) -> bool:
    """Test inventory status endpoint"""
    print("📦 Testing inventory status...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/api/v1/inventory/status",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            reorder_needed = sum(1 for item in data if item['needs_reorder'])
            print(f"✅ Retrieved inventory for {len(data)} products")
            print(f"   ⚠️  Products needing reorder: {reorder_needed}")
            
            # Show products needing reorder
            for item in data:
                if item['needs_reorder']:
                    print(f"   🔴 {item['product_name']}: {item['current_stock']} (reorder at {item['reorder_level']})")
            return True
        else:
            print(f"❌ Inventory status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Inventory status error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Starting Greenspot Grocer API Tests")
    print("=" * 50)
    
    # Track test results
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Health Check
    if test_api_health():
        tests_passed += 1
        print()
        
        # Test 2: Authentication
        token = authenticate()
        if token:
            tests_passed += 1
            print()
            
            # Test 3: Executive Summary
            if test_executive_summary(token):
                tests_passed += 1
            print()
            
            # Test 4: Product Performance
            if test_product_performance(token):
                tests_passed += 1
            print()
            
            # Test 5: Customer Insights
            if test_customer_insights(token):
                tests_passed += 1
            print()
            
            # Test 6: Inventory Status
            if test_inventory_status(token):
                tests_passed += 1
            print()
    
    # Print results
    print("=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! API is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the API configuration and database connection.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)