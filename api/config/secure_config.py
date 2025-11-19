"""
Secure configuration for Greenspot Grocer API
"""
import os
from encryption_utils import decrypt_password

# Encrypted database password (encrypted version of 'devpwd')
DB_PASSWORD_ENCRYPTED = 'Z0FBQUFBQnBIVkd4WnJodUpnZU5PY2hNQi1EbzNXZkplSTVnOUlvS25jWkNVT01sLU44WlJ5NUlKOVZSaDJmVU4zSFhLdFFaZkNTMk9QcDhkQnVjNjRLRHR6cGFVMk55SGc9PQ=='

# Database configuration with encrypted password
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': decrypt_password(DB_PASSWORD_ENCRYPTED),
    'database': os.getenv('DB_NAME', 'greenspot_grocer'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'charset': 'utf8mb4',
    'autocommit': True
}

# JWT Configuration
JWT_CONFIG = {
    'secret_key': os.getenv('JWT_SECRET_KEY', 'greenspot_grocer_secret_key_2025'),
    'algorithm': 'HS256',
    'access_token_expire_minutes': int(os.getenv('JWT_EXPIRE_MINUTES', '30'))
}

# API Configuration
API_CONFIG = {
    'title': 'Greenspot Grocer Analytics API',
    'description': 'Secure REST API for Greenspot Grocer business analytics',
    'version': '2.1.0',
    'host': os.getenv('API_HOST', '127.0.0.1'),
    'port': int(os.getenv('API_PORT', '8000')),
    'cors_origins': os.getenv('CORS_ORIGINS', '*').split(',')
}

# Default admin credentials (in production, store in secure vault)
ADMIN_CREDENTIALS = {
    'username': os.getenv('ADMIN_USERNAME', 'admin'),
    'password': os.getenv('ADMIN_PASSWORD', 'admin123')
}

def get_database_config():
    """Get database configuration with decrypted password"""
    return DATABASE_CONFIG.copy()

def get_jwt_config():
    """Get JWT configuration"""
    return JWT_CONFIG.copy()

def get_api_config():
    """Get API configuration"""
    return API_CONFIG.copy()

def get_admin_credentials():
    """Get admin credentials"""
    return ADMIN_CREDENTIALS.copy()