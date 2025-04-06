"""Workflow entity module for AutoQliq.

This module provides the Workflow entity class for browser automation.
"""

import json
from typing import List, Dict, Any, Optional

from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult
from src.core.actions import ActionFactory, TypeAction


class Workflow:
    """
    Represents a workflow consisting of a sequence of actions.

    A workflow has a name and a list of actions that can be executed
    in sequence using a web driver.

    Attributes:
        name: A unique identifier for this workflow
        actions: A list of actions to be executed in sequence
    """

    def __init__(self, name: str, actions: List[IAction]):
        """
        Initialize a Workflow.

        Args:
            name: A unique identifier for this workflow
            actions: A list of actions to be executed in sequence

        Raises:
            ValueError: If the name is empty
        """
        if not name:
            raise ValueError("Workflow name cannot be empty")

        self.name = name
        self.actions = actions.copy()  # Create a copy to avoid modifying the original list

    def add_action(self, action: IAction) -> None:
        """
        Add an action to the workflow.

        Args:
            action: The action to add
        """
        self.actions.append(action)

    def remove_action(self, index: int) -> None:
        """
        Remove an action from the workflow.

        Args:
            index: The index of the action to remove

        Raises:
            IndexError: If the index is out of range
        """
        if index < 0 or index >= len(self.actions):
            raise IndexError(f"Action index {index} out of range")

        self.actions.pop(index)

    def execute(self, driver: IWebDriver, credential_repository: Optional[ICredentialRepository] = None) -> List[ActionResult]:
        """
        Execute all actions in the workflow.

        Args:
            driver: The web driver to use for execution
            credential_repository: Optional credential repository for TypeAction

        Returns:
            A list of ActionResult objects, one for each action executed
        """
        results = []

        for action in self.actions:
            # Pass credential repository to execute if it's a TypeAction
            if isinstance(action, TypeAction) and credential_repository:
                result = action.execute(driver, credential_repository)
            else:
                result = action.execute(driver)
            results.append(result)

            # Stop execution if an action fails
            if not result.is_success():
                break

        return results

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the workflow to a dictionary representation.

        Returns:
            A dictionary containing the workflow's data
        """
        return {
            "name": self.name,
            "actions": [action.to_dict() for action in self.actions]
        }

    def to_json(self) -> str:
        """
        Convert the workflow to a JSON string.

        Returns:
            A JSON string representing the workflow
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        """
        Create a Workflow from a dictionary.

        Args:
            data: A dictionary containing workflow data

        Returns:
            A new Workflow instance
        """
        name = data.get("name", "")
        action_dicts = data.get("actions", [])

        actions = [ActionFactory.create_action(action_dict) for action_dict in action_dicts]

        return cls(name=name, actions=actions)

    @classmethod
    def from_json(cls, json_str: str) -> 'Workflow':
        """
        Create a Workflow from a JSON string.

        Args:
            json_str: A JSON string representing a workflow

        Returns:
            A new Workflow instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """
        Get a string representation of the workflow.

        Returns:
            A string representation of the workflow
        """
        return f"Workflow(name='{self.name}', actions={len(self.actions)})"
