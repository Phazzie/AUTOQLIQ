import logging
# ... existing imports ...
from src.core.actions.constants import SUPPORTED_LOCATORS # Import the constant

logger = logging.getLogger(__name__)

# Remove the local definition:
# SUPPORTED_LOCATORS = ["id", "xpath", "css selector", "name", "link text", "partial link text", "tag name", "class name"]

class ReadAttributeAction(ActionBase):
    """Action to find an element and read the value of one of its attributes."""

    def validate_parameters(self) -> None:
        """Validate locator and attribute_name parameters."""
        locator_type = self.parameters.get("locator_type")
        locator_value = self.parameters.get("locator_value")
        attribute_name = self.parameters.get("attribute_name")

        if not locator_type or not isinstance(locator_type, str):
            raise ValidationError("Missing or invalid 'locator_type' parameter (string expected).")
        # Use the imported constant
        if locator_type.lower() not in SUPPORTED_LOCATORS:
            raise ValidationError(f"Unsupported locator_type: '{locator_type}'. Supported: {SUPPORTED_LOCATORS}")
        # ... rest of validation ...
        if not locator_value or not isinstance(locator_value, str):
            raise ValidationError("Missing or invalid 'locator_value' parameter (string expected).")
        if not attribute_name or not isinstance(attribute_name, str):
            raise ValidationError("Missing or invalid 'attribute_name' parameter (string expected).")


        logger.debug(f"ReadAttributeAction parameters validated: {locator_type}='{locator_value}', attribute='{attribute_name}'")

    # ... _execute method remains the same ...