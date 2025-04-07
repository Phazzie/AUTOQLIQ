"""Actions package initialization for AutoQliq.

This package contains all action-related components, including base classes,
specific action implementations, factories, and serialization logic.
"""

from .base import ActionBase
from .navigation import NavigateAction
from .interaction import ClickAction, TypeAction
from .utility import WaitAction, ScreenshotAction
from .conditional_action import ConditionalAction
from .loop_action import LoopAction
from .error_handling_action import ErrorHandlingAction
from .template_action import TemplateAction
from .factory import ActionFactory

__all__ = [
    "ActionBase",
    "NavigateAction",
    "ClickAction",
    "TypeAction",
    "WaitAction",
    "ScreenshotAction",
    "ConditionalAction",
    "LoopAction",
    "ErrorHandlingAction",
    "TemplateAction",
    "ActionFactory",
]