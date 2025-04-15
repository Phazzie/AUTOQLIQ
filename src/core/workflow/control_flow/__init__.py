"""Control flow package for AutoQliq workflows.

This package provides control flow handlers for the WorkflowRunner.
"""

# Interfaces
from src.core.workflow.control_flow.interfaces import (
    IControlFlowHandler,
    IConditionalActionHandler,
    ILoopActionHandler,
    IErrorHandlingActionHandler,
    ITemplateActionHandler
)

# Implementations
from src.core.workflow.control_flow.base import ControlFlowHandlerBase
from src.core.workflow.control_flow.conditional_handler import ConditionalHandler
from src.core.workflow.control_flow.loop_handler import LoopHandler
from src.core.workflow.control_flow.error_handler import ErrorHandlingHandler
from src.core.workflow.control_flow.template.handler import TemplateHandler

__all__ = [
    # Interfaces
    'IControlFlowHandler',
    'IConditionalActionHandler',
    'ILoopActionHandler',
    'IErrorHandlingActionHandler',
    'ITemplateActionHandler',

    # Implementations
    'ControlFlowHandlerBase',
    'ConditionalHandler',
    'LoopHandler',
    'ErrorHandlingHandler',
    'TemplateHandler',
]
