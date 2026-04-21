import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import nox

nox.options.sessions = ("test",)
# nox.options.sessions = "lint_pylint", "typecheck", "test"

EDITABLE_TESTS = True
if "GITHUB_ACTIONS" in os.environ:
    EDITABLE_TESTS = False

BENCHMARK_ROOT = Path(".benchmarks")


def install_test_dependencies(session):
    args = [".[test]"]
    if EDITABLE_TESTS:
        args.insert(0, "-e")
    session.install(*args)


def benchmark_save_name():
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        check=False,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not branch:
        branch = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        ).stdout.strip()
    safe_branch = re.sub(r"[^A-Za-z0-9._-]+", "-", branch or "detached").strip("-") or "detached"
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return f"{safe_branch}-{timestamp}"


def flatten_benchmark_results() -> None:
    root = BENCHMARK_ROOT
    if not root.exists():
        return

    for benchmark_file in sorted(root.rglob("*.json")):
        if benchmark_file.parent == root:
            continue
        target = root / benchmark_file.name
        if target.exists():
            benchmark_file.unlink()
            continue
        benchmark_file.replace(target)

    for directory in sorted(root.rglob("*"), reverse=True):
        if directory.is_dir():
            try:
                directory.rmdir()
            except OSError:
                pass


def resolve_benchmark_file(path_str: str) -> Path:
    candidate = Path(path_str)
    if candidate.exists():
        return candidate

    flattened_candidate = BENCHMARK_ROOT / candidate.name
    if flattened_candidate.exists():
        return flattened_candidate

    raise FileNotFoundError(path_str)


def load_benchmark_means(path: Path) -> tuple[str, dict[str, float]]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    means: dict[str, float] = {}
    for benchmark in payload.get("benchmarks", []):
        benchmark_id = benchmark.get("param") or benchmark.get("fullname") or benchmark.get("name")
        stats = benchmark.get("stats", {})
        mean = stats.get("mean")
        if benchmark_id and mean is not None:
            means[benchmark_id] = float(mean)

    return path.stem, means


def format_seconds(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:0.3f}"


def format_percent(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:+0.1f}%"


def compare_saved_benchmarks(session, baseline_path: Path, contender_path: Path) -> None:
    baseline_label, baseline_means = load_benchmark_means(baseline_path)
    contender_label, contender_means = load_benchmark_means(contender_path)

    common_ids = sorted(set(baseline_means) & set(contender_means))
    if not common_ids:
        session.error("no overlapping benchmarks found in the supplied files")

    rows: list[tuple[str, float, float, float, float | None]] = []
    for benchmark_id in common_ids:
        baseline = baseline_means[benchmark_id]
        contender = contender_means[benchmark_id]
        delta = contender - baseline
        percent = None if baseline == 0 else (delta / baseline) * 100
        rows.append((benchmark_id, baseline, contender, delta, percent))

    rows.sort(key=lambda row: (row[3] == 0, row[0]))

    headers = (
        "benchmark",
        f"{baseline_label} avg [s]",
        f"{contender_label} avg [s]",
        "delta [s]",
        "delta [%]",
    )
    widths = [len(header) for header in headers]
    rendered_rows: list[tuple[str, str, str, str, str]] = []
    for benchmark_id, baseline, contender, delta, percent in rows:
        rendered = (
            benchmark_id,
            format_seconds(baseline),
            format_seconds(contender),
            f"{delta:+0.3f}",
            format_percent(percent),
        )
        widths = [max(width, len(value)) for width, value in zip(widths, rendered)]
        rendered_rows.append(rendered)

    def render_line(values: tuple[str, str, str, str, str]) -> str:
        return "  ".join(
            value.ljust(width) if index == 0 else value.rjust(width)
            for index, (value, width) in enumerate(zip(values, widths))
        )

    session.log(f"baseline:  {baseline_path}")
    session.log(f"contender: {contender_path}")
    session.log(render_line(headers))
    session.log(render_line(tuple("-" * width for width in widths)))
    for rendered in rendered_rows:
        session.log(render_line(rendered))

    missing_in_contender = sorted(set(baseline_means) - set(contender_means))
    missing_in_baseline = sorted(set(contender_means) - set(baseline_means))
    if missing_in_contender:
        session.log(f"missing in contender: {', '.join(missing_in_contender)}")
    if missing_in_baseline:
        session.log(f"missing in baseline: {', '.join(missing_in_baseline)}")


def run_performance_session(session):
    pytest_args = list(session.posargs) if session.posargs else []
    pytest_args.insert(0, os.fspath(Path("tests/test_encoding.py")))

    try:
        session.run(
            "pytest",
            *pytest_args,
            f"--benchmark-storage={BENCHMARK_ROOT.resolve().as_uri()}",
            f"--benchmark-save={benchmark_save_name()}",
            "--benchmark-min-rounds=1",
            "-m",
            "performance",
            "-vvv",
        )
    finally:
        flatten_benchmark_results()


@nox.session
def doc(session):
    """
    Build the documentation.

    Accepts the following arguments:
    - serve: open documentation after build
    - further arguments are passed to mkbuild
    """

    options = session.posargs[:]
    open_doc = "serve" in options
    if open_doc:
        options.remove("serve")

    session.install("-e", ".[doc]")

    if open_doc:
        open_cmd = "xdg-open" if sys.platform == "linux" else "open"
        session.run(open_cmd, "http://localhost:8000/systems/constraint_handler/")
        session.run("mkdocs", "serve", *options)
    else:
        session.run("mkdocs", "build", *options)


@nox.session
def dev(session):
    """
    Create a development environment in editable mode.

    Activate it by running `source .nox/dev/bin/activate`.
    """
    session.install("-e", ".[dev]")


@nox.session
def lint_pylint(session):
    """
    Run pylint.
    """
    session.install("-e", ".[lint_pylint]")
    session.run("pylint", "constraint_handler", "tests")


@nox.session
def typecheck(session):
    """
    Typecheck the code using mypy.
    """
    session.install("-e", ".[typecheck]")
    session.run("mypy", "--strict", "-p", "constraint_handler", "-p", "tests")


@nox.session
def test(session):
    """
    Run pytest.

    """

    install_test_dependencies(session)
    if session.posargs:
        session.run("pytest", *session.posargs, "-vvv")
    else:
        session.run("pytest", "-m", "not performance", "-vvv")


@nox.session
def performance(session):
    """
    Run performance checks and save benchmark results under .benchmarks.
    """
    install_test_dependencies(session)
    run_performance_session(session)


@nox.session
def benchmark_compare(session):
    """
    Compare saved benchmark runs using mean runtime only.

    Usage:
        nox -s benchmark_compare -- path/to/run1.json path/to/run2.json
    """
    install_test_dependencies(session)
    flatten_benchmark_results()
    if len(session.posargs) != 2:
        session.error("usage: nox -s benchmark_compare -- <baseline.json> <contender.json>")
    try:
        baseline_path = resolve_benchmark_file(session.posargs[0])
        contender_path = resolve_benchmark_file(session.posargs[1])
    except FileNotFoundError as error:
        session.error(f"benchmark file not found: {error.args[0]}")
        return

    compare_saved_benchmarks(session, baseline_path, contender_path)
