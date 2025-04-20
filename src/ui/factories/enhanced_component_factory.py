"""Enhanced component factory for AutoQliq UI."""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Dict, Any, List, Callable

from src.core.exceptions import UIError
from src.ui.components.workflow_list import WorkflowList
from src.ui.components.action_list import ActionList
from src.ui.components.credential_list import CredentialList
from src.ui.components.execution_log import ExecutionLog

logger = logging.getLogger(__name__)


class EnhancedComponentFactory:
    """
    Factory for creating enhanced UI components.
    
    This class provides methods for creating enhanced UI components with consistent
    styling and behavior.
    """
    
    @staticmethod
    def create_workflow_list(
        parent: tk.Widget,
        on_select: Optional[Callable[[str], None]] = None,
        on_create: Optional[Callable[[], None]] = None,
        on_edit: Optional[Callable[[str], None]] = None,
        on_delete: Optional[Callable[[str], None]] = None,
        height: int = 15,
        width: int = 30
    ) -> WorkflowList:
        """
        Create a workflow list component.
        
        Args:
            parent: The parent widget
            on_select: Callback when a workflow is selected
            on_create: Callback when the create button is clicked
            on_edit: Callback when the edit button is clicked
            on_delete: Callback when the delete button is clicked
            height: Height of the listbox in lines
            width: Width of the listbox in characters
            
        Returns:
            A WorkflowList component
            
        Raises:
            UIError: If the component cannot be created
        """
        try:
            return WorkflowList(
                parent,
                on_select=on_select,
                on_create=on_create,
                on_edit=on_edit,
                on_delete=on_delete,
                height=height,
                width=width
            )
        except Exception as e:
            error_msg = "Failed to create WorkflowList component"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="WorkflowList", cause=e) from e
    
    @staticmethod
    def create_action_list(
        parent: tk.Widget,
        on_select: Optional[Callable[[int], None]] = None,
        on_add: Optional[Callable[[], None]] = None,
        on_edit: Optional[Callable[[int], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None,
        on_move_up: Optional[Callable[[int], None]] = None,
        on_move_down: Optional[Callable[[int], None]] = None,
        height: int = 15,
        width: int = 50
    ) -> ActionList:
        """
        Create an action list component.
        
        Args:
            parent: The parent widget
            on_select: Callback when an action is selected
            on_add: Callback when the add button is clicked
            on_edit: Callback when the edit button is clicked
            on_delete: Callback when the delete button is clicked
            on_move_up: Callback when the move up button is clicked
            on_move_down: Callback when the move down button is clicked
            height: Height of the listbox in lines
            width: Width of the listbox in characters
            
        Returns:
            An ActionList component
            
        Raises:
            UIError: If the component cannot be created
        """
        try:
            return ActionList(
                parent,
                on_select=on_select,
                on_add=on_add,
                on_edit=on_edit,
                on_delete=on_delete,
                on_move_up=on_move_up,
                on_move_down=on_move_down,
                height=height,
                width=width
            )
        except Exception as e:
            error_msg = "Failed to create ActionList component"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="ActionList", cause=e) from e
    
    @staticmethod
    def create_credential_list(
        parent: tk.Widget,
        on_select: Optional[Callable[[str], None]] = None,
        on_create: Optional[Callable[[], None]] = None,
        on_edit: Optional[Callable[[str], None]] = None,
        on_delete: Optional[Callable[[str], None]] = None,
        height: int = 10,
        width: int = 30
    ) -> CredentialList:
        """
        Create a credential list component.
        
        Args:
            parent: The parent widget
            on_select: Callback when a credential is selected
            on_create: Callback when the create button is clicked
            on_edit: Callback when the edit button is clicked
            on_delete: Callback when the delete button is clicked
            height: Height of the listbox in lines
            width: Width of the listbox in characters
            
        Returns:
            A CredentialList component
            
        Raises:
            UIError: If the component cannot be created
        """
        try:
            return CredentialList(
                parent,
                on_select=on_select,
                on_create=on_create,
                on_edit=on_edit,
                on_delete=on_delete,
                height=height,
                width=width
            )
        except Exception as e:
            error_msg = "Failed to create CredentialList component"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="CredentialList", cause=e) from e
    
    @staticmethod
    def create_execution_log(
        parent: tk.Widget,
        on_clear: Optional[Callable[[], None]] = None,
        on_save: Optional[Callable[[], None]] = None,
        height: int = 15,
        width: int = 80
    ) -> ExecutionLog:
        """
        Create an execution log component.
        
        Args:
            parent: The parent widget
            on_clear: Callback when the clear button is clicked
            on_save: Callback when the save button is clicked
            height: Height of the text widget in lines
            width: Width of the text widget in characters
            
        Returns:
            An ExecutionLog component
            
        Raises:
            UIError: If the component cannot be created
        """
        try:
            return ExecutionLog(
                parent,
                on_clear=on_clear,
                on_save=on_save,
                height=height,
                width=width
            )
        except Exception as e:
            error_msg = "Failed to create ExecutionLog component"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="ExecutionLog", cause=e) from e
