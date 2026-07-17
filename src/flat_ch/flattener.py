import itertools

from clingo import Function, Number

from flat_ch.core.domain import FlatFact, UserInput
from flat_ch.core.input_schema import STATEMENT_SCHEMAS, LayoutToken
from flat_ch.core.operators import Arity, Operator
from flat_ch.core.serialization import clingo_to_python, python_to_clingo
from flat_ch.core.types import Type
from flat_ch.evaluator import evaluate_operation_pure
from flat_ch.operators.python import PythonRegistry
from flat_ch.utils import symbol_name


class Flattener:
    def __init__(
        self,
        registry: PythonRegistry,
        constant_folding: bool = False,
    ):
        self._registry = registry

        self.expression_ids = itertools.count(100000)
        self.structural_cache = {}
        self.constant_exprs = {}
        self.constant_variables = {}
        self.constant_folding = constant_folding
        self.symbol_state_table = {}
        self.emitted_facts = []
        self.current_call_facts = set()

        self.type_values = {t.name: t.value for t in Type}
        self.op_values = {o.name: o.value for o in Operator}

        self._fact_expr_val = FlatFact.EXPRESSION_VALUE.value
        self._fact_expr_var = FlatFact.EXPRESSION_VARIABLE.value
        self._fact_pair = FlatFact.PAIR.value

        self.expression_handlers = {
            UserInput.VALUE: self._parse_value,
            UserInput.VARIABLE: self._parse_variable,
            UserInput.OPERATION: self._parse_operation,
            UserInput.BIND: self._parse_bind,
            UserInput.PAIR: self._parse_pair,
        }

    def _begin_flatten_call(self) -> None:
        self.emitted_facts.clear()
        self.current_call_facts.clear()
        self.constant_variables.clear()

    def _emit_fact(self, fact) -> None:
        if fact in self.current_call_facts:
            return
        self.current_call_facts.add(fact)
        self.emitted_facts.append(fact)

    def flatten(self, clingo_term):
        """
        Emits a flat representation of the input Clingo term.

        Input terms are expected to be top-level declarations corresponding to UserInput variants. The method
        will route the term through the appropriate processing logic based on its type, which may involve
        recursive flattening of nested expressions. Additionally, this method performs validation against the
        defined InputSchemas to ensure correct structure and detect any variable state collisions.
        """
        self._begin_flatten_call()

        term_name = clingo_term.name
        try:
            node_type = UserInput(term_name)
        except ValueError as e:
            raise ValueError(f"Unrecognized declaration: '{term_name}'.") from e

        if node_type not in STATEMENT_SCHEMAS:
            raise KeyError(f"No InputSchema registered for UserInput variant: '{node_type.name}'")

        term_args = clingo_term.arguments
        self._process_declaration(node_type, term_name, term_args)
        return self.emitted_facts

    def _process_declaration(self, node_type, term_name, term_args):
        """
        Routes a top-level declaration node through the appropriate processing logic.

        This also validates the statement against its InputSchema, ensuring correct arity
        and performing collision checks for variable states.
        """
        schema = STATEMENT_SCHEMAS[node_type]
        schema_layout = schema.layout

        if node_type == UserInput.OPTIMIZE_PRECISION and len(term_args) == 1:
            term_args = (*term_args, Function("all", []))

        if len(term_args) != len(schema_layout):
            raise ValueError(
                f"Arity Mismatch: Node '{term_name}' expected {len(schema_layout)} " f"arguments, got {len(term_args)}."
            )

        emit_args = []
        identifier_symbol = None
        collision_state = schema.collision_state

        for arg_symbol, token in zip(term_args, schema_layout):
            if token == LayoutToken.IDENTIFIER:
                if collision_state:
                    self._check_collision(arg_symbol, collision_state)
                identifier_symbol = arg_symbol
                emit_args.append(arg_symbol)
            elif token == LayoutToken.EXPRESSION:
                expr_id = self._flatten_expression(arg_symbol)
                if node_type == UserInput.DEFINE and expr_id in self.constant_exprs:
                    self.constant_variables[identifier_symbol] = expr_id
                emit_args.append(Number(expr_id))
            elif token == LayoutToken.PASS:
                emit_args.append(arg_symbol)

        self.emitted_facts.append(Function(schema.flat_fact.value, emit_args))

    def _flatten_expression(self, clingo_term) -> int:
        """
        Recursively flattens an expression term into its components,
        emitting facts as needed and returning the unique expression ID.
        """
        term_name = clingo_term.name
        try:
            node_type = UserInput(term_name)
        except ValueError as e:
            raise TypeError(f"Unrecognized expression: '{term_name}'. ") from e

        if node_type not in self.expression_handlers:
            raise TypeError(f"No handler registered for expression type: '{node_type.name}'.")

        return self.expression_handlers[node_type](clingo_term)

    # =========================================================================
    # EXPRESSIONS
    # =========================================================================
    def _parse_value(self, clingo_term) -> int:
        term_args = clingo_term.arguments
        type_symbol, value_symbol = term_args[0], term_args[1]
        type_id = Type(self.type_values[type_symbol.name.upper()])

        _, pure_value = clingo_to_python(Function("", [Number(type_id.value), value_symbol]))
        if type_id == Type.FLOAT:
            value_symbol = python_to_clingo(type_id, pure_value).arguments[1]
        return self._intern_value_expr(type_id, value_symbol, pure_value)

    def _intern_value_expr(self, type_id: Type, value_symbol, pure_value) -> int:
        cache_key = ("val", type_id.value, value_symbol)
        expr_id = self.structural_cache.get(cache_key)
        if expr_id is None:
            expr_id = next(self.expression_ids)
            self.structural_cache[cache_key] = expr_id

        self._emit_fact(Function(self._fact_expr_val, [Number(expr_id), Number(type_id.value), value_symbol]))

        self.constant_exprs[expr_id] = (type_id, pure_value)
        return expr_id

    def _parse_variable(self, clingo_term) -> int:
        variable_symbol = clingo_term.arguments[0]
        constant_expr_id = self.constant_variables.get(variable_symbol)
        if constant_expr_id is not None:
            return constant_expr_id

        cache_key = ("var", variable_symbol)
        expr_id = self.structural_cache.get(cache_key)
        if expr_id is None:
            expr_id = next(self.expression_ids)
            self.structural_cache[cache_key] = expr_id
        self._emit_fact(Function(self._fact_expr_var, [Number(expr_id), variable_symbol]))
        return expr_id

    def _parse_bind(self, clingo_term) -> int:
        term_args = clingo_term.arguments
        var_name = symbol_name(term_args[0])
        expr_term = term_args[1]

        expr_id = self._flatten_expression(expr_term)
        self._registry.add_input_to_current(var_name, expr_id)

        return expr_id

    def _parse_pair(self, clingo_term) -> int:
        key_expr, value_expr = clingo_term.arguments

        key_expr_id = self._flatten_expression(key_expr)
        value_expr_id = self._flatten_expression(value_expr)

        cache_key = ("pair", key_expr_id, value_expr_id)
        expr_id = self.structural_cache.get(cache_key)

        if expr_id is None:
            expr_id = next(self.expression_ids)

            self.structural_cache[cache_key] = expr_id
        self._emit_fact(Function(self._fact_expr, [Number(expr_id), Function("pair", [])]))
        self._emit_fact(Function(self._fact_pair, [Number(expr_id), Number(key_expr_id), Number(value_expr_id)]))

        return expr_id

    def _parse_operation(self, clingo_term) -> int:
        term_args = clingo_term.arguments
        operation_symbol = term_args[0]
        operator_name = operation_symbol.name
        operator = Operator(self.op_values[operator_name.upper()])

        args_term = term_args[1] if len(term_args) > 1 else Function("", [])

        if operator == Operator.PYTHON and len(operation_symbol.arguments) > 1:
            script_payload = operation_symbol.arguments[0].string
            target_output = symbol_name(operation_symbol.arguments[1])
            python_id = self._registry.register_program(script_payload, target_output)

        if hasattr(args_term, "name") and args_term.name == "":
            argument_ids = [self._flatten_expression(arg) for arg in args_term.arguments]
        else:
            argument_ids = [self._flatten_expression(args_term)]

        if operator == Operator.PYTHON and len(operation_symbol.arguments) == 1:
            script_payload = operation_symbol.arguments[0].string
            target_output = "__fch_result"
            arg_names = [f"_fch_arg_{index}" for index in range(1, len(argument_ids) + 1)]
            call_args = ", ".join(arg_names)
            script_payload = f"{target_output} = ({script_payload})({call_args})"
            python_id = self._registry.register_program(script_payload, target_output)
            for arg_id, arg_name in zip(argument_ids, arg_names):
                self._registry.add_input_to_current(arg_name, arg_id)

        if self.constant_folding:
            constant_args = []
            is_pure = True
            for arg_id in argument_ids:
                const_data = self.constant_exprs.get(arg_id)
                if const_data is None:
                    is_pure = False
                    break
                constant_args.append(const_data)

            if is_pure:
                try:
                    if operator == Operator.PYTHON:
                        result_type, result_value = self._registry.execute_current_directly(constant_args, argument_ids)
                    else:
                        result_type, result_value = evaluate_operation_pure(operator, constant_args)
                    result_symbol = python_to_clingo(result_type, result_value).arguments[1]
                    return self._intern_value_expr(result_type, result_symbol, result_value)
                except (NotImplementedError, TypeError, ValueError):
                    print(
                        f"Warning: Constant folding failed for operation '{operator.name}' with arguments {constant_args}. Falling back to standard flattening."
                    )

        if operator == Operator.PYTHON:
            cache_key = ("operation", operator.value, python_id, tuple(argument_ids))
        else:
            cache_key = ("operation", operator.value, tuple(argument_ids))

        expr_id = self.structural_cache.get(cache_key)
        if expr_id is None:
            expr_id = next(self.expression_ids)
            self.structural_cache[cache_key] = expr_id
        eid_num = Number(expr_id)
        allowed = operator.allowed_arities
        arity_count = len(argument_ids)

        if arity_count == 1 and (allowed & Arity.UNARY):
            self._emit_fact(Function(f"op_{operator_name}", [eid_num, Number(argument_ids[0])]))

        elif arity_count == 2 and (allowed & Arity.BINARY):
            self._emit_fact(
                Function(f"op_{operator_name}", [eid_num, Number(argument_ids[0]), Number(argument_ids[1])])
            )

        elif arity_count == 3 and (allowed & Arity.TERNARY):
            self._emit_fact(
                Function(
                    f"op_{operator_name}",
                    [eid_num, Number(argument_ids[0]), Number(argument_ids[1]), Number(argument_ids[2])],
                )
            )

        elif allowed & Arity.VARIADIC:
            self._emit_fact(Function(f"op_{operator_name}_variadic", [eid_num, Number(arity_count)]))

            for position, arg_id in enumerate(argument_ids, start=1):
                self._emit_fact(Function(f"op_{operator_name}_arg", [eid_num, Number(position), Number(arg_id)]))

        else:
            raise TypeError(f"Operator {operator.name} does not support arity count of {arity_count}.")

        if operator == Operator.PYTHON:
            self._registry.finalize_current(expr_id)
        return expr_id

    # =========================================================================
    # CORE UTILITIES
    # =========================================================================

    def _check_collision(self, name_symbol, intended_state: str):
        """
        Checks if a symbol is already registered in the symbol_state_table with a conflicting state.
        """
        current_state = self.symbol_state_table.get(name_symbol)

        if current_state and current_state != intended_state:
            raise ValueError(
                f"Redefinition Error: Cannot mark variable '{name_symbol}' as {intended_state} "
                f"because it is already registered as {current_state} globally."
            )
        self.symbol_state_table[name_symbol] = intended_state
