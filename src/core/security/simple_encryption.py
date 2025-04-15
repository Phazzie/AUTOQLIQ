"""Basic encryption implementation using Fernet symmetric encryption."""

import base64
import logging
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.core.security.encryption import IEncryptionService


logger = logging.getLogger(__name__)


class SimpleEncryptionService(IEncryptionService):
    """
    A simple encryption service using Fernet symmetric encryption.
    
    This implementation uses a key derived from a master key and stored salt.
    The key is stored in memory only during the lifetime of this object.
    """
    
    def __init__(self, key_file_path: Optional[str] = None, master_key: Optional[str] = None):
        """
        Initialize the encryption service.
        
        Args:
            key_file_path: Path to store/retrieve the salt for key derivation.
                If not provided, a default location in the user's home directory is used.
            master_key: Master key used for encryption. If not provided, it will attempt
                to use an environment variable AUTOQLIQ_MASTER_KEY, or generate a warning.
        
        Note:
            In a production environment, you would never hardcode a master key or store it
            in plain text. This implementation is a simplified version for development.
        """
        # Set up key file location
        if key_file_path:
            self.key_file_path = Path(key_file_path)
        else:
            # Default to a directory in user's home
            home = Path.home()
            app_dir = home / ".autoqliq"
            app_dir.mkdir(exist_ok=True)
            self.key_file_path = app_dir / "encryption.key"
        
        # Get master key from argument, environment, or use a default (not secure for production)
        self._master_key = master_key or os.environ.get("AUTOQLIQ_MASTER_KEY")
        if not self._master_key:
            logger.warning(
                "No master key provided and AUTOQLIQ_MASTER_KEY env var not set. "
                "Using insecure default key. NOT RECOMMENDED FOR PRODUCTION."
            )
            self._master_key = "AutoQliq_Default_Insecure_Key_DO_NOT_USE_IN_PRODUCTION"
        
        # Initialize or load salt and derive key
        self._initialize_key()
    
    def _initialize_key(self) -> None:
        """Initialize or load the encryption key from the key file."""
        try:
            if not self.key_file_path.exists():
                # Generate a new salt and save it
                logger.info(f"Creating new encryption key file at {self.key_file_path}")
                salt = os.urandom(16)
                with open(self.key_file_path, "wb") as key_file:
                    key_file.write(salt)
            else:
                # Load existing salt
                logger.debug(f"Loading existing encryption key from {self.key_file_path}")
                with open(self.key_file_path, "rb") as key_file:
                    salt = key_file.read()
            
            # Derive the key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self._master_key.encode()))
            self._fernet = Fernet(key)
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption key: {e}")
            raise ValueError(f"Failed to initialize encryption key: {e}")
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt the given plaintext string.
        
        Args:
            plaintext: The string to be encrypted
            
        Returns:
            The encrypted string as a base64-encoded value
            
        Raises:
            Exception: If encryption fails
        """
        try:
            encrypted_bytes = self._fernet.encrypt(plaintext.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise Exception(f"Encryption failed: {e}")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt the given ciphertext string.
        
        Args:
            ciphertext: The encrypted string to be decrypted
            
        Returns:
            The decrypted plaintext string
            
        Raises:
            Exception: If decryption fails
        """
        try:
            decrypted_bytes = self._fernet.decrypt(ciphertext.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise Exception(f"Decryption failed: {e}")
