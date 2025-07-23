"""Utility functions for converting ASP to Python data structures."""

from clingo import Symbol


def asp_to_python_list(symbol: Symbol) -> list[Symbol]:
    """Convert an ASP list symbol to a Symbol list."""

    result = []
    if len(symbol.arguments) > 1:
        result.append(symbol.arguments[0])
        result.extend(asp_to_python_list(symbol.arguments[1]))

    return result
