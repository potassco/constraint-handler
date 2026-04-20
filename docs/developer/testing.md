# Testing

This page documents how the project validates behavior.

The test suite is centered around small ASP examples that act as specifications for the language features.

---

## Test Structure

Tests can be found in the `tests/` directory. The main structure is:

| Path | Description |
| :--- | :--- |
| `example/` | ASP programs used as executable feature specifications |
| `utils/` | shared test helpers for building expectations and running solvers |
| `test_api.py` | tests focused on the Python API and integration points |
| `test_encoding.py` | Declares which tests from `example/` should be run against which engines and performs the actual test execution |
| `test_operator_validation.py` | tests focused on Python-side operator argument validation |

The example-based tests are the most important for validating behavior in the constraint handler. They are also the most useful for contributors, since they provide a clear specification of what the system should do in various scenarios.

Each example consists of one input program together with one or more expectation files. The input lives in `name.lp`, while expected atoms are stored in separate files with specific suffixes.

The general pattern is:

| File Type | Description |
| :--- | :--- |
| `name.lp` | input program or feature example |
| `name.expected.all` | atoms expected in every model |
| `name.expected.any` | atoms expected in at least one model |
| `name.expected.first` | atoms expected in the first model |
| `name.expected.none` | atoms that must not appear in any model |

The expectation files are combined by the shared test helpers in `tests/utils/testing.py`.

If a test defines `expected.all` or `expected.first` but not `expected.any`, the harness also requires that at least one model exists.

For reasoning mode tests, there exist two additional files:

| File Type | Description |
| :--- | :--- |
| `name.expected.brave` | atoms expected in the last model using brave reasoning |
| `name.expected.cautious` | atoms expected in the last model using cautious reasoning |

The reasoning-mode expectations are executed as additional solver runs with the corresponding enumeration mode.

## Engine Matrix

`test_encoding.py` does not run each example just once. Instead, it drives the same example suite across multiple engines:

- `compile`
- `ground`
- `propagator`

Each engine has its own list of unsupported examples.

The propagator tests are also run in two modes: normal solving and `propagator_check_only=True`. That gives the propagator path broader coverage than the other engines.


!!! Example
    To create a test for `simple_addition` we may follow these steps:

    1. Create `simple_addition.lp` inside `tests/example/` with the input program:

    ```prolog
    evaluate(add,(val(int,1),(val(int,2),()))).
    ```

    2. Create `simple_addition.expected.all` with the expected output:

    ```prolog
    evaluated(add,(val(int,1),(val(int,2),())),val(int,3))
    ```

    3. To add it to the shared example suite, go to `test_encoding.py` and add `simple_addition` to the `base_tests` list.

    4. Check the per-engine unsupported lists in `test_encoding.py`. If the new example only works on some engines, document that there instead of forcing it into all engines.

    5. Run the test with
    ```bash
    pytest -k simple_addition
    ```
---

## Running the Tests

The project uses `pytest` as the test runner. The tests can be run individually or as a whole.

For contributors, the usual workflow is:

1. Create or modify tests in the `tests/` directory according to the specifications of the feature being developed.
2. If the change affects the example suite, register the new example in `test_encoding.py` and update the engine-specific unsupported lists if necessary.
3. Run the relevant tests using `pytest` to ensure that the new or modified tests pass and that no existing tests are broken.
4. If a test fails, investigate the failure by checking the expected and actual outputs, and adjust the implementation or the test as needed.
5. Once all tests pass, the changes can be committed and submitted for review.