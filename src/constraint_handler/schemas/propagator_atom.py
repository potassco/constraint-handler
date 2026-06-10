from __future__ import annotations

from typing import NamedTuple

import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.domain as domain
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.warning as warning

Bool_evaluated = atom.Bool_evaluated
Evaluated = atom.Evaluated
Main_solverIdentifiers = atom.Main_solverIdentifiers
Multimap_value = atom.Multimap_value
Set_value = atom.Set_value
Value = atom.Value

BoolDomain = domain.BoolDomain
FromFacts = domain.FromFacts
FromList = domain.FromList


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


class Propagator_variable_interface(NamedTuple):
    label: expression.constant
    variable: expression.constant
