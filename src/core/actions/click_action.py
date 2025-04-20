import logging
# ... existing imports ...
from src.core.actions.constants import SUPPORTED_LOCATORS # Import the constant

logger = logging.getLogger(__name__)

# Remove the local definition:
# SUPPORTED_LOCATORS = ["id", "xpath", "css selector", "name", "link text", "partial link text", "tag name", "class name"]

class ClickAction(ActionBase):
    """Action to find an element and click it."""
    action_type: str = "Click"

    def __init__(self, name: Optional[str] = None, locator_type: Optional[str] = None, locator_value: Optional[str] = None, **kwargs):
        super().__init__(name, **kwargs)
        # Store parameters directly as attributes for clarity and type hinting
        self.locator_type = locator_type
        self.locator_value = locator_value
        # Validate parameters during initialization
        try:
            self.validate_parameters()
        except ValidationError as e:
            # Re-raise with action context
            raise ValidationError(
                e.message,
                field_name=e.field_name,
                action_name=self.name,
                action_type=self.action_type
            ) from e
        logger.debug(f"[{self.action_type} '{self.name}'] Initialized with {self.locator_type}='{self.locator_value}'")

    def validate_parameters(self) -> None:
        """Validate 'locator_type' and 'locator_value' parameters."""
        logger.debug(f"[{self.action_type} '{self.name}'] Validating parameters.")
        locator_type = self.locator_type
        locator_value = self.locator_value

        if not locator_type or not isinstance(locator_type, str):
            raise ValidationError("Missing or invalid 'locator_type' parameter (string expected).", field_name="locator_type", action_name=self.name, action_type=self.action_type)
        # Use the imported constant
        if locator_type.lower() not in SUPPORTED_LOCATORS:
            raise ValidationError(f"Unsupported locator_type: '{locator_type}'. Supported: {SUPPORTED_LOCATORS}", field_name="locator_type", action_name=self.name, action_type=self.action_type)
        if not locator_value or not isinstance(locator_value, str):
            raise ValidationError("Missing or invalid 'locator_value' parameter (string expected).", field_name="locator_value", action_name=self.name, action_type=self.action_type)
        logger.debug(f"[{self.action_type} '{self.name}'] Parameters validated: {locator_type}='{locator_value}'")

    def validate(self) -> bool:
        """Validate the action configuration."""
        super().validate() # Validate base (name)
        self.validate_parameters() # Validate specific parameters
        logger.debug(f"[{self.action_type} '{self.name}'] Validation successful.")
        return True

    def execute(self, driver: IWebDriver, credential_repo: Optional[ICredentialRepository] = None, context: Optional[Dict[str, Any]] = None) -> ActionResult:
        """Execute the click action."""
        locator_type = self.locator_type
        locator_value = self.locator_value
        logger.info(f"[{self.action_type} '{self.name}'] Executing click on element located by {locator_type}: {locator_value}")
        try:
            self.validate() # Ensure valid before execution
            # Assuming IWebDriver has a find_element method that takes type and value
            # and returns a clickable element or raises WebDriverError
            element = driver.find_element(by=locator_type, value=locator_value)
            if not element:
                 msg = f"[{self.action_type} '{self.name}'] Element not found using {locator_type}: {locator_value}"
                 logger.warning(msg)
                 return ActionResult.failure(msg)

            driver.click(element) # Assuming IWebDriver has a click method that takes an element
            logger.info(f"[{self.action_type} '{self.name}'] Successfully clicked element located by {locator_type}: {locator_value}")
            return ActionResult.success(f"Clicked element located by {locator_type}: {locator_value}")

        except (ValidationError, WebDriverError) as e:
            msg = f"[{self.action_type} '{self.name}'] Click failed on element {locator_type}: {locator_value}. Error: {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            err_msg = f"[{self.action_type} '{self.name}'] Unexpected error during click on element {locator_type}: {locator_value}. Error: {e}"
            logger.error(err_msg, exc_info=True)
            return ActionResult.failure(err_msg)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action."""
        base_dict = super().to_dict()
        base_dict["locator_type"] = self.locator_type
        base_dict["locator_value"] = self.locator_value
        return base_dict

    # No nested actions
    # def get_nested_actions(self) -> List[IAction]: return []

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"{self.__class__.__name__}(name='{self.name}', locator_type='{self.locator_type}', locator_value='{self.locator_value}')"

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"{self.action_type}: {self.name} ({self.locator_type}='{self.locator_value}')"

# STATUS: INCOMPLETE ⚠ (Needs unit tests)