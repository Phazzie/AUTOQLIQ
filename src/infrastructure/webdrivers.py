from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from typing import Any
from src.core.interfaces import IWebDriver

class SeleniumWebDriver(IWebDriver):
    def __init__(self):
        self.driver = webdriver.Chrome()

    def get(self, url: str) -> None:
        self.driver.get(url)

    def quit(self) -> None:
        self.driver.quit()

    def find_element(self, selector: str) -> Any:
        return self.driver.find_element(By.CSS_SELECTOR, selector)

    def click_element(self, selector: str) -> None:
        element = self.find_element(selector)
        element.click()

    def type_text(self, selector: str, text: str) -> None:
        element = self.find_element(selector)
        element.send_keys(text)

    def take_screenshot(self, file_path: str) -> None:
        self.driver.save_screenshot(file_path)

    def is_element_present(self, selector: str) -> bool:
        try:
            self.find_element(selector)
            return True
        except:
            return False

    def get_current_url(self) -> str:
        return self.driver.current_url
