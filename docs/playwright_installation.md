# Playwright Installation Guide for AutoQliq

This guide will help you install and configure Playwright for use with AutoQliq.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- AutoQliq installed

## Installation Steps

### 1. Install Playwright Python Package

First, you need to install the Playwright Python package:

```bash
pip install playwright
```

### 2. Install Browser Binaries

After installing the Python package, you need to install the browser binaries that Playwright will use:

```bash
playwright install
```

This command will download and install Chromium, Firefox, and WebKit (Safari) browsers.

If you only want to install specific browsers, you can use:

```bash
# Install only Chromium
playwright install chromium

# Install only Firefox
playwright install firefox

# Install only WebKit
playwright install webkit
```

### 3. Verify Installation

To verify that Playwright is installed correctly, you can run the example script:

```bash
python examples/playwright_example.py
```

If everything is set up correctly, this script will:
1. Launch a browser using Playwright
2. Navigate to example.com
3. Take a screenshot
4. Close the browser

## Using Playwright in AutoQliq

To use Playwright instead of Selenium in your AutoQliq workflows:

1. When creating a WebDriver instance, specify `driver_type="playwright"`:

```python
from src.infrastructure.webdrivers import WebDriverFactory, BrowserType

driver = WebDriverFactory.create_driver(
    browser_type=BrowserType.CHROME,
    driver_type="playwright",
    implicit_wait_seconds=5
)
```

2. Use the driver as you would normally with the IWebDriver interface:

```python
driver.get("https://example.com")
element = driver.find_element("h1")
text = driver.get_element_text("h1")
driver.quit()
```

## Playwright-Specific Features

Playwright provides some advanced features not available in Selenium:

### Network Interception

```python
def handle_route(route, request):
    # Mock a response
    if request.url.endswith("/api/data"):
        route.fulfill(
            status=200,
            body=json.dumps({"message": "Mocked response"}),
            headers={"Content-Type": "application/json"}
        )
    else:
        # Continue with the request
        route.continue_()

# Add a route handler
driver.add_route_handler("**/api/**", handle_route)
```

### Full Page Screenshots

```python
# Take a full page screenshot (including content outside the viewport)
driver.take_full_page_screenshot("full_page.png")
```

### Element Screenshots

```python
# Take a screenshot of a specific element
driver.take_element_screenshot("#my-element", "element.png")
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'playwright'**
   - Solution: Run `pip install playwright`

2. **Browser binaries not found**
   - Solution: Run `playwright install`

3. **Permission issues on Linux**
   - Solution: Install additional dependencies with `playwright install-deps`

4. **Slow performance**
   - Solution: Try using a different browser type (e.g., BrowserType.FIREFOX)

### Getting Help

If you encounter issues with Playwright in AutoQliq:

1. Check the Playwright documentation: https://playwright.dev/python/docs/intro
2. Look for error messages in the AutoQliq logs
3. Ensure you're using the latest version of AutoQliq and Playwright

## Comparing Selenium and Playwright

| Feature | Selenium | Playwright |
|---------|----------|------------|
| Browser Support | Chrome, Firefox, Edge, Safari | Chromium, Firefox, WebKit |
| Speed | Good | Excellent |
| Stability | Good | Excellent |
| Auto-waiting | Limited | Built-in |
| Network Interception | Limited | Advanced |
| Mobile Emulation | Basic | Advanced |
| Screenshots | Basic | Full-page, element-specific |
| Installation | Requires WebDrivers | Self-contained |
| Iframe Handling | Manual | Simplified |
| Parallel Execution | Requires setup | Built-in |

## Conclusion

Playwright offers several advantages over Selenium, including better performance, more stable tests, and advanced features like network interception. However, Selenium has broader browser support and is more widely used.

AutoQliq supports both drivers, allowing you to choose the best tool for your specific needs.
