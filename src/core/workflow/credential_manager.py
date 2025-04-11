"""Credential Management module for AutoQliq workflows.

This module provides mechanisms for securely handling and retrieving
credentials needed during workflow execution (e.g., by TypeAction).

Note: This is currently a placeholder. A concrete implementation would
typically involve integrating with secure storage solutions (like environment
variables, key vaults, password managers, or encrypted files) via the
ICredentialRepository interface.
"""

import logging
from abc import ABC, abstractmethod

# Assuming ICredentialRepository and CredentialError are defined
from src.core.interfaces import ICredentialRepository
from src.core.exceptions import CredentialError

logger = logging.getLogger(__name__)


class CredentialManager(ICredentialRepository, ABC):
    """
    Abstract base class for credential managers.

    Defines the contract for retrieving credentials, fulfilling the
    ICredentialRepository interface. Concrete implementations will
    handle the specifics of storing and accessing credentials securely.
    """

    @abstractmethod
    def get_credential(self, key: str) -> str:
        """
        Retrieve a credential value associated with the given key.

        Args:
            key (str): The unique identifier for the credential.

        Returns:
            str: The credential value.

        Raises:
            CredentialError: If the credential key is not found or access fails.
            NotImplementedError: If called on the abstract class itself.
        """
        pass

    def add_credential(self, key: str, value: str) -> None:
        """
        Add or update a credential (Optional method).

        Args:
            key (str): The unique identifier for the credential.
            value (str): The credential value to store.

        Raises:
            NotImplementedError: By default, indicating storage is not supported
                                 or handled by this specific implementation.
            CredentialError: If adding the credential fails.
        """
        logger.warning(f"Method 'add_credential' not implemented in {self.__class__.__name__}")
        raise NotImplementedError("Adding credentials is not supported by this manager.")

# Example concrete implementation (In-Memory - NOT FOR PRODUCTION)
class InMemoryCredentialManager(CredentialManager):
    """
    Simple in-memory credential manager (for testing/development only).

    WARNING: Stores credentials in plain text in memory. Do not use for
             sensitive production data.
    """
    def __init__(self, credentials: dict[str, str] | None = None):
        self._store = credentials or {}
        logger.warning("Initialized InMemoryCredentialManager. Use only for testing.")

    def get_credential(self, key: str) -> str:
        """Retrieve credential from the in-memory dictionary."""
        if key in self._store:
            logger.debug(f"Retrieved credential for key '{key}' from in-memory store.")
            # Return a copy to prevent modification? Depends on use case.
            return self._store[key]
        else:
            logger.error(f"Credential key '{key}' not found in in-memory store.")
            raise CredentialError(f"Credential key '{key}' not found.")

    def add_credential(self, key: str, value: str) -> None:
        """Add credential to the in-memory dictionary."""
        if not isinstance(key, str) or not key:
             raise ValueError("Credential key must be a non-empty string.")
        if not isinstance(value, str):
             raise ValueError("Credential value must be a string.")
        logger.debug(f"Adding/updating credential for key '{key}' in in-memory store.")
        self._store[key] = value

