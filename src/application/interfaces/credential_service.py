"""Credential service interface for AutoQliq.

DEPRECATED: Use src.core.interfaces.service.ICredentialService instead.
This module remains for backward compatibility.
"""
import warnings

# Re-export from the new location
from src.core.interfaces.service import ICredentialService

__all__ = ["ICredentialService"]

warnings.warn(
    "Importing ICredentialService from src.application.interfaces.credential_service is deprecated. "
    "Import from src.core.interfaces.service instead.",
    DeprecationWarning,
    stacklevel=2
)