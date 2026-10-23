"""Smoke tests for the installed package."""

from importlib.metadata import metadata
from importlib.resources import files

import constraint_handler


def test_package_is_installed() -> None:
    """Verify installed package metadata and the bundled typing marker."""
    assert metadata("constraint-handler")["Name"] == "constraint-handler"
    assert files(constraint_handler).joinpath("py.typed").is_file()
