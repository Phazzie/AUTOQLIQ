from dataclasses import dataclass, asdict
import json
from typing import Dict, Any

@dataclass
class Credential:
    """Represents a set of login credentials for a website or service.

    Attributes:
        name: A unique identifier for this credential set
        username: The username or email for login
        password: The password for login
    """
    name: str
    username: str
    password: str

    def __post_init__(self):
        """Validate the credential data after initialization."""
        if not self.name:
            raise ValueError("Credential name cannot be empty")
        if not self.username:
            raise ValueError("Username cannot be empty")
        if not self.password:
            raise ValueError("Password cannot be empty")

    def __str__(self) -> str:
        """Return a string representation with masked password."""
        return f"Credential(name='{self.name}', username='{self.username}', password='********')"

    def to_json(self) -> str:
        """Serialize the credential to a JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Credential':
        """Create a Credential instance from a dictionary.

        Args:
            data: A dictionary containing credential data

        Returns:
            A new Credential instance
        """
        return cls(
            name=data.get('name', ''),
            username=data.get('username', ''),
            password=data.get('password', '')
        )

    @classmethod
    def from_json(cls, json_data: str) -> 'Credential':
        """Create a Credential instance from a JSON string.

        Args:
            json_data: A JSON string containing credential data

        Returns:
            A new Credential instance
        """
        data = json.loads(json_data)
        return cls.from_dict(data)
