"""Browser type enumeration for WebDriver implementations."""
import enum

class BrowserType(enum.Enum):
    """Enum representing supported browser types."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
