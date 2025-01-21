"""Test config module"""

import pytest


@pytest.fixture
def test_config(tmp_path):
    """Create a test configuration"""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
paths:
  dataset: "test_dataset"
    """
    )
    return config_path
