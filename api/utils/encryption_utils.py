"""
Encryption utilities for sensitive configuration data
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ConfigEncryption:
    def __init__(self, master_key: str = None):
        """Initialize encryption with master key"""
        if master_key is None:
            # Use environment variable or default
            master_key = os.getenv('GREENSPOT_MASTER_KEY', 'greenspot_default_key_2025')
        
        self.master_key = master_key.encode()
        self.fernet = self._create_fernet()
    
    def _create_fernet(self) -> Fernet:
        """Create Fernet encryption instance"""
        # Create a salt (in production, store this securely)
        salt = b'greenspot_salt_2025'
        
        # Derive key from master key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string"""
        encrypted = self.fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt encrypted string"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
        decrypted = self.fernet.decrypt(encrypted_bytes)
        return decrypted.decode()

# Global encryption instance
_encryption = ConfigEncryption()

def encrypt_password(password: str) -> str:
    """Encrypt a password"""
    return _encryption.encrypt(password)

def decrypt_password(encrypted_password: str) -> str:
    """Decrypt a password"""
    return _encryption.decrypt(encrypted_password)

# Utility function to generate encrypted password
def generate_encrypted_password(password: str) -> None:
    """Generate and print encrypted password for configuration"""
    encrypted = encrypt_password(password)
    print(f"Original password: {password}")
    print(f"Encrypted password: {encrypted}")
    print(f"Add this to your config: DB_PASSWORD_ENCRYPTED = '{encrypted}'")

if __name__ == "__main__":
    # Generate encrypted password for 'devpwd'
    generate_encrypted_password("devpwd")