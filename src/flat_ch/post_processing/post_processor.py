from __future__ import annotations

import clingo

from flat_ch.post_processing.optimization import OptimizationScore

_OPTIMIZE_OUTPUT_FLAG = "_fch_enable_optimize_value_output"


class PostProcessor:
    def __init__(self, control: clingo.Control) -> None:
        self._optimization_score = OptimizationScore(control)
        self._cached_symbols: list[clingo.Symbol] | None = None
        self._last_symbols: list[clingo.Symbol] | None = None

    def symbols(self, model: clingo.Model) -> list[clingo.Symbol]:
        if self._cached_symbols is not None:
            return self._cached_symbols

        symbols = self._optimization_score.symbols(model)
        if (
            model.optimality_proven
            and model.type in {clingo.ModelType.BraveConsequences, clingo.ModelType.CautiousConsequences}
            and self._last_symbols is not None
        ):
            symbols = self._last_symbols.copy()

        self._last_symbols = symbols.copy()
        if model.optimality_proven:
            self._cached_symbols = symbols.copy()
        return symbols


def _output_enabled(control: clingo.Control) -> bool:
    return next(control.symbolic_atoms.by_signature(_OPTIMIZE_OUTPUT_FLAG, 0), None) is not None


def add_post_processor(control: clingo.Control) -> None:
    original_solve = control.solve

    def solve(*args, **kwargs):
        if not _output_enabled(control):
            return original_solve(*args, **kwargs)

        postprocessor = PostProcessor(control)

        user_on_model = kwargs.get("on_model")
        if len(args) > 1 and args[1] is not None:
            user_on_model = args[1]

        def on_model(model: clingo.Model):
            model.extend(postprocessor.symbols(model))
            if user_on_model is not None:
                return user_on_model(model)
            return None

        if len(args) > 1:
            args = (args[0], on_model, *args[2:])
        else:
            kwargs["on_model"] = on_model

        return original_solve(*args, **kwargs)

    control.solve = solve
