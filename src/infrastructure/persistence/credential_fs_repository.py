from typing import List, Optional
import os
import json
import logging

from src.core.interfaces.repository_interfaces import ICredentialRepository
from src.core.credentials import Credential
from src.core.exceptions import RepositoryError, ValidationError

logger = logging.getLogger(__name__)

class FileSystemCredentialRepository(ICredentialRepository):
    """Filesystem-based repository for Credential entities."""
    def __init__(self, path: str, create_if_missing: bool = True):
        self.path = path
        if create_if_missing:
            dir_ = os.path.dirname(self.path)
            if dir_ and not os.path.exists(dir_):
                try:
                    os.makedirs(dir_, exist_ok=True)
                    logger.info(f"Created credentials directory: {dir_}")
                except Exception as e:
                    logger.error(f"Failed to create credentials dir: {e}")
                    raise RepositoryError("Cannot initialize credential repository", cause=e)
        if not os.path.exists(self.path):
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def save(self, credentials: Credential) -> None:
        try:
            data = self.list()
            # remove existing by name
            data = [c for c in data if c.name != credentials.name]
            data.append(credentials.to_dict())
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved credential: {credentials.name}")
        except (ValidationError, RepositoryError):
            raise
        except Exception as e:
            logger.error(f"Error saving credential {credentials.name}: {e}")
            raise RepositoryError("Save failed", repository_name="CredentialRepository", entity_id=credentials.name, cause=e)

    def get(self, name: str) -> Optional[Credential]:
        try:
            for c in self.list():
                if c.name == name:
                    return c
            return None
        except Exception as e:
            logger.error(f"Error retrieving credential {name}: {e}")
            raise RepositoryError("Get failed", repository_name="CredentialRepository", entity_id=name, cause=e)

    def list(self) -> List[Credential]:
        creds = []
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                items = json.load(f)
            for data in items:
                try:
                    creds.append(Credential.from_dict(data))
                except ValidationError as ve:
                    logger.warning(f"Invalid credential data skipped: {ve}")
            return creds
        except Exception as e:
            logger.error(f"Error listing credentials: {e}")
            raise RepositoryError("List failed", repository_name="CredentialRepository", cause=e)

    def delete(self, name: str) -> None:
        try:
            data = [c.to_dict() for c in self.list() if c.name != name]
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Deleted credential: {name}")
        except Exception as e:
            logger.error(f"Error deleting credential {name}: {e}")
            raise RepositoryError("Delete failed", repository_name="CredentialRepository", entity_id=name, cause=e)
