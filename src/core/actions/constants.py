"""Constants shared across action modules."""

# List of supported locator strategies for finding web elements.
# Aligns with common WebDriver implementations (Selenium, etc.)
SUPPORTED_LOCATORS = [
    "id",
    "xpath",
    "css selector",
    "name",
    "link text",
    "partial link text",
    "tag name",
    "class name"
]
