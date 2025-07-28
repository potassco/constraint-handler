""" This module contains the Clingspector class for checking Clingo logic programs.

"""

from __future__ import annotations

import logging
import os
from enum import Enum

from clingo.control import Control, Model

from clingspector.diagnostic import Diagnostic

logger = logging.getLogger("clingspector")


class Clingspector:
    """Clingspector class for validating Clingo logic programs and reporting errors."""

    class Option(Enum):
        """Options for the Clingspector."""

        VERBOSE = 1
        """ Enable verbose output.

            This includes the clingo model output.
        """

    def __init__(self) -> None:
        self._diagnostics: list[Diagnostic] = []
        self._ctl = Control(["--warn=none"])
        self._verbose = False

        features_directory = "src/clingspector/features"

        base_files = ["src/clingspector/base.lp"]
        base_files.extend(
            [f"{features_directory}/{file}" for file in os.listdir(features_directory) if file.endswith(".lp")]
        )

        for file in base_files:
            logger.debug("Loading base file: %s", file)
            self._ctl.load(file)

    def get_diagnostics(self) -> list[Diagnostic]:
        """Get the list of diagnostics found during the last solve."""

        return self._diagnostics

    def set_flags(self, option: Clingspector.Option, value: bool) -> None:
        """Set a flag to a given value"""

        match option:
            case Clingspector.Option.VERBOSE:
                self._verbose = value

    def load(self, files: list[str]) -> None:
        """Load Clingo files."""

        for file in files:
            self._ctl.load(file)

    def run(self) -> None:
        """Run the Clingspector to check the loaded Clingo files."""

        self._ctl.ground([("base", [])])
        ret = self._ctl.solve(on_model=self._on_model)

        if ret.satisfiable and self._verbose:
            logger.info("SAT")
        if ret.unsatisfiable and self._verbose:
            logger.info("UNSAT")

    def _on_model(self, model: Model):
        for symbol in model.symbols(shown=True):
            diagnostic = Diagnostic.from_symbol(symbol)

            if diagnostic:
                self._diagnostics.append(diagnostic)

        for diagnostic in self._diagnostics:
            logger.warning(str(diagnostic))

        if self._verbose:
            logger.info("\n ".join(str(s) for s in model.symbols(shown=True)))
