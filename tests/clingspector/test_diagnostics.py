import pytest
import logging
import os
from clingspector.checker import Checker
from clingspector.diagnostic import DiagnosticType
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

def test_valid_program(checker: Checker):
    file_path = os.path.join(TEST_FILES_DIR, "valid.lp")
    checker.load([file_path])
    checker.solve()
    diagnostics = checker.get_diagnostics()
    assert len(diagnostics) == 0

def test_undefined_variable(checker: Checker):
    file_path = os.path.join(TEST_FILES_DIR, "undefined_variable.lp")
    checker.load([file_path])
    checker.solve()
    diagnostics = checker.get_diagnostics()
    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert diag.type == DiagnosticType.UNDEFINED_VARIABLE
    # assert isinstance(diag, UndefinedVariableDiagnostic) 
    assert diag.variable == "x"
    assert diag.dependent_variable == "y"

def test_cyclic_dependency(checker: Checker):
    file_path = os.path.join(TEST_FILES_DIR, "cycle.lp")
    checker.load([file_path])
    checker.solve()
    diagnostics = checker.get_diagnostics()
    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert diag.type == DiagnosticType.CYCLIC_DEPENDENCY
    assert diag.involved_variables == ["x", "y"]