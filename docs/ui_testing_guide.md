# AutoQliq UI Testing Guide

## Overview

This guide explains how to use the UI testing framework for AutoQliq. The framework provides tools and utilities for testing Tkinter-based UI components, including dialogs, views, and presenters.

## Test Structure

The UI testing framework is organized as follows:

- `tests/ui_testing/ui_test_base.py`: Base class for UI tests
- `tests/ui_testing/test_*.py`: Test cases for specific UI components
- `tests/ui_testing/run_ui_tests.py`: Script to run all UI tests

## UITestBase Class

The `UITestBase` class provides common functionality for UI testing:

- Setting up a Tkinter root window
- Mocking common dialogs and message boxes
- Utility methods for interacting with UI components
- Cleanup after tests

### Key Features

- **Automatic Mocking**: Common Tkinter dialogs (simpledialog, messagebox, filedialog) are automatically mocked
- **UI Interaction Helpers**: Methods for clicking buttons, selecting items, setting values, etc.
- **Assertion Helpers**: Methods for asserting widget state, text, etc.

## Writing UI Tests

To write a UI test:

1. Create a new test class that inherits from `UITestBase`
2. Override `setUp()` to create the UI component to test
3. Write test methods for specific functionality
4. Override `tearDown()` if needed for additional cleanup

Example:

```python
class TestMyDialog(UITestBase):
    def setUp(self):
        super().setUp()
        self.dialog = MyDialog(self.root)
        
    def test_initialization(self):
        self.assertEqual(self.dialog.title(), "My Dialog")
        
    def test_button_click(self):
        self.click_button(self.dialog.ok_button)
        self.mock_presenter.save_data.assert_called_once()
```

## Running Tests

### Running All UI Tests

To run all UI tests:

```bash
python tests/ui_testing/run_ui_tests.py
```

### Running Specific Tests

To run a specific test file:

```bash
python tests/ui_testing/test_action_selection_dialog.py
```

To run a specific test method:

```bash
python -m unittest tests.ui_testing.test_action_selection_dialog.TestActionSelectionDialog.test_initialization
```

## Best Practices

1. **Keep Tests Independent**: Each test should be independent of others
2. **Mock External Dependencies**: Use mocks for external dependencies
3. **Test One Thing at a Time**: Each test method should test one specific aspect
4. **Use Helper Methods**: Use the helper methods provided by `UITestBase`
5. **Clean Up Resources**: Make sure to clean up resources in `tearDown()`

## Common Patterns

### Testing Dialogs

For dialogs, you typically need to:
- Mock the `wait_window()` method to prevent blocking
- Test initialization, button clicks, and result values

### Testing Views

For views, you typically need to:
- Create a mock presenter
- Test initialization, UI interactions, and presenter method calls

### Testing Presenters

For presenters, you typically need to:
- Create a mock view
- Test initialization, method calls, and view updates

## Troubleshooting

### Common Issues

1. **Tests Hang**: Make sure to mock `wait_window()` for dialogs
2. **Widget Not Found**: Check widget hierarchy and names
3. **Mock Not Called**: Check that the correct method is being called

### Debugging Tips

1. Use `print()` statements to debug
2. Inspect widget hierarchies with `winfo_children()`
3. Check mock call counts and arguments with `mock_method.call_count` and `mock_method.call_args`
