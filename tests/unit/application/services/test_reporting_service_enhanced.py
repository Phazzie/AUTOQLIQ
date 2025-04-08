#!/usr/bin/env python3
"""
Enhanced unit tests for ReportingService class in src/application/services/reporting_service.py.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime, timedelta

# Import the module under test
from src.application.services.reporting_service import ReportingService, LOG_DIRECTORY
from src.core.exceptions import AutoQliqError, RepositoryError


class TestReportingService(unittest.TestCase):
    """
    Test cases for the ReportingService class to ensure it follows SOLID, KISS, and DRY principles.
    
    These tests cover the 6 main responsibilities of ReportingService:
    1. Log directory management
    2. Log filename generation
    3. Saving execution logs
    4. Retrieving execution details
    5. Listing past executions
    6. Generating summary reports
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temp directory to use as the log directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_log_dir = LOG_DIRECTORY
        
        # Patch the LOG_DIRECTORY constant to use our temp directory
        patcher = patch('src.application.services.reporting_service.LOG_DIRECTORY', self.temp_dir.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        
        # Create the service
        self.reporting_service = ReportingService()
        
        # Sample execution log data for testing
        self.sample_execution_log = {
            'workflow_name': 'TestWorkflow',
            'start_time_iso': datetime.now().isoformat(),
            'end_time_iso': (datetime.now() + timedelta(seconds=5)).isoformat(),
            'duration_seconds': 5.0,
            'final_status': 'SUCCESS',
            'actions': [
                {'name': 'Action1', 'status': 'SUCCESS', 'duration_seconds': 2.0},
                {'name': 'Action2', 'status': 'SUCCESS', 'duration_seconds': 3.0}
            ]
        }
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_ensure_log_directory(self):
        """Test creating the log directory."""
        # The directory should have been created in setUp
        self.assertTrue(os.path.exists(self.temp_dir.name))
        
        # Test the method directly
        with patch('os.makedirs') as mock_makedirs:
            self.reporting_service._ensure_log_directory()
            mock_makedirs.assert_called_once_with(self.temp_dir.name, exist_ok=True)
        
        # Test error handling
        with patch('os.makedirs', side_effect=OSError("Permission denied")):
            # Should not raise an exception
            self.reporting_service._ensure_log_directory()
    
    def test_generate_filename(self):
        """Test generating a unique filename for a log."""
        # Test with valid execution log
        filename = self.reporting_service._generate_filename(self.sample_execution_log)
        
        # Verify filename format
        self.assertTrue(filename.startswith("exec_TestWorkflow_"))
        self.assertTrue(filename.endswith("_SUCCESS.json"))
        
        # Test with missing keys
        incomplete_log = {'workflow_name': 'IncompleteLog'}
        filename = self.reporting_service._generate_filename(incomplete_log)
        self.assertTrue(filename.startswith("exec_IncompleteLog_"))
        self.assertTrue(filename.endswith("_UNKNOWN.json"))
        
        # Test with special characters in workflow name
        special_log = {
            'workflow_name': 'Test/Workflow:With<Special>Chars',
            'start_time_iso': datetime.now().isoformat(),
            'final_status': 'FAILED'
        }
        filename = self.reporting_service._generate_filename(special_log)
        self.assertTrue(filename.startswith("exec_Test_Workflow_With_Special_Chars_"))
        self.assertTrue(filename.endswith("_FAILED.json"))
    
    def test_log_execution_start(self):
        """Test logging the start of an execution."""
        execution_id = self.reporting_service.log_execution_start("TestWorkflow")
        
        # Verify execution ID format
        self.assertTrue(execution_id.startswith("exec_TestWorkflow_"))
        self.assertTrue(execution_id.endswith("_RUNNING.json"))
    
    def test_save_execution_log(self):
        """Test saving an execution log."""
        # Test with valid execution log
        with patch('builtins.open', mock_open()) as mock_file:
            self.reporting_service.save_execution_log(self.sample_execution_log)
            
            # Verify file was opened for writing
            mock_file.assert_called_once()
            # Get the call arguments
            args, kwargs = mock_file.call_args
            # Verify it's a path in our temp directory
            self.assertTrue(args[0].startswith(self.temp_dir.name))
            self.assertEqual(kwargs['mode'], 'w')
            
            # Verify json.dump was called
            handle = mock_file()
            handle.write.assert_called()
        
        # Test with invalid execution log
        with self.assertRaises(ValueError):
            self.reporting_service.save_execution_log({})
        
        # Test with valid log but file write error
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with self.assertRaises(RepositoryError):
                self.reporting_service.save_execution_log(self.sample_execution_log)
    
    def test_get_execution_details(self):
        """Test retrieving execution details."""
        # Create a test log file
        filename = "exec_TestWorkflow_20230101_120000_000000_SUCCESS.json"
        filepath = os.path.join(self.temp_dir.name, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.sample_execution_log, f)
        
        # Test retrieving valid execution details
        details = self.reporting_service.get_execution_details(filename)
        self.assertEqual(details['workflow_name'], 'TestWorkflow')
        self.assertEqual(details['final_status'], 'SUCCESS')
        
        # Test with non-existent file
        details = self.reporting_service.get_execution_details("exec_NonExistent_20230101_120000_000000_SUCCESS.json")
        self.assertIsNone(details)
        
        # Test with invalid execution ID format
        with self.assertRaises(ValueError):
            self.reporting_service.get_execution_details("invalid_filename.txt")
        
        # Test with file read error
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with self.assertRaises(RepositoryError):
                self.reporting_service.get_execution_details(filename)
        
        # Test with invalid JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("invalid json")
        
        with self.assertRaises(RepositoryError):
            self.reporting_service.get_execution_details(filename)
    
    def test_list_past_executions(self):
        """Test listing past executions."""
        # Create multiple test log files
        for i in range(5):
            workflow_name = "TestWorkflow" if i < 3 else "OtherWorkflow"
            status = "SUCCESS" if i % 2 == 0 else "FAILED"
            
            log_data = {
                'workflow_name': workflow_name,
                'start_time_iso': datetime.now().isoformat(),
                'duration_seconds': float(i),
                'final_status': status
            }
            
            filename = self.reporting_service._generate_filename(log_data)
            filepath = os.path.join(self.temp_dir.name, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_data, f)
        
        # Test listing all executions (limited to default 50)
        executions = self.reporting_service.list_past_executions()
        self.assertEqual(len(executions), 5)
        
        # Test listing with workflow filter
        executions = self.reporting_service.list_past_executions(workflow_name="TestWorkflow")
        self.assertEqual(len(executions), 3)
        for execution in executions:
            self.assertEqual(execution['workflow_name'], 'TestWorkflow')
        
        # Test listing with limit
        executions = self.reporting_service.list_past_executions(limit=2)
        self.assertEqual(len(executions), 2)
        
        # Test with missing log directory
        with patch('os.path.exists', return_value=False):
            executions = self.reporting_service.list_past_executions()
            self.assertEqual(len(executions), 0)
        
        # Test with error in reading a log file
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            # Should skip files with errors
            executions = self.reporting_service.list_past_executions()
            self.assertEqual(len(executions), 0)
        
        # Test with error in listing directory
        with patch('os.listdir', side_effect=OSError("Permission denied")):
            with self.assertRaises(RepositoryError):
                self.reporting_service.list_past_executions()
    
    def test_generate_summary_report(self):
        """Test generating a summary report."""
        # Currently a placeholder, but test the method exists and returns a dict
        report = self.reporting_service.generate_summary_report()
        self.assertIsInstance(report, dict)
        self.assertIn("message", report)

if __name__ == '__main__':
    unittest.main()