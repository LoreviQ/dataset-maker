"""Test scrape module"""

import pytest

from scrape import get_tags


def test_get_tags(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test get_tags function."""
    monkeypatch.setattr("builtins.input", lambda _: "python dataset maker")
    tags = get_tags()
    assert tags == "python+dataset+maker"
