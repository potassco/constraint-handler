from typing import Optional, Sequence

import clingo
import clingo.symbol
import clintest.solver
import clintest.test

from clintest.assertion import Contains
from clintest.quantifier import All, Any
from clintest.test import And, Assert


def atoms_from_file(file_name):
    try:
        with open(file_name, "r") as f:
            contents = f.read().split()
            return [clingo.symbol.parse_term(atom) for atom in contents]
    except FileNotFoundError:
        # print("missing file",file_name)
        return []

def build_expectations(name):
    expected_all = atoms_from_file(name + ".expected.all")
    test_all = And(*(Assert(All(), Contains(a)) for a in expected_all))
    expected_any = atoms_from_file(name + ".expected.any")
    test_any = And(*(Assert(Any(), Contains(a)) for a in expected_any))
    return And(test_all, test_any)

class PropPrint(clingo.propagator.Propagator):
    def __init__(self):
        print("creation")
        pass

    def init(self, init):
        print("init")
        pass

    def propagate(self, ctl, changes):
        for a in changes:
            print(a,end=" ")
        print()

    def check(self, ctl):
        print("check",len(ctl.assignment.trail))


class SolverWithPropagators(clintest.solver.Solver):

    def __init__(
        self,
        arguments: Optional[Sequence[str]] = None,
        program: Optional[str] = None,
        files: Optional[Sequence[str]] = None,
        propagators: list[clingo.propagator.Propagator] = [],
    ) -> None:
        self.__arguments = [] if arguments is None else arguments
        self.__program = "" if program is None else program
        self.__files = [] if files is None else files
        self.__propgators = [] if not len(propagators) else propagators

    def wrap(self,test,props,method):
        def fn(*args, **kwargs):
            for prop in props:
                if hasattr(prop,method) and callable(getattr(prop,method)):
                    getattr(prop,method)(*args, **kwargs)
            getattr(test,method)(*args, **kwargs)
        return fn

    def solve(self, test: clintest.test.Test) -> None:
        ctl = clingo.Control(self.__arguments)

        ctl.add("base", [], self.__program)

        for file in self.__files:
            ctl.load(file)

        ctl.ground([("base", [])])
        props = [prop() for prop in self.__propgators]
        for prop in props:
            ctl.register_propagator(prop)
            
        if not test.outcome().is_certain():
            ctl.solve(
                on_core=self.wrap(test,props,"on_core"),
                on_finish=self.wrap(test,props,"on_finish"),
                on_model=self.wrap(test,props,"on_model"),
                on_unsat=self.wrap(test,props,"on_unsat"),
                on_statistics=self.wrap(test,props,"on_statistics"),
            )

    def __repr__(self):
        name = self.__class__.__name__
        arguments = repr(self.__arguments)
        program = repr(self.__program)
        files = repr(self.__files)
        props = repr(self.__propagators)
        return f"{name}({arguments}, {program}, {files}, {props})"
