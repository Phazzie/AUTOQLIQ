# Repository Implementations

This directory contains implementations of the repository interfaces defined in `src/core/interfaces/repository/`.

## Directory Structure

- `base/`: Base classes for repository implementations
  - `repository.py`: Base implementation of `IBaseRepository`
  - `file_system_repository.py`: Base implementation for file system repositories
  - `database_repository.py`: Base implementation for database repositories

- `workflow/`: Implementations of `IWorkflowRepository`
  - `file_system_workflow_repository.py`: File system implementation of `IWorkflowRepository`
  - `database_workflow_repository.py`: Database implementation of `IWorkflowRepository`

- `credential/`: Implementations of `ICredentialRepository`
  - `file_system_credential_repository.py`: File system implementation of `ICredentialRepository`
  - `database_credential_repository.py`: Database implementation of `ICredentialRepository`

- `factory.py`: Factory for creating repository instances

## Usage

```python
# Import the repository factory
from src.infrastructure.repositories.factory import RepositoryFactory

# Create a workflow repository
workflow_repo = RepositoryFactory.create_workflow_repository(
    repo_type="file_system",
    directory_path="/path/to/workflows",
    create_if_missing=True
)

# Create a credential repository
credential_repo = RepositoryFactory.create_credential_repository(
    repo_type="file_system",
    directory_path="/path/to/credentials",
    create_if_missing=True
)
```

## Deprecated Implementations

The old repository implementations in the root of this directory are deprecated and will be removed in a future release. Use the new implementations in the subdirectories instead.
