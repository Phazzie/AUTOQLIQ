"""Registry base class for UI components.

This module provides a base class for registries of UI components.
"""

from typing import Dict, Any, TypeVar, Generic, Optional, Callable

T = TypeVar('T')


class Registry(Generic[T]):
    """Base class for registries.
    
    This class provides a generic registry for storing and retrieving items.
    
    Attributes:
        _items: Dictionary of registered items
    """
    
    def __init__(self):
        """Initialize a new Registry."""
        self._items: Dict[str, T] = {}
    
    def register(self, key: str, item: T) -> None:
        """Register an item.
        
        Args:
            key: The key for the item
            item: The item to register
        """
        self._items[key] = item
    
    def get(self, key: str) -> Optional[T]:
        """Get an item.
        
        Args:
            key: The key for the item
            
        Returns:
            The item, or None if not registered
        """
        return self._items.get(key)
    
    def create(self, key: str, *args, **kwargs) -> Any:
        """Create an item.
        
        Args:
            key: The key for the item
            *args: Arguments to pass to the item
            **kwargs: Keyword arguments to pass to the item
            
        Returns:
            The created item
            
        Raises:
            ValueError: If the item is not registered
        """
        item = self.get(key)
        if item is None:
            raise ValueError(f"Item not registered: {key}")
        
        if callable(item):
            return item(*args, **kwargs)
        
        return item
    
    def list_keys(self) -> list[str]:
        """List all registered keys.
        
        Returns:
            A list of registered keys
        """
        return list(self._items.keys())
