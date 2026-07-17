from __future__ import annotations

from flat_ch.ch_flattener import normalize_execution_declare
from flat_ch.ssa import SSA


class CHSSA:
    def __init__(self, flattener):
        self._flattener = flattener
        self._ssa = SSA()

    def apply(self, execution):
        normalized_execution = normalize_execution_declare(execution)
        ssa_done = self._ssa.apply(normalized_execution)
        return [fact for term in ssa_done for fact in self._flattener.flatten(term)]
