# AutoQliq Refactoring Guide

**********ARCHIVED**********
Archived on: 2025-04-06


## Overview

This guide explains how to use the AutoQliq refactoring system to implement major code restructuring while maintaining SOLID, KISS, DRY principles, and TDD methodology. The system uses a specialized AI to generate refactored code and a Python script to apply those changes to the codebase.

## The Refactoring Process

### 1. Understanding the Current System

The AutoQliq refactoring system consists of three key components:

1. **`apply_refactoring.py`**: A Python script that parses specially formatted text files containing refactored code and applies the changes to the codebase.
2. **`refactoring_request_final.txt`**: A template that provides context about the refactoring needs, current implementation, and expected output format.
3. **`GEMINI.txt`**: An example of the output from an AI model (in this case, Google's Gemini) that follows the required format for the refactoring script.

### 2. How the Refactoring Script Works

The `apply_refactoring.py` script:

- Parses a specially formatted text file containing refactored code
- Extracts file paths and their complete content
- Creates or updates files in the codebase
- Creates directory structures automatically if needed
- Provides detailed logging of all changes made

### 3. Required Format for AI Output

The script expects the refactored code in this **EXACT** format:

```
FILE LIST
src/file1.py
src/file2.py
...

FILE CONTENTS
FILE: src/file1.py
(complete python code for file1.py)

FILE: src/file2.py
(complete python code for file2.py)
...
```

**Important Format Rules:**
- The file must start with a "FILE LIST" section listing all files to be created/updated
- Each file path must be on its own line
- The "FILE CONTENTS" section must follow the file list
- Each file's content must be preceded by "FILE: filepath" on its own line
- The complete content of each file must be included
- There must be no missing files (every file in the list must have content)

### 4. Creating a Refactoring Request

To create an effective refactoring request for the AI:

1. **Identify the files that need refactoring**:
   - Analyze the codebase for violations of SOLID, KISS, and DRY principles
   - Focus on files with multiple responsibilities, long methods, or duplicated code

2. **Create a detailed refactoring request**:
   - Explain the current issues with the code
   - Specify the desired outcome (e.g., better separation of concerns)
   - Provide the current implementation of key files
   - List the new files that should be created
   - Include examples of the expected output format

3. **Emphasize key principles**:
   - Single Responsibility Principle (SRP): Each class should have only one reason to change
   - Keep It Simple, Stupid (KISS): Methods should be simple and under 20 lines
   - Don't Repeat Yourself (DRY): Avoid code duplication
   - Test-Driven Development (TDD): Code should be testable and have tests

### 5. Generating Refactored Code with AI

1. **Submit the refactoring request to the AI**:
   - Use a powerful AI model like Google's Gemini, Claude, or GPT-4
   - Provide the complete refactoring request
   - Emphasize the importance of following the exact format requirements

2. **Review the AI's output**:
   - Ensure it follows the required format (FILE LIST and FILE CONTENTS sections)
   - Check that all files in the list have corresponding content
   - Verify that the code adheres to SOLID, KISS, and DRY principles
   - Make any necessary adjustments to the format or content

### 6. Applying the Refactored Code

1. **Save the AI's output to a file**:
   - Save the complete output, including the FILE LIST and FILE CONTENTS sections
   - Ensure the file is in plain text format

2. **Run the refactoring script**:
   ```bash
   python apply_refactoring.py path/to/ai_output.txt
   ```

3. **Review the changes**:
   - The script will show a list of files that will be created or updated
   - Confirm the changes before proceeding
   - Check the log file (`refactoring.log`) for any issues

4. **Test the refactored code**:
   - Run existing tests to ensure functionality is preserved
   - Create new tests for any new components
   - Verify that the code works as expected

## Example Refactoring

### Current Issues

The AutoQliq codebase has several issues that need to be addressed:

1. **Violation of Single Responsibility Principle**:
   - `src/core/actions.py` handles multiple responsibilities including action creation, validation, execution, serialization, and error handling
   - `src/core/workflow.py` handles workflow data management, execution, credential management, and error handling
   - `src/infrastructure/webdrivers.py` handles WebDriver creation, browser interaction, error handling, and screenshot functionality

2. **Long Methods**:
   - Many methods exceed 20 lines, making them difficult to understand and test
   - Complex logic is not broken down into smaller, focused methods

3. **Code Duplication**:
   - Error handling code is duplicated across multiple methods
   - Similar functionality is implemented in multiple places

### Refactoring Plan

The refactoring plan involves:

1. **Breaking down large files into focused modules**:
   - Create separate modules for different types of actions
   - Separate workflow execution from data management
   - Split WebDriver functionality into focused components

2. **Creating clear class hierarchies**:
   - Define base classes with common functionality
   - Create specialized subclasses for specific behaviors
   - Use interfaces to define contracts

3. **Implementing proper error handling**:
   - Centralize error handling logic
   - Use decorators for consistent error handling
   - Provide detailed error messages and context

4. **Maintaining backward compatibility**:
   - Keep existing module names but make them re-export from new structure
   - Issue deprecation warnings for old usage patterns
   - Provide clear migration paths

### Example Refactored Structure

The refactored code structure includes:

1. **Actions Package**:
   - `src/core/actions/base.py`: Base action class
   - `src/core/actions/navigation.py`: Navigation actions
   - `src/core/actions/interaction.py`: User interaction actions
   - `src/core/actions/utility.py`: Utility actions
   - `src/core/actions/serialization.py`: Serialization utilities
   - `src/core/actions/factory.py`: Factory for creating actions
   - `src/core/actions/__init__.py`: Package initialization

2. **Workflow Package**:
   - `src/core/workflow/runner.py`: Workflow execution
   - `src/core/workflow/error_handler.py`: Error handling
   - `src/core/workflow/credential_manager.py`: Credential management
   - `src/core/workflow/__init__.py`: Package initialization

3. **WebDrivers Package**:
   - `src/infrastructure/webdrivers/base.py`: Base definitions
   - `src/infrastructure/webdrivers/selenium_driver.py`: Selenium implementation
   - `src/infrastructure/webdrivers/playwright_driver.py`: Playwright implementation
   - `src/infrastructure/webdrivers/error_handler.py`: Error handling
   - `src/infrastructure/webdrivers/factory.py`: Factory for creating drivers
   - `src/infrastructure/webdrivers/__init__.py`: Package initialization

## Best Practices for Refactoring

1. **Follow SOLID Principles**:
   - **Single Responsibility**: Each class should have only one reason to change
   - **Open/Closed**: Classes should be open for extension but closed for modification
   - **Liskov Substitution**: Subtypes must be substitutable for their base types
   - **Interface Segregation**: Many client-specific interfaces are better than one general-purpose interface
   - **Dependency Inversion**: Depend on abstractions, not concretions

2. **Keep Methods Simple (KISS)**:
   - Methods should be under 20 lines
   - Each method should do one thing and do it well
   - Use descriptive names that clearly indicate what the method does

3. **Avoid Duplication (DRY)**:
   - Extract common functionality into base classes or utility methods
   - Use composition to share behavior
   - Create reusable components

4. **Write Tests First (TDD)**:
   - Write tests before implementing functionality
   - Ensure all code is testable
   - Maintain high test coverage

5. **Document Your Code**:
   - Use descriptive docstrings
   - Explain the purpose of classes and methods
   - Document parameters, return values, and exceptions

## Conclusion

The AutoQliq refactoring system provides a powerful way to implement major code restructuring while maintaining high quality standards. By leveraging AI to generate refactored code and using the `apply_refactoring.py` script to apply those changes, you can efficiently improve your codebase's adherence to SOLID, KISS, and DRY principles.

Remember that refactoring is an iterative process. Start with the most critical issues, apply the changes, test thoroughly, and then move on to the next set of improvements. With each iteration, your codebase will become more maintainable, extensible, and robust.
