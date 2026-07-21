from __future__ import annotations

from typing import TYPE_CHECKING

import clingo

from flat_ch.api.ch.input import UserInput
from flat_ch.core.base_registration import BaseRegistration, parse_operator, parse_python_operator
from flat_ch.core.domain import (
    BoolEvaluateInput,
    EnsureConstraint,
    EvaluateInput,
    ExecutionDeclare,
    ExecutionRun,
    ExecutionStatement,
    Expression,
    IAssertStatement,
    IAssignStatement,
    IBind,
    IIfStatement,
    INoopStatement,
    IOperation,
    IPythonOperation,
    IPythonStatement,
    IValue,
    IVariableDefine,
    IVariableRef,
    OptimizeMaximizeSum,
    OptimizePrecision,
    PythonEvaluateInput,
    Type,
)
from flat_ch.core.evaluation.operators import Operator
from flat_ch.core.serialization import SerializerProtocol

if TYPE_CHECKING:
    from flat_ch.core.registry import ProgramRegistry


_ASP_TO_TYPE_ENUM = {type_name.lower(): type_enum for type_name, type_enum in Type.__members__.items()}


class Registration(BaseRegistration):
    def __init__(self, registry: ProgramRegistry, serializer: SerializerProtocol) -> None:
        super().__init__(serializer)
        self.reg = registry
        self._expression_cache: dict[clingo.Symbol, Expression] = {}

        self._dispatch_decl = {
            "variable_declareOptional": self._handle_declareOptional,
            UserInput.DECLARE.value: self._handle_declare,
            UserInput.DOMAIN.value: self._handle_domain,
            UserInput.DEFINE.value: self._handle_define,
            UserInput.ENSURE.value: self._handle_ensure,
            UserInput.EVALUATE.value: self._handle_evaluate,
            UserInput.BOOL_EVALUATE.value: self._handle_bool_evaluate,
            UserInput.OPTIMIZE_SUM.value: self._handle_optimize_sum,
            UserInput.OPTIMIZE_PRECISION.value: self._handle_optimize_precision,
            UserInput.EXECUTION_DECLARE.value: self._handle_execution_declare,
            UserInput.EXECUTION_RUN.value: self._handle_execution_run,
            UserInput.SET_DECLARE.value: self._handle_set_declare,
            UserInput.SET_BASE_DOMAIN.value: self._handle_set_base_domain,
            UserInput.SET_ASSIGN.value: self._handle_set_assign,
        }

        self._dispatch_expr = {
            UserInput.VALUE.value: self._handle_value,
            UserInput.VARIABLE.value: self._handle_variable,
            UserInput.OPERATION.value: self._handle_operation,
            "python": self._handle_python,
        }

        self._dispatch_statement = {
            UserInput.STATEMENT_SEQUENCE.value: self._handle_statement_sequence,
            UserInput.STATEMENT_ASSIGN.value: self._handle_statement_assign,
            UserInput.STATEMENT_ASSERT.value: self._handle_statement_assert,
            UserInput.STATEMENT_IF.value: self._handle_statement_if,
            UserInput.STATEMENT_NOOP.value: self._handle_statement_noop,
            UserInput.STATEMENT_PYTHON.value: self._handle_statement_python,
        }

    def register(self, term: clingo.Symbol) -> clingo.Number:
        try:
            handler = self._dispatch_decl.get(term.name)
            args = term.arguments
        except (AttributeError, RuntimeError):
            return clingo.Number(0)

        if handler is not None:
            handler(args)
        else:
            raise ValueError(f"Invalid fact format: {term}")

        return clingo.Number(0)

    def _handle_declareOptional(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 1:
            var_sym = self._lower_variable_symbol(args[0])
            self.reg.update_var(var_sym, (IValue(Type.NONE, None),))

    def _handle_declare(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 3:
            domain_kind = args[2].name
            var_sym = self._lower_variable_symbol(args[1])

            if domain_kind == "set":
                self.reg.update_set(var_sym)
            elif domain_kind == "boolDomain":
                self.reg.update_var(var_sym, (IValue(Type.BOOL, True), IValue(Type.BOOL, False)))
            elif domain_kind == "fromFacts":
                self.reg.update_var(var_sym, ())
            elif domain_kind == "fromList":
                unnested = tuple(self.parse_expression(s) for s in self.unnest(args[2].arguments[0]))
                self.reg.update_var(var_sym, unnested)

    def _handle_domain(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 3:
            var_sym = self._lower_variable_symbol(args[1])
            self.reg.update_var(var_sym, (self.parse_expression(args[2]),))

    def _handle_define(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 3:
            var_sym = self._lower_variable_symbol(args[1])
            self.reg.sequential_inputs.append(
                IVariableDefine(var_sym, self.parse_expression(args[2]), self.reg.current_registration_id)
            )

    def _handle_ensure(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 2:
            self.reg.sequential_inputs.append(
                EnsureConstraint(self.to_str(args[0]), self.parse_expression(args[1]), self.reg.current_registration_id)
            )

    def _handle_evaluate(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 3:
            label = self.to_str(args[0])
            original_argument_tuple = args[2]
            unwound_exprs = tuple(self.parse_expression(s) for s in self.unnest(original_argument_tuple))
            python_code = parse_python_operator(args[1])
            reg_id = self.reg.current_registration_id

            if python_code is not None:
                bound_args = tuple(IBind(f"_fch_arg_{idx}", expr) for idx, expr in enumerate(unwound_exprs, start=1))
                self.reg.sequential_inputs.append(
                    PythonEvaluateInput(
                        label=label,
                        code=python_code,
                        arguments=bound_args,
                        original_argument_tuple=original_argument_tuple,
                        registration_id=reg_id,
                    )
                )
            else:
                self.reg.sequential_inputs.append(
                    EvaluateInput(
                        label,
                        parse_operator(args[1]),
                        self._normalize_operation_arguments(args[1], unwound_exprs),
                        original_argument_tuple=original_argument_tuple,
                        registration_id=reg_id,
                    )
                )

    def _handle_bool_evaluate(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 2:
            label = None if args[0] == args[1] else self.to_str(args[0])
            self.reg.sequential_inputs.append(
                BoolEvaluateInput(
                    label,
                    self.parse_expression(args[1]),
                    original_expression=args[1],
                    registration_id=self.reg.current_registration_id,
                )
            )

    def _handle_optimize_sum(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 4:
            self.reg.sequential_inputs.append(
                OptimizeMaximizeSum(self.parse_expression(args[1]), args[2], args[3].number, self.to_str(args[0]))
            )

    def _handle_optimize_precision(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 2:
            self.reg.sequential_inputs.append(
                OptimizePrecision(self.parse_expression(args[0]), self.scalar_value(args[1]))
            )

    def _handle_execution_declare(self, args: tuple[clingo.Symbol, ...]):
        label = self.to_str(args[0])
        inputs = tuple(self.unnest(args[3]))
        outputs = tuple(self.unnest(args[4]))

        self.reg.add_execution(
            ExecutionDeclare(
                args[1],
                self._parse_execution_statement(args[2]),
                inputs,
                outputs,
                label=label,
            )
        )

    def _parse_execution_statement(self, symbol: clingo.Symbol) -> list[ExecutionStatement]:
        try:
            handler = self._dispatch_statement.get(symbol.name)
            args = symbol.arguments
        except (AttributeError, RuntimeError):
            raise ValueError(f"Unknown execution statement format: {symbol}")

        if handler is None:
            raise ValueError(f"Unknown execution statement format: {symbol}")
        return handler(args)

    def _handle_statement_sequence(self, args: tuple[clingo.Symbol, ...]) -> list[ExecutionStatement]:
        if len(args) == 2:
            return self._parse_execution_statement(args[0]) + self._parse_execution_statement(args[1])
        raise ValueError(f"Invalid seq2 statement format: {args}")

    def _handle_statement_assign(self, args: tuple[clingo.Symbol, ...]) -> list[ExecutionStatement]:
        if len(args) == 2:
            return [
                IAssignStatement(
                    variable=self.to_str(args[0]),
                    expression=self.parse_expression(args[1]),
                )
            ]
        raise ValueError(f"Invalid assign statement format: {args}")

    def _handle_statement_assert(self, args: tuple[clingo.Symbol, ...]) -> list[ExecutionStatement]:
        if len(args) == 1:
            return [IAssertStatement(condition=self.parse_expression(args[0]))]
        raise ValueError(f"Invalid assert statement format: {args}")

    def _handle_statement_if(self, args: tuple[clingo.Symbol, ...]) -> list[ExecutionStatement]:
        if len(args) == 3:
            return [
                IIfStatement(
                    condition=self.parse_expression(args[0]),
                    then_branch=self._parse_execution_statement(args[1]),
                    else_branch=self._parse_execution_statement(args[2]),
                )
            ]
        raise ValueError(f"Invalid if statement format: {args}")

    def _handle_statement_noop(self, args: tuple[clingo.Symbol, ...]) -> list[ExecutionStatement]:
        if not args:
            return [INoopStatement()]
        raise ValueError(f"Invalid noop statement format: {args}")

    def _handle_statement_python(self, args: tuple[clingo.Symbol, ...]) -> list[ExecutionStatement]:
        if len(args) == 1 and args[0].type == clingo.SymbolType.String:
            return [IPythonStatement(code=args[0].string)]
        raise ValueError(f"Invalid statement_python format: {args}")

    def _handle_execution_run(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 2:
            self.reg.sequential_inputs.append(ExecutionRun(self.to_str(args[0]), self.scalar_value(args[1])))

    def _handle_set_declare(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 2:
            self.reg.update_set(args[1])

    def _handle_set_base_domain(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 3:
            self.reg.update_set(args[1], base_domain=(self.parse_expression(args[2]),))

    def _handle_set_assign(self, args: tuple[clingo.Symbol, ...]):
        if len(args) == 3:
            self.reg.update_set(args[1], assignment=(self.parse_expression(args[2]),))

    def parse_expression(self, symbol: clingo.Symbol) -> Expression:
        cached = self._expression_cache.get(symbol)
        if cached is not None:
            return cached

        try:
            term_name = symbol.name
            args = symbol.arguments
        except (AttributeError, RuntimeError):
            raise ValueError(f"Invalid expression format: {symbol}")

        if not args and term_name == "bad":
            expression = IValue(Type.FAIL, "bad")
            self._expression_cache[symbol] = expression
            return expression

        handler = self._dispatch_expr.get(term_name)
        if handler is not None:
            expression = handler(args)
            self._expression_cache[symbol] = expression
            return expression

        raise ValueError(f"Invalid expression format: {symbol}")

    def _handle_value(self, args: tuple[clingo.Symbol, ...]) -> Expression:
        if len(args) == 2:
            type_name = self.to_str(args[0]).lower()
            val_sym = args[1]
            if type_name == "symbol":
                normalized = val_sym.string if val_sym.type == clingo.SymbolType.String else self.to_str(val_sym)
                return IValue(Type.STRING, normalized)

            type_enum = _ASP_TO_TYPE_ENUM[type_name]
            return IValue(type_enum, self.cast_runtime_value(type_enum, val_sym))

    def _handle_variable(self, args: tuple[clingo.Symbol, ...]) -> Expression:
        if len(args) == 1:
            return IVariableRef(self._lower_variable_symbol(args[0]))

    def _handle_operation(self, args: tuple[clingo.Symbol, ...]) -> Expression:
        if len(args) == 2:
            op_sym = args[0]
            python_code = parse_python_operator(op_sym)
            unwound_args = tuple(self.parse_expression(item) for item in self.unnest(args[1]))

            if python_code is not None:
                bound_args = tuple(IBind(f"_fch_arg_{idx}", expr) for idx, expr in enumerate(unwound_args, start=1))
                return IPythonOperation(python_code, bound_args)

            operator = parse_operator(op_sym)
            normalized_args = self._normalize_operation_arguments(op_sym, unwound_args)
            return IOperation(operator, normalized_args)

    def _handle_python(self, args: tuple[clingo.Symbol, ...]) -> Expression:
        if len(args) == 1 and args[0].type == clingo.SymbolType.String:
            return IPythonOperation(code=args[0].string, arguments=(), outputs=("__fch_result",))
        if len(args) == 2 and args[0].type == clingo.SymbolType.String:
            target = self.to_str(args[1])
            return IPythonOperation(code=args[0].string, arguments=(), outputs=(target,))
        raise ValueError(f"Invalid python expression format: {args}")

    def _lower_variable_symbol(self, symbol: clingo.Symbol) -> clingo.Symbol | str:
        try:
            args = symbol.arguments
            if len(args) == 2:
                sym_name = symbol.name
                exec_arg, var_arg = args[0], args[1]

                if sym_name == "execution_input":
                    return clingo.Function("", [exec_arg, var_arg, clingo.Function("in", [])])
                if sym_name == "execution_output":
                    return clingo.Function("", [exec_arg, var_arg, clingo.Function("out", [])])
        except (AttributeError, RuntimeError):
            pass

        return symbol

    def _normalize_operation_arguments(
        self,
        operator_symbol: clingo.Symbol,
        arguments: tuple[Expression, ...],
    ) -> tuple[Expression, ...]:
        try:
            if operator_symbol.name == "union" and len(arguments) > 2:
                expression = IOperation(Operator.UNION, arguments[:2])
                for argument in arguments[2:]:
                    expression = IOperation(Operator.UNION, (expression, argument))
                return (
                    (expression.arguments[0], expression.arguments[1])
                    if isinstance(expression, IOperation)
                    else arguments
                )
        except (AttributeError, RuntimeError):
            pass
        return arguments
