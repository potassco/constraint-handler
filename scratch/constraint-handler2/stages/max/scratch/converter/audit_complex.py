"""Audit converted legacy fixtures against native and complex ASP encodings."""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import resource
import signal
import subprocess
import sys
import time
import traceback
from collections import Counter
from importlib.resources import files
from pathlib import Path

from clingo.control import Control
from clingo.core import Library
from clingo.script import enable_python
from clingo.solve import Model
from clingo.symbol import Function, Symbol, SymbolType, parse_term

from constraint_handler import Engine, Operator, PreprocessOptions, Preprocessor
from constraint_handler.asp_facts import asp_facts
from constraint_handler.internal_input import Operation

from .converter import ConversionError, convert_file, convert_string

ROOT = Path(__file__).resolve().parents[6]
CORPUS = ROOT / "tests"
MODEL_LIMIT = 1000
LOGGER = logging.getLogger(__name__)


def legacy_value(symbol: Symbol) -> object:
    """Decode legacy expected values without conflating Boolean and numeric types."""
    if symbol.type == SymbolType.Number:
        return ("integer", symbol.number)
    if symbol.type == SymbolType.String:
        return ("string", symbol.string)
    if symbol.type == SymbolType.Tuple:
        return ("tuple", tuple(legacy_value(item) for item in symbol.arguments))
    if symbol.name == "val":
        kind, value = symbol.arguments
        if kind.name == "int":
            return ("integer", value.number)
        if kind.name == "float":
            number = value.arguments[0].string if value.arguments else value.number
            return ("real", float(number))
        if kind.name in {"bool", "boolean"}:
            return ("boolean", str(value) == "true")
        if kind.name == "string":
            return ("string", value.string)
        if kind.name == "none":
            return ("none", None)
    return ("unsupported", str(symbol))


def current_value(symbol: Symbol) -> object:
    """Decode current value terms into the same typed comparison keys."""
    if symbol.name == "integer":
        return ("integer", symbol.arguments[0].number)
    if symbol.name == "real":
        return ("real", float(symbol.arguments[0].string))
    if symbol.name == "string":
        return ("string", symbol.arguments[0].string)
    if symbol.name == "boolean":
        return ("boolean", str(symbol.arguments[0]) == "true")
    if symbol.name == "none":
        return ("none", None)
    if symbol.name == "tuple" and symbol.arguments:
        return (
            "tuple",
            tuple(current_value(item) for item in symbol.arguments[0].arguments),
        )
    return ("unsupported", str(symbol))


def model_values(atoms: list[Symbol]) -> dict[Symbol, object]:
    """Decode complete scalar, set, and tuple payloads keyed by their subjects."""
    values = {
        atom.arguments[0]: atom.arguments[1] for atom in atoms if atom.name == "value"
    }
    sizes = {
        atom.arguments[0]: atom.arguments[1].number
        for atom in atoms
        if atom.name == "tuple_size"
    }
    members: dict[Symbol, set[object]] = {}
    slots: dict[Symbol, dict[int, Symbol]] = {}
    for atom in atoms:
        if atom.name == "set_value":
            subject, member = atom.arguments
            key = current_value(member)
            members.setdefault(subject, set()).add(
                ("number", key[1]) if key[0] in {"integer", "real"} else key
            )
    for subject in values:
        if subject.type == SymbolType.Function and subject.name == "__tuple":
            parent, index = subject.arguments
            slots.setdefault(parent, {})[index.number] = subject

    def decode(subject: Symbol) -> object:
        """Require every tuple slot and preserve defined empty collections."""
        value = values[subject]
        if value.name == "set":
            return ("set", frozenset(members.get(subject, ())))
        if value.name == "tuple" and not value.arguments:
            return (
                "tuple",
                tuple(decode(slots[subject][index]) for index in range(sizes[subject])),
            )
        return current_value(value)

    return {subject: decode(subject) for subject in values}


def audit_case(path: Path, domains_only: bool = False) -> dict[str, object]:
    """Run one fixture, retaining stage failures and model-level evidence."""
    result: dict[str, object] = {"case": str(path.relative_to(CORPUS))}
    stage = "conversion"
    started = time.monotonic()

    def checkpoint(next_stage: str) -> None:
        """Flush the last completed measurements before potentially expensive work."""
        nonlocal stage
        stage = next_stage
        result["stage"] = stage
        result["elapsed_seconds"] = round(time.monotonic() - started, 3)
        result["peak_rss_mib"] = round(
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1
        )
        print(json.dumps({"progress": result}), flush=True)

    try:
        checkpoint("conversion")
        try:
            store = convert_file(path)
            result["conversion_mode"] = "direct"
        except ConversionError as error:
            result["direct_conversion_error"] = str(error)
            if (
                path.parent == CORPUS
                or "performance" not in path.relative_to(CORPUS).parts
            ):
                raise
            checkpoint("input_grounding")
            input_lib = Library()
            input_control = Control(input_lib, ["2"])
            input_control.parse_files([str(path)])
            input_control.ground()
            input_models: list[list[Symbol]] = []
            input_control.solve(
                on_model=lambda model: input_models.append(model.symbols(atoms=True))
            )
            if len(input_models) != 1:
                raise ValueError(
                    "grounding adapter requires one deterministic input model"
                ) from error
            source_facts = []
            for atom in input_models[0]:
                if not (
                    atom.name.startswith(("variable_", "set_", "execution_"))
                    or atom.name
                    in {"ensure", "evaluate", "bool_evaluate", "phase_request"}
                ):
                    continue
                args = list(atom.arguments)
                if (
                    atom.name == "variable_declare"
                    and len(args) == 3
                    and str(args[2])
                    in {"fromFacts", "open", "definition", "set", "boolDomain"}
                ):
                    args = [args[0], args[2], args[1]]
                elif atom.name == "execution_declare" and len(args) == 5:
                    args = [args[1], args[2], args[3], args[4], args[0]]
                elif atom.name == "execution_run" and len(args) == 2:
                    args = [args[1]]
                source_facts.append(str(Function(input_lib, atom.name, args)) + ".")
            result["grounded_input_facts"] = len(source_facts)
            result["conversion_mode"] = "grounded_legacy_adapter"
            checkpoint("conversion")
            store = convert_string("\n".join(sorted(source_facts)))
        result["variables"] = len(store.variables)
        result["set_variables"] = len(store.set_variables)
        result["defaults"] = sum(
            len(variable.defaults) for variable in store.variables.values()
        )
        result["constraints"] = len(store.constraints)
        result["original_expressions"] = len(store.expressions)
        checkpoint("preprocessing")
        preprocessor = Preprocessor(PreprocessOptions())
        preprocessor.add(store)
        problem, diagnostics = preprocessor.preprocess()
        result["diagnostics"] = [
            {"severity": str(item.severity), "message": item.message}
            for item in diagnostics.items
        ]
        domain_groups = {
            "roots": [
                (str(expr_id), problem.domains.get(expression))
                for expr_id, expression in problem.store.expressions.items()
            ],
            "variables": [
                (variable.name, problem.domains.get(variable))
                for variable in (*problem.store.variables, *problem.store.set_variables)
            ],
            "metadata": [
                (str(index), domain)
                for index, domain in enumerate(problem.domains.values())
            ],
        }
        result["domain_summary"] = {}
        for group, entries in domain_groups.items():
            categories = {
                "unknown": [
                    name
                    for name, domain in entries
                    if domain is not None and domain.unknown
                ],
                "empty": [
                    name
                    for name, domain in entries
                    if domain is not None and domain.is_empty()
                ],
                "integer_interval": [
                    name
                    for name, domain in entries
                    if domain is not None and domain.int_range is not None
                ],
                "implicit_set": [
                    name
                    for name, domain in entries
                    if domain is not None and domain.implicit_set_elements is not None
                ],
                "explicit_set": [
                    name
                    for name, domain in entries
                    if domain is not None and domain.explicit_sets
                ],
                "nullable": [
                    name
                    for name, domain in entries
                    if domain is not None and domain.has_none
                ],
                "tuple": [
                    name
                    for name, domain in entries
                    if domain is not None and domain.tuples
                ],
                "missing_metadata": [
                    name for name, domain in entries if domain is None
                ],
            }
            result["domain_summary"][group] = {
                "total": len(entries),
                **{category: len(names) for category, names in categories.items()},
            }
            if group != "metadata":
                result[f"{group}_domain_examples"] = {
                    category: names[:30]
                    for category, names in categories.items()
                    if names
                }
        result["unknown_root_expressions"] = [
            {"id": expr_id, "expression": str(expression)[:600]}
            for expr_id, expression in problem.store.expressions.items()
            if problem.domains.get(expression) is not None
            and problem.domains[expression].unknown
        ][:30]
        if diagnostics.has_errors:
            result["status"] = "preprocessing_errors"
            return result
        result["engines"] = dict(
            Counter(str(engine) for engine in problem.engines.values())
        )
        auxiliaries = set(problem.store.variables) - set(store.variables)
        result["split_auxiliaries"] = len(auxiliaries)
        result["auxiliary_names"] = sorted(variable.name for variable in auxiliaries)[
            :30
        ]
        result["prepared_expressions"] = len(problem.store.expressions)
        calls = []
        for expr_id, expression in problem.store.expressions.items():
            if (
                not isinstance(expression, Operation)
                or expression.op != Operator.python_eval
            ):
                continue
            counts = [problem.domains[arg].cardinality() for arg in expression.args[1:]]
            calls.append(
                {
                    "id": expr_id,
                    "arguments": [str(arg) for arg in expression.args[1:]],
                    "domain_sizes": counts,
                    "result_unknown": problem.domains[expression].unknown,
                    "estimated_rows": None if None in counts else math.prod(counts),
                    "source": str(expression.args[0])[:500],
                }
            )
        result["call_count"] = len(calls)
        result["unknown_input_calls"] = [
            call for call in calls if None in call["domain_sizes"]
        ]
        result["unknown_result_calls"] = [
            call for call in calls if call["result_unknown"]
        ]
        result["largest_calls"] = sorted(
            calls, key=lambda call: call["estimated_rows"] or 0, reverse=True
        )[:20]
        result["estimated_rows"] = (
            None
            if any(call["estimated_rows"] is None for call in calls)
            else sum(call["estimated_rows"] for call in calls)
        )
        if domains_only:
            result["status"] = "domains_only"
            checkpoint("domains_complete")
            return result
        checkpoint("facts")
        lib = Library()
        enable_python(lib)
        facts = asp_facts(lib, problem.store, problem.engines, problem.domains)
        result["rows"] = sum(fact.name == "output" for fact in facts)
        result["sample_outputs"] = [
            str(fact) for fact in facts if fact.name == "output"
        ][:100]
        checkpoint("solver_creation")
        if Engine.propagator in problem.engines.values():
            raise NotImplementedError(
                "solving with unknown input domains requires a propagator"
            )
        checkpoint("grounding")
        control = Control(lib, ["0"])
        control.parse_string("\n".join(f"{fact}." for fact in facts))
        for encoding in (
            "native.lp",
            "boolean.lp",
            "integer.lp",
            "eq.lp",
            "set.lp",
            "tuples.lp",
            "none.lp",
            "complex.lp",
        ):
            control.parse_string(
                files("constraint_handler").joinpath("encoding", encoding).read_text()
            )
        control.ground([("base", [])])
        checkpoint("solving")
        models: list[set[tuple[str, str, object]]] = []
        raw_models: list[list[str]] = []

        def collect(model: Model) -> bool:
            """Capture variable values and stop explicitly at the audit model cap."""
            values: set[tuple[str, str, object]] = set()
            raw: list[str] = []
            atoms = model.symbols(atoms=True)
            payloads = model_values(atoms)
            for atom in atoms:
                if atom.name not in {"value", "set_value"}:
                    continue
                subject, value = atom.arguments
                if subject.type != SymbolType.Function or subject.name != "variable":
                    continue
                values.add(
                    (
                        atom.name,
                        subject.arguments[0].string,
                        payloads[subject]
                        if atom.name == "value"
                        else current_value(value),
                    )
                )
                raw.append(str(atom))
            models.append(values)
            if len(raw_models) < 5:
                raw_models.append(sorted(raw)[:150])
            return len(models) < MODEL_LIMIT

        solve_result = control.solve(on_model=collect)
        result["model_count"] = len(models)
        result["exhausted"] = solve_result.exhausted
        result["sample_models"] = raw_models
        checkpoint("expectations")
        failures: list[dict[str, object]] = []
        ignored: list[str] = []
        checked = 0
        for expectation_file in sorted(path.parent.glob(path.stem + ".expected.*")):
            quantifier = expectation_file.suffix[1:]
            if quantifier == "stats":
                for line in expectation_file.read_text().splitlines():
                    if line.startswith("models="):
                        checked += 1
                        expected_count = int(line.split("=", 1)[1])
                        if expected_count != len(models):
                            failures.append(
                                {
                                    "kind": "model_count",
                                    "expected": expected_count,
                                    "actual": len(models),
                                }
                            )
                continue
            for line in expectation_file.read_text().splitlines():
                if not line.strip():
                    continue
                atom = parse_term(lib, line.strip())
                if atom.name not in {"value", "set_value"} or len(atom.arguments) != 2:
                    ignored.append(f"{quantifier}: {line}")
                    continue
                variable, value = atom.arguments
                key = (
                    atom.name,
                    variable.string
                    if variable.type == SymbolType.String
                    else str(variable),
                    legacy_value(value),
                )
                if key[2][0] == "unsupported":
                    ignored.append(f"{quantifier}: {line}")
                    continue
                present = [key in model for model in models]
                if quantifier in {"all", "cautious"}:
                    holds = bool(models) and all(present)
                elif quantifier in {"any", "brave"}:
                    holds = any(present)
                elif quantifier == "none":
                    holds = not any(present)
                elif quantifier in {"first", "last"}:
                    ignored.append(f"order-dependent {quantifier}: {line}")
                    continue
                else:
                    ignored.append(f"unsupported {quantifier}: {line}")
                    continue
                checked += 1
                if not holds:
                    failures.append(
                        {
                            "kind": quantifier,
                            "expected": line,
                            "models_with_value": sum(present),
                        }
                    )
        result["checked_expectations"] = checked
        result["ignored_expectations"] = ignored
        result["failures"] = failures
        if not solve_result.exhausted:
            result["status"] = "model_limit"
        elif failures:
            result["status"] = "value_mismatch"
        elif not models:
            result["status"] = "unsatisfiable_unverified"
        elif not checked:
            result["status"] = "no_value_expectations"
        elif ignored:
            result["status"] = "values_match_diagnostics_unchecked"
        else:
            result["status"] = "expectations_match"
    except Exception as error:
        LOGGER.exception("Audit failed during %s", stage)
        result["status"] = f"{stage}_exception"
        result["error"] = f"{type(error).__name__}: {error}"
        result["traceback"] = traceback.format_exc()
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    result["peak_rss_mib"] = round(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1
    )
    return result


def main() -> None:
    """Isolate all corpus cases with per-case timeouts and write machine-readable evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path(__file__).with_name("audit_results.json")
    )
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--cpu-seconds", type=int, default=10)
    parser.add_argument("--memory-mib", type=int, default=768)
    parser.add_argument(
        "--section",
        choices=("correctness", "performance", "sets", "all"),
        default="all",
    )
    parser.add_argument("--domains-only", action="store_true")
    arguments = parser.parse_args()
    if arguments.case:
        memory_bytes = arguments.memory_mib * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        resource.setrlimit(
            resource.RLIMIT_CPU, (arguments.cpu_seconds, arguments.cpu_seconds + 1)
        )
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        print(
            json.dumps(audit_case(arguments.case, domains_only=arguments.domains_only))
        )
        return
    results = []
    sections = (
        ("correctness", "performance")
        if arguments.section == "all"
        else ("correctness/set",)
        if arguments.section == "sets"
        else (arguments.section,)
    )
    paths = sorted(
        path for section in sections for path in (CORPUS / section).rglob("*.lp")
    )
    for path in paths:
        result = {"case": str(path.relative_to(CORPUS))}
        try:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "scratch.converter.audit_complex",
                    "--case",
                    str(path),
                    "--memory-mib",
                    str(arguments.memory_mib),
                    "--cpu-seconds",
                    str(arguments.cpu_seconds),
                    *(["--domains-only"] if arguments.domains_only else []),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            timed_out = False
            try:
                stdout, stderr = process.communicate(timeout=arguments.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
            for line in stdout.splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                result = event.get("progress", event)
            if timed_out:
                result["status"] = "wall_timeout"
            elif process.returncode:
                result["status"] = (
                    "cpu_limit"
                    if process.returncode == -signal.SIGXCPU
                    else "worker_exit"
                )
            elif "status" not in result:
                result["status"] = "runner_error"
            result["returncode"] = process.returncode
            if stderr:
                result["stderr"] = stderr[-8000:]
        except (ValueError, OSError) as error:
            result = {
                "case": str(path.relative_to(CORPUS)),
                "status": "runner_error",
                "error": str(error),
            }
        result["limits"] = {
            "wall_seconds": arguments.timeout,
            "cpu_seconds": arguments.cpu_seconds,
            "memory_mib": arguments.memory_mib,
            "models": MODEL_LIMIT,
        }
        results.append(result)
        arguments.output.write_text(json.dumps(results, indent=2) + "\n")
        print(f"{result['case']}: {result['status']}", flush=True)
    arguments.output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(dict(Counter(result["status"] for result in results)), indent=2))


if __name__ == "__main__":
    main()
