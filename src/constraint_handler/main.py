import typing
from importlib.resources import files

import clingo
import clingo.script

import constraint_handler.evaluator as evaluator
import constraint_handler.post_processor as post_processor
import constraint_handler.propagator as propagator

module_main = [
    "main",
    "template/variable_involve",
]

m0_context = [
    "0_context/operator",
    "0_context/python_externals",
    "0_context/types",
]

m1_default_arguments = [
    "1_default_arguments/default_arguments",
]

m2_single_static_assignment = [
    "2_single_static_assignment/statement",
]

m3_sugar = [
    "3_sugar/sugar",
]

m4_variable_safety_checks = [
    "4_analysis/variable_safety_checks/confusing_name",
    "4_analysis/variable_safety_checks/empty_domain",
    "4_analysis/variable_safety_checks/multiple_declarations",
    "4_analysis/variable_safety_checks/reserved_name",
    "4_analysis/variable_safety_checks/undeclared",
]

m4_analysis = [
    "4_analysis/domain",
    "4_analysis/bad/safe",
    "4_analysis/float_normalize/float_normalize",
    "4_analysis/type_checking/type",
    "4_analysis/wf_check/wf_check",
] + m4_variable_safety_checks

m5_presolve = [
    "5_presolve/dispatch",
    "5_presolve/engine",
    "5_presolve/presolve",
]

m6_datatype = [
    "6_solve/compile/bool",
    "6_solve/compile/cast",
    "6_solve/compile/conditionals",
    "6_solve/compile/equality",
    "6_solve/compile/float",
    "6_solve/compile/int",
    "6_solve/compile/multimap",
    "6_solve/compile/set",
    "6_solve/compile/string",
]

m6_compile = [
    "6_solve/compile/direct",
]

m6_compile2 = [
    "6_solve/compile2/bad",
    "6_solve/compile2/boolean",
    "6_solve/compile2/domain",
    "6_solve/compile2/equality",
    "6_solve/compile2/float",
    "6_solve/compile2/int",
    "6_solve/compile2/none",
    "6_solve/compile2/python",
    "6_solve/compile2/set",
    "6_solve/compile2/string",
    "6_solve/compile2/symbol",
    "6_solve/compile2/tuple",
    "6_solve/compile2/value",
    "6_solve/compile2/variables",
]

m6_ground = [
    "6_solve/ground/gringoEval",
]

m6_propagator = [
    "6_solve/propagator/propagator",
]

m6_solve = (
    [
        "6_solve/defaults",
        "6_solve/finiteDomain",
        "6_solve/optimize",
        "6_solve/preference",
    ]
    + m6_datatype
    + m6_compile
    + m6_ground
    + m6_propagator
    + m6_compile2
)

m7_output = [
    "7_output/bad_value",
    "7_output/bool_evaluate",
    "7_output/value",
    "7_output/warning",
]

t_modules = {
    "expression": ("PHASE", ["sugar", "type_check", "compile", "compile2"]),
    "correction": ("PHASE", ["constantFolding", "float_normalize", "safe", "type_check", "wf_check"]),
}
modules = (
    module_main
    + m0_context
    + m1_default_arguments
    + m2_single_static_assignment
    + m3_sugar
    + m4_analysis
    + m5_presolve
    + m6_solve
    + m7_output
)

python_enabled = False


def add_to_control(ctrl: clingo.Control, environment=None, _environment_ids=dict()):
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
        data = files("constraint_handler.data.template").joinpath(f"{file_name}.lp").read_text()
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
    setup_propagator(ctrl)


def setup_propagator(ctrl: clingo.Control):
    prop = propagator.ConstraintHandlerPropagator()
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
