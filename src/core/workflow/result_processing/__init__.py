"""Result processing package for AutoQliq workflows.

This package provides result processing components for the WorkflowRunner.
"""

# Main components
from src.core.workflow.result_processing.processor import ResultProcessor
from src.core.workflow.result_processing.formatter import ResultFormatter
from src.core.workflow.result_processing.status_analyzer import StatusAnalyzer

# Status analysis components
from src.core.workflow.result_processing.error_status_analyzer import ErrorStatusAnalyzer
from src.core.workflow.result_processing.result_status_analyzer import ResultStatusAnalyzer

# Formatting components
from src.core.workflow.result_processing.summary_formatter import SummaryFormatter
from src.core.workflow.result_processing.detailed_report_formatter import DetailedReportFormatter
from src.core.workflow.result_processing.action_result_formatter import ActionResultFormatter

# Processing components
from src.core.workflow.result_processing.time_metrics_calculator import TimeMetricsCalculator
from src.core.workflow.result_processing.log_structure_builder import LogStructureBuilder
from src.core.workflow.result_processing.workflow_completion_logger import WorkflowCompletionLogger

# Sensitive data filtering components
from src.core.workflow.result_processing.sensitive_data_filter import SensitiveDataFilter
from src.core.workflow.result_processing.sensitive_key_detector import SensitiveKeyDetector
from src.core.workflow.result_processing.dictionary_filter import DictionaryFilter
from src.core.workflow.result_processing.list_filter import ListFilter

__all__ = [
    # Main components
    'ResultProcessor',
    'ResultFormatter',
    'StatusAnalyzer',

    # Status analysis components
    'ErrorStatusAnalyzer',
    'ResultStatusAnalyzer',

    # Formatting components
    'SummaryFormatter',
    'DetailedReportFormatter',
    'ActionResultFormatter',

    # Processing components
    'TimeMetricsCalculator',
    'LogStructureBuilder',
    'WorkflowCompletionLogger',

    # Sensitive data filtering components
    'SensitiveDataFilter',
    'SensitiveKeyDetector',
    'DictionaryFilter',
    'ListFilter',
]
