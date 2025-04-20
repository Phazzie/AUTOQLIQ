"""Default workflow loader for AutoQliq.

This module provides functionality to load the default workflow when the application starts.
It checks if the default workflow exists and creates it if it doesn't.
"""

import os
import json
import logging
from typing import Dict, Any, List

from src.core.interfaces import IWorkflowRepository
from src.core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

DEFAULT_WORKFLOW_NAME = "default_workflow"
DEFAULT_WORKFLOW_PATH = "workflows/default_workflow.json"


def ensure_default_workflow_exists(workflow_repo: IWorkflowRepository) -> None:
    """
    Ensure that the default workflow exists in the repository.
    If it doesn't exist, create it from the template file.

    Args:
        workflow_repo: The workflow repository
    """
    logger.info("Checking for default workflow...")

    try:
        # Check if the default workflow exists in the repository
        workflow_list = workflow_repo.list_workflows()
        if DEFAULT_WORKFLOW_NAME in workflow_list:
            logger.info(f"Default workflow '{DEFAULT_WORKFLOW_NAME}' already exists.")
            return

        # If not, check if the template file exists
        if not os.path.exists(DEFAULT_WORKFLOW_PATH):
            logger.warning(f"Default workflow template file not found at '{DEFAULT_WORKFLOW_PATH}'.")
            create_basic_default_workflow(workflow_repo)
            return

        # Load the template file
        logger.info(f"Loading default workflow template from '{DEFAULT_WORKFLOW_PATH}'...")
        try:
            with open(DEFAULT_WORKFLOW_PATH, 'r') as f:
                workflow_data = json.load(f)

            # Save the workflow to the repository
            logger.info(f"Creating default workflow '{DEFAULT_WORKFLOW_NAME}'...")
            workflow_repo.create_workflow(DEFAULT_WORKFLOW_NAME)

            # The repository expects action objects, not raw dictionaries
            # For file system repositories, we can pass the raw data and it will be handled
            try:
                from src.infrastructure.repositories.serialization.action_serializer import deserialize_actions
                action_objects = deserialize_actions(workflow_data)
                workflow_repo.save(DEFAULT_WORKFLOW_NAME, action_objects)
            except ImportError:
                # Fall back to direct save if we can't import the deserializer
                workflow_repo.save(DEFAULT_WORKFLOW_NAME, workflow_data)

            logger.info(f"Default workflow '{DEFAULT_WORKFLOW_NAME}' created successfully.")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading default workflow template: {e}")
            create_basic_default_workflow(workflow_repo)
    except Exception as e:
        logger.error(f"Error ensuring default workflow exists: {e}")


def create_basic_default_workflow(workflow_repo: IWorkflowRepository) -> None:
    """
    Create a basic default workflow if the template file is not available.

    Args:
        workflow_repo: The workflow repository
    """
    logger.info("Creating basic default workflow...")

    try:
        # Create a basic default workflow
        basic_workflow = [
            {
                "type": "Navigate",
                "name": "Navigate to website",
                "url": "https://example.com"
            },
            {
                "type": "Wait",
                "name": "Wait for page to load",
                "duration_seconds": 2
            },
            {
                "type": "Screenshot",
                "name": "Take screenshot",
                "file_path": "screenshots/example.png"
            }
        ]

        # Save the workflow to the repository
        workflow_repo.create_workflow(DEFAULT_WORKFLOW_NAME)

        # The repository expects action objects, not raw dictionaries
        # For file system repositories, we can pass the raw data and it will be handled
        try:
            from src.infrastructure.repositories.serialization.action_serializer import deserialize_actions
            action_objects = deserialize_actions(basic_workflow)
            workflow_repo.save(DEFAULT_WORKFLOW_NAME, action_objects)
        except ImportError:
            # Fall back to direct save if we can't import the deserializer
            workflow_repo.save(DEFAULT_WORKFLOW_NAME, basic_workflow)

        logger.info(f"Basic default workflow '{DEFAULT_WORKFLOW_NAME}' created successfully.")
    except Exception as e:
        logger.error(f"Error creating basic default workflow: {e}")
