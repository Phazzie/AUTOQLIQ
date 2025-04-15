"""Workflow completion logger for workflow execution.

This module provides the WorkflowCompletionLogger class for logging workflow completion status.
"""

import logging
from typing import Optional

from src.core.workflow.result_processing.interfaces import IWorkflowCompletionLogger

logger = logging.getLogger(__name__)


class WorkflowCompletionLogger(IWorkflowCompletionLogger):
    """
    Logs workflow completion status.

    Responsible for logging the final status of workflow execution.
    """

    def log_workflow_completion(self,
                              workflow_name: str,
                              final_status: str,
                              error_message: Optional[str]) -> None:
        """
        Log the workflow completion status.

        Args:
            workflow_name: Name of the workflow
            final_status: Final status of the workflow
            error_message: Optional error message
        """
        logger.info(f"Workflow '{workflow_name}' completed with status: {final_status}")
        if error_message:
            logger.error(f"Workflow error: {error_message}")
