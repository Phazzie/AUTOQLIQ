"""Tests for component factory."""

import unittest
from unittest.mock import MagicMock

from src.core.workflow.result_processing.interfaces import (
    IStatusAnalyzer, IErrorStatusAnalyzer, IResultStatusAnalyzer,
    ISummaryFormatter, IDetailedReportFormatter, IActionResultFormatter,
    ITimeMetricsCalculator, ILogStructureBuilder, IWorkflowCompletionLogger
)
from src.core.workflow.result_processing.factory import ComponentFactory


class TestComponentFactory(unittest.TestCase):
    """Test cases for component factory."""

    def setUp(self):
        """Set up test fixtures."""
        self._factory = ComponentFactory()

    def test_create_status_analyzer(self):
        """Test creating a status analyzer."""
        component = self._factory.create(IStatusAnalyzer)
        self.assertIsNotNone(component)
        self.assertTrue(isinstance(component, IStatusAnalyzer))

    def test_create_error_status_analyzer(self):
        """Test creating an error status analyzer."""
        component = self._factory.create(IErrorStatusAnalyzer)
        self.assertIsNotNone(component)
        self.assertTrue(isinstance(component, IErrorStatusAnalyzer))

    def test_create_result_status_analyzer(self):
        """Test creating a result status analyzer."""
        component = self._factory.create(IResultStatusAnalyzer)
        self.assertIsNotNone(component)
        self.assertTrue(isinstance(component, IResultStatusAnalyzer))

    def test_create_summary_formatter(self):
        """Test creating a summary formatter."""
        component = self._factory.create(ISummaryFormatter)
        self.assertIsNotNone(component)
        self.assertTrue(isinstance(component, ISummaryFormatter))

    def test_create_detailed_report_formatter(self):
        """Test creating a detailed report formatter."""
        component = self._factory.create(IDetailedReportFormatter)
        self.assertIsNotNone(component)
        self.assertTrue(isinstance(component, IDetailedReportFormatter))

    def test_create_action_result_formatter(self):
        """Test creating an action result formatter."""
        component = self._factory.create(IActionResultFormatter)
        self.assertIsNotNone(component)
        self.assertTrue(isinstance(component, IActionResultFormatter))

    def test_create_time_metrics_calculator(self):
        """Test creating a time metrics calculator."""
        component = self._factory.create(ITimeMetricsCalculator)
        self.assertIsNotNone(component)
        self.assertTrue(isinstance(component, ITimeMetricsCalculator))

    def test_create_log_structure_builder(self):
        """Test creating a log structure builder."""
        component = self._factory.create(ILogStructureBuilder)
        self.assertIsNotNone(component)
        self.assertTrue(isinstance(component, ILogStructureBuilder))

    def test_create_workflow_completion_logger(self):
        """Test creating a workflow completion logger."""
        component = self._factory.create(IWorkflowCompletionLogger)
        self.assertIsNotNone(component)
        self.assertTrue(isinstance(component, IWorkflowCompletionLogger))

    def test_create_with_unknown_type(self):
        """Test creating a component with an unknown type."""
        # Create a mock interface
        mock_interface = MagicMock()
        
        # Attempt to create a component with the mock interface
        with self.assertRaises(ValueError):
            self._factory.create(mock_interface)


if __name__ == "__main__":
    unittest.main()
