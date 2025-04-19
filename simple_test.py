"""Simple test script for the CredentialService."""

import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a test credentials file
test_file = "test_credentials.json"

# Delete the file if it exists
if os.path.exists(test_file):
    os.remove(test_file)

# Create an empty file
with open(test_file, 'w') as f:
    f.write('{}')

print("Test file created successfully.")
print(f"Current directory: {os.getcwd()}")
print(f"Test file exists: {os.path.exists(test_file)}")

# Clean up
if os.path.exists(test_file):
    os.remove(test_file)
    print("Test file removed successfully.")
