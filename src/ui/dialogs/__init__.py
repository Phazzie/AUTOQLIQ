"""UI Dialogs package for AutoQliq.

This package contains custom Toplevel dialog windows used by the application.
"""

from .action_editor_dialog import ActionEditorDialog
from .credential_manager_dialog import CredentialManagerDialog

__all__ = [
    "ActionEditorDialog",
    "CredentialManagerDialog",
]