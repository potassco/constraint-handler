import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import clingo
import pytest

import constraint_handler

ctrl_options = ["0", "--heuristic=Domain"]
Engine = Literal["compile", "ground", "propagator"]
performance_examples_dir = Path("tests/performance")


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


def run_benchmark_program(benchmark_case: PerformanceBenchmark) -> None:
    benchmark_options = list(ctrl_options)
    if benchmark_case.constants:
        for name, value in sorted(benchmark_case.constants.items()):
            benchmark_options.extend(["-c", f"{name}={value}"])

    ctl = clingo.Control(benchmark_options)
    constraint_handler.add_to_control(ctl, propagator_check_only=benchmark_case.check_mode)
    ctl.add(f"defaultEngine({benchmark_case.engine}).")
    ctl.load(os.fspath(benchmark_case.program_path))
    ctl.ground()
    ctl.solve()


def assert_benchmark_threshold(benchmark, benchmark_case: PerformanceBenchmark) -> None:
    durations = benchmark.stats.stats.data
    average_runtime = benchmark.stats["mean"]
    assert average_runtime <= benchmark_case.max_average_seconds, (
        f"{benchmark_case.engine} benchmark {benchmark_case.name} average runtime {average_runtime:.3f}s exceeded "
        f"{benchmark_case.max_average_seconds:.3f}s over {len(durations)} measured runs "
        f"(durations={', '.join(f'{duration:.3f}s' for duration in durations)})"
    )


def benchmark_param(benchmark_case: PerformanceBenchmark):
    return pytest.param(benchmark_case, id=benchmark_case.pytest_id)


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
        run_benchmark_program,
        args=(benchmark_case,),
        rounds=benchmark_case.measured_runs,
        iterations=1,
        warmup_rounds=benchmark_case.warmup_runs,
    )
    assert_benchmark_threshold(benchmark, benchmark_case)
