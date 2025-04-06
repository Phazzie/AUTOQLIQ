"""Core interfaces consolidation for AutoQliq."""

# This file serves as a central point for importing core interfaces.
# Individual interface definitions are in the src.core.interfaces package.
# This helps maintain backward compatibility if older code imports from here.

import warnings

# Ensure action_result is available directly if needed
from src.core.action_result import ActionResult
# Import specific interfaces from their modules
from src.core.interfaces.action import IAction
from src.core.interfaces.repository import IWorkflowRepository, ICredentialRepository
from src.core.interfaces.webdriver import IWebDriver


__all__ = [
    "IAction",
    "IWorkflowRepository",
    "ICredentialRepository",
    "IWebDriver",
    "ActionResult" # Export ActionResult as well
]

warnings.warn(
    "Importing interfaces directly from src.core.interfaces is deprecated. "
    "Please import from the specific modules within the src.core.interfaces package (e.g., src.core.interfaces.action).",
    DeprecationWarning,
    stacklevel=2
)