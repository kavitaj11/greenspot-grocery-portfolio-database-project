"""
Legacy configuration for Greenspot Grocer API
Maintained for backward compatibility
"""

# Basic database configuration (non-encrypted)
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'greenspot_grocer',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': True
}

# JWT settings
SECRET_KEY = "greenspot_grocer_secret_key_2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS settings
CORS_ORIGINS = ["*"]

# Note: This is the legacy configuration file.
# For secure, encrypted configuration, use the new organized structure:
# - config/__init__.py for encrypted configuration
# - utils/encryption_utils.py for encryption utilities