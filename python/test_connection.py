"""
Test MySQL connection for Greenspot Grocer
==========================================

Run this script to test your MySQL connection before running the full ETL.
"""

import mysql.connector
from mysql.connector import Error
from config import DATABASE_CONFIG

def test_connection():
    """Test MySQL connection with current config"""
    print("🔧 Testing MySQL Connection...")
    print("=" * 40)
    
    try:
        # Test basic connection (without database)
        print("1. Testing basic MySQL connection...")
        connection = mysql.connector.connect(
            host=DATABASE_CONFIG['host'],
            port=DATABASE_CONFIG.get('port', 3306),
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password']
        )
        
        if connection.is_connected():
            print("   ✅ Connected to MySQL server successfully!")
            
            # Get server info
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"   📋 MySQL version: {version[0]}")
            
            # Test database creation
            print("\n2. Testing database creation...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_CONFIG['database']}")
            print(f"   ✅ Database '{DATABASE_CONFIG['database']}' ready")
            
            # Test using the database
            cursor.execute(f"USE {DATABASE_CONFIG['database']}")
            print(f"   ✅ Successfully switched to '{DATABASE_CONFIG['database']}'")
            
            cursor.close()
            connection.close()
            
            print("\n🎉 Connection test PASSED!")
            print("\nNext steps:")
            print("1. Run the schema creation in MySQL Workbench")
            print("2. Execute: python greenspot_etl.py")
            return True
            
    except Error as e:
        print(f"   ❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        if "Access denied" in str(e):
            print("   • Check username/password in config.py")
            print("   • Verify MySQL user has proper permissions")
        elif "Can't connect" in str(e):
            print("   • Make sure MySQL server is running")
            print("   • Check if port 3306 is correct")
            print("   • Verify host is 'localhost'")
        else:
            print("   • Check MySQL Workbench connection first")
            print("   • Verify mysql-connector-python is installed")
        return False
    
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def show_current_config():
    """Display current configuration"""
    print("📋 Current Configuration:")
    print("-" * 25)
    print(f"Host: {DATABASE_CONFIG['host']}")
    print(f"Port: {DATABASE_CONFIG.get('port', 3306)}")
    print(f"Database: {DATABASE_CONFIG['database']}")
    print(f"User: {DATABASE_CONFIG['user']}")
    print(f"Password: {'*' * len(DATABASE_CONFIG['password']) if DATABASE_CONFIG['password'] else '(empty)'}")
    print()

if __name__ == "__main__":
    print("🛒 Greenspot Grocer - MySQL Connection Test")
    print("=" * 50)
    
    show_current_config()
    
    # Test connection
    success = test_connection()
    
    if not success:
        print("\n⚠️  Please fix connection issues before proceeding")
        print("Update credentials in config.py if needed. ")
    
    input("\nPress Enter to exit...")