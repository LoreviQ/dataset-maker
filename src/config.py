"""Configuration loader for dataset-maker"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml


def get_package_root() -> Path:
    """Get the root directory of the package"""
    return Path(__file__).parent.parent


def get_project_dir() -> Path:
    """Get the current project directory"""
    return Path(os.getcwd())


def load_config() -> Dict[Any, Any]:
    """Load configuration from yaml file"""
    # Always load base config from package directory
    config_path = get_package_root() / "config.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Override with project-specific config if it exists
    project_config = get_project_dir() / "config.yaml"
    if project_config.exists():
        with open(project_config, "r", encoding="utf-8") as f:
            project_specific = yaml.safe_load(f)
            config.update(project_specific)

    # Add computed paths relative to project directory
    config["paths"]["dataset_dir"] = str(get_project_dir() / config["paths"]["dataset"])

    return config


# Load config at module level
CONFIG = load_config()
