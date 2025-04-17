"""Sensitive key detector for workflow execution results.

This module provides the SensitiveKeyDetector class for detecting sensitive keys.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


class SensitiveKeyDetector:
    """
    Detects sensitive keys in workflow execution results.
    
    Responsible for identifying keys that might contain sensitive information.
    """
    
    def __init__(self, sensitive_words: List[str] = None):
        """
        Initialize the sensitive key detector.
        
        Args:
            sensitive_words: List of words that indicate sensitive data
        """
        # Default list of words that might indicate sensitive information
        self.sensitive_words = sensitive_words or [
            "password", "token", "secret", "key", "credential", "auth"
        ]
    
    def is_sensitive_key(self, key: str) -> bool:
        """
        Determine if a key might contain sensitive information.
        
        Args:
            key: The key to check
            
        Returns:
            bool: True if the key might contain sensitive information
        """
        return any(sensitive_word in key.lower() for sensitive_word in self.sensitive_words)
    
    def detect_sensitive_keys(self, keys: List[str]) -> List[str]:
        """
        Detect sensitive keys from a list of keys.
        
        Args:
            keys: List of keys to check
            
        Returns:
            List[str]: List of sensitive keys
        """
        return [key for key in keys if self.is_sensitive_key(key)]
