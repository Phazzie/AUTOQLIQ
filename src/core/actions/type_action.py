import logging
# ... existing imports ...
from src.core.actions.constants import SUPPORTED_LOCATORS # Import the constant

logger = logging.getLogger(__name__)

# Remove the local definition:
# SUPPORTED_LOCATORS = ["id", "xpath", "css selector", "name", "link text", "partial link text", "tag name", "class name"]

class TypeAction(ActionBase):
    """Action to find an element and type text into it."""
    action_type: str = "Type"

    def __init__(self, name: Optional[str] = None, locator_type: Optional[str] = None, locator_value: Optional[str] = None, text: Optional[str] = None, clear_first: bool = True, **kwargs):
        super().__init__(name, **kwargs)
        # Store parameters directly as attributes
        self.locator_type = locator_type
        self.locator_value = locator_value
        self.text = text
        self.clear_first = clear_first
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
        logger.debug(f"[{self.action_type} '{self.name}'] Initialized with {self.locator_type}='{self.locator_value}', text='{self.text}', clear_first={self.clear_first}")

    def validate_parameters(self) -> None:
        """Validate locator, text, and optional clear_first parameters."""
        logger.debug(f"[{self.action_type} '{self.name}'] Validating parameters.")
        locator_type = self.locator_type
        locator_value = self.locator_value
        text_to_type = self.text
        clear_first = self.clear_first

        if not locator_type or not isinstance(locator_type, str):
            raise ValidationError("Missing or invalid 'locator_type' parameter (string expected).", field_name="locator_type", action_name=self.name, action_type=self.action_type)
        # Use the imported constant
        if locator_type.lower() not in SUPPORTED_LOCATORS:
            raise ValidationError(f"Unsupported locator_type: '{locator_type}'. Supported: {SUPPORTED_LOCATORS}", field_name="locator_type", action_name=self.name, action_type=self.action_type)
        if not locator_value or not isinstance(locator_value, str):
            raise ValidationError("Missing or invalid 'locator_value' parameter (string expected).", field_name="locator_value", action_name=self.name, action_type=self.action_type)
        if text_to_type is None or not isinstance(text_to_type, str):
             # Allow empty string, but require 'text' key to be present
            raise ValidationError("Missing or invalid 'text' parameter (string expected).", field_name="text", action_name=self.name, action_type=self.action_type)
        if not isinstance(clear_first, bool):
            raise ValidationError("'clear_first' parameter must be a boolean (true/false).", field_name="clear_first", action_name=self.name, action_type=self.action_type)

        logger.debug(f"[{self.action_type} '{self.name}'] Parameters validated: {locator_type}='{locator_value}', text='{text_to_type}', clear={clear_first}")

    def validate(self) -> bool:
        """Validate the action configuration."""
        super().validate() # Validate base (name)
        self.validate_parameters() # Validate specific parameters
        logger.debug(f"[{self.action_type} '{self.name}'] Validation successful.")
        return True

    def execute(self, driver: IWebDriver, credential_repo: Optional[ICredentialRepository] = None, context: Optional[Dict[str, Any]] = None) -> ActionResult:
        """Execute the type action."""
        locator_type = self.locator_type
        locator_value = self.locator_value
        text_to_type = self.text
        clear_first = self.clear_first

        logger.info(f"[{self.action_type} '{self.name}'] Executing type into element located by {locator_type}: {locator_value}")
        try:
            self.validate() # Ensure valid before execution
            # Assuming IWebDriver has a find_element method that takes type and value
            # and returns an element or raises WebDriverError
            element = driver.find_element(by=locator_type, value=locator_value)
            if not element:
                 msg = f"[{self.action_type} '{self.name}'] Element not found using {locator_type}: {locator_value}"
                 logger.warning(msg)
                 return ActionResult.failure(msg)

            if clear_first:
                logger.debug(f"[{self.action_type} '{self.name}'] Clearing element before typing.")
                driver.clear(element) # Assuming IWebDriver has a clear method

            driver.type_text(element, text_to_type) # Assuming IWebDriver has a type_text method
            logger.info(f"[{self.action_type} '{self.name}'] Successfully typed text into element located by {locator_type}: {locator_value}")
            return ActionResult.success(f"Typed text into element located by {locator_type}: {locator_value}")

        except (ValidationError, WebDriverError) as e:
            msg = f"[{self.action_type} '{self.name}'] Type failed on element {locator_type}: {locator_value}. Error: {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            err_msg = f"[{self.action_type} '{self.name}'] Unexpected error during type into element {locator_type}: {locator_value}. Error: {e}"
            logger.error(err_msg, exc_info=True)
            return ActionResult.failure(err_msg)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action."""
        base_dict = super().to_dict()
        base_dict["locator_type"] = self.locator_type
        base_dict["locator_value"] = self.locator_value
        base_dict["text"] = self.text
        base_dict["clear_first"] = self.clear_first
        return base_dict

    # No nested actions
    # def get_nested_actions(self) -> List[IAction]: return []

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"{self.__class__.__name__}(name='{self.name}', locator_type='{self.locator_type}', locator_value='{self.locator_value}', text='{self.text}', clear_first={self.clear_first})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"{self.action_type}: {self.name} ({self.locator_type}='{self.locator_value}', text='{self.text[:20]}...')"

# STATUS: INCOMPLETE ⚠ (Needs unit tests)