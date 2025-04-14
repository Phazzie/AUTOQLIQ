"""Credential entity module for AutoQliq.

This module provides the Credential entity class for storing login credentials.
"""

from typing import Dict, Any, Optional
import json

from src.core.interfaces.entity_interfaces import ICredential
from src.core.exceptions import ValidationError


class Credential(ICredential):
    """
    Represents a set of login credentials for a website or service.

    Attributes:
        name: A unique identifier for this credential set
        username: The username or email for login
        password: The password for login
    """

    def __init__(self, name: str, username: str, password: str):
        """
        Initialize a new Credential instance.

        Args:
            name: A unique identifier for this credential set
            username: The username or email for login
            password: The password for login

        Raises:
            ValidationError: If any of the required fields are empty
        """
        self._name = name
        self._username = username
        self._password = password
        self.validate()

    @property
    def name(self) -> str:
        """Get the name of the credential."""
        return self._name

    @property
    def username(self) -> str:
        """Get the username of the credential."""
        return self._username

    @property
    def password(self) -> str:
        """Get the password of the credential."""
        return self._password

    def validate(self) -> bool:
        """
        Validate the credential data.
        
        Returns:
            True if validation passes.
            
        Raises:
            ValidationError: If validation fails.
        """
        if not self._name:
            raise ValidationError("Credential name cannot be empty")
        if not self._username:
            raise ValidationError("Username cannot be empty")
        if not self._password:
            raise ValidationError("Password cannot be empty")
        return True

    def to_dict(self) -> Dict[str, str]:
        """
        Convert the credential to a dictionary representation.
        
        Returns:
            A dictionary containing the credential's data.
        """
        return {
            "name": self._name,
            "username": self._username,
            "password": self._password
        }

    def to_json(self) -> str:
        """
        Serialize the credential to a JSON string.
        
        Returns:
            A JSON string representing the credential.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Credential':
        """
        Create a Credential instance from a dictionary.

        Args:
            data: A dictionary containing credential data

        Returns:
            A new Credential instance
            
        Raises:
            ValidationError: If required data is missing or invalid.
        """
        name = data.get('name', '')
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not name or not username or not password:
            missing = []
            if not name:
                missing.append('name')
            if not username:
                missing.append('username')
            if not password:
                missing.append('password')
            raise ValidationError(f"Credential data missing required fields: {', '.join(missing)}")
        
        return cls(
            name=name,
            username=username,
            password=password
        )

    @classmethod
    def from_json(cls, json_data: str) -> 'Credential':
        """
        Create a Credential instance from a JSON string.

        Args:
            json_data: A JSON string containing credential data

        Returns:
            A new Credential instance
        """
        data = json.loads(json_data)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """Return a string representation with masked password."""
        return f"Credential(name='{self._name}', username='{self._username}', password='********')"
        
    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"Credential(name='{self._name}', username='{self._username}', password='********')"
