from src.config import config
from src.core.interfaces.repository_interfaces import IWorkflowRepository, ICredentialRepository
from src.infrastructure.persistence.workflow_fs_repository import FileSystemWorkflowRepository
from src.infrastructure.persistence.credential_fs_repository import FileSystemCredentialRepository

class RepositoryFactory:
    """Factory to create repository instances based on configuration."""
    def create_workflow_repository(self) -> IWorkflowRepository:
        repo_type = config.repository_type
        if repo_type == 'file_system':
            return FileSystemWorkflowRepository(
                path=config.workflows_path,
                create_if_missing=config.repo_create_if_missing
            )
        else:
            raise NotImplementedError(f"Repository type '{repo_type}' not supported for workflows.")

    def create_credential_repository(self) -> ICredentialRepository:
        repo_type = config.repository_type
        if repo_type == 'file_system':
            return FileSystemCredentialRepository(
                path=config.credentials_path,
                create_if_missing=config.repo_create_if_missing
            )
        else:
            raise NotImplementedError(f"Repository type '{repo_type}' not supported for credentials.")