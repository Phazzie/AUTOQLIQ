import os

# Create the main archive directory
os.makedirs("archived_files", exist_ok=True)

# Create subdirectories
subdirs = ["scripts", "logs", "docs", "temp"]
for subdir in subdirs:
    os.makedirs(os.path.join("archived_files", subdir), exist_ok=True)

print("Created archive directories:")
for subdir in subdirs:
    print(f"- archived_files/{subdir}")
