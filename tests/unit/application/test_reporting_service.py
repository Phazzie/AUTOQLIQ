"""Unit tests for the ReportingService."""

import unittest
import os
import json
import time
import shutil # For cleaning up logs dir
from unittest.mock import patch, mock_open, ANY, MagicMock
from datetime import datetime

# Assuming correct paths for imports
from src.application.services.reporting_service import ReportingService, LOG_DIRECTORY
from src.core.exceptions import RepositoryError, AutoQliqError

class TestReportingService(unittest.TestCase):
    """Test suite for ReportingService."""

    def setUp(self):
        """Set up test environment."""
        # Ensure log directory exists for tests but is empty
        if os.path.exists(LOG_DIRECTORY): shutil.rmtree(LOG_DIRECTORY)
        os.makedirs(LOG_DIRECTORY, exist_ok=True)
        self.service = ReportingService()

    def tearDown(self):
        """Clean up log directory."""
        if os.path.exists(LOG_DIRECTORY): shutil.rmtree(LOG_DIRECTORY)
        patch.stopall() # Stop any patches started in tests

    @patch("src.application.services.reporting_service.os.makedirs")
    @patch("src.application.services.reporting_service.os.path.exists")
    def test_init_ensures_log_directory(self, mock_exists, mock_makedirs):
        """Test __init__ creates log directory if it doesn't exist."""
        mock_exists.return_value = False
        ReportingService() # Re-initialize
        mock_exists.assert_called_once_with(LOG_DIRECTORY)
        mock_makedirs.assert_called_once_with(LOG_DIRECTORY, exist_ok=True)

    @patch("src.application.services.reporting_service.open", new_callable=mock_open)
    @patch("src.application.services.reporting_service.os.path.join")
    @patch("src.application.services.reporting_service.datetime")
    def test_save_execution_log_success(self, mock_dt, mock_join, mock_file_open):
        """Test saving a valid execution log creates correct file and content."""
        mock_now = datetime(2024, 7, 27, 14, 0, 0); mock_dt.now.return_value = mock_now
        mock_dt.fromisoformat.return_value = mock_now
        wf_name = "Test_WF"; start_iso = mock_now.isoformat()
        log_data = { "workflow_name": wf_name, "start_time_iso": start_iso, "end_time_iso": (mock_now.replace(second=15)).isoformat(),
                     "duration_seconds": 15.0, "final_status": "SUCCESS", "error_message": None, "action_results": [{"status": "success"}] }
        expected_filename = "exec_Test_WF_20240727_140000_SUCCESS.json"; expected_filepath = os.path.join(LOG_DIRECTORY, expected_filename)
        mock_join.return_value = expected_filepath

        self.service.save_execution_log(log_data)

        mock_join.assert_called_once_with(LOG_DIRECTORY, expected_filename)
        mock_file_open.assert_called_once_with(expected_filepath, 'w', encoding='utf-8')
        handle = mock_file_open(); written_content = "".join(call_args[0][0] for call_args in handle.write.call_args_list)
        saved_json_data = json.loads(written_content); self.assertEqual(saved_json_data, log_data)

    def test_save_execution_log_invalid_data_logs_error(self):
        """Test saving invalid log data logs error and doesn't write."""
        with patch("src.application.services.reporting_service.open", new_callable=mock_open) as mock_file:
            with self.assertLogs(level='ERROR') as log: self.service.save_execution_log({})
            self.assertIn("invalid execution log data", log.output[0]); mock_file.assert_not_called()

    @patch("src.application.services.reporting_service.open", side_effect=IOError("Cannot write"))
    def test_save_execution_log_io_error_raises_repository_error(self, mock_file_open):
        """Test save raises RepositoryError on file write failure."""
        log_data = {"workflow_name": "Test", "start_time_iso": datetime.now().isoformat()}
        with self.assertRaisesRegex(RepositoryError, "Failed to write execution log.*Cannot write"):
            self.service.save_execution_log(log_data)

    # --- Tests for Reading Logs ---
    @patch("src.application.services.reporting_service.os.listdir")
    @patch("src.application.services.reporting_service.open", new_callable=mock_open)
    @patch("src.application.services.reporting_service.json.load")
    def test_list_past_executions_success(self, mock_json_load, mock_file, mock_listdir):
        """Test listing past executions reads summary from log files."""
        log_files = [ "exec_WF_B_20240726_110000_FAILED.json", "exec_WF_A_20240727_100000_SUCCESS.json",
                      "exec_WF_A_20240727_090000_SUCCESS.json", "readme.txt" ]
        mock_listdir.return_value = log_files
        log_content = {"workflow_name": "WF_X", "start_time_iso": "2024-07-27T00:00:00", "final_status": "S", "duration_seconds": 1.0}
        mock_json_load.return_value = log_content # Return same content for all reads for simplicity

        results = self.service.list_past_executions(limit=50)

        mock_listdir.assert_called_once_with(LOG_DIRECTORY)
        self.assertEqual(mock_file.call_count, 3) # Opened 3 json files
        self.assertEqual(mock_json_load.call_count, 3)
        self.assertEqual(len(results), 3)
        # Check structure of one item (order depends on listdir/sort)
        self.assertIn('execution_id', results[0]); self.assertIn('workflow_name', results[0])
        self.assertIn('start_time_iso', results[0]); self.assertIn('final_status', results[0])
        self.assertIn('duration_seconds', results[0]); self.assertNotIn('action_results', results[0])

    @patch("src.application.services.reporting_service.os.listdir")
    def test_list_past_executions_filter_by_name(self, mock_listdir):
         """Test filtering executions by workflow name."""
         log_files = ["exec_WF_A_20240727_100000_S.json", "exec_WF_B_20240726_110000_F.json", "exec_WF_A_20240727_090000_S.json"]
         mock_listdir.return_value = log_files
         with patch("src.application.services.reporting_service.open", mock_open()):
              with patch("src.application.services.reporting_service.json.load") as mock_json_load:
                   mock_json_load.return_value = {"workflow_name": "WF_A", "start_time_iso": "", "final_status": "", "duration_seconds": 0}
                   results = self.service.list_past_executions(workflow_name="WF_A")
                   self.assertEqual(len(results), 2)
                   self.assertEqual(mock_json_load.call_count, 2) # Only loaded WF_A files

    @patch("src.application.services.reporting_service.os.listdir", return_value=[])
    def test_list_past_executions_empty(self, mock_listdir): self.assertEqual(self.service.list_past_executions(), [])

    @patch("src.application.services.reporting_service.os.path.exists")
    @patch("src.application.services.reporting_service.open", new_callable=mock_open)
    @patch("src.application.services.reporting_service.json.load")
    def test_get_execution_details_success(self, mock_json_load, mock_file, mock_exists):
        """Test getting details for a specific execution ID (filename)."""
        exec_id = "exec_WF_A_20240727_100000_SUCCESS.json"; expected_log_data = {"workflow_name": "WF_A", "action_results": []}
        expected_filepath = os.path.join(LOG_DIRECTORY, exec_id); mock_exists.return_value = True
        mock_json_load.return_value = expected_log_data

        details = self.service.get_execution_details(exec_id)

        mock_exists.assert_called_once_with(expected_filepath); mock_file.assert_called_once_with(expected_filepath, 'r', encoding='utf-8')
        mock_json_load.assert_called_once(); self.assertEqual(details, expected_log_data)

    @patch("src.application.services.reporting_service.os.path.exists", return_value=False)
    def test_get_execution_details_not_found(self, mock_exists):
        """Test getting details for a non-existent execution ID."""
        exec_id = "non_existent_log.json"; expected_filepath = os.path.join(LOG_DIRECTORY, exec_id)
        details = self.service.get_execution_details(exec_id)
        self.assertIsNone(details); mock_exists.assert_called_once_with(expected_filepath)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)