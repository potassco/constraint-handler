import os
from dataclasses import dataclass
from pathlib import Path

import clingo
import pytest

import constraint_handler
from constraint_handler.engine import Engine, compile, ground, propagator, propagator_check

ctrl_options = ["1000", "--heuristic=Domain"]
performance_examples_dir = Path("tests/performance")


@dataclass(frozen=True)
class PerformanceBenchmark:
    name: str
    max_average_seconds: float
    measured_runs: int = 1
    warmup_runs: int = 0
    constants: dict[str, int] | None = None

    @property
    def program_path(self) -> str:
        return performance_examples_dir / f"{self.name}.lp"


def run_benchmark_program(benchmark_case: PerformanceBenchmark, engine: Engine) -> None:
    benchmark_options = list(ctrl_options)
    if benchmark_case.constants:
        for name, value in sorted(benchmark_case.constants.items()):
            benchmark_options.extend(["-c", f"{name}={value}"])

    ctl = clingo.Control(benchmark_options)
    constraint_handler.add_to_control(ctl)
    ctl.add(engine.program())
    ctl.load(os.fspath(benchmark_case.program_path))
    ctl.ground()
    ctl.solve()


def assert_benchmark_threshold(benchmark, benchmark_case: PerformanceBenchmark, engine: Engine) -> None:
    durations = benchmark.stats.stats.data
    average_runtime = benchmark.stats["mean"]
    assert average_runtime <= benchmark_case.max_average_seconds, (
        f"{engine.identifier()} benchmark {benchmark_case.name} "
        f"average runtime {average_runtime:.3f}s exceeded "
        f"{benchmark_case.max_average_seconds:.3f}s over {len(durations)} measured runs "
        f"(durations={', '.join(f'{duration:.3f}s' for duration in durations)})"
    )


def benchmark_param(benchmark_case: PerformanceBenchmark, engine: Engine, marks: tuple = ()):
    return pytest.param(
        benchmark_case,
        engine,
        id=f"{engine.identifier()}-{benchmark_case.name}",
        marks=(
            *marks,
            pytest.mark.timeout(
                benchmark_case.max_average_seconds * (benchmark_case.measured_runs + benchmark_case.warmup_runs) + 1
            ),
        ),
    )


compile_benchmarks = [
    PerformanceBenchmark("sum_aggregates", 6.0),
    PerformanceBenchmark("sum_chain", 0.5),
    PerformanceBenchmark("bad_scaling_ground", 2.0, constants={"max_depth": 8}),
    PerformanceBenchmark("repeated_constraints", 20.0, constants={"pair_count": 1000}),
    PerformanceBenchmark("large_int_domain", 6.0, constants={"int_domain_size": 8000}),
    PerformanceBenchmark("assignment_chain", 5.0, constants={"chain_length": 200}),
]

ground_benchmarks = [
    PerformanceBenchmark("sum_aggregates", 200.0),
    PerformanceBenchmark("sum_chain", 1.0),
    PerformanceBenchmark("bad_scaling_compile", 1.0, constants={"max_depth": 9}),
    PerformanceBenchmark("repeated_constraints", 70.0, constants={"pair_count": 1000}),
    PerformanceBenchmark("large_int_domain", 60.0, constants={"int_domain_size": 600}),
    PerformanceBenchmark("assignment_chain", 6.0, constants={"chain_length": 200}),
]

propagator_check_benchmarks = [
    PerformanceBenchmark("sum_aggregates", 20.0),
    PerformanceBenchmark("sum_chain", 1.5),
    PerformanceBenchmark("repeated_constraints", 170.0, constants={"pair_count": 130}),
    PerformanceBenchmark("assignment_chain", 5.0, constants={"chain_length": 200}),
]

propagator_solve_benchmarks = [
    PerformanceBenchmark("sum_aggregates", 100.0),
    PerformanceBenchmark("sum_chain", 1.5),
    PerformanceBenchmark("repeated_constraints", 100.0, constants={"pair_count": 1000}),
    PerformanceBenchmark("assignment_chain", 5.0, constants={"chain_length": 200}),
]

all_benchmarks = (
    [benchmark_param(benchmark_case, compile) for benchmark_case in compile_benchmarks]
    + [benchmark_param(benchmark_case, ground) for benchmark_case in ground_benchmarks]
    + [benchmark_param(benchmark_case, propagator_check) for benchmark_case in propagator_check_benchmarks]
    + [benchmark_param(benchmark_case, propagator) for benchmark_case in propagator_solve_benchmarks]
    + [
        benchmark_param(
            PerformanceBenchmark("large_int_domain", 300.0, constants={"int_domain_size": 3000}),
            engine,
            marks=(pytest.mark.skip(reason="Temporarily disabled: incredibly slow (2026-05-18)"),),
        )
        for engine in (propagator_check, propagator)
    ]
)


@pytest.mark.parametrize(
    ("benchmark_case", "engine"),
    all_benchmarks,
)
@pytest.mark.performance
def test_performance(benchmark, benchmark_case: PerformanceBenchmark, engine: Engine):
    benchmark.extra_info.update(
        {
            "engine": engine.name,
            "fixture": benchmark_case.name,
            "engine_parameters": engine.parameters,
            "constants": benchmark_case.constants or {},
        }
    )
    benchmark.pedantic(
        run_benchmark_program,
        args=(benchmark_case, engine),
        rounds=benchmark_case.measured_runs,
        iterations=1,
        warmup_rounds=benchmark_case.warmup_runs,
    )
    assert_benchmark_threshold(benchmark, benchmark_case, engine)
