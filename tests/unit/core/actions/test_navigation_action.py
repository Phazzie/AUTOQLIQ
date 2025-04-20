import pytest
from unittest.mock import Mock
from src.core.actions.navigation import NavigateAction
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError, ActionError
from src.core.interfaces import IWebDriver

@pytest.fixture
def driver_stub():
    return Mock(spec=IWebDriver)

def test_navigate_action_success(driver_stub):
    url = "https://example.com"
    action = NavigateAction(url=url, name="Go to Example")
    result = action.execute(driver_stub)

    driver_stub.get.assert_called_once_with(url)
    assert result.status == ActionStatus.SUCCESS
    assert result.message == f"Navigated to {url}"

def test_navigate_action_validation_fails_on_empty_url():
    with pytest.raises(ValidationError) as excinfo:
        NavigateAction(url="", name="Invalid Nav")
    assert "URL must be a non-empty string." in str(excinfo.value)

def test_navigate_action_validation_fails_on_invalid_url_type():
    with pytest.raises(ValidationError) as excinfo:
        NavigateAction(url=123, name="Invalid Nav")
    assert "URL must be a non-empty string." in str(excinfo.value)

def test_navigate_action_execution_fails_on_webdriver_error(driver_stub):
    driver_stub.get.side_effect = Exception("Browser error")
    url = "https://example.com"
    action = NavigateAction(url=url, name="Go to Example")

    result = action.execute(driver_stub)

    driver_stub.get.assert_called_once_with(url)
    assert result.status == ActionStatus.FAILURE
    assert "Browser error" in result.message

def test_navigate_action_to_dict():
    url = "https://example.com/page"
    action = NavigateAction(url=url, name="Nav Page")
    expected_dict = {
        "type": "Navigate",
        "name": "Nav Page",
        "url": url
    }
    assert action.to_dict() == expected_dict

def test_navigate_action_default_name():
    url = "https://example.com"
    action = NavigateAction(url=url)
    assert action.name == "Navigate"
