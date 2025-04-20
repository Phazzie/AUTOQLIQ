"""Dialog factory for AutoQliq UI."""

import tkinter as tk
import logging
from typing import Dict, Any, Optional

from src.core.exceptions import UIError
from src.ui.dialogs.enhanced_action_editor_dialog import EnhancedActionEditorDialog
from src.ui.dialogs.conditional_action_editor_dialog import ConditionalActionEditorDialog
from src.ui.dialogs.loop_action_editor_dialog import LoopActionEditorDialog
from src.ui.dialogs.credential_manager_dialog import CredentialManagerDialog
from src.ui.dialogs.diagnostics_dialog import DiagnosticsDialog

logger = logging.getLogger(__name__)


class DialogFactory:
    """
    Factory for creating dialog windows.

    This class provides methods for creating various dialog windows with
    consistent styling and behavior.
    """

    @staticmethod
    def create_action_editor_dialog(
        parent: tk.Widget,
        action_data: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None
    ) -> EnhancedActionEditorDialog:
        """
        Create an action editor dialog.

        Args:
            parent: The parent widget
            action_data: Initial action data (for editing an existing action)
            title: Custom title for the dialog

        Returns:
            An EnhancedActionEditorDialog instance

        Raises:
            UIError: If the dialog cannot be created
        """
        try:
            return EnhancedActionEditorDialog(
                parent=parent,
                action_data=action_data,
                title=title
            )
        except Exception as e:
            error_msg = "Failed to create action editor dialog"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="EnhancedActionEditorDialog", cause=e) from e

    @staticmethod
    def create_credential_manager_dialog(
        parent: tk.Widget,
        credential_service: Any
    ) -> CredentialManagerDialog:
        """
        Create a credential manager dialog.

        Args:
            parent: The parent widget
            credential_service: The credential service

        Returns:
            A CredentialManagerDialog instance

        Raises:
            UIError: If the dialog cannot be created
        """
        try:
            return CredentialManagerDialog(
                parent=parent,
                credential_service=credential_service
            )
        except Exception as e:
            error_msg = "Failed to create credential manager dialog"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="CredentialManagerDialog", cause=e) from e

    @staticmethod
    def create_diagnostics_dialog(
        parent: tk.Widget,
        repositories: Optional[Dict[str, Any]] = None,
        services: Optional[Dict[str, Any]] = None
    ) -> DiagnosticsDialog:
        """
        Create a diagnostics dialog.

        Args:
            parent: The parent widget
            repositories: Dictionary of repository instances
            services: Dictionary of service instances

        Returns:
            A DiagnosticsDialog instance

        Raises:
            UIError: If the dialog cannot be created
        """
        try:
            return DiagnosticsDialog(
                parent=parent,
                repositories=repositories,
                services=services
            )
        except Exception as e:
            error_msg = "Failed to create diagnostics dialog"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="DiagnosticsDialog", cause=e) from e

    @staticmethod
    def create_conditional_action_editor_dialog(
        parent: tk.Widget,
        action_data: Optional[Dict[str, Any]] = None,
        workflow_presenter: Any = None
    ) -> ConditionalActionEditorDialog:
        """
        Create a conditional action editor dialog.

        Args:
            parent: The parent widget
            action_data: Initial action data (for editing an existing action)
            workflow_presenter: The workflow presenter for accessing actions

        Returns:
            A ConditionalActionEditorDialog instance

        Raises:
            UIError: If the dialog cannot be created
        """
        try:
            return ConditionalActionEditorDialog(
                parent=parent,
                action_data=action_data,
                workflow_presenter=workflow_presenter
            )
        except Exception as e:
            error_msg = "Failed to create conditional action editor dialog"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="ConditionalActionEditorDialog", cause=e) from e

    @staticmethod
    def create_loop_action_editor_dialog(
        parent: tk.Widget,
        action_data: Optional[Dict[str, Any]] = None,
        workflow_presenter: Any = None
    ) -> LoopActionEditorDialog:
        """
        Create a loop action editor dialog.

        Args:
            parent: The parent widget
            action_data: Initial action data (for editing an existing action)
            workflow_presenter: The workflow presenter for accessing actions

        Returns:
            A LoopActionEditorDialog instance

        Raises:
            UIError: If the dialog cannot be created
        """
        try:
            return LoopActionEditorDialog(
                parent=parent,
                action_data=action_data,
                workflow_presenter=workflow_presenter
            )
        except Exception as e:
            error_msg = "Failed to create loop action editor dialog"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="LoopActionEditorDialog", cause=e) from e

    @staticmethod
    def show_action_editor(
        parent: tk.Widget,
        action_data: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Show an action editor dialog and return the result.

        Args:
            parent: The parent widget
            action_data: Initial action data (for editing an existing action)
            title: Custom title for the dialog

        Returns:
            The action data if the user clicked OK, None if the user cancelled

        Raises:
            UIError: If the dialog cannot be created
        """
        try:
            # Check if this is a special action type
            if action_data and action_data.get("type") == "Conditional":
                dialog = DialogFactory.create_conditional_action_editor_dialog(
                    parent=parent,
                    action_data=action_data
                )
            elif action_data and action_data.get("type") == "Loop":
                dialog = DialogFactory.create_loop_action_editor_dialog(
                    parent=parent,
                    action_data=action_data
                )
            else:
                dialog = DialogFactory.create_action_editor_dialog(
                    parent=parent,
                    action_data=action_data,
                    title=title
                )
            return dialog.show()
        except Exception as e:
            error_msg = "Failed to show action editor dialog"
            logger.exception(error_msg)
            raise UIError(error_msg, component_name="ActionEditorDialog", cause=e) from e
