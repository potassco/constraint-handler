"""Smoke tests for the installed package."""

from importlib.metadata import metadata
from importlib.resources import files
from pathlib import Path

import pytest

import constraint_handler


def test_package_is_installed() -> None:
    """Verify installed metadata, the typing marker, and the bundled encodings."""
    assert metadata("constraint-handler")["Name"] == "constraint-handler"
    assert files(constraint_handler).joinpath("py.typed").is_file()
    for encoding in (
        "native.lp",
        "boolean.lp",
        "integer.lp",
        "complex.lp",
    ):
        assert files(constraint_handler).joinpath("encoding", encoding).is_file()


def test_native_encoding_is_independent_of_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Load the bundled encoding from an installed package outside the source tree."""
    monkeypatch.chdir(tmp_path)
    preprocessor = constraint_handler.Preprocessor(
        constraint_handler.PreprocessOptions()
    )
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    solver = prepared.create_solver(constraint_handler.SolveOptions())
    assert solver.solve().satisfiable
