import unittest
from typing import Any, List, Dict, Optional

from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.workflow_entity import Workflow
from src.core.credentials import Credential
from src.core.actions import (
    NavigateAction,
    ClickAction,
    TypeAction,
    WaitAction,
    ScreenshotAction,
    ActionFactory
)


class MockCredentialRepository(ICredentialRepository):
    """Mock implementation of ICredentialRepository for testing."""

    def __init__(self):
        self.credentials = [
            {"name": "test_login", "username": "user@example.com", "password": "password123"}
        ]

    def get_all(self) -> List[Dict[str, str]]:
        return self.credentials

    def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
        for credential in self.credentials:
            if credential["name"] == name:
                return credential
        return None


class MockWebDriver(IWebDriver):
    """Mock implementation of IWebDriver for testing."""

    def __init__(self):
        self.navigation_history = []
        self.clicked_elements = []
        self.typed_text = {}
        self.screenshots = []
        self.elements_present = {"#login-button", "#username", "#password", "#dashboard"}

    def get(self, url: str) -> None:
        self.navigation_history.append(url)

    def quit(self) -> None:
        pass

    def find_element(self, selector: str) -> Any:
        if selector in self.elements_present:
            return {"selector": selector}
        return None

    def click_element(self, selector: str) -> None:
        self.clicked_elements.append(selector)

    def type_text(self, selector: str, text: str) -> None:
        self.typed_text[selector] = text

    def take_screenshot(self, file_path: str) -> None:
        self.screenshots.append(file_path)

    def is_element_present(self, selector: str) -> bool:
        return selector in self.elements_present

    def get_current_url(self) -> str:
        return self.navigation_history[-1] if self.navigation_history else ""


class TestDomainModelIntegration(unittest.TestCase):
    """
    Integration tests for the domain model components working together.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.driver = MockWebDriver()
        self.credential_repo = MockCredentialRepository()

        # No need to set class-level credential repository anymore

    def tearDown(self):
        """Tear down test fixtures."""
        # No teardown needed

    def test_credential_entity_integration(self):
        """Test that Credential entity can be created, serialized, and deserialized."""
        # Create a credential
        credential = Credential(name="test_login", username="user@example.com", password="password123")

        # Serialize to JSON
        json_str = credential.to_json()

        # Deserialize from JSON
        deserialized = Credential.from_json(json_str)

        # Verify the deserialized credential matches the original
        self.assertEqual(credential.name, deserialized.name)
        self.assertEqual(credential.username, deserialized.username)
        self.assertEqual(credential.password, deserialized.password)

    def test_action_execution_integration(self):
        """Test that actions can be executed with a web driver."""
        # Create actions
        navigate_action = NavigateAction(url="https://example.com")
        click_action = ClickAction(selector="#login-button")
        type_action = TypeAction(selector="#username", value_type="credential", value_key="test_login.username", credential_repository=self.credential_repo)
        wait_action = WaitAction(duration_seconds=1)
        screenshot_action = ScreenshotAction(file_path="test.png")

        # Execute actions
        navigate_result = navigate_action.execute(self.driver)
        click_result = click_action.execute(self.driver)
        type_result = type_action.execute(self.driver)
        wait_result = wait_action.execute(self.driver)
        screenshot_result = screenshot_action.execute(self.driver)

        # Verify results
        self.assertTrue(navigate_result.is_success())
        self.assertTrue(click_result.is_success())
        self.assertTrue(type_result.is_success())
        self.assertTrue(wait_result.is_success())
        self.assertTrue(screenshot_result.is_success())

        # Verify driver state
        self.assertEqual(self.driver.navigation_history, ["https://example.com"])
        self.assertEqual(self.driver.clicked_elements, ["#login-button"])
        self.assertEqual(self.driver.typed_text, {"#username": "user@example.com"})
        self.assertEqual(self.driver.screenshots, ["test.png"])

    def test_workflow_execution_integration(self):
        """Test that a workflow can be created and executed."""
        # Create actions
        actions = [
            NavigateAction(url="https://example.com"),
            ClickAction(selector="#login-button"),
            TypeAction(selector="#username", value_type="credential", value_key="test_login.username", credential_repository=self.credential_repo),
            TypeAction(selector="#password", value_type="credential", value_key="test_login.password", credential_repository=self.credential_repo),
            ClickAction(selector="#login-button"),
            WaitAction(duration_seconds=1)
        ]

        # Create workflow
        workflow = Workflow(name="login_workflow", actions=actions)

        # Execute workflow with credential repository
        results = workflow.execute(self.driver, self.credential_repo)

        # Verify results
        self.assertEqual(len(results), 6)
        for result in results:
            self.assertTrue(result.is_success())

        # Verify driver state
        self.assertEqual(self.driver.navigation_history, ["https://example.com"])
        self.assertEqual(self.driver.clicked_elements, ["#login-button", "#login-button"])
        self.assertEqual(self.driver.typed_text, {
            "#username": "user@example.com",
            "#password": "password123"
        })

    def test_action_factory_integration(self):
        """Test that ActionFactory can create actions from dictionaries."""
        # Create action dictionaries
        action_dicts = [
            {"type": "Navigate", "url": "https://example.com"},
            {"type": "Click", "selector": "#login-button"},
            {"type": "Type", "selector": "#username", "value_type": "credential", "value_key": "test_login.username"},
            {"type": "Wait", "duration_seconds": 1},
            {"type": "Screenshot", "file_path": "test.png"}
        ]

        # Create actions using factory
        actions = []
        for action_dict in action_dicts:
            action = ActionFactory.create_action(action_dict)
            # Set credential repository for TypeAction instances
            if isinstance(action, TypeAction):
                action.credential_repository = self.credential_repo
            actions.append(action)



        # Verify action types
        self.assertIsInstance(actions[0], NavigateAction)
        self.assertIsInstance(actions[1], ClickAction)
        self.assertIsInstance(actions[2], TypeAction)
        self.assertIsInstance(actions[3], WaitAction)
        self.assertIsInstance(actions[4], ScreenshotAction)

        # Execute actions
        results = [action.execute(self.driver) for action in actions]

        # Verify results
        for result in results:
            self.assertTrue(result.is_success())

    def test_workflow_serialization_integration(self):
        """Test that a workflow can be serialized and deserialized."""
        # Create actions
        actions = [
            NavigateAction(url="https://example.com"),
            ClickAction(selector="#login-button"),
            TypeAction(selector="#username", value_type="credential", value_key="test_login.username", credential_repository=self.credential_repo)
        ]

        # Create workflow
        workflow = Workflow(name="test_workflow", actions=actions)

        # Serialize to JSON
        json_str = workflow.to_json()

        # Deserialize from JSON
        deserialized = Workflow.from_json(json_str)

        # Verify the deserialized workflow matches the original
        self.assertEqual(workflow.name, deserialized.name)
        self.assertEqual(len(workflow.actions), len(deserialized.actions))

        # Execute both workflows with credential repository and compare results
        original_results = workflow.execute(self.driver, self.credential_repo)
        deserialized_results = deserialized.execute(self.driver, self.credential_repo)

        # Verify results
        self.assertEqual(len(original_results), len(deserialized_results))
        for result in original_results + deserialized_results:
            self.assertTrue(result.is_success())

    def test_exception_handling_integration(self):
        """Test that exceptions are properly handled during workflow execution."""
        # Create a mock driver that raises exceptions
        class ErrorProneDriver(MockWebDriver):
            def click_element(self, selector: str) -> None:
                if selector == "#error-button":
                    raise Exception("Simulated error")
                super().click_element(selector)

        error_driver = ErrorProneDriver()

        # Create actions with one that will fail
        actions = [
            NavigateAction(url="https://example.com"),
            ClickAction(selector="#error-button")  # This will fail
        ]

        # Create workflow
        workflow = Workflow(name="error_workflow", actions=actions)

        # Execute workflow and capture results
        results = workflow.execute(error_driver)

        # Verify results
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].is_success())
        self.assertFalse(results[1].is_success())
        self.assertIn("Failed to click element #error-button", results[1].message)


if __name__ == "__main__":
    unittest.main()
