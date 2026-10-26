"""Load grounded variable declarations and values for the propagator."""

from collections.abc import Callable
from typing import cast

import clingo
from clingo import Symbol

import constraint_handler.schemas.propagator_atom as prop_atom
from constraint_handler import myClorm
from constraint_handler.PropagatorConstants import OTHER_ENGINE_VAR_NAME, propagator_warning_t
from constraint_handler.PropagatorVariables import (
    BoolEvaluateVariable,
    DictVariable,
    EvaluateVariable,
    SetVariable,
    SharedValue,
    Variable,
    VariableManager,
    VariableType,
    VariableValue,
)
from constraint_handler.schemas import expression, internal, type_, warning


class VariableLoader:
    """Decode grounded atoms and register variables in the supplied solve state."""

    def __init__(
        self,
        variables: VariableManager,
        errors: propagator_warning_t,
        evaluate_variables: list[EvaluateVariable],
        shared_values: list[SharedValue],
        *,
        get_variable_value: Callable[[expression.Expr, int], VariableValue],
        register_variable_value: Callable[[VariableType, VariableValue], None],
        add_literal2var: Callable[[int, VariableType], None],
        add_watch: Callable[[int], None],
    ) -> None:
        """Bind the current solve's state and registration operations.

        Args:
            variables: Manager receiving loaded variables.
            errors: Collection receiving input warnings.
            evaluate_variables: Collection receiving explicit evaluations.
            shared_values: Collection receiving shared-value declarations.
            get_variable_value: Intern and index an expression/literal pair.
            register_variable_value: Associate a value with its owner.
            add_literal2var: Register a normalized literal-variable association.
            add_watch: Register a watch while respecting check-only mode.
        """
        self.variable_manager = variables
        self.errors = errors
        self.evaluatevars = evaluate_variables
        self.shared_values = shared_values
        self.get_variable_value = get_variable_value
        self.register_variable_value = register_variable_value
        self.add_literal2var = add_literal2var
        self.add_watch = add_watch

    def load_variables(self, init: clingo.PropagateInit) -> None:
        """Load declarations and cross-engine values in dependency order.

        Args:
            init: Clingo propagation initialization object.
        """
        self.get_variable_interface(init)
        self.get_variables(init)
        self.get_set_declarations(init)
        self.get_multimap_declarations(init)
        self.get_engine_variables(init)

    def load_evaluations(self, init: clingo.PropagateInit) -> None:
        """Load explicit evaluations after objective expressions are registered.

        Args:
            init: Clingo propagation initialization object.
        """
        self.get_evaluate(init)
        self.get_shared_values(init)

    def get_engine_variables(self, ctl: clingo.PropagateInit):
        """
        Load atoms that represent the values of variables from the input program.

        This reads `_se_value`, `_set_contains`, and `Multimap_value` atoms and updates the
        corresponding variables with the assigned values.
        This is used for variables whose values are defined by other engines

        Args:
            ctl: Clingo PropagateInit object.
        """
        if len(self.variable_manager) == 0:
            # if there are no variables, we can skip this part since propagator is not used
            return
        value_atoms = myClorm.findInPropagateInit(ctl, internal._se_value)
        set_value_atoms = myClorm.findInPropagateInit(ctl, internal._set_contains)
        multimap_value_atoms = myClorm.findInPropagateInit(ctl, prop_atom.Multimap_value)

        for (name, val), _literal in value_atoms.items():
            if not isinstance(name, expression.Variable):
                # ignore other stuff
                continue

            # if it is a variable, get the symbol for it
            _name = myClorm.pytocl(name).arguments[0]
            if _name not in self.variable_manager:
                if isinstance(val, internal.Ref) and isinstance(val.expr, expression.Variable) and val.expr == name:
                    # If the set references itself, it should get its values later from _set_contains,
                    # Here, we make the set variable
                    # TODO: make a difference for sets and multimaps,
                    # currently, Ref is only implemented for sets so we do nothing for multimaps here
                    self.variable_manager.add_variable(_name, SetVariable(OTHER_ENGINE_VAR_NAME, _name, _literal))
                    self.add_watch(_literal)
                    self.add_watch(-_literal)
                    self.add_literal2var(_literal, self.variable_manager.get_variable(_name, SetVariable.__name__))
                    continue
                # If the value references something else, or it is not a reference,
                # we make a normal variable and add the value to it,
                self.variable_manager.add_variable(_name, Variable(OTHER_ENGINE_VAR_NAME, _name))

            variable: Variable = cast(Variable, self.variable_manager.get_variable(_name, Variable.__name__))
            expr: expression.Expr = val.expr if isinstance(val, internal.Ref) else val

            value = self.get_variable_value(expr, _literal)
            variable.add_value(value, _literal)
            self.register_variable_value(variable, value)

            self.add_watch(_literal)
            self.add_watch(-_literal)
            self.add_literal2var(_literal, self.variable_manager.get_variable(_name, Variable.__name__))

        for (name, val_set), _literal in set_value_atoms.items():
            if not isinstance(name, expression.Variable):
                continue
            _name = myClorm.pytocl(name).arguments[0]

            if _name not in self.variable_manager:
                self.errors.append(
                    warning.Warning(
                        warning.Variable(warning.VariableWarning.undeclared),  # ty:ignore[unresolved-attribute]
                        (_name,),
                        f"Warning: Got set value of another engine for variable that does not exist! Ignoring value {_name}, {val_set}.",
                    )
                )
                continue

            set_variable = cast(SetVariable, self.variable_manager.get_variable(_name, SetVariable.__name__))

            expr: expression.Expr = val_set.expr if isinstance(val_set, internal.Ref) else val_set

            value = self.get_variable_value(expr, _literal)
            set_variable.add_value(value, None)
            self.register_variable_value(set_variable, value)
            self.add_watch(_literal)
            self.add_watch(-_literal)

        for (name, key, val), _literal in multimap_value_atoms.items():
            if name not in self.variable_manager:
                multimap_variable = DictVariable(OTHER_ENGINE_VAR_NAME, name, _literal)
                self.variable_manager.add_variable(name, multimap_variable)
            else:
                if self.variable_manager.has_var_type(name, DictVariable.__name__):
                    # TODO: fix issue where value(myvar, ref(dict...)) makes a variable when it should not
                    multimap_variable = DictVariable(OTHER_ENGINE_VAR_NAME, name, _literal)
                    self.variable_manager.add_variable(name, multimap_variable)
                multimap_variable = cast(DictVariable, self.variable_manager.get_variable(name, DictVariable.__name__))

            key_value = self.get_variable_value(key, 1)
            value = self.get_variable_value(val, _literal)
            multimap_variable.add_value(key_value, value)
            self.register_variable_value(multimap_variable, key_value)
            self.register_variable_value(multimap_variable, value)

            self.add_watch(_literal)
            self.add_watch(-_literal)
            self.add_literal2var(_literal, self.variable_manager.get_variable(name, DictVariable.__name__))

    def get_variable_interface(self, ctl: clingo.PropagateInit):

        user_var_names = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_variable_interface)

        for (id, _), _ in user_var_names.items():
            self.variable_manager.add_user_variable_name(id)

    def get_variables(self, ctl: clingo.PropagateInit):
        """
        Load base variable declarations/definitions/domains from ASP facts.

        Reads variable-related atoms and creates/extends `Variable` instances.
        Note that nogoods are added to prevent True assignments to values that are parts of domains that are assigned False.

        Args:
            ctl: Clingo PropagateInit object.
        """
        var_declares = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_variable_declare)
        var_defines = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_variable_define)
        var_domains = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_variable_domain)

        from_facts_literals: dict[Symbol, int] = {}
        for (symbol_var, domain, name), _literal in var_declares.items():
            if not self.variable_manager.has_var_type(symbol_var, Variable.__name__):
                self.variable_manager.add_variable(
                    symbol_var, Variable(name, symbol_var, symbol_var in self.variable_manager.user_variable_names)
                )
            else:
                print(
                    f"Warning!!: Variable {symbol_var} was defined via declare at least 2 times! This may cause unexpected behavior."
                )

            variable: Variable = cast(Variable, self.variable_manager.get_variable(symbol_var, Variable.__name__))

            self.add_watch(_literal)
            self.add_watch(-_literal)

            # TODO: make sure we dont need this literal being watched for Variables
            self.add_literal2var(_literal, variable)

            if isinstance(domain, prop_atom.FromFacts):
                # values will be added from facts, nothing to do here
                from_facts_literals[symbol_var] = _literal
            else:
                self.errors.append(
                    warning.Warning(
                        warning.Propagator(),
                        (symbol_var,),
                        f"Unknown domain type '{domain}' for variable '{symbol_var}'",
                    )
                )

        for (symbol_var, expr, name), _literal in var_defines.items():
            if not self.variable_manager.has_var_type(symbol_var, Variable.__name__):
                define_variable = Variable(name, symbol_var, symbol_var in self.variable_manager.user_variable_names)
                self.variable_manager.add_variable(symbol_var, define_variable)

            define_variable: Variable = cast(
                Variable, self.variable_manager.get_variable(symbol_var, Variable.__name__)
            )
            value = self.get_variable_value(expr, _literal)
            define_variable.add_value(value, _literal)
            self.register_variable_value(define_variable, value)
            self.add_watch(_literal)
            self.add_watch(-_literal)

            # TODO: make sure we dont need this literal being watched for Variables
            # self.literal2var.setdefault(_literal, []).append(define_variable)
            # here we dont add a nogood since its the same literal

        for (symbol_var, domain_expr, name), _literal in var_domains.items():
            # These values are assigned the "from_facts" domain literal for the given variable
            if not self.variable_manager.has_var_type(symbol_var, Variable.__name__):
                continue
            domain_variable: Variable = cast(
                Variable, self.variable_manager.get_variable(symbol_var, Variable.__name__)
            )

            domain_literal = from_facts_literals[symbol_var]
            value = self.get_variable_value(domain_expr, _literal)
            domain_variable.add_value(value, domain_literal)
            self.register_variable_value(domain_variable, value)
            self.add_watch(_literal)
            self.add_watch(-_literal)

            ctl.add_clause([-_literal, domain_literal])
            # literal defining the domain should also be included, not just the variable declaration literal!
            # ctl.add_clause([-literal, _literal])

            # self.literal2var.setdefault(_literal, []).append(domain_variable)

        for var in self.variable_manager.get_variables_by_type(Variable.__name__):
            var = cast(Variable, var)
            if len(var.expressions) == 0:
                value = self.get_variable_value(expression.Bad.bad, 1)
                var.add_value(value, 1)
                self.register_variable_value(var, value)

    def get_shared_values(self, ctl: clingo.PropagateInit):
        """
        Load shared value declarations from ASP facts and create SharedValueVariable instances.

        Args:
            ctl: Clingo PropagateInit object.
        """

        shared_values = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_share_value)
        for (expr, name), literal in shared_values.items():
            shared_value_var: SharedValue = SharedValue(expr, literal)

            self.shared_values.append(shared_value_var)

    def get_evaluate(self, ctl: clingo.PropagateInit):
        """
        Load `evaluate` atoms into `EvaluateVariable` instances.
        Also load "bool_evaluate" atoms and create the corresponding variables.

        Args:
            ctl: Clingo PropagateInit object.
        """

        evaluate_atoms = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_evaluate)
        bool_evaluate_atoms = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_bool_evaluate)
        bool_evaluated_atoms = myClorm.findInPropagateInit(ctl, internal._bool_evaluated)
        for (ref, expr, _), literal in evaluate_atoms.items():
            var = EvaluateVariable(ref, expr, literal)
            self.evaluatevars.append(var)

        true_val = expression.Val(type_.BaseType.bool, True)  # ty:ignore[unresolved-attribute]
        false_val = expression.Val(type_.BaseType.bool, False)  # ty:ignore[unresolved-attribute]

        for (expr, label), literal in bool_evaluate_atoms.items():
            b_vals = {}
            for (bexpr, value), b_literal in bool_evaluated_atoms.items():
                if bexpr == expr:
                    b_vals[value] = b_literal
                    # self.add_watch(b_literal)
                    # self.add_watch(-b_literal)

            value = self.get_variable_value(expr, literal)
            bool_var = BoolEvaluateVariable(
                label,
                value,
                b_vals[true_val],
                b_vals[false_val],
                b_vals[expression.Bad.bad],
            )
            self.register_variable_value(bool_var, value)

            self.add_watch(literal)
            self.add_watch(-literal)
            self.add_literal2var(literal, bool_var)
            # for blit in b_vals.values():
            #     self.literal2var.setdefault(blit, []).append(bool_var)
            # Var name is given here so it works well with the rest of the system
            # It should do nothing and also should never appear in any assignments!!
            self.variable_manager.add_variable(bool_var.var, bool_var)

    def get_set_declarations(self, ctl: clingo.PropagateInit):
        """
        Load set declarations and assignments from ASP facts.

        Args:
            ctl: Clingo propagation initializer.
        """

        declares = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_set_declare)
        for (symbol_var, name), literal in declares.items():
            variable = SetVariable(
                name, symbol_var, literal, is_user_variable=symbol_var in self.variable_manager.user_variable_names
            )
            self.variable_manager.add_variable(symbol_var, variable)
            self.add_literal2var(literal, variable)

            self.add_watch(literal)
            self.add_watch(-literal)

        assigns = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_set_assign)
        for (symbol_var, expr, condition, name), literal in assigns.items():
            try:
                setvar: SetVariable = cast(
                    SetVariable, self.variable_manager.get_variable(symbol_var, SetVariable.__name__)
                )
            except KeyError:
                continue
            condition_value = self.get_variable_value(condition, literal)
            value = self.get_variable_value(expr, literal)
            setvar.add_value(value, condition_value)
            self.register_variable_value(setvar, value)
            self.register_variable_value(setvar, condition_value)

            self.add_watch(literal)
            self.add_watch(-literal)

    def get_multimap_declarations(self, ctl: clingo.PropagateInit):
        """
        Load multimap (dict) declarations and assignments from ASP facts.

        Args:
            ctl: Clingo PropagateInit object.
        """
        declares = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_multimap_declare)
        for (symbol_var, name), literal in declares.items():
            variable = DictVariable(
                name, symbol_var, literal, is_user_variable=symbol_var in self.variable_manager.user_variable_names
            )
            self.variable_manager.add_variable(symbol_var, variable)
            self.add_literal2var(literal, variable)

            self.add_watch(literal)
            self.add_watch(-literal)

        assigns = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_multimap_assign)
        for (symbol_var, key_expr, expr, name), literal in assigns.items():
            try:
                dictvar: DictVariable = cast(
                    DictVariable, self.variable_manager.get_variable(symbol_var, DictVariable.__name__)
                )
            except KeyError:
                continue
            key_value = self.get_variable_value(key_expr, 1)
            value = self.get_variable_value(expr, literal)
            dictvar.add_value(key_value, value)
            self.register_variable_value(dictvar, key_value)
            self.register_variable_value(dictvar, value)

            self.add_watch(literal)
            self.add_watch(-literal)
