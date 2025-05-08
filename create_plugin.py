import shutil
import os
from pathlib import Path

# List of directories to copy
folders = [
    "core",
    "config",
    "orchestration/airflow_plugin/plugin_core",
    "orchestration/airflow_plugin/plugins"
]

# List of specific files to copy
files = [
    
]

# List of directories to create __init__.py files in (subdirectories)
init_files = [
    "orchestration",
    "orchestration/airflow_plugin",
    ""  # Empty string to represent the root directory
]

# Destination directory
destination = Path("plugin_extracted")

# Remove the destination directory if it exists
if destination.exists() and destination.is_dir():
    shutil.rmtree(destination)

# Create the destination directory
destination.mkdir(parents=True, exist_ok=True)

# Copy each folder to the destination, preserving structure
for folder in folders:
    source = Path(folder)
    dest = destination / source
    if source.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, dest)
    else:
        print(f"Warning: {source} does not exist and was skipped.")

# Copy specific files, preserving their relative paths
for file in files:
    source_file = Path(file)
    dest_file = destination / source_file
    if source_file.exists():
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, dest_file)
    else:
        print(f"Warning: {source_file} does not exist and was skipped.")

# Check if directory is empty or specified to be the root, and create __init__.py in appropriate locations
for directory in init_files:
    if directory == "":
        # If directory is empty, target the root of the destination
        target_dir = destination
    else:
        # Otherwise, target the specific subdirectory
        target_dir = destination / directory

    init_path = target_dir / "__init__.py"
    
    if not init_path.exists():
        init_path.parent.mkdir(parents=True, exist_ok=True)
        init_path.touch()  # Creates an empty __init__.py
        print(f"Created __init__.py in {target_dir}.")

print("Folders, files, and __init__.py files created successfully.")
