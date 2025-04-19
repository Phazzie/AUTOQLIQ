"""Workflow execution module for AutoQliq.

Provides execution functionality for the WorkflowRunner.
"""

import logging
import time
from typing import List, Dict, Any, Optional
import threading

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError
from src.core.workflow.error_handling.strategy_enum import ErrorHandlingStrategy
from src.core.workflow.stop_event_checker import check_stop_event

logger = logging.getLogger(__name__)


def execute_workflow(
    runner,
    actions: List[IAction],
    workflow_name: str,
    context_manager,
    result_processor,
    error_strategy_enum: ErrorHandlingStrategy,
    stop_event: Optional[threading.Event] = None
) -> Dict[str, Any]:
    """
    Execute a workflow.

    Args:
        runner: The WorkflowRunner instance
        actions: List of actions to execute
        workflow_name: Name of the workflow
        context_manager: Context manager
        result_processor: Result processor
        error_strategy_enum: Error handling strategy enum
        stop_event: Optional event to signal graceful stop request

    Returns:
        Dict[str, Any]: Execution log
    """
    if not isinstance(actions, list):
        raise TypeError("Actions must be list.")
    if not workflow_name:
        workflow_name = "Unnamed Workflow"

    # Create execution context
    context = context_manager.create_context()

    # Initialize tracking variables
    start_time = time.time()
    all_action_results = []
    error = None

    logger.info(f"RUNNER: Starting workflow '{workflow_name}' with {len(actions)} top-level actions.")

    try:
        # Check stop event before starting
        check_stop_event(stop_event)

        # Execute actions
        all_action_results = runner._execute_actions(actions, context, workflow_name)

    except Exception as e:
        # Store error for result processing
        error = e

    # Process results
    execution_log = result_processor.create_execution_log(
        workflow_name=workflow_name,
        action_results=all_action_results,
        start_time=start_time,
        error=error,
        error_strategy_name=error_strategy_enum.name
    )

    return execution_log
