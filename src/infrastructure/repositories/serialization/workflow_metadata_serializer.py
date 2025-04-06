"""Workflow metadata serialization utilities for AutoQliq.

This module provides functions and classes for serializing and deserializing
workflow metadata to and from dictionary representations.
"""

import logging
import json
from typing import Dict, Any, List, Optional

from src.core.interfaces import IAction
from src.core.exceptions import SerializationError

logger = logging.getLogger(__name__)


class WorkflowMetadataSerializer:
    """
    Handles serialization and deserialization of workflow metadata.
    
    This class provides methods for extracting and combining workflow metadata
    with action data, allowing workflows to be stored with additional information.
    """
    
    @staticmethod
    def extract_metadata(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from workflow data.
        
        Args:
            workflow_data: The workflow data containing metadata and actions
            
        Returns:
            A dictionary containing only the metadata
            
        Raises:
            SerializationError: If the metadata cannot be extracted
        """
        try:
            # Create a copy of the workflow data
            metadata = workflow_data.copy()
            
            # Remove the actions key if it exists
            if 'actions' in metadata:
                del metadata['actions']
                
            return metadata
        except Exception as e:
            error_msg = f"Failed to extract workflow metadata: {str(e)}"
            logger.error(error_msg)
            raise SerializationError(error_msg) from e
    
    @staticmethod
    def combine_metadata(metadata: Dict[str, Any], actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine metadata with action data.
        
        Args:
            metadata: The workflow metadata
            actions: The serialized actions
            
        Returns:
            A dictionary containing both metadata and actions
            
        Raises:
            SerializationError: If the data cannot be combined
        """
        try:
            # Create a copy of the metadata
            workflow_data = metadata.copy()
            
            # Add the actions
            workflow_data['actions'] = actions
            
            return workflow_data
        except Exception as e:
            error_msg = f"Failed to combine workflow metadata with actions: {str(e)}"
            logger.error(error_msg)
            raise SerializationError(error_msg) from e


# Module-level functions that use the WorkflowMetadataSerializer class
def extract_workflow_metadata(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from workflow data.
    
    Args:
        workflow_data: The workflow data containing metadata and actions
        
    Returns:
        A dictionary containing only the metadata
        
    Raises:
        SerializationError: If the metadata cannot be extracted
    """
    return WorkflowMetadataSerializer.extract_metadata(workflow_data)


def extract_workflow_actions(workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract action data from workflow data.
    
    Args:
        workflow_data: The workflow data containing metadata and actions
        
    Returns:
        A list of dictionary representations of the actions
        
    Raises:
        SerializationError: If the actions cannot be extracted
    """
    try:
        return workflow_data.get('actions', [])
    except Exception as e:
        error_msg = f"Failed to extract workflow actions: {str(e)}"
        logger.error(error_msg)
        raise SerializationError(error_msg) from e