import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import clingo
import pytest

import constraint_handler
import tests.utils.testing as chut

ctrl_options = ["0", "--heuristic=Domain"]
Engine = Literal["compile", "ground", "propagator"]
performance_examples_dir = Path("tests/example/performance")


@dataclass(frozen=True)
class PerformanceBenchmark:
    name: str
    engine: Engine
    max_average_seconds: float
    measured_runs: int = 1
    warmup_runs: int = 0
    check_mode: bool = False
    constants: dict[str, int] | None = None

    @property
    def pytest_id(self) -> str:
        if self.engine != "propagator":
            return f"{self.engine}-{self.name}"
        mode = "check" if self.check_mode else "solve"
        return f"{self.engine}-{mode}-{self.name}"

    @property
    def program_path(self) -> str:
        return performance_examples_dir / f"{self.name}.lp"


def run_test(name: str, engine: Engine, check_mode: bool = False):
    name = "tests/example/" + name
    engine_prg = f"defaultEngine({engine})."
    solver = chut.Solver(ctrl_options, engine_prg, files=[name + ".lp"], propagator_check_only=check_mode)
    test = chut.build_expectations(name)
    solver.solve(test)
    test.assert_()

    for test, extra_args in chut.build_reasoning_mode_expectations(name):
        solver = chut.Solver(ctrl_options + extra_args, engine_prg, files=[name + ".lp"])
        solver.solve(test)
        test.assert_()


def run_benchmark_program(benchmark: PerformanceBenchmark) -> None:
    benchmark_options = list(ctrl_options)
    if benchmark.constants:
        for name, value in sorted(benchmark.constants.items()):
            benchmark_options.extend(["-c", f"{name}={value}"])

    ctl = clingo.Control(benchmark_options)
    constraint_handler.add_to_control(ctl, propagator_check_only=benchmark.check_mode)
    ctl.add(f"defaultEngine({benchmark.engine}).")
    ctl.load(os.fspath(benchmark.program_path))
    ctl.ground()
    ctl.solve()


def run_benchmark_case(benchmark: PerformanceBenchmark) -> None:
    run_benchmark_program(benchmark)


def assert_benchmark_threshold(benchmark, benchmark_case: PerformanceBenchmark) -> None:
    durations = benchmark.stats.stats.data
    average_runtime = benchmark.stats["mean"]
    assert average_runtime <= benchmark_case.max_average_seconds, (
        f"{benchmark_case.engine} benchmark {benchmark_case.name} average runtime {average_runtime:.3f}s exceeded "
        f"{benchmark_case.max_average_seconds:.3f}s over {len(durations)} measured runs "
        f"(durations={', '.join(f'{duration:.3f}s' for duration in durations)})"
    )


def benchmark_param(benchmark: PerformanceBenchmark):
    return pytest.param(benchmark, id=benchmark.pytest_id)


base_tests = [
    "basic_assignments",
    "booleans",
    "bool_evaluate",
    "conditional_assign",
    "custom_globals",
    "empty_variadics",
    "engine_request",
    "engine_request_interaction",
    "engine_request_mult",
    "engine_request_set_ref",
    "eq_compound_int",
    "error_recovery",
    "error_recovery_ensure",
    "executions",
    "execution_assert",
    "execution_conditional",
    "execution_loop",
    "floats",
    "ints",
    "integrity",
    "lambdas",
    "lambda_recursive",
    "lambda_zero_args",
    "multimap_basics",
    "multimap_equality",
    "multimap_executions",
    "multimaps",
    "nested_set",
    "optimize_bools",
    "optimize_floats",
    "optimize_ints",
    "optimize_priority",
    "set_membership_decomposed",
    "set_membership_python",
    "python_multi_args",
    "reasoning_modes",
    "set_comparisons",
    "set_executions",
    "set_fold_bools",
    "set_from_domain",
    "set_iterations",
    "set_manipulations",
    "set_selfref",
    "strings",
    "type_checking",
    "variable_parallel_declaration",
    "variable_flexible_domain",
    "variables",
    "warning_bad",
    "warning_fake_forbid",
    "warning_python",
    "warning_statement_malformed",
    "warning_syntax",
    "warning_type",
    "warning_variables",
    "warning_variable_confusingName",
    "warning_variable_undeclared",
    "warning_variable_undeclared_statement",
]

compile_extra = [
    "preferences",
]
ground_extra = []
propagator_extra = []

compile_benchmarks = [
    benchmark_param(
        PerformanceBenchmark(
            "sum_aggregates",
            "compile",
            1.5,
        )
    ),
    benchmark_param(PerformanceBenchmark("sum_chain_performance", "compile", 1.0)),
    benchmark_param(
        PerformanceBenchmark(
            "repeated_constraints_performance",
            "compile",
            60.0,
            constants={"pair_count": 1000},
        )
    ),
    benchmark_param(
        PerformanceBenchmark(
            "large_int_domain_performance",
            "compile",
            60.0,
            constants={"int_domain_size": 8000},  # uses an excessive amount of memory
        )
    ),
    benchmark_param(
        PerformanceBenchmark(
            "assignment_chain_performance",
            "compile",
            15.0,
            constants={"chain_length": 200},
        )
    ),
]

ground_benchmarks = [
    benchmark_param(
        PerformanceBenchmark(
            "sum_aggregates",
            "ground",
            100.0,
        )
    ),
    benchmark_param(PerformanceBenchmark("sum_chain_performance", "ground", 1.0)),
    benchmark_param(
        PerformanceBenchmark(
            "repeated_constraints_performance",
            "ground",
            70.0,
            constants={"pair_count": 1000},
        )
    ),
    benchmark_param(
        PerformanceBenchmark(
            "large_int_domain_performance",
            "ground",
            75.0,
            constants={"int_domain_size": 900},
        )
    ),
    benchmark_param(
        PerformanceBenchmark(
            "assignment_chain_performance",
            "ground",
            2.0,
            constants={"chain_length": 200},
        )
    ),
]

propagator_benchmarks = [
    benchmark_param(
        PerformanceBenchmark(
            "sum_aggregates",
            "propagator",
            85.0,
            check_mode=True,
        )
    ),
    benchmark_param(
        PerformanceBenchmark(
            "sum_aggregates",
            "propagator",
            65.0,
            check_mode=False,
        )
    ),
    benchmark_param(PerformanceBenchmark("sum_chain_performance", "propagator", 1.5, check_mode=True)),
    benchmark_param(PerformanceBenchmark("sum_chain_performance", "propagator", 1.5, check_mode=False)),
    benchmark_param(
        PerformanceBenchmark(
            "repeated_constraints_performance",
            "propagator",
            90.0,
            check_mode=True,
            constants={"pair_count": 130},
        )
    ),
    benchmark_param(
        PerformanceBenchmark(
            "repeated_constraints_performance",
            "propagator",
            120.0,
            check_mode=False,
            constants={"pair_count": 1000},
        )
    ),
    benchmark_param(
        PerformanceBenchmark(
            "large_int_domain_performance",
            "propagator",
            13.0,
            check_mode=True,
            constants={"int_domain_size": 15},
        )
    ),
    benchmark_param(
        PerformanceBenchmark(
            "large_int_domain_performance",
            "propagator",
            95.0,
            check_mode=False,
            constants={"int_domain_size": 3000},
        )
    ),
    benchmark_param(
        PerformanceBenchmark(
            "assignment_chain_performance",
            "propagator",
            2.0,
            check_mode=True,
            constants={"chain_length": 200},
        )
    ),
    benchmark_param(
        PerformanceBenchmark(
            "assignment_chain_performance",
            "propagator",
            2.0,
            check_mode=False,
            constants={"chain_length": 200},
        )
    ),
]

all_benchmarks = compile_benchmarks + ground_benchmarks + propagator_benchmarks


@pytest.mark.parametrize(
    "name",
    base_tests + compile_extra,
)
def test_engine_compile(name: str):
    unsupported: list[str] = [
        "engine_request",
        "engine_request_mult",
        "optimize_bools",
        "optimize_floats",
        "optimize_ints",
        "optimize_priority",
        "warning_syntax",
    ]
    if name not in unsupported:
        run_test(name, "compile")


@pytest.mark.parametrize(
    "benchmark_case",
    all_benchmarks,
)
@pytest.mark.performance
def test_performance(benchmark, benchmark_case: PerformanceBenchmark):
    benchmark.extra_info.update(
        {
            "engine": benchmark_case.engine,
            "fixture": benchmark_case.name,
            "check_mode": benchmark_case.check_mode,
            "constants": benchmark_case.constants or {},
        }
    )
    benchmark.pedantic(
        run_benchmark_case,
        args=(benchmark_case,),
        rounds=benchmark_case.measured_runs,
        iterations=1,
        warmup_rounds=benchmark_case.warmup_runs,
    )
    assert_benchmark_threshold(benchmark, benchmark_case)


@pytest.mark.parametrize(
    "name",
    base_tests + ground_extra,
)
def test_engine_ground(name: str):
    unsupported: list[str] = [
        "engine_request",
        "engine_request_mult",
        "lambdas",
        "lambda_recursive",
        "lambda_zero_args",
        "multimap_basics",
        "multimap_equality",
        "multimap_executions",
        "multimaps",
        "optimize_bools",
        "optimize_floats",
        "optimize_ints",
        "optimize_priority",
        "reasoning_modes",
        "set_fold_bools",
        "engine_request_set_ref",
        "set_iterations",
        "set_selfref",
        "type_checking",
        "warning_syntax",
    ]
    if name not in unsupported:
        run_test(name, "ground")


@pytest.mark.parametrize(
    ["name", "check_mode"],
    list(zip(base_tests + propagator_extra, [True] * len(base_tests + propagator_extra)))
    + list(zip(base_tests + propagator_extra, [False] * len(base_tests + propagator_extra))),
)
def test_engine_propagator(name, check_mode):
    unsupported: list[str] = [
        "bool_evaluate",
        "engine_request",
        "engine_request_mult",
        "lambda_recursive",
        "multimaps",
        "optimize_bools",
        "optimize_floats",
        "optimize_ints",
        "optimize_priority",
        "set_fold_bools",
        "set_iterations",
        "set_selfref",
        "warning_variables",
        "warning_variable_undeclared",
        "type_checking",
    ]
    if name not in unsupported:
        run_test(name, "propagator", check_mode)
