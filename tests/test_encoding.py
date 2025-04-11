import clingo.script
import clingo.symbol
from clintest.test import And, Assert
from clintest.quantifier import All, Any
from clintest.assertion import Contains
from clintest.solver import Clingo

clingo.script.enable_python()


def atoms_from_file(file_name):
    try:
        with open(file_name, "r") as f:
            contents = f.read().split()
            return [clingo.symbol.parse_term(atom) for atom in contents]
    except FileNotFoundError:
        # print("missing file",file_name)
        return []


def run_test(name):
    solver = Clingo("0", "#show value/3.", files=[name + ".lp"])
    expected_all = atoms_from_file(name + ".expected.all")
    test_all = And(*(Assert(All(), Contains(a)) for a in expected_all))
    expected_any = atoms_from_file(name + ".expected.any")
    test_any = And(*(Assert(Any(), Contains(a)) for a in expected_any))
    test = And(test_all, test_any)
    solver.solve(test)
    test.assert_()


def test_basic_tests():
    run_test("tests/example/booleans")

def test_basic_assignments():
    run_test("tests/example/basic_assignments")

def test_conditional_assign():
    run_test("tests/example/conditional_assign")

def test_set_manipulations():
    run_test("tests/example/set_manipulations")

if __name__ == "__main__":
    test_basic_tests()
    test_basic_assignments()
    test_conditional_assign()
    test_set_manipulations()