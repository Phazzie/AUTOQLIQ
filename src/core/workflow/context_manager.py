"""Context manager for workflow execution.

This module provides a facade for the context management components.
"""

import logging
from typing import Dict, Any

from src.core.workflow.context import WorkflowContextManager

logger = logging.getLogger(__name__)

# For backward compatibility, re-export the WorkflowContextManager as ContextManager
ContextManager = WorkflowContextManager
