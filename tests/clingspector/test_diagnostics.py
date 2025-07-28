"""Test cases for Clingspector diagnostics."""

import logging
import os

import pytest

from clingspector.clingspector import Clingspector
from clingspector.diagnostic import CyclicDependencyDiagnostic, Diagnostic, UndefinedVariableDiagnostic, UnsupportedArgumentTypeDiagnostic, UnsupportedOperatorDiagnostic
from clingspector.utils.log_formatter import LoggingFormatter

logger = logging.getLogger("clingspector")
handler = logging.StreamHandler()
handler.setFormatter(LoggingFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files")


def get_diagnostics(file_name: str) -> list[Diagnostic]:
    """Load a Clingspector file and return the diagnostics."""

    clingspector = Clingspector()
    file_path = os.path.join(TEST_FILES_DIR, file_name)
    clingspector.load([file_path])
    clingspector.run()
    diagnostics = clingspector.get_diagnostics()

    return diagnostics
    

def test_valid():
    """Test a valid program that should not produce any diagnostics."""
    diagnostics = get_diagnostics("valid.lp")

    assert len(diagnostics) == 0


def test_undefined_variable():
    """Test a program with an undefined variable.

    This should produce a diagnostic indicating the undefined variable.
    """

    diagnostics = get_diagnostics("undefined_variable.lp")

    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert isinstance(diag, UndefinedVariableDiagnostic)
    assert diag.variable == "x"
    assert diag.undefined_variable == "y"


def test_direct_cycle():
    """Test a program with a direct cyclic dependency.

    This should produce a diagnostic indicating the cyclic dependency.
    """

    diagnostics = get_diagnostics("direct_cycle.lp")

    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert isinstance(diag, CyclicDependencyDiagnostic)
    assert diag.involved_variables == ["x"]


def test_simple_cycle():
    """Test a program with a simple cyclic dependency.

    This should produce a diagnostic indicating the cyclic dependency.
    """

    diagnostics = get_diagnostics("simple_cycle.lp")

    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert isinstance(diag, CyclicDependencyDiagnostic)
    assert diag.involved_variables == ["x", "y"]


def test_overlapping_cycles():
    """Test a program with overlapping cycles.

    This should still only produce a single diagnostic
    containing all involved variables.
    """

    diagnostics = get_diagnostics("overlapping_cycle.lp")

    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert isinstance(diag, CyclicDependencyDiagnostic)
    assert diag.involved_variables == ["a", "b", "c", "d", "e"]

def test_unsupported_operator():
    """Test a program with an unsupported operator.

    This should produce a diagnostic indicating the unsupported operator.
    """

    diagnostics = get_diagnostics("unsupported_operator_type.lp")

    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert isinstance(diag, UnsupportedOperatorDiagnostic)
    assert diag.operator == "nonsense"

def test_unsupported_argument_type():
    """Test a program with an unsupported argument type.

    This should produce a diagnostic indicating the unsupported argument type.
    """

    diagnostics = get_diagnostics("unsupported_argument_type.lp")

    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert isinstance(diag, UnsupportedArgumentTypeDiagnostic)
    assert diag.operator == "add"
    assert diag.arguments == ["int", "float"]