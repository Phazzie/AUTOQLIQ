from abc import ABC, abstractmethod
from typing import Dict, Any

from src.core.interfaces import IAction, IWebDriver
from src.core.action_result import ActionResult


class ActionBase(IAction, ABC):
    """
    Base class for all actions in the system.

    This abstract class provides common functionality for all actions
    and ensures they implement the IAction interface.

    Attributes:
        name: A descriptive name for the action
    """

    def __init__(self, name: str):
        """
        Initialize an ActionBase.

        Args:
            name: A descriptive name for the action
        """
        self.name = name

    def validate(self) -> bool:
        """
        Validate that the action is properly configured.

        This method can be overridden by subclasses to provide
        specific validation logic.

        Returns:
            True if the action is valid, False otherwise
        """
        return True

    @abstractmethod
    def execute(self, driver: IWebDriver) -> ActionResult:
        """
        Execute the action using the provided web driver.

        Args:
            driver: The web driver to use for execution

        Returns:
            An ActionResult indicating success or failure
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the action to a dictionary representation.

        Returns:
            A dictionary containing the action's data
        """
        pass
