import logging
# ... existing imports ...
from src.core.actions.constants import SUPPORTED_LOCATORS # Import the constant

logger = logging.getLogger(__name__)

# Remove the local definition:
# SUPPORTED_LOCATORS = ["id", "xpath", "css selector", "name", "link text", "partial link text", "tag name", "class name"]

class ClickAction(ActionBase):
    """Action to find an element and click it."""

    def validate_parameters(self) -> None:
        """Validate 'locator_type' and 'locator_value' parameters."""
        locator_type = self.parameters.get("locator_type")
        locator_value = self.parameters.get("locator_value")

        if not locator_type or not isinstance(locator_type, str):
            raise ValidationError("Missing or invalid 'locator_type' parameter (string expected).")
        # Use the imported constant
        if locator_type.lower() not in SUPPORTED_LOCATORS:
            raise ValidationError(f"Unsupported locator_type: '{locator_type}'. Supported: {SUPPORTED_LOCATORS}")
        if not locator_value or not isinstance(locator_value, str):
            raise ValidationError("Missing or invalid 'locator_value' parameter (string expected).")
        logger.debug(f"ClickAction parameters validated: {locator_type}='{locator_value}'")

    # ... _execute method remains the same ...