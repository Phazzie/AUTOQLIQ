"""Encryption service interface for secure data handling."""

import abc
from typing import Optional


class IEncryptionService(abc.ABC):
    """Interface for encryption services to securely encrypt and decrypt data."""

    @abc.abstractmethod
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt the given plaintext string.
        
        Args:
            plaintext: The string to be encrypted
            
        Returns:
            The encrypted string
            
        Raises:
            Exception: If encryption fails for any reason
        """
        pass
    
    @abc.abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt the given ciphertext string.
        
        Args:
            ciphertext: The encrypted string to be decrypted
            
        Returns:
            The decrypted plaintext string
            
        Raises:
            Exception: If decryption fails for any reason
        """
        pass
