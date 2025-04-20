from abc import ABC, abstractmethod
from typing import Dict, Any

from src.core.action_result import ActionResult

class IAction(ABC):
    """Contract for all actions in the AutoQliq system."""

    @abstractmethod
    def validate(self) -> bool:
        """Ensure action configuration is valid."""
        pass

    @abstractmethod
    def execute(self, driver: 'IWebDriver') -> ActionResult:
        """Perform the action using the provided web driver."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action's parameters for persistence or logging."""
        pass