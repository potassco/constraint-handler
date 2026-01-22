"""
The constraint-handler project.
"""

from importlib.resources import files

import clingo
import clingo.ast
import clingo.script

modules = [
    "bool",
    "conditionals",
    "direct",
    "execution",
    "float",
    "gringoEval",
    "groundExec",
    "int",
    "main",
    "multimap",
    "optimize",
    "preference",
    "propagator",
    "pythonHelper",
    "set",
    "string",
    "symbol",
    "variable",
]


def add_to_control(
    ctrl: clingo.Control, propagator_check_only: bool = False, environment=None, _environment_ids=dict()
):
    """Adds encoding logic to the provided Control instance. The environment argumennt specifies the locals used in the python statements and expressions."""
    clingo.script.enable_python()
    for mod in modules:
        file = files("constraint_handler.data").joinpath(f"{mod}.lp")
        ctrl.load(str(file))
    if environment is not None:
        eid = id(environment)
        if eid in _environment_ids:
            idx = _environment_ids[eid]
        else:
            idx = len(_environment_ids)
            evaluator._solver_environment[idx] = environment
            _environment_ids[eid] = idx
        ctrl.add(f"main_solverIdentifier({idx}).")
    setup_propagator(ctrl, propagator_check_only)


def setup_propagator(ctrl: clingo.Control, check_only: bool = False):
    p = propagator.ConstraintHandlerPropagator(check_only)
    ctrl.register_propagator(p)
    p.get_configuration(ctrl)
    original_solve = ctrl.solve

    def combine_on_model(on_model):
        def om(m):
            if p.on_model(m) != False:
                return on_model(m)
            else:
                return True

        return om

    def new_solve(*args, **kwargs):
        if len(args) > 1:
            args = (args[0], combine_on_model(args[1])) + args[2:]
        elif "on_model" in kwargs:
            kwargs["on_model"] = combine_on_model(kwargs["on_model"])
        else:
            kwargs["on_model"] = p.on_model
        return original_solve(*args, **kwargs)

    ctrl.solve = new_solve


def set_globals(environment=None):
    """The environment argumennt specifies the globals used in the python statements and expressions.
    By default, the globals import the math module.
    Calling set_globals with no arguments clears the globals."""
    if environment is not None:
        evaluator._shared_environment = environment
    else:
        evaluator._shared_environment = dict()


def add_to_globals(environment):
    evaluator._shared_environment.update(environment)


def add_encoding_to_program_builder(b: clingo.ast.ProgramBuilder):
    """Adds encoding logic to the provided ProgramBuilder instance."""
    clingo.script.enable_python()
    all_files = [str(files("constraint_handler.data").joinpath(f"{mod}.lp")) for mod in modules]
    with b:
        clingo.ast.parse_files(all_files, lambda stm: b.add(stm))
