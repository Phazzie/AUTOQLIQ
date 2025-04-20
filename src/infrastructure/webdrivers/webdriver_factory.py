from typing import Optional
import logging

from src.config import config
from src.core.interfaces.driver_interface import IWebDriver
from src.infrastructure.webdrivers.selenium_chrome import SeleniumChromeDriver
from src.infrastructure.webdrivers.selenium_firefox import SeleniumFirefoxDriver
from src.core.exceptions import WebDriverError

logger = logging.getLogger(__name__)

class WebDriverFactory:
    """Factory to create IWebDriver instances based on configuration."""
    def __init__(self):
        # Retrieve config settings
        self.browser = config.default_browser.lower()
        self.driver_path = config.get_driver_path(self.browser)
        self.implicit_wait = getattr(config, 'implicit_wait', 0)
        # Optional settings (not in config by default)
        self.headless = False
        self.window_size = None

    def create_webdriver(self) -> IWebDriver:
        """Instantiate the configured IWebDriver implementation."""
        logger.info(f"Creating WebDriver for browser: {self.browser}")
        try:
            if self.browser == 'chrome':
                return SeleniumChromeDriver(
                    driver_path=self.driver_path,
                    headless=self.headless,
                    window_size=self.window_size,
                    implicit_wait=self.implicit_wait
                )
            elif self.browser == 'firefox':
                return SeleniumFirefoxDriver(
                    driver_path=self.driver_path,
                    headless=self.headless,
                    window_size=self.window_size,
                    implicit_wait=self.implicit_wait
                )
            else:
                # Unsupported browser
                raise WebDriverError(f"Unsupported browser type: {self.browser}", driver_type=self.browser)
        except WebDriverError:
            raise
        except Exception as e:
            logger.error(f"Failed to create WebDriver (browser={self.browser}): {e}")
            raise WebDriverError("WebDriverFactory failed to create driver", driver_type=self.browser, cause=e)
