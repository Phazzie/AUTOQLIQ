"""List filter for workflow execution results.

This module provides the ListFilter class for filtering sensitive data from lists.
"""

import logging
from typing import Any, List

logger = logging.getLogger(__name__)


class ListFilter:
    """
    Filters sensitive data from lists in workflow execution results.
    
    Responsible for filtering sensitive data from list structures.
    """
    
    def __init__(self, dictionary_filter=None):
        """
        Initialize the list filter.
        
        Args:
            dictionary_filter: Optional dictionary filter for nested dictionaries
        """
        self.dictionary_filter = dictionary_filter
    
    def filter_list(self, data_list: List[Any]) -> List[Any]:
        """
        Filter sensitive data from a list of items.
        
        Args:
            data_list: The list to filter
            
        Returns:
            List[Any]: Filtered list
        """
        filtered_list = []
        
        for item in data_list:
            if isinstance(item, dict) and self.dictionary_filter:
                # Recursively filter dictionaries in the list
                filtered_list.append(self.dictionary_filter.filter_dict(item, self))
            elif isinstance(item, list):
                # Recursively filter nested lists
                filtered_list.append(self.filter_list(item))
            else:
                # Keep non-dictionary, non-list items as is
                filtered_list.append(item)
        
        return filtered_list
