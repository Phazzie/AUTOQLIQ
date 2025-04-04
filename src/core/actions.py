from typing import Dict, Any
from src.core.interfaces import IAction, IWebDriver
from src.core.exceptions import LoginFailedError
from src.core.credentials import Credential
import time
import json

class NavigateAction(IAction):
    def __init__(self, url: str):
        self.url = url

    def execute(self, driver: IWebDriver) -> None:
        driver.get(self.url)

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Navigate", "url": self.url}

class ClickAction(IAction):
    def __init__(self, selector: str, check_success_selector: str = None, check_failure_selector: str = None):
        self.selector = selector
        self.check_success_selector = check_success_selector
        self.check_failure_selector = check_failure_selector

    def execute(self, driver: IWebDriver) -> None:
        driver.click_element(self.selector)
        if self.check_success_selector and not driver.is_element_present(self.check_success_selector):
            if self.check_failure_selector and driver.is_element_present(self.check_failure_selector):
                raise LoginFailedError("Login failed due to presence of failure element.")
            raise LoginFailedError("Login failed due to absence of success element.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Click",
            "selector": self.selector,
            "check_success_selector": self.check_success_selector,
            "check_failure_selector": self.check_failure_selector,
        }

class TypeAction(IAction):
    def __init__(self, selector: str, value_type: str, value_key: str):
        self.selector = selector
        self.value_type = value_type
        self.value_key = value_key

    def execute(self, driver: IWebDriver) -> None:
        value = self._get_value()
        driver.type_text(self.selector, value)

    def _get_value(self) -> str:
        if self.value_type == "credential":
            with open("credentials.json", "r") as file:
                credentials = json.load(file)
                for credential in credentials:
                    if credential["name"] == self.value_key.split(".")[0]:
                        return credential[self.value_key.split(".")[1]]
        raise ValueError("Unsupported value type or key not found.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Type",
            "selector": self.selector,
            "value_type": self.value_type,
            "value_key": self.value_key,
        }

class WaitAction(IAction):
    def __init__(self, duration_seconds: int):
        self.duration_seconds = duration_seconds

    def execute(self, driver: IWebDriver) -> None:
        time.sleep(self.duration_seconds)

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Wait", "duration_seconds": self.duration_seconds}

class ScreenshotAction(IAction):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def execute(self, driver: IWebDriver) -> None:
        driver.take_screenshot(self.file_path)

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Screenshot", "file_path": self.file_path}

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
