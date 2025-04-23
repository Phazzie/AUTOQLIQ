"""DEPRECATED: Old repository implementations for AutoQliq.

This package contains deprecated repository implementations that are scheduled
for removal in a future release. Use the new implementations in
src/infrastructure/repositories/ instead.
"""

import warnings

def _deprecated(name):
    warnings.warn(
        f"{name} is deprecated. Use the new implementations in src.infrastructure.repositories instead.",
        DeprecationWarning,
        stacklevel=2
    )

# We'll add imports for the old implementations here as we move them
# For now, this file serves as a placeholder

__all__ = []  # We'll add exports for the old implementations here as we move them
