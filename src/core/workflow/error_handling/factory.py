"""Factory for creating error handling strategies.

This module provides a factory for creating error handling strategies.
"""

import logging
from typing import Dict, Any

from src.core.workflow.error_handling.base import ErrorHandlingStrategyBase
from src.core.workflow.error_handling.stop_strategy import StopOnErrorStrategy
from src.core.workflow.error_handling.continue_strategy import ContinueOnErrorStrategy
from src.core.workflow.error_handling.retry_strategy import RetryOnErrorStrategy

logger = logging.getLogger(__name__)


def create_error_handling_strategy(strategy_type: str, **kwargs) -> ErrorHandlingStrategyBase:
    """
    Create an error handling strategy based on the specified type.
    
    Args:
        strategy_type: Type of strategy to create ('stop', 'continue', 'retry')
        **kwargs: Additional arguments for the strategy
        
    Returns:
        An instance of the appropriate ErrorHandlingStrategyBase subclass
        
    Raises:
        ValueError: If strategy_type is not recognized
    """
    if strategy_type.lower() == 'stop':
        return StopOnErrorStrategy()
    elif strategy_type.lower() == 'continue':
        return ContinueOnErrorStrategy()
    elif strategy_type.lower() == 'retry':
        max_retries = kwargs.get('max_retries', 3)
        retry_delay = kwargs.get('retry_delay_seconds', 1.0)
        fallback_type = kwargs.get('fallback_strategy', 'stop')
        
        # Create fallback strategy
        if fallback_type == 'continue':
            fallback = ContinueOnErrorStrategy()
        else:
            fallback = StopOnErrorStrategy()
            
        return RetryOnErrorStrategy(max_retries, retry_delay, fallback)
    else:
        raise ValueError(f"Unknown error handling strategy type: {strategy_type}")
