import argparse
import sys
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict

import clingo
import clingo.script

from flat_ch.core.evaluation.python import set_default_globals
from flat_ch.core.file_generation import generate_files


def _print_model(model: clingo.Model) -> None:
    shown_symbols = model.symbols(shown=True)
    if not shown_symbols:
        return

    print("\n".join(str(symbol) for symbol in shown_symbols))


def add_to_control(control: clingo.Control, globals_map: Dict[str, Any], api: str) -> None:
    if api not in {"flat", "ch"}:
        raise ValueError(f"Unsupported api mode: {api}")

    clingo.script.enable_python()
    set_default_globals(globals_map)

    api_pkg = files("flat_ch.api.ch") if api == "ch" else files("flat_ch.api.flat")
    core_pkg = files("flat_ch.core")
    modules = [
        api_pkg.joinpath("api.lp"),
        api_pkg.joinpath("python_api.lp"),
        core_pkg.joinpath("encodings/python.lp"),
        core_pkg.joinpath("encodings/flatten.lp"),
        core_pkg.joinpath("encodings/aliasing.lp"),
        core_pkg.joinpath("encodings/solve.lp"),
        core_pkg.joinpath("encodings/set.lp"),
        core_pkg.joinpath("encodings/dict.lp"),
    ]

    for file in modules:
        control.load(str(file))

    generated_dir = core_pkg.joinpath("encodings/generated")
    for file in generated_dir.glob("*.lp"):
        control.load(str(file))


def _run_file(target_file: Path, api_mode: str) -> int:
    try:
        control = clingo.Control()
        add_to_control(control, {}, api_mode)
        control.load(str(target_file))
        control.ground([("base", [])])
        control.solve(on_model=_print_model)
        return 0
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(prog="fch", description="Flat Constraint Handler")

    parser.add_argument("--generate", action="store_true", help="Generate static/dynamic variants from your templates.")
    parser.add_argument("--ch", action="store_true", help="Run the input file through the CH-compatible API.")
    parser.add_argument("file", nargs="?", help="Logic program to run with flat_ch boilerplate.")

    args = parser.parse_args()

    if args.generate:
        if args.file is not None:
            parser.error("--generate does not accept an input file")
        generate_files()
        return

    if args.file is None:
        parser.print_help()
        sys.exit(0)

    target_file = Path(args.file).resolve()
    if not target_file.is_file():
        parser.error(f"Input file not found: {target_file}")

    api_mode = "ch" if args.ch else "flat"
    sys.exit(_run_file(target_file, api_mode))


if __name__ == "__main__":
    main()
