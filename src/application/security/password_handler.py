"""Password Hashing and Verification Abstraction."""

import abc
import logging

# Attempt to import werkzeug, set availability flag
try:
    from werkzeug.security import generate_password_hash, check_password_hash
    WERKZEUG_AVAILABLE = True
except ImportError:
    generate_password_hash = None
    check_password_hash = None
    WERKZEUG_AVAILABLE = False

# Assuming AppConfig exists and provides security settings
# If not, use hardcoded defaults here or pass config object
try:
    from src.config import config as app_config
except ImportError:
    # Fallback config if src.config is not available during testing/refactoring
    class MockAppConfig:
        password_hash_method = "pbkdf2:sha256:600000" # Example default
    app_config = MockAppConfig()


logger = logging.getLogger(__name__)

class IPasswordHandler(abc.ABC):
    """Interface for password hashing and verification."""
    @abc.abstractmethod
    def hash_password(self, password: str) -> str:
        """Hashes the provided password."""
        pass

    @abc.abstractmethod
    def verify_password(self, stored_hash: str, provided_password: str) -> bool:
        """Verifies a provided password against a stored hash."""
        pass

class WerkzeugPasswordHandler(IPasswordHandler):
    """Password handler using Werkzeug security functions."""

    # Get hash method from config
    DEFAULT_HASH_METHOD = getattr(app_config, 'password_hash_method', "pbkdf2:sha256:600000")

    def hash_password(self, password: str) -> str:
        """Hashes the password using werkzeug or falls back to insecure plaintext."""
        if not WERKZEUG_AVAILABLE or not generate_password_hash:
            logger.critical("SECURITY RISK: Werkzeug not available. Storing password as plain text prefixed with 'plaintext:'. Ensure werkzeug is installed.")
            # Prefix indicates insecurity - DO NOT USE IN PRODUCTION WITHOUT WERKZEUG
            return f"plaintext:{password}"
        try:
            # Generate hash using configured method
            hashed = generate_password_hash(password, method=self.DEFAULT_HASH_METHOD)
            logger.debug("Password hashed successfully using Werkzeug.")
            return hashed
        except Exception as e:
            logger.exception("Failed to hash password using Werkzeug.")
            # Decide on fallback: raise error or use insecure? Raising is safer.
            raise RuntimeError("Password hashing failed.") from e

    def verify_password(self, stored_hash: str, provided_password: str) -> bool:
        """Verifies the password using werkzeug or falls back to insecure plaintext check."""
        if not stored_hash or not provided_password:
            logger.debug("Cannot verify password, either stored hash or provided password is empty.")
            return False # Cannot verify empty inputs

        if not WERKZEUG_AVAILABLE or not check_password_hash:
            logger.warning("Werkzeug not available. Attempting insecure plaintext password verification.")
            # Check for plaintext prefix added by insecure hash_password fallback
            if stored_hash.startswith("plaintext:"):
                match = stored_hash[len("plaintext:"):] == provided_password
                logger.debug(f"Plaintext comparison result: {match}")
                return match
            logger.error(f"Cannot verify password: Werkzeug unavailable and stored hash '{stored_hash[:10]}...' has unknown format.")
            return False # Cannot verify unknown hash format without werkzeug

        try:
            # Use werkzeug to check hash
            is_valid = check_password_hash(stored_hash, provided_password)
            logger.debug(f"Werkzeug password verification result: {is_valid}")
            return is_valid
        except Exception as e:
            # Log error during hash checking but return False for security
            logger.error(f"Error during password verification check: {e}")
            return False
