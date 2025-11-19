"""
Greenspot Grocer Setup Script
============================

This script automates the complete setup of the Greenspot Grocer database project.
Run this after configuring your database credentials in config.py.

Usage: python setup_project.py
"""

import sys
import os
import subprocess
import logging
from config import DATABASE_CONFIG, CSV_FILE_PATH
from greenspot_etl import GreenspotETL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import pandas
        import mysql.connector
        logger.info("✓ All Python dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"✗ Missing dependency: {e}")
        logger.info("Please run: pip install -r requirements.txt")
        return False

def test_database_connection():
    """Test database connection"""
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=DATABASE_CONFIG['host'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password']
        )
        conn.close()
        logger.info("✓ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False

def create_database():
    """Create the greenspot_grocer database if it doesn't exist"""
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=DATABASE_CONFIG['host'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_CONFIG['database']}")
        cursor.close()
        conn.close()
        logger.info(f"✓ Database '{DATABASE_CONFIG['database']}' ready")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to create database: {e}")
        return False

def run_schema_creation():
    """Execute the schema creation script"""
    try:
        schema_file = "../sql/create_schema.sql"
        if not os.path.exists(schema_file):
            logger.error(f"✗ Schema file not found: {schema_file}")
            return False
        
        # Use mysql command line tool
        cmd = [
            "mysql",
            f"--host={DATABASE_CONFIG['host']}",
            f"--user={DATABASE_CONFIG['user']}",
            f"--password={DATABASE_CONFIG['password']}",
            DATABASE_CONFIG['database']
        ]
        
        with open(schema_file, 'r') as f:
            result = subprocess.run(cmd, stdin=f, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ Database schema created successfully")
            return True
        else:
            logger.error(f"✗ Schema creation failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error running schema creation: {e}")
        return False

def check_csv_file():
    """Check if CSV file exists"""
    if os.path.exists(CSV_FILE_PATH):
        logger.info(f"✓ CSV file found: {CSV_FILE_PATH}")
        return True
    else:
        logger.error(f"✗ CSV file not found: {CSV_FILE_PATH}")
        logger.info("Please ensure GreenspotDataset.csv is in the correct location")
        return False

def run_etl():
    """Run the ETL process"""
    try:
        logger.info("Starting ETL process...")
        etl = GreenspotETL(DATABASE_CONFIG)
        success = etl.run_etl(CSV_FILE_PATH)
        
        if success:
            logger.info("✓ ETL process completed successfully")
            return True
        else:
            logger.error("✗ ETL process failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ ETL process error: {e}")
        return False

def run_validation():
    """Run validation queries"""
    try:
        validation_file = "../sql/validation_queries.sql"
        if not os.path.exists(validation_file):
            logger.warning(f"⚠ Validation file not found: {validation_file}")
            return True
        
        cmd = [
            "mysql",
            f"--host={DATABASE_CONFIG['host']}",
            f"--user={DATABASE_CONFIG['user']}",
            f"--password={DATABASE_CONFIG['password']}",
            DATABASE_CONFIG['database']
        ]
        
        with open(validation_file, 'r') as f:
            result = subprocess.run(cmd, stdin=f, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ Validation queries executed successfully")
            print("\nVALIDATION RESULTS:")
            print("=" * 50)
            print(result.stdout)
            return True
        else:
            logger.error(f"✗ Validation failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.warning(f"⚠ Could not run validation queries: {e}")
        return True  # Non-critical failure

def print_summary():
    """Print setup summary and next steps"""
    print("\n" + "=" * 60)
    print("🎉 GREENSPOT GROCER SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the validation output above")
    print("2. Run analytics queries:")
    print(f"   mysql -u {DATABASE_CONFIG['user']} -p {DATABASE_CONFIG['database']} < ../sql/analytics_queries.sql")
    print("3. Explore the database structure:")
    print(f"   mysql -u {DATABASE_CONFIG['user']} -p {DATABASE_CONFIG['database']}")
    print("4. Review logs for any issues:")
    print("   cat etl_log.txt")
    print("\nDatabase ready for use! 🚀")
    print("=" * 60)

def main():
    """Main setup function"""
    print("🛒 Greenspot Grocer Database Setup")
    print("=" * 40)
    
    # Step 1: Check dependencies
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        return False
    
    # Step 2: Test database connection
    print("\n2. Testing database connection...")
    if not test_database_connection():
        print("Please check your database configuration in config.py")
        return False
    
    # Step 3: Create database
    print("\n3. Creating database...")
    if not create_database():
        return False
    
    # Step 4: Create schema
    print("\n4. Creating database schema...")
    if not run_schema_creation():
        print("Note: You may need to run the schema creation manually:")
        print(f"mysql -u {DATABASE_CONFIG['user']} -p {DATABASE_CONFIG['database']} < ../sql/create_schema.sql")
    
    # Step 5: Check CSV file
    print("\n5. Checking CSV file...")
    if not check_csv_file():
        return False
    
    # Step 6: Run ETL
    print("\n6. Running ETL process...")
    if not run_etl():
        return False
    
    # Step 7: Run validation
    print("\n7. Running validation...")
    run_validation()  # Non-critical if it fails
    
    # Step 8: Print summary
    print_summary()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during setup: {e}")
        sys.exit(1)