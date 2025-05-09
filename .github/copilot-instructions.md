# AI Coding Assistant Standards

## Core Requirements

- **SOLID Compliance**: Each class has exactly one responsibility; interfaces are lean; dependencies are injected
- **Function Size**: All methods ≤20 lines with single purpose (measured by line count)
- **Error Handling**: Every operation has appropriate error handling with specific recovery steps
- **Logging**: INFO for operations, ERROR for failures with context details

## Technical Standards

- **Clean Architecture**: Separate concerns with proper layering and dependency management
- **Defensive Programming**: Validate inputs, use appropriate assertions, handle edge cases
- **Configuration**: Externalize all constants, settings, and environment-specific values
- **Performance**: Consider efficiency in algorithms and resource usage

## Self-Check Checklist

- [ ] All classes have single responsibility (count responsibilities)
- [ ] No method exceeds 20 lines (verify with line counter)
- [ ] Every critical operation has error handling (count try/except blocks)
- [ ] Logging exists at appropriate levels (verify log calls)
- [ ] Constants and configuration values are externalized
- [ ] Code is properly tested with appropriate coverage

## Completion Status

End implementation with:

- `STATUS: COMPLETE ✓` (All checklist items verified)
- `STATUS: INCOMPLETE ⚠` (List specific failed checklist items)

- @azure Rule - Use Azure Best Practices: When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `get_azure_best_practices` tool if available.
