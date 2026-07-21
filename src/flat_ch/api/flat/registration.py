from __future__ import annotations

from typing import TYPE_CHECKING

import clingo

from flat_ch.api.flat.input import UserInput
from flat_ch.core.base_registration import BaseRegistration, parse_operator, parse_python_operator
from flat_ch.core.domain import (
    BoolEvaluateInput,
    EnsureConstraint,
    EvaluateInput,
    ExecutionDeclare,
    ExecutionRun,
    Expression,
    IBind,
    IOperation,
    IPair,
    IPythonOperation,
    IValue,
    IVariableDefine,
    IVariableRef,
    OptimizeMaximizeSum,
    OptimizePrecision,
    PythonEvaluateInput,
)
from flat_ch.core.serialization import SerializerProtocol
from flat_ch.core.types import Type

if TYPE_CHECKING:
    from flat_ch.core.registry import ProgramRegistry


_ASP_TO_TYPE_ENUM = {type_name.lower(): type_enum for type_name, type_enum in Type.__members__.items()}


class Registration(BaseRegistration):
    def __init__(self, registry: ProgramRegistry, serializer: SerializerProtocol) -> None:
        super().__init__(serializer)
        self.reg = registry
        self._expression_cache: dict[clingo.Symbol, Expression] = {}

        self._ui_decl = UserInput.DECLARE.value
        self._ui_dom = UserInput.DOMAIN.value
        self._ui_def = UserInput.DEFINE.value
        self._ui_ensure = UserInput.ENSURE.value
        self._ui_eval = UserInput.EVALUATE.value
        self._ui_bool_eval = UserInput.BOOL_EVALUATE.value
        self._ui_set_decl = UserInput.SET_DECLARE.value
        self._ui_set_base = UserInput.SET_BASE_DOMAIN.value
        self._ui_set_assign = UserInput.SET_ASSIGN.value
        self._ui_opt_sum = UserInput.OPTIMIZE_SUM.value
        self._ui_opt_prec = UserInput.OPTIMIZE_PRECISION.value
        self._ui_exec_decl = UserInput.EXECUTION_DECLARE.value
        self._ui_exec_run = UserInput.EXECUTION_RUN.value
        self._ui_val = UserInput.VALUE.value
        self._ui_var = UserInput.VARIABLE.value
        self._ui_bind = UserInput.BIND.value
        self._ui_pair = UserInput.PAIR.value
        self._ui_op = UserInput.OPERATION.value

    def parse_expression(self, symbol: clingo.Symbol) -> Expression:
        if symbol in self._expression_cache:
            return self._expression_cache[symbol]

        term_name = symbol.name
        args = symbol.arguments
        node: Expression

        if term_name == self._ui_val:
            type_enum = _ASP_TO_TYPE_ENUM[self.to_str(args[0]).lower()]
            node = IValue(type_enum, self.cast_runtime_value(type_enum, args[1]))
        elif term_name == self._ui_var:
            node = IVariableRef(self.to_str(args[0]))
        elif term_name == self._ui_bind:
            node = IBind(self.to_str(args[0]), self.parse_expression(args[1]))
        elif term_name == self._ui_pair:
            node = IPair(self.parse_expression(args[0]), self.parse_expression(args[1]))
        elif term_name == self._ui_op:
            python_code = parse_python_operator(args[0])
            unwound_args = tuple(self.parse_expression(item) for item in self.unnest(args[1]))
            if python_code is not None:
                node = IPythonOperation(python_code, unwound_args)
            else:
                node = IOperation(parse_operator(args[0]), unwound_args)
        else:
            raise ValueError(f"Unknown FCH expression signature: {symbol}")

        self._expression_cache[symbol] = node
        return node

    def register(self, term: clingo.Symbol) -> clingo.Number:
        if term.type != clingo.SymbolType.Function:
            return clingo.Number(0)

        term_name = term.name
        args = term.arguments
        args_len = len(args)

        match term_name:
            case self._ui_decl if args_len == 1:
                self.reg.update_var(self.to_str(args[0]), ())
            case self._ui_dom if args_len == 2:
                self.reg.update_var(self.to_str(args[0]), (self.parse_expression(args[1]),))
            case self._ui_def if args_len == 2:
                self.reg.sequential_inputs.append(
                    IVariableDefine(
                        self.to_str(args[0]), self.parse_expression(args[1]), self.reg.current_registration_id
                    )
                )
            case self._ui_ensure if args_len == 1:
                self.reg.sequential_inputs.append(
                    EnsureConstraint(None, self.parse_expression(args[0]), self.reg.current_registration_id)
                )
            case self._ui_ensure if args_len == 2:
                self.reg.sequential_inputs.append(
                    EnsureConstraint(
                        self.to_str(args[0]), self.parse_expression(args[1]), self.reg.current_registration_id
                    )
                )
            case self._ui_eval if args_len == 2:
                unwound = tuple(self.parse_expression(s) for s in self.unnest(args[1]))
                python_code = parse_python_operator(args[0])
                if python_code is not None:
                    self.reg.sequential_inputs.append(
                        PythonEvaluateInput(
                            None, python_code, unwound, registration_id=self.reg.current_registration_id
                        )
                    )
                else:
                    self.reg.sequential_inputs.append(
                        EvaluateInput(
                            None, parse_operator(args[0]), unwound, registration_id=self.reg.current_registration_id
                        )
                    )
            case self._ui_eval if args_len == 3:
                lbl = self.to_str(args[0])
                unwound = tuple(self.parse_expression(s) for s in self.unnest(args[2]))
                python_code = parse_python_operator(args[1])
                if python_code is not None:
                    self.reg.sequential_inputs.append(
                        PythonEvaluateInput(lbl, python_code, unwound, registration_id=self.reg.current_registration_id)
                    )
                else:
                    self.reg.sequential_inputs.append(
                        EvaluateInput(
                            lbl, parse_operator(args[1]), unwound, registration_id=self.reg.current_registration_id
                        )
                    )
            case self._ui_bool_eval if args_len == 2:
                lbl = None if args[0] == args[1] else self.to_str(args[0])
                self.reg.sequential_inputs.append(
                    BoolEvaluateInput(
                        lbl, self.parse_expression(args[1]), registration_id=self.reg.current_registration_id
                    )
                )
            case self._ui_set_decl if args_len == 1:
                self.reg.update_set(self.to_str(args[0]))
            case self._ui_set_base if args_len == 2:
                self.reg.update_set(self.to_str(args[0]), base_domain=(self.parse_expression(args[1]),))
            case self._ui_set_assign if args_len == 2:
                self.reg.update_set(self.to_str(args[0]), assignment=(self.parse_expression(args[1]),))
            case self._ui_opt_sum if args_len == 3:
                self.reg.sequential_inputs.append(
                    OptimizeMaximizeSum(self.parse_expression(args[0]), self.to_str(args[1]), int(args[2].number))
                )
            case self._ui_opt_prec if args_len == 1:
                self.reg.sequential_inputs.append(OptimizePrecision(self.parse_expression(args[0])))
            case self._ui_opt_prec if args_len == 2:
                self.reg.sequential_inputs.append(
                    OptimizePrecision(self.parse_expression(args[0]), self.scalar_value(args[1]))
                )
            case self._ui_exec_decl if args_len == 4:
                self.reg.sequential_inputs.append(
                    ExecutionDeclare(
                        self.to_str(args[0]),
                        self.scalar_value(args[1]),
                        tuple(self.to_str(symbol) for symbol in self.unnest(args[2])),
                        tuple(self.to_str(symbol) for symbol in self.unnest(args[3])),
                    )
                )
            case self._ui_exec_run if args_len == 1:
                self.reg.sequential_inputs.append(ExecutionRun(self.to_str(args[0])))
            case _:
                raise ValueError(f"Invalid or out-of-spec FCH fact format: {term}")

        return clingo.Number(0)
