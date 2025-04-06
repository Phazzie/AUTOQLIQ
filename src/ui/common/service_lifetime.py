"""Service lifetime definitions for dependency injection.

This module provides definitions for service lifetimes in dependency injection.
"""

from enum import Enum, auto


class ServiceLifetime(Enum):
    """Enum for service lifetimes.
    
    SINGLETON: The service is created once and reused
    TRANSIENT: The service is created each time it is requested
    SCOPED: The service is created once per scope
    """
    SINGLETON = auto()
    TRANSIENT = auto()
    SCOPED = auto()
