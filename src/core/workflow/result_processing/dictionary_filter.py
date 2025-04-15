"""Dictionary filter for workflow execution results.

This module provides the DictionaryFilter class for filtering sensitive data from dictionaries.
"""

import logging
from typing import Dict, Any, List

from src.core.workflow.result_processing.sensitive_key_detector import SensitiveKeyDetector

logger = logging.getLogger(__name__)


class DictionaryFilter:
    """
    Filters sensitive data from dictionaries in workflow execution results.
    
    Responsible for filtering sensitive data from dictionary structures.
    """
    
    def __init__(self, 
                key_detector: SensitiveKeyDetector,
                mask: str = "********"):
        """
        Initialize the dictionary filter.
        
        Args:
            key_detector: Detector for sensitive keys
            mask: String to use for masking sensitive data
        """
        self.key_detector = key_detector
        self.mask = mask
    
    def filter_dict(self, data: Dict[str, Any], list_filter=None) -> Dict[str, Any]:
        """
        Filter sensitive data from a dictionary.
        
        Args:
            data: The dictionary to filter
            list_filter: Optional list filter for nested lists
            
        Returns:
            Dict[str, Any]: Filtered dictionary
        """
        # Create a copy to avoid modifying the original
        filtered_data = {}
        
        # Process each key in the data
        for key, value in data.items():
            if self.key_detector.is_sensitive_key(key):
                filtered_data[key] = self.mask
            elif isinstance(value, dict):
                # Recursively filter nested dictionaries
                filtered_data[key] = self.filter_dict(value, list_filter)
            elif isinstance(value, list) and list_filter:
                # Filter lists that might contain dictionaries
                filtered_data[key] = list_filter.filter_list(value)
            else:
                # Keep non-dictionary, non-list values as is
                filtered_data[key] = value
        
        return filtered_data
