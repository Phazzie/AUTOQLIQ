"""Result processing package for AutoQliq workflows.

This package provides result processing components for the WorkflowRunner.
"""

from src.core.workflow.result_processing.processor import ResultProcessor
from src.core.workflow.result_processing.formatter import ResultFormatter
from src.core.workflow.result_processing.status_analyzer import StatusAnalyzer

__all__ = [
    'ResultProcessor',
    'ResultFormatter',
    'StatusAnalyzer',
]
