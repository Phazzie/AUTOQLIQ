"""Sample code with various code quality issues.

This module contains examples of code that violates SOLID, KISS, and DRY principles.
"""

import os
import sys
import re
import json
import datetime
from typing import Dict, List, Any, Optional

# SRP Violation: Class with multiple responsibilities
class UserManager:
    """User manager class that handles user data, authentication, and file operations."""
    
    def __init__(self, db_path: str):
        """Initialize the user manager.
        
        Args:
            db_path: Path to the user database file
        """
        self.db_path = db_path
        self.users = {}
        self.load_users()
    
    def load_users(self) -> None:
        """Load users from the database file."""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r') as f:
                    self.users = json.load(f)
            else:
                self.users = {}
        except Exception as e:
            print(f"Error loading users: {str(e)}")
            self.users = {}
    
    def save_users(self) -> None:
        """Save users to the database file."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {str(e)}")
    
    def add_user(self, username: str, password: str, email: str) -> bool:
        """Add a new user.
        
        Args:
            username: The username
            password: The password
            email: The email address
            
        Returns:
            True if the user was added successfully, False otherwise
        """
        if username in self.users:
            return False
        
        if not self.validate_email(email):
            return False
        
        if not self.validate_password(password):
            return False
        
        self.users[username] = {
            "password": self.hash_password(password),
            "email": email,
            "created_at": datetime.datetime.now().isoformat(),
            "last_login": None
        }
        
        self.save_users()
        return True
    
    def validate_email(self, email: str) -> bool:
        """Validate an email address.
        
        Args:
            email: The email address to validate
            
        Returns:
            True if the email is valid, False otherwise
        """
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None
    
    def validate_password(self, password: str) -> bool:
        """Validate a password.
        
        Args:
            password: The password to validate
            
        Returns:
            True if the password is valid, False otherwise
        """
        # Password must be at least 8 characters long
        if len(password) < 8:
            return False
        
        # Password must contain at least one uppercase letter
        if not any(c.isupper() for c in password):
            return False
        
        # Password must contain at least one lowercase letter
        if not any(c.islower() for c in password):
            return False
        
        # Password must contain at least one digit
        if not any(c.isdigit() for c in password):
            return False
        
        # Password must contain at least one special character
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in password):
            return False
        
        return True
    
    def hash_password(self, password: str) -> str:
        """Hash a password.
        
        Args:
            password: The password to hash
            
        Returns:
            The hashed password
        """
        # This is a simple hash function for demonstration purposes
        # In a real application, use a proper password hashing library
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate a user.
        
        Args:
            username: The username
            password: The password
            
        Returns:
            True if the authentication was successful, False otherwise
        """
        if username not in self.users:
            return False
        
        if self.users[username]["password"] != self.hash_password(password):
            return False
        
        self.users[username]["last_login"] = datetime.datetime.now().isoformat()
        self.save_users()
        
        return True
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get a user by username.
        
        Args:
            username: The username
            
        Returns:
            The user data, or None if the user does not exist
        """
        return self.users.get(username)
    
    def delete_user(self, username: str) -> bool:
        """Delete a user.
        
        Args:
            username: The username
            
        Returns:
            True if the user was deleted successfully, False otherwise
        """
        if username not in self.users:
            return False
        
        del self.users[username]
        self.save_users()
        
        return True
    
    def backup_database(self, backup_path: str) -> bool:
        """Backup the user database.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            True if the backup was successful, False otherwise
        """
        try:
            with open(backup_path, 'w') as f:
                json.dump(self.users, f, indent=2)
            return True
        except Exception as e:
            print(f"Error backing up database: {str(e)}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore the user database from a backup.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            True if the restore was successful, False otherwise
        """
        try:
            with open(backup_path, 'r') as f:
                self.users = json.load(f)
            self.save_users()
            return True
        except Exception as e:
            print(f"Error restoring database: {str(e)}")
            return False
    
    def generate_report(self, report_path: str) -> bool:
        """Generate a report of all users.
        
        Args:
            report_path: Path to the report file
            
        Returns:
            True if the report was generated successfully, False otherwise
        """
        try:
            with open(report_path, 'w') as f:
                f.write("User Report\n")
                f.write("==========\n\n")
                
                for username, user_data in self.users.items():
                    f.write(f"Username: {username}\n")
                    f.write(f"Email: {user_data['email']}\n")
                    f.write(f"Created: {user_data['created_at']}\n")
                    f.write(f"Last Login: {user_data['last_login']}\n")
                    f.write("\n")
            
            return True
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            return False

# KISS Violation: Complex method with deep nesting and high cyclomatic complexity
def process_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process a list of data items.
    
    Args:
        data: List of data items
        
    Returns:
        Processed data
    """
    result = {
        "total_items": len(data),
        "processed_items": 0,
        "valid_items": 0,
        "invalid_items": 0,
        "categories": {},
        "tags": {},
        "stats": {
            "min_value": float('inf'),
            "max_value": float('-inf'),
            "sum": 0,
            "average": 0
        }
    }
    
    for item in data:
        result["processed_items"] += 1
        
        if "id" not in item or "value" not in item:
            result["invalid_items"] += 1
            continue
        
        if not isinstance(item["id"], str) or not isinstance(item["value"], (int, float)):
            result["invalid_items"] += 1
            continue
        
        result["valid_items"] += 1
        
        # Update stats
        value = item["value"]
        result["stats"]["min_value"] = min(result["stats"]["min_value"], value)
        result["stats"]["max_value"] = max(result["stats"]["max_value"], value)
        result["stats"]["sum"] += value
        
        # Process categories
        if "category" in item:
            category = item["category"]
            
            if category not in result["categories"]:
                result["categories"][category] = {
                    "count": 0,
                    "items": [],
                    "stats": {
                        "min_value": float('inf'),
                        "max_value": float('-inf'),
                        "sum": 0,
                        "average": 0
                    }
                }
            
            result["categories"][category]["count"] += 1
            result["categories"][category]["items"].append(item["id"])
            result["categories"][category]["stats"]["min_value"] = min(result["categories"][category]["stats"]["min_value"], value)
            result["categories"][category]["stats"]["max_value"] = max(result["categories"][category]["stats"]["max_value"], value)
            result["categories"][category]["stats"]["sum"] += value
        
        # Process tags
        if "tags" in item and isinstance(item["tags"], list):
            for tag in item["tags"]:
                if not isinstance(tag, str):
                    continue
                
                if tag not in result["tags"]:
                    result["tags"][tag] = {
                        "count": 0,
                        "items": [],
                        "stats": {
                            "min_value": float('inf'),
                            "max_value": float('-inf'),
                            "sum": 0,
                            "average": 0
                        }
                    }
                
                result["tags"][tag]["count"] += 1
                result["tags"][tag]["items"].append(item["id"])
                result["tags"][tag]["stats"]["min_value"] = min(result["tags"][tag]["stats"]["min_value"], value)
                result["tags"][tag]["stats"]["max_value"] = max(result["tags"][tag]["stats"]["max_value"], value)
                result["tags"][tag]["stats"]["sum"] += value
    
    # Calculate averages
    if result["valid_items"] > 0:
        result["stats"]["average"] = result["stats"]["sum"] / result["valid_items"]
    
    for category in result["categories"]:
        if result["categories"][category]["count"] > 0:
            result["categories"][category]["stats"]["average"] = result["categories"][category]["stats"]["sum"] / result["categories"][category]["count"]
    
    for tag in result["tags"]:
        if result["tags"][tag]["count"] > 0:
            result["tags"][tag]["stats"]["average"] = result["tags"][tag]["stats"]["sum"] / result["tags"][tag]["count"]
    
    return result

# DRY Violation: Duplicate code
def validate_user_input(username: str, email: str, age: int) -> List[str]:
    """Validate user input.
    
    Args:
        username: The username
        email: The email address
        age: The age
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Validate username
    if not username:
        errors.append("Username is required")
    elif len(username) < 3:
        errors.append("Username must be at least 3 characters long")
    elif len(username) > 20:
        errors.append("Username must be at most 20 characters long")
    elif not re.match(r"^[a-zA-Z0-9_]+$", username):
        errors.append("Username can only contain letters, numbers, and underscores")
    
    # Validate email
    if not email:
        errors.append("Email is required")
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors.append("Email is invalid")
    
    # Validate age
    if age < 18:
        errors.append("You must be at least 18 years old")
    elif age > 120:
        errors.append("Age is invalid")
    
    return errors

def validate_product_input(name: str, description: str, price: float) -> List[str]:
    """Validate product input.
    
    Args:
        name: The product name
        description: The product description
        price: The product price
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Validate name
    if not name:
        errors.append("Name is required")
    elif len(name) < 3:
        errors.append("Name must be at least 3 characters long")
    elif len(name) > 50:
        errors.append("Name must be at most 50 characters long")
    elif not re.match(r"^[a-zA-Z0-9 ]+$", name):
        errors.append("Name can only contain letters, numbers, and spaces")
    
    # Validate description
    if not description:
        errors.append("Description is required")
    elif len(description) < 10:
        errors.append("Description must be at least 10 characters long")
    elif len(description) > 1000:
        errors.append("Description must be at most 1000 characters long")
    
    # Validate price
    if price <= 0:
        errors.append("Price must be greater than 0")
    elif price > 10000:
        errors.append("Price is too high")
    
    return errors

# DRY Violation: Repeated string literals
def generate_error_message(error_code: int) -> str:
    """Generate an error message.
    
    Args:
        error_code: The error code
        
    Returns:
        The error message
    """
    if error_code == 1:
        return "An error occurred while processing your request. Please try again later."
    elif error_code == 2:
        return "Invalid input. Please check your input and try again."
    elif error_code == 3:
        return "Permission denied. You do not have permission to perform this action."
    elif error_code == 4:
        return "Resource not found. The requested resource could not be found."
    elif error_code == 5:
        return "An error occurred while processing your request. Please try again later."
    else:
        return "An unknown error occurred. Please contact support for assistance."

def log_error(error_code: int, message: str) -> None:
    """Log an error.
    
    Args:
        error_code: The error code
        message: The error message
    """
    print(f"Error {error_code}: {message}")
    
    if error_code == 1:
        print("An error occurred while processing your request. Please try again later.")
    elif error_code == 2:
        print("Invalid input. Please check your input and try again.")
    elif error_code == 3:
        print("Permission denied. You do not have permission to perform this action.")
    elif error_code == 4:
        print("Resource not found. The requested resource could not be found.")
    elif error_code == 5:
        print("An error occurred while processing your request. Please try again later.")
    else:
        print("An unknown error occurred. Please contact support for assistance.")

# DRY Violation: Repeated numeric constants
def calculate_price(base_price: float, quantity: int, discount: float = 0) -> float:
    """Calculate the price.
    
    Args:
        base_price: The base price
        quantity: The quantity
        discount: The discount
        
    Returns:
        The calculated price
    """
    # Apply quantity discount
    if quantity >= 10:
        base_price *= 0.9  # 10% discount
    elif quantity >= 5:
        base_price *= 0.95  # 5% discount
    
    # Apply additional discount
    if discount > 0:
        base_price *= (1 - discount)
    
    # Apply tax
    tax_rate = 0.08  # 8% tax
    price_with_tax = base_price * (1 + tax_rate)
    
    # Apply shipping
    if price_with_tax < 50:
        shipping = 5.99
    else:
        shipping = 0
    
    return price_with_tax + shipping

def calculate_total(subtotal: float, tax_rate: float = 0.08, shipping_threshold: float = 50, shipping_cost: float = 5.99) -> float:
    """Calculate the total.
    
    Args:
        subtotal: The subtotal
        tax_rate: The tax rate
        shipping_threshold: The shipping threshold
        shipping_cost: The shipping cost
        
    Returns:
        The calculated total
    """
    # Apply tax
    tax = subtotal * tax_rate
    
    # Apply shipping
    if subtotal < shipping_threshold:
        shipping = shipping_cost
    else:
        shipping = 0
    
    return subtotal + tax + shipping

if __name__ == "__main__":
    # Example usage
    user_manager = UserManager("users.json")
    user_manager.add_user("john_doe", "P@ssw0rd!", "john.doe@example.com")
    
    data = [
        {"id": "item1", "value": 10, "category": "A", "tags": ["tag1", "tag2"]},
        {"id": "item2", "value": 20, "category": "B", "tags": ["tag2", "tag3"]},
        {"id": "item3", "value": 30, "category": "A", "tags": ["tag1", "tag3"]}
    ]
    
    result = process_data(data)
    print(json.dumps(result, indent=2))
    
    errors = validate_user_input("john_doe", "john.doe@example.com", 25)
    print(errors)
    
    price = calculate_price(100, 5)
    print(f"Price: ${price:.2f}")
