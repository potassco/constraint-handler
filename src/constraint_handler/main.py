import typing
from importlib.resources import files

import clingo
import clingo.script

import constraint_handler.evaluator as evaluator
import constraint_handler.post_processor as post_processor
import constraint_handler.propagator as propagator

datatype_modules = [
    "bool",
    "conditionals",
    "equality",
    "float",
    "int",
    "multimap",
    "operator",
    "set",
    "string",
    "symbol",
]

extra_modules = [
    "domain",
    "gringoEval",
    "optimize",
    "preference",
    "propagator",
]

core_modules = [
    "atom",
    "defaultArguments",
    "direct",
    "expression",
    "main",
    "pythonHelper",
    "pythonInterface",
    "solve",
    "statement",
    "sugar",
    "type",
    "variable",
    "wf_check",
]

modules = datatype_modules + extra_modules + core_modules
# modules = extra_modules + core_modules
# modules = core_modules

python_enabled = False


def add_to_control(
    ctrl: clingo.Control, propagator_check_only: bool = False, environment=None, _environment_ids=dict()
):
    """Adds encoding logic to the provided Control instance. The environment argumennt specifies the locals used in the python statements and expressions."""
    global python_enabled
    if not python_enabled:
        clingo.script.enable_python()
        python_enabled = True
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
    prop = propagator.ConstraintHandlerPropagator(check_only)
    post_prop = post_processor.OptimizePostProcessingPropagator()

    ctrl.register_propagator(prop)
    ctrl.register_propagator(post_prop)
    prop.get_configuration(ctrl)
    original_solve = ctrl.solve

    def combine_on_model(on_model: typing.Callable[[clingo.Model], bool | None] | None = None):
        def om(model):
            post_processor.set_optimize_valuation(post_prop, model)
            if prop.on_model(model) == False:
                return False
            if on_model is not None:
                return on_model(model)

        return om

    def new_solve(*args, **kwargs):
        post_prop.reset_optimize_value_symbols()
        if len(args) > 1:
            args = (args[0], combine_on_model(args[1])) + args[2:]
        elif "on_model" in kwargs:
            kwargs["on_model"] = combine_on_model(kwargs["on_model"])
        else:
            kwargs["on_model"] = combine_on_model()
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
