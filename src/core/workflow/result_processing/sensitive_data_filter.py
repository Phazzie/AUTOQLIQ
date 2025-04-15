"""Sensitive data filter for workflow execution results.

This module provides the SensitiveDataFilter class for filtering sensitive data from workflow results.
"""

import logging
from typing import Dict, Any, List, Union

logger = logging.getLogger(__name__)


class SensitiveDataFilter:
    """
    Filters sensitive data from workflow execution results.
    
    Responsible for identifying and masking sensitive information in result data.
    """
    
    def __init__(self, 
                sensitive_words: List[str] = None, 
                mask: str = "********"):
        """
        Initialize the sensitive data filter.
        
        Args:
            sensitive_words: List of words that indicate sensitive data
            mask: String to use for masking sensitive data
        """
        # Default list of words that might indicate sensitive information
        self.sensitive_words = sensitive_words or [
            "password", "token", "secret", "key", "credential", "auth"
        ]
        self.mask = mask
    
    def filter_data(self, data: Any) -> Any:
        """
        Filter sensitive data from any data structure.
        
        Args:
            data: The data to filter
            
        Returns:
            Any: Filtered data with sensitive information masked
        """
        if isinstance(data, dict):
            return self._filter_dict(data)
        elif isinstance(data, list):
            return self._filter_list(data)
        else:
            # For primitive types, return as is
            return data
    
    def _filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter sensitive data from a dictionary.
        
        Args:
            data: The dictionary to filter
            
        Returns:
            Dict[str, Any]: Filtered dictionary
        """
        # Create a copy to avoid modifying the original
        filtered_data = {}
        
        # Process each key in the data
        for key, value in data.items():
            if self._is_sensitive_key(key):
                filtered_data[key] = self.mask
            elif isinstance(value, dict):
                # Recursively filter nested dictionaries
                filtered_data[key] = self._filter_dict(value)
            elif isinstance(value, list):
                # Filter lists that might contain dictionaries
                filtered_data[key] = self._filter_list(value)
            else:
                # Keep non-dictionary, non-list values as is
                filtered_data[key] = value
        
        return filtered_data
    
    def _filter_list(self, data_list: List[Any]) -> List[Any]:
        """
        Filter sensitive data from a list of items.
        
        Args:
            data_list: The list to filter
            
        Returns:
            List[Any]: Filtered list
        """
        filtered_list = []
        
        for item in data_list:
            if isinstance(item, dict):
                # Recursively filter dictionaries in the list
                filtered_list.append(self._filter_dict(item))
            elif isinstance(item, list):
                # Recursively filter nested lists
                filtered_list.append(self._filter_list(item))
            else:
                # Keep non-dictionary, non-list items as is
                filtered_list.append(item)
        
        return filtered_list
    
    def _is_sensitive_key(self, key: str) -> bool:
        """
        Determine if a key might contain sensitive information.
        
        Args:
            key: The key to check
            
        Returns:
            bool: True if the key might contain sensitive information
        """
        return any(sensitive_word in key.lower() for sensitive_word in self.sensitive_words)
