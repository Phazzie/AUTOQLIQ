"""Actions package initialization for AutoQliq.

This package contains all action-related components, including base classes,
specific action implementations, factories, and serialization logic.

Exports:
    ActionBase: Abstract base class for all actions.
    NavigateAction: Action for navigating to a URL.
    ClickAction: Action for clicking an element.
    TypeAction: Action for typing text into an element.
    WaitAction: Action for pausing execution.
    ScreenshotAction: Action for taking a screenshot.
    ActionFactory: Factory for creating action instances.
"""

from .base import ActionBase
from .navigation import NavigateAction
from .interaction import ClickAction, TypeAction
from .utility import WaitAction, ScreenshotAction
from .factory import ActionFactory

__all__ = [
    "ActionBase",
    "NavigateAction",
    "ClickAction",
    "TypeAction",
    "WaitAction",
    "ScreenshotAction",
    "ActionFactory",
]
```

```text