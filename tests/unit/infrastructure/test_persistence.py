import unittest
from unittest.mock import patch, mock_open, MagicMock
from src.infrastructure.persistence import FileSystemCredentialRepository, FileSystemWorkflowRepository
from src.core.interfaces import IAction

class TestFileSystemCredentialRepository(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data='[{"name": "example_login", "username": "user@example.com", "password": "password123"}]')
    def test_get_all(self, mock_file):
        repo = FileSystemCredentialRepository("credentials.json")
        credentials = repo.get_all()
        self.assertEqual(len(credentials), 1)
        self.assertEqual(credentials[0]["name"], "example_login")

    @patch("builtins.open", new_callable=mock_open, read_data='[{"name": "example_login", "username": "user@example.com", "password": "password123"}]')
    def test_get_by_name(self, mock_file):
        repo = FileSystemCredentialRepository("credentials.json")
        credential = repo.get_by_name("example_login")
        self.assertIsNotNone(credential)
        self.assertEqual(credential["username"], "user@example.com")

class TestFileSystemWorkflowRepository(unittest.TestCase):
    @patch("os.listdir", return_value=["example_workflow.json"])
    def test_list_workflows(self, mock_listdir):
        repo = FileSystemWorkflowRepository("workflows")
        workflows = repo.list_workflows()
        self.assertEqual(len(workflows), 1)
        self.assertEqual(workflows[0], "example_workflow")

    @patch("builtins.open", new_callable=mock_open, read_data='[{"type": "Navigate", "url": "https://login.example.com"}]')
    def test_load(self, mock_file):
        repo = FileSystemWorkflowRepository("workflows")
        repo._create_action = MagicMock(return_value=MagicMock(spec=IAction))
        actions = repo.load("example_workflow")
        self.assertEqual(len(actions), 1)
        repo._create_action.assert_called_once_with({"type": "Navigate", "url": "https://login.example.com"})

    @patch("builtins.open", new_callable=mock_open)
    def test_save(self, mock_file):
        repo = FileSystemWorkflowRepository("workflows")
        action_mock = MagicMock(spec=IAction)
        action_mock.to_dict.return_value = {"type": "Navigate", "url": "https://login.example.com"}
        repo.save("example_workflow", [action_mock])
        mock_file().write.assert_called_once_with('[{"type": "Navigate", "url": "https://login.example.com"}]')

if __name__ == "__main__":
    unittest.main()
