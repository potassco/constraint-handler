from importlib.resources import files
from typing import Any, Dict

import clingo
import clingo.script

from flat_ch.operators.python import set_default_globals

def add_to_control(control: clingo.Control, globals_map: Dict[str, Any], api: str = "flat"):
    if api == "ch":
        from flat_ch import ch_api

        ch_api.add_to_control(control, globals_map)
        return
    if api != "flat":
        raise ValueError(f"Unsupported api mode: {api}")

    clingo.script.enable_python()

    set_default_globals(globals_map)

    modules= [
        "encodings/api",
        "encodings/python",
        "encodings/python_api",
        "encodings/flatten",
        "encodings/aliasing",
        "encodings/solve",
        "encodings/set",
        "encodings/dict"
    ]

    for mod in modules:
        file = files("flat_ch").joinpath(f"{mod}.lp")
        control.load(str(file))
    
    generated_dir = files("flat_ch").joinpath("encodings/generated")
    for file in generated_dir.glob("*.lp"):
        control.load(str(file))
