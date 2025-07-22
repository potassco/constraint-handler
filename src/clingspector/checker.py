from enum import Enum
import logging
import os
from clingo.control import Control, Model

from clingspector.diagnostic import Diagnostic

logger = logging.getLogger("clingspector")

class Flags(Enum):
    VERBOSE = 1

class Checker:
    def __init__(self):
        self._set_default_flags()
        self._diagnostics: list[Diagnostic] = []
        self._ctl = Control(["--warn=none"])

        features_directory = "src/clingspector/features"

        base_files = ["src/clingspector/base.lp"]
        base_files.extend([
            f"{features_directory}/{file}" for file in os.listdir(features_directory) if file.endswith(".lp")
        ])

        for file in base_files:
            logger.debug(f"Loading base file: {file}")
            self._ctl.load(file)

    def get_diagnostics(self) -> list[Diagnostic]:
        return self._diagnostics
    
    def _set_default_flags(self):
        """Set default flags for the checker."""
        self._verbose = False

    def set_flags(self, option: Flags, value:bool):
        match option:
            case Flags.VERBOSE:
                self._verbose = value

    def load(self, files):
        for file in files:
            self._ctl.load(file)
    
    def solve(self):
        self._ctl.ground([("base", [])])
        ret = self._ctl.solve(on_model=self._on_model)

        if ret.satisfiable and self._verbose:
            logger.info("SAT")
        if ret.unsatisfiable and self._verbose:
            logger.info("UNSAT")

    def _on_model(self, model:Model):
        for symbol in model.symbols(shown = True):
            diagnostic = Diagnostic.from_symbol(symbol)

            if diagnostic:
                self._diagnostics.append(diagnostic)

        for diagnostic in self._diagnostics:
            logger.warning(str(diagnostic))

        if self._verbose:
            logger.info('\n '.join(str(s) for s in model.symbols(shown=True)))