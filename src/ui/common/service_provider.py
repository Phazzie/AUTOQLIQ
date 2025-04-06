"""Service provider for UI components.

This module provides a simple dependency injection container for UI components.
"""

import inspect
from typing import Dict, Any, Type, Optional, TypeVar, Generic, cast, Callable

from src.ui.common.service_lifetime import ServiceLifetime

T = TypeVar('T')

class ServiceProvider:
    """Service provider for UI components.

    This class provides a simple dependency injection container for UI components.
    It allows registering and retrieving service instances by their type.

    Attributes:
        _services: Dictionary of registered service instances
        _factories: Dictionary of registered service factories
        _instances: Dictionary of singleton instances
        _lifetimes: Dictionary of service lifetimes
    """

    def __init__(self):
        """Initialize a new ServiceProvider."""
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        self._instances: Dict[Type, Any] = {}
        self._lifetimes: Dict[Type, ServiceLifetime] = {}

    def register(self, service_type: Type[T], instance: Optional[T] = None,
                factory: Optional[Callable[[], T]] = None,
                lifetime: ServiceLifetime = ServiceLifetime.SINGLETON) -> None:
        """Register a service.

        Args:
            service_type: The type of the service
            instance: The service instance
            factory: A factory function for creating the service
            lifetime: The lifetime of the service
        """
        self._services[service_type] = instance
        self._factories[service_type] = factory
        self._lifetimes[service_type] = lifetime

    def get(self, service_type: Type[T]) -> Optional[T]:
        """Get a service instance.

        Args:
            service_type: The type of the service

        Returns:
            The service instance, or None if not registered
        """
        # Check for singleton instance
        if service_type in self._instances:
            return cast(T, self._instances[service_type])

        # Check for direct instance
        if service_type in self._services and self._services[service_type] is not None:
            instance = self._services[service_type]
            if self._lifetimes.get(service_type) == ServiceLifetime.SINGLETON:
                self._instances[service_type] = instance
            return cast(T, instance)

        # Check for factory
        if service_type in self._factories and self._factories[service_type] is not None:
            factory = self._factories[service_type]
            instance = factory()
            if self._lifetimes.get(service_type) == ServiceLifetime.SINGLETON:
                self._instances[service_type] = instance
            return cast(T, instance)

        return None

    def require(self, service_type: Type[T]) -> T:
        """Get a required service instance.

        Args:
            service_type: The type of the service

        Returns:
            The service instance

        Raises:
            ValueError: If the service is not registered
        """
        service = self.get(service_type)
        if service is None:
            raise ValueError(f"Service not registered: {service_type.__name__}")
        return service

    def resolve_dependencies(self, func: Callable) -> Dict[str, Any]:
        """Resolve dependencies for a function.

        Args:
            func: The function to resolve dependencies for

        Returns:
            A dictionary of parameter names and resolved dependencies
        """
        sig = inspect.signature(func)
        args = {}

        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                service = self.get(param.annotation)
                if service is not None:
                    args[param_name] = service

        return args
