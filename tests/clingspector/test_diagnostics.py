"""Test cases for Clingspector diagnostics."""

import pytest
import logging
import os
from clingspector.checker import Checker
from clingspector.diagnostic import CyclicDependencyDiagnostic, UndefinedVariableDiagnostic
from clingspector.utils.log_formatter import LoggingFormatter

logger = logging.getLogger("clingspector")
handler = logging.StreamHandler()
handler.setFormatter(LoggingFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

@pytest.fixture
def checker():
    return Checker()

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files")

def test_valid(checker: Checker):
    """Test a valid program that should not produce any diagnostics."""

    file_path = os.path.join(TEST_FILES_DIR, "valid.lp")
    checker.load([file_path])
    checker.solve()
    diagnostics = checker.get_diagnostics()
    assert len(diagnostics) == 0

def test_undefined_variable(checker: Checker):
    """ Test a program with an undefined variable.
    
        This should produce a diagnostic indicating the undefined variable.
    """

    file_path = os.path.join(TEST_FILES_DIR, "undefined_variable.lp")
    checker.load([file_path])
    checker.solve()
    diagnostics = checker.get_diagnostics()
    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert isinstance(diag, UndefinedVariableDiagnostic)
    assert diag.variable == "x"
    assert diag.undefined_variable == "y"

def test_direct_cycle(checker: Checker):
    """ Test a program with a direct cyclic dependency.
    
        This should produce a diagnostic indicating the cyclic dependency.
    """

    file_path = os.path.join(TEST_FILES_DIR, "direct_cycle.lp")
    checker.load([file_path])
    checker.solve()
    diagnostics = checker.get_diagnostics()
    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert isinstance(diag, CyclicDependencyDiagnostic)
    assert diag.involved_variables == ["x"]

def test_simple_cycle(checker: Checker):
    """ Test a program with a simple cyclic dependency.
    
        This should produce a diagnostic indicating the cyclic dependency.
    """

    file_path = os.path.join(TEST_FILES_DIR, "simple_cycle.lp")
    checker.load([file_path])
    checker.solve()
    diagnostics = checker.get_diagnostics()
    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert isinstance(diag, CyclicDependencyDiagnostic)
    assert diag.involved_variables == ["x", "y"]

def test_overlapping_cycles(checker: Checker):
    """ Test a program with overlapping cycles.
    
        This should still only produce a single diagnostic 
        containing all involved variables.
    """

    file_path = os.path.join(TEST_FILES_DIR, "overlapping_cycle.lp")
    checker.load([file_path])
    checker.solve()
    diagnostics = checker.get_diagnostics()
    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert isinstance(diag, CyclicDependencyDiagnostic)
    assert diag.involved_variables == ["a", "b", "c", "d", "e"]