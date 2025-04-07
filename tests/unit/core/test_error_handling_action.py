"""Unit tests for the ErrorHandlingAction."""

import unittest
from unittest.mock import MagicMock, call, ANY

# Assuming correct paths for imports
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.interfaces import IWebDriver, IAction, ICredentialRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError, ActionError

# Mock Actions for testing branches from conditional test can be reused
from tests.unit.core.test_conditional_action import MockBranchAction

class TestErrorHandlingAction(unittest.TestCase):
    """Tests for ErrorHandlingAction."""

    def setUp(self):
        """Set up mocks for each test."""
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_repo = MagicMock(spec=ICredentialRepository)

    def test_init_validation(self):
        """Test initialization validation."""
        # Valid: try only
        action_try = ErrorHandlingAction(name="TryOnly", try_actions=[MockBranchAction()])
        self.assertTrue(action_try.validate())

        # Valid: try and catch
        action_both = ErrorHandlingAction(name="TryCatch", try_actions=[MockBranchAction()], catch_actions=[MockBranchAction()])
        self.assertTrue(action_both.validate())

        # Valid: empty try, valid catch (maybe useful?)
        action_catch = ErrorHandlingAction(name="CatchOnly", try_actions=[], catch_actions=[MockBranchAction()])
        self.assertTrue(action_catch.validate())

        # Invalid nested action list type
        with self.assertRaisesRegex(ValidationError, "try_actions must be a list"):
            ErrorHandlingAction(name="BadTry", try_actions="not list") # type: ignore
        with self.assertRaisesRegex(ValidationError, "catch_actions must be a list"):
             ErrorHandlingAction(name="BadCatch", catch_actions={}) # type: ignore
        # Contains non-IAction
        with self.assertRaisesRegex(ValidationError, "try_actions must be a list"):
             ErrorHandlingAction(name="BadTryItem", try_actions=[MagicMock()])
        with self.assertRaisesRegex(ValidationError, "catch_actions must be a list"):
             ErrorHandlingAction(name="BadCatchItem", catch_actions=[123]) # type: ignore


    def test_validate_nested_actions(self):
         """Test that validation checks nested actions in both branches."""
         valid_action = MockBranchAction()
         invalid_action = MockBranchAction()
         invalid_action.validate = MagicMock(side_effect=ValidationError("Nested invalid"))

         # Invalid in try
         action_bad_try = ErrorHandlingAction(try_actions=[valid_action, invalid_action])
         with self.assertRaisesRegex(ValidationError, "Action 2 in try_actions failed validation"):
             action_bad_try.validate()
         self.assertEqual(valid_action.validate_mock.call_count, 1)
         self.assertEqual(invalid_action.validate.call_count, 1)

         # Invalid in catch
         valid_action.validate_mock.reset_mock()
         invalid_action.validate.reset_mock()
         action_bad_catch = ErrorHandlingAction(try_actions=[valid_action], catch_actions=[invalid_action])
         with self.assertRaisesRegex(ValidationError, "Action 1 in catch_actions failed validation"):
             action_bad_catch.validate()
         self.assertEqual(valid_action.validate_mock.call_count, 1)
         self.assertEqual(invalid_action.validate.call_count, 1)

    def test_execute_try_succeeds(self):
        """Test execution when all try_actions succeed."""
        try_action1 = MockBranchAction("Try1")
        try_action2 = MockBranchAction("Try2")
        catch_action = MockBranchAction("Catch1")

        action = ErrorHandlingAction(
            name="TrySuccess",
            try_actions=[try_action1, try_action2],
            catch_actions=[catch_action]
        )
        test_context = {"id": 1}
        result = action.execute(self.mock_driver, self.mock_repo, test_context)

        self.assertTrue(result.is_success())
        self.assertIn("no errors", result.message)
        # Verify try actions called with context
        try_action1.execute_mock.assert_called_once_with(self.mock_driver, self.mock_repo, test_context)
        try_action2.execute_mock.assert_called_once_with(self.mock_driver, self.mock_repo, test_context)
        # Verify catch action NOT called
        catch_action.execute_mock.assert_not_called()

    def test_execute_try_fails_catch_succeeds(self):
        """Test execution when try fails and catch succeeds (overall success)."""
        try_action1 = MockBranchAction("Try1", succeed=True)
        try_action2 = MockBranchAction("Try2Fail", succeed=False, msg="Try failed") # Fails
        try_action3 = MockBranchAction("Try3") # Skipped
        catch_action1 = MockBranchAction("Catch1", succeed=True)

        action = ErrorHandlingAction(
            name="TryFailCatchSuccess",
            try_actions=[try_action1, try_action2, try_action3],
            catch_actions=[catch_action1]
        )
        test_context = {"id": 2}
        result = action.execute(self.mock_driver, self.mock_repo, test_context)

        self.assertTrue(result.is_success()) # Overall success because catch handled it
        self.assertIn("Error handled by 'catch' block", result.message)
        # Verify try actions called up to failure
        try_action1.execute_mock.assert_called_once()
        try_action2.execute_mock.assert_called_once()
        try_action3.execute_mock.assert_not_called()
        # Verify catch action called with modified context
        catch_action1.execute_mock.assert_called_once()
        call_args, _ = catch_action1.execute_mock.call_args
        self.assertEqual(call_args[0], self.mock_driver)
        self.assertEqual(call_args[1], self.mock_repo)
        expected_catch_context = {'id': 2, 'try_block_error_message': 'Try failed', 'try_block_error_type': 'ActionFailure'}
        self.assertEqual(call_args[2], expected_catch_context)


    def test_execute_try_raises_catch_succeeds(self):
        """Test execution when try raises exception and catch succeeds."""
        try_action1 = MockBranchAction("Try1")
        try_action2 = MockBranchAction("Try2Raise")
        try_action2.execute_mock.side_effect = ValueError("Try exception") # Raises
        catch_action1 = MockBranchAction("Catch1")

        action = ErrorHandlingAction(
            name="TryRaiseCatchSuccess",
            try_actions=[try_action1, try_action2],
            catch_actions=[catch_action1]
        )
        result = action.execute(self.mock_driver, self.mock_repo)

        self.assertTrue(result.is_success()) # Overall success
        self.assertIn("Error handled by 'catch' block", result.message)
        try_action1.execute_mock.assert_called_once()
        try_action2.execute_mock.assert_called_once()
        # Verify catch action called with error context
        catch_action1.execute_mock.assert_called_once()
        call_args, _ = catch_action1.execute_mock.call_args
        self.assertEqual(call_args[2]['try_block_error_type'], 'ValueError')
        self.assertEqual(call_args[2]['try_block_error_message'], 'Try exception')

    def test_execute_try_fails_no_catch(self):
        """Test failure propagates if try fails and no catch block exists."""
        try_action1 = MockBranchAction("Try1Fail", succeed=False, msg="Original Fail")

        action = ErrorHandlingAction(
            name="TryFailNoCatch",
            try_actions=[try_action1],
            catch_actions=[] # Empty catch
        )
        result = action.execute(self.mock_driver, self.mock_repo)

        self.assertFalse(result.is_success())
        self.assertIn("'try' block failed and no 'catch' block defined", result.message)
        self.assertIn("Original Fail", result.message)
        try_action1.execute_mock.assert_called_once()


    def test_execute_try_fails_catch_fails(self):
        """Test failure if try fails AND catch also fails."""
        try_action1 = MockBranchAction("Try1Fail", succeed=False, msg="Try Failed")
        catch_action1 = MockBranchAction("Catch1Fail", succeed=False, msg="Catch Failed")

        action = ErrorHandlingAction(
            name="BothFail",
            try_actions=[try_action1],
            catch_actions=[catch_action1]
        )
        result = action.execute(self.mock_driver, self.mock_repo)

        self.assertFalse(result.is_success())
        self.assertIn("Original error occurred AND 'catch' block failed", result.message)
        self.assertIn("Catch failure: Catch Failed", result.message)
        try_action1.execute_mock.assert_called_once()
        catch_action1.execute_mock.assert_called_once()


    def test_execute_try_fails_catch_raises(self):
        """Test failure if try fails AND catch raises an exception."""
        try_action1 = MockBranchAction("Try1Fail", succeed=False, msg="Try Failed")
        catch_action1 = MockBranchAction("Catch1Raise")
        catch_action1.execute_mock.side_effect = RuntimeError("Catch Exception")

        action = ErrorHandlingAction(
            name="TryFailCatchRaise",
            try_actions=[try_action1],
            catch_actions=[catch_action1]
        )
        result = action.execute(self.mock_driver, self.mock_repo)

        self.assertFalse(result.is_success())
        self.assertIn("Original error occurred AND 'catch' block raised exception", result.message)
        self.assertIn("Catch exception: RuntimeError: Catch Exception", result.message)
        try_action1.execute_mock.assert_called_once()
        catch_action1.execute_mock.assert_called_once()


    @patch('src.core.actions.error_handling_action.serialize_actions')
    def test_to_dict_serialization(self, mock_serialize):
        """Test serialization includes nested actions."""
        try_action = MockBranchAction("TryAct")
        catch_action = MockBranchAction("CatchAct")
        action = ErrorHandlingAction(
            name="ErrHandleSer",
            try_actions=[try_action],
            catch_actions=[catch_action]
        )

        mock_serialize.side_effect = [
            [try_action.to_dict()], # Return for try_actions
            [catch_action.to_dict()] # Return for catch_actions
        ]

        expected_dict = {
            "type": "ErrorHandling",
            "name": "ErrHandleSer",
            "try_actions": [try_action.to_dict()],
            "catch_actions": [catch_action.to_dict()],
        }
        self.assertEqual(action.to_dict(), expected_dict)
        self.assertEqual(mock_serialize.call_count, 2)
        mock_serialize.assert_has_calls([call([try_action]), call([catch_action])])


    def test_get_nested_actions(self):
        """Test retrieving nested actions from both branches."""
        try_action = MockBranchAction("Try1")
        catch_action = MockBranchAction("Catch1")
        action = ErrorHandlingAction(
            try_actions=[try_action],
            catch_actions=[catch_action],
            name="NestErr"
        )
        nested = action.get_nested_actions()
        self.assertEqual(len(nested), 2)
        self.assertIn(try_action, nested)
        self.assertIn(catch_action, nested)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)