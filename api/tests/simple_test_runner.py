#!/usr/bin/env python3
"""
Simple Test Runner for Greenspot Grocer API (Windows Compatible)
"""
import os
import sys
import subprocess
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def run_test(test_name, test_file, description):
    """Run a specific test and return results"""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"Description: {description}")
    print(f"File: {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"PASSED - {test_name}")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print(f"FAILED - {test_name}")
            if result.stderr:
                print("Error:")
                print(result.stderr)
            if result.stdout:
                print("Output:")
                print(result.stdout)
        
        return result.returncode == 0
    
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT - {test_name} (30s)")
        return False
    except Exception as e:
        print(f"EXCEPTION - {test_name}: {e}")
        return False

def main():
    """Run all tests"""
    print("GREENSPOT GROCER API - TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Change to tests directory
    test_dir = os.path.dirname(__file__)
    os.chdir(test_dir)
    
    tests = [
        ("Database Connection Test", "db_test.py", "Test database connectivity and basic queries"),
        ("Schema Validation Test", "schema_check.py", "Validate database schema and table structure")
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_name, test_file, description in tests:
        if os.path.exists(test_file):
            success = run_test(test_name, test_file, description)
            results.append((test_name, success))
            if success:
                passed += 1
            else:
                failed += 1
        else:
            print(f"FILE NOT FOUND: {test_name} - {test_file}")
            results.append((test_name, False))
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    for test_name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\nRESULTS: {passed} passed, {failed} failed, {len(results)} total")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed == 0:
        print("ALL TESTS PASSED!")
        return 0
    else:
        print(f"{failed} TESTS FAILED!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)