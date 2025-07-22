from clingo import Symbol


def asp_to_python_list(symbol:Symbol) -> list[Symbol]:
    result = []
    if len(symbol.arguments) > 1:
        result.append(symbol.arguments[0])
        result.extend(asp_to_python_list(symbol.arguments[1]))
    return result