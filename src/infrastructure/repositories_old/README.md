# DEPRECATED Repository Implementations

This directory contains deprecated repository implementations that are scheduled for removal in a future release.

## Why are these files deprecated?

These repository implementations have been replaced by new, more consistent implementations in the `src/infrastructure/repositories/` directory. The new implementations follow a more consistent design and adhere more closely to SOLID principles.

## What should I use instead?

Use the new repository implementations in the `src/infrastructure/repositories/` directory:

- Base classes: `src/infrastructure/repositories/base/`
- Workflow repositories: `src/infrastructure/repositories/workflow/`
- Credential repositories: `src/infrastructure/repositories/credential/`
- Factory: `src/infrastructure/repositories/factory.py`

## When will these files be removed?

These files are scheduled for removal in the next major release. They are kept temporarily for backward compatibility.

## How do I migrate my code?

If your code depends on these deprecated implementations, update your imports to use the new implementations. The new implementations provide the same functionality with a more consistent API.

For example, replace:

```python
from src.infrastructure.repositories.workflow_repository import FileSystemWorkflowRepository
```

With:

```python
from src.infrastructure.repositories.workflow.file_system_workflow_repository import FileSystemWorkflowRepository
```
