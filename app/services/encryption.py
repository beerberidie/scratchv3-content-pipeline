"""
Encryption service for securing sensitive data
"""
import base64
import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize the encryption cipher"""
        if not settings.encryption_key:
            logger.warning("No encryption key configured. Sensitive data will not be encrypted.")
            return
        
        try:
            # Ensure the key is properly formatted
            key = settings.encryption_key
            if isinstance(key, str):
                key = key.encode()
            
            self._fernet = Fernet(key)
            logger.info("Encryption service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            self._fernet = None
    
    def encrypt(self, data: str) -> Optional[str]:
        """
        Encrypt a string
        
        Args:
            data: String to encrypt
        
        Returns:
            Encrypted string (base64 encoded) or None if encryption fails
        """
        if not data:
            return None
        
        if not self._fernet:
            logger.warning("Encryption not available. Returning data as-is.")
            return data
        
        try:
            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None
    
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """
        Decrypt a string
        
        Args:
            encrypted_data: Base64 encoded encrypted string
        
        Returns:
            Decrypted string or None if decryption fails
        """
        if not encrypted_data:
            return None
        
        if not self._fernet:
            logger.warning("Encryption not available. Returning data as-is.")
            return encrypted_data
        
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            # Decrypt
            decrypted_data = self._fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except (InvalidToken, Exception) as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def encrypt_api_key(self, api_key: str) -> Optional[str]:
        """
        Encrypt an API key
        
        Args:
            api_key: API key to encrypt
        
        Returns:
            Encrypted API key or None if encryption fails
        """
        if not api_key or not api_key.strip():
            return None
        
        return self.encrypt(api_key.strip())
    
    def decrypt_api_key(self, encrypted_api_key: str) -> Optional[str]:
        """
        Decrypt an API key
        
        Args:
            encrypted_api_key: Encrypted API key
        
        Returns:
            Decrypted API key or None if decryption fails
        """
        if not encrypted_api_key:
            return None
        
        return self.decrypt(encrypted_api_key)
    
    def is_encryption_available(self) -> bool:
        """
        Check if encryption is available
        
        Returns:
            True if encryption is properly configured
        """
        return self._fernet is not None
    
    def rotate_key(self, new_key: str, old_encrypted_data: dict) -> dict:
        """
        Rotate encryption key and re-encrypt data
        
        Args:
            new_key: New encryption key
            old_encrypted_data: Dictionary of encrypted data to re-encrypt
        
        Returns:
            Dictionary with re-encrypted data
        """
        if not self.is_encryption_available():
            logger.error("Cannot rotate key: encryption not available")
            return old_encrypted_data
        
        # Store old fernet instance
        old_fernet = self._fernet
        
        try:
            # Initialize with new key
            self._fernet = Fernet(new_key.encode() if isinstance(new_key, str) else new_key)
            
            re_encrypted_data = {}
            
            for key, encrypted_value in old_encrypted_data.items():
                if encrypted_value:
                    # Decrypt with old key
                    try:
                        encrypted_bytes = base64.b64decode(encrypted_value.encode())
                        decrypted_data = old_fernet.decrypt(encrypted_bytes)
                        
                        # Re-encrypt with new key
                        new_encrypted_data = self._fernet.encrypt(decrypted_data)
                        re_encrypted_data[key] = base64.b64encode(new_encrypted_data).decode()
                        
                    except Exception as e:
                        logger.error(f"Failed to rotate key for {key}: {e}")
                        re_encrypted_data[key] = encrypted_value  # Keep old value
                else:
                    re_encrypted_data[key] = encrypted_value
            
            logger.info("Key rotation completed successfully")
            return re_encrypted_data
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            # Restore old fernet instance
            self._fernet = old_fernet
            return old_encrypted_data


# Global encryption service instance
encryption_service = EncryptionService()
