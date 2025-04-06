"""Enhanced tests for the CredentialService class.

This module provides comprehensive tests for the CredentialService class,
following TDD, SOLID, KISS, and DRY principles.
"""
import unittest
from unittest.mock import MagicMock

from src.core.exceptions import CredentialError
from src.core.interfaces import ICredentialRepository
from src.application.interfaces import ICredentialService
from src.application.services.credential_service import CredentialService


class TestCredentialService(unittest.TestCase):
    """Test cases for the CredentialService class.

    This test suite verifies that the CredentialService correctly implements
    the ICredentialService interface and properly interacts with the
    ICredentialRepository dependency.
    """

    def setUp(self):
        """Set up test fixtures.

        Creates a mock credential repository and initializes the credential service
        with this mock. Also sets up a sample credential for testing.
        """
        # Create a mock repository with the correct interface
        self.credential_repo = MagicMock(spec=ICredentialRepository)

        # Create the service under test
        self.service = CredentialService(credential_repository=self.credential_repo)

        # Sample credential for testing
        self.sample_credential = {
            "name": "test_credential",
            "username": "test_user",
            "password": "test_pass"
        }

        # Create the service with a mock logger
        self.service.logger = MagicMock()
        self.mock_logger = self.service.logger

    def tearDown(self):
        """Clean up after tests.

        Reset mocks to ensure they don't affect other tests.
        """
        # No need to stop patches since we're not using them anymore

    def test_should_implement_icredential_service_interface(self):
        """
        Verifies that CredentialService correctly implements the ICredentialService interface.

        Given:
        - A CredentialService instance

        When:
        - Checking if it's an instance of ICredentialService

        Then:
        - It should be an instance of ICredentialService
        """
        # Arrange - done in setUp

        # Act & Assert
        self.assertIsInstance(self.service, ICredentialService)

    def test_should_create_credential_when_valid_inputs_provided(self):
        """
        Verifies that create_credential creates a new credential when valid inputs are provided.

        Given:
        - A CredentialService with a mock repository
        - Valid credential information (name, username, password)

        When:
        - Calling create_credential with the valid information

        Then:
        - The repository's save_credential method should be called with the correct credential
        - The method should return True
        - The operation should be logged
        """
        # Arrange
        name = "test_credential"
        username = "test_user"
        password = "test_pass"
        self.credential_repo.save.return_value = None

        # Act
        result = self.service.create_credential(name, username, password)

        # Assert
        self.assertTrue(result)
        expected_credential = {
            "name": name,
            "username": username,
            "password": password
        }
        self.credential_repo.save.assert_called_once_with(expected_credential)
        self.mock_logger.info.assert_called_with(f"Creating credential: {name}")

    def test_should_raise_credential_error_when_create_credential_fails(self):
        """
        Verifies that create_credential raises CredentialError when the repository operation fails.

        Given:
        - A CredentialService with a mock repository
        - The repository raises an exception when save_credential is called

        When:
        - Calling create_credential

        Then:
        - CredentialError should be raised
        - The error should contain appropriate context information
        """
        # Arrange
        name = "test_credential"
        username = "test_user"
        password = "test_pass"
        error_message = "Database connection failed"
        self.credential_repo.save.side_effect = Exception(error_message)

        # Act & Assert
        with self.assertRaises(CredentialError) as context:
            self.service.create_credential(name, username, password)

        # Verify error message contains both the decorator's message and the original error
        self.assertIn("Failed to create credential", str(context.exception))
        self.assertIn(error_message, str(context.exception))

    def test_should_update_credential_when_credential_exists(self):
        """
        Verifies that update_credential updates an existing credential.

        Given:
        - A CredentialService with a mock repository
        - A credential that exists in the repository
        - New credential information

        When:
        - Calling update_credential with the new information

        Then:
        - The repository's get_by_name method should be called to verify existence
        - The repository's save_credential method should be called with the updated credential
        - The method should return True
        - The operation should be logged
        """
        # Arrange
        name = "test_credential"
        new_username = "new_user"
        new_password = "new_pass"
        self.credential_repo.get_by_name.return_value = self.sample_credential
        self.credential_repo.save.return_value = None

        # Act
        result = self.service.update_credential(name, new_username, new_password)

        # Assert
        self.assertTrue(result)
        self.credential_repo.get_by_name.assert_called_once_with(name)
        expected_credential = {
            "name": name,
            "username": new_username,
            "password": new_password
        }
        self.credential_repo.save.assert_called_once_with(expected_credential)
        self.mock_logger.info.assert_called_with(f"Updating credential: {name}")

    def test_should_raise_credential_error_when_update_credential_not_found(self):
        """
        Verifies that update_credential raises CredentialError when the credential doesn't exist.

        Given:
        - A CredentialService with a mock repository
        - The repository raises CredentialError when get_by_name is called

        When:
        - Calling update_credential

        Then:
        - CredentialError should be raised
        - The error should contain appropriate context information
        """
        # Arrange
        name = "nonexistent_credential"
        username = "new_user"
        password = "new_pass"
        error_message = "Credential not found"
        self.credential_repo.get_by_name.side_effect = CredentialError(error_message)

        # Act & Assert
        with self.assertRaises(CredentialError) as context:
            self.service.update_credential(name, username, password)

        # Verify error message
        self.assertIn(error_message, str(context.exception))

        # Verify save_credential was not called
        self.credential_repo.save.assert_not_called()

    def test_should_raise_credential_error_when_update_credential_save_fails(self):
        """
        Verifies that update_credential raises CredentialError when saving the credential fails.

        Given:
        - A CredentialService with a mock repository
        - The credential exists in the repository
        - The repository raises an exception when save_credential is called

        When:
        - Calling update_credential

        Then:
        - CredentialError should be raised
        - The error should contain appropriate context information
        """
        # Arrange
        name = "test_credential"
        username = "new_user"
        password = "new_pass"
        self.credential_repo.get_by_name.return_value = self.sample_credential
        error_message = "Database connection failed"
        self.credential_repo.save.side_effect = Exception(error_message)

        # Act & Assert
        with self.assertRaises(CredentialError) as context:
            self.service.update_credential(name, username, password)

        # Verify error message contains both the decorator's message and the original error
        self.assertIn("Failed to update credential", str(context.exception))
        self.assertIn(error_message, str(context.exception))

    def test_should_delete_credential_when_credential_exists(self):
        """
        Verifies that delete_credential deletes an existing credential.

        Given:
        - A CredentialService with a mock repository
        - A credential that exists in the repository

        When:
        - Calling delete_credential with the credential name

        Then:
        - The repository's delete_credential method should be called with the credential name
        - The method should return True
        - The operation should be logged
        """
        # Arrange
        name = "test_credential"
        self.credential_repo.delete.return_value = True

        # Act
        result = self.service.delete_credential(name)

        # Assert
        self.assertTrue(result)
        self.credential_repo.delete.assert_called_once_with(name)
        self.mock_logger.info.assert_called_with(f"Deleting credential: {name}")

    def test_should_raise_credential_error_when_delete_credential_fails(self):
        """
        Verifies that delete_credential raises CredentialError when the repository operation fails.

        Given:
        - A CredentialService with a mock repository
        - The repository raises an exception when delete_credential is called

        When:
        - Calling delete_credential

        Then:
        - CredentialError should be raised
        - The error should contain appropriate context information
        """
        # Arrange
        name = "test_credential"
        error_message = "Database connection failed"
        self.credential_repo.delete.side_effect = Exception(error_message)

        # Act & Assert
        with self.assertRaises(CredentialError) as context:
            self.service.delete_credential(name)

        # Verify error message contains both the decorator's message and the original error
        self.assertIn("Failed to delete credential", str(context.exception))
        self.assertIn(error_message, str(context.exception))

    def test_should_get_credential_when_credential_exists(self):
        """
        Verifies that get_credential returns the credential when it exists.

        Given:
        - A CredentialService with a mock repository
        - A credential that exists in the repository

        When:
        - Calling get_credential with the credential name

        Then:
        - The repository's get_by_name method should be called with the credential name
        - The method should return the credential
        - The operation should be logged
        """
        # Arrange
        name = "test_credential"
        self.credential_repo.get_by_name.return_value = self.sample_credential

        # Act
        result = self.service.get_credential(name)

        # Assert
        self.assertEqual(result, self.sample_credential)
        self.credential_repo.get_by_name.assert_called_once_with(name)
        self.mock_logger.debug.assert_called_with(f"Getting credential: {name}")

    def test_should_raise_credential_error_when_get_credential_fails(self):
        """
        Verifies that get_credential raises CredentialError when the repository operation fails.

        Given:
        - A CredentialService with a mock repository
        - The repository raises an exception when get_by_name is called

        When:
        - Calling get_credential

        Then:
        - CredentialError should be raised
        - The error should contain appropriate context information
        """
        # Arrange
        name = "test_credential"
        error_message = "Database connection failed"
        self.credential_repo.get_by_name.side_effect = Exception(error_message)

        # Act & Assert
        with self.assertRaises(CredentialError) as context:
            self.service.get_credential(name)

        # Verify error message contains both the decorator's message and the original error
        self.assertIn("Failed to get credential", str(context.exception))
        self.assertIn(error_message, str(context.exception))

    def test_should_list_credentials_when_credentials_exist(self):
        """
        Verifies that list_credentials returns a list of credential names.

        Given:
        - A CredentialService with a mock repository
        - Multiple credentials exist in the repository

        When:
        - Calling list_credentials

        Then:
        - The repository's get_all method should be called
        - The method should return a list of credential names
        - The operation should be logged
        """
        # Arrange
        credential_names = ["credential1", "credential2"]
        self.credential_repo.list_credentials.return_value = credential_names

        # Act
        result = self.service.list_credentials()

        # Assert
        self.assertEqual(result, ["credential1", "credential2"])
        self.credential_repo.list_credentials.assert_called_once()
        self.mock_logger.debug.assert_called_with("Listing credentials")

    def test_should_return_empty_list_when_no_credentials_exist(self):
        """
        Verifies that list_credentials returns an empty list when no credentials exist.

        Given:
        - A CredentialService with a mock repository
        - No credentials exist in the repository

        When:
        - Calling list_credentials

        Then:
        - The repository's get_all method should be called
        - The method should return an empty list
        - The operation should be logged
        """
        # Arrange
        self.credential_repo.list_credentials.return_value = []

        # Act
        result = self.service.list_credentials()

        # Assert
        self.assertEqual(result, [])
        self.credential_repo.list_credentials.assert_called_once()
        self.mock_logger.debug.assert_called_with("Listing credentials")

    def test_should_raise_credential_error_when_list_credentials_fails(self):
        """
        Verifies that list_credentials raises CredentialError when the repository operation fails.

        Given:
        - A CredentialService with a mock repository
        - The repository raises an exception when get_all is called

        When:
        - Calling list_credentials

        Then:
        - CredentialError should be raised
        - The error should contain appropriate context information
        """
        # Arrange
        error_message = "Database connection failed"
        self.credential_repo.list_credentials.side_effect = Exception(error_message)

        # Act & Assert
        with self.assertRaises(CredentialError) as context:
            self.service.list_credentials()

        # Verify error message contains both the decorator's message and the original error
        self.assertIn("Failed to list credentials", str(context.exception))
        self.assertIn(error_message, str(context.exception))

    def test_should_verify_decorator_order_for_method_calls(self):
        """
        Verifies that the decorators are applied in the correct order.

        The @log_method_call decorator should be applied before @handle_exceptions
        to ensure that method calls are logged even if they raise exceptions.

        Given:
        - A CredentialService with a mock repository
        - The repository raises an exception

        When:
        - Calling a method that will raise an exception

        Then:
        - The method call should be logged before the exception is handled
        """
        # This test is more of a design verification than a functional test
        # We're checking that the decorators are applied in the correct order
        # by examining the class definition

        # Import the module to get access to the actual class definition
        import inspect
        from src.application.services.credential_service import CredentialService

        # Get the source code of the class
        source = inspect.getsource(CredentialService)

        # Check that @log_method_call appears before @handle_exceptions for each method
        methods = ["create_credential", "update_credential", "delete_credential",
                  "get_credential", "list_credentials"]

        for method in methods:
            method_index = source.find(f"def {method}")
            if method_index == -1:
                self.fail(f"Method {method} not found in CredentialService")

            # Get the decorators for this method
            method_source = source[:method_index]
            last_decorators = method_source.split("@")[-2:]  # Get the last two decorators

            # Check that log_method_call comes before handle_exceptions
            self.assertTrue(
                "log_method_call" in last_decorators[0] and "handle_exceptions" in last_decorators[1],
                f"Decorators for {method} are not in the correct order"
            )


if __name__ == "__main__":
    unittest.main()
