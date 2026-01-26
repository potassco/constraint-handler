# constraint_handler

The constraint handler is a clingo library that supports solving discrete
combinatorial decision or optimization problems where constraints and variables
are defined through expressions.

## Installation

This project requires Python `3.12+` and can be installed either from TestPyPI
or directly from source.

### From TestPyPI

This is the easiest way to get started. Run the following command in your
terminal:

```bash
pip install -i https://test.pypi.org/simple/ constraint-handler
```

### From Source (for Developers)

To install the project for development, clone the repository and install it in
editable mode.

```bash
git clone https://github.com/potassco/constraint-handler
cd constraint-handler
pip install -e .[dev]
```

## Documentation

To generate the documentation, at least the "doc" part of the project needs to
be installed. This is included in the "dev" installation.

After that, to view the documentation locally, run:

```bash
mkdocs serve
```

## Manual Execution

To try to solve a set of facts in the (undocumented) input format call

```bash
clingo your_facts.lp tests/example/includeAll.lp 0
```

to solve all your described constraints.
