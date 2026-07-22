from __future__ import annotations

import ast
import itertools
from dataclasses import dataclass
from typing import Any

from clingo import Function, Number, String, Symbol

from flat_ch.core.domain import (
    BoolEvaluateInput,
    EnsureConstraint,
    EvaluateInput,
    Expression,
    ExprKind,
    FlatFact,
    IBind,
    IOperation,
    IPair,
    IPythonOperation,
    ISetDeclare,
    IValue,
    IVariableDeclare,
    IVariableDefine,
    IVariableRef,
    OptimizeMaximizeSum,
    OptimizePrecision,
    ProgramInput,
    ProgramInputKind,
    PythonEvaluateInput,
)
from flat_ch.core.evaluation.operators import Arity, Operator
from flat_ch.core.evaluation.python import PythonRegistry
from flat_ch.core.serialization import SerializerProtocol


def _is_python_expression(code: str) -> bool:
    try:
        ast.parse(code, mode="eval")
    except SyntaxError:
        return False
    return True


@dataclass(frozen=True, slots=True)
class InternedNode:
    expr_id: int
    kind: ExprKind
    payload: Any


class Flattener:
    def __init__(
        self,
        python_registry: PythonRegistry | None = None,
        serializer: SerializerProtocol | None = None,
        constant_folding: bool = False,
    ) -> None:
        self.py_reg = python_registry or PythonRegistry()
        if serializer is None:
            raise ValueError("Flattener requires a serializer instance.")
        self.serializer = serializer
        self.constant_folding = constant_folding
        self.expression_ids = itertools.count(100000)
        self.structural_cache: dict[tuple, int] = {}
        self.dag_nodes: dict[int, InternedNode] = {}
        self.interned_program: list[tuple[ProgramInputKind, tuple]] = []
        self.emitted_facts: list[Symbol] = []
        self.current_call_facts: set[Symbol] = set()

    def flatten(self, program_ir: list[ProgramInput]) -> list[Symbol]:
        self.structural_cache.clear()
        self.dag_nodes.clear()
        self.interned_program.clear()
        self.emitted_facts.clear()
        self.current_call_facts.clear()

        for node in program_ir:
            self._intern_program_input(node)

        self._emit_all_facts()
        return self.emitted_facts

    def _emit_fact(self, fact: Symbol) -> None:
        if fact in self.current_call_facts:
            return
        self.current_call_facts.add(fact)
        self.emitted_facts.append(fact)

    def _symbols_to_clingo_tuple(self, items: tuple[Symbol, ...]) -> Symbol:
        result = Function("", [])
        for item in reversed(items):
            result = Function("", [item, result])
        return result

    def _intern_program_input(self, node: ProgramInput) -> None:
        match node.kind:
            case ProgramInputKind.VARIABLE_DECLARE:
                var_decl: IVariableDeclare = node  # type: ignore
                dom_ids = tuple(self._intern_expr(arg) for arg in var_decl.domain)
                self.interned_program.append(
                    (ProgramInputKind.VARIABLE_DECLARE, (var_decl.name, dom_ids, var_decl.registration_id))
                )

            case ProgramInputKind.VARIABLE_DEFINE:
                var_def: IVariableDefine = node  # type: ignore
                expr_id = self._intern_expr(var_def.expression)
                self.interned_program.append(
                    (ProgramInputKind.VARIABLE_DEFINE, (var_def.name, expr_id, var_def.registration_id))
                )

            case ProgramInputKind.SET_DECLARE:
                set_decl: ISetDeclare = node  # type: ignore
                base_ids = tuple(self._intern_expr(expr) for expr in set_decl.base_domain)
                assignment_ids = tuple(self._intern_expr(expr) for expr in set_decl.assignment)
                self.interned_program.append((ProgramInputKind.SET_DECLARE, (set_decl.name, base_ids, assignment_ids)))

            case ProgramInputKind.ENSURE_CONSTRAINT:
                ens: EnsureConstraint = node  # type: ignore
                expr_id = self._intern_expr(ens.expression)
                label_str = ens.label if ens.label else "__anonymous"
                self.interned_program.append(
                    (ProgramInputKind.ENSURE_CONSTRAINT, (label_str, expr_id, ens.registration_id))
                )

            case ProgramInputKind.EVALUATE_INPUT:
                ev: EvaluateInput = node  # type: ignore
                op_expr = IOperation(ev.operator, ev.arguments)
                res_expr_id = self._intern_expr(op_expr)

                op_name = ev.operator.asp_name if isinstance(ev.operator, Operator) else str(ev.operator)

                orig_args_tuple = ev.original_argument_tuple
                if orig_args_tuple is None:
                    orig_args = tuple(self._to_raw_expr_symbol(arg) for arg in ev.arguments)
                    orig_args_tuple = self._symbols_to_clingo_tuple(orig_args)

                self.interned_program.append(
                    (ProgramInputKind.EVALUATE_INPUT, (op_name, orig_args_tuple, res_expr_id, ev.registration_id))
                )

            case ProgramInputKind.PYTHON_EVALUATE_INPUT:
                py_ev: PythonEvaluateInput = node  # type: ignore
                py_op = IPythonOperation(py_ev.code, py_ev.arguments)
                res_expr_id = self._intern_expr(py_op)

                orig_args_tuple = py_ev.original_argument_tuple
                if orig_args_tuple is None:
                    orig_args = tuple(self._to_raw_expr_symbol(b.expression) for b in py_ev.arguments)
                    orig_args_tuple = self._symbols_to_clingo_tuple(orig_args)

                self.interned_program.append(
                    (
                        ProgramInputKind.PYTHON_EVALUATE_INPUT,
                        (py_ev.code, orig_args_tuple, res_expr_id, py_ev.registration_id),
                    )
                )

            case ProgramInputKind.BOOL_EVALUATE_INPUT:
                bev: BoolEvaluateInput = node  # type: ignore
                expr_id = self._intern_expr(bev.expression)
                orig_symbol = bev.original_expression
                if orig_symbol is None:
                    orig_symbol = self._to_raw_expr_symbol(bev.expression)

                self.interned_program.append(
                    (ProgramInputKind.BOOL_EVALUATE_INPUT, (orig_symbol, expr_id, bev.registration_id))
                )

            case ProgramInputKind.OPTIMIZE_MAXIMIZE_SUM:
                opt_sum: OptimizeMaximizeSum = node  # type: ignore
                expr_id = self._intern_expr(opt_sum.expression)
                self.interned_program.append(
                    (
                        ProgramInputKind.OPTIMIZE_MAXIMIZE_SUM,
                        (expr_id, opt_sum.element, opt_sum.priority, opt_sum.label),
                    )
                )

            case ProgramInputKind.OPTIMIZE_PRECISION:
                opt_prec: OptimizePrecision = node  # type: ignore
                expr_id = self._intern_expr(opt_prec.expression)
                self.interned_program.append((ProgramInputKind.OPTIMIZE_PRECISION, (expr_id, opt_prec.priority)))

            case _:
                pass

    def _intern_expr(self, expr: Expression) -> int:
        match expr.kind:
            case ExprKind.VALUE:
                val_node: IValue = expr  # type: ignore
                cache_key = (ExprKind.VALUE, val_node.type, val_node.value)

                expr_id = self.structural_cache.get(cache_key)
                if expr_id is None:
                    expr_id = next(self.expression_ids)
                    self.structural_cache[cache_key] = expr_id
                    self.dag_nodes[expr_id] = InternedNode(expr_id, ExprKind.VALUE, (val_node.type, val_node.value))
                return expr_id

            case ExprKind.VARIABLE:
                var_node: IVariableRef = expr  # type: ignore
                cache_key = (ExprKind.VARIABLE, var_node.name)

                expr_id = self.structural_cache.get(cache_key)
                if expr_id is None:
                    expr_id = next(self.expression_ids)
                    self.structural_cache[cache_key] = expr_id
                    self.dag_nodes[expr_id] = InternedNode(expr_id, ExprKind.VARIABLE, var_node.name)
                return expr_id

            case ExprKind.OPERATION:
                op_node: IOperation = expr  # type: ignore
                arg_ids = tuple(self._intern_expr(arg) for arg in op_node.arguments)
                cache_key = (ExprKind.OPERATION, op_node.operator, arg_ids)

                expr_id = self.structural_cache.get(cache_key)
                if expr_id is None:
                    expr_id = next(self.expression_ids)
                    self.structural_cache[cache_key] = expr_id
                    self.dag_nodes[expr_id] = InternedNode(expr_id, ExprKind.OPERATION, (op_node.operator, arg_ids))
                return expr_id

            case ExprKind.PYTHON_OPERATION:
                py_op: IPythonOperation = expr  # type: ignore
                target_out = py_op.outputs[0] if py_op.outputs else "__fch_result"
                arg_names = [bind.name for bind in py_op.arguments]
                call_args = ", ".join(arg_names)

                code_str = py_op.code.strip()

                if not py_op.outputs:
                    executable_code = f"{target_out} = ({code_str})({call_args})"
                elif _is_python_expression(code_str):
                    executable_code = f"{target_out} = {code_str}"
                else:
                    executable_code = code_str

                python_id = self.py_reg.register_program(executable_code, target_output=target_out)

                bound_ids = tuple((b.name, self._intern_expr(b.expression)) for b in py_op.arguments)
                cache_key = (
                    ExprKind.PYTHON_OPERATION,
                    python_id,
                    bound_ids,
                    py_op.outputs,
                )

                expr_id = self.structural_cache.get(cache_key)
                if expr_id is None:
                    expr_id = next(self.expression_ids)
                    self.structural_cache[cache_key] = expr_id
                    self.py_reg.link_expr_to_program(
                        expr_id,
                        python_id,
                        [name for name, _arg_id in bound_ids],
                    )
                    self.dag_nodes[expr_id] = InternedNode(
                        expr_id,
                        ExprKind.PYTHON_OPERATION,
                        (python_id, bound_ids, py_op.outputs),
                    )
                return expr_id

            case ExprKind.BIND:
                bind_node: IBind = expr  # type: ignore
                child_id = self._intern_expr(bind_node.expression)
                cache_key = (ExprKind.BIND, bind_node.name, child_id)

                expr_id = self.structural_cache.get(cache_key)
                if expr_id is None:
                    expr_id = next(self.expression_ids)
                    self.structural_cache[cache_key] = expr_id
                    self.dag_nodes[expr_id] = InternedNode(expr_id, ExprKind.BIND, (bind_node.name, child_id))
                return expr_id

            case ExprKind.PAIR:
                pair_node: IPair = expr  # type: ignore
                k_id = self._intern_expr(pair_node.key)
                v_id = self._intern_expr(pair_node.value)
                cache_key = (ExprKind.PAIR, k_id, v_id)

                expr_id = self.structural_cache.get(cache_key)
                if expr_id is None:
                    expr_id = next(self.expression_ids)
                    self.structural_cache[cache_key] = expr_id
                    self.dag_nodes[expr_id] = InternedNode(expr_id, ExprKind.PAIR, (k_id, v_id))
                return expr_id

            case _:
                raise ValueError(f"Unknown expression kind: {expr.kind}")

    def _to_raw_expr_symbol(self, expr: Expression) -> Symbol:
        match expr.kind:
            case ExprKind.VALUE:
                val_node: IValue = expr  # type: ignore
                clingo_val = self.serializer.python_to_clingo(val_node.type, val_node.value).arguments[1]
                type_sym = Function(val_node.type.name.lower(), [])
                return Function("val", [type_sym, clingo_val])

            case ExprKind.VARIABLE:
                var_node: IVariableRef = expr  # type: ignore
                var_name = var_node.name

                if isinstance(var_name, Symbol):
                    if var_name.name == "" and len(var_name.arguments) == 3:
                        exec_sym, var_sym, dir_sym = var_name.arguments
                        if dir_sym.name == "in":
                            var_sym = Function("execution_input", [exec_sym, var_sym])
                        elif dir_sym.name == "out":
                            var_sym = Function("execution_output", [exec_sym, var_sym])
                        else:
                            var_sym = var_name
                    else:
                        var_sym = var_name
                else:
                    var_sym = Function(var_name, [])

                return Function("variable", [var_sym])

            case ExprKind.OPERATION:
                op_node: IOperation = expr  # type: ignore
                op_name = op_node.operator.asp_name if isinstance(op_node.operator, Operator) else str(op_node.operator)
                args_sym = Function("", [])
                for arg in reversed(op_node.arguments):
                    args_sym = Function("", [self._to_raw_expr_symbol(arg), args_sym])
                return Function("operation", [Function(op_name, []), args_sym])

            case ExprKind.PYTHON_OPERATION:
                py_op: IPythonOperation = expr  # type: ignore
                target_out = py_op.outputs[0] if py_op.outputs else "__fch_result"
                py_sym = Function("python", [String(py_op.code), String(target_out)])
                args_sym = Function("", [])
                for b in reversed(py_op.arguments):
                    bind_sym = Function("bind", [String(b.name), self._to_raw_expr_symbol(b.expression)])
                    args_sym = Function("", [bind_sym, args_sym])
                return Function("operation", [py_sym, args_sym])

            case ExprKind.BIND:
                bind_node: IBind = expr  # type: ignore
                return Function("bind", [String(bind_node.name), self._to_raw_expr_symbol(bind_node.expression)])

            case ExprKind.PAIR:
                pair_node: IPair = expr  # type: ignore
                return Function(
                    "pair", [self._to_raw_expr_symbol(pair_node.key), self._to_raw_expr_symbol(pair_node.value)]
                )

            case _:
                raise ValueError(f"Unknown expr kind: {expr.kind}")

    def _emit_all_facts(self) -> None:
        for node in self.dag_nodes.values():
            self._emit_dag_node_fact(node)

        for kind, payload in self.interned_program:
            self._emit_program_input_fact(kind, payload)

    def _emit_dag_node_fact(self, node: InternedNode) -> None:
        eid_num = Number(node.expr_id)

        match node.kind:
            case ExprKind.VALUE:
                val_type, raw_value = node.payload
                clingo_val = self.serializer.python_to_clingo(val_type, raw_value).arguments[1]
                self._emit_fact(
                    Function(
                        FlatFact.EXPRESSION_VALUE.value,
                        [eid_num, Number(val_type.value), clingo_val],
                    )
                )

            case ExprKind.VARIABLE:
                var_payload = node.payload
                if isinstance(var_payload, Symbol):
                    var_sym = var_payload
                else:
                    var_sym = Function(var_payload, [])

                self._emit_fact(
                    Function(
                        FlatFact.EXPRESSION_VARIABLE.value,
                        [eid_num, var_sym],
                    )
                )

            case ExprKind.OPERATION:
                operator, arg_ids = node.payload
                op_enum = operator if isinstance(operator, Operator) else Operator[str(operator).upper()]
                op_name = op_enum.asp_name
                allowed = op_enum.allowed_arities
                arity_count = len(arg_ids)

                if arity_count == 1 and (allowed & Arity.UNARY):
                    self._emit_fact(Function(f"op_{op_name}", [eid_num, Number(arg_ids[0])]))
                elif arity_count == 2 and (allowed & Arity.BINARY):
                    self._emit_fact(
                        Function(
                            f"op_{op_name}",
                            [eid_num, Number(arg_ids[0]), Number(arg_ids[1])],
                        )
                    )
                elif arity_count == 3 and (allowed & Arity.TERNARY):
                    self._emit_fact(
                        Function(
                            f"op_{op_name}",
                            [
                                eid_num,
                                Number(arg_ids[0]),
                                Number(arg_ids[1]),
                                Number(arg_ids[2]),
                            ],
                        )
                    )
                elif allowed & Arity.VARIADIC:
                    self._emit_fact(Function(f"op_{op_name}_variadic", [eid_num, Number(arity_count)]))
                    for pos, arg_id in enumerate(arg_ids, start=1):
                        self._emit_fact(
                            Function(
                                f"op_{op_name}_arg",
                                [eid_num, Number(pos), Number(arg_id)],
                            )
                        )
                else:
                    raise TypeError(f"Operator {op_enum.name} does not support arity count of {arity_count}.")

            case ExprKind.PYTHON_OPERATION:
                python_id, bound_ids, outputs = node.payload
                out_target = outputs[0] if outputs else ""

                self._emit_fact(
                    Function(
                        "op_python",
                        [eid_num, Number(python_id), String(out_target)],
                    )
                )

                arity_count = len(bound_ids)
                self._emit_fact(Function("op_python_variadic", [eid_num, Number(arity_count)]))
                for pos, (_var_name, arg_id) in enumerate(bound_ids, start=1):
                    self._emit_fact(
                        Function(
                            "op_python_arg",
                            [eid_num, Number(pos), Number(arg_id)],
                        )
                    )

            case ExprKind.PAIR:
                k_id, v_id = node.payload
                self._emit_fact(
                    Function(
                        FlatFact.PAIR.value,
                        [eid_num, Number(k_id), Number(v_id)],
                    )
                )

            case _:
                pass

    def _emit_program_input_fact(self, kind: ProgramInputKind, payload: tuple) -> None:
        match kind:
            case ProgramInputKind.VARIABLE_DECLARE:
                name, dom_ids, registration_id = payload
                var_sym = name if isinstance(name, Symbol) else Function(name, [])
                decl_args = [var_sym]
                if registration_id is not None:
                    decl_args.insert(0, Number(registration_id))
                self._emit_fact(Function(FlatFact.VARIABLE_DECLARE.value, decl_args))
                for dom_id in dom_ids:
                    dom_args = [var_sym, Number(dom_id)]
                    if registration_id is not None:
                        dom_args.insert(0, Number(registration_id))
                    self._emit_fact(
                        Function(
                            FlatFact.VARIABLE_DOMAIN.value,
                            dom_args,
                        )
                    )

            case ProgramInputKind.VARIABLE_DEFINE:
                name, expr_id, registration_id = payload
                var_sym = name if isinstance(name, Symbol) else Function(name, [])
                fact_name = FlatFact.VARIABLE_DEFINE.value
                fact_args = [var_sym, Number(expr_id)]
                if registration_id is not None:
                    fact_args.insert(0, Number(registration_id))
                self._emit_fact(Function(fact_name, fact_args))

            case ProgramInputKind.SET_DECLARE:
                name, base_ids, assignment_ids = payload
                set_sym = name if isinstance(name, Symbol) else Function(name, [])
                self._emit_fact(Function(FlatFact.SET.value, [set_sym]))
                for expr_id in base_ids:
                    self._emit_fact(
                        Function(
                            FlatFact.SET_BASE_DOMAIN.value,
                            [set_sym, Number(expr_id)],
                        )
                    )
                for expr_id in assignment_ids:
                    self._emit_fact(
                        Function(
                            FlatFact.SET_ASSIGN.value,
                            [set_sym, Number(expr_id)],
                        )
                    )

            case ProgramInputKind.ENSURE_CONSTRAINT:
                label_str, expr_id, registration_id = payload
                fact_name = FlatFact.ENSURE.value
                fact_args = [Function(label_str, []), Number(expr_id)]
                if registration_id is not None:
                    fact_args.insert(0, Number(registration_id))
                self._emit_fact(Function(fact_name, fact_args))

            case ProgramInputKind.EVALUATE_INPUT:
                op_name, args_tuple, res_expr_id, registration_id = payload
                fact_name = FlatFact.EVALUATE.value
                fact_args = [Function(op_name, []), args_tuple, Number(res_expr_id)]
                if registration_id is not None:
                    fact_args.insert(0, Number(registration_id))
                self._emit_fact(Function(fact_name, fact_args))

            case ProgramInputKind.PYTHON_EVALUATE_INPUT:
                code_str, args_tuple, res_expr_id, registration_id = payload
                fact_name = FlatFact.EVALUATE.value
                fact_args = [Function("python", [String(code_str)]), args_tuple, Number(res_expr_id)]
                if registration_id is not None:
                    fact_args.insert(0, Number(registration_id))
                self._emit_fact(Function(fact_name, fact_args))

            case ProgramInputKind.BOOL_EVALUATE_INPUT:
                orig_symbol, expr_id, registration_id = payload
                fact_name = FlatFact.BOOL_EVALUATE.value
                fact_args = [orig_symbol, Number(expr_id)]
                if registration_id is not None:
                    fact_args.insert(0, Number(registration_id))
                self._emit_fact(Function(fact_name, fact_args))

            case ProgramInputKind.OPTIMIZE_MAXIMIZE_SUM:
                expr_id, elem, prio, label = payload
                elem_sym = elem if isinstance(elem, Symbol) else Function(elem, [])
                label_sym = Function(label if label is not None else "_label_anonymous", [])
                self._emit_fact(
                    Function(
                        FlatFact.OPTIMIZE_SUM.value,
                        [Number(expr_id), elem_sym, Number(prio)],
                    )
                )
                self._emit_fact(
                    Function(
                        FlatFact.OPTIMIZE_LABEL.value,
                        [label_sym, Number(expr_id), Number(prio)],
                    )
                )

            case ProgramInputKind.OPTIMIZE_PRECISION:
                expr_id, prio = payload
                prio_sym = Number(prio) if isinstance(prio, int) else Function(str(prio), [])
                self._emit_fact(
                    Function(
                        FlatFact.OPTIMIZE_PRECISION.value,
                        [Number(expr_id), prio_sym],
                    )
                )

            case _:
                pass

    def debug_print_dag(self) -> None:
        print(f"\n=== INTERNED EXPRESSION DAG (Nodes: {len(self.dag_nodes)}) ===")
        for expr_id, node in self.dag_nodes.items():
            print(f"  [{expr_id}] {node.kind.name} -> {node.payload}")

        print(f"\n=== CANONICAL PROGRAM INPUTS (Declarations: {len(self.interned_program)}) ===")
        for kind, payload in self.interned_program:
            print(f"  {kind.name}: {payload}")
        print("===============================================================\n")
