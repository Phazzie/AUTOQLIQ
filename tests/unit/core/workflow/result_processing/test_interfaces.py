"""Tests for result processing interfaces."""

import unittest
from unittest.mock import MagicMock

from src.core.action_result import ActionResult
from src.core.workflow.result_processing.interfaces import (
    IStatusAnalyzer, IErrorStatusAnalyzer, IResultStatusAnalyzer,
    ISummaryFormatter, IDetailedReportFormatter, IActionResultFormatter,
    ITimeMetricsCalculator, ILogStructureBuilder, IWorkflowCompletionLogger
)


class TestInterfaces(unittest.TestCase):
    """Test cases for result processing interfaces."""

    def test_status_analyzer_interface(self):
        """Test IStatusAnalyzer interface."""
        # Create a mock that implements the interface
        mock_analyzer = MagicMock(spec=IStatusAnalyzer)
        
        # Set up return value
        mock_analyzer.determine_status.return_value = ("SUCCESS", None, "All actions completed successfully")
        
        # Call the method
        status, error_message, summary = mock_analyzer.determine_status([], None)
        
        # Verify the result
        self.assertEqual(status, "SUCCESS")
        self.assertIsNone(error_message)
        self.assertEqual(summary, "All actions completed successfully")
        
        # Verify the mock was called
        mock_analyzer.determine_status.assert_called_once_with([], None)

    def test_error_status_analyzer_interface(self):
        """Test IErrorStatusAnalyzer interface."""
        # Create a mock that implements the interface
        mock_analyzer = MagicMock(spec=IErrorStatusAnalyzer)
        
        # Set up return value
        mock_analyzer.analyze_error.return_value = ("FAILED", "Error message", "Error summary")
        
        # Call the method
        status, error_message, summary = mock_analyzer.analyze_error(Exception("Test error"))
        
        # Verify the result
        self.assertEqual(status, "FAILED")
        self.assertEqual(error_message, "Error message")
        self.assertEqual(summary, "Error summary")
        
        # Verify the mock was called
        mock_analyzer.analyze_error.assert_called_once()

    def test_result_status_analyzer_interface(self):
        """Test IResultStatusAnalyzer interface."""
        # Create a mock that implements the interface
        mock_analyzer = MagicMock(spec=IResultStatusAnalyzer)
        
        # Set up return value
        mock_analyzer.analyze_results.return_value = ("SUCCESS", None, "All actions completed successfully")
        
        # Call the method
        status, error_message, summary = mock_analyzer.analyze_results([])
        
        # Verify the result
        self.assertEqual(status, "SUCCESS")
        self.assertIsNone(error_message)
        self.assertEqual(summary, "All actions completed successfully")
        
        # Verify the mock was called
        mock_analyzer.analyze_results.assert_called_once_with([])

    def test_summary_formatter_interface(self):
        """Test ISummaryFormatter interface."""
        # Create a mock that implements the interface
        mock_formatter = MagicMock(spec=ISummaryFormatter)
        
        # Set up return value
        mock_formatter.format_summary.return_value = "Workflow summary"
        
        # Call the method
        summary = mock_formatter.format_summary({})
        
        # Verify the result
        self.assertEqual(summary, "Workflow summary")
        
        # Verify the mock was called
        mock_formatter.format_summary.assert_called_once_with({})

    def test_detailed_report_formatter_interface(self):
        """Test IDetailedReportFormatter interface."""
        # Create a mock that implements the interface
        mock_formatter = MagicMock(spec=IDetailedReportFormatter)
        
        # Set up return value
        mock_formatter.format_detailed_report.return_value = "Detailed report"
        
        # Call the method
        report = mock_formatter.format_detailed_report({})
        
        # Verify the result
        self.assertEqual(report, "Detailed report")
        
        # Verify the mock was called
        mock_formatter.format_detailed_report.assert_called_once_with({})

    def test_action_result_formatter_interface(self):
        """Test IActionResultFormatter interface."""
        # Create a mock that implements the interface
        mock_formatter = MagicMock(spec=IActionResultFormatter)
        
        # Set up return value
        mock_formatter.format_action_results.return_value = [{"status": "success"}]
        
        # Call the method
        results = mock_formatter.format_action_results([])
        
        # Verify the result
        self.assertEqual(results, [{"status": "success"}])
        
        # Verify the mock was called
        mock_formatter.format_action_results.assert_called_once_with([])

    def test_time_metrics_calculator_interface(self):
        """Test ITimeMetricsCalculator interface."""
        # Create a mock that implements the interface
        mock_calculator = MagicMock(spec=ITimeMetricsCalculator)
        
        # Set up return value
        mock_calculator.calculate_time_metrics.return_value = {"duration": 10.0}
        
        # Call the method
        metrics = mock_calculator.calculate_time_metrics(0.0)
        
        # Verify the result
        self.assertEqual(metrics, {"duration": 10.0})
        
        # Verify the mock was called
        mock_calculator.calculate_time_metrics.assert_called_once_with(0.0)

    def test_log_structure_builder_interface(self):
        """Test ILogStructureBuilder interface."""
        # Create a mock that implements the interface
        mock_builder = MagicMock(spec=ILogStructureBuilder)
        
        # Set up return value
        mock_builder.create_log_structure.return_value = {"status": "SUCCESS"}
        
        # Call the method
        log = mock_builder.create_log_structure(
            "workflow", {}, "SUCCESS", None, "summary", "strategy", []
        )
        
        # Verify the result
        self.assertEqual(log, {"status": "SUCCESS"})
        
        # Verify the mock was called
        mock_builder.create_log_structure.assert_called_once()

    def test_workflow_completion_logger_interface(self):
        """Test IWorkflowCompletionLogger interface."""
        # Create a mock that implements the interface
        mock_logger = MagicMock(spec=IWorkflowCompletionLogger)
        
        # Call the method
        mock_logger.log_workflow_completion("workflow", "SUCCESS", None)
        
        # Verify the mock was called
        mock_logger.log_workflow_completion.assert_called_once_with("workflow", "SUCCESS", None)


if __name__ == "__main__":
    unittest.main()
