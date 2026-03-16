import typing
from importlib.resources import files

import clingo
import clingo.script

import constraint_handler.evaluator as evaluator
import constraint_handler.post_processor as post_processor
import constraint_handler.propagator as propagator

modules = [
    "bool",
    "conditionals",
    "direct",
    "equality",
    "execution",
    "expression",
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
    "type",
    "variable",
]

python_enabled = False
ground_patched = False
model_patched = False


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
    # patch_clingo(ctrl)
    setup_propagator(ctrl, propagator_check_only)


def patch_clingo(ctrl):
    global ground_patched
    if not ground_patched:
        old_control_ground = clingo.Control.ground

        def new_control_ground(self, *k, **kw):
            old_control_ground(self, *k, **kw)
            post_processor.set_map(self)

        setattr(clingo.Control, "ground", new_control_ground)
        ground_patched = True
    global model_patched
    if not model_patched or True:
        old_model_init = clingo.Model.__init__

        def new_model_init(self, *k, **kw):
            old_model_init(self, *k, **kw)
            post_processor.set_valuation(ctrl, self)

        setattr(clingo.Model, "__init__", new_model_init)
        model_patched = True


def setup_propagator(ctrl: clingo.Control, check_only: bool = False):
    prop = propagator.ConstraintHandlerPropagator(check_only)
    ctrl.register_propagator(prop)
    prop.get_configuration(ctrl)
    original_solve = ctrl.solve

    def combine_on_model(on_model: typing.Callable[[clingo.Model], bool | None] | None = None):
        def om(model):
            if prop.on_model(model) == False:
                return False
            if on_model is not None:
                return on_model(model)

        return om

    def new_solve(*args, **kwargs):
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
