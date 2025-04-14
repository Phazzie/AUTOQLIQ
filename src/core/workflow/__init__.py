"""Workflow package initialization for AutoQliq.

This package contains components related to workflow definition,
execution, and management.

Exports:
    WorkflowRunner: Class responsible for executing a sequence of actions.
    Workflow: Core entity representing a sequence of actions.
    RefactoredWorkflowRunner: Refactored version of WorkflowRunner with improved modularity.
"""

# For backward compatibility, import the original WorkflowRunner
from .runner import WorkflowRunner, ErrorHandlingStrategy
from .workflow_entity import Workflow

# Import the refactored components
from .runner_refactored import WorkflowRunner as RefactoredWorkflowRunner
from .backward_compatibility import WorkflowRunner as CompatibleWorkflowRunner

# Import specialized components
from .action_executor import ActionExecutor
from .context.manager import WorkflowContextManager
from .result_processing.processor import ResultProcessor

__all__ = [
    # Original components
    "WorkflowRunner",
    "Workflow",
    "ErrorHandlingStrategy",

    # Refactored components
    "RefactoredWorkflowRunner",
    "CompatibleWorkflowRunner",
    "ActionExecutor",
    "WorkflowContextManager",
    "ResultProcessor",
]
