import unittest
from unittest.mock import MagicMock, patch

from src.presenters.workflow_runner_presenter import WorkflowRunnerPresenter
from src.core.exceptions import WorkflowError, CredentialError, WebDriverError


class TestWorkflowRunnerPresenter(unittest.TestCase):
    def setUp(self):
        # Create mock dependencies
        self.workflow_repository = MagicMock()
        self.credential_repository = MagicMock()
        self.webdriver_factory = MagicMock()
        self.workflow_runner = MagicMock()

        # Create test data
        self.test_workflow_name = "test_workflow"
        self.test_credential_name = "test_credential"
        self.test_credential = {
            "name": self.test_credential_name,
            "username": "testuser",
            "password": "testpass"
        }
        self.test_actions = [MagicMock(), MagicMock()]

        # Set up mock repository responses
        self.workflow_repository.get_workflow_list.return_value = ["workflow1", "workflow2"]
        self.workflow_repository.load_workflow.return_value = self.test_actions

        self.credential_repository.get_all.return_value = [self.test_credential]
        self.credential_repository.get_by_name.return_value = self.test_credential

        # Set up mock webdriver factory
        self.mock_webdriver = MagicMock()
        self.webdriver_factory.create_webdriver.return_value = self.mock_webdriver

        # Set up mock workflow runner
        self.workflow_runner.run_workflow.return_value = True

        # Create the presenter after setting up all mocks
        self.presenter = WorkflowRunnerPresenter(
            self.workflow_repository,
            self.credential_repository,
            self.webdriver_factory,
            self.workflow_runner
        )

    def test_get_workflow_list(self):
        # Act
        result = self.presenter.get_workflow_list()

        # Assert
        self.workflow_repository.get_workflow_list.assert_called_once()
        self.assertEqual(result, ["workflow1", "workflow2"])

    def test_get_credential_list(self):
        # Act
        result = self.presenter.get_credential_list()

        # Assert
        self.credential_repository.get_all.assert_called_once()
        self.assertEqual(result, [self.test_credential])

    def test_run_workflow(self):
        # Act
        result = self.presenter.run_workflow(self.test_workflow_name, self.test_credential_name)

        # Assert
        # Check that the workflow was loaded
        self.workflow_repository.load_workflow.assert_called_once_with(self.test_workflow_name)

        # Check that the credential was retrieved
        self.credential_repository.get_by_name.assert_called_once_with(self.test_credential_name)

        # Check that the webdriver was created
        self.webdriver_factory.create_webdriver.assert_called_once()

        # Check that the workflow runner was called
        self.workflow_runner.run_workflow.assert_called_once_with(
            self.test_actions,
            self.mock_webdriver,
            self.test_credential
        )

        # Check the result
        self.assertTrue(result)

    def test_run_workflow_error_loading_workflow(self):
        # Arrange
        self.workflow_repository.load_workflow.side_effect = WorkflowError("Test error")

        # Act & Assert
        with self.assertRaises(WorkflowError):
            self.presenter.run_workflow(self.test_workflow_name, self.test_credential_name)

    def test_run_workflow_error_getting_credential(self):
        # Arrange
        self.credential_repository.get_by_name.side_effect = CredentialError("Test error")

        # Act & Assert
        with self.assertRaises(CredentialError):
            self.presenter.run_workflow(self.test_workflow_name, self.test_credential_name)

    def test_run_workflow_credential_not_found(self):
        # Arrange
        self.credential_repository.get_by_name.return_value = None

        # Act & Assert
        with self.assertRaises(CredentialError):
            self.presenter.run_workflow(self.test_workflow_name, self.test_credential_name)

    def test_run_workflow_error_creating_webdriver(self):
        # Arrange
        self.webdriver_factory.create_webdriver.side_effect = WebDriverError("Test error")

        # Act & Assert
        with self.assertRaises(WebDriverError):
            self.presenter.run_workflow(self.test_workflow_name, self.test_credential_name)

    def test_run_workflow_error_running_workflow(self):
        # Arrange
        self.workflow_runner.run_workflow.side_effect = Exception("Test error")

        # Act & Assert
        with self.assertRaises(Exception):
            self.presenter.run_workflow(self.test_workflow_name, self.test_credential_name)

    def test_stop_workflow(self):
        # Arrange
        self.workflow_runner.stop_workflow.return_value = True

        # Act
        result = self.presenter.stop_workflow()

        # Assert
        self.workflow_runner.stop_workflow.assert_called_once()
        self.assertTrue(result)

    def test_stop_workflow_error(self):
        # Arrange
        self.workflow_runner.stop_workflow.side_effect = Exception("Test error")

        # Act & Assert
        with self.assertRaises(Exception):
            self.presenter.stop_workflow()

    def test_cleanup(self):
        # Set the webdriver to ensure it exists
        self.presenter._webdriver = self.mock_webdriver

        # Act
        self.presenter.cleanup()

        # Assert
        self.mock_webdriver.quit.assert_called_once()

    def test_cleanup_no_webdriver(self):
        # Arrange
        self.presenter._webdriver = None

        # Act - Should not raise an exception
        self.presenter.cleanup()

    def test_cleanup_error(self):
        # Arrange
        self.mock_webdriver.quit.side_effect = Exception("Test error")

        # Act - Should not raise an exception
        self.presenter.cleanup()

    def test_load_workflow(self):
        # Act
        result = self.presenter.load_workflow(self.test_workflow_name)

        # Assert
        self.workflow_repository.load_workflow.assert_called_once_with(self.test_workflow_name)
        self.assertEqual(result, self.test_actions)

    def test_get_credential(self):
        # Act
        result = self.presenter.get_credential(self.test_credential_name)

        # Assert
        self.credential_repository.get_by_name.assert_called_once_with(self.test_credential_name)
        self.assertEqual(result, self.test_credential)

    def test_create_webdriver(self):
        # Act
        result = self.presenter.create_webdriver()

        # Assert
        self.webdriver_factory.create_webdriver.assert_called_once()
        self.assertEqual(result, self.mock_webdriver)

    def test_run_workflow_actions(self):
        # Act
        result = self.presenter.run_workflow_actions(self.test_actions, self.mock_webdriver, self.test_credential)

        # Assert
        self.workflow_runner.run_workflow.assert_called_once_with(self.test_actions, self.mock_webdriver, self.test_credential)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
