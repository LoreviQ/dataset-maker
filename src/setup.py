"""Setup file for project."""

import os
import shutil
from pathlib import Path


def get_package_root() -> Path:
    """Get the root directory of the package"""
    return Path(__file__).parent.parent


def prepare_project_directory() -> None:
    """Create project directory in home folder and change to it."""
    # Get project name from user
    project_name = input("Enter project name: ")

    # Get home directory and create full path
    home_dir = str(Path.home())
    project_path = Path(home_dir) / "Loras" / project_name

    # Create directory if it doesn't exist
    project_path.mkdir(parents=True, exist_ok=True)

    # Copy default config to project directory
    default_config = get_package_root() / "config.yaml"
    project_config = project_path / "config.yaml"

    if not project_config.exists():
        shutil.copy2(default_config, project_config)

    # Change current working directory to project directory
    os.chdir(project_path)
    print(f"Created and switched to directory: {project_path}")
