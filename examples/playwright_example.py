"""Example script demonstrating how to use the Playwright driver in AutoQliq."""

import logging
import sys
import time
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.infrastructure.webdrivers import WebDriverFactory, BrowserType

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """Run a simple example using the Playwright driver."""
    # Check if Playwright is available
    if not WebDriverFactory.is_playwright_available():
        print("Playwright is not installed. Please run:")
        print("pip install playwright")
        print("playwright install")
        return
    
    # Create a Playwright driver
    driver = WebDriverFactory.create_driver(
        browser_type=BrowserType.CHROME,
        driver_type="playwright",
        implicit_wait_seconds=5
    )
    
    try:
        # Navigate to a website
        driver.get("https://example.com")
        print(f"Current URL: {driver.get_current_url()}")
        
        # Check if an element is present
        if driver.is_element_present("h1"):
            print("Found h1 element")
            
            # Get the text of the element
            h1_text = driver.get_element_text("h1")
            print(f"H1 text: {h1_text}")
            
            # Take a screenshot
            driver.take_screenshot("example_screenshot.png")
            print("Screenshot saved to example_screenshot.png")
            
            # Execute JavaScript
            title = driver.execute_script("return document.title")
            print(f"Page title (via JavaScript): {title}")
            
            # Wait for 2 seconds to see the browser
            time.sleep(2)
        else:
            print("H1 element not found")
    finally:
        # Close the browser
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    main()
