import sys
import os
import logging
import traceback
import importlib

# Set up basic logging for the runner itself
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure the 'src' directory is discoverable.
# Adding the project root to sys.path allows imports like 'from src.some_module ...'
# This assumes run.py is in the project root directory.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Attempt to import and run the main application entry point
# Define the target module and function
TARGET_MODULE = "src.main_ui" # Or "src.main_ui_refactored_v4" etc. if preferred
TARGET_FUNCTION = "main"

try:
    logging.info(f"Attempting to import '{TARGET_FUNCTION}' from '{TARGET_MODULE}'...")
    # Dynamically import the module
    main_ui_module = importlib.import_module(TARGET_MODULE)

    # Check if the target function exists
    if hasattr(main_ui_module, TARGET_FUNCTION) and callable(getattr(main_ui_module, TARGET_FUNCTION)):
        main_function = getattr(main_ui_module, TARGET_FUNCTION)
        logging.info(f"Found '{TARGET_FUNCTION}'. Executing...")
        # Execute the main function
        main_function()
        logging.info("Application finished.")
    else:
        # Log an error if the function isn't found or isn't callable
        logging.error(f"Error: Module '{TARGET_MODULE}' does not have a callable function named '{TARGET_FUNCTION}'.")
        sys.exit(f"Could not find the main entry point '{TARGET_FUNCTION}' in '{TARGET_MODULE}'.")

except ImportError as e:
    # Log import errors clearly
    logging.error(f"Import Error: Failed to import '{TARGET_MODULE}'. Check module existence, dependencies, and potential circular imports.", exc_info=False)
    logging.error(f"Specific Error: {e}")
    # Provide guidance on potential issues
    print("\n--- Troubleshooting ---")
    print(f"1. Ensure the file '{TARGET_MODULE.replace('.', '/')}.py' exists.")
    print(f"2. Check if all dependencies in requirements.txt are installed (pip install -r requirements.txt).")
    print(f"3. Look for errors during the import process above (e.g., errors inside {TARGET_MODULE}.py).")
    print(f"4. Check Python Path: {sys.path}")
    print("---------------------\n")
    sys.exit(f"Failed to start application due to ImportError: {e}")

except Exception as e:
    # Catch any other exceptions during startup or execution
    logging.error(f"An unexpected error occurred during application execution.", exc_info=True) # Log full traceback here
    print(f"\n--- Runtime Error ---")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Details: {e}")
    print("Traceback:")
    traceback.print_exc() # Also print traceback to console for immediate visibility
    print("---------------------\n")
    sys.exit(f"Application failed with an unexpected error: {e}")

# Note: The manipulation of sys.modules['__main__'].__dict__ has been removed.
# Required types (Optional, Dict, etc.) should be imported within the modules that need them.
# The use of exec() has been removed and replaced with standard import mechanisms.
