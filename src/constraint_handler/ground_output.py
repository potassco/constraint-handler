"""Readable ground program output for Clingo controls."""

import json
import typing
from functools import partialmethod
from tempfile import TemporaryFile

import clingo
from clingo.backend import Observer


class GroundProgramObserver(Observer):
    """Spool grounding events to disk until Clingo's atom names are available."""

    def __init__(self, ctrl: clingo.Control, output: typing.TextIO) -> None:
        self._ctrl = ctrl
        self._ground = ctrl.ground
        self._output = output
        self._spool: typing.TextIO | None = None
        self._objective = 0

    def ground(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        with TemporaryFile(mode="w+t", encoding="utf-8") as spool:
            self._spool = spool
            try:
                self._ground(*args, **kwargs)
            finally:
                self._spool = None

            names = {atom.literal: str(atom.symbol) for atom in self._ctrl.symbolic_atoms}
            spool.seek(0)
            for line in spool:
                callback, arguments = json.loads(line)
                self._emit(callback, *arguments, names=names)

    def _capture(self, callback: str, *args: typing.Any) -> None:
        match callback, args:
            case "begin_step" | "end_step", _:
                return
            case "output_atom" | "output_term", (symbol, value):
                args = (str(symbol), value)
            case "external", (atom, value):
                args = (atom, value.name.rstrip("_").lower())
            case "heuristic", (atom, kind, bias, priority, values):
                args = (atom, kind.name.rstrip("_").lower(), bias, priority, values)

        if self._spool is None:
            self._emit(callback, *args)
        else:
            self._spool.write(json.dumps((callback, args), separators=(",", ":")) + "\n")

    def _emit(self, callback: str, *args: typing.Any, names: dict[int, str] | None = None) -> None:
        def literal(value: int) -> str:
            atom = abs(value)
            name = names.get(atom) if names is not None else None
            if name is None:
                name = f"_ch_ground_atom({atom})"
            return f"not {name}" if value < 0 else name

        def condition(values: typing.Sequence[int], separator: str) -> str:
            return separator + ", ".join(map(literal, values)) if values else ""

        if callback in ("rule", "weight_rule"):
            choice, head, *body = args
            lhs = "; ".join(map(literal, head))
            if choice:
                lhs = f"{{{lhs}}}"
            if callback == "weight_rule":
                bound, weights = body
                elements = "; ".join(
                    f"{weight},{index} : {literal(value)}" for index, (value, weight) in enumerate(weights)
                )
                rhs = f"#sum {{ {elements} }} >= {bound}"
            else:
                rhs = ", ".join(map(literal, body[0]))
            self._output.write(f"{lhs}{' ' if lhs else ''}:- {rhs}.\n" if rhs else f"{lhs or ':-'}.\n")
            return

        match callback, args:
            case "init_program", _:
                self._output.write("#show.\n")
            case "minimize", (priority, weights):
                self._objective += 1
                elements = "; ".join(
                    f"{weight}@{priority},{self._objective},{index} : {literal(value)}"
                    for index, (value, weight) in enumerate(weights)
                )
                self._output.write(f"#minimize {{ {elements} }}.\n")
            case "output_atom", (symbol, atom):
                self._output.write(f"#show {symbol}{condition((atom,) if atom else (), ' : ')}.\n")
            case "output_term", (symbol, values):
                self._output.write(f"#show {symbol}{condition(values, ' : ')}.\n")
            case "external", (atom, value):
                self._output.write(f"#external {literal(atom)}. [{value}]\n")
            case "heuristic", (atom, modifier, bias, priority, values):
                body = condition(values, " : ")
                self._output.write(f"#heuristic {literal(atom)}{body}. [{bias}@{priority},{modifier}]\n")
            case "project", (atoms,):
                for atom in atoms:
                    self._output.write(f"#project {literal(atom)}.\n")
                if not atoms:
                    self._output.write("#project _ch_ground_atom(0) : #false.\n")
            case "acyc_edge", (source, target, values):
                self._output.write(f"#edge ({source},{target}){condition(values, ' : ')}.\n")
            case "assume", (values,) if values:
                self._output.write(f"% assume {', '.join(map(literal, values))}\n")
            case _ if callback.startswith("theory_"):
                self._output.write(f"% {callback}{args!r}\n")

    for _name, _callback in vars(Observer).items():
        if not _name.startswith("_") and callable(_callback):
            vars()[_name] = partialmethod(_capture, _name)
    del _name, _callback
