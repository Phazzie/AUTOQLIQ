"""Test script for the CredentialService."""

import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from src.infrastructure.repositories.credential_repository import FileSystemCredentialRepository
from src.application.services.credential_service import CredentialService

def main():
    """Test the CredentialService."""
    # Create a test credentials file
    test_file = "test_credentials.json"

    # Delete the file if it exists
    if os.path.exists(test_file):
        os.remove(test_file)

    # Create the repository and service
    repository = FileSystemCredentialRepository(test_file)
    service = CredentialService(repository)

    # Test creating a credential
    print("Creating credential...")
    result = service.create_credential("test_cred", "testuser", "testpassword")
    print(f"Create result: {result}")

    # Test listing credentials
    print("\nListing credentials...")
    credentials = service.list_credentials()
    print(f"Credentials: {credentials}")

    # Test getting a credential
    print("\nGetting credential...")
    credential = service.get_credential("test_cred")
    print(f"Credential: {credential}")
    print(f"Username: {credential.username}")
    print(f"Password hash: {credential.password_hash}")
    print(f"Salt: {credential.salt}")

    # Test verifying a credential with correct password
    print("\nVerifying credential with correct password...")
    verify_result = service.verify_credential("test_cred", "testpassword")
    print(f"Verify result: {verify_result}")

    # Test verifying a credential with incorrect password
    print("\nVerifying credential with incorrect password...")
    verify_result = service.verify_credential("test_cred", "wrongpassword")
    print(f"Verify result: {verify_result}")

    # Test deleting a credential
    print("\nDeleting credential...")
    delete_result = service.delete_credential("test_cred")
    print(f"Delete result: {delete_result}")

    # Test listing credentials after deletion
    print("\nListing credentials after deletion...")
    credentials = service.list_credentials()
    print(f"Credentials: {credentials}")

    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    main()
