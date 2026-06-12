import typing
from importlib.resources import files

import clingo
import clingo.script

import constraint_handler.evaluator as evaluator
import constraint_handler.post_processor as post_processor
import constraint_handler.propagator as propagator

module_main = [
    "main",
    "operator",
    "pythonHelper",
    "pythonInterface",
    "pythonOther",
]

module_0_default_arguments = [
    "0_default_arguments/default_arguments",
]

module_1_single_static_assignment = [
    "1_single_static_assignment/statement",
]

module_2_sugar = [
    "2_sugar/sugar",
]

module_3_simplify = [
    "3_domain/domain",
]

module_3_variable_safety_checks = [
    "3_safe/variable_safety_checks/confusing_name",
    "3_safe/variable_safety_checks/empty_domain",
    "3_safe/variable_safety_checks/multiple_declarations",
    "3_safe/variable_safety_checks/reserved_name",
    "3_safe/variable_safety_checks/support",
    "3_safe/variable_safety_checks/undeclared",
]

module_3_safe = (
    [
        "3_safe/bad/safe",
        "3_safe/float_normalize/float_normalize",
        "3_safe/type_checking/type",
        "3_safe/wf_check/wf_check",
    ]
    + module_3_simplify
    + module_3_variable_safety_checks
)

module_4_datatype = [
    "4_solve/compile/bool",
    "4_solve/compile/conditionals",
    "4_solve/compile/equality",
    "4_solve/compile/float",
    "4_solve/compile/int",
    "4_solve/compile/multimap",
    "4_solve/compile/set",
    "4_solve/compile/string",
    "4_solve/compile/symbol",
]

module_4_compile = [
    "4_solve/compile/direct",
    "4_solve/compile/optimize",
    "4_solve/compile/preference",
]

module_4_compile3 = [
    "4_solve/compile3/variables",
    "4_solve/compile3/ensure",
    "4_solve/compile3/value",
    "4_solve/compile3/boolean",
    "4_solve/compile3/set",
    "4_solve/compile3/int",
    "4_solve/compile3/float",
    "4_solve/compile3/string",
    "4_solve/compile3/symbol",
    "4_solve/compile3/tuple",
    "4_solve/compile3/optimize",
    "4_solve/compile3/output",
    "4_solve/compile3/evaluate",
    "4_solve/compile3/bad",
    "4_solve/compile3/none",
    "4_solve/compile3/preference",
    "4_solve/compile3/python",
    "4_solve/compile3/equality",
module_4_compile2 = [
    "4_solve/compile2/variables",
    "4_solve/compile2/ensure",
    "4_solve/compile2/value",
    "4_solve/compile2/boolean",
    "4_solve/compile2/set",
    "4_solve/compile2/int",
    "4_solve/compile2/float",
    "4_solve/compile2/string",
    "4_solve/compile2/symbol",
    "4_solve/compile2/tuple",
    "4_solve/compile2/optimize",
    "4_solve/compile2/output",
    "4_solve/compile2/evaluate",
    "4_solve/compile2/bad",
    "4_solve/compile2/none",
    "4_solve/compile2/preference",
    "4_solve/compile2/python",
    "4_solve/compile2/equality",
]

module_4_ground = [
    "4_solve/ground/gringoEval",
]

module_4_propagator = [
    "4_solve/propagator/propagator",
]

module_4_solve = (
    [
        "4_solve/engine",
        "4_solve/finiteDomain",
        "4_solve/solve",
    ]
    + module_4_datatype
    + module_4_compile
    + module_4_ground
    + module_4_propagator
    + module_4_compile2
    + module_4_compile3
)

module_5_output = [
    "5_output/bad_value",
    "5_output/bool_evaluate",
    "5_output/value",
]

t_modules = {"expression": ("PHASE", ["sugar", "compile", "compile2", "compile3", "ground", "propagator"])}
modules = (
    module_main
    + module_0_default_arguments
    + module_1_single_static_assignment
    + module_2_sugar
    + module_3_safe
    + module_4_solve
    + module_5_output
)
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
    for file_name, map in t_modules.items():
        kw, sub = map
        data = files("constraint_handler.data").joinpath(f"{file_name}.lp").read_text()
        for phase in sub:
            ndata = str(data).replace(kw, phase)
            ctrl.add(ndata)
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
            if prop.on_model(model) == False:
                return False
            post_processor.set_optimize_valuation(post_prop, model)
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
