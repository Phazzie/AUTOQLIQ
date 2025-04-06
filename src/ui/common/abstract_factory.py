"""Abstract factory for UI components.

This module provides an abstract factory base class for UI component factories.
"""

import abc
import functools
from typing import TypeVar, Generic, Type, Any, Dict, Optional, Callable

from src.core.exceptions import UIError
from src.ui.common.service_provider import ServiceProvider
from src.ui.common.component_registry import ComponentRegistry

T = TypeVar('T')


def factory_method(component_type: str):
    """Decorator for marking factory methods.

    Args:
        component_type: The type of component this factory method creates

    Returns:
        A decorator function
    """
    def decorator(func):
        func._factory_component_type = component_type
        return func
    return decorator


def factory_error_handler(operation: str, component_name: str):
    """Decorator for handling errors in factory methods.

    Args:
        operation: The operation being performed
        component_name: The name of the component

    Returns:
        A decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            return self._handle_factory_error(operation, component_name, func, self, *args, **kwargs)
        return wrapper
    return decorator


class AbstractFactory(Generic[T], abc.ABC):
    """Abstract factory for UI components.

    This class provides a base class for all UI component factories, ensuring
    consistent behavior and dependency management.

    Attributes:
        service_provider: The service provider for dependency injection
        registry: The component registry for dynamic component creation
    """

    def __init__(
        self,
        service_provider: Optional[ServiceProvider] = None,
        registry: Optional[ComponentRegistry] = None
    ):
        """Initialize a new AbstractFactory.

        Args:
            service_provider: The service provider for dependency injection
            registry: The component registry for dynamic component creation
        """
        self.service_provider = service_provider or ServiceProvider()
        self.registry = registry or ComponentRegistry()

        # Register factories
        self._register_factories()

    def _handle_factory_error(self, operation: str, component_name: str, func: Callable, *args, **kwargs) -> Any:
        """Handle errors in factory methods.

        Args:
            operation: The operation being performed
            component_name: The name of the component
            func: The function to execute
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function

        Raises:
            UIError: If the function raises an exception
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Failed to {operation}"
            raise UIError(error_msg, component_name=component_name, cause=e)

    def _register_factories(self) -> None:
        """Register factories in the registry.

        This method scans the class for methods decorated with @factory_method
        and registers them in the registry.
        """
        import inspect
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, '_factory_component_type'):
                self.register_factory(method._factory_component_type, method)

    def create(self, component_type: str, **kwargs) -> T:
        """Create a component by type.

        Args:
            component_type: The type of component to create
            **kwargs: Arguments to pass to the factory method

        Returns:
            The created component

        Raises:
            ValueError: If the component type is not registered
        """
        return self.registry.create(component_type, **kwargs)

    def get_service(self, service_type: Type) -> Any:
        """Get a service from the service provider.

        Args:
            service_type: The type of service to get

        Returns:
            The service instance

        Raises:
            ValueError: If the service is not registered
        """
        return self.service_provider.require(service_type)

    def register_service(self, service_type: Type, instance: Any) -> None:
        """Register a service in the service provider.

        Args:
            service_type: The type of service to register
            instance: The service instance
        """
        self.service_provider.register(service_type, instance)

    def register_factory(self, component_type: str, factory_method: Any) -> None:
        """Register a factory method in the registry.

        Args:
            component_type: The type of component to register
            factory_method: The factory method for creating the component
        """
        self.registry.register(component_type, factory_method)
