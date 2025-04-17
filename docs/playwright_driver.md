# Playwright WebDriver Implementation

## Overview

The Playwright WebDriver implementation provides an alternative to the Selenium WebDriver for browser automation in AutoQliq. It leverages the Playwright library, which offers several advantages:

- Faster and more reliable automation
- Better handling of modern web applications
- Built-in auto-waiting for elements
- Cross-browser support (Chromium, Firefox, WebKit)
- Powerful network interception capabilities

## Architecture

The Playwright implementation follows a modular design with the following components:

1. **PlaywrightDriver**: The main driver class that implements the `IWebDriver` interface
2. **Handler Classes**: Specialized classes for different aspects of browser automation:
   - `PlaywrightElementHandler`: Element interactions (find, click, type, etc.)
   - `PlaywrightDialogHandler`: Alert/dialog handling
   - `PlaywrightScreenshotHandler`: Screenshot capabilities
   - `PlaywrightCookieHandler`: Cookie management
   - `PlaywrightNetworkHandler`: Network request/response interception

## Usage

### Basic Usage

```python
from src.infrastructure.webdrivers.factory import WebDriverFactory
from src.infrastructure.webdrivers.base import BrowserType

# Create a Playwright WebDriver instance
driver = WebDriverFactory.create_driver(
    browser_type=BrowserType.CHROME,
    driver_type="playwright"
)

# Navigate to a URL
driver.get("https://example.com")

# Find and interact with elements
driver.click_element("#submit-button")
driver.type_text("#search-input", "search query")

# Take screenshots
driver.take_screenshot("screenshot.png")

# Close the browser
driver.quit()
```

### Advanced Features

#### Network Interception

```python
# Wait for a specific request
response = driver.wait_for_request("https://api.example.com/data")

# Add a route handler to intercept requests
def handle_request(route, request):
    # Modify request or response
    route.fulfill(status=200, body=json.dumps({"data": "mocked"}))

driver.add_route_handler("**/api/data", handle_request)
```

#### Dialog Handling

```python
# Accept an alert
driver.accept_alert()

# Dismiss an alert
driver.dismiss_alert()

# Get alert text
alert_text = driver.get_alert_text()
```

## Installation Requirements

To use the Playwright WebDriver, you need to install the Playwright library and browser binaries:

```bash
pip install playwright
playwright install
```

## Comparison with Selenium

| Feature | Playwright | Selenium |
|---------|-----------|----------|
| Speed | Faster | Slower |
| Reliability | More reliable | Less reliable |
| Auto-waiting | Built-in | Manual implementation |
| Browser support | Chromium, Firefox, WebKit | Chrome, Firefox, Edge, Safari, IE |
| Network interception | Built-in | Limited |
| Shadow DOM support | Built-in | Limited |
| Installation | Requires additional step | Simpler |

## Implementation Details

### Browser Type Mapping

The `BrowserType` enum is mapped to Playwright's browser types as follows:

- `BrowserType.CHROME` → Playwright's Chromium
- `BrowserType.FIREFOX` → Playwright's Firefox
- `BrowserType.EDGE` → Playwright's Chromium (with a warning)
- `BrowserType.SAFARI` → Playwright's WebKit

### Error Handling

All Playwright-specific errors are caught and wrapped in `WebDriverError` instances to maintain consistency with the `IWebDriver` interface.

## Testing

The Playwright implementation includes comprehensive unit tests that verify all functionality, including error handling and edge cases.

## Future Enhancements

Potential future enhancements for the Playwright implementation:

1. Support for browser contexts to enable multi-tab automation
2. Enhanced mobile device emulation
3. Improved performance metrics collection
4. Video recording of test runs
5. Integration with Playwright's trace viewer for debugging
