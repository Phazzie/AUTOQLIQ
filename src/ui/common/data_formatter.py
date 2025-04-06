"""Data formatter for UI components."""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from src.core.interfaces import IAction


class DataFormatter:
    """Formatter for data displayed in UI components.
    
    This class provides methods for formatting data for display in UI components.
    """
    
    @staticmethod
    def format_action(action: IAction) -> str:
        """Format an action for display.
        
        Args:
            action: The action to format
            
        Returns:
            A formatted string representation of the action
        """
        action_type = action.action_type
        
        if action_type == "Navigate":
            return f"Navigate to {getattr(action, 'url', 'unknown URL')}"
        elif action_type == "Click":
            return f"Click on {getattr(action, 'selector', 'unknown element')}"
        elif action_type == "Type":
            return f"Type '{getattr(action, 'text', '')}' into {getattr(action, 'selector', 'unknown element')}"
        elif action_type == "Wait":
            return f"Wait for {getattr(action, 'duration_seconds', 0)} seconds"
        elif action_type == "Screenshot":
            return f"Take screenshot: {getattr(action, 'name', 'unnamed')}"
        else:
            return f"{action_type}: {action.name}"
    
    @staticmethod
    def format_action_list(actions: List[IAction]) -> List[str]:
        """Format a list of actions for display.
        
        Args:
            actions: The actions to format
            
        Returns:
            A list of formatted string representations of the actions
        """
        return [DataFormatter.format_action(action) for action in actions]
    
    @staticmethod
    def format_credential(credential: Dict[str, str]) -> str:
        """Format a credential for display.
        
        Args:
            credential: The credential to format
            
        Returns:
            A formatted string representation of the credential
        """
        name = credential.get("name", "Unnamed")
        username = credential.get("username", "")
        
        return f"{name} ({username})"
    
    @staticmethod
    def format_credential_list(credentials: List[Dict[str, str]]) -> List[str]:
        """Format a list of credentials for display.
        
        Args:
            credentials: The credentials to format
            
        Returns:
            A list of formatted string representations of the credentials
        """
        return [DataFormatter.format_credential(credential) for credential in credentials]
    
    @staticmethod
    def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format a datetime for display.
        
        Args:
            dt: The datetime to format
            format_string: The format string to use
            
        Returns:
            A formatted string representation of the datetime
        """
        return dt.strftime(format_string)
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format a duration in seconds for display.
        
        Args:
            seconds: The duration in seconds
            
        Returns:
            A formatted string representation of the duration
        """
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format a file size in bytes for display.
        
        Args:
            size_bytes: The file size in bytes
            
        Returns:
            A formatted string representation of the file size
        """
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            size_kb = size_bytes / 1024
            return f"{size_kb:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            size_mb = size_bytes / (1024 * 1024)
            return f"{size_mb:.1f} MB"
        else:
            size_gb = size_bytes / (1024 * 1024 * 1024)
            return f"{size_gb:.1f} GB"
