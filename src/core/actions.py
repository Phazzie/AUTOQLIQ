from typing import Dict, Any, Optional, ClassVar
from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.action_base import ActionBase
from src.core.action_result import ActionResult
from src.core.exceptions import CredentialError
import time
import json

class NavigateAction(ActionBase):
    def __init__(self, url: str, name: str = "Navigate"):
        super().__init__(name)
        self.url = url

    def validate(self) -> bool:
        return bool(self.url)

    def execute(self, driver: IWebDriver) -> ActionResult:
        try:
            driver.get(self.url)
            return ActionResult.success(f"Navigated to {self.url}")
        except Exception as e:
            return ActionResult.failure(f"Failed to navigate to {self.url}: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Navigate", "name": self.name, "url": self.url}

class ClickAction(ActionBase):
    def __init__(self, selector: str, name: str = "Click", check_success_selector: Optional[str] = None, check_failure_selector: Optional[str] = None):
        super().__init__(name)
        self.selector = selector
        self.check_success_selector = check_success_selector
        self.check_failure_selector = check_failure_selector

    def validate(self) -> bool:
        return bool(self.selector)

    def execute(self, driver: IWebDriver) -> ActionResult:
        try:
            driver.click_element(self.selector)

            # Check for success/failure indicators if specified
            if self.check_success_selector and not driver.is_element_present(self.check_success_selector):
                if self.check_failure_selector and driver.is_element_present(self.check_failure_selector):
                    return ActionResult.failure("Login failed due to presence of failure element.")
                return ActionResult.failure("Login failed due to absence of success element.")

            return ActionResult.success(f"Clicked element {self.selector}")
        except Exception as e:
            return ActionResult.failure(f"Failed to click element {self.selector}: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Click",
            "name": self.name,
            "selector": self.selector,
            "check_success_selector": self.check_success_selector,
            "check_failure_selector": self.check_failure_selector,
        }

class TypeAction(ActionBase):
    # Class variable to store credential repository
    _credential_repository: ClassVar[Optional[ICredentialRepository]] = None

    @classmethod
    def set_credential_repository(cls, repository: ICredentialRepository) -> None:
        """Set the credential repository for all TypeAction instances."""
        cls._credential_repository = repository

    def __init__(self, selector: str, value_type: str, value_key: str, name: str = "Type"):
        super().__init__(name)
        self.selector = selector
        self.value_type = value_type
        self.value_key = value_key

    def validate(self) -> bool:
        return bool(self.selector) and bool(self.value_type) and bool(self.value_key)

    def execute(self, driver: IWebDriver) -> ActionResult:
        try:
            value = self._get_value()
            driver.type_text(self.selector, value)
            return ActionResult.success(f"Typed text into element {self.selector}")
        except ValueError as e:
            return ActionResult.failure(str(e))
        except CredentialError as e:
            return ActionResult.failure(str(e))
        except Exception as e:
            return ActionResult.failure(f"Failed to type text into element {self.selector}: {str(e)}")

    def _get_value(self) -> str:
        if self.value_type == "credential":
            # Check if credential repository is set
            if not self._credential_repository:
                raise CredentialError("Credential repository not set. Call TypeAction.set_credential_repository() first.")

            # Parse credential key (format: "credential_name.field")
            parts = self.value_key.split(".")
            if len(parts) != 2:
                raise CredentialError(f"Invalid credential key format: {self.value_key}. Expected format: 'credential_name.field'")

            credential_name, field = parts

            # Get credential from repository
            credential = self._credential_repository.get_by_name(credential_name)
            if not credential:
                raise CredentialError(f"Credential not found: {credential_name}", credential_name=credential_name)

            # Get field from credential
            if field not in credential:
                raise CredentialError(f"Field '{field}' not found in credential '{credential_name}'", credential_name=credential_name)

            return credential[field]
        elif self.value_type == "text":
            return self.value_key
        raise ValueError(f"Unsupported value type: {self.value_type}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Type",
            "name": self.name,
            "selector": self.selector,
            "value_type": self.value_type,
            "value_key": self.value_key,
        }

class WaitAction(ActionBase):
    def __init__(self, duration_seconds: int, name: str = "Wait"):
        super().__init__(name)
        self.duration_seconds = duration_seconds

    def validate(self) -> bool:
        return self.duration_seconds > 0

    def execute(self, driver: IWebDriver) -> ActionResult:
        try:
            time.sleep(self.duration_seconds)
            return ActionResult.success(f"Waited for {self.duration_seconds} seconds")
        except Exception as e:
            return ActionResult.failure(f"Failed to wait: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Wait", "name": self.name, "duration_seconds": self.duration_seconds}

class ScreenshotAction(ActionBase):
    def __init__(self, file_path: str, name: str = "Screenshot"):
        super().__init__(name)
        self.file_path = file_path

    def validate(self) -> bool:
        return bool(self.file_path)

    def execute(self, driver: IWebDriver) -> ActionResult:
        try:
            driver.take_screenshot(self.file_path)
            return ActionResult.success(f"Took screenshot and saved to {self.file_path}")
        except Exception as e:
            return ActionResult.failure(f"Failed to take screenshot: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Screenshot", "name": self.name, "file_path": self.file_path}

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
