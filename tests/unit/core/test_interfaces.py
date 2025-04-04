import unittest
from unittest.mock import Mock, patch
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional

from src.core.interfaces import IWebDriver, IAction, IWorkflowRepository, ICredentialRepository


class TestIWebDriverInterface(unittest.TestCase):
    """
    Tests for the IWebDriver interface to ensure it defines all required methods
    for browser automation and that implementations can be properly substituted.
    """

    def test_interface_contract_completeness(self):
        """Test that IWebDriver interface defines all required methods."""
        # Verify all required methods are defined in the interface
        required_methods = [
            'get', 'quit', 'find_element', 'click_element', 'type_text',
            'take_screenshot', 'is_element_present', 'get_current_url'
        ]

        for method_name in required_methods:
            self.assertTrue(
                hasattr(IWebDriver, method_name) and callable(getattr(IWebDriver, method_name)),
                f"IWebDriver interface missing required method: {method_name}"
            )

    def test_interface_implementation_substitutability(self):
        """
        Test that a concrete implementation of IWebDriver can be used
        wherever the interface is expected (Liskov Substitution Principle).
        """
        # Create a minimal concrete implementation of IWebDriver for testing
        class ConcreteWebDriver(IWebDriver):
            def get(self, url: str) -> None:
                pass

            def quit(self) -> None:
                pass

            def find_element(self, selector: str) -> Any:
                return Mock()

            def click_element(self, selector: str) -> None:
                pass

            def type_text(self, selector: str, text: str) -> None:
                pass

            def take_screenshot(self, file_path: str) -> None:
                pass

            def is_element_present(self, selector: str) -> bool:
                return True

            def get_current_url(self) -> str:
                return "https://example.com"

        # Create an instance of the concrete implementation
        driver = ConcreteWebDriver()

        # Verify it can be used as an IWebDriver
        self.assertIsInstance(driver, IWebDriver)

        # Test that all methods can be called
        driver.get("https://example.com")
        element = driver.find_element("#test")
        driver.click_element("#button")
        driver.type_text("#input", "test text")
        driver.take_screenshot("test.png")
        self.assertTrue(driver.is_element_present("#exists"))
        self.assertEqual(driver.get_current_url(), "https://example.com")
        driver.quit()

    def test_interface_method_signatures(self):
        """Test that IWebDriver method signatures are correct."""
        # This test verifies that the method signatures match what we expect

        # get method should accept a URL string and return None
        self.assertEqual(IWebDriver.get.__annotations__['url'], str)
        self.assertEqual(IWebDriver.get.__annotations__['return'], None)

        # quit method should take no arguments and return None
        self.assertEqual(IWebDriver.quit.__annotations__['return'], None)

        # find_element should accept a selector string and return Any
        self.assertEqual(IWebDriver.find_element.__annotations__['selector'], str)
        self.assertEqual(IWebDriver.find_element.__annotations__['return'], Any)

        # click_element should accept a selector string and return None
        self.assertEqual(IWebDriver.click_element.__annotations__['selector'], str)
        self.assertEqual(IWebDriver.click_element.__annotations__['return'], None)

        # type_text should accept a selector string and text string and return None
        self.assertEqual(IWebDriver.type_text.__annotations__['selector'], str)
        self.assertEqual(IWebDriver.type_text.__annotations__['text'], str)
        self.assertEqual(IWebDriver.type_text.__annotations__['return'], None)

        # take_screenshot should accept a file_path string and return None
        self.assertEqual(IWebDriver.take_screenshot.__annotations__['file_path'], str)
        self.assertEqual(IWebDriver.take_screenshot.__annotations__['return'], None)

        # is_element_present should accept a selector string and return bool
        self.assertEqual(IWebDriver.is_element_present.__annotations__['selector'], str)
        self.assertEqual(IWebDriver.is_element_present.__annotations__['return'], bool)

        # get_current_url should take no arguments and return a string
        self.assertEqual(IWebDriver.get_current_url.__annotations__['return'], str)


class TestIActionInterface(unittest.TestCase):
    """
    Tests for the IAction interface to ensure it defines all required methods
    for action execution and that implementations can be properly substituted.
    """

    def test_interface_contract_completeness(self):
        """Test that IAction interface defines all required methods."""
        # Verify all required methods are defined in the interface
        required_methods = ['execute', 'to_dict']

        for method_name in required_methods:
            self.assertTrue(
                hasattr(IAction, method_name) and callable(getattr(IAction, method_name)),
                f"IAction interface missing required method: {method_name}"
            )

    def test_interface_implementation_substitutability(self):
        """
        Test that a concrete implementation of IAction can be used
        wherever the interface is expected (Liskov Substitution Principle).
        """
        # Create a minimal concrete implementation of IAction for testing
        class ConcreteAction(IAction):
            def execute(self, driver: IWebDriver) -> None:
                pass

            def to_dict(self) -> Dict[str, Any]:
                return {"type": "Test"}

        # Create an instance of the concrete implementation
        action = ConcreteAction()

        # Verify it can be used as an IAction
        self.assertIsInstance(action, IAction)

        # Test that all methods can be called
        mock_driver = Mock(spec=IWebDriver)
        action.execute(mock_driver)
        result = action.to_dict()
        self.assertEqual(result, {"type": "Test"})

    def test_interface_method_signatures(self):
        """Test that IAction method signatures are correct."""
        # This test verifies that the method signatures match what we expect

        # execute method should accept a driver and return Any
        self.assertEqual(IAction.execute.__annotations__['driver'], IWebDriver)
        self.assertEqual(IAction.execute.__annotations__['return'], Any)

        # to_dict method should return a Dict[str, Any]
        self.assertEqual(IAction.to_dict.__annotations__['return'], Dict[str, Any])


class TestIWorkflowRepositoryInterface(unittest.TestCase):
    """
    Tests for the IWorkflowRepository interface to ensure it defines all required methods
    for workflow storage and retrieval and that implementations can be properly substituted.
    """

    def test_interface_contract_completeness(self):
        """Test that IWorkflowRepository interface defines all required methods."""
        # Verify all required methods are defined in the interface
        required_methods = ['save', 'load', 'list_workflows']

        for method_name in required_methods:
            self.assertTrue(
                hasattr(IWorkflowRepository, method_name) and callable(getattr(IWorkflowRepository, method_name)),
                f"IWorkflowRepository interface missing required method: {method_name}"
            )

    def test_interface_implementation_substitutability(self):
        """
        Test that a concrete implementation of IWorkflowRepository can be used
        wherever the interface is expected (Liskov Substitution Principle).
        """
        # Create a minimal concrete implementation of IWorkflowRepository for testing
        class ConcreteWorkflowRepository(IWorkflowRepository):
            def save(self, name: str, workflow_actions: List[IAction]) -> None:
                pass

            def load(self, name: str) -> List[IAction]:
                return []

            def list_workflows(self) -> List[str]:
                return ["workflow1", "workflow2"]

        # Create an instance of the concrete implementation
        repo = ConcreteWorkflowRepository()

        # Verify it can be used as an IWorkflowRepository
        self.assertIsInstance(repo, IWorkflowRepository)

        # Test that all methods can be called
        mock_action = Mock(spec=IAction)
        repo.save("test_workflow", [mock_action])
        actions = repo.load("test_workflow")
        self.assertEqual(actions, [])
        workflows = repo.list_workflows()
        self.assertEqual(workflows, ["workflow1", "workflow2"])

    def test_interface_method_signatures(self):
        """Test that IWorkflowRepository method signatures are correct."""
        # This test verifies that the method signatures match what we expect

        # save method should accept a name and workflow_actions and return None
        self.assertEqual(IWorkflowRepository.save.__annotations__['name'], str)
        self.assertEqual(IWorkflowRepository.save.__annotations__['workflow_actions'], List[IAction])
        self.assertEqual(IWorkflowRepository.save.__annotations__['return'], None)

        # load method should accept a name and return List[IAction]
        self.assertEqual(IWorkflowRepository.load.__annotations__['name'], str)
        self.assertEqual(IWorkflowRepository.load.__annotations__['return'], List[IAction])

        # list_workflows method should return List[str]
        self.assertEqual(IWorkflowRepository.list_workflows.__annotations__['return'], List[str])


class TestICredentialRepositoryInterface(unittest.TestCase):
    """
    Tests for the ICredentialRepository interface to ensure it defines all required methods
    for credential storage and retrieval and that implementations can be properly substituted.
    """

    def test_interface_contract_completeness(self):
        """Test that ICredentialRepository interface defines all required methods."""
        # Verify all required methods are defined in the interface
        required_methods = ['get_all', 'get_by_name']

        for method_name in required_methods:
            self.assertTrue(
                hasattr(ICredentialRepository, method_name) and callable(getattr(ICredentialRepository, method_name)),
                f"ICredentialRepository interface missing required method: {method_name}"
            )

    def test_interface_implementation_substitutability(self):
        """
        Test that a concrete implementation of ICredentialRepository can be used
        wherever the interface is expected (Liskov Substitution Principle).
        """
        # Create a minimal concrete implementation of ICredentialRepository for testing
        class ConcreteCredentialRepository(ICredentialRepository):
            def get_all(self) -> List[Dict[str, str]]:
                return [{"name": "test", "username": "user", "password": "pass"}]

            def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
                if name == "test":
                    return {"name": "test", "username": "user", "password": "pass"}
                return None

        # Create an instance of the concrete implementation
        repo = ConcreteCredentialRepository()

        # Verify it can be used as an ICredentialRepository
        self.assertIsInstance(repo, ICredentialRepository)

        # Test that all methods can be called
        credentials = repo.get_all()
        self.assertEqual(credentials, [{"name": "test", "username": "user", "password": "pass"}])

        credential = repo.get_by_name("test")
        self.assertEqual(credential, {"name": "test", "username": "user", "password": "pass"})

        non_existent = repo.get_by_name("non_existent")
        self.assertIsNone(non_existent)

    def test_interface_method_signatures(self):
        """Test that ICredentialRepository method signatures are correct."""
        # This test verifies that the method signatures match what we expect

        # get_all method should return List[Dict[str, str]]
        self.assertEqual(ICredentialRepository.get_all.__annotations__['return'], List[Dict[str, str]])

        # get_by_name method should accept a name and return Optional[Dict[str, str]]
        self.assertEqual(ICredentialRepository.get_by_name.__annotations__['name'], str)
        self.assertEqual(ICredentialRepository.get_by_name.__annotations__['return'], Optional[Dict[str, str]])


if __name__ == '__main__':
    unittest.main()
