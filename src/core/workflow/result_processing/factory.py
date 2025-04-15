"""Factory for result processing components.

This module provides a factory for creating result processing components.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Type, TypeVar

from src.core.workflow.result_processing.interfaces import (
    IFactory, IStatusAnalyzer, IResultFormatter, ITimeMetricsCalculator,
    ILogStructureBuilder, IWorkflowCompletionLogger,
    IErrorStatusAnalyzer, IResultStatusAnalyzer,
    ISummaryFormatter, IDetailedReportFormatter, IActionResultFormatter
)
from src.core.workflow.result_processing.status_analyzer import StatusAnalyzer
from src.core.workflow.result_processing.error_status_analyzer import ErrorStatusAnalyzer
from src.core.workflow.result_processing.result_status_analyzer import ResultStatusAnalyzer
from src.core.workflow.result_processing.formatter import ResultFormatter
from src.core.workflow.result_processing.summary_formatter import SummaryFormatter
from src.core.workflow.result_processing.detailed_report_formatter import DetailedReportFormatter
from src.core.workflow.result_processing.action_result_formatter import ActionResultFormatter
from src.core.workflow.result_processing.time_metrics_calculator import TimeMetricsCalculator
from src.core.workflow.result_processing.log_structure_builder import LogStructureBuilder
from src.core.workflow.result_processing.workflow_completion_logger import WorkflowCompletionLogger

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ComponentFactory(IFactory):
    """Factory for creating result processing components."""
    
    def __init__(self):
        """Initialize the component factory."""
        self._component_registry = {
            IStatusAnalyzer: StatusAnalyzer,
            IErrorStatusAnalyzer: ErrorStatusAnalyzer,
            IResultStatusAnalyzer: ResultStatusAnalyzer,
            IResultFormatter: ResultFormatter,
            ISummaryFormatter: SummaryFormatter,
            IDetailedReportFormatter: DetailedReportFormatter,
            IActionResultFormatter: ActionResultFormatter,
            ITimeMetricsCalculator: TimeMetricsCalculator,
            ILogStructureBuilder: LogStructureBuilder,
            IWorkflowCompletionLogger: WorkflowCompletionLogger
        }
    
    def create(self, component_type: Type[T], **kwargs) -> T:
        """
        Create a component of the specified type.
        
        Args:
            component_type: The type of component to create
            **kwargs: Additional arguments for component creation
            
        Returns:
            T: An instance of the specified component type
            
        Raises:
            ValueError: If the component type is unknown
        """
        if component_type not in self._component_registry:
            raise ValueError(f"Unknown component type: {component_type}")
        
        component_class = self._component_registry[component_type]
        return component_class(**kwargs)
