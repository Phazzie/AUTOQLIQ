"""Component factory registry for UI components.

This module provides a registry for component factories, allowing dynamic factory creation.
"""

from typing import Type, Optional, TypeVar

from src.ui.common.abstract_factory import AbstractFactory
from src.ui.common.service_provider import ServiceProvider
from src.ui.common.registry import Registry

T = TypeVar('T', bound=AbstractFactory)


class ComponentFactoryRegistry(Registry[Type[T]]):
    """Registry for component factories.

    This class provides a registry for component factories, allowing dynamic factory creation.

    Attributes:
        service_provider: The service provider for dependency injection
    """

    def __init__(self, service_provider: Optional[ServiceProvider] = None):
        """Initialize a new ComponentFactoryRegistry.

        Args:
            service_provider: The service provider for dependency injection
        """
        super().__init__()
        self.service_provider = service_provider or ServiceProvider()

    def create(self, factory_type: str, **kwargs) -> T:
        """Create a factory by type.

        Args:
            factory_type: The type of factory to create
            **kwargs: Arguments to pass to the factory constructor

        Returns:
            The created factory

        Raises:
            ValueError: If the factory type is not registered
        """
        factory_class = self.get(factory_type)
        if factory_class is None:
            raise ValueError(f"Factory type not registered: {factory_type}")

        # Create the factory with the service provider
        return factory_class(service_provider=self.service_provider, **kwargs)

    def get_factory_class(self, factory_type: str) -> Optional[Type[T]]:
        """Get a factory class by type.

        Args:
            factory_type: The type of factory to get

        Returns:
            The factory class, or None if not registered
        """
        return self.get(factory_type)

    def list_factory_types(self) -> list[str]:
        """List all registered factory types.

        Returns:
            A list of registered factory types
        """
        return self.list_keys()
