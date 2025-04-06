"""Form validator for UI components."""
import re
from typing import Dict, Any, List, Optional, Callable, Union

from src.core.exceptions import UIError


class ValidationError(UIError):
    """Error raised when form validation fails."""
    
    def __init__(self, message: str, field_name: Optional[str] = None):
        """Initialize a ValidationError.
        
        Args:
            message: The error message
            field_name: The name of the field that failed validation
        """
        super().__init__(message, component_name="FormValidator")
        self.field_name = field_name


class FormValidator:
    """Validator for form inputs.
    
    This class provides methods for validating form inputs with various rules.
    """
    
    @staticmethod
    def validate_required(value: str, field_name: str) -> None:
        """Validate that a field is not empty.
        
        Args:
            value: The value to validate
            field_name: The name of the field
            
        Raises:
            ValidationError: If the field is empty
        """
        if not value:
            raise ValidationError(f"{field_name} is required", field_name=field_name)
    
    @staticmethod
    def validate_min_length(value: str, min_length: int, field_name: str) -> None:
        """Validate that a field has a minimum length.
        
        Args:
            value: The value to validate
            min_length: The minimum length required
            field_name: The name of the field
            
        Raises:
            ValidationError: If the field is shorter than the minimum length
        """
        if len(value) < min_length:
            raise ValidationError(
                f"{field_name} must be at least {min_length} characters long", 
                field_name=field_name
            )
    
    @staticmethod
    def validate_max_length(value: str, max_length: int, field_name: str) -> None:
        """Validate that a field has a maximum length.
        
        Args:
            value: The value to validate
            max_length: The maximum length allowed
            field_name: The name of the field
            
        Raises:
            ValidationError: If the field is longer than the maximum length
        """
        if len(value) > max_length:
            raise ValidationError(
                f"{field_name} must be at most {max_length} characters long", 
                field_name=field_name
            )
    
    @staticmethod
    def validate_pattern(value: str, pattern: str, field_name: str, error_message: Optional[str] = None) -> None:
        """Validate that a field matches a pattern.
        
        Args:
            value: The value to validate
            pattern: The regular expression pattern to match
            field_name: The name of the field
            error_message: A custom error message
            
        Raises:
            ValidationError: If the field does not match the pattern
        """
        if not re.match(pattern, value):
            message = error_message or f"{field_name} has an invalid format"
            raise ValidationError(message, field_name=field_name)
    
    @staticmethod
    def validate_email(value: str, field_name: str) -> None:
        """Validate that a field is a valid email address.
        
        Args:
            value: The value to validate
            field_name: The name of the field
            
        Raises:
            ValidationError: If the field is not a valid email address
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        FormValidator.validate_pattern(
            value, pattern, field_name, f"{field_name} must be a valid email address"
        )
    
    @staticmethod
    def validate_url(value: str, field_name: str) -> None:
        """Validate that a field is a valid URL.
        
        Args:
            value: The value to validate
            field_name: The name of the field
            
        Raises:
            ValidationError: If the field is not a valid URL
        """
        pattern = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"
        FormValidator.validate_pattern(
            value, pattern, field_name, f"{field_name} must be a valid URL"
        )
    
    @staticmethod
    def validate_numeric(value: str, field_name: str) -> None:
        """Validate that a field contains only numeric characters.
        
        Args:
            value: The value to validate
            field_name: The name of the field
            
        Raises:
            ValidationError: If the field contains non-numeric characters
        """
        if not value.isdigit():
            raise ValidationError(
                f"{field_name} must contain only numeric characters", 
                field_name=field_name
            )
    
    @staticmethod
    def validate_alpha(value: str, field_name: str) -> None:
        """Validate that a field contains only alphabetic characters.
        
        Args:
            value: The value to validate
            field_name: The name of the field
            
        Raises:
            ValidationError: If the field contains non-alphabetic characters
        """
        if not value.isalpha():
            raise ValidationError(
                f"{field_name} must contain only alphabetic characters", 
                field_name=field_name
            )
    
    @staticmethod
    def validate_alphanumeric(value: str, field_name: str) -> None:
        """Validate that a field contains only alphanumeric characters.
        
        Args:
            value: The value to validate
            field_name: The name of the field
            
        Raises:
            ValidationError: If the field contains non-alphanumeric characters
        """
        if not value.isalnum():
            raise ValidationError(
                f"{field_name} must contain only alphanumeric characters", 
                field_name=field_name
            )
    
    @staticmethod
    def validate_custom(value: str, validator: Callable[[str], bool], field_name: str, error_message: str) -> None:
        """Validate a field using a custom validator function.
        
        Args:
            value: The value to validate
            validator: A function that takes a string and returns a boolean
            field_name: The name of the field
            error_message: The error message to display if validation fails
            
        Raises:
            ValidationError: If the validator returns False
        """
        if not validator(value):
            raise ValidationError(error_message, field_name=field_name)
    
    @staticmethod
    def validate_form(form_data: Dict[str, str], rules: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[str]]:
        """Validate a form against a set of rules.
        
        Args:
            form_data: A dictionary of form field names and values
            rules: A dictionary of field names and validation rules
            
        Returns:
            A dictionary of field names and error messages, or an empty dictionary if validation passes
            
        Example:
            ```python
            form_data = {"name": "John", "email": "invalid-email"}
            rules = {
                "name": [
                    {"type": "required"},
                    {"type": "min_length", "min_length": 3}
                ],
                "email": [
                    {"type": "required"},
                    {"type": "email"}
                ]
            }
            errors = FormValidator.validate_form(form_data, rules)
            # errors = {"email": ["Email must be a valid email address"]}
            ```
        """
        errors: Dict[str, List[str]] = {}
        
        for field_name, field_rules in rules.items():
            field_errors: List[str] = []
            value = form_data.get(field_name, "")
            
            for rule in field_rules:
                try:
                    rule_type = rule.get("type", "")
                    
                    if rule_type == "required":
                        FormValidator.validate_required(value, field_name)
                    elif rule_type == "min_length":
                        FormValidator.validate_min_length(value, rule.get("min_length", 0), field_name)
                    elif rule_type == "max_length":
                        FormValidator.validate_max_length(value, rule.get("max_length", 0), field_name)
                    elif rule_type == "pattern":
                        FormValidator.validate_pattern(
                            value, 
                            rule.get("pattern", ""), 
                            field_name, 
                            rule.get("error_message")
                        )
                    elif rule_type == "email":
                        FormValidator.validate_email(value, field_name)
                    elif rule_type == "url":
                        FormValidator.validate_url(value, field_name)
                    elif rule_type == "numeric":
                        FormValidator.validate_numeric(value, field_name)
                    elif rule_type == "alpha":
                        FormValidator.validate_alpha(value, field_name)
                    elif rule_type == "alphanumeric":
                        FormValidator.validate_alphanumeric(value, field_name)
                    elif rule_type == "custom":
                        FormValidator.validate_custom(
                            value, 
                            rule.get("validator", lambda x: True), 
                            field_name, 
                            rule.get("error_message", f"Invalid {field_name}")
                        )
                except ValidationError as e:
                    field_errors.append(str(e))
            
            if field_errors:
                errors[field_name] = field_errors
        
        return errors
