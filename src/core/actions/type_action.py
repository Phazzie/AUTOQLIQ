import logging
# ... existing imports ...
from src.core.actions.constants import SUPPORTED_LOCATORS # Import the constant

logger = logging.getLogger(__name__)

# Remove the local definition:
# SUPPORTED_LOCATORS = ["id", "xpath", "css selector", "name", "link text", "partial link text", "tag name", "class name"]

class TypeAction(ActionBase):
    """Action to find an element and type text into it."""

    def validate_parameters(self) -> None:
        """Validate locator, text, and optional clear_first parameters."""
        locator_type = self.parameters.get("locator_type")
        locator_value = self.parameters.get("locator_value")
        text_to_type = self.parameters.get("text")
        clear_first = self.parameters.get("clear_first", True) # Default to True

        if not locator_type or not isinstance(locator_type, str):
            raise ValidationError("Missing or invalid 'locator_type' parameter (string expected).")
        # Use the imported constant
        if locator_type.lower() not in SUPPORTED_LOCATORS:
            raise ValidationError(f"Unsupported locator_type: '{locator_type}'. Supported: {SUPPORTED_LOCATORS}")
        # ... rest of validation ...
        if not locator_value or not isinstance(locator_value, str):
            raise ValidationError("Missing or invalid 'locator_value' parameter (string expected).")
        if text_to_type is None or not isinstance(text_to_type, str):
             # Allow empty string, but require 'text' key to be present
            raise ValidationError("Missing or invalid 'text' parameter (string expected).")
        if not isinstance(clear_first, bool):
            raise ValidationError("'clear_first' parameter must be a boolean (true/false).")


        logger.debug(f"TypeAction parameters validated: {locator_type}='{locator_value}', text='{text_to_type}', clear={clear_first}")

    # ... _execute method remains the same ...