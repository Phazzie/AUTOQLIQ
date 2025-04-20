import logging
from src.config import config

def setup_logging() -> None:
    """Configure root and file handlers using settings from AppConfig."""
    root = logging.getLogger()
    root.setLevel(config.log_level)

    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(config.log_level)
    console.setFormatter(fmt)
    root.addHandler(console)

    # File handler
    file_handler = logging.FileHandler(config.log_file)
    file_handler.setLevel(config.log_level)
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)