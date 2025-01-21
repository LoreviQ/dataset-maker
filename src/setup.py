"""Setup file for project."""

import os
from pathlib import Path


def prepare_project_directory():
    """Create project directory in home folder and change to it."""
    # Get project name from user
    project_name = input("Enter project name: ")

    # Get home directory and create full path
    home_dir = str(Path.home())
    project_path = os.path.join(home_dir, "Loras", project_name)

    # Create directory if it doesn't exist
    os.makedirs(project_path, exist_ok=True)

    # Change current working directory to project directory
    os.chdir(project_path)
    print(f"Created and switched to directory: {project_path}")
