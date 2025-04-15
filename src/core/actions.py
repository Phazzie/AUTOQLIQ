from typing import Dict, Any, Optional
from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.action_base import ActionBase
from src.core.action_result import ActionResult
from src.core.exceptions import CredentialError, ActionError, WebDriverError
import time
# Remove unused import

class ActionFactory:
    _registry = {
        "Navigate": NavigateAction,
        "Click": ClickAction,
        "Type": TypeAction,
        "Wait": WaitAction,
        "Screenshot": ScreenshotAction,
    }

    @classmethod
    def create_action(cls, action_data: Dict[str, Any]) -> IAction:
        action_type = action_data["type"]
        action_class = cls._registry.get(action_type)
        if not action_class:
            raise ValueError(f"Unsupported action type: {action_type}")
        return action_class(**{k: v for k, v in action_data.items() if k != "type"})
