"""
Configuration file for Greenspot Grocer ETL
"""

# Database configuration - MySQL Workbench Connected
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'greenspot_grocer',
    'user': 'root',          # Use root user like MySQL Workbench
    'password': 'devpwd',          # Update with your MySQL root password
    'charset': 'utf8mb4',
    'use_unicode': True,
    'autocommit': False
}

# File paths
CSV_FILE_PATH = "../GreenspotDataset.csv"
LOG_FILE_PATH = "etl_log.txt"

# ETL Settings
BATCH_SIZE = 100
MAX_RETRY_ATTEMPTS = 3

# Data validation settings
ENABLE_DATA_VALIDATION = True
SKIP_INVALID_RECORDS = True

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"