"""Playwright WebDriver implementation for AutoQliq.

This module is maintained for backward compatibility with existing code that
imports PlaywrightDriver directly from this location. It simply re-exports
the PlaywrightDriver class from its new location in the package structure.

New code should import from src.infrastructure.webdrivers.playwright instead.

This approach allows us to refactor the implementation into a more modular
structure without breaking existing code that depends on the old import path.
"""

# Re-export the PlaywrightDriver from the new package structure
# This maintains backward compatibility while allowing the implementation
# to be properly organized in a package with specialized handler classes
from src.infrastructure.webdrivers.playwright import PlaywrightDriver

# Define what symbols are exported when using 'from module import *'
__all__ = ['PlaywrightDriver']
