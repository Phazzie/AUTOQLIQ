"""Validation utilities for actions.

This module provides utility functions for validating action parameters.
"""

import logging
from typing import List, Optional

from src.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def validate_locator_type(locator_type: str, valid_types: Optional[List[str]] = None) -> None:
    """Validate locator type.
    
    Args:
        locator_type: The locator type to validate
        valid_types: Optional list of valid locator types. If not provided, uses default list.
        
    Raises:
        ValidationError: If the locator type is invalid
    """
    if valid_types is None:
        valid_types = ["id", "name", "xpath", "css", "link_text", "partial_link_text", "tag_name", "class_name"]
    
    if locator_type not in valid_types:
        raise ValidationError(f"Invalid locator type: {locator_type}. Valid types are: {valid_types}")
