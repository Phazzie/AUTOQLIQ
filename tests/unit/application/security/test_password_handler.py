"""Unit tests for password handlers."""

import unittest
from unittest.mock import patch, MagicMock

# Module containing the handlers
from src.application.security import password_handler
from src.application.security.password_handler import IPasswordHandler, WerkzeugPasswordHandler

# Mock werkzeug functions conditionally based on actual availability during test run
mock_werkzeug = password_handler.WERKZEUG_AVAILABLE

class TestWerkzeugPasswordHandler(unittest.TestCase):
    """Tests for the WerkzeugPasswordHandler."""

    def setUp(self):
        self.handler = WerkzeugPasswordHandler()

    @unittest.skipUnless(mock_werkzeug, "Werkzeug library not available")
    @patch('src.application.security.password_handler.generate_password_hash')
    def test_hash_password_werkzeug_available(self, mock_generate):
        """Test hashing when werkzeug is available."""
        mock_generate.return_value = "hashed_password_value"
        password = "mypassword"
        expected_method = self.handler.DEFAULT_HASH_METHOD

        hashed = self.handler.hash_password(password)

        self.assertEqual(hashed, "hashed_password_value")
        mock_generate.assert_called_once_with(password, method=expected_method)

    @unittest.skipIf(mock_werkzeug, "Werkzeug library IS available")
    def test_hash_password_werkzeug_unavailable(self):
        """Test hashing fallback when werkzeug is unavailable."""
        password = "mypassword"
        with self.assertLogs(level='CRITICAL') as log:
            hashed = self.handler.hash_password(password)

        self.assertEqual(hashed, f"plaintext:{password}")
        self.assertIn("SECURITY RISK", log.output[0])
        self.assertIn("Werkzeug not available", log.output[0])

    @unittest.skipUnless(mock_werkzeug, "Werkzeug library not available")
    @patch('src.application.security.password_handler.check_password_hash')
    def test_verify_password_werkzeug_available_success(self, mock_check):
        """Test successful verification when werkzeug is available."""
        mock_check.return_value = True
        stored_hash = "pbkdf2:sha256:600000$salt$hashpart"
        provided_password = "correct_password"

        is_valid = self.handler.verify_password(stored_hash, provided_password)

        self.assertTrue(is_valid)
        mock_check.assert_called_once_with(stored_hash, provided_password)

    @unittest.skipUnless(mock_werkzeug, "Werkzeug library not available")
    @patch('src.application.security.password_handler.check_password_hash')
    def test_verify_password_werkzeug_available_failure(self, mock_check):
        """Test failed verification when werkzeug is available."""
        mock_check.return_value = False
        stored_hash = "pbkdf2:sha256:600000$salt$hashpart"
        provided_password = "wrong_password"

        is_valid = self.handler.verify_password(stored_hash, provided_password)

        self.assertFalse(is_valid)
        mock_check.assert_called_once_with(stored_hash, provided_password)

    @unittest.skipIf(mock_werkzeug, "Werkzeug library IS available")
    def test_verify_password_werkzeug_unavailable_plaintext_success(self):
        """Test successful plaintext verification when werkzeug is unavailable."""
        stored_hash = "plaintext:correct_password"
        provided_password = "correct_password"

        with self.assertLogs(level='WARNING') as log:
            is_valid = self.handler.verify_password(stored_hash, provided_password)

        self.assertTrue(is_valid)
        self.assertIn("Attempting insecure plaintext", log.output[0])

    @unittest.skipIf(mock_werkzeug, "Werkzeug library IS available")
    def test_verify_password_werkzeug_unavailable_plaintext_failure(self):
        """Test failed plaintext verification when werkzeug is unavailable."""
        stored_hash = "plaintext:correct_password"
        provided_password = "wrong_password"

        with self.assertLogs(level='WARNING'): # Still logs warning
            is_valid = self.handler.verify_password(stored_hash, provided_password)

        self.assertFalse(is_valid)

    @unittest.skipIf(mock_werkzeug, "Werkzeug library IS available")
    def test_verify_password_werkzeug_unavailable_unknown_hash(self):
        """Test verification failure for unknown hash format when werkzeug unavailable."""
        stored_hash = "unknownformat$hash"
        provided_password = "password"

        with self.assertLogs(level='ERROR') as log:
            is_valid = self.handler.verify_password(stored_hash, provided_password)

        self.assertFalse(is_valid)
        self.assertIn("Cannot verify password", log.output[0])
        self.assertIn("unknown format", log.output[0])

    def test_verify_password_empty_inputs(self):
        """Test verification fails with empty inputs."""
        self.assertFalse(self.handler.verify_password("", "password"))
        self.assertFalse(self.handler.verify_password("hash", ""))
        self.assertFalse(self.handler.verify_password("", ""))

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
