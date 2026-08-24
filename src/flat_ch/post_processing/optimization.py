from __future__ import annotations

import clingo

from flat_ch.core.serialization import FLOAT_REMAINDER_SCALE, normalize_float_str
from flat_ch.core.types import Type


def _output_label(label: clingo.Symbol) -> clingo.Symbol:
    return label


class OptimizationScore:
    def __init__(self, control: clingo.Control) -> None:
        self._labels: list[tuple[clingo.Symbol, clingo.Symbol, clingo.Symbol]] = []
        for atom in control.symbolic_atoms.by_signature("_fch_optimize_label", 3):
            args = atom.symbol.arguments
            self._labels.append((args[0], args[1], args[2]))
        expression_ids = {expr_id for _, expr_id, _ in self._labels}
        priorities = {priority for _, _, priority in self._labels}

        self._dynamic_val_atoms: dict[clingo.Symbol, list[tuple[int, clingo.Symbol, clingo.Symbol]]] = {}
        for atom in control.symbolic_atoms.by_signature("_fch_dynamic_expr_val", 3):
            sym = atom.symbol
            if sym.arguments[0] in expression_ids:
                self._dynamic_val_atoms.setdefault(sym.arguments[0], []).append(
                    (atom.literal, sym.arguments[1], sym.arguments[2])
                )

        self._precision_atoms: dict[clingo.Symbol, list[tuple[int, int]]] = {}
        for atom in control.symbolic_atoms.by_signature("_fch_optimize_precision_value", 2):
            sym = atom.symbol
            if sym.arguments[0] in priorities:
                self._precision_atoms.setdefault(sym.arguments[0], []).append((atom.literal, sym.arguments[1].number))

    def symbols(self, model: clingo.Model) -> list[clingo.Symbol]:
        is_true = model.is_true

        dynamic_types: dict[clingo.Symbol, tuple[clingo.Symbol, clingo.Symbol]] = {}
        for expr_id, candidates in self._dynamic_val_atoms.items():
            for literal, type_id, value in candidates:
                if is_true(literal):
                    dynamic_types[expr_id] = (type_id, value)
                    break

        precisions: dict[clingo.Symbol, int] = {}
        for priority, candidates in self._precision_atoms.items():
            for literal, prec_num in candidates:
                if is_true(literal):
                    precisions[priority] = prec_num
                    break

        totals: dict[tuple[clingo.Symbol, clingo.Symbol], int] = {}
        int_type_sym = clingo.Number(Type.INT.value)
        bool_type_sym = clingo.Number(Type.BOOL.value)
        float_type_sym = clingo.Number(Type.FLOAT.value)

        for label, expr_id, priority in self._labels:
            key = (label, priority)
            dynamic_value = dynamic_types.get(expr_id)
            if dynamic_value is None:
                continue
            type_id, value = dynamic_value
            precision = precisions.get(priority, 1)
            if type_id == int_type_sym:
                weight = value.number * precision
            elif type_id == bool_type_sym:
                weight = precision if value.name == "true" else 0
            elif type_id == float_type_sym:
                int_part, remainder = value.arguments
                numeric = int_part.number + remainder.number / FLOAT_REMAINDER_SCALE
                weight = int(numeric * precision // 1)
            else:
                continue
            totals[key] = totals.get(key, 0) + weight

        results: list[clingo.Symbol] = []
        for (label, priority), scaled_total in totals.items():
            precision = precisions.get(priority, 1)
            numeric = scaled_total / precision

            if precision != 1 or not numeric.is_integer():
                value_type = clingo.Function("float", [])
                payload = clingo.Function("float", [clingo.String(normalize_float_str(numeric))])
            else:
                value_type = clingo.Function("int", [])
                payload = clingo.Number(int(numeric))

            value = clingo.Function("val", [value_type, payload])
            results.append(clingo.Function("optimize_value", [_output_label(label), priority, value]))

        return results
