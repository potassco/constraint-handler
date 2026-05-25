from __future__ import annotations

from collections import namedtuple

import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.warning as warning
from constraint_handler.schemas.atom import (
    Evaluated,
    Main_solverIdentifiers,
    Multimap_value,
    Set_value,
    Value,
)
from constraint_handler.schemas.domain import (
    BoolDomain,
    FromFacts,
    FromList,
)

class Propagator_variable_declare(atom.Variable_declare):
    pass


class Propagator_variable_define(atom.Variable_define):
    pass


class Propagator_variable_domain(atom.Variable_domain):
    pass


class Propagator_variable_declareOptional(atom.Variable_declareOptional):
    pass


class Propagator_ensure(atom.Ensure):
    pass


class Propagator_bool_evaluate(atom.Bool_evaluate):
    pass


class Propagator_set_declare(atom.Set_declare):
    pass


class Propagator_set_assign(atom.Set_assign):
    pass


class Propagator_set_baseDomain(atom.Set_baseDomain):
    pass


class Propagator_multimap_declare(atom.Multimap_declare):
    pass


class Propagator_multimap_assign(atom.Multimap_assign):
    pass


class Propagator_optimize_maximizeSum(atom.Optimize_maximizeSum):
    pass


class Propagator_optimize_precision(atom.Optimize_precision):
    pass


class Propagator_execution_declare(atom.Execution_declare):
    pass


class Propagator_execution_run(atom.Execution_run):
    pass


class Propagator_evaluate(atom.Evaluate):
    pass


class Propagator_warning_forbid(warning.Warning_forbid):
    pass


class Propagator_warning_ignore(warning.Warning_ignore):
    pass
