import abc
from typing import Any, List, Dict, Optional

from src.core.action_result import ActionResult

class IWebDriver(abc.ABC):
    @abc.abstractmethod
    def get(self, url: str) -> None: pass
    @abc.abstractmethod
    def quit(self) -> None: pass
    @abc.abstractmethod
    def find_element(self, selector: str) -> Any: pass
    @abc.abstractmethod
    def click_element(self, selector: str) -> None: pass
    @abc.abstractmethod
    def type_text(self, selector: str, text: str) -> None: pass
    @abc.abstractmethod
    def take_screenshot(self, file_path: str) -> None: pass
    @abc.abstractmethod
    def is_element_present(self, selector: str) -> bool: pass
    @abc.abstractmethod
    def get_current_url(self) -> str: pass

class IAction(abc.ABC):
    @abc.abstractmethod
    def execute(self, driver: IWebDriver) -> ActionResult: pass
    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]: pass

class ICredentialRepository(abc.ABC):
    @abc.abstractmethod
    def get_all(self) -> List[Dict[str, str]]: pass
    @abc.abstractmethod
    def get_by_name(self, name: str) -> Optional[Dict[str, str]]: pass

class IWorkflowRepository(abc.ABC):
    @abc.abstractmethod
    def save(self, name: str, workflow_actions: List[IAction]) -> None: pass
    @abc.abstractmethod
    def load(self, name: str) -> List[IAction]: pass
    @abc.abstractmethod
    def list_workflows(self) -> List[str]: pass
