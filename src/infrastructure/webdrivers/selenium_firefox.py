from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
import logging
from typing import Optional
from src.core.interfaces.driver_interface import IWebDriver
from src.core.exceptions import WebDriverError

logger = logging.getLogger(__name__)

class SeleniumFirefoxDriver(IWebDriver):
    """IWebDriver implementation using Selenium FirefoxDriver."""
    def __init__(self, driver_path: Optional[str] = None, headless: bool = False, window_size: Optional[str] = None, implicit_wait: int = 0):
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        if window_size:
            w, h = window_size.split('x') if 'x' in window_size else (None, None)
            if w and h:
                options.add_argument(f'--width={w}')
                options.add_argument(f'--height={h}')
        try:
            service = FirefoxService(executable_path=driver_path) if driver_path else FirefoxService()
            self._driver = webdriver.Firefox(service=service, options=options)
            if implicit_wait:
                self._driver.implicitly_wait(implicit_wait)
            logger.info('Initialized Firefox WebDriver')
        except Exception as e:
            logger.error(f'Failed to start FirefoxDriver: {e}', exc_info=True)
            raise WebDriverError('FirefoxDriver initialization failed', driver_type='firefox', cause=e)

    def get(self, url: str) -> None:
        try:
            self._driver.get(url)
        except Exception as e:
            logger.error(f'Navigation error: {e}', exc_info=True)
            raise WebDriverError(f'get() failed for URL {url}', driver_type='firefox', cause=e)

    def find_element(self, selector: str) -> any:
        try:
            return self._driver.find_element(By.CSS_SELECTOR, selector)
        except Exception as e:
            logger.error(f'find_element error: {e}', exc_info=True)
            raise WebDriverError(f'find_element() failed for selector {selector}', driver_type='firefox', cause=e)

    def click_element(self, selector: str) -> None:
        try:
            elem = self.find_element(selector)
            elem.click()
        except WebDriverError:
            raise
        except Exception as e:
            logger.error(f'click_element error: {e}', exc_info=True)
            raise WebDriverError(f'click_element() failed for selector {selector}', driver_type='firefox', cause=e)

    # Alias for backward compatibility
    def click(self, selector: str) -> None:
        return self.click_element(selector)

    def type_text(self, selector: str, text: str) -> None:
        try:
            elem = self.find_element(selector)
            elem.clear()
            elem.send_keys(text)
        except WebDriverError:
            raise
        except Exception as e:
            logger.error(f'type_text error: {e}', exc_info=True)
            raise WebDriverError(f'type_text() failed for selector {selector}', driver_type='firefox', cause=e)

    def get_attribute(self, selector: str, attribute: str) -> any:
        try:
            elem = self.find_element(selector)
            return elem.get_attribute(attribute)
        except Exception as e:
            logger.error(f'get_attribute error: {e}', exc_info=True)
            raise WebDriverError(f'get_attribute() failed for selector {selector}', driver_type='firefox', cause=e)

    def quit(self) -> None:
        try:
            self._driver.quit()
            logger.info('Firefox WebDriver quit')
        except Exception as e:
            logger.error(f'quit error: {e}', exc_info=True)
            raise WebDriverError('quit() failed', driver_type='firefox', cause=e)

    def take_screenshot(self, file_path: str) -> None:
        try:
            self._driver.save_screenshot(file_path)
            logger.info(f'Screenshot saved to {file_path}')
        except Exception as e:
            logger.error(f'take_screenshot error: {e}', exc_info=True)
            raise WebDriverError(f'take_screenshot() failed for path {file_path}', driver_type='firefox', cause=e)

    def is_element_present(self, selector: str) -> bool:
        try:
            self._driver.find_element(By.CSS_SELECTOR, selector)
            return True
        except Exception:
            return False

    def get_current_url(self) -> str:
        try:
            return self._driver.current_url
        except Exception as e:
            logger.error(f'get_current_url error: {e}', exc_info=True)
            raise WebDriverError('get_current_url() failed', driver_type='firefox', cause=e)

    def execute_script(self, script: str, *args: any) -> any:
        try:
            return self._driver.execute_script(script, *args)
        except Exception as e:
            logger.error(f'execute_script error: {e}', exc_info=True)
            raise WebDriverError(f'execute_script() failed: {script}', driver_type='firefox', cause=e)

    def wait_for_element(self, selector: str, timeout: int = 10) -> any:
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            element = WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except Exception as e:
            logger.error(f'wait_for_element error: {e}', exc_info=True)
            raise WebDriverError(f'wait_for_element() failed for selector {selector}', driver_type='firefox', cause=e)

    def switch_to_frame(self, frame_reference) -> None:
        try:
            self._driver.switch_to.frame(frame_reference)
        except Exception as e:
            logger.error(f'switch_to_frame error: {e}', exc_info=True)
            raise WebDriverError(f'switch_to_frame() failed', driver_type='firefox', cause=e)

    def switch_to_default_content(self) -> None:
        try:
            self._driver.switch_to.default_content()
        except Exception as e:
            logger.error(f'switch_to_default_content error: {e}', exc_info=True)
            raise WebDriverError('switch_to_default_content() failed', driver_type='firefox', cause=e)

    def accept_alert(self) -> None:
        try:
            self._driver.switch_to.alert.accept()
        except Exception as e:
            logger.error(f'accept_alert error: {e}', exc_info=True)
            raise WebDriverError('accept_alert() failed', driver_type='firefox', cause=e)

    def dismiss_alert(self) -> None:
        try:
            self._driver.switch_to.alert.dismiss()
        except Exception as e:
            logger.error(f'dismiss_alert error: {e}', exc_info=True)
            raise WebDriverError('dismiss_alert() failed', driver_type='firefox', cause=e)

    def get_alert_text(self) -> str:
        try:
            return self._driver.switch_to.alert.text
        except Exception as e:
            logger.error(f'get_alert_text error: {e}', exc_info=True)
            raise WebDriverError('get_alert_text() failed', driver_type='firefox', cause=e)
