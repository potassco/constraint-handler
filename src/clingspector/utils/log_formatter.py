"""Module for the custom logging formatter."""

import logging
from enum import Enum


class ANSIColors(Enum):
    """ANSI Codes for text coloring.

    A coloring code turns any text following it into the respective color,
    to return to normal formatting the reset code is required.
    """

    GREEN = "\x1b[32;1m"
    YELLOW = "\x1b[33;1m"
    WHITE = "\x1b[37;1m"
    RED = "\x1b[31;1m"
    BLUE = "\x1b[34;1m"
    RESET = "\x1b[0m"
    """ Reset all text formatting."""


class LoggingFormatter(logging.Formatter):
    """
    Basic logging formatter with more information and coloring.
    """

    _BASE_FORMAT = (
        f"%(levelname)-8s{ANSIColors.RESET.value} | "
        f"{ANSIColors.WHITE.value}%(asctime)s{ANSIColors.RESET.value} | "
        f"%(message)s"
    )
    """ Basic format for all debug levels."""

    _FORMATS = {
        logging.DEBUG: ANSIColors.BLUE.value + _BASE_FORMAT + ANSIColors.RESET.value,
        logging.INFO: ANSIColors.GREEN.value + _BASE_FORMAT + ANSIColors.RESET.value,
        logging.WARNING: ANSIColors.YELLOW.value + _BASE_FORMAT + ANSIColors.RESET.value,
        logging.ERROR: ANSIColors.RED.value + _BASE_FORMAT + ANSIColors.RESET.value,
        logging.CRITICAL: ANSIColors.RED.value + _BASE_FORMAT + ANSIColors.RESET.value,
    }
    """ Debug-level specific formats."""

    def format(self, record: logging.LogRecord) -> str:
        """Create and set the actual formatter and format."""

        log_fmt = self._FORMATS.get(record.levelno, self._BASE_FORMAT)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)
