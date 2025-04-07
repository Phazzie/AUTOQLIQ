"""Reporting service implementation for AutoQliq using simple file storage."""

import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Core interfaces
from src.core.interfaces.service import IReportingService
from src.core.exceptions import AutoQliqError, RepositoryError # Use RepositoryError for file issues

# Common utilities
from src.infrastructure.common.logging_utils import log_method_call
# Configuration needed for log path? Or hardcode? Let's hardcode 'logs/' for now.
# from src.config import config

logger = logging.getLogger(__name__)
LOG_DIRECTORY = "logs" # Directory to store execution logs

class ReportingService(IReportingService):
    """
    Basic implementation of IReportingService using simple JSON file storage.

    Stores each workflow execution log as a separate JSON file in the LOG_DIRECTORY.
    Provides methods for saving logs and basic retrieval (listing, getting details).
    """

    def __init__(self):
        """Initialize the ReportingService."""
        logger.info("ReportingService initialized.")
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Create the log directory if it doesn't exist."""
        try:
            os.makedirs(LOG_DIRECTORY, exist_ok=True)
            logger.debug(f"Ensured log directory exists: {LOG_DIRECTORY}")
        except OSError as e:
             logger.error(f"Failed to create log directory '{LOG_DIRECTORY}': {e}", exc_info=True)
             # Allow service to continue, but saving logs will fail

    def _generate_filename(self, execution_log: Dict[str, Any]) -> str:
         """Generates a unique filename based on log content."""
         try:
             start_dt = datetime.fromisoformat(execution_log['start_time_iso'])
             ts_str = start_dt.strftime("%Y%m%d_%H%M%S")
         except (ValueError, KeyError):
             ts_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f") # Fallback timestamp
         safe_wf_name = "".join(c if c.isalnum() else "_" for c in execution_log.get('workflow_name', 'UnknownWF'))
         status = execution_log.get('final_status', 'UNKNOWN')
         # Use start time for uniqueness, status for easier browsing
         return f"exec_{safe_wf_name}_{ts_str}_{status}.json"

    # --- Methods required by IReportingService ---

    def log_execution_start(self, workflow_name: str) -> str:
        """Generates and returns a unique ID (filename format) for a new execution."""
        # This ID isn't strictly used by save_execution_log which generates its own filename,
        # but could be useful if intermediate logging were implemented.
        execution_id = self._generate_filename({
             'workflow_name': workflow_name,
             'start_time_iso': datetime.now().isoformat(),
             'final_status': 'RUNNING' # Potential status for initial log
        })
        logger.info(f"Generated potential Execution ID for '{workflow_name}': {execution_id}")
        return execution_id

    def log_action_result(self, execution_id: str, action_index: int, action_name: str, result: Dict[str, Any]) -> None:
        """Currently NO-OP. Full log saved at end."""
        logger.debug(f"Placeholder: Log action result for ExecID '{execution_id}'. Not saving individually.")
        pass

    def log_execution_end(self, execution_id: str, final_status: str, duration: float, error_message: Optional[str] = None) -> None:
        """Currently NO-OP. Full log saved via save_execution_log."""
        logger.debug(f"Placeholder: Log execution end for ExecID '{execution_id}'. Status: {final_status}. Not saving individually.")
        pass

    @log_method_call(logger)
    def save_execution_log(self, execution_log: Dict[str, Any]) -> None:
        """Saves the full execution log data to a unique JSON file."""
        if not isinstance(execution_log, dict) or not execution_log.get('workflow_name') or not execution_log.get('start_time_iso'):
            logger.error("Attempted to save invalid execution log data (missing required keys).")
            raise ValueError("Invalid execution log data provided.") # Raise error

        try:
            filename = self._generate_filename(execution_log)
            filepath = os.path.join(LOG_DIRECTORY, filename)

            logger.info(f"Saving execution log to: {filepath}")
            try:
                self._ensure_log_directory() # Ensure dir exists just before write
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(execution_log, f, indent=2)
                logger.debug(f"Successfully saved execution log: {filename}")
            except (IOError, TypeError, PermissionError) as e:
                 logger.error(f"Failed to write execution log file '{filepath}': {e}", exc_info=True)
                 raise RepositoryError(f"Failed to write execution log '{filepath}'", cause=e) from e

        except Exception as e:
             logger.error(f"Error processing execution log for saving: {e}", exc_info=True)
             # Wrap unexpected errors
             raise AutoQliqError(f"Failed to process execution log: {e}", cause=e) from e


    @log_method_call(logger)
    def generate_summary_report(self, since: Optional[Any] = None) -> Dict[str, Any]:
        """Generate a summary report by reading log files."""
        logger.info(f"Generating summary report (since: {since}). Reading logs from '{LOG_DIRECTORY}'.")
        # TODO: Implement reading and aggregation logic
        logger.warning("Placeholder: Generate summary report called. Aggregation logic not implemented.")
        return { "message": "Reporting aggregation logic not implemented." }

    @log_method_call(logger)
    def get_execution_details(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed results by reading the corresponding log file."""
        # Assume execution_id is the filename for this implementation
        filename = execution_id
        filepath = os.path.join(LOG_DIRECTORY, filename)
        logger.info(f"Attempting to load execution details from: {filepath}")

        if not filename.startswith("exec_") or not filename.endswith(".json"):
             logger.error(f"Invalid execution ID format provided: {execution_id}")
             raise ValueError(f"Invalid execution ID format: {execution_id}")

        try:
            if not os.path.exists(filepath) or not os.path.isfile(filepath):
                logger.warning(f"Execution log file not found: {filepath}")
                return None # Return None if file doesn't exist

            with open(filepath, 'r', encoding='utf-8') as f:
                log_data = json.load(f) # Raises JSONDecodeError
            logger.debug(f"Successfully loaded execution details for ID: {execution_id}")
            return log_data
        except json.JSONDecodeError as e:
             logger.error(f"Invalid JSON in execution log file '{filepath}': {e}")
             raise RepositoryError(f"Failed to parse execution log '{filename}'", cause=e) from e
        except (IOError, PermissionError, OSError) as e:
             logger.error(f"Error reading execution log file '{filepath}': {e}")
             raise RepositoryError(f"Failed to read execution log '{filename}'", cause=e) from e
        except Exception as e:
             logger.exception(f"Unexpected error getting execution details for '{execution_id}'")
             raise AutoQliqError(f"Unexpected error retrieving execution log '{filename}'", cause=e) from e


    @log_method_call(logger)
    def list_past_executions(self, workflow_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List past workflow execution summaries from log files."""
        logger.info(f"Listing past executions (Workflow: {workflow_name}, Limit: {limit}).")
        summaries = []
        try:
            if not os.path.exists(LOG_DIRECTORY) or not os.path.isdir(LOG_DIRECTORY):
                 logger.warning(f"Log directory not found: {LOG_DIRECTORY}")
                 return []

            log_files = [f for f in os.listdir(LOG_DIRECTORY) if f.startswith("exec_") and f.endswith(".json")]

            # Filter by workflow name if provided
            if workflow_name:
                 safe_filter_name = "".join(c if c.isalnum() else "_" for c in workflow_name)
                 log_files = [f for f in log_files if f.startswith(f"exec_{safe_filter_name}_")]

            # Sort by timestamp in filename (descending - newest first)
            # Assumes filename format exec_NAME_YYYYMMDD_HHMMSS_STATUS.json
            log_files.sort(reverse=True)

            # Limit results
            log_files = log_files[:limit]

            # Read summary info from each file
            for filename in log_files:
                filepath = os.path.join(LOG_DIRECTORY, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        log_data = json.load(f)
                    # Extract summary fields, providing defaults
                    summary = {
                        "execution_id": filename, # Use filename as ID
                        "workflow_name": log_data.get("workflow_name", "Unknown"),
                        "start_time_iso": log_data.get("start_time_iso"),
                        "duration_seconds": log_data.get("duration_seconds"),
                        "final_status": log_data.get("final_status", "UNKNOWN"),
                    }
                    summaries.append(summary)
                except Exception as e:
                     logger.error(f"Failed to read or parse summary from log file '{filename}': {e}")
                     # Skip this file on error, maybe add a placeholder summary?
                     summaries.append({
                          "execution_id": filename, "workflow_name": "Error",
                          "start_time_iso": None, "duration_seconds": None, "final_status": "PARSE_ERROR"
                     })


            logger.debug(f"Found {len(summaries)} execution summaries.")
            return summaries

        except Exception as e:
             logger.error(f"Error listing past executions: {e}", exc_info=True)
             raise RepositoryError(f"Failed to list execution logs: {e}", cause=e) from e