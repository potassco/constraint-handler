import pytest
import logging
import os
from clingspector.checker import Checker, Flags
from clingspector.diagnostics import DiagnosticType, UndefinedVariableDiagnostic
from clingspector.utils.log_formatter import LoggingFormatter

# Configure logging for tests
logger = logging.getLogger("clingspector")
handler = logging.StreamHandler()
handler.setFormatter(LoggingFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Fixture to create a Checker instance
@pytest.fixture
def checker():
    return Checker()

# Helper to get path to test files
TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files")

def test_valid_program(checker: Checker):
    file_path = os.path.join(TEST_FILES_DIR, "valid.lp")
    checker.load([file_path])
    checker.solve()
    diagnostics = checker.get_diagnostics()
    assert len(diagnostics) == 0

def test_undefined_variable(checker: Checker):
    file_path = os.path.join(TEST_FILES_DIR, "undefined_variable.lp")
    checker.set_flags(Flags.VERBOSE, False)
    checker.load([file_path])
    checker.solve()
    diagnostics = checker.get_diagnostics()
    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert diag.type == DiagnosticType.UNDEFINED_VARIABLE
    # assert isinstance(diag, UndefinedVariableDiagnostic) 
    assert diag.variable == "x"
    assert diag.dependent_variable == "y"

# def test_cyclic_dependency(checker: Checker):
#     file_path = os.path.join(TEST_FILES_DIR, "cycle.lp")
#     checker.set_flags(Flags.VERBOSE, False)
#     checker.load([file_path])
#     checker.solve()
#     diagnostics = checker.get_diagnostics()
#     assert any(diag.type == DiagnosticType.CYCLIC_DEPENDENCY for diag in diagnostics)
#     cycle_diag = next(diag for diag in diagnostics if diag.type == DiagnosticType.CYCLIC_DEPENDENCY)
#     assert set(cycle_diag.variables) == {"x", "y"}