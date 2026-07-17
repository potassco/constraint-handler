from clingo import Symbol, SymbolType


def symbol_name(symbol: Symbol) -> str:
    if symbol.type == SymbolType.String:
        return symbol.string
    if symbol.type == SymbolType.Function:
        return symbol.name
    return str(symbol)
