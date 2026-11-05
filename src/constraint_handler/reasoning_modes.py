"""State and strategies for standard, brave, and cautious reasoning."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable

import clingo
from clingo import Symbol

from constraint_handler.PropagatorConstants import REASONING_MODE_PROGRAM, REASONING_STAGE_ATOM, ReasoningMode
from constraint_handler.PropagatorVariables import BoolEvaluateVariable, VariableType
from constraint_handler.schemas import result, warning


class _ReasoningStrategy(ABC):
    """
    Shared stage state and interface for a reasoning-mode strategy.

    This class should be subclassed to implement specific reasoning strategies
    such as brave or cautious reasoning.

    Properties:
        mode: The reasoning mode (standard, brave, or cautious, etc).
        stage_literals: Mapping from stage number to solver literal.
        variable_literals: Mapping from VariableType to solver literal.
        previously_stage_2: Flag indicating if stage 2 was previously reached.
        stage1_nogoods: List of nogoods accumulated in stage 1.
        accumulated_model: The accumulated model across model processing.
    """

    mode = ReasoningMode.STANDARD

    def __init__(self) -> None:
        self.stage_literals: dict[int, int] = {1: -1, 2: -1}
        self.variable_literals: dict[VariableType, int] = {}
        self.previously_stage_2 = False
        self.stage1_nogoods: list[Iterable[int]] = []
        self.accumulated_model: set[result.ResultAtom] | None = None

    def configure(self, ctl: clingo.Control) -> warning.Warning | None:
        """
        Configure the reasoning strategy with the given Clingo control object.

        Args:
            ctl: The Clingo control object.

        Returns:
            A warning if the configuration is not suitable for the reasoning strategy, otherwise None.
        """
        return None

    def reset(self) -> None:
        """
        Reset the internal state of the reasoning strategy.

        This includes clearing stage literals, variable literals, stage 1 nogoods,
        and the accumulated model, as well as resetting the previously_stage_2 flag.
        """
        self.stage_literals = {1: -1, 2: -1}
        self.variable_literals.clear()
        self.previously_stage_2 = False
        self.stage1_nogoods.clear()
        self.accumulated_model = None

    def add_helper_atoms(self, init: clingo.PropagateInit, variables: Iterable[VariableType]) -> None:
        """
        Add helper atoms for the given variables to the Clingo propagate initialization.

        Args:
            init: The Clingo propagate initialization object.
            variables: An iterable of variables for which to add helper atoms.

        Returns:
            None
        """
        return

    def process_model(
        self,
        model: set[result.ResultAtom],
        ctl: clingo.PropagateControl,
        variables_for_symbol: Callable[[Symbol], Iterable[VariableType]],
        get_reasons: Callable[[VariableType], set[int]],
    ) -> tuple[set[result.ResultAtom], list[Iterable[int]], bool]:
        """
        Process the given model and update the accumulated model.

        Args:
            model: The current model as a set of result atoms.
            ctl: The Clingo propagate control object.
            variables_for_symbol: A callable that maps a symbol to an iterable of variables.
            get_reasons: A callable that returns the reasons for a given variable.

        Returns:
            A tuple containing the updated model, a list of nogoods, and a boolean flag.
        """
        return model, [], False

    def get_nogoods(
        self,
        variables: set[result.ResultAtom],
        solver_stage: bool,
        variables_for_symbol: Callable[[Symbol], Iterable[VariableType]],
        get_reasons: Callable[[VariableType], set[int]],
    ) -> list[Iterable[int]]:
        """
        Get the nogoods for the given variables.

        Args:
            variables: A set of result atoms representing the variables.
            solver_stage: A boolean flag indicating the current solver stage. If True, the solver is still accumulating atoms handled by the solver.
            variables_for_symbol: A callable that maps a symbol to an iterable of variables.
            get_reasons: A callable that returns the reasons for a given variable.

        Returns:
            A list of nogoods, each represented as an iterable of integers.
        """
        return []


class _StagedReasoningStrategy(_ReasoningStrategy):
    """Common stage transitions for brave and cautious model enumeration."""

    def configure(self, ctl: clingo.Control) -> warning.Warning | None:
        ctl.add("base", [], REASONING_MODE_PROGRAM)
        if ctl.configuration.solver.heuristic != "Domain":  # ty:ignore[unresolved-attribute]
            return warning.Warning(
                warning.Propagator(),
                (),
                f"Brave/cautious reasoning requires --heuristic=Domain, but {ctl.configuration.solver.heuristic} was set. This may lead to incorrect results.",  # ty:ignore[unresolved-attribute]
            )
        return None

    def add_helper_atoms(self, init: clingo.PropagateInit, variables: Iterable[VariableType]) -> None:
        for atom in init.symbolic_atoms.by_signature(REASONING_STAGE_ATOM, 1):
            stage = atom.symbol.arguments[0].number
            assert stage in (1, 2, 3), f"Unknown reasoning stage atom: {atom.symbol}"
            if stage in self.stage_literals:
                self.stage_literals[stage] = init.solver_literal(atom.literal)

        for variable in variables:
            if isinstance(variable, BoolEvaluateVariable):
                continue
            self.variable_literals[variable] = init.add_literal(freeze=True)

    def process_model(
        self,
        model: set[result.ResultAtom],
        ctl: clingo.PropagateControl,
        variables_for_symbol: Callable[[Symbol], Iterable[VariableType]],
        get_reasons: Callable[[VariableType], set[int]],
    ) -> tuple[set[result.ResultAtom], list[Iterable[int]], bool]:
        previous_model = self.accumulated_model
        accumulated_model = self.accumulate_model(previous_model, model)
        self.accumulated_model = accumulated_model

        if not ctl.assignment.is_true(self.stage_literals[2]):
            self.stage1_nogoods.extend(self.get_nogoods(accumulated_model, True, variables_for_symbol, get_reasons))
            return accumulated_model, [], False

        if not self.previously_stage_2:
            self.previously_stage_2 = True
            nogoods = list(self.stage1_nogoods)
            nogoods.extend(self.get_nogoods(accumulated_model, True, variables_for_symbol, get_reasons))
            nogoods.append([-literal for literal in self.variable_literals.values()] + [self.stage_literals[2]])
            return accumulated_model, nogoods, True

        assert previous_model is not None
        considered = self.consider_model_changes(previous_model, accumulated_model)
        nogoods = self.get_nogoods(considered, False, variables_for_symbol, get_reasons)
        return accumulated_model, nogoods, True

    @abstractmethod
    def accumulate_model(
        self,
        previous_model: set[result.ResultAtom] | None,
        current_model: set[result.ResultAtom],
    ) -> set[result.ResultAtom]:
        raise NotImplementedError

    @abstractmethod
    def consider_model_changes(
        self,
        previous_model: set[result.ResultAtom],
        accumulated_model: set[result.ResultAtom],
    ) -> set[result.ResultAtom]:
        raise NotImplementedError

    @abstractmethod
    def get_nogoods(
        self,
        variables: set[result.ResultAtom],
        solver_stage: bool,
        variables_for_symbol: Callable[[Symbol], Iterable[VariableType]],
        get_reasons: Callable[[VariableType], set[int]],
    ) -> list[Iterable[int]]:
        raise NotImplementedError


class StandardReasoningStrategy(_ReasoningStrategy):
    """Keep the solver's current model without accumulating or adding nogoods."""


class BraveReasoningStrategy(_StagedReasoningStrategy):
    mode = ReasoningMode.BRAVE

    def accumulate_model(self, previous_model, current_model):
        if previous_model is None:
            return set(current_model)
        return previous_model.union(current_model)

    def consider_model_changes(self, previous_model, accumulated_model):
        return accumulated_model.difference(previous_model)

    def get_nogoods(self, variables, solver_stage, variables_for_symbol, get_reasons):
        return self._reasoning_nogoods(variables, variables_for_symbol, get_reasons)

    def _reasoning_nogoods(self, variables, variables_for_symbol, get_reasons):
        nogoods = []
        for result_var in self._variable_result_atoms(variables):
            for variable in variables_for_symbol(result_var.name):
                nogood = get_reasons(variable).union({self.variable_literals[variable]})
                nogood.add(self.stage_literals[2])
                nogoods.append(nogood)
        return nogoods

    @staticmethod
    def _variable_result_atoms(variables):
        for result_var in variables:
            if isinstance(
                result_var,
                (result.Evaluated, warning.Warning, warning.Warning_raised0, warning.Warning_raised1, warning.Warning_raised2),
            ):
                continue
            if not isinstance(result_var, (result.Value, result.Set_value, result.Multimap_value)):
                raise TypeError(f"Unexpected variable type: {type(result_var)} with value {result_var}")
            assert isinstance(result_var.name, Symbol)
            yield result_var


class CautiousReasoningStrategy(_StagedReasoningStrategy):
    mode = ReasoningMode.CAUTIOUS

    def accumulate_model(self, previous_model, current_model):
        if previous_model is None:
            return set(current_model)
        return previous_model.intersection(current_model)

    def consider_model_changes(self, previous_model, accumulated_model):
        return previous_model.difference(accumulated_model)

    def get_nogoods(self, variables, solver_stage, variables_for_symbol, get_reasons):
        nogoods = []
        for result_var in BraveReasoningStrategy._variable_result_atoms(variables):
            for variable in variables_for_symbol(result_var.name):
                if solver_stage:
                    nogood = get_reasons(variable).union({self.variable_literals[variable]})
                    nogood.add(self.stage_literals[2])
                    nogoods.append(nogood)
                else:
                    nogoods.append({self.variable_literals[variable], self.stage_literals[2]})
        return nogoods


class ReasoningModeHandler:
    """Select a reasoning strategy and expose its model/nogood interface."""

    def __init__(self) -> None:
        self._strategy: _ReasoningStrategy = StandardReasoningStrategy()

    def configure(self, ctl: clingo.Control) -> warning.Warning | None:
        mode = ctl.configuration.solve.enum_mode  # ty:ignore[unresolved-attribute]
        strategy_type = {
            "brave": BraveReasoningStrategy,
            "cautious": CautiousReasoningStrategy,
        }.get(mode, StandardReasoningStrategy)
        self._strategy = strategy_type()
        return self._strategy.configure(ctl)

    def reset(self) -> None:
        self._strategy.reset()

    def add_helper_atoms(self, init: clingo.PropagateInit, variables: Iterable[VariableType]) -> None:
        self._strategy.add_helper_atoms(init, variables)

    def process_model(
        self,
        model: set[result.ResultAtom],
        ctl: clingo.PropagateControl,
        variables_for_symbol: Callable[[Symbol], Iterable[VariableType]],
        get_reasons: Callable[[VariableType], set[int]],
    ) -> tuple[set[result.ResultAtom], list[Iterable[int]], bool]:
        return self._strategy.process_model(model, ctl, variables_for_symbol, get_reasons)

    def get_nogoods(
        self,
        variables: set[result.ResultAtom],
        solver_stage: bool,
        variables_for_symbol: Callable[[Symbol], Iterable[VariableType]],
        get_reasons: Callable[[VariableType], set[int]],
    ) -> list[Iterable[int]]:
        return self._strategy.get_nogoods(variables, solver_stage, variables_for_symbol, get_reasons)
