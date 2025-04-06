"""Registry for UI component types.

This module provides a registry for UI component types, allowing dynamic component creation.
"""

from typing import Callable, Any, TypeVar, Optional

from src.ui.common.registry import Registry

T = TypeVar('T')

class ComponentRegistry(Registry[Callable[..., T]]):
    """Registry for UI component types.

    This class provides a registry for UI component types, allowing dynamic component creation.
    """

    def get_factory(self, component_type: str) -> Optional[Callable[..., T]]:
        """Get a component factory.

        Args:
            component_type: The type of the component

        Returns:
            The factory function, or None if not registered
        """
        return self.get(component_type)

    def list_component_types(self) -> list[str]:
        """List all registered component types.

        Returns:
            A list of registered component types
        """
        return self.list_keys()
