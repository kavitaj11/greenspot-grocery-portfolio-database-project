#!/usr/bin/env python3
"""
Password Management Utility for Greenspot Grocer API - Updated for organized structure
"""
import argparse
import getpass
import os
import sys

# Add the utils directory to the path
sys.path.append(os.path.dirname(__file__))
from encryption_utils import encrypt_password, decrypt_password

def encrypt_new_password():
    """Encrypt a new password"""
    print("🔐 Password Encryption Utility")
    print("=" * 40)
    
    password = getpass.getpass("Enter password to encrypt: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if password != confirm_password:
        print("❌ Passwords don't match!")
        return
    
    encrypted = encrypt_password(password)
    print(f"\n✅ Password encrypted successfully!")
    print(f"Encrypted value: {encrypted}")
    print(f"\n📝 Add this to your config/__init__.py:")
    print(f"DB_PASSWORD_ENCRYPTED = '{encrypted}'")

def decrypt_existing_password():
    """Decrypt an existing password"""
    print("🔓 Password Decryption Utility")
    print("=" * 40)
    
    encrypted_password = input("Enter encrypted password: ")
    
    try:
        decrypted = decrypt_password(encrypted_password)
        print(f"\n✅ Password decrypted successfully!")
        print(f"Decrypted value: {decrypted}")
    except Exception as e:
        print(f"❌ Decryption failed: {e}")

def test_encryption():
    """Test encryption/decryption with sample data"""
    print("🧪 Testing Encryption/Decryption")
    print("=" * 40)
    
    test_password = "test123"
    print(f"Original: {test_password}")
    
    encrypted = encrypt_password(test_password)
    print(f"Encrypted: {encrypted}")
    
    decrypted = decrypt_password(encrypted)
    print(f"Decrypted: {decrypted}")
    
    if test_password == decrypted:
        print("✅ Encryption/Decryption test passed!")
    else:
        print("❌ Encryption/Decryption test failed!")

def change_database_password():
    """Generate new encrypted password for database"""
    print("🔄 Change Database Password")
    print("=" * 40)
    
    new_password = getpass.getpass("Enter new database password: ")
    confirm_password = getpass.getpass("Confirm new database password: ")
    
    if new_password != confirm_password:
        print("❌ Passwords don't match!")
        return
    
    encrypted = encrypt_password(new_password)
    print(f"\n✅ New database password encrypted!")
    print(f"Encrypted value: {encrypted}")
    print(f"\n📝 Update config/__init__.py with:")
    print(f"DB_PASSWORD_ENCRYPTED = '{encrypted}'")
    print(f"\n⚠️  Don't forget to update your MySQL user password:")
    print(f"ALTER USER 'root'@'localhost' IDENTIFIED BY '{new_password}';")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Password Management Utility")
    parser.add_argument('action', choices=['encrypt', 'decrypt', 'test', 'change-db'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    print("📁 Running from organized structure (utils folder)")
    
    if args.action == 'encrypt':
        encrypt_new_password()
    elif args.action == 'decrypt':
        decrypt_existing_password()
    elif args.action == 'test':
        test_encryption()
    elif args.action == 'change-db':
        change_database_password()

if __name__ == "__main__":
    main()